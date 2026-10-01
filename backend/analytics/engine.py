"""
Analytics Engine for Smart Investment & Portfolio Analytics.
Performs financial math, risk modeling, emergency fund analysis, asset allocation, 
goal planning (SIP estimation), portfolio health & concentration diagnostics, 
and Monte Carlo wealth simulation using NumPy and Pandas.
"""

from typing import Dict, Any, List, Tuple, Optional, Union
import numpy as np
import pandas as pd

from .seed import (
    ASSET_CLASS_PARAMS,
    DEFAULT_MARKET_SNAPSHOT,
    DEFAULT_USER_PROFILE,
    PRESET_PERSONAS,
)


def _safe_float(val: Any, default: float = 0.0) -> float:
    """Helper function to safely convert values to float."""
    try:
        if val is None:
            return default
        res = float(val)
        return res if not np.isnan(res) and not np.isinf(res) else default
    except (ValueError, TypeError):
        return default


def _safe_int(val: Any, default: int = 0) -> int:
    """Helper function to safely convert values to int."""
    try:
        if val is None:
            return default
        return int(val)
    except (ValueError, TypeError):
        return default


def calculate_cash_flow(income: Any, expenses: Any) -> Dict[str, Any]:
    """Calculates monthly cash flow metrics including investable surplus and savings rate."""
    income = max(0.0, _safe_float(income, 0.0))
    expenses = max(0.0, _safe_float(expenses, 0.0))
    surplus = max(0.0, income - expenses)
    savings_rate = (surplus / income * 100.0) if income > 0 else 0.0
    expense_ratio = (expenses / income * 100.0) if income > 0 else 0.0

    return {
        "monthly_income": round(income, 2),
        "monthly_expenses": round(expenses, 2),
        "investable_surplus": round(surplus, 2),
        "savings_rate_pct": round(savings_rate, 2),
        "expense_ratio_pct": round(expense_ratio, 2),
    }


def calculate_emergency_fund(
    expenses: float, current_reserve: float, stability_score: int
) -> Dict[str, Any]:
    """
    Evaluates emergency fund readiness.
    Determines recommended months of buffer based on income stability.
    """
    expenses = max(0.0, _safe_float(expenses, 0.0))
    current_reserve = max(0.0, _safe_float(current_reserve, 0.0))
    stability_score = max(1, min(10, _safe_int(stability_score, 8)))

    # Lower stability requires larger emergency buffer
    if stability_score >= 8:
        target_months = 6
    elif stability_score >= 5:
        target_months = 9
    else:
        target_months = 12

    target_reserve = target_months * expenses
    gap = max(0.0, target_reserve - current_reserve)
    readiness_pct = (current_reserve / target_reserve * 100.0) if target_reserve > 0 else 100.0
    readiness_pct = min(100.0, round(readiness_pct, 2))

    if readiness_pct >= 100.0:
        status = "Fully Funded"
        badge = "success"
    elif readiness_pct >= 75.0:
        status = "Adequate Reserve"
        badge = "info"
    elif readiness_pct >= 45.0:
        status = "Partial Reserve Needed"
        badge = "warning"
    else:
        status = "Critical Gap - Action Required"
        badge = "danger"

    return {
        "target_months": target_months,
        "target_reserve": round(target_reserve, 2),
        "current_reserve": round(current_reserve, 2),
        "reserve_gap": round(gap, 2),
        "readiness_pct": readiness_pct,
        "status": status,
        "status_badge": badge,
        "months_covered": round(current_reserve / expenses, 1) if expenses > 0 else 99.0
    }


