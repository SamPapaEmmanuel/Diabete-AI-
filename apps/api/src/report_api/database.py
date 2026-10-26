from collections.abc import Iterator

from fastapi import Request
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session


def create_report_engine(database_url: str) -> Engine:
    return create_engine(database_url, pool_pre_ping=True, hide_parameters=True)


def report_session(request: Request) -> Iterator[Session]:
    with Session(request.app.state.database) as session:
        yield session
