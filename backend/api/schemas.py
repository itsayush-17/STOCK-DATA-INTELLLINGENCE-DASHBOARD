"""Validated request and response shapes for the public API."""

from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    created_at: datetime


class TokenRead(BaseModel):
    access_token: str
    token_type: str = "bearer"


class HoldingInput(BaseModel):
    asset_type: str = Field(min_length=1, max_length=80)
    name: str = Field(min_length=1, max_length=180)
    ticker: str | None = Field(default=None, max_length=40)
    category: str = Field(default="Other", max_length=80)
    sector: str = Field(default="Unclassified", max_length=100)
    country: str = Field(default="India", max_length=80)
    quantity: float = Field(default=1, gt=0, le=1e12)
    invested_amount: float = Field(gt=0, le=1e15)
    current_value: float = Field(gt=0, le=1e15)
    buy_price: float = Field(gt=0, le=1e15)
    buy_date: date
    platform: str | None = Field(default=None, max_length=120)
    notes: str | None = Field(default=None, max_length=5000)


class HoldingRead(HoldingInput):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime


class RiskQuiz(BaseModel):
    time_horizon_years: int = Field(ge=0, le=80)
    loss_tolerance_pct: int = Field(ge=0, le=100)
    income_stability: int = Field(ge=1, le=10)
    investing_experience: int = Field(ge=1, le=10)
    emergency_fund_ready: bool


class EmergencyCheck(BaseModel):
    monthly_essential_expenses: float = Field(gt=0, le=1e12)
    current_reserve: float = Field(ge=0, le=1e15)
    target_months: int = Field(default=6, ge=3, le=12)


class SIPInput(BaseModel):
    monthly_amount: float = Field(gt=0, le=1e12)
    annual_return_pct: float = Field(ge=-99, le=100)
    years: int = Field(ge=1, le=80)
    inflation_pct: float = Field(default=0, ge=0, le=50)


class LumpSumInput(BaseModel):
    amount: float = Field(gt=0, le=1e15)
    annual_return_pct: float = Field(ge=-99, le=100)
    years: int = Field(ge=1, le=80)
    inflation_pct: float = Field(default=0, ge=0, le=50)


class GoalInput(BaseModel):
    target_amount: float = Field(gt=0, le=1e15)
    current_savings: float = Field(default=0, ge=0, le=1e15)
    years: int = Field(ge=1, le=80)
    annual_return_pct: float = Field(default=6, ge=-99, le=100)
    inflation_pct: float = Field(default=0, ge=0, le=50)