def calculate_risk_profile(
    age: int, horizon_years: int, stability_score: int, loss_tolerance_score: int
) -> Dict[str, Any]:
    """
    Computes a risk profile score (0 to 100) and classifies risk posture.
    """
    age = max(18, min(80, _safe_int(age, 32)))
    horizon_years = max(1, min(40, _safe_int(horizon_years, 15)))
    stability_score = max(1, min(10, _safe_int(stability_score, 8)))
    loss_tolerance_score = max(1, min(10, _safe_int(loss_tolerance_score, 7)))

    # Factor 1: Age (Younger = higher risk capacity)
    age_score = max(0.0, min(100.0, 100.0 - (age - 20) * 1.6))
    
    # Factor 2: Horizon (Longer = higher capacity)
    horizon_score = min(100.0, horizon_years * 3.33)
    
    # Factor 3: Stability (Higher stability = higher capacity)
    stability_factor = stability_score * 10.0
    
    # Factor 4: Loss Tolerance (Self-assessed comfort with volatility)
    loss_factor = loss_tolerance_score * 10.0

    weighted_score = (
        0.25 * age_score +
        0.25 * horizon_score +
        0.20 * stability_factor +
        0.30 * loss_factor
    )
    score = round(max(0.0, min(100.0, weighted_score)), 1)

    if score <= 35.0:
        posture = "Conservative"
        description = "Focus on capital preservation and debt instruments with minimal market volatility."
    elif score <= 60.0:
        posture = "Moderate / Balanced"
        description = "Balanced growth through a mix of equity, debt, and gold reserves."
    elif score <= 80.0:
        posture = "Aggressive Growth"
        description = "High equity allocation aiming for capital appreciation over a medium-to-long horizon."
    else:
        posture = "Very Aggressive / Wealth Creation"
        description = "Maximum growth focus with high equity and international exposure, comfortable with drawdown volatility."

    return {
        "risk_score": score,
        "posture": posture,
        "description": description,
        "sub_scores": {
            "age_capacity": round(age_score, 1),
            "horizon_capacity": round(horizon_score, 1),
            "stability_score": round(stability_factor, 1),
            "loss_tolerance": round(loss_factor, 1)
        }
    }


def calculate_target_allocation(
    risk_score: float, horizon_years: int, emergency_status: str, surplus: float
) -> Dict[str, Any]:
    """
    Recommends optimal asset allocation across Equity Domestic, Debt, Gold, Cash, and International Equity.
    Calculates monthly SIP rupee split based on surplus.
    """
    risk_score = max(0.0, min(100.0, _safe_float(risk_score, 50.0)))
    surplus = max(0.0, _safe_float(surplus, 0.0))

    # Baseline equity percentage derived from risk score
    equity_dom = min(75.0, max(15.0, risk_score * 0.70))
    intl_eq = min(15.0, max(0.0, (risk_score - 40.0) * 0.25)) if risk_score > 40 else 0.0
    gold_pct = 10.0
    
    # Liquid cash requirement
    # pyrefly: ignore [unnecessary-type-conversion]
    if emergency_status and "Critical Gap" in str(emergency_status):
        cash_pct = 20.0
        equity_dom = max(10.0, equity_dom - 10.0)
    # pyrefly: ignore [unnecessary-type-conversion]
    elif emergency_status and "Partial Reserve" in str(emergency_status):
        cash_pct = 12.0
    else:
        cash_pct = 5.0

    debt_pct = max(10.0, 100.0 - (equity_dom + intl_eq + gold_pct + cash_pct))
    
    # Normalize to ensure exactly 100%
    total = equity_dom + intl_eq + gold_pct + cash_pct + debt_pct
    total = total if total > 0 else 100.0

    weights = {
        "equity_domestic": round((equity_dom / total) * 100.0, 1),
        "debt": round((debt_pct / total) * 100.0, 1),
        "gold": round((gold_pct / total) * 100.0, 1),
        "cash": round((cash_pct / total) * 100.0, 1),
        "equity_international": round((intl_eq / total) * 100.0, 1)
    }
    
    # Adjust for rounding difference to hit 100.0 exactly
    diff = round(100.0 - sum(weights.values()), 1)
    weights["equity_domestic"] = round(weights["equity_domestic"] + diff, 1)

    # Calculate rupee split
    monthly_split = {
        k: round((v / 100.0) * surplus, 2) for k, v in weights.items()
    }

    return {
        "weights_pct": weights,
        "monthly_split_inr": monthly_split,
        "labels": {
            "equity_domestic": "Domestic Equity",
            "debt": "Debt & Fixed Income",
            "gold": "Gold & Metals",
            "cash": "Liquid / Cash",
            "equity_international": "International Equity"
        }
    }


