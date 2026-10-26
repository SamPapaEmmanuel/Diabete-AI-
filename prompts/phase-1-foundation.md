Phase 1 only.

Read AGENTS.md and docs/phase-log.md. Scaffold:

- apps/web and apps/api
- CI with formatters and linters
- the design token file (colour, spacing, radius, type, light and dark)
- the base layout with the left rail on desktop and the tab bar on mobile
- the PostgreSQL schema with migrations
- an authentication skeleton

Add a test that fails if any token or stylesheet contains a gradient.

Exit check: the app boots, and lint and tests pass in CI. Update docs/phase-log.md
and stop.
