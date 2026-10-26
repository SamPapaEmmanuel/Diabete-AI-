from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException
from starlette.responses import Response

from report_api.account_contract import ServiceView
from report_api.account_mail import AccountMail, LocalAccountMail
from report_api.account_routes import AccountFailure, router
from report_api.database import create_report_engine
from report_api.settings import ReportSettings


def create_app(settings: ReportSettings | None = None, mail: AccountMail | None = None) -> FastAPI:
    resolved = settings or ReportSettings()
    engine = create_report_engine(resolved.database_url)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield
        engine.dispose()

    application = FastAPI(title="Report API", version="0.1.0", lifespan=lifespan)
    application.state.settings = resolved
    application.state.database = engine
    application.state.mail = mail or LocalAccountMail(
        resolved.mail_directory, resolved.frontend_origin
    )
    application.include_router(router)

    @application.middleware("http")
    async def protect_responses(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
        return response

    @application.exception_handler(AccountFailure)
    async def account_failure(_: Request, error: AccountFailure) -> JSONResponse:
        headers = {"Retry-After": "900"} if error.status == 429 else {}
        return JSONResponse(
            {"message_key": error.message_key}, status_code=error.status, headers=headers
        )

    @application.exception_handler(RequestValidationError)
    async def validation_failure(_: Request, error: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            {
                "message_key": "request.invalid",
                "fields": [list(item["loc"]) for item in error.errors()],
            },
            status_code=422,
        )

    @application.exception_handler(SQLAlchemyError)
    async def database_failure(_: Request, __: SQLAlchemyError) -> JSONResponse:
        return JSONResponse({"message_key": "service.unavailable"}, status_code=503)

    @application.exception_handler(OSError)
    async def mail_failure(_: Request, __: OSError) -> JSONResponse:
        return JSONResponse({"message_key": "service.unavailable"}, status_code=503)

    @application.exception_handler(HTTPException)
    async def missing_resource(_: Request, error: HTTPException) -> JSONResponse:
        return JSONResponse({"message_key": "request.not_found"}, status_code=error.status_code)

    @application.get("/api/v1/health/live")
    def live() -> ServiceView:
        return ServiceView(status="ready")

    @application.get("/api/v1/health/ready")
    def ready() -> ServiceView:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1 FROM alembic_version LIMIT 1"))
        return ServiceView(status="ready")

    @application.get("/api/v1/public-config")
    def public_config() -> ServiceView:
        return ServiceView(status="ready")

    return application


app = create_app()
