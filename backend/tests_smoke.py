"""Small smoke tests for the analytics engine."""

from analytics.engine import bootstrap_payload, build_analysis


def test_analysis_payload_has_core_sections() -> None:
    analysis = build_analysis()
    assert analysis["risk_profile"]["label"] in {"Conservative", "Moderate", "Aggressive"}
    assert analysis["cash_flow"]["investable_surplus"] > 0
    assert sum(analysis["recommendation"]["target_allocation_pct"].values()) == 100
    assert analysis["portfolio"]["health_score"] >= 0


def test_bootstrap_payload_contains_market_and_analysis() -> None:
    payload = bootstrap_payload()
    assert "analysis" in payload
    assert "market" in payload
    assert payload["market"]["derived"]["market_regime"] in {"Risk-On", "Balanced", "Defensive"}


def test_analysis_accepts_a_partial_planner_update() -> None:
    analysis = build_analysis(
        {
            "monthly_income": 120_000,
            "monthly_expenses": {"rent": 30_000, "emis": 5_000},
            "risk_inputs": {"investment_horizon_years": 12},
        }
    )
    assert analysis["cash_flow"]["monthly_income"] == 120_000
    assert analysis["cash_flow"]["emi"] == 5_000
    assert analysis["simulation"]["years"] == 12