def calculate_goal_plan(goals: List[Dict[str, Any]], surplus: float) -> Dict[str, Any]:
    """
    Computes required monthly SIP for each financial goal using annuity formulas.
    Evaluates total monthly SIP feasibility against investable surplus.
    """
    if not isinstance(goals, list):
        goals = []

    surplus = max(0.0, _safe_float(surplus, 0.0))
    total_required_sip = 0.0
    processed_goals = []

    for idx, goal in enumerate(goals):
        if not isinstance(goal, dict):
            continue
        g_name = str(goal.get("name", f"Goal {idx+1}"))
        target_amt = max(0.0, _safe_float(goal.get("target_amount", 0.0)))
        timeline_yrs = max(0.1, _safe_float(goal.get("timeline_years", 1.0)))
        exp_return_pct = _safe_float(goal.get("expected_return_pct", 10.0))
        priority = str(goal.get("priority", "Medium"))

        months = timeline_yrs * 12.0
        monthly_r = (exp_return_pct / 100.0) / 12.0

        if monthly_r > 0:
            # Future Value of annuity formula: FV = PMT * (((1 + r)^n - 1) / r)
            # PMT = FV * r / (((1 + r)^n) - 1)
            pmt = target_amt * monthly_r / (((1.0 + monthly_r) ** months) - 1.0)
        else:
            pmt = target_amt / months

        required_sip = round(max(0.0, pmt), 2)
        total_required_sip += required_sip

        processed_goals.append({
            "id": str(goal.get("id", f"g_{idx+1}")),
            "name": g_name,
            "target_amount": round(target_amt, 2),
            "timeline_years": timeline_yrs,
            "expected_return_pct": exp_return_pct,
            "priority": priority,
            "required_monthly_sip": required_sip,
        })

    total_required_sip = round(total_required_sip, 2)
    surplus_coverage_pct = round((surplus / total_required_sip * 100.0), 1) if total_required_sip > 0 else 100.0

    if surplus >= total_required_sip:
        feasibility = "Goals Fully Solvent"
        feasibility_badge = "success"
        gap_surplus = round(surplus - total_required_sip, 2)
    else:
        feasibility = "SIP Deficit - Prioritization Required"
        feasibility_badge = "warning"
        gap_surplus = round(surplus - total_required_sip, 2)

    return {
        "goals": processed_goals,
        "total_required_sip": total_required_sip,
        "investable_surplus": surplus,
        "surplus_coverage_pct": surplus_coverage_pct,
        "feasibility": feasibility,
        "feasibility_badge": feasibility_badge,
        "surplus_gap_or_buffer": gap_surplus
    }


