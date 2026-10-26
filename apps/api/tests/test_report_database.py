from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from report_api.identity_schema import Account, ConsentRecord, ReportSubject, utc_now
from report_api.saved_report_schema import ReviewedObservation, SavedReport


def account_records(database: Session, email: str) -> tuple[Account, ReportSubject, ConsentRecord]:
    account = Account(email=email, password_hash="test-only-hash")
    database.add(account)
    database.flush()
    subject = ReportSubject(account_id=account.id)
    consent = ConsentRecord(
        account_id=account.id, version="test-consent", purpose="report_processing"
    )
    database.add_all([subject, consent])
    database.flush()
    return account, subject, consent


def test_migration_matches_model_and_has_only_account_health_storage(
    engine: Engine, migration_config: Config
) -> None:
    command.check(migration_config)
    tables = set(inspect(engine).get_table_names())
    assert {
        "accounts",
        "auth_sessions",
        "consent_records",
        "report_subjects",
        "saved_reports",
        "reviewed_observations",
        "interpretation_snapshots",
    } <= tables
    assert "guest_reports" not in tables and "extracted_observations" not in tables


def test_one_subject_per_account_is_enforced(database: Session) -> None:
    account, _, _ = account_records(database, "one-subject@example.org")
    with pytest.raises(IntegrityError), database.begin_nested():
        database.add(ReportSubject(account_id=account.id))
        database.flush()


@pytest.mark.parametrize("foreign_relation", ["subject", "consent"])
def test_cross_account_report_links_are_rejected(database: Session, foreign_relation: str) -> None:
    owner, subject, consent = account_records(database, "owner@example.org")
    _, other_subject, other_consent = account_records(database, "other-owner@example.org")
    with pytest.raises(IntegrityError), database.begin_nested():
        database.add(
            SavedReport(
                account_id=owner.id,
                subject_id=other_subject.id if foreign_relation == "subject" else subject.id,
                consent_id=other_consent.id if foreign_relation == "consent" else consent.id,
                confirmed_at=utc_now(),
                context={},
            )
        )
        database.flush()


def test_exact_decimal_values_and_account_cascade(database: Session) -> None:
    account, subject, consent = account_records(database, "precision@example.org")
    report = SavedReport(
        account_id=account.id,
        subject_id=subject.id,
        consent_id=consent.id,
        collection_date=date(2026, 10, 26),
        confirmed_at=utc_now(),
        context={},
    )
    database.add(report)
    database.flush()
    exact = Decimal("123.456789012345678901")
    observation = ReviewedObservation(
        report_id=report.id,
        test_name="source_value",
        value=exact,
        value_text=str(exact),
        unit="mg/dL",
        context={},
    )
    database.add(observation)
    database.flush()
    observation_id = observation.id
    database.expire_all()
    stored = database.get(ReviewedObservation, observation_id)
    assert stored is not None and stored.value == exact
    database.delete(account)
    database.flush()
    assert (
        database.scalar(
            select(ReviewedObservation.id).where(ReviewedObservation.id == observation_id)
        )
        is None
    )
    assert database.get(SavedReport, uuid4()) is None
