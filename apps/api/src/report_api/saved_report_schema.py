from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from report_api.identity_schema import ReportBase, utc_now


class SavedReport(ReportBase):
    __tablename__ = "saved_reports"
    __table_args__ = (
        ForeignKeyConstraint(
            ["subject_id", "account_id"],
            ["report_subjects.id", "report_subjects.account_id"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["consent_id", "account_id"],
            ["consent_records.id", "consent_records.account_id"],
            ondelete="CASCADE",
        ),
        UniqueConstraint("id", "account_id"),
        CheckConstraint("revision >= 1", name="positive_revision"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    account_id: Mapped[UUID] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"), index=True
    )
    subject_id: Mapped[UUID]
    consent_id: Mapped[UUID]
    revision: Mapped[int] = mapped_column(default=1)
    collection_date: Mapped[date | None] = mapped_column(Date)
    confirmed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    saved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    superseded_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("saved_reports.id", ondelete="SET NULL")
    )
    context: Mapped[dict[str, object]] = mapped_column(JSONB)


class ReviewedObservation(ReportBase):
    __tablename__ = "reviewed_observations"
    __table_args__ = (
        CheckConstraint("value > 0", name="positive_value"),
        CheckConstraint("value_operator IN ('eq','lt','lte','gt','gte')", name="value_operator"),
        CheckConstraint("unit IN ('mg/dL','mmol/L','%')", name="unit"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    report_id: Mapped[UUID] = mapped_column(
        ForeignKey("saved_reports.id", ondelete="CASCADE"), index=True
    )
    test_name: Mapped[str] = mapped_column(String(64))
    value: Mapped[Decimal] = mapped_column(Numeric())
    value_text: Mapped[str] = mapped_column(String(64))
    value_operator: Mapped[str] = mapped_column(String(3), default="eq")
    unit: Mapped[str] = mapped_column(String(16))
    reference_interval: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    context: Mapped[dict[str, object]] = mapped_column(JSONB)
    included: Mapped[bool] = mapped_column(default=True)
    exclusion_reason: Mapped[str | None] = mapped_column(String(240))


class InterpretationSnapshot(ReportBase):
    __tablename__ = "interpretation_snapshots"
    __table_args__ = (
        CheckConstraint(
            "outcome IN ('classified','not_classified','out_of_scope')", name="outcome"
        ),
        CheckConstraint(
            "overall_status IS NULL OR overall_status IN "
            "('normal','prediabetes_range','diabetes_range')",
            name="overall_status",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    report_id: Mapped[UUID] = mapped_column(
        ForeignKey("saved_reports.id", ondelete="CASCADE"), index=True
    )
    threshold_version: Mapped[str] = mapped_column(String(40))
    content_version: Mapped[str | None] = mapped_column(String(40))
    outcome: Mapped[str] = mapped_column(String(16))
    overall_status: Mapped[str | None] = mapped_column(String(24))
    result: Mapped[dict[str, object]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class RetainedReportAsset(ReportBase):
    __tablename__ = "retained_report_assets"
    __table_args__ = (
        ForeignKeyConstraint(
            ["report_id", "account_id"],
            ["saved_reports.id", "saved_reports.account_id"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["retention_consent_id", "account_id"],
            ["consent_records.id", "consent_records.account_id"],
            ondelete="CASCADE",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    account_id: Mapped[UUID]
    report_id: Mapped[UUID] = mapped_column(index=True)
    retention_consent_id: Mapped[UUID]
    encrypted_object_key: Mapped[str] = mapped_column(String(255), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
