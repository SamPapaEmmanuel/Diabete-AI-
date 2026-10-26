import hashlib
import hmac
from datetime import timedelta
from typing import Annotated, cast

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy import case, delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from report_api.account_contract import (
    AccountCredentials,
    AccountView,
    ActionTokenRequest,
    EmailRequest,
    MessageView,
    PasswordResetRequest,
)
from report_api.account_mail import AccountMail, MailPurpose
from report_api.account_security import (
    DUMMY_PASSWORD_HASH,
    PASSWORD_HASHER,
    csrf_token,
    opaque_token,
    password_is_common,
    password_matches,
    token_hash,
    valid_csrf,
)
from report_api.database import report_session
from report_api.identity_schema import (
    Account,
    AccountActionToken,
    AuthRateLimit,
    AuthSession,
    ReportSubject,
    utc_now,
)
from report_api.settings import ReportSettings

router = APIRouter(prefix="/api/v1", tags=["account"])
DatabaseSession = Annotated[Session, Depends(report_session)]


class AccountFailure(Exception):
    def __init__(self, status: int, message_key: str) -> None:
        self.status = status
        self.message_key = message_key


def request_settings(request: Request) -> ReportSettings:
    return cast(ReportSettings, request.app.state.settings)


def csrf_guard(request: Request) -> None:
    settings = request_settings(request)
    if request.headers.get("origin") != settings.frontend_origin:
        raise AccountFailure(403, "auth.origin_invalid")
    header = request.headers.get("x-csrf-token", "")
    cookie = request.cookies.get(settings.csrf_cookie, "")
    session_token = request.cookies.get(settings.session_cookie, "")
    if not hmac.compare_digest(header, cookie) or not valid_csrf(
        settings.csrf_secret, session_token, header
    ):
        raise AccountFailure(403, "auth.csrf_invalid")


def limit_attempts(
    request: Request, database: Session, category: str, identity: str, maximum: int, minutes: int
) -> None:
    settings = request_settings(request)
    key = hmac.new(
        settings.csrf_secret.encode(), f"{category}:{identity}".encode(), hashlib.sha256
    ).hexdigest()
    now = utc_now()
    statement = insert(AuthRateLimit).values(
        key_hash=key, attempts=1, expires_at=now + timedelta(minutes=minutes)
    )
    attempt_statement = statement.on_conflict_do_update(
        index_elements=[AuthRateLimit.key_hash],
        set_={
            "attempts": case(
                (AuthRateLimit.expires_at <= now, 1), else_=AuthRateLimit.attempts + 1
            ),
            "expires_at": case(
                (AuthRateLimit.expires_at <= now, now + timedelta(minutes=minutes)),
                else_=AuthRateLimit.expires_at,
            ),
        },
    ).returning(AuthRateLimit.attempts)
    attempts = database.execute(attempt_statement).scalar_one()
    database.commit()
    if attempts > maximum:
        raise AccountFailure(429, "auth.rate_limited")


def clear_login_failures(request: Request, database: Session, email: str) -> None:
    key = hmac.new(
        request_settings(request).csrf_secret.encode(), f"login:{email}".encode(), hashlib.sha256
    ).hexdigest()
    database.execute(delete(AuthRateLimit).where(AuthRateLimit.key_hash == key))


def issue_action(
    request: Request, database: Session, account: Account, purpose: MailPurpose
) -> None:
    token = opaque_token()
    lifetime = timedelta(hours=24) if purpose == "verify_email" else timedelta(minutes=15)
    database.add(
        AccountActionToken(
            account_id=account.id,
            token_hash=token_hash(token),
            purpose=purpose,
            expires_at=utc_now() + lifetime,
        )
    )
    mail = cast(AccountMail, request.app.state.mail)
    mail.send(account.email, purpose, token)


