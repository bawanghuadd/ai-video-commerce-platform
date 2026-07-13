"""Create the Phase 1 application schema.

Revision ID: 20260713_0001
Revises: None
"""
from alembic import op
import sqlalchemy as sa


revision = "20260713_0001"
down_revision = None
branch_labels = None
depends_on = None


def timestamps():
    return (
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("display_name", sa.String(50), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(30), nullable=False, server_default="user"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        *timestamps(),
        sa.UniqueConstraint("username", name="uq_users_username"),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("product_name", sa.String(100), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("stock", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("selling_points", sa.Text(), nullable=True),
        sa.Column("target_audience", sa.String(200), nullable=True),
        *timestamps(),
    )
    op.create_index("ix_products_id", "products", ["id"])
    op.create_index("ix_products_product_name", "products", ["product_name"])

    op.create_table(
        "content_analyses",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("platform", sa.String(30), nullable=False, server_default="抖音"),
        sa.Column("content_title", sa.String(200), nullable=False),
        sa.Column("source_url", sa.String(500), nullable=True),
        sa.Column("opening_hook", sa.Text(), nullable=True),
        sa.Column("content_structure", sa.Text(), nullable=True),
        sa.Column("selling_point_expression", sa.Text(), nullable=True),
        sa.Column("target_audience", sa.String(200), nullable=True),
        sa.Column("analysis_result", sa.Text(), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="待拆解"),
        *timestamps(),
    )
    op.create_index("ix_content_analyses_id", "content_analyses", ["id"])
    op.create_index("ix_content_analyses_product_id", "content_analyses", ["product_id"])

    op.create_table(
        "scripts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("content_analysis_id", sa.Integer(), sa.ForeignKey("content_analyses.id", ondelete="SET NULL"), nullable=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("platform", sa.String(30), nullable=False, server_default="抖音"),
        sa.Column("script_type", sa.String(50), nullable=False, server_default="带货短视频"),
        sa.Column("opening_hook", sa.Text(), nullable=True),
        sa.Column("full_script", sa.Text(), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("status", sa.String(30), nullable=False, server_default="草稿"),
        *timestamps(),
    )
    op.create_index("ix_scripts_id", "scripts", ["id"])
    op.create_index("ix_scripts_product_id", "scripts", ["product_id"])
    op.create_index("ix_scripts_content_analysis_id", "scripts", ["content_analysis_id"])
    op.create_index("ix_scripts_title", "scripts", ["title"])
    op.create_index("ix_scripts_status", "scripts", ["status"])

    op.create_table(
        "script_scenes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("script_id", sa.Integer(), sa.ForeignKey("scripts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scene_number", sa.Integer(), nullable=False),
        sa.Column("duration_seconds", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("shot_type", sa.String(50), nullable=True),
        sa.Column("visual_content", sa.Text(), nullable=False),
        sa.Column("voiceover", sa.Text(), nullable=True),
        sa.Column("subtitle", sa.Text(), nullable=True),
        sa.Column("camera_movement", sa.String(200), nullable=True),
        *timestamps(),
        sa.UniqueConstraint("script_id", "scene_number", name="uq_script_scene_number"),
    )
    op.create_index("ix_script_scenes_id", "script_scenes", ["id"])
    op.create_index("ix_script_scenes_script_id", "script_scenes", ["script_id"])

    op.create_table(
        "video_tasks",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("script_id", sa.Integer(), sa.ForeignKey("scripts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("platform", sa.String(30), nullable=False, server_default="抖音"),
        sa.Column("assignee", sa.String(100), nullable=False, server_default="未分配"),
        sa.Column("status", sa.String(30), nullable=False, server_default="待制作"),
        sa.Column("duration_seconds", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("resolution", sa.String(30), nullable=False, server_default="1080P"),
        sa.Column("cover_url", sa.String(500), nullable=True),
        sa.Column("video_url", sa.String(500), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        *timestamps(),
    )
    for name in ("id", "product_id", "script_id", "title", "status"):
        op.create_index(f"ix_video_tasks_{name}", "video_tasks", [name])

    op.create_table(
        "knowledge_items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="SET NULL"), nullable=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("summary", sa.String(500), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("source_type", sa.String(50), nullable=False, server_default="手动录入"),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="草稿"),
        sa.Column("is_featured", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("usage_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_by", sa.String(100), nullable=False, server_default="系统管理员"),
        *timestamps(),
    )
    for name in ("id", "product_id", "title", "category", "status", "is_featured"):
        op.create_index(f"ix_knowledge_items_{name}", "knowledge_items", [name])

    op.create_table(
        "system_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("platform_name", sa.String(100), nullable=False, server_default="AI短视频电商平台"),
        sa.Column("platform_subtitle", sa.String(200), nullable=False, server_default="AI驱动的短视频内容创作与电商增长平台"),
        sa.Column("default_platform", sa.String(30), nullable=False, server_default="抖音"),
        sa.Column("timezone", sa.String(50), nullable=False, server_default="Asia/Shanghai"),
        sa.Column("theme", sa.String(20), nullable=False, server_default="dark"),
        sa.Column("ai_provider", sa.String(50), nullable=False, server_default="OpenAI"),
        sa.Column("ai_model", sa.String(100), nullable=False, server_default="default"),
        sa.Column("temperature", sa.Float(), nullable=False, server_default="0.7"),
        sa.Column("enable_ai_generation", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("enable_auto_review", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("enable_notifications", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("updated_by", sa.String(100), nullable=False, server_default="系统管理员"),
        *timestamps(),
    )


def downgrade() -> None:
    op.drop_table("system_settings")
    op.drop_table("knowledge_items")
    op.drop_table("video_tasks")
    op.drop_table("script_scenes")
    op.drop_table("scripts")
    op.drop_table("content_analyses")
    op.drop_table("products")
    op.drop_table("users")
