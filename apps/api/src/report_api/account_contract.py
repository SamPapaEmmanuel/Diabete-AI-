from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, SecretStr, field_validator


class AccountCredentials(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    password: SecretStr

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, value: SecretStr) -> SecretStr:
        if not 15 <= len(value.get_secret_value()) <= 128:
            raise ValueError("auth.password_length")
        return value


class ActionTokenRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    token: SecretStr


class PasswordResetRequest(ActionTokenRequest):
    password: SecretStr

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, value: SecretStr) -> SecretStr:
        return AccountCredentials.validate_password_length(value)


class EmailRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr


class AccountView(BaseModel):
    id: UUID
    email: str
    verified: bool
    can_save_reports: bool
    locale: str
    theme: str


class MessageView(BaseModel):
    message_key: str


class ServiceView(BaseModel):
    status: Literal["ready", "unavailable"]
    phase: Literal["foundation"] = "foundation"
    uploads_enabled: Literal[False] = False
    interpretation_enabled: Literal[False] = False