def account_view(account: Account) -> AccountView:
    return AccountView(
        id=account.id,
        email=account.email,
        verified=account.verified_at is not None,
        can_save_reports=account.verified_at is not None,
        locale=account.locale,
        theme=account.theme,
    )


def authenticated_account(request: Request, database: DatabaseSession) -> Account:
    settings = request_settings(request)
    secret = request.cookies.get(settings.session_cookie, "")
    session = database.scalar(
        select(AuthSession).where(AuthSession.token_hash == token_hash(secret))
    )
    now = utc_now()
    if (
        session is None
        or session.expires_at <= now
        or session.last_seen_at <= now - timedelta(minutes=30)
    ):
        raise AccountFailure(401, "auth.sign_in_required")
    account = database.get(Account, session.account_id)
    if account is None:
        raise AccountFailure(401, "auth.sign_in_required")
    session.last_seen_at = now
    database.commit()
    return account


def verified_account(account: Annotated[Account, Depends(authenticated_account)]) -> Account:
    if account.verified_at is None:
        raise AccountFailure(403, "auth.verification_required")
    return account


@router.get("/auth/csrf")
def begin_form(request: Request, response: Response) -> dict[str, str]:
    settings = request_settings(request)
    token = csrf_token(settings.csrf_secret, request.cookies.get(settings.session_cookie, ""))
    response.set_cookie(
        settings.csrf_cookie,
        token,
        secure=settings.cookie_secure,
        httponly=True,
        samesite="lax",
        path="/",
        max_age=7200,
    )
    return {"token": token}


@router.post("/auth/register", status_code=202, dependencies=[Depends(csrf_guard)])
def register_account(
    body: AccountCredentials, request: Request, database: DatabaseSession
) -> MessageView:
    email = str(body.email).casefold()
    address = request.client.host if request.client else "unknown"
    limit_attempts(request, database, "register_ip", address, 100, 60)
    limit_attempts(request, database, "register", email, 3, 60)
    password = body.password.get_secret_value()
    if password_is_common(password):
        raise AccountFailure(422, "auth.password_common")
    encoded = PASSWORD_HASHER.hash(password)
    account = database.scalar(select(Account).where(Account.email == email))
    if account is None:
        account = Account(email=email, password_hash=encoded)
        database.add(account)
        database.flush()
        database.add(ReportSubject(account_id=account.id))
        issue_action(request, database, account, "verify_email")
        database.commit()
    return MessageView(message_key="auth.check_email")


@router.post("/auth/verify-email", dependencies=[Depends(csrf_guard)])
def verify_email(body: ActionTokenRequest, database: DatabaseSession) -> MessageView:
    action = database.scalar(
        select(AccountActionToken)
        .where(
            AccountActionToken.token_hash == token_hash(body.token.get_secret_value()),
            AccountActionToken.purpose == "verify_email",
        )
        .with_for_update()
    )
    if action is None or action.consumed_at is not None or action.expires_at <= utc_now():
        raise AccountFailure(422, "auth.invalid_token")
    account = database.get(Account, action.account_id)
    if account is None:
        raise AccountFailure(422, "auth.invalid_token")
    account.verified_at = utc_now()
    action.consumed_at = utc_now()
    database.commit()
    return MessageView(message_key="auth.email_verified")


@router.post("/auth/login", dependencies=[Depends(csrf_guard)])
def login_account(
    body: AccountCredentials, request: Request, response: Response, database: DatabaseSession
) -> AccountView:
    settings = request_settings(request)
    email = str(body.email).casefold()
    address = request.client.host if request.client else "unknown"
    limit_attempts(request, database, "login_ip", address, 100, 15)
    limit_attempts(request, database, "login", email, 5, 15)
    account = database.scalar(select(Account).where(Account.email == email))
    encoded = account.password_hash if account else DUMMY_PASSWORD_HASH
    matches = password_matches(encoded, body.password.get_secret_value())
    if not matches or account is None:
        raise AccountFailure(401, "auth.invalid_credentials")
    clear_login_failures(request, database, email)
    old_token = request.cookies.get(settings.session_cookie, "")
    database.execute(delete(AuthSession).where(AuthSession.token_hash == token_hash(old_token)))
    token = opaque_token()
    database.add(
        AuthSession(
            account_id=account.id,
            token_hash=token_hash(token),
            expires_at=utc_now() + timedelta(hours=12),
        )
    )
    database.commit()
    response.set_cookie(
        settings.session_cookie,
        token,
        secure=settings.cookie_secure,
        httponly=True,
        samesite="lax",
        path="/",
        max_age=43200,
    )
    return account_view(account)


