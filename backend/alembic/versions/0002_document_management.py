"""document management lifecycle, access, versions and retention"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_document_management"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def _uuid():
    return postgresql.UUID(as_uuid=True)


def upgrade():
    additions = [
        sa.Column("title", sa.String(180), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(80), nullable=True),
        sa.Column("lifecycle", sa.String(32), nullable=False, server_default="submitted"),
        sa.Column("visibility", sa.String(32), nullable=False, server_default="employee_and_hr"),
        sa.Column("checksum_sha256", sa.String(64), nullable=True),
        sa.Column("scan_status", sa.String(24), nullable=False, server_default="not_scanned"),
        sa.Column("current_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("archived_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("created_by", _uuid(), nullable=True),
        sa.Column("updated_by", _uuid(), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=True),
    ]
    for column in additions:
        op.add_column("documents", column)
    with op.batch_alter_table("documents") as batch:
        batch.create_foreign_key("fk_documents_created_by_users", "users", ["created_by"], ["id"], ondelete="SET NULL")
        batch.create_foreign_key("fk_documents_updated_by_users", "users", ["updated_by"], ["id"], ondelete="SET NULL")
    op.create_index("ix_documents_category", "documents", ["category"])
    op.create_index("ix_documents_lifecycle", "documents", ["lifecycle"])
    op.create_index("ix_documents_checksum_sha256", "documents", ["checksum_sha256"])
    op.create_index("ix_documents_expires_at", "documents", ["expires_at"])

    op.add_column("document_reviews", sa.Column("decision", sa.String(32), nullable=True))
    op.add_column("document_reviews", sa.Column("previous_status", sa.String(32), nullable=True))
    op.add_column("document_reviews", sa.Column("assigned_to", _uuid(), nullable=True))
    op.add_column("document_reviews", sa.Column("due_at", sa.DateTime(), nullable=True))
    with op.batch_alter_table("document_reviews") as batch:
        batch.create_foreign_key("fk_document_reviews_assigned_to_users", "users", ["assigned_to"], ["id"], ondelete="SET NULL")

    op.create_table(
        "document_versions",
        sa.Column("id", _uuid(), nullable=False),
        sa.Column("document_id", _uuid(), nullable=False),
        sa.Column("organization_id", _uuid(), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_path", sa.String(500), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("checksum_sha256", sa.String(64), nullable=False),
        sa.Column("change_note", sa.String(1000), nullable=True),
        sa.Column("uploaded_by", _uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("document_id", "version_number", name="uq_document_version_number"),
    )
    op.create_index("ix_document_versions_document_id", "document_versions", ["document_id"])
    op.create_index("ix_document_versions_organization_id", "document_versions", ["organization_id"])
    op.create_index("ix_document_versions_checksum_sha256", "document_versions", ["checksum_sha256"])

    op.create_table(
        "document_access_grants",
        sa.Column("id", _uuid(), nullable=False),
        sa.Column("document_id", _uuid(), nullable=False),
        sa.Column("organization_id", _uuid(), nullable=False),
        sa.Column("user_id", _uuid(), nullable=False),
        sa.Column("granted_by", _uuid(), nullable=True),
        sa.Column("permission", sa.String(24), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["granted_by"], ["users.id"], ondelete="SET NULL"),
    )
    for column in ("document_id", "organization_id", "user_id"):
        op.create_index(f"ix_document_access_grants_{column}", "document_access_grants", [column])

    op.create_table(
        "document_tags",
        sa.Column("id", _uuid(), nullable=False),
        sa.Column("document_id", _uuid(), nullable=False),
        sa.Column("organization_id", _uuid(), nullable=False),
        sa.Column("name", sa.String(48), nullable=False),
        sa.Column("normalized_name", sa.String(48), nullable=False),
        sa.Column("created_by", _uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("document_id", "normalized_name", name="uq_document_tag_name"),
    )
    for column in ("document_id", "organization_id", "normalized_name"):
        op.create_index(f"ix_document_tags_{column}", "document_tags", [column])

    op.create_table(
        "document_activities",
        sa.Column("id", _uuid(), nullable=False),
        sa.Column("document_id", _uuid(), nullable=False),
        sa.Column("organization_id", _uuid(), nullable=False),
        sa.Column("actor_id", _uuid(), nullable=True),
        sa.Column("event_type", sa.String(48), nullable=False),
        sa.Column("summary", sa.String(500), nullable=False),
        sa.Column("details_json", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"], ondelete="SET NULL"),
    )
    for column in ("document_id", "organization_id", "event_type", "created_at"):
        op.create_index(f"ix_document_activities_{column}", "document_activities", [column])

    op.create_table(
        "document_comments",
        sa.Column("id", _uuid(), nullable=False),
        sa.Column("document_id", _uuid(), nullable=False),
        sa.Column("organization_id", _uuid(), nullable=False),
        sa.Column("author_id", _uuid(), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("is_internal", sa.Boolean(), nullable=False),
        sa.Column("parent_id", _uuid(), nullable=True),
        sa.Column("edited_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["parent_id"], ["document_comments.id"], ondelete="CASCADE"),
    )
    for column in ("document_id", "organization_id"):
        op.create_index(f"ix_document_comments_{column}", "document_comments", [column])

    op.create_table(
        "document_retention_policies",
        sa.Column("id", _uuid(), nullable=False),
        sa.Column("organization_id", _uuid(), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("category", sa.String(80), nullable=True),
        sa.Column("retention_days", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(24), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_by", _uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_document_retention_policies_organization_id", "document_retention_policies", ["organization_id"])

    op.create_table(
        "document_shares",
        sa.Column("id", _uuid(), nullable=False),
        sa.Column("document_id", _uuid(), nullable=False),
        sa.Column("organization_id", _uuid(), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("created_by", _uuid(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("max_downloads", sa.Integer(), nullable=True),
        sa.Column("download_count", sa.Integer(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index("ix_document_shares_document_id", "document_shares", ["document_id"])
    op.create_index("ix_document_shares_organization_id", "document_shares", ["organization_id"])
    op.create_index("ix_document_shares_token_hash", "document_shares", ["token_hash"])

    op.create_table(
        "document_retention_executions",
        sa.Column("id", _uuid(), nullable=False),
        sa.Column("policy_id", _uuid(), nullable=True),
        sa.Column("document_id", _uuid(), nullable=False),
        sa.Column("organization_id", _uuid(), nullable=False),
        sa.Column("action", sa.String(24), nullable=False),
        sa.Column("result", sa.String(24), nullable=False),
        sa.Column("executed_by", _uuid(), nullable=True),
        sa.Column("executed_at", sa.DateTime(), nullable=False),
        sa.Column("details", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["policy_id"], ["document_retention_policies.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["executed_by"], ["users.id"], ondelete="SET NULL"),
    )
    for column in ("document_id", "organization_id"):
        op.create_index(f"ix_document_retention_executions_{column}", "document_retention_executions", [column])


def downgrade():
    for table in (
        "document_retention_executions", "document_shares", "document_retention_policies",
        "document_comments", "document_activities", "document_tags",
        "document_access_grants", "document_versions",
    ):
        op.drop_table(table)
    with op.batch_alter_table("document_reviews") as batch:
        batch.drop_constraint("fk_document_reviews_assigned_to_users", type_="foreignkey")
        for column in ("decision", "previous_status", "assigned_to", "due_at"):
            batch.drop_column(column)
    with op.batch_alter_table("documents") as batch:
        batch.drop_constraint("fk_documents_created_by_users", type_="foreignkey")
        batch.drop_constraint("fk_documents_updated_by_users", type_="foreignkey")
    for index in ("ix_documents_category", "ix_documents_lifecycle", "ix_documents_checksum_sha256", "ix_documents_expires_at"):
        op.drop_index(index, table_name="documents")
    for column in (
        "title", "description", "category", "lifecycle", "visibility", "checksum_sha256",
        "scan_status", "current_version", "expires_at", "archived_at", "deleted_at",
        "created_by", "updated_by", "metadata_json",
    ):
        op.drop_column("documents", column)