def analyze_portfolio(
    portfolio_data: Dict[str, Any], target_allocation: Dict[str, Any], emergency_readiness: float, surplus_coverage: float
) -> Dict[str, Any]:
    """
    Performs concentration, diversification, target alignment, and health scoring on current portfolio.
    """
    if not isinstance(portfolio_data, dict):
        portfolio_data = {}
    if not isinstance(target_allocation, dict):
        target_allocation = {}

    holdings = portfolio_data.get("holdings", [])
    if not isinstance(holdings, list) or not holdings:
        return {
            "total_value": 0.0,
            "current_weights_pct": {},
            "alignment_score": 0.0,
            "diversification_score": 0.0,
            "health_score": 0.0,
            "sector_breakdown": [],
            "rebalancing_suggestions": ["No portfolio holdings provided. Begin investing according to target asset allocation."]
        }

    df = pd.DataFrame(holdings)
    
    # Ensure required columns exist cleanly
    if "amount" not in df.columns:
        df["amount"] = 0.0
    else:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)

    if "asset_class" not in df.columns:
        df["asset_class"] = "equity_domestic"
    else:
        df["asset_class"] = df["asset_class"].fillna("equity_domestic").astype(str)

    if "sector" not in df.columns:
        df["sector"] = "General"
    else:
        df["sector"] = df["sector"].fillna("General").astype(str)

    total_val = float(df["amount"].sum())

    if total_val <= 0:
        total_val = 1.0  # Avoid zero division

    # Asset class breakdown
    asset_sums = df.groupby("asset_class")["amount"].sum().to_dict()
    all_classes = ["equity_domestic", "debt", "gold", "cash", "equity_international"]
    current_weights = {ac: round((asset_sums.get(ac, 0.0) / total_val) * 100.0, 1) for ac in all_classes}

    # Alignment Score calculation: 100 - sum(|current_weight - target_weight|) / 2
    target_weights = target_allocation.get("weights_pct", {})
    if not isinstance(target_weights, dict):
        target_weights = {}

    abs_diff_sum = sum(abs(current_weights.get(ac, 0.0) - target_weights.get(ac, 0.0)) for ac in all_classes)
    alignment_score = max(0.0, min(100.0, 100.0 - (abs_diff_sum / 2.0)))

    # Sector breakdown & concentration
    sector_sums = df.groupby("sector")["amount"].sum().reset_index()
    sector_sums["weight_pct"] = (sector_sums["amount"] / total_val) * 100.0
    sector_breakdown = [
        {"sector": str(r["sector"]), "amount": round(float(r["amount"]), 2), "weight_pct": round(float(r["weight_pct"]), 1)}
        for r in sector_sums.to_dict(orient="records")
    ]

    # Herfindahl-Hirschman Index (HHI) for Diversification Score
    weights_frac = np.array(list(current_weights.values())) / 100.0
    hhi = float(np.sum(weights_frac ** 2))
    # Normalized HHI score: HHI=0.2 is well-diversified (score 100), HHI=1.0 is concentrated (score 0)
    diversification_score = max(0.0, min(100.0, (1.0 - hhi) * 125.0))

    # Overall Health Score weighted synthesis
    health_score = (
        0.35 * alignment_score +
        0.25 * diversification_score +
        0.25 * min(100.0, _safe_float(emergency_readiness, 0.0)) +
        0.15 * min(100.0, _safe_float(surplus_coverage, 0.0))
    )

    # Generate smart rebalancing suggestions
    suggestions = []
    labels = target_allocation.get("labels", {})
    for ac in all_classes:
        curr_w = current_weights.get(ac, 0.0)
        targ_w = target_weights.get(ac, 0.0)
        diff = curr_w - targ_w
        ac_name = labels.get(ac, ac) if isinstance(labels, dict) else ac

        if diff > 10.0:
            suggestions.append(f"Overweight in {ac_name} ({curr_w}% vs {targ_w}% target). Consider trimming or directing new SIPs elsewhere.")
        elif diff < -10.0:
            suggestions.append(f"Underweight in {ac_name} ({curr_w}% vs {targ_w}% target). Allocate upcoming monthly surplus here.")

    if not suggestions:
        suggestions.append("Portfolio is well-aligned with target asset allocation.")

    return {
        "total_value": round(total_val, 2),
        "current_weights_pct": current_weights,
        "alignment_score": round(alignment_score, 1),
        "diversification_score": round(diversification_score, 1),
        "health_score": round(health_score, 1),
        "sector_breakdown": sector_breakdown,
        "rebalancing_suggestions": suggestions
    }


