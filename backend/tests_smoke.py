"""
Smoke test suite for Smart Investment & Portfolio Analytics platform.
Tests engine logic, seed payloads, calculations, and server endpoints.

Run from the project root:
    python -m pytest tests/ -v
"""

import sys
from pathlib import Path

# Put BOTH the project root and the backend folder on sys.path,
# so "backend.xxx" imports and plain "analytics.xxx" imports both work.
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
for _p in (ROOT_DIR, BACKEND_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import json
import socket
import threading
import time
import urllib.request

import pytest

from backend.analytics.seed import (
    ASSET_CLASS_PARAMS,
    DEFAULT_MARKET_SNAPSHOT,
    DEFAULT_USER_PROFILE,
    PRESET_PERSONAS,
)
from backend.analytics.engine import (
    calculate_cash_flow,
    calculate_emergency_fund,
    calculate_risk_profile,
    calculate_target_allocation,
    calculate_goal_plan,
    analyze_portfolio,
    run_monte_carlo,
    run_full_analysis,
)
from backend.server import create_server


# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------
def test_seed_payload_integrity():
    """Verify seed data dictionaries have required keys and correct data types."""
    assert "equity_domestic" in ASSET_CLASS_PARAMS
    assert ASSET_CLASS_PARAMS["equity_domestic"]["expected_return"] == 0.12

    assert "indices" in DEFAULT_MARKET_SNAPSHOT
    assert len(DEFAULT_MARKET_SNAPSHOT["indices"]) >= 3

    # Market data changes over time, so check type and a sane range
    # instead of one exact number.
    repo = DEFAULT_MARKET_SNAPSHOT["macro_indicators"]["rbi_repo_rate"]
    assert isinstance(repo, (int, float))
    assert 0 < repo < 15

    # Check the profile has valid fields without locking in exact values.
    assert isinstance(DEFAULT_USER_PROFILE["name"], str)
    assert DEFAULT_USER_PROFILE["name"].strip() != ""
    assert DEFAULT_USER_PROFILE["monthly_income"] > 0

    assert len(PRESET_PERSONAS) >= 3


# ---------------------------------------------------------------------------
# Engine functions
# ---------------------------------------------------------------------------
def test_cash_flow_calculation():
    """Test cash flow surplus, savings rate, and expense ratio calculations."""
    cf = calculate_cash_flow(200000.0, 120000.0)
    assert cf["monthly_income"] == 200000.0
    assert cf["monthly_expenses"] == 120000.0
    assert cf["investable_surplus"] == 80000.0
    assert cf["savings_rate_pct"] == 40.0
    assert cf["expense_ratio_pct"] == 60.0

    # Edge case: zero income
    cf_zero = calculate_cash_flow(0.0, 50000.0)
    assert cf_zero["investable_surplus"] == 0.0
    assert cf_zero["savings_rate_pct"] == 0.0


def test_emergency_fund_evaluation():
    """Test emergency fund readiness scoring and gap calculations."""
    # High stability profile (8+ stability -> 6 months target)
    ef = calculate_emergency_fund(100000.0, 600000.0, 8)
    assert ef["target_months"] == 6
    assert ef["target_reserve"] == 600000.0
    assert ef["readiness_pct"] == 100.0
    assert ef["status"] == "Fully Funded"

    # Deficit case
    ef_gap = calculate_emergency_fund(100000.0, 200000.0, 8)
    assert ef_gap["reserve_gap"] == 400000.0
    assert ef_gap["readiness_pct"] == pytest.approx(33.33, abs=0.01)
    assert "Critical Gap" in ef_gap["status"]


def test_risk_profile_scoring():
    """Test risk scoring logic across different age and horizon inputs."""
    # Young investor with long horizon and high risk tolerance
    rp_young = calculate_risk_profile(
        age=25, horizon_years=25, stability_score=9, loss_tolerance_score=9
    )
    assert rp_young["risk_score"] > 70.0
    assert "Aggressive" in rp_young["posture"]

    # Older investor with short horizon
    rp_older = calculate_risk_profile(
        age=60, horizon_years=5, stability_score=4, loss_tolerance_score=3
    )
    assert rp_older["risk_score"] < 45.0

    # The young investor should always score higher than the older one
    assert rp_young["risk_score"] > rp_older["risk_score"]


def test_target_allocation_model():
    """Test asset allocation recommendation logic and 100% total sum constraint."""
    alloc = calculate_target_allocation(
        risk_score=75.0,
        horizon_years=15,
        emergency_status="Fully Funded",
        surplus=85000.0,
    )
    weights = alloc["weights_pct"]
    assert sum(weights.values()) == pytest.approx(100.0, abs=0.1)
    assert weights["equity_domestic"] > 40.0
    assert alloc["monthly_split_inr"]["equity_domestic"] > 0.0


def test_goal_plan_and_sip():
    """Test annuity goal SIP estimation."""
    goals_input = [
        {
            "name": "Child Education",
            "target_amount": 2400000.0,
            "timeline_years": 10,
            "expected_return_pct": 12.0,
        }
    ]
    gp = calculate_goal_plan(goals_input, surplus=50000.0)
    assert len(gp["goals"]) == 1
    assert gp["goals"][0]["required_monthly_sip"] > 0.0
    assert gp["surplus_coverage_pct"] > 0.0


def test_portfolio_analytics():
    """Test portfolio alignment, concentration, and health scoring."""
    target_alloc = calculate_target_allocation(70.0, 15, "Fully Funded", 85000.0)
    portfolio_data = {
        "holdings": [
            {"asset_class": "equity_domestic", "amount": 600000.0, "sector": "Technology"},
            {"asset_class": "debt", "amount": 400000.0, "sector": "Fixed Income"},
        ]
    }
    pa = analyze_portfolio(
        portfolio_data, target_alloc, emergency_readiness=100.0, surplus_coverage=100.0
    )
    assert pa["total_value"] == 1000000.0
    assert pa["alignment_score"] > 0.0
    assert pa["health_score"] > 0.0
    assert len(pa["rebalancing_suggestions"]) >= 1


def test_monte_carlo_simulation():
    """Test Monte Carlo stochastic trajectory outcomes and percentiles."""
    weights = {
        "equity_domestic": 50.0,
        "debt": 30.0,
        "gold": 10.0,
        "cash": 5.0,
        "equity_international": 5.0,
    }
    mc = run_monte_carlo(
        initial_portfolio_value=1000000.0,
        monthly_sip=50000.0,
        allocation_weights=weights,
        horizon_years=10,
        n_simulations=500,
    )

    assert mc["horizon_years"] == 10
    outcomes = mc["outcomes"]
    # Optimistic >= Base >= Conservative
    assert outcomes["optimistic_p90"] >= outcomes["base_p50"]
    assert outcomes["base_p50"] >= outcomes["conservative_p10"]
    assert len(mc["time_series"]) > 0


def test_full_analysis_workflow():
    """Test end-to-end full analysis pipeline."""
    res = run_full_analysis(DEFAULT_USER_PROFILE)
    for key in (
        "cash_flow",
        "emergency_fund",
        "risk_profile",
        "target_allocation",
        "goal_plan",
        "portfolio_analytics",
        "simulation",
        "insights",
    ):
        assert key in res, f"Missing key in analysis result: {key}"
    assert len(res["insights"]) >= 4


def test_edge_cases_and_malformed_inputs():
    """Test engine resilience when handling None, empty, or invalid data types."""
    # Invalid cash flow inputs
    cf_bad = calculate_cash_flow("invalid", None)
    assert cf_bad["monthly_income"] == 0.0
    assert cf_bad["monthly_expenses"] == 0.0

    # Null goals list
    # pyrefly: ignore [bad-argument-type]
    gp_null = calculate_goal_plan(None, 50000.0)
    assert gp_null["goals"] == []

    # Incomplete holdings list missing asset_class or sector
    pa_bad = analyze_portfolio({"holdings": [{"amount": "100000"}]}, {}, 100.0, 100.0)
    assert pa_bad["total_value"] == 100000.0

    # Non-dict profile payload
    # pyrefly: ignore [bad-argument-type]
    res_none = run_full_analysis(" not_a_dict")
    assert "cash_flow" in res_none


# ---------------------------------------------------------------------------
# Server endpoints
# ---------------------------------------------------------------------------
def _get_free_port() -> int:
    """Ask the OS for a free port so tests never clash with a running app."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_for_port(port: int, timeout: float = 5.0) -> None:
    """Keep trying to connect until the server is accepting connections."""
    start = time.time()
    while time.time() - start < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return
        time.sleep(0.05)
    raise RuntimeError(f"Server did not start on port {port} within {timeout}s")


def test_server_endpoints():
    """Launch local server on a free port in a thread and test the REST API."""
    test_port = _get_free_port()
    httpd = create_server(port=test_port, host="127.0.0.1")
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()
    _wait_for_port(test_port)

    # This opener ignores system proxies, which can break 127.0.0.1 requests.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    try:
        base_url = f"http://127.0.0.1:{test_port}"

        # GET /api/bootstrap
        with opener.open(f"{base_url}/api/bootstrap", timeout=10) as req_boot:
            assert req_boot.status == 200
            data_boot = json.loads(req_boot.read().decode("utf-8"))
            assert "market_snapshot" in data_boot
            assert "cash_flow" in data_boot

        # GET /api/analyze
        with opener.open(f"{base_url}/api/analyze", timeout=10) as req_an:
            assert req_an.status == 200
            data_an = json.loads(req_an.read().decode("utf-8"))
            assert "risk_profile" in data_an

        # POST /api/analyze
        post_payload = json.dumps(
            {"monthly_income": 300000.0, "monthly_expenses": 100000.0}
        ).encode("utf-8")
        post_req = urllib.request.Request(
            f"{base_url}/api/analyze",
            data=post_payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with opener.open(post_req, timeout=10) as res_post:
            assert res_post.status == 200
            data_post = json.loads(res_post.read().decode("utf-8"))
            assert data_post["cash_flow"]["monthly_income"] == 300000.0
            assert data_post["cash_flow"]["investable_surplus"] == 200000.0
    finally:
        httpd.shutdown()
        httpd.server_close()


if __name__ == "__main__":
    sys.exit(pytest.main(["-v", __file__]))