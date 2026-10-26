# Diabetes AI Report Interpreter

Web application that reads a diabetes lab report (JPEG, PNG, HEIC or PDF) with OCR,
extracts glucose-related values, classifies them against clinical thresholds, and
returns a plain-language explanation with diet and non-pharmacological guidance.

The app screens and educates. It does not diagnose, and it never mentions
medication, drug names or doses.

## Users

Patients and caregivers in Ghana first. Mobile first. English at launch, with all
copy kept in a translation file so Twi can be added later.

## Core flow

1. Upload a report (camera capture on mobile).
2. Preprocess the image and run OCR.
3. Parse test name, value, unit and reference range for: fasting blood sugar,
   random blood sugar, 2-hour post-prandial, OGTT, HbA1c. Units: mg/dL, mmol/L.
4. Review screen: source image on the left, extracted fields on the right, each
   field with a confidence score. Low-confidence fields are highlighted. The user
   must confirm all values before anything is interpreted.
5. Interpretation: the rule engine reads `config/thresholds.json` and returns a
   status per test and overall (normal, prediabetes range, diabetes range), plus an
   urgent notice for very high or very low values.
6. Guidance: rule-based selection from a reviewed content library in `content/`.
   Output covers foods to favour and limit, portions, a sample weekly meal plan
   built from a Ghanaian food library (banku, kenkey, fufu, waakye, jollof, gari,
   yam, plantain, beans, kontomire, garden eggs), plus physical activity, weight,
   sleep, stress, hydration, alcohol and tobacco, home monitoring habits and
   follow-up timing.
7. Save to history, show trends per test, export a PDF summary and a one-page
   clinician sheet.

## Accounts and data

- Guest mode interprets one report and stores nothing.
- Accounts (email and password, email verification) add history and trends.
- Delete original images after confirmation unless the user opts to keep them.
- Encrypt in transit and at rest, keep health data out of logs, include a consent
  screen and full account deletion.
- Follow Ghana's Data Protection Act, 2012 (Act 843).

## Stack

- Front end: React, TypeScript in strict mode, Vite.
- Back end: Python, FastAPI, typed and validated schemas.
- OCR: Tesseract with OpenCV preprocessing (deskew, denoise, contrast). Keep the
  engine behind an interface so PaddleOCR can replace it.
- Data: PostgreSQL. Jobs: Redis-backed queue for OCR.
- Tests: pytest, Vitest, Playwright.

## Clinical rules

- Status comes only from the rule engine and `config/thresholds.json`. Do not
  hard-code thresholds anywhere else. Every threshold carries a source note and the
  file has a version field.
- Never write "you have diabetes". Write that the value falls in the range
  consistent with diabetes and that a confirmatory test and a clinician review are
  needed.
- Pregnancy, children and people already treated for diabetes are out of scope for
  classification. Show a message to speak to a clinician.
- Guidance text is never generated freely. Select it from `content/` by rule.
- Reference thresholds (ADA criteria; verify against the current Standards of Care
  before relying on them):
  - Fasting plasma glucose: below 100 mg/dL (5.6 mmol/L) normal; 100 to 125 mg/dL
    (5.6 to 6.9 mmol/L) prediabetes range; 126 mg/dL (7.0 mmol/L) or above diabetes
    range.
  - 2-hour OGTT: below 140 mg/dL (7.8 mmol/L) normal; 140 to 199 mg/dL (7.8 to 11.0
    mmol/L) prediabetes range; 200 mg/dL (11.1 mmol/L) or above diabetes range.
  - HbA1c: below 5.7% normal; 5.7% to 6.4% prediabetes range; 6.5% or above diabetes
    range.
  - Random glucose: 200 mg/dL (11.1 mmol/L) or above with classic symptoms is in the
    diabetes range. It is not used to classify normal or prediabetes.
  - Urgent-notice triggers are set with the clinical reviewer. Starting points: below
    70 mg/dL (3.9 mmol/L) and above 300 mg/dL (16.7 mmol/L).

## Design rules

- No gradients anywhere: backgrounds, buttons, cards, charts, borders, shadows,
  overlays. Solid colours only.
- No emoji or emoji-style glyphs in the interface, copy, code, comments, commit
  messages or docs.
- Avoid the generated-site look: purple and blue palettes, glass blur, a centred
  hero with three feature cards, sparkle or robot icons, "Powered by AI" badges,
  oversized uniform rounded corners.
- Tone: clinical and calm. Off-white surfaces, one deep blue-green accent, red and
  amber used only for result status. Light and dark themes from tokens.
- Tokens for colour, spacing, radius and type. Radius at most 6 px. 4 px spacing
  grid. Elevation by border, not soft shadow.
- One humanist sans for the interface and one monospaced face for lab values. Two
  weights, no more than five sizes.
- Results use flat range bars with the value printed beside them. No gauges.
- One line-icon family at a fixed stroke width. No stock illustrations.
- Real content only. No lorem ipsum or placeholder names.
- Left rail on desktop, bottom tab bar on mobile.
- Every screen has loading, empty, error and offline states.
- WCAG 2.2 AA. Status is never conveyed by colour alone.

## Code rules

- Name files and functions after the domain: `glucose_panel`, `unit_converter`,
  `range_band`. Never `utils`, `helper`, `test2`, `final_v2`, `newfile`.
- Comments explain why, not what. No banner comments, no "generated by" notes, no
  leftover TODO markers in committed code.
- The README states what the project is, how to run it and how to test it. No
  badges, no marketing language.
- One formatter and linter per language, enforced in CI.
- Plain commit messages in the imperative, one change per commit.

## Repository layout

```
apps/web
apps/api
config/thresholds.json
content/guidance
content/foods
docs
tests/fixtures/reports
```

## Working agreements

- Work on one phase at a time. Do not start the next phase.
- Before coding a phase, restate the plan in a short list and note anything
  ambiguous. If a decision is needed from me, stop and ask.
- Write tests with the code. A phase is done only when its exit check passes.
- At the end of each phase, update `docs/phase-log.md` with what changed and what is
  left, in plain sentences.
- Read `docs/phase-log.md` at the start of each session to see where the previous
  phase stopped.
