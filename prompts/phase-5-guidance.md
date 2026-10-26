Phase 5 only.

Read AGENTS.md and docs/phase-log.md. Build:

- the profile form: age, sex, weight, height, activity level, dietary restrictions
- the rule-based guidance selector
- the content library in content/guidance and the Ghanaian food library in
  content/foods, with carbohydrate-load notes
- a sample weekly meal plan and the non-pharmacological advice sections
- a review status field on every content file
- a test that scans all guidance output for medication terms and fails if any appear

Exit check: output contains no medication terms and every content file is marked for
clinician review. Update docs/phase-log.md and stop.
