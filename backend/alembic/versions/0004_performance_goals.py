"""add performance goals, review cycles, feedback and improvement plans"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0004_performance_goals"
down_revision = "0003_training_learning"
branch_labels = None
depends_on = None
UUID = postgresql.UUID(as_uuid=True)


def upgrade():
    op.create_table("performance_goals",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("organization_id", UUID, sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("owner_id", UUID, sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_by", UUID, sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("title", sa.String(240), nullable=False), sa.Column("description", sa.Text()),
        sa.Column("goal_type", sa.String(32), nullable=False, server_default="individual"),
        sa.Column("status", sa.String(24), nullable=False, server_default="not_started"),
        sa.Column("priority", sa.String(16), nullable=False, server_default="medium"),
        sa.Column("progress", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("start_date", sa.DateTime()), sa.Column("due_date", sa.DateTime()),
        sa.Column("completed_at", sa.DateTime()), sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("organization_id", "title", "owner_id", name="uq_performance_goal_owner_title"))
    op.create_index("ix_performance_goals_organization_id", "performance_goals", ["organization_id"])
    op.create_index("ix_performance_goals_owner_id", "performance_goals", ["owner_id"])
    op.create_table("performance_key_results",
        sa.Column("id", UUID, primary_key=True), sa.Column("goal_id", UUID, sa.ForeignKey("performance_goals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(240), nullable=False), sa.Column("metric", sa.String(80)),
        sa.Column("start_value", sa.Float(), nullable=False, server_default="0"), sa.Column("target_value", sa.Float(), nullable=False, server_default="100"),
        sa.Column("current_value", sa.Float(), nullable=False, server_default="0"), sa.Column("weight", sa.Float(), nullable=False, server_default="1"),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"), sa.Column("updated_at", sa.DateTime(), nullable=False))
    op.create_index("ix_performance_key_results_goal_id", "performance_key_results", ["goal_id"])
    op.create_table("performance_review_cycles",
        sa.Column("id", UUID, primary_key=True), sa.Column("organization_id", UUID, sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(160), nullable=False), sa.Column("description", sa.Text()), sa.Column("cycle_type", sa.String(24), nullable=False, server_default="quarterly"),
        sa.Column("starts_at", sa.DateTime(), nullable=False), sa.Column("ends_at", sa.DateTime(), nullable=False), sa.Column("self_review_deadline", sa.DateTime()),
        sa.Column("manager_review_deadline", sa.DateTime()), sa.Column("status", sa.String(24), nullable=False, server_default="draft"),
        sa.Column("created_by", UUID, sa.ForeignKey("users.id", ondelete="SET NULL")), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_index("ix_performance_review_cycles_organization_id", "performance_review_cycles", ["organization_id"])
    op.create_table("performance_reviews",
        sa.Column("id", UUID, primary_key=True), sa.Column("organization_id", UUID, sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("cycle_id", UUID, sa.ForeignKey("performance_review_cycles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("employee_id", UUID, sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("manager_id", UUID, sa.ForeignKey("employees.id", ondelete="SET NULL")), sa.Column("self_rating", sa.Float()), sa.Column("manager_rating", sa.Float()),
        sa.Column("self_summary", sa.Text()), sa.Column("manager_summary", sa.Text()), sa.Column("strengths", sa.Text()), sa.Column("growth_areas", sa.Text()),
        sa.Column("status", sa.String(24), nullable=False, server_default="not_started"), sa.Column("submitted_at", sa.DateTime()),
        sa.Column("reviewed_at", sa.DateTime()), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("cycle_id", "employee_id", name="uq_performance_review_cycle_employee"))
    for col in ("organization_id", "cycle_id", "employee_id"):
        op.create_index(f"ix_performance_reviews_{col}", "performance_reviews", [col])
    op.create_table("performance_feedback",
        sa.Column("id", UUID, primary_key=True), sa.Column("organization_id", UUID, sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("review_id", UUID, sa.ForeignKey("performance_reviews.id", ondelete="CASCADE"), nullable=False),
        sa.Column("author_id", UUID, sa.ForeignKey("users.id", ondelete="SET NULL")), sa.Column("feedback_type", sa.String(24), nullable=False, server_default="peer"),
        sa.Column("rating", sa.Float()), sa.Column("strengths", sa.Text()), sa.Column("suggestions", sa.Text()),
        sa.Column("is_anonymous", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_index("ix_performance_feedback_organization_id", "performance_feedback", ["organization_id"])
    op.create_index("ix_performance_feedback_review_id", "performance_feedback", ["review_id"])
    op.create_table("performance_improvement_plans",
        sa.Column("id", UUID, primary_key=True), sa.Column("organization_id", UUID, sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("employee_id", UUID, sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False),
        sa.Column("review_id", UUID, sa.ForeignKey("performance_reviews.id", ondelete="SET NULL")),
        sa.Column("created_by", UUID, sa.ForeignKey("users.id", ondelete="SET NULL")), sa.Column("title", sa.String(200), nullable=False),
        sa.Column("objectives", sa.Text(), nullable=False), sa.Column("support_plan", sa.Text()), sa.Column("status", sa.String(24), nullable=False, server_default="active"),
        sa.Column("starts_at", sa.DateTime(), nullable=False), sa.Column("ends_at", sa.DateTime(), nullable=False), sa.Column("outcome_notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_index("ix_performance_improvement_plans_organization_id", "performance_improvement_plans", ["organization_id"])
    op.create_index("ix_performance_improvement_plans_employee_id", "performance_improvement_plans", ["employee_id"])


def downgrade():
    for table in ("performance_improvement_plans", "performance_feedback", "performance_reviews", "performance_review_cycles", "performance_key_results", "performance_goals"):
        op.drop_table(table)
