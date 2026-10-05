"""Versioned API for investment education, planning, and private portfolios."""

from collections import defaultdict
import os

import jwt
import numpy as np
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import SessionLocal, get_db
from .guide_seed import guide_records
from .models import Holding, InvestmentGuide, User
from .schemas import EmergencyCheck, GoalInput, HoldingInput, HoldingRead, LumpSumInput
from .schemas import RiskQuiz, SIPInput, TokenRead, UserCreate, UserLogin, UserRead
from .security import JWT_ALGORITHM, JWT_SECRET, create_access_token, hash_password, verify_password


DISCLAIMER = (
    "Educational information only; this is not SEBI-registered investment advice. "
    "Returns are not guaranteed and past performance does not predict future results. "
    "Consider a licensed financial or tax professional for personal decisions."
)
app = FastAPI(
    title="Northstar Investment Analytics API",
    version="1.0.0",
    description=DISCLAIMER,
)
bearer = HTTPBearer(auto_error=False)


@app.on_event("startup")
def seed_guides() -> None:
    """Seed guide content after migrations have created the database tables."""
    if os.getenv("SEED_GUIDES", "true").lower() != "true":
        return
    with SessionLocal() as db:
        existing = set(db.scalars(select(InvestmentGuide.slug)).all())
        additions = [guide for guide in guide_records() if guide.slug not in existing]
        if additions:
            db.add_all(additions)
            db.commit()


def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Sign in to access your portfolio.")
    try:
        claims = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = int(claims["sub"])
    except (jwt.PyJWTError, KeyError, ValueError) as error:
        raise HTTPException(status_code=401, detail="Session is invalid or expired.") from error
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Account was not found.")
    return user


@app.get("/api/v1/health")
def health() -> dict:
    return {"status": "ok", "disclaimer": DISCLAIMER}


