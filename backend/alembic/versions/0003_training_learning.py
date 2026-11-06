"""expand training into a lesson-based learning module"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003_training_learning"
down_revision = "0002_document_management"
branch_labels = None
depends_on = None


def uuid_type():
    return postgresql.UUID(as_uuid=True)


def upgrade():
    op.add_column("training_courses", sa.Column("category", sa.String(80), nullable=True))
    op.add_column("training_courses", sa.Column("level", sa.String(24), nullable=False, server_default="beginner"))
    op.add_column("training_courses", sa.Column("thumbnail_url", sa.String(1000), nullable=True))
    op.add_column("training_courses", sa.Column("published", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("training_assignments", sa.Column("last_accessed_at", sa.DateTime(), nullable=True))
    op.add_column("training_assignments", sa.Column("assessment_score", sa.Float(), nullable=True))
    op.add_column("training_assignments", sa.Column("certificate_code", sa.String(80), nullable=True))
    op.create_unique_constraint("uq_training_assignment_certificate_code", "training_assignments", ["certificate_code"])
    op.create_table(
        "training_lessons",
        sa.Column("id", uuid_type(), nullable=False),
        sa.Column("course_id", uuid_type(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("resource_url", sa.String(1000), nullable=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_preview", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["course_id"], ["training_courses.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_training_lessons_course_id", "training_lessons", ["course_id"])
    op.create_table(
        "training_lesson_progress",
        sa.Column("id", uuid_type(), nullable=False),
        sa.Column("assignment_id", uuid_type(), nullable=False),
        sa.Column("lesson_id", uuid_type(), nullable=False),
        sa.Column("is_completed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["assignment_id"], ["training_assignments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["lesson_id"], ["training_lessons.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("assignment_id", "lesson_id", name="uq_training_assignment_lesson"),
    )
    op.create_index("ix_training_lesson_progress_assignment_id", "training_lesson_progress", ["assignment_id"])
    op.create_index("ix_training_lesson_progress_lesson_id", "training_lesson_progress", ["lesson_id"])
    op.create_table(
        "training_certificates",
        sa.Column("id", uuid_type(), nullable=False),
        sa.Column("assignment_id", uuid_type(), nullable=False),
        sa.Column("organization_id", uuid_type(), nullable=False),
        sa.Column("employee_id", uuid_type(), nullable=False),
        sa.Column("course_title", sa.String(255), nullable=False),
        sa.Column("certificate_code", sa.String(80), nullable=False),
        sa.Column("issued_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["assignment_id"], ["training_assignments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("assignment_id"),
        sa.UniqueConstraint("certificate_code"),
    )
    op.create_index("ix_training_certificates_organization_id", "training_certificates", ["organization_id"])
    op.create_index("ix_training_certificates_employee_id", "training_certificates", ["employee_id"])
    op.create_index("ix_training_certificates_certificate_code", "training_certificates", ["certificate_code"])


def downgrade():
    op.drop_table("training_certificates")
    op.drop_table("training_lesson_progress")
    op.drop_table("training_lessons")
    op.drop_constraint("uq_training_assignment_certificate_code", "training_assignments", type_="unique")
    for column in ("certificate_code", "assessment_score", "last_accessed_at"):
        op.drop_column("training_assignments", column)
    for column in ("published", "thumbnail_url", "level", "category"):
        op.drop_column("training_courses", column)
