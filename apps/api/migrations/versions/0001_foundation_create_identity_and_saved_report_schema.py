"""Create identity and saved report schema."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001_foundation"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("locale", sa.String(length=16), nullable=False),
        sa.Column("theme", sa.String(length=8), nullable=False),
        sa.CheckConstraint("theme IN ('system', 'light', 'dark')", name=op.f("ck_accounts_theme")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_accounts")),
        sa.UniqueConstraint("email", name=op.f("uq_accounts_email")),
    )
    op.create_table(
        "auth_rate_limits",
        sa.Column("key_hash", sa.String(length=64), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("attempts >= 0", name=op.f("ck_auth_rate_limits_nonnegative_attempts")),
        sa.PrimaryKeyConstraint("key_hash", name=op.f("pk_auth_rate_limits")),
    )
    op.create_index(
        op.f("ix_auth_rate_limits_expires_at"), "auth_rate_limits", ["expires_at"], unique=False
    )
    op.create_table(
        "account_action_tokens",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("purpose", sa.String(length=20), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "purpose IN ('verify_email', 'reset_password')",
            name=op.f("ck_account_action_tokens_purpose"),
        ),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["accounts.id"],
            name=op.f("fk_account_action_tokens_account_id_accounts"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_account_action_tokens")),
        sa.UniqueConstraint("token_hash", name=op.f("uq_account_action_tokens_token_hash")),
    )
    op.create_index(
        op.f("ix_account_action_tokens_account_id"),
        "account_action_tokens",
        ["account_id"],
        unique=False,
    )
    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["accounts.id"],
            name=op.f("fk_auth_sessions_account_id_accounts"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_auth_sessions")),
        sa.UniqueConstraint("token_hash", name=op.f("uq_auth_sessions_token_hash")),
    )
    op.create_index(
        op.f("ix_auth_sessions_account_id"), "auth_sessions", ["account_id"], unique=False
    )
    op.create_table(
        "consent_records",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("version", sa.String(length=32), nullable=False),
        sa.Column("purpose", sa.String(length=24), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("withdrawn_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "purpose IN ('report_processing', 'retain_original')",
            name=op.f("ck_consent_records_purpose"),
        ),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["accounts.id"],
            name=op.f("fk_consent_records_account_id_accounts"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_consent_records")),
        sa.UniqueConstraint("id", "account_id", name=op.f("uq_consent_records_id")),
    )
    op.create_index(
        op.f("ix_consent_records_account_id"), "consent_records", ["account_id"], unique=False
    )
    op.create_table(
        "report_subjects",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=True),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["accounts.id"],
            name=op.f("fk_report_subjects_account_id_accounts"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_report_subjects")),
        sa.UniqueConstraint("account_id", name=op.f("uq_report_subjects_account_id")),
        sa.UniqueConstraint("id", "account_id", name=op.f("uq_report_subjects_id")),
    )
    op.create_table(
        "saved_reports",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("subject_id", sa.Uuid(), nullable=False),
        sa.Column("consent_id", sa.Uuid(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("collection_date", sa.Date(), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("saved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("superseded_by", sa.Uuid(), nullable=True),
        sa.Column("context", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.CheckConstraint("revision >= 1", name=op.f("ck_saved_reports_positive_revision")),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["accounts.id"],
            name=op.f("fk_saved_reports_account_id_accounts"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["consent_id", "account_id"],
            ["consent_records.id", "consent_records.account_id"],
            name=op.f("fk_saved_reports_consent_id_consent_records"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["subject_id", "account_id"],
            ["report_subjects.id", "report_subjects.account_id"],
            name=op.f("fk_saved_reports_subject_id_report_subjects"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["superseded_by"],
            ["saved_reports.id"],
            name=op.f("fk_saved_reports_superseded_by_saved_reports"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_saved_reports")),
        sa.UniqueConstraint("id", "account_id", name=op.f("uq_saved_reports_id")),
    )
    op.create_index(
        op.f("ix_saved_reports_account_id"), "saved_reports", ["account_id"], unique=False
    )
    op.create_table(
        "interpretation_snapshots",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("report_id", sa.Uuid(), nullable=False),
        sa.Column("threshold_version", sa.String(length=40), nullable=False),
        sa.Column("content_version", sa.String(length=40), nullable=True),
        sa.Column("outcome", sa.String(length=16), nullable=False),
        sa.Column("overall_status", sa.String(length=24), nullable=True),
        sa.Column("result", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "outcome IN ('classified','not_classified','out_of_scope')",
            name=op.f("ck_interpretation_snapshots_outcome"),
        ),
        sa.CheckConstraint(
            "overall_status IS NULL OR overall_status IN "
            "('normal','prediabetes_range','diabetes_range')",
            name=op.f("ck_interpretation_snapshots_overall_status"),
        ),
        sa.ForeignKeyConstraint(
            ["report_id"],
            ["saved_reports.id"],
            name=op.f("fk_interpretation_snapshots_report_id_saved_reports"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_interpretation_snapshots")),
    )
    op.create_index(
        op.f("ix_interpretation_snapshots_report_id"),
        "interpretation_snapshots",
        ["report_id"],
        unique=False,
    )
    op.create_table(
        "retained_report_assets",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("report_id", sa.Uuid(), nullable=False),
        sa.Column("retention_consent_id", sa.Uuid(), nullable=False),
        sa.Column("encrypted_object_key", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["report_id", "account_id"],
            ["saved_reports.id", "saved_reports.account_id"],
            name=op.f("fk_retained_report_assets_report_id_saved_reports"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["retention_consent_id", "account_id"],
            ["consent_records.id", "consent_records.account_id"],
            name=op.f("fk_retained_report_assets_retention_consent_id_consent_records"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_retained_report_assets")),
        sa.UniqueConstraint(
            "encrypted_object_key", name=op.f("uq_retained_report_assets_encrypted_object_key")
        ),
    )
    op.create_index(
        op.f("ix_retained_report_assets_report_id"),
        "retained_report_assets",
        ["report_id"],
        unique=False,
    )
    op.create_table(
        "reviewed_observations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("report_id", sa.Uuid(), nullable=False),
        sa.Column("test_name", sa.String(length=64), nullable=False),
        sa.Column("value", sa.Numeric(), nullable=False),
        sa.Column("value_text", sa.String(length=64), nullable=False),
        sa.Column("value_operator", sa.String(length=3), nullable=False),
        sa.Column("unit", sa.String(length=16), nullable=False),
        sa.Column("reference_interval", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("context", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("included", sa.Boolean(), nullable=False),
        sa.Column("exclusion_reason", sa.String(length=240), nullable=True),
        sa.CheckConstraint(
            "unit IN ('mg/dL','mmol/L','%%')", name=op.f("ck_reviewed_observations_unit")
        ),
        sa.CheckConstraint(
            "value_operator IN ('eq','lt','lte','gt','gte')",
            name=op.f("ck_reviewed_observations_value_operator"),
        ),
        sa.CheckConstraint("value > 0", name=op.f("ck_reviewed_observations_positive_value")),
        sa.ForeignKeyConstraint(
            ["report_id"],
            ["saved_reports.id"],
            name=op.f("fk_reviewed_observations_report_id_saved_reports"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_reviewed_observations")),
    )
    op.create_index(
        op.f("ix_reviewed_observations_report_id"),
        "reviewed_observations",
        ["report_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_reviewed_observations_report_id"), table_name="reviewed_observations")
    op.drop_table("reviewed_observations")
    op.drop_index(op.f("ix_retained_report_assets_report_id"), table_name="retained_report_assets")
    op.drop_table("retained_report_assets")
    op.drop_index(
        op.f("ix_interpretation_snapshots_report_id"), table_name="interpretation_snapshots"
    )
    op.drop_table("interpretation_snapshots")
    op.drop_index(op.f("ix_saved_reports_account_id"), table_name="saved_reports")
    op.drop_table("saved_reports")
    op.drop_table("report_subjects")
    op.drop_index(op.f("ix_consent_records_account_id"), table_name="consent_records")
    op.drop_table("consent_records")
    op.drop_index(op.f("ix_auth_sessions_account_id"), table_name="auth_sessions")
    op.drop_table("auth_sessions")
    op.drop_index(op.f("ix_account_action_tokens_account_id"), table_name="account_action_tokens")
    op.drop_table("account_action_tokens")
    op.drop_index(op.f("ix_auth_rate_limits_expires_at"), table_name="auth_rate_limits")
    op.drop_table("auth_rate_limits")
    op.drop_table("accounts")