@app.post("/api/v1/auth/register", response_model=UserRead, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    email = str(data.email).lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    user = User(email=email, password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/api/v1/auth/login", response_model=TokenRead)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == str(data.email).lower()))
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email or password is incorrect.")
    return TokenRead(access_token=create_access_token(user.id))


@app.get("/api/v1/auth/me", response_model=UserRead)
def me(user: User = Depends(current_user)):
    return user


def serialize_guide(guide: InvestmentGuide) -> dict:
    return {column.name: getattr(guide, column.name) for column in InvestmentGuide.__table__.columns}


@app.get("/api/v1/guides")
def list_guides(q: str | None = None, region: str | None = None,
                category: str | None = None, db: Session = Depends(get_db)):
    query = select(InvestmentGuide)
    if region:
        query = query.where(InvestmentGuide.region == region)
    if category:
        query = query.where(InvestmentGuide.category.ilike(f"%{category}%"))
    if q:
        query = query.where(InvestmentGuide.name.ilike(f"%{q}%"))
    entries = db.scalars(query.order_by(InvestmentGuide.region, InvestmentGuide.name)).all()
    return {"items": [serialize_guide(item) for item in entries], "disclaimer": DISCLAIMER}


@app.get("/api/v1/guides/{slug}")
def get_guide(slug: str, db: Session = Depends(get_db)):
    item = db.scalar(select(InvestmentGuide).where(InvestmentGuide.slug == slug))
    if item is None:
        raise HTTPException(status_code=404, detail="Investment guide not found.")
    return {**serialize_guide(item), "disclaimer": DISCLAIMER}


@app.post("/api/v1/portfolio/holdings", response_model=HoldingRead, status_code=201)
def add_holding(data: HoldingInput, user: User = Depends(current_user), db: Session = Depends(get_db)):
    holding = Holding(**data.model_dump(), user_id=user.id)
    db.add(holding)
    db.commit()
    db.refresh(holding)
    return holding


@app.get("/api/v1/portfolio/holdings", response_model=list[HoldingRead])
def list_holdings(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return db.scalars(select(Holding).where(Holding.user_id == user.id).order_by(Holding.buy_date.desc())).all()


def get_owned_holding(holding_id: int, user_id: int, db: Session) -> Holding:
    holding = db.scalar(select(Holding).where(Holding.id == holding_id, Holding.user_id == user_id))
    if holding is None:
        raise HTTPException(status_code=404, detail="Holding not found.")
    return holding


@app.put("/api/v1/portfolio/holdings/{holding_id}", response_model=HoldingRead)
def update_holding(holding_id: int, data: HoldingInput,
                   user: User = Depends(current_user), db: Session = Depends(get_db)):
    holding = get_owned_holding(holding_id, user.id, db)
    for key, value in data.model_dump().items():
        setattr(holding, key, value)
    db.commit()
    db.refresh(holding)
    return holding


@app.delete("/api/v1/portfolio/holdings/{holding_id}", status_code=204)
def delete_holding(holding_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    holding = get_owned_holding(holding_id, user.id, db)
    db.delete(holding)
    db.commit()


@app.get("/api/v1/portfolio/summary")
def portfolio_summary(user: User = Depends(current_user), db: Session = Depends(get_db)):
    holdings = db.scalars(select(Holding).where(Holding.user_id == user.id)).all()
    invested = sum(item.invested_amount for item in holdings)
    current = sum(item.current_value for item in holdings)
    by_category: dict[str, float] = defaultdict(float)
    by_sector: dict[str, float] = defaultdict(float)
    by_country: dict[str, float] = defaultdict(float)
    for item in holdings:
        by_category[item.category] += item.current_value
        by_sector[item.sector] += item.current_value
        by_country[item.country] += item.current_value
    largest = max(by_sector.values(), default=0)
    concentration = largest / current if current else 0
    score = round(max(0, min(100, 100 - max(concentration - 0.25, 0) * 150 - max(3 - len(by_category), 0) * 8)))
    return {
        "total_invested": round(invested, 2), "current_value": round(current, 2),
        "profit_loss": round(current - invested, 2),
        "profit_loss_pct": round((current / invested - 1) * 100, 2) if invested else 0,
        "asset_allocation": [{"name": key, "value": round(value, 2)} for key, value in by_category.items()],
        "sector_allocation": [{"name": key, "value": round(value, 2)} for key, value in by_sector.items()],
        "country_allocation": [{"name": key, "value": round(value, 2)} for key, value in by_country.items()],
        "health_score": score,
        "suggestions": ([f"{concentration:.0%} of your recorded value is in one sector; consider checking your concentration risk."]
                        if concentration > 0.5 else ["Review your mix against your goals and time horizon."]),
        "price_data_note": "Current values are entered by you; live price refresh is planned for a later stage.",
        "disclaimer": DISCLAIMER,
    }


@app.post("/api/v1/tools/risk-profile")
def risk_profile(data: RiskQuiz):
    points = (min(data.time_horizon_years, 30) / 30 * 30
              + data.loss_tolerance_pct / 100 * 35
              + data.income_stability / 10 * 15
              + data.investing_experience / 10 * 10
              + (10 if data.emergency_fund_ready else 0))
    label = "Conservative" if points < 38 else "Moderate" if points < 68 else "Aggressive"
    allocations = {"Conservative": {"Equity": 25, "Debt": 50, "Gold": 10, "Cash": 15},
                   "Moderate": {"Equity": 50, "Debt": 30, "Gold": 10, "Cash": 10},
                   "Aggressive": {"Equity": 70, "Debt": 15, "Gold": 10, "Cash": 5}}
    return {"score": round(points), "profile": label, "sample_allocation_pct": allocations[label],
            "note": "This learning exercise is not a personal recommendation. Review your goals and ability to bear losses.",
            "disclaimer": DISCLAIMER}


@app.post("/api/v1/tools/emergency-fund")
def emergency_fund(data: EmergencyCheck):
    target = data.monthly_essential_expenses * data.target_months
    return {"target": round(target, 2), "current": data.current_reserve,
            "gap": round(max(target - data.current_reserve, 0), 2),
            "months_covered": round(data.current_reserve / data.monthly_essential_expenses, 1),
            "disclaimer": DISCLAIMER}


@app.post("/api/v1/tools/sip-calculator")
def sip_calculator(data: SIPInput):
    rate = (1 + data.annual_return_pct / 100) ** (1 / 12) - 1
    months = data.years * 12
    value = data.monthly_amount * months if rate == 0 else data.monthly_amount * (((1 + rate) ** months - 1) / rate) * (1 + rate)
    real = value / ((1 + data.inflation_pct / 100) ** data.years)
    return {"invested": round(data.monthly_amount * months, 2), "estimated_value": round(value, 2),
            "inflation_adjusted_value": round(real, 2), "assumed_annual_return_pct": data.annual_return_pct,
            "disclaimer": DISCLAIMER}


@app.post("/api/v1/tools/lumpsum-calculator")
def lumpsum_calculator(data: LumpSumInput):
    value = data.amount * (1 + data.annual_return_pct / 100) ** data.years
    real = value / ((1 + data.inflation_pct / 100) ** data.years)
    return {"invested": data.amount, "estimated_value": round(value, 2),
            "inflation_adjusted_value": round(real, 2), "disclaimer": DISCLAIMER}


@app.post("/api/v1/tools/goal-planner")
def goal_planner(data: GoalInput):
    target = data.target_amount * (1 + data.inflation_pct / 100) ** data.years
    monthly_return = (1 + data.annual_return_pct / 100) ** (1 / 12) - 1
    months = data.years * 12
    current_future_value = data.current_savings * (1 + monthly_return) ** months
    gap = max(target - current_future_value, 0)
    factor = months if monthly_return == 0 else ((1 + monthly_return) ** months - 1) / monthly_return
    return {"inflation_adjusted_target": round(target, 2), "monthly_saving_estimate": round(gap / factor, 2),
            "disclaimer": DISCLAIMER}


@app.post("/api/v1/tools/monte-carlo")
def monte_carlo(data: SIPInput):
    """Illustrative 1,000-path simulation with 10th, 50th, and 90th percentiles."""
    months = data.years * 12
    annual = data.annual_return_pct / 100
    monthly_mean = (1 + annual) ** (1 / 12) - 1
    volatility = min(max(abs(annual) * 0.65, 0.04), 0.45) / np.sqrt(12)
    rng = np.random.default_rng(2026)
    monthly_changes = rng.normal(monthly_mean, volatility, (1000, months))
    values = np.zeros(1000)
    for index in range(months):
        values = np.maximum((values + data.monthly_amount) * (1 + monthly_changes[:, index]), 0)
    p10, p50, p90 = np.percentile(values, [10, 50, 90])
    return {"percentiles": {"p10": round(float(p10), 2), "p50": round(float(p50), 2), "p90": round(float(p90), 2)},
            "paths": 1000, "assumed_annual_return_pct": data.annual_return_pct,
            "disclaimer": DISCLAIMER}


@app.get("/api/v1/tools/compare")
def compare_investments(slugs: str, db: Session = Depends(get_db)):
    wanted = [slug.strip() for slug in slugs.split(",") if slug.strip()]
    if not 2 <= len(wanted) <= 3:
        raise HTTPException(status_code=422, detail="Compare two or three guide slugs.")
    records = db.scalars(select(InvestmentGuide).where(InvestmentGuide.slug.in_(wanted))).all()
    by_slug = {record.slug: record for record in records}
    if len(by_slug) != len(wanted):
        raise HTTPException(status_code=404, detail="One or more investment guides were not found.")
    fields = ("name", "risk_level", "historical_return_range", "time_horizon", "minimum_amount", "liquidity", "tax_note", "pros", "cons")
    return {"items": [{field: getattr(by_slug[slug], field) for field in fields} for slug in wanted], "disclaimer": DISCLAIMER}
