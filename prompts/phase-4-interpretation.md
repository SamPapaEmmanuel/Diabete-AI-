Phase 4 only.

Read AGENTS.md and docs/phase-log.md. Build:

- the rule engine that reads config/thresholds.json and returns per-test status,
  overall status and urgent-notice state
- explanation text generated from templates in content/, following the wording rules
  in AGENTS.md
- handling for out-of-scope cases: pregnancy, children, known diabetes on treatment
- boundary tests for every threshold at the value, one below and one above, in both
  mg/dL and mmol/L

Exit check: all boundary tests pass. Update docs/phase-log.md and stop.
