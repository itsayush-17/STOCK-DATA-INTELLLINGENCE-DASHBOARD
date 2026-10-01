"""
Seeded market, macro, persona, and default data definitions for Smart Investment & Portfolio Analytics.
"""

from typing import Dict, Any, List

ASSET_CLASS_PARAMS: Dict[str, Dict[str, Any]] = {
    "equity_domestic": {
        "expected_return": 0.12,  # 12% p.a.
        "volatility": 0.16,       # 16% annual std dev
        "name": "Domestic Equity (India Large/Mid/Small Cap)"
    },
    "debt": {
        "expected_return": 0.07,  # 7% p.a.
        "volatility": 0.04,       # 4% annual std dev
        "name": "Debt & Fixed Income (Debt Funds, PPF, FDs)"
    },
    "gold": {
        "expected_return": 0.09,  # 9% p.a.
        "volatility": 0.12,       # 12% annual std dev
        "name": "Gold & Precious Metals (SGBs, Gold ETFs)"
    },
    "cash": {
        "expected_return": 0.045, # 4.5% p.a.
        "volatility": 0.015,      # 1.5% annual std dev
        "name": "Liquid & Cash Reserves (Savings, Liquid Funds)"
    },
    "equity_international": {
        "expected_return": 0.11,  # 11% p.a.
        "volatility": 0.18,       # 18% annual std dev
        "name": "International Equity (US/Global Funds)"
    }
}

DEFAULT_MARKET_SNAPSHOT: Dict[str, Any] = {
    "as_of_date": "2026-10-01",
    "indices": [
        {"symbol": "^NSEI", "name": "NIFTY 50", "value": 24850.40, "change_pct": 0.65, "region": "India"},
        {"symbol": "^BSESN", "name": "BSE SENSEX", "value": 81240.15, "change_pct": 0.58, "region": "India"},
        {"symbol": "NIFTYMID100", "name": "NIFTY MIDCAP 100", "value": 58420.80, "change_pct": 1.12, "region": "India"},
        {"symbol": "^GSPC", "name": "S&P 500", "value": 5750.20, "change_pct": -0.22, "region": "USA"},
        {"symbol": "^IXIC", "name": "NASDAQ 100", "value": 18100.50, "change_pct": -0.45, "region": "USA"}
    ],
    "macro_indicators": {
        "rbi_repo_rate": 6.50,
        "cpi_inflation_pct": 4.80,
        "igb_10y_yield_pct": 7.05,
        "usd_inr": 83.55,
        "brent_crude_usd": 81.40
    },
    "sector_performance": [
        {"sector": "Financial Services & Banking", "weight_nifty50_pct": 32.5, "change_1m_pct": 2.4, "status": "Strong"},
        {"sector": "Information Technology", "weight_nifty50_pct": 13.8, "change_1m_pct": 3.8, "status": "Outperforming"},
        {"sector": "Oil, Gas & Consumable Fuels", "weight_nifty50_pct": 11.2, "change_1m_pct": -1.1, "status": "Consolidating"},
        {"sector": "Fast Moving Consumer Goods (FMCG)", "weight_nifty50_pct": 9.1, "change_1m_pct": 0.8, "status": "Defensive Stable"},
        {"sector": "Automobile & Auto Components", "weight_nifty50_pct": 6.7, "change_1m_pct": 4.2, "status": "Strong"},
        {"sector": "Healthcare & Pharma", "weight_nifty50_pct": 5.4, "change_1m_pct": 1.9, "status": "Steady Growth"},
        {"sector": "Metals & Mining", "weight_nifty50_pct": 3.8, "change_1m_pct": -2.3, "status": "Volatile"}
    ],
    "regime_summary": {
        "regime": "Moderate Inflation / Steady Growth",
        "description": "Indian economy shows resilient domestic demand with CPI inflation within RBI tolerance band (4-6%) and stable policy rates."
    }
}

