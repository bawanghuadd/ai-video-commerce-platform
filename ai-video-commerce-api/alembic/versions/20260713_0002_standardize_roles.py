"""Standardize admin/editor/viewer roles.

Revision ID: 20260713_0002
Revises: 20260713_0001
"""
from alembic import op
import sqlalchemy as sa


revision = "20260713_0002"
down_revision = "20260713_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(sa.text("UPDATE users SET role = 'editor' WHERE role = 'user'"))
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "role",
            existing_type=sa.String(length=30),
            existing_nullable=False,
            server_default="viewer",
        )


def downgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "role",
            existing_type=sa.String(length=30),
            existing_nullable=False,
            server_default="user",
        )
    op.execute(sa.text("UPDATE users SET role = 'user' WHERE role = 'editor'"))
