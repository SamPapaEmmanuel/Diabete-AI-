import os
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from report_api.account_mail import MailPurpose
from report_api.app import create_app
from report_api.database import report_session
from report_api.settings import ReportSettings


class AccountTestMail:
    def __init__(self) -> None:
        self.messages: list[dict[str, str]] = []

    def send(self, email: str, purpose: MailPurpose, token: str) -> None:
        self.messages.append({"email": email, "purpose": purpose, "token": token})


@pytest.fixture(scope="session")
def database_url() -> str:
    url = os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql+psycopg://report:local-report-password@127.0.0.1:55432/report_test",
    )
    if not (make_url(url).database or "").endswith("_test"):
        raise RuntimeError("Tests require an isolated database with a name ending in _test")
    return url


@pytest.fixture(scope="session")
def migration_config(database_url: str) -> Config:
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    config.attributes["database_url"] = database_url
    return config


@pytest.fixture(scope="session")
def engine(database_url: str, migration_config: Config) -> Iterator[Engine]:
    command.upgrade(migration_config, "head")
    database = create_engine(database_url, hide_parameters=True)
    yield database
    database.dispose()


@pytest.fixture
def database(engine: Engine) -> Iterator[Session]:
    with engine.connect() as connection:
        transaction = connection.begin()
        with Session(bind=connection, join_transaction_mode="create_savepoint") as session:
            yield session
        transaction.rollback()


@pytest.fixture
def mail() -> AccountTestMail:
    return AccountTestMail()


@pytest.fixture
def client(database_url: str, database: Session, mail: AccountTestMail) -> Iterator[TestClient]:
    settings = ReportSettings(
        environment="test", database_url=database_url, frontend_origin="http://testserver"
    )
    application = create_app(settings, mail)
    application.dependency_overrides[report_session] = lambda: database
    with TestClient(application) as browser:
        browser.headers["Origin"] = settings.frontend_origin
        yield browser


def submit_form(client: TestClient, path: str, payload: dict[str, Any]) -> Any:
    token = client.get("/api/v1/auth/csrf").json()["token"]
    return client.post(f"/api/v1{path}", json=payload, headers={"X-CSRF-Token": token})
