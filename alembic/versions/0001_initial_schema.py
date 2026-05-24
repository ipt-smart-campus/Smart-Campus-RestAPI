"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-05-24

"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── buildings ──────────────────────────────────────────
    op.create_table(
        "buildings",
        sa.Column("id",          sa.String(10),  primary_key=True),
        sa.Column("name",        sa.String(100), nullable=False),
        sa.Column("description", sa.String(255), nullable=True),
        sa.Column("latitude",    sa.Float(),     nullable=False),
        sa.Column("longitude",   sa.Float(),     nullable=False),
    )

    # ── rooms ──────────────────────────────────────────────
    op.create_table(
        "rooms",
        sa.Column("id",          sa.String(20),  primary_key=True),
        sa.Column("name",        sa.String(100), nullable=False),
        sa.Column("floor",       sa.Integer(),   nullable=False, server_default="0"),
        sa.Column("capacity",    sa.Integer(),   nullable=False, server_default="30"),
        sa.Column("type",        sa.String(50),  nullable=False, server_default="classroom"),
        sa.Column("building_id", sa.String(10),
                  sa.ForeignKey("buildings.id", ondelete="CASCADE"), nullable=False),
    )

    # ── sensors ────────────────────────────────────────────
    op.create_table(
        "sensors",
        sa.Column("id",          sa.String(50),  primary_key=True),
        sa.Column("type",        sa.String(30),  nullable=False),
        sa.Column("unit",        sa.String(10),  nullable=False),
        sa.Column("description", sa.String(200), nullable=True),
        sa.Column("active",      sa.Boolean(),   nullable=False, server_default="true"),
        sa.Column("room_id",     sa.String(20),
                  sa.ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False),
    )

    # ── sensor_readings ────────────────────────────────────
    op.create_table(
        "sensor_readings",
        sa.Column("id",        sa.Integer(),                  primary_key=True, autoincrement=True),
        sa.Column("sensor_id", sa.String(50),
                  sa.ForeignKey("sensors.id", ondelete="CASCADE"), nullable=False),
        sa.Column("value",     sa.Float(),                    nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True),    nullable=False),
    )
    op.create_index("ix_readings_sensor_time", "sensor_readings", ["sensor_id", "timestamp"])

    # ── alerts ─────────────────────────────────────────────
    op.create_table(
        "alerts",
        sa.Column("id",          sa.Integer(),               primary_key=True, autoincrement=True),
        sa.Column("sensor_id",   sa.String(50),
                  sa.ForeignKey("sensors.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type",        sa.String(30),              nullable=False),
        sa.Column("message",     sa.String(500),             nullable=False),
        sa.Column("value",       sa.Float(),                 nullable=False),
        sa.Column("resolved",    sa.Boolean(),               nullable=False, server_default="false"),
        sa.Column("created_at",  sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_alerts_sensor_resolved", "alerts", ["sensor_id", "resolved"])


def downgrade() -> None:
    op.drop_table("alerts")
    op.drop_table("sensor_readings")
    op.drop_table("sensors")
    op.drop_table("rooms")
    op.drop_table("buildings")