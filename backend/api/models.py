"""Persisted users, holdings, and educational investment guides."""

from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    holdings: Mapped[list["Holding"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Holding(Base):
    __tablename__ = "holdings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    asset_type: Mapped[str] = mapped_column(String(80))
    name: Mapped[str] = mapped_column(String(180))
    ticker: Mapped[str | None] = mapped_column(String(40), nullable=True)
    category: Mapped[str] = mapped_column(String(80), default="Other")
    sector: Mapped[str] = mapped_column(String(100), default="Unclassified")
    country: Mapped[str] = mapped_column(String(80), default="India")
    quantity: Mapped[float] = mapped_column(Float, default=1)
    invested_amount: Mapped[float] = mapped_column(Float)
    current_value: Mapped[float] = mapped_column(Float)
    buy_price: Mapped[float] = mapped_column(Float)
    buy_date: Mapped[date] = mapped_column(Date)
    platform: Mapped[str | None] = mapped_column(String(120), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    user: Mapped[User] = relationship(back_populates="holdings")


class InvestmentGuide(Base):
    __tablename__ = "investment_guides"
    __table_args__ = (UniqueConstraint("slug", name="uq_investment_guides_slug"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(100), index=True)
    name: Mapped[str] = mapped_column(String(180))
    region: Mapped[str] = mapped_column(String(30), index=True)
    category: Mapped[str] = mapped_column(String(80), index=True)
    risk_level: Mapped[str] = mapped_column(String(20))
    what_is_it: Mapped[str] = mapped_column(Text)
    how_it_works: Mapped[str] = mapped_column(Text)
    example: Mapped[str] = mapped_column(Text)
    how_you_may_earn: Mapped[str] = mapped_column(Text)
    historical_return_range: Mapped[str] = mapped_column(String(100))
    time_horizon: Mapped[str] = mapped_column(String(80))
    minimum_amount: Mapped[str] = mapped_column(String(100))
    liquidity: Mapped[str] = mapped_column(String(180))
    tax_note: Mapped[str] = mapped_column(Text)
    suitable_for: Mapped[str] = mapped_column(Text)
    avoid_if: Mapped[str] = mapped_column(Text)
    common_mistakes: Mapped[str] = mapped_column(Text)
    pros: Mapped[str] = mapped_column(Text)
    cons: Mapped[str] = mapped_column(Text)
    explain_like_15: Mapped[str] = mapped_column(Text)
    warning: Mapped[str | None] = mapped_column(Text, nullable=True)
