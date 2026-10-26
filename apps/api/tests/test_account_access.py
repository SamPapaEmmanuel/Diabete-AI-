from datetime import timedelta

from conftest import AccountTestMail, submit_form
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from report_api.account_security import token_hash
from report_api.identity_schema import Account, AccountActionToken, AuthSession, utc_now

CREDENTIALS = {"email": "reader@example.org", "password": "A quiet afternoon in Accra"}


def test_registration_verification_login_and_logout(
    client: TestClient, mail: AccountTestMail, database: Session
) -> None:
    response = submit_form(client, "/auth/register", CREDENTIALS)
    assert response.status_code == 202
    account = database.scalar(select(Account))
    assert account is not None and account.password_hash.startswith("$argon2id$")
    assert account.password_hash != CREDENTIALS["password"]
    action = database.scalar(select(AccountActionToken))
    assert action is not None and action.token_hash == token_hash(mail.messages[0]["token"])
    login = submit_form(client, "/auth/login", CREDENTIALS)
    assert login.status_code == 200 and not login.json()["can_save_reports"]
    assert "httponly" in login.headers["set-cookie"].lower()
    assert "samesite=lax" in login.headers["set-cookie"].lower()
    verified = submit_form(client, "/auth/verify-email", {"token": mail.messages[0]["token"]})
    assert verified.status_code == 200
    assert client.get("/api/v1/account").json()["can_save_reports"] is True
    assert (
        submit_form(client, "/auth/verify-email", {"token": mail.messages[0]["token"]}).status_code
        == 422
    )
    assert submit_form(client, "/auth/logout", {}).status_code == 204
    assert client.get("/api/v1/account").status_code == 401


def test_authentication_requires_origin_and_csrf(client: TestClient) -> None:
    assert client.post("/api/v1/auth/register", json=CREDENTIALS).status_code == 403
    token = client.get("/api/v1/auth/csrf").json()["token"]
    response = client.post(
        "/api/v1/auth/register",
        json=CREDENTIALS,
        headers={"Origin": "https://outside.example.org", "X-CSRF-Token": token},
    )
    assert response.status_code == 403
    assert response.json()["message_key"] == "auth.origin_invalid"


def test_login_rotates_session_and_binds_csrf(client: TestClient, mail: AccountTestMail) -> None:
    submit_form(client, "/auth/register", CREDENTIALS)
    first = submit_form(client, "/auth/login", CREDENTIALS)
    old_cookie = client.cookies.get("report_session")
    old_csrf = client.get("/api/v1/auth/csrf").json()["token"]
    second = submit_form(client, "/auth/login", CREDENTIALS)
    assert first.status_code == second.status_code == 200
    assert client.cookies.get("report_session") != old_cookie
    assert (
        client.post("/api/v1/auth/logout", json={}, headers={"X-CSRF-Token": old_csrf}).status_code
        == 403
    )


def test_reset_is_single_use_and_revokes_sessions(
    client: TestClient, mail: AccountTestMail
) -> None:
    submit_form(client, "/auth/register", CREDENTIALS)
    submit_form(client, "/auth/login", CREDENTIALS)
    assert (
        submit_form(
            client, "/auth/password-reset-requests", {"email": CREDENTIALS["email"]}
        ).status_code
        == 202
    )
    body = {"token": mail.messages[-1]["token"], "password": "Walking by the coast at dawn"}
    assert submit_form(client, "/auth/password-resets", body).status_code == 200
    assert client.get("/api/v1/account").status_code == 401
    assert submit_form(client, "/auth/password-resets", body).status_code == 422
    assert submit_form(client, "/auth/login", CREDENTIALS).status_code == 401
    assert (
        submit_form(
            client, "/auth/login", {"email": CREDENTIALS["email"], "password": body["password"]}
        ).status_code
        == 200
    )


def test_expired_verification_and_idle_session_are_rejected(
    client: TestClient, mail: AccountTestMail, database: Session
) -> None:
    submit_form(client, "/auth/register", CREDENTIALS)
    action = database.scalar(select(AccountActionToken))
    assert action is not None
    action.expires_at = utc_now() - timedelta(seconds=1)
    database.commit()
    assert (
        submit_form(client, "/auth/verify-email", {"token": mail.messages[0]["token"]}).status_code
        == 422
    )
    submit_form(client, "/auth/login", CREDENTIALS)
    session = database.scalar(select(AuthSession))
    assert session is not None
    session.last_seen_at = utc_now() - timedelta(minutes=31)
    database.commit()
    assert client.get("/api/v1/account").status_code == 401


def test_unknown_accounts_use_generic_responses(client: TestClient, mail: AccountTestMail) -> None:
    submit_form(client, "/auth/register", CREDENTIALS)
    duplicate = submit_form(client, "/auth/register", CREDENTIALS)
    assert duplicate.status_code == 202
    assert len(mail.messages) == 1
    known = submit_form(client, "/auth/password-reset-requests", {"email": CREDENTIALS["email"]})
    unknown = submit_form(
        client, "/auth/password-reset-requests", {"email": "another-reader@example.org"}
    )
    assert known.status_code == unknown.status_code == 202
    assert known.json() == unknown.json()


def test_invalid_inputs_do_not_echo_passwords(client: TestClient) -> None:
    password = "sensitive-short"
    response = submit_form(client, "/auth/register", {"email": "invalid", "password": password})
    assert response.status_code == 422
    assert password not in response.text
    assert '"input"' not in response.text
    common = submit_form(
        client, "/auth/register", {"email": "reader@example.org", "password": "123456789012345"}
    )
    assert common.status_code == 422 and common.json()["message_key"] == "auth.password_common"


def test_login_throttle_persists_failed_attempts(client: TestClient) -> None:
    for _ in range(5):
        assert submit_form(client, "/auth/login", CREDENTIALS).status_code == 401
    response = submit_form(client, "/auth/login", CREDENTIALS)
    assert response.status_code == 429 and "Retry-After" in response.headers


def test_foundation_exposes_no_report_processing(client: TestClient) -> None:
    response = client.get("/api/v1/public-config")
    assert response.json()["uploads_enabled"] is False
    assert response.json()["interpretation_enabled"] is False
    assert response.headers["cache-control"] == "no-store"
    assert client.post("/api/v1/reports").status_code == 404
    assert client.get("/api/v1/health/live").status_code == 200
    assert client.get("/api/v1/health/ready").status_code == 200
