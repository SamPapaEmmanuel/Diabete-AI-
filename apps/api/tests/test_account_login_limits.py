from conftest import submit_form
from fastapi.testclient import TestClient


def test_successful_sign_ins_do_not_accumulate_failed_attempts(client: TestClient) -> None:
    credentials = {
        "email": "repeat-reader@example.org",
        "password": "An evening walk around the garden",
    }
    assert submit_form(client, "/auth/register", credentials).status_code == 202
    for _ in range(6):
        assert submit_form(client, "/auth/login", credentials).status_code == 200