DEFAULT_USER_PROFILE: Dict[str, Any] = {
    "name": "Rohan Sharma",
    "age": 32,
    "horizon_years": 15,
    "income_stability_score": 8,  # Scale 1-10 (8 = Salaried IT Professional)
    "loss_tolerance_score": 7,     # Scale 1-10 (7 = Comfortable with market swings)
    "monthly_income": 180000.0,    # INR 1,80,000 / month
    "monthly_expenses": 95000.0,   # INR 95,000 / month
    "current_emergency_reserve": 450000.0, # INR 4,50,000 (approx ~4.7 months buffer)
    "goals": [
        {
            "id": "g1",
            "name": "Emergency Fund Top-Up",
            "target_amount": 570000.0, # 6 months of expenses (5.7 Lakhs)
            "timeline_years": 1,
            "priority": "High",
            "expected_return_pct": 6.5
        },
        {
            "id": "g2",
            "name": "Home Down Payment",
            "target_amount": 2500000.0, # 25 Lakhs
            "timeline_years": 5,
            "priority": "High",
            "expected_return_pct": 9.0
        },
        {
            "id": "g3",
            "name": "Children Higher Education",
            "target_amount": 5000000.0, # 50 Lakhs
            "timeline_years": 12,
            "priority": "Medium",
            "expected_return_pct": 11.5
        },
        {
            "id": "g4",
            "name": "Retirement Corpus",
            "target_amount": 35000000.0, # 3.5 Crore
            "timeline_years": 25,
            "priority": "High",
            "expected_return_pct": 12.0
        }
    ],
    "current_portfolio": {
        "total_value": 1500000.0, # INR 15 Lakhs
        "holdings": [
            {"asset_class": "equity_domestic", "amount": 900000.0, "sector": "Information Technology"},
            {"asset_class": "equity_domestic", "amount": 300000.0, "sector": "Financial Services & Banking"},
            {"asset_class": "debt", "amount": 150000.0, "sector": "Fixed Income / PPF"},
            {"asset_class": "gold", "amount": 90000.0, "sector": "Commodities"},
            {"asset_class": "cash", "amount": 60000.0, "sector": "Liquid Reserves"}
        ]
    }
}

PRESET_PERSONAS: List[Dict[str, Any]] = [
    {
        "id": "rohan",
        "title": "Rohan Sharma - 32, Salaried Tech Professional",
        "description": "Moderate-high income, building down payment and retirement nest egg.",
        "profile": DEFAULT_USER_PROFILE
    },
    {
        "id": "priya",
        "title": "Priya Patel - 41, Business Owner & Parent",
        "description": "Variable business cash flows, focused on child education & conservative wealth preservation.",
        "profile": {
            "name": "Priya Patel",
            "age": 41,
            "horizon_years": 10,
            "income_stability_score": 5,
            "loss_tolerance_score": 5,
            "monthly_income": 250000.0,
            "monthly_expenses": 140000.0,
            "current_emergency_reserve": 1200000.0,
            "goals": [
                {
                    "id": "g1",
                    "name": "Child Overseas Education",
                    "target_amount": 7500000.0,
                    "timeline_years": 7,
                    "priority": "High",
                    "expected_return_pct": 10.0
                },
                {
                    "id": "g2",
                    "name": "Retirement Corpus",
                    "target_amount": 40000000.0,
                    "timeline_years": 18,
                    "priority": "High",
                    "expected_return_pct": 11.0
                }
            ],
            "current_portfolio": {
                "total_value": 4200000.0,
                "holdings": [
                    {"asset_class": "equity_domestic", "amount": 1800000.0, "sector": "Financial Services & Banking"},
                    {"asset_class": "debt", "amount": 1500000.0, "sector": "Fixed Income / PPF"},
                    {"asset_class": "gold", "amount": 500000.0, "sector": "Commodities"},
                    {"asset_class": "equity_international", "amount": 400000.0, "sector": "Global Tech"}
                ]
            }
        }
    },
    {
        "id": "amit_sunita",
        "title": "Amit & Sunita - 26, Young Double Income Couple",
        "description": "High risk tolerance, long investment horizon, aggressive wealth building.",
        "profile": {
            "name": "Amit & Sunita",
            "age": 26,
            "horizon_years": 20,
            "income_stability_score": 9,
            "loss_tolerance_score": 9,
            "monthly_income": 220000.0,
            "monthly_expenses": 80000.0,
            "current_emergency_reserve": 600000.0,
            "goals": [
                {
                    "id": "g1",
                    "name": "First Home Purchase",
                    "target_amount": 3000000.0,
                    "timeline_years": 4,
                    "priority": "High",
                    "expected_return_pct": 9.5
                },
                {
                    "id": "g2",
                    "name": "Early Retirement / Financial Independence",
                    "target_amount": 60000000.0,
                    "timeline_years": 20,
                    "priority": "High",
                    "expected_return_pct": 13.0
                }
            ],
            "current_portfolio": {
                "total_value": 850000.0,
                "holdings": [
                    {"asset_class": "equity_domestic", "amount": 600000.0, "sector": "Information Technology"},
                    {"asset_class": "equity_international", "amount": 150000.0, "sector": "Global Tech"},
                    {"asset_class": "cash", "amount": 100000.0, "sector": "Liquid Reserves"}
                ]
            }
        }
    }
]