def run_monte_carlo(
    initial_portfolio_value: float,
    monthly_sip: float,
    allocation_weights: Dict[str, float],
    horizon_years: int = 15,
    n_simulations: int = 1000
) -> Dict[str, Any]:
    """
    Performs 1000-path Monte Carlo stochastic simulation over horizon years.
    Returns 10th percentile (Conservative), 50th percentile (Median/Base), 
    and 90th percentile (Optimistic) growth trajectories.
    """
    if not isinstance(allocation_weights, dict):
        allocation_weights = {}

    initial_val = max(0.0, _safe_float(initial_portfolio_value, 0.0))
    sip = max(0.0, _safe_float(monthly_sip, 0.0))
    years = max(1, min(40, _safe_int(horizon_years, 15)))
    n_simulations = max(10, min(5000, _safe_int(n_simulations, 1000)))
    total_months = years * 12

    # Portfolio expected return & volatility based on asset allocation weights
    weights = np.array([
        allocation_weights.get("equity_domestic", 50.0) / 100.0,
        allocation_weights.get("debt", 30.0) / 100.0,
        allocation_weights.get("gold", 10.0) / 100.0,
        allocation_weights.get("cash", 5.0) / 100.0,
        allocation_weights.get("equity_international", 5.0) / 100.0,
    ])

    returns = np.array([
        ASSET_CLASS_PARAMS["equity_domestic"]["expected_return"],
        ASSET_CLASS_PARAMS["debt"]["expected_return"],
        ASSET_CLASS_PARAMS["gold"]["expected_return"],
        ASSET_CLASS_PARAMS["cash"]["expected_return"],
        ASSET_CLASS_PARAMS["equity_international"]["expected_return"]
    ])

    vols = np.array([
        ASSET_CLASS_PARAMS["equity_domestic"]["volatility"],
        ASSET_CLASS_PARAMS["debt"]["volatility"],
        ASSET_CLASS_PARAMS["gold"]["volatility"],
        ASSET_CLASS_PARAMS["cash"]["volatility"],
        ASSET_CLASS_PARAMS["equity_international"]["volatility"]
    ])

    port_mean_annual = float(np.sum(weights * returns))
    port_vol_annual = float(np.sqrt(np.sum((weights * vols) ** 2))) # Baseline uncorrelated estimate

    # Convert to monthly parameters
    monthly_mu = (port_mean_annual - 0.5 * (port_vol_annual ** 2)) / 12.0
    monthly_sigma = port_vol_annual / np.sqrt(12.0)

    # Set seed for reproducible deterministic simulation paths
    np.random.seed(42)
    simulations = np.zeros((n_simulations, total_months + 1))
    simulations[:, 0] = initial_val

    # Vectorized trajectory simulation
    random_shocks = np.random.normal(0, 1, size=(n_simulations, total_months))
    monthly_returns = np.exp(monthly_mu + monthly_sigma * random_shocks) - 1.0

    for m in range(1, total_months + 1):
        simulations[:, m] = (simulations[:, m - 1] * (1.0 + monthly_returns[:, m - 1])) + sip

    # Compute percentiles across simulations
    p10 = np.percentile(simulations, 10, axis=0)
    p50 = np.percentile(simulations, 50, axis=0)
    p90 = np.percentile(simulations, 90, axis=0)

    # Downsample points for UI charting (every 12 months / annual check-points)
    time_series = []
    step = 12 if total_months >= 24 else 1
    for m in range(0, total_months + 1, step):
        yr = m // 12 if step == 12 else round(m / 12.0, 1)
        time_series.append({
            "year": yr,
            "month": m,
            "conservative_p10": round(float(p10[m]), 0),
            "base_p50": round(float(p50[m]), 0),
            "optimistic_p90": round(float(p90[m]), 0),
        })

    # Terminal summary
    total_invested = initial_val + (sip * total_months)
    return {
        "horizon_years": years,
        "n_simulations": n_simulations,
        "total_invested": round(total_invested, 2),
        "expected_portfolio_return_pct": round(port_mean_annual * 100.0, 2),
        "expected_portfolio_volatility_pct": round(port_vol_annual * 100.0, 2),
        "outcomes": {
            "conservative_p10": round(float(p10[-1]), 0),
            "base_p50": round(float(p50[-1]), 0),
            "optimistic_p90": round(float(p90[-1]), 0),
        },
        "time_series": time_series
    }


