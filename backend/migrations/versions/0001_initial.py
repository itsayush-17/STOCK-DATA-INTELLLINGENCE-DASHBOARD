"""Create accounts, holdings, and investment guide tables."""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_table(
        "holdings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("asset_type", sa.String(80), nullable=False),
        sa.Column("name", sa.String(180), nullable=False),
        sa.Column("ticker", sa.String(40)),
        sa.Column("category", sa.String(80), nullable=False),
        sa.Column("sector", sa.String(100), nullable=False),
        sa.Column("country", sa.String(80), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("invested_amount", sa.Float(), nullable=False),
        sa.Column("current_value", sa.Float(), nullable=False),
        sa.Column("buy_price", sa.Float(), nullable=False),
        sa.Column("buy_date", sa.Date(), nullable=False),
        sa.Column("platform", sa.String(120)),
        sa.Column("notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_holdings_user_id", "holdings", ["user_id"])
    op.create_table(
        "investment_guides",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("name", sa.String(180), nullable=False),
        sa.Column("region", sa.String(30), nullable=False),
        sa.Column("category", sa.String(80), nullable=False),
        sa.Column("risk_level", sa.String(20), nullable=False),
        sa.Column("what_is_it", sa.Text(), nullable=False),
        sa.Column("how_it_works", sa.Text(), nullable=False),
        sa.Column("example", sa.Text(), nullable=False),
        sa.Column("how_you_may_earn", sa.Text(), nullable=False),
        sa.Column("historical_return_range", sa.String(100), nullable=False),
        sa.Column("time_horizon", sa.String(80), nullable=False),
        sa.Column("minimum_amount", sa.String(100), nullable=False),
        sa.Column("liquidity", sa.String(180), nullable=False),
        sa.Column("tax_note", sa.Text(), nullable=False),
        sa.Column("suitable_for", sa.Text(), nullable=False),
        sa.Column("avoid_if", sa.Text(), nullable=False),
        sa.Column("common_mistakes", sa.Text(), nullable=False),
        sa.Column("pros", sa.Text(), nullable=False),
        sa.Column("cons", sa.Text(), nullable=False),
        sa.Column("explain_like_15", sa.Text(), nullable=False),
        sa.Column("warning", sa.Text()),
        sa.UniqueConstraint("slug", name="uq_investment_guides_slug"),
    )
    op.create_index("ix_investment_guides_slug", "investment_guides", ["slug"])
    op.create_index("ix_investment_guides_region", "investment_guides", ["region"])
    op.create_index("ix_investment_guides_category", "investment_guides", ["category"])


def downgrade() -> None:
    op.drop_index("ix_investment_guides_category", table_name="investment_guides")
    op.drop_index("ix_investment_guides_region", table_name="investment_guides")
    op.drop_index("ix_investment_guides_slug", table_name="investment_guides")
    op.drop_table("investment_guides")
    op.drop_index("ix_holdings_user_id", table_name="holdings")
    op.drop_table("holdings")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
