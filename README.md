# Diabetes AI Report Interpreter

A web application for reviewing diabetes laboratory reports and understanding screening ranges, with reviewed Ghanaian food and lifestyle guidance planned for later phases. It screens and educates; a clinician confirms a diagnosis.

Phase 1 provides the React/TypeScript interface, light and dark themes, responsive navigation, FastAPI service, PostgreSQL migrations and local account registration, email verification, sign-in, recovery and sign-out. Report upload, OCR, interpretation, guidance, history retrieval and PDF export belong to later phases. Clinical interpretation is disabled.

## Requirements

- Node.js 24 and npm.
- Python 3.13 and uv.
- PostgreSQL, supplied either by the optional local binary package or Docker Compose.

Use synthetic account details and reports during development.

## Install

From the repository root:

```sh
npm ci
uv sync --locked --project apps/api
```

Copy `.env.example` to `.env`. This file is ignored by Git. The sample credentials are for loopback-only local development.

## Run

Start PostgreSQL in a terminal:

```sh
npm run db:local
```

This starts a persistent development cluster inside `.runtime/postgres-data`, listening on `127.0.0.1:55432`, and creates `report_dev` and `report_test`. Set the port in `REPORT_DATABASE_URL` in `.env` to `55432`. Stop the process with Ctrl+C; development records remain available on restart. The binary wrapper is a development dependency, not the hosted database.

Alternatively, run `docker compose up -d postgres redis` and keep port `5432` in `.env`. Redis persistence is disabled and is reserved for the next phase.

Apply the initial migration:

```sh
uv run --project apps/api alembic -c apps/api/alembic.ini upgrade head
```

Start the API in another terminal and the web app in a third:

```sh
npm run api:dev
npm run dev
```

Open `http://localhost:5173`. Vite proxies `/api` to the local API. Readiness is available at `http://127.0.0.1:8000/api/v1/health/ready`.

Account emails are written to private local JSON files in `.runtime/mail`; they are never sent externally. Open the link in the most recent message addressed to your synthetic account to verify it or reset its password. Do not publish this directory or log its tokens. The production environment intentionally refuses to start until a reviewed hosted mail transport and configuration are implemented. Local HTTP uses non-Secure cookies; hosted sessions require HTTPS and Secure cookies.

## Test

Start the local PostgreSQL process first. The test database must have a name ending in `_test`; tests refuse other database names. The default is the local `report_test` database on port `55432`. When using Docker, set `TEST_DATABASE_URL` to the same PostgreSQL connection on port `5432`, with database `report_test`, and create that database first.

```sh
npm run format:check
npm run lint
npm run typecheck
npm test
npm run build
uv run --project apps/api ruff format --check apps/api
uv run --project apps/api ruff check apps/api
uv run --project apps/api mypy --config-file apps/api/pyproject.toml apps/api/src apps/api/migrations apps/api/tests
uv run --project apps/api pytest apps/api/tests
uv run --project apps/api alembic -c apps/api/alembic.ini check
npx playwright install chromium
npm run test:e2e
```

Browser tests start the API and the built Vite preview automatically if they are not already running, and use the database configured in `.env` or the environment. Run `npm run build` first. They create synthetic accounts in that development/test database and local outbox. They check desktop/mobile navigation, keyboard access, both themes, automated accessibility, offline handling and the account flow. Test accounts are development data; use a dedicated database for automated runs. An existing Microsoft Edge installation can be used by setting `PLAYWRIGHT_CHANNEL=msedge`; CI uses downloaded Chromium.

The no-gradient and theme-contrast checks run with `npm test`. API tests cover authentication, token reuse/expiry, CSRF/origin checks, throttling, data redaction, schema ownership, exact decimals and account cascades. The migration is also exercised on a clean database and rolled back/upgraded in CI. GitHub Actions runs these checks on pushes and pull requests; a remote repository is needed to obtain an actual GitHub run.

## Project layout

```text
apps/web                  React interface, tokens and Vitest tests
apps/api                  FastAPI service, schemas, Alembic and pytest
config/thresholds.json     Versioned clinical draft; clinical use disabled
content/locales/en-GH.json Shared interface, server-message and email copy
content/guidance           Reviewed guidance in a later phase
content/foods              Ghanaian food library in a later phase
tests/browser             Playwright foundation checks
tests/fixtures/reports     Authorized report fixtures in a later phase
docs                      Specification, decisions and phase log
```

The specification and [Phase 0 decisions](docs/phase-0-decisions.md) define the implementation baseline. Read [the phase log](docs/phase-log.md) before starting a phase. Work on one phase at a time; this scaffold stops before OCR ingestion.
