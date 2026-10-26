Phase 3 only.

Read AGENTS.md and docs/phase-log.md. Build:

- the parser that turns OCR output into structured fields: test name (with aliases
  such as FBS, FPG, RBS, PPBS, HbA1c, A1c), value, unit, reference range and
  confidence
- unit normalisation between mg/dL and mmol/L, and HbA1c as a percentage
- the two-pane review screen with the source image and editable fields,
  low-confidence highlighting, and a confirm action that is required before
  interpretation can run
- an accuracy script that scores the parser against hand-labelled fixtures

Exit check: 95 percent of fields correct on the labelled fixtures. Update
docs/phase-log.md and stop.
