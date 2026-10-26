import hashlib
import hmac
import secrets
import time

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

PASSWORD_HASHER = PasswordHasher(memory_cost=19456, time_cost=2, parallelism=1)
DUMMY_PASSWORD_HASH = PASSWORD_HASHER.hash(secrets.token_urlsafe(32))
COMMON_PASSWORDS = {
    "passwordpassword",
    "password123456789",
    "123456789012345",
    "qwertyuiopasdfgh",
    "letmeinletmeinletmein",
    "iloveyouiloveyou",
    "thisisapassword",
    "correcthorsebatterystaple",
}


def opaque_token() -> str:
    return secrets.token_urlsafe(32)


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def password_is_common(password: str) -> bool:
    folded = password.casefold()
    return folded in COMMON_PASSWORDS or len(set(folded)) <= 2


def password_matches(encoded: str, password: str) -> bool:
    try:
        return PASSWORD_HASHER.verify(encoded, password)
    except (VerificationError, InvalidHashError):
        return False


def csrf_token(secret: str, session_token: str) -> str:
    nonce = f"{int(time.time())}.{opaque_token()}"
    signature = hmac.new(secret.encode(), f"{session_token}.{nonce}".encode(), "sha256").hexdigest()
    return f"{nonce}.{signature}"


def valid_csrf(secret: str, session_token: str, token: str) -> bool:
    try:
        issued, nonce, signature = token.split(".")
        age = int(time.time()) - int(issued)
    except (ValueError, TypeError):
        return False
    expected = hmac.new(
        secret.encode(), f"{session_token}.{issued}.{nonce}".encode(), "sha256"
    ).hexdigest()
    return 0 <= age <= 7200 and hmac.compare_digest(expected, signature)