@router.get("/account")
def current_account(account: Annotated[Account, Depends(authenticated_account)]) -> AccountView:
    return account_view(account)


@router.post("/auth/logout", status_code=204, dependencies=[Depends(csrf_guard)])
def logout_account(request: Request, response: Response, database: DatabaseSession) -> None:
    settings = request_settings(request)
    token = request.cookies.get(settings.session_cookie, "")
    database.execute(delete(AuthSession).where(AuthSession.token_hash == token_hash(token)))
    database.commit()
    response.delete_cookie(
        settings.session_cookie,
        path="/",
        secure=settings.cookie_secure,
        httponly=True,
        samesite="lax",
    )


@router.post("/auth/resend-verification", status_code=202, dependencies=[Depends(csrf_guard)])
def resend_verification(
    body: EmailRequest, request: Request, database: DatabaseSession
) -> MessageView:
    return send_account_action(body, request, database, "verify_email")


@router.post("/auth/password-reset-requests", status_code=202, dependencies=[Depends(csrf_guard)])
def request_password_reset(
    body: EmailRequest, request: Request, database: DatabaseSession
) -> MessageView:
    return send_account_action(body, request, database, "reset_password")


def send_account_action(
    body: EmailRequest, request: Request, database: Session, purpose: MailPurpose
) -> MessageView:
    email = str(body.email).casefold()
    limit_attempts(request, database, purpose, email, 3, 60)
    address = request.client.host if request.client else "unknown"
    limit_attempts(request, database, f"{purpose}_ip", address, 100, 60)
    account = database.scalar(select(Account).where(Account.email == email))
    if account is not None and (purpose == "reset_password" or account.verified_at is None):
        issue_action(request, database, account, purpose)
        database.commit()
    return MessageView(
        message_key="auth.check_email" if purpose == "verify_email" else "auth.reset_sent"
    )


@router.post("/auth/password-resets", dependencies=[Depends(csrf_guard)])
def reset_password(
    body: PasswordResetRequest, request: Request, response: Response, database: DatabaseSession
) -> MessageView:
    action = database.scalar(
        select(AccountActionToken)
        .where(
            AccountActionToken.token_hash == token_hash(body.token.get_secret_value()),
            AccountActionToken.purpose == "reset_password",
        )
        .with_for_update()
    )
    if action is None or action.consumed_at is not None or action.expires_at <= utc_now():
        raise AccountFailure(422, "auth.invalid_token")
    account = database.get(Account, action.account_id)
    if account is None:
        raise AccountFailure(422, "auth.invalid_token")
    password = body.password.get_secret_value()
    if password_is_common(password):
        raise AccountFailure(422, "auth.password_common")
    account.password_hash = PASSWORD_HASHER.hash(password)
    database.execute(delete(AuthSession).where(AuthSession.account_id == account.id))
    database.execute(
        delete(AccountActionToken).where(
            AccountActionToken.account_id == account.id,
            AccountActionToken.purpose == "reset_password",
        )
    )
    database.commit()
    settings = request_settings(request)
    response.delete_cookie(
        settings.session_cookie,
        path="/",
        secure=settings.cookie_secure,
        httponly=True,
        samesite="lax",
    )
    return MessageView(message_key="auth.password_updated")
