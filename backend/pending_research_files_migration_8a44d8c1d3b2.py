"""Pending Alembic migration for research_files.

The intended destination is:
backend/migrations/versions/8a44d8c1d3b2_add_research_files_table.py

That directory is currently not writable in this environment, so this file
preserves the migration content until permissions are fixed.
"""
from alembic import op
import sqlalchemy as sa


revision = "8a44d8c1d3b2"
down_revision = "d1f07fba9b6b"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "research_files",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("record_id", sa.UUID(), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("stored_filename", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("file_size", sa.BigInteger(), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["record_id"], ["research_records.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("record_id"),
        sa.UniqueConstraint("stored_filename"),
    )
    with op.batch_alter_table("research_files", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_research_files_record_id"), ["record_id"], unique=True)


def downgrade():
    with op.batch_alter_table("research_files", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_research_files_record_id"))

    op.drop_table("research_files")
