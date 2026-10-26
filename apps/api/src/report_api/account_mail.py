import json
from pathlib import Path
from typing import Literal, Protocol
from uuid import uuid4

from report_api.settings import PROJECT_ROOT

MailPurpose = Literal["verify_email", "reset_password"]


class AccountMail(Protocol):
    def send(self, email: str, purpose: MailPurpose, token: str) -> None: ...


class LocalAccountMail:
    def __init__(self, directory: Path, frontend_origin: str) -> None:
        self.directory = directory
        self.frontend_origin = frontend_origin
        self.messages: dict[str, str] = json.loads(
            (PROJECT_ROOT / "content/locales/en-GH.json").read_text(encoding="utf-8")
        )

    def send(self, email: str, purpose: MailPurpose, token: str) -> None:
        self.directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        action = "verify" if purpose == "verify_email" else "reset"
        prefix = "mail.verify" if purpose == "verify_email" else "mail.reset"
        path = self.directory / f"{uuid4()}.json"
        with path.open("x", encoding="utf-8") as message_file:
            path.chmod(0o600)
            json.dump(
                {
                    "to": email,
                    "subject": self.messages[f"{prefix}_subject"],
                    "body": self.messages[f"{prefix}_body"],
                    "link": f"{self.frontend_origin}/#/account/{action}?token={token}",
                },
                message_file,
            )