def classify_market_regime(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """Classifies current market regime using macro and index signals."""
    if not isinstance(snapshot, dict):
        snapshot = {}
    macro = snapshot.get("macro_indicators", {})
    if not isinstance(macro, dict):
        macro = {}

    cpi = _safe_float(macro.get("cpi_inflation_pct"), 4.8)

    if cpi > 6.0:
        regime = "High Inflationary Pressure"
        bias = "Overweight Cash & Commodities; Underweight Long-Duration Debt"
    elif cpi < 4.0:
        regime = "Disinflationary Expansion"
        bias = "Overweight Equities & Growth Assets"
    else:
        regime = "Moderate Inflation / Steady Growth"
        bias = "Balanced Asset Allocation; High Quality Equities & Mid-Duration Debt"

    return {
        "regime": regime,
        "tactical_bias": bias,
        "macro_snapshot": macro
    }


def generate_plain_language_insights(
    profile: Dict[str, Any],
    cash_flow: Dict[str, Any],
    emergency: Dict[str, Any],
    risk: Dict[str, Any],
    allocation: Dict[str, Any],
    goals: Dict[str, Any],
    portfolio: Dict[str, Any],
    simulation: Dict[str, Any]
) -> List[str]:
    """Generates plain-language executive insights for the user dashboard."""
    insights = []
    if not isinstance(profile, dict): profile = {}
    if not isinstance(cash_flow, dict): cash_flow = {}
    if not isinstance(emergency, dict): emergency = {}
    if not isinstance(risk, dict): risk = {}
    if not isinstance(allocation, dict): allocation = {}
    if not isinstance(goals, dict): goals = {}
    if not isinstance(simulation, dict): simulation = {}

    # Insight 1: Cash Flow & Surplus
    surplus = cash_flow.get("investable_surplus", 0.0)
    s_rate = cash_flow.get("savings_rate_pct", 0.0)
    if s_rate >= 40.0:
        insights.append(f"Excellent monthly cash flow! You save {s_rate}% of income (₹{surplus:,.0f} investable surplus).")
    elif s_rate >= 20.0:
        insights.append(f"Healthy savings rate of {s_rate}%, yielding ₹{surplus:,.0f} available for monthly investments.")
    else:
        insights.append(f"Your savings rate is currently {s_rate}%. Focus on optimizing discretionary expenses to expand investable surplus.")

    # Insight 2: Emergency Readiness
    readiness = emergency.get("readiness_pct", 0.0)
    months_covered = emergency.get("months_covered", 0.0)
    reserve_gap = emergency.get("reserve_gap", 0.0)
    if readiness < 75.0:
        insights.append(f"Emergency Reserve Priority: You currently have {months_covered} months of expenses saved. Prioritize filling the ₹{reserve_gap:,.0f} gap before high-risk equities.")
    else:
        insights.append(f"Emergency Safety Net is solid with {months_covered} months of expense coverage ready.")

    # Insight 3: Target Allocation & Risk
    posture = risk.get("posture", "Balanced")
    score = risk.get("risk_score", 50.0)
    weights = allocation.get("weights_pct", {})
    eq_w = weights.get("equity_domestic", 50.0)
    d_w = weights.get("debt", 30.0)
    insights.append(f"Based on your {posture} profile (Score: {score}/100), we recommend allocating {eq_w}% to Domestic Equity and {d_w}% to Debt.")

    # Insight 4: Goals Feasibility
    cov = goals.get("surplus_coverage_pct", 100.0)
    req_sip = goals.get("total_required_sip", 0.0)
    if cov >= 100.0:
        insights.append(f"All monthly SIP goal requirements (₹{req_sip:,.0f}) are fully covered by your monthly surplus.")
    else:
        insights.append(f"Goal SIP gap detected: Required SIP is ₹{req_sip:,.0f}/mo vs your surplus of ₹{surplus:,.0f}/mo. Consider staggering long-term goals or stepping up SIPs as income grows.")

    # Insight 5: Monte Carlo projection highlight
    outcomes = simulation.get("outcomes", {})
    p50_val = outcomes.get("base_p50", 0.0)
    horizon = simulation.get("horizon_years", 15)
    insights.append(f"{horizon}-Year Wealth Projection: Under expected market growth, your portfolio is projected to grow to approx ₹{p50_val:,.0f} (Base Case).")

    return insights


# pyrefly: ignore [bad-function-definition]
def run_full_analysis(profile_payload: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Main entrypoint that runs the end-to-end analytics workflow.
    """
    if not isinstance(profile_payload, dict):
        profile_payload = DEFAULT_USER_PROFILE.copy()

    # Merge user profile with defaults to ensure all required keys exist
    profile = DEFAULT_USER_PROFILE.copy()
    profile.update(profile_payload)

    # Step 1: Cash Flow
    cash_flow = calculate_cash_flow(
        profile.get("monthly_income", 180000.0),
        profile.get("monthly_expenses", 95000.0)
    )

    # Step 2: Emergency Reserve
    emergency = calculate_emergency_fund(
        cash_flow["monthly_expenses"],
        profile.get("current_emergency_reserve", 450000.0),
        profile.get("income_stability_score", 8)
    )

    # Step 3: Risk Profile
    risk = calculate_risk_profile(
        profile.get("age", 32),
        profile.get("horizon_years", 15),
        profile.get("income_stability_score", 8),
        profile.get("loss_tolerance_score", 7)
    )

    # Step 4: Asset Allocation Recommendation
    allocation = calculate_target_allocation(
        risk["risk_score"],
        profile.get("horizon_years", 15),
        emergency["status"],
        cash_flow["investable_surplus"]
    )

    # Step 5: Goal Planning
    goals = calculate_goal_plan(
        profile.get("goals", []),
        cash_flow["investable_surplus"]
    )

    # Step 6: Portfolio Analytics & Health Diagnostics
    curr_portfolio = profile.get("current_portfolio", {})
    portfolio_analytics = analyze_portfolio(
        curr_portfolio,
        allocation,
        emergency["readiness_pct"],
        goals["surplus_coverage_pct"]
    )

    # Step 7: Monte Carlo Simulation
    initial_value = portfolio_analytics["total_value"]
    monthly_sip = cash_flow["investable_surplus"]
    simulation = run_monte_carlo(
        initial_value,
        monthly_sip,
        allocation["weights_pct"],
        profile.get("horizon_years", 15)
    )

    # Step 8: Market & Macro Regime
    market_snapshot = DEFAULT_MARKET_SNAPSHOT
    regime = classify_market_regime(market_snapshot)

    # Step 9: Plain Language NLG Insights
    insights = generate_plain_language_insights(
        profile, cash_flow, emergency, risk, allocation, goals, portfolio_analytics, simulation
    )

    return {
        "profile": profile,
        "cash_flow": cash_flow,
        "emergency_fund": emergency,
        "risk_profile": risk,
        "target_allocation": allocation,
        "goal_plan": goals,
        "portfolio_analytics": portfolio_analytics,
        "simulation": simulation,
        "market_snapshot": market_snapshot,
        "market_regime": regime,
        "insights": insights,
        "preset_personas": PRESET_PERSONAS
    }
