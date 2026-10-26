# Diabetes AI Report Interpreter: Phase 0 specification

Date: 2026-10-26. Status: Phase 0 baseline with selected first-release defaults in [the decision record](phase-0-decisions.md). Clinical approval and external launch requirements remain outstanding.

## Scope and boundaries

The application helps patients and caregivers in Ghana read a diabetes laboratory report, check extracted values, understand screening ranges and access reviewed food and lifestyle guidance. It screens and educates; it does not diagnose. It must never present drug names, doses or treatment instructions. English is the launch language, with all interface, validation, result and export copy referenced through translation keys so Twi can be added later.

Phase 0 produces this specification, `docs/phase-0-decisions.md`, `config/thresholds.json` and `docs/phase-log.md` only. No application, infrastructure, content library or test implementation is part of this phase. The decision record answers Q01-Q22 at the project owner's request and supplies the detailed first-release policies for each reference below. Product and engineering defaults are selected; clinical recommendations still require named professional approval. The original questions and remaining launch questions are retained at the end.

The future stack is React, strict TypeScript and Vite; Python with FastAPI and validated schemas; PostgreSQL; a Redis-backed OCR queue; and Tesseract behind a replaceable OCR interface. OpenCV supplies deskewing, denoising and contrast adjustment. PaddleOCR must be replaceable without changing the review or interpretation contracts. Verification uses pytest, Vitest and Playwright.

Input formats are JPEG, PNG, HEIC and PDF, including camera capture on mobile. Extraction covers fasting blood sugar, random blood sugar, two-hour post-prandial glucose, OGTT and HbA1c. Glucose accepts mg/dL and mmol/L; HbA1c requires percent. Unsupported units must be identified, not guessed or treated as equivalent (Q02, Q06).

Classification is limited to consenting adults aged 18 or older who are not pregnant and have not already been diagnosed with diabetes or begun diabetes care. Ask about scope before upload and direct excluded users to a clinician without assigning a screening status. Unknown eligibility cannot silently pass. If adult eligibility is not established, stop before upload. Consenting adults excluded by clinical eligibility may review, export and explicitly save a transcription without classification or tailored guidance; questionnaire wording still needs clinical review (Q04).

Guest mode handles one logical report per session in memory, without persistent storage or history (Q08). Verified accounts add explicitly saved history and trends. Originals are deleted after confirmation unless an account holder explicitly opts to keep them for up to 12 months; derived images and raw OCR are removed after review even when originals are retained. The detailed expiry, deletion and backup schedule is selected in Q09 and requires privacy review before real data.

## User stories and acceptance conditions

| ID   | Story                                                                                  | Acceptance condition                                                                                                                                                                                      |
| ---- | -------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| US01 | As a patient, I want to understand consent and scope before sending a report.          | No upload or OCR starts before consent; refusal exits without creating report data; excluded or uncertain eligibility cannot be classified.                                                               |
| US02 | As a guest, I want to understand one report without creating an account.               | The full upload, review, result and download flow is available in the active session; no persistent history is created; ending or expiring the session removes its data.                                  |
| US03 | As a mobile user, I want to photograph a report or choose a supported file.            | Camera permission failure has a file-picker fallback; page orientation and legibility can be inspected before submission.                                                                                 |
| US04 | As a user, I want to see processing progress and recover from failures.                | Queue and OCR states are distinguished; retry and cancellation are safe; no result is invented when extraction fails.                                                                                     |
| US05 | As a patient or caregiver, I want to correct every extracted field against the source. | Test, value, unit and reference range have field-level confidence and source locations; uncertain fields are labelled; every included observation is explicitly confirmed.                                |
| US06 | As a user, I want interpretation only after review.                                    | The server rejects interpretation until all included observations and required context are confirmed at the current revision; editing invalidates confirmation and dependent output.                      |
| US07 | As a patient, I want an understandable result without a diagnosis.                     | Each applicable test has a text status and flat range bar; an overall result states its coverage; exclusions and unclassified tests have reasons; urgent notices are distinct from diagnostic categories. |
| US08 | As a patient, I want guidance using foods available in Ghana.                          | Only approved content is selected by rule; food portions, a weekly plan and all required lifestyle topics are covered without freely generated advice.                                                    |
| US09 | As an account holder, I want to save reports and compare the same test over time.      | Saving is deliberate; only confirmed observations enter trends; test, unit, report date and rules version remain traceable.                                                                               |
| US10 | As a user, I want a summary to take to a clinician.                                    | A readable PDF summary and a one-page clinician sheet use the same confirmed snapshot and identify unclassified tests and limitations.                                                                    |
| US11 | As an account holder, I want control over my images and account data.                  | Image retention is opt-in; individual reports and the full account can be deleted; revoked sessions and deleted reports cannot be recreated by queued jobs.                                               |
| US12 | As a user with accessibility or connectivity needs, I want a usable interface.         | Keyboard and screen-reader access, status text, responsive layouts and explicit loading, empty, error and offline states are present on every screen.                                                     |

## Screen list and plain-text sketches

Sketches describe content and hierarchy, not final copy or visual styling. Actual values come from the user's report; no sample patient identity is introduced. Every label and message will use the translation system. Clinical text needs content approval (Q01, Q16, Q21).

The shared desktop shell has a left rail: Report, History, Account. Mobile uses a bottom tab bar with the same destinations. Guest History explains that an account is needed instead of suggesting a saved record exists. A persistent guest/account indicator, page title and connection state sit above the content.

### S01: Start

```text
Diabetes report interpreter
Read your lab values and prepare for a clinician conversation.
This service screens and educates. It does not diagnose.
[Continue as guest]  [Sign in]  [Create account]
Guest reports are not saved to history.
[Privacy and consent]
```

### S02: Eligibility and consent

```text
Before you upload
Who is the report for?                 [Myself / Someone I support]
Age eligibility                       [Answer / Not sure]
Pregnancy                             [Yes / No / Not sure]
Already receiving treatment for diabetes [Yes / No / Not sure]
How the report is processed and deleted
[ ] I agree to the stated processing of this report
[Continue]  [Cancel]
Outside scope: Speak to a clinician about interpreting this report.
```

Caregivers may assist a consenting adult in that adult's own account; independent proxy access is deferred (Q15, Q18). Scope answers are required; consent is never preselected. Clinically excluded adults can choose transcription-only use after the clinician-referral message; children and people whose adult eligibility is unknown stop before upload (Q04).

### S03: Upload and preview

```text
Add your report
[Take a photo]  [Choose JPEG, PNG, HEIC or PDF]
Report preview                         Page selector
[Rotate] [Replace] [Remove]
Keep all text visible and check that the image is clear.
[Read report]  [Cancel]
```

Show the selected one-file, five-page and 20 MiB limits before upload, with image-resolution and observation limits explained where relevant (Q12).

### S04: Processing

```text
Reading your report
Upload complete
Waiting for processing / Preparing image / Reading text
Pages completed and pages remaining, when known
[Cancel]
If processing fails: reason and [Retry] [Choose another file]
```

Use honest stage progress, not a fabricated completion percentage. Apply the queue, timeout, cancellation and retry budgets selected in Q13; performance targets remain unmeasured.

### S05: Review extracted values

```text
Check every value against your report
DESKTOP
Source image, page and zoom | Test              Confidence  [Confirm]
Selected field highlighted | Value             Confidence  [Confirm]
                           | Unit              Confidence  [Confirm]
                           | Reference range   Confidence  [Confirm]
                           | Needs checking: reason and editable field
                           | Test context and report date
                           | [Exclude row with reason]
Account: [ ] Keep original report images
[Confirm all reviewed values and continue]
MOBILE
Source image and page controls
Selected observation and editable fields below the image
```

Confidence is an OCR review signal, not a clinical certainty score. Missing reference ranges can be explicitly confirmed as absent. Included test names, values and units cannot be missing. The final button remains disabled until every included field and row is reviewed; it cannot replace individual confirmation, and the server enforces the same condition. Manual additions require a visible source and location; exclusions require reasons and remain visible in coverage (Q11, Q12). No classification or urgent value interpretation appears before confirmation. General emergency-help information is always available and does not read the report (Q03).

### S06: Results

```text
Your reviewed results
Urgent notice, when applicable: text and next action
Overall screening status and which tests support it
Test name | Confirmed value and unit | Status text
[Flat labelled range band]            Value printed beside band
Why this result is shown
Unclassified tests and reasons
Confirmatory testing and clinician review message when applicable
[Guidance] [Meal plan] [Export]
Account: [Save to history]             Guest: [End session]
```

Approved wording for a diabetes-range result must say the value falls in a range consistent with diabetes and that a confirmatory test and clinician review are needed. It must not declare a diagnosis. An unavailable or unclassified result is never styled as normal (Q07).

### S07: Food and lifestyle guidance

```text
Your guidance
Foods to favour | Foods to limit | Portions
Physical activity | Weight | Sleep | Stress
Hydration | Alcohol and tobacco
Home monitoring habits | Follow-up
Reviewed content and review date
[Open weekly meal plan] [Back to results]
```

### S08: Weekly meal plan

```text
Sample weekly meal plan
Day       Breakfast       Lunch       Evening meal
Monday through Sunday: approved meals and household portions
Food notes and approved substitutions
This is an educational sample plan.
[Food guidance] [Export]
```

The library must cover banku, kenkey, fufu, waakye, jollof, gari, yam, plantain, beans, kontomire and garden eggs. Use a fixed seven-day template with reviewed substitutions for allergies, foods avoided and vegetarian preference. Portions and suitability require dietitian approval; withhold an unsuitable plan instead of generating a replacement (Q16).

### S09: History

```text
Saved reports
[Add report]                  [Filter by date]
Report date | Included tests | Screening summary | [Open]
Per report: [Export] [Delete]
Empty: No saved reports. [Add your first report]
Guest: History is available with a verified account.
```

### S10: Test trends

```text
Trends
[Test selector] [Date range] [Unit]
Labelled time series for the selected test
Date | Value | Unit | Source report
Missing dates or incomparable observations are explained.
[Open report] [History]
```

Do not mix tests into one series, interpolate missing observations or turn a trend into a diagnosis. Split series by test, source unit and relevant context; conversion is deferred. Keep distinct repeat results separate, omit superseded snapshots from the default trend and list undated observations separately (Q02, Q18).

### S11: Export

```text
Export reviewed results
[PDF summary] [One-page clinician sheet]
Included report, test values, dates and guidance sections
Original images excluded by default
[Prepare download]
Ready: [Download]             Failed: [Retry]
```

Both outputs use confirmed data and exact interpretation/content versions, including explicit non-classification outcomes. Use A4 portrait, optional display name and opaque report ID, private downloads expiring after 15 minutes, and no original images. Q19 specifies the ten-observation, one-page clinician-sheet acceptance check.

### S12: Sign in or create account

```text
Sign in                         Create account
Email                           Email
Password                        Password and confirmation
[Sign in]                       [Create account]
[Forgot password]               Privacy notice
[Continue as guest]             Email verification is required.
```

### S13: Email verification

```text
Verify your email
Check your inbox for a verification link.
[Resend verification] [Return to sign in]
Link result: Verified / Expired / Already used
Verified: [Continue to your account]
```

### S14: Password recovery

```text
Request a reset                  Set a new password
Email                           New password and confirmation
[Send reset link]               [Save password]
If the account exists, a link    Expired or used link: [Request another]
will be sent.                    Success: [Sign in]
```

Recovery uses the generic email, single-use token and session-revocation policy selected in Q17.

### S15: Account and data settings

```text
Account
Email and verification state
Theme [Light / Dark / System]    Language [English]
Image retention explanation and per-report controls
[Privacy and consent] [Sign out]
[Delete account and data]
```

### S16: Delete account and data

```text
Delete your account
Reports, values, images, guidance selections and exports will be removed.
Deletion timing and backup handling
Confirm your identity
[Cancel] [Delete account and data]
Submitted: deletion status and completion information
```

This action requires an explicit confirmation and recent authentication. It revokes sessions immediately; completion wording must reflect the actual deletion lifecycle (Q09, Q17).

### Screen states and accessibility

Each screen implements all four states below; a state can be a region on the screen rather than a separate route. Offline mode does not persist health data in browser storage. Already visible data may remain only in the active page's memory. Reload cannot restore unsaved guest work; verified account users can retrieve deliberately saved records after reconnecting and authenticating (Q08, Q14).

| Screen | Loading                            | Empty                                      | Error                                                       | Offline                                                                         |
| ------ | ---------------------------------- | ------------------------------------------ | ----------------------------------------------------------- | ------------------------------------------------------------------------------- |
| S01    | Load public copy/session state     | No session: show entry choices             | Session unavailable: offer guest entry when service returns | Explain that upload requires a connection                                       |
| S02    | Load current consent text          | Unanswered scope fields                    | Explain missing answers or unavailable consent              | Keep entered answers in memory; disable submission                              |
| S03    | Read file and preview              | Choose or photograph a report              | Explain format, size or decode failure                      | Preview locally; disable upload                                                 |
| S04    | Queue and OCR stages               | Job cancelled or absent                    | Failed stage and supported retry                            | Reconnect to the same job; do not duplicate it                                  |
| S05    | Load source and fields             | No supported observations found            | Identify missing or invalid fields                          | Keep unsaved edits in memory; disable confirmation                              |
| S06    | Request interpretation             | No confirmed eligible observations         | Interpretation unavailable; no guessed status               | Label visible result as the current in-memory snapshot                          |
| S07    | Load approved selections           | No applicable approved content             | Content unavailable; no generated substitute                | Show only already loaded content                                                |
| S08    | Load approved meal plan            | No suitable approved plan                  | Explain missing plan data                                   | Show only already loaded plan                                                   |
| S09    | Load report list                   | No saved reports or guest account required | Fetch failed with retry                                     | Do not imply unseen history is empty                                            |
| S10    | Load selected series               | No comparable data or too few points       | Explain incompatible unit/date                              | Show loaded points and an offline label                                         |
| S11    | Prepare PDF                        | No confirmed snapshot                      | Export failed or expired                                    | Disable generation; retain an already downloaded file only on the user's device |
| S12    | Submit authentication              | Blank form                                 | Generic authentication error                                | Disable submission and explain why                                              |
| S13    | Validate link or resend            | No verification link                       | Expired, invalid or used link                               | Retry after reconnecting                                                        |
| S14    | Send or consume reset link         | Blank email or missing reset token         | Invalid, expired or used link                               | Disable submission                                                              |
| S15    | Load account preferences           | Signed out                                 | Preference update failed                                    | Display loaded preferences; disable remote changes                              |
| S16    | Reauthenticate or request deletion | No active account                          | Deletion failed or pending                                  | Do not report deletion as complete                                              |

Visual rules follow `AGENTS.md`: solid off-white surfaces, one deep blue-green accent, red and amber for result status only, no gradients or emoji, no glass effects, no stock illustrations and no promotional AI badges. Use light/dark tokens for colour, spacing, radius and type; a 4 px spacing grid; radius no greater than 6 px; borders instead of soft shadows; one humanist sans and one monospaced face; two weights and at most five sizes. Q20 selects Source Sans 3, Source Code Pro, Lucide line icons at 2 px stroke, the palette and the spacing/type scales. Validation and confidence warnings use neutral text and markers, preserving red and amber for results.

Target WCAG 2.2 AA: text labels accompany colour, range bars have textual equivalents, trends have a data table, all controls are keyboard accessible, focus stays visible, dialogs manage focus, form errors name the field, and progress/status changes are announced. Source images support zoom and page navigation. Preserve usability with reflow, text enlargement and touch input. Q20 defines the browser, real-device and assistive-technology matrix; Q21 defines plain Ghanaian English and copy review.

## Processing and interpretation contract

The planned report lifecycle is `uploaded -> queued -> preprocessing -> extracting -> awaiting_review -> confirmed -> interpreted`. Interpretation may return an explicit non-classification outcome without evaluating numerical bands. Failure and cancellation are explicit outcomes; deletion is terminal. Saving a confirmed snapshot to history is a separate account action, not an implicit consequence of upload. A report revision increases when observations or context change. Confirmations, interpretations, guidance and exports bind to one revision.

1. Verify session ownership, scope and current consent before accepting a file.
2. Validate file contents as well as the extension, decode pages safely, strip unnecessary metadata, and prepare images. Do not send health data to an external OCR service.
3. Queue OCR through the engine interface. Return text spans, page coordinates and engine confidence; parsing creates separate candidate observations without interpreting them.
4. Preserve the original transcription, edited fields and source location while review is active. Distinguish absent reference ranges from extraction failures. Never substitute a reference range for the measured value.
5. Require explicit confirmation of every included observation, the report date or its unknown state, and relevant test context. Excluded rows keep an exclusion reason. A missing test/value/unit, unresolved duplicate or stale revision blocks confirmation.
6. At confirmation, freeze the reviewed snapshot and apply the image-retention choice. Revoke access to originals when retention is off and purge under Q09. Remove derived source copies and raw OCR text even when originals are retained. Completion of deletion must be observable and retryable. Later edits create a superseding revision; source deletion requires re-upload and review again (Q12, Q18).
7. Only the server rule engine reads `config/thresholds.json` to determine status. The front end renders the returned status, bounds and explanation keys without maintaining another threshold table. The engine rejects an unapproved configuration for clinical use and validates its schema, version, units, bounds and source notes at load time.
8. Run applicability checks before classification. Random glucose has no normal or prediabetes category; its supplied diabetes-range criterion requires confirmed classic symptoms. Missing symptom information is not a negative answer. Two-hour post-prandial values are not OGTT values. A test without an approved matching rule returns `not_classified` with a reason (Q05, Q06).
9. Urgent notices are a separate output, checked only on confirmed values under an approved policy. They must not be hidden by an otherwise normal-range category. The provided urgent values remain provisional project starting points. Q03 selects date-labelled historical flags, general emergency help for all users, and no numeric rules for excluded users; trigger applicability and wording still need approval.
10. Return per-test clinical status as `normal`, `prediabetes_range` or `diabetes_range`, when applicable. Model `not_classified` and `out_of_scope` as explicit non-classification outcomes, not extra clinical ranges. Q07 recommends the highest applicable range with coverage and discordance qualifiers, withholding an overall normal label when an urgent notice, unclassified included test or missing context exists. No applicable test yields null overall status with a reason. Clinical approval is still required.
11. Select explanations, guidance and meals only from versioned, reviewed content. Missing approved content produces an unavailable state. No free-form model output supplies patient guidance.

The threshold file deliberately preserves the supplied inclusive and exclusive endpoints in each reported unit. The rounded endpoints leave gaps for some higher-precision inputs. Do not silently fill those gaps, round a value into a band, or assume that converted units give identical boundary results. Q02 selects `not_classified` for such values and defers conversion in the first release; clinical approval remains pending. Laboratory reference ranges are displayed as source information and never replace the rule-engine thresholds.

The supplied classification bounds were rechecked on 2026-10-26 against the indexed publisher text of Tables 2.1 and 2.2 of the [ADA Standards of Care in Diabetes, 2026](https://diabetesjournals.org/care/article/49/Supplement_1/S27/163926/2-Diagnosis-and-Classification-of-Diabetes), including the [publisher PDF](https://diabetesjournals.org/care/article-pdf/49/Supplement_1/S27/848854/dc26s002.pdf). Direct retrieval of both the article and PDF returned HTTP 403. This check supports the transcription; it does not approve the application's eligibility rules, aggregation, urgent notices or guidance. The configuration remains version `0.1.0-draft`, with clinical use disabled until review (Q01).

## Data model

This is a logical model, not a database migration. Use opaque identifiers, UTC timestamps, explicit report/test dates, decimal representations for measured values and versioned records. Preserve source units and precision; binary floating-point rounding must not determine classification. Dates must distinguish a specimen/test date from an upload date and record uncertainty. Authentication records and health data have separate access paths. Q14 selects the architecture, encryption and key-management approach; hosting cost and legal review remain launch prerequisites.

For accounts, PostgreSQL holds deliberately saved structured health records and account/job metadata; encrypted blob storage holds retained images and temporary exports. Work in progress, extraction candidates and raw OCR stay in transient stores outside database backups. Redis carries opaque job identifiers and operational state, not report text or values, and has persistence disabled. Guest counterparts are transient objects only: no guest health records in PostgreSQL, durable blobs, Redis persistence, logs, browser storage or backups. Q08 and Q14 select a bounded memory service, internal worker capabilities and expiry/cleanup behavior, which must be verified during implementation.

| Entity               | Main fields                                                                                                                                                                                                            | Relations and lifecycle                                                                                                                                                                                                      |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Account              | `id`, normalized unique email, password hash, verification time, locale, theme, creation time, deletion state                                                                                                          | Owns saved reports, consents and sessions; never store a plaintext password; full deletion removes linked personal data.                                                                                                     |
| ReportSubject        | `id`, `account_id`, optional display name, consent reference                                                                                                                                                           | One consenting adult subject per account in the first release; reports belong to this subject, and family members cannot share its history.                                                                                  |
| AuthSession          | `id`, `account_id`, hashed token identifier, expiry, revocation time, recent-auth time                                                                                                                                 | Revocable account session; implementation and timeout policy under Q17.                                                                                                                                                      |
| AccountActionToken   | `id`, `account_id`, purpose, token hash, expiry, consumed time                                                                                                                                                         | Single-use verification/reset token; raw secrets are not logged or stored.                                                                                                                                                   |
| GuestSession         | opaque session identifier, created/expiry times, active report identifier, interpretation-consumed state                                                                                                               | Memory only; one active report, no account identity or history; retries of the same request must not consume another report.                                                                                                 |
| ConsentRecord        | `id`, account or transient guest owner, consent/privacy version, purpose, accepted time, withdrawn time                                                                                                                | Processing consent is separate from original-image retention; guest consent exists only for the active session; legal retention policy under Q15.                                                                            |
| Report               | `id`, owner, subject reference, consent reference, lifecycle state, revision, report/test date and certainty, scope answers, symptom/test-context answers, retention choice, saved time                                | Owns assets, jobs and observations; nullable saved time distinguishes work in progress from history; one subject and collection episode per report under Q18.                                                                |
| ReportAsset          | `id`, `report_id`, type, MIME type, page count, size, encrypted location or transient handle, expiry, deletion state                                                                                                   | Original and derived images are private; deletion covers thumbnails, preprocessed pages and source text; guest assets never become durable.                                                                                  |
| OcrJob               | `id`, `report_id`, engine/version, preprocessing/parser version, state, attempt, stage, timestamps, redacted error code                                                                                                | Worker uses report ownership and deletion state before reads and writes; queue messages contain no health payload.                                                                                                           |
| ExtractedObservation | `id`, `report_id`, source label, canonical test or unknown, raw numeric text, parsed decimal value, value operator, unit, raw/parsed reference interval, page/bounding boxes, field confidences and flags              | Transient candidate, not a backed-up database row; reference interval includes bound operators and its own unit; raw OCR is removed after review under Q09.                                                                  |
| ReviewedObservation  | `id`, extracted-observation reference when available, report revision, confirmed test/value/operator/unit/reference range, source precision, test date/context, edited-field flags, included/excluded state and reason | Separate from OCR output; preserves inequalities without converting them to exact values; field confirmation records who/when for an account or transient session; manually supplied fields have no invented OCR confidence. |
| ReviewConfirmation   | `id`, `report_id`, revision, included observation identifiers, confirmed context, confirmed time, actor, image-retention choice                                                                                        | Snapshot is complete only when all included observations are confirmed; changes invalidate it and derived output.                                                                                                            |
| Interpretation       | `id`, confirmation reference, threshold version, engine version, overall outcome/status/reason, coverage, generated time, content version                                                                              | Immutable result snapshot for a report revision; later rule versions do not silently rewrite history (Q18).                                                                                                                  |
| TestInterpretation   | `id`, interpretation/observation references, outcome, nullable status, matched rule identifiers, urgent notice identifiers, explanation keys                                                                           | Stores rule provenance and reasons; has no independent numeric threshold definitions.                                                                                                                                        |
| GuidanceItem         | stable key, version, locale, topic, approved text, applicability rules, source references, reviewer, approval date/status                                                                                              | Version-controlled under `content/guidance`; drafts cannot be selected for patients.                                                                                                                                         |
| FoodItem             | stable key, version, locale, Ghanaian food name, approved preparation/portion options, household measure, relevant allergens, sources and review metadata                                                              | Version-controlled under `content/foods`; nutrition claims and portion measures require review (Q16).                                                                                                                        |
| GuidanceSelection    | interpretation reference, approved content version, selected guidance keys and rule identifiers                                                                                                                        | Reproducible selection; no generated replacement text.                                                                                                                                                                       |
| MealPlan             | interpretation reference, library/version, seven day entries, meal slots, food/portion identifiers, approved substitutions                                                                                             | Deterministic or reproducibly seeded rule selection; no unsupported nutrition calculations or personalisation (Q16).                                                                                                         |
| ExportJob            | `id`, owner, interpretation reference, kind, locale, content version, state, expiry, private output location or memory handle                                                                                          | PDF and clinician sheet are snapshots; guest exports remain transient; access/download/deletion require ownership.                                                                                                           |
| DataDeletionJob      | opaque identifier, owner/report references needed during deletion, scope, requested time, stage, completion time, redacted failure code                                                                                | Revokes access, cancels jobs and deletes related data; any retained operational receipt must not contain health data or preserve a deleted identity (Q09, Q15).                                                              |

Relations are account to many reports; report to many assets, OCR jobs and observations; report revision to one active confirmation; confirmation to versioned interpretation; interpretation to many test results, guidance items and exports. Guest sessions follow the same validation contract without persistent rows. Database foreign keys, ownership checks and deletion ordering must enforce these relations.

Encrypt health data in transit and at rest, including worker connections, retained blobs and backups. Do not log health values, OCR text, images, patient names, filenames, consent answers, request bodies, tokens or exported documents. Application errors use redacted codes and a random correlation identifier. Do not send health-bearing pages to analytics or session replay. Use private responses with `Cache-Control: no-store`; do not cache health data in a service worker or persistent browser store. Deletion workers must prevent retries from recreating deleted data.

The project must follow Ghana's Data Protection Act, 2012 (Act 843). The Data Protection Commission's [compliance guidance](https://dpc.gov.gh/compliance/) identifies controller registration, privacy notices, safeguards and accountability as compliance concerns. A named owner must resolve the applicable legal basis, consent and caregiver authority, hosting/processor arrangements, retention and deletion obligations before launch (Q15). This specification is not a claim of legal compliance.

## Proposed API endpoints

Prefix: `/api/v1`. All payloads and responses use typed, validated schemas. `Public` means no authenticated session; `Session` means a valid guest or account session with ownership; `Account` means an authenticated account, including one awaiting verification; `Verified` means a verified account. A signed-in but unverified account cannot persist report history. It may use an explicitly separate guest flow while verification is pending (Q17).

These routes specify the planned contract only. Q17 selects server-side cookie sessions, CSRF tokens and origin checks, token lifetimes and SES for account email. Do not place credentials or report content in query strings. Resource access always checks ownership; a resource belonging to another user returns the same not-found response as an unknown identifier.

| Method and path                                                         | Access                    | Request and successful response                                                                                                                                                     |
| ----------------------------------------------------------------------- | ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GET /public-config`                                                    | Public                    | Available formats, approved upload limits, locale and consent versions; 200; no health data or client classification logic.                                                         |
| `GET /consent-text`                                                     | Public                    | Current versioned privacy and consent text; 200.                                                                                                                                    |
| `POST /guest-sessions`                                                  | Public                    | Create an opaque transient session; 201 with expiry and one-report policy.                                                                                                          |
| `DELETE /guest-sessions/current`                                        | Session                   | End guest session and erase transient report data; 204.                                                                                                                             |
| `POST /auth/register`                                                   | Public                    | Email/password; 202 with a generic verification response, without revealing whether an account exists.                                                                              |
| `POST /auth/verify-email`                                               | Public                    | Single-use verification token; 200 with verification state.                                                                                                                         |
| `POST /auth/resend-verification`                                        | Public                    | Email; 202 with generic response, rate limited.                                                                                                                                     |
| `POST /auth/login`                                                      | Public                    | Email/password; 200 with account/verification state and session established.                                                                                                        |
| `POST /auth/logout`                                                     | Account                   | Revoke current session; 204.                                                                                                                                                        |
| `POST /auth/password-reset-requests`                                    | Public                    | Email; 202 with generic response.                                                                                                                                                   |
| `POST /auth/password-resets`                                            | Public                    | Single-use token and new password; 204; revoke affected sessions.                                                                                                                   |
| `GET /account`                                                          | Account                   | Account identity, verification and preferences; 200.                                                                                                                                |
| `PATCH /account/preferences`                                            | Account                   | Locale/theme; 200; reject unsupported options.                                                                                                                                      |
| `POST /consents`                                                        | Session                   | Consent version and affirmative processing consent; 201 with consent identifier.                                                                                                    |
| `DELETE /consents/{consent_id}`                                         | Session                   | Withdraw consent, prevent new processing and begin deletion as applicable; 202 with deletion state (Q09, Q15).                                                                      |
| `POST /reports`                                                         | Session                   | Multipart supported file, consent identifier and scope/context answers; 202 with report identifier, revision and OCR job identifier.                                                |
| `GET /reports/{report_id}`                                              | Session                   | Owned report metadata, lifecycle and current revision; 200.                                                                                                                         |
| `GET /reports/{report_id}/ocr-jobs/{job_id}`                            | Session                   | Stage, progress when measurable and redacted failure/retry state; 200.                                                                                                              |
| `POST /reports/{report_id}/ocr-jobs`                                    | Session                   | Retry an eligible failed job for the current revision; 202; do not create parallel duplicate jobs.                                                                                  |
| `DELETE /reports/{report_id}/ocr-jobs/{job_id}`                         | Session                   | Cancel processing; 202 with cancellation state.                                                                                                                                     |
| `GET /reports/{report_id}/pages/{page_number}`                          | Session                   | Private source page for review; 200 binary response; 410 when already deleted.                                                                                                      |
| `GET /reports/{report_id}/review`                                       | Session                   | Observations, source coordinates, confidences, flags and current context/revision; 200.                                                                                             |
| `PATCH /reports/{report_id}/review`                                     | Session                   | Expected revision, field edits, confirmations, exclusions and context corrections; 200 with new revision; invalidates previous confirmation/output.                                 |
| `POST /reports/{report_id}/confirmations`                               | Session                   | Expected revision, confirmation of all included observations/context, retention choice; 201 with snapshot and source-deletion state.                                                |
| `POST /reports/{report_id}/interpretations`                             | Session                   | Confirmation identifier/revision; 201 with engine output; same idempotent retry returns existing result; 409 if review or clinical configuration is not ready.                      |
| `GET /reports/{report_id}/interpretations/{interpretation_id}`          | Session                   | Immutable per-test/overall result, coverage and rule/content versions; 200.                                                                                                         |
| `GET /reports/{report_id}/interpretations/{interpretation_id}/guidance` | Session                   | Approved guidance selection, provenance and weekly plan; 200, including explicit unavailable sections.                                                                              |
| `POST /reports/{report_id}/save`                                        | Verified                  | Explicitly save the confirmed snapshot and result or non-classification outcome to history; 200; duplicate request does not duplicate history. Guest import is not supported (Q08). |
| `GET /reports`                                                          | Verified                  | Paginated saved history with date/test filters and cursor; 200.                                                                                                                     |
| `GET /trends`                                                           | Verified                  | Selected test, date range and source unit; 200 with confirmed dated observations and source identifiers; no cross-unit conversion in this release (Q02).                            |
| `DELETE /reports/{report_id}/images`                                    | Session                   | Remove all retained original/derived source assets; 202 with deletion state, or 204 if already removed.                                                                             |
| `DELETE /reports/{report_id}`                                           | Session                   | Revoke report access, cancel jobs and delete associated data; 202 with deletion state.                                                                                              |
| `POST /reports/{report_id}/exports`                                     | Session                   | Interpretation identifier, `summary` or `clinician_sheet`, locale; 202 with export identifier.                                                                                      |
| `GET /exports/{export_id}`                                              | Session                   | Export status/expiry or redacted failure; 200.                                                                                                                                      |
| `GET /exports/{export_id}/download`                                     | Session                   | Private PDF attachment; 200; 409 until ready, 410 after expiry.                                                                                                                     |
| `DELETE /account`                                                       | Account                   | Recent authentication and explicit deletion confirmation; 202 with deletion receipt; immediately revoke account sessions.                                                           |
| `GET /deletions/{deletion_id}`                                          | Session or scoped receipt | Redacted progress/completion; 200; account deletion uses a short-lived receipt capability rather than retaining normal account access (Q09, Q17).                                   |

Report creation, job retries, confirmation, interpretation, saving, export and deletion requests accept scoped idempotency keys. Versioned review requests carry an expected revision; stale updates return 409 without overwriting newer work. Server-side validation prevents bypassing consent, review, eligibility, ownership and guest restrictions. Health-related URLs use opaque identifiers; HTTP access logs must not retain raw sensitive paths or query values.

Errors have a stable code, translation key, optional field identifiers, retryable flag and correlation identifier; they never echo health data. HTTP 400 covers malformed requests, 401 absent/expired authentication, 403 disallowed account capabilities, 404 unknown or unowned resources, 409 lifecycle/revision conflicts, 410 expired transient resources, 413 oversize uploads, 415 unsupported formats, 422 invalid fields, 429 rate limits and 503 unavailable processing services. Excluded or unclassifiable observations are explicit domain outcomes, not server failures.

## Error cases and recovery

| Case                                                                            | Required behavior and recovery                                                                                                                                                                                                                                                      |
| ------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Consent declined, missing, outdated or withdrawn                                | Do not start processing; explain the required consent or end the flow; withdrawal cancels processing and follows the deletion policy.                                                                                                                                               |
| Excluded population or unknown eligibility                                      | Do not classify; show the approved clinician referral message and permitted next steps (Q04).                                                                                                                                                                                       |
| Camera unavailable or permission denied                                         | Explain the issue and offer file selection; do not repeatedly prompt for camera access.                                                                                                                                                                                             |
| Unsupported, spoofed, empty, oversized or corrupt file                          | Reject before OCR with a specific safe reason; preserve no invalid upload; allow a supported replacement.                                                                                                                                                                           |
| Password-protected PDF, excessive pages or failed HEIC/PDF decode               | Explain the supported limits; request an unlocked/readable supported copy; do not ask the user to send a document password (Q12).                                                                                                                                                   |
| Blurred, rotated, dark, cropped or unreadable image                             | Attempt allowed preprocessing; if still unreadable, request a clearer source; do not invent values.                                                                                                                                                                                 |
| No supported tests or an unsupported OGTT time point                            | Show an empty extraction state or an explicitly unclassified observation; do not reinterpret another test as a supported one.                                                                                                                                                       |
| Multiple people, repeated panels or ambiguous duplicate rows                    | Block combining observations until the source/subject and inclusion decisions are resolved (Q12, Q18).                                                                                                                                                                              |
| Missing or ambiguous test name, decimal mark, value or unit                     | Flag the field for correction; never infer a unit solely from the apparent magnitude; do not interpret an incomplete observation.                                                                                                                                                   |
| Missing reference range                                                         | Distinguish absent-on-report from unreadable; allow explicit confirmation of absence; do not fill it with the application's screening thresholds.                                                                                                                                   |
| Invalid numeric input or unit/test mismatch                                     | Reject non-finite, negative or malformed values and require correction/exclusion of zero; reject glucose units on HbA1c and unsupported conversions. Preserve extreme positive values for source recheck and approved rules; do not impose an invented upper clinical cutoff (Q02). |
| Inequality value, unknown specimen or insufficient fasting/OGTT/symptom context | Preserve the source notation; return a review requirement or `not_classified`; do not silently change an inequality into an exact value (Q02, Q05, Q06).                                                                                                                            |
| Conflicting source values, lab ranges or tests                                  | Preserve each observation and its provenance; highlight the inconsistency; do not silently average values or treat a lab reference range as a diagnostic rule (Q07).                                                                                                                |
| Low or unavailable confidence                                                   | Label the specific field and require explicit review; unavailable confidence is not high confidence; the same confirmation gate still applies to high-confidence fields.                                                                                                            |
| Queue unavailable, worker crash, timeout or OCR failure                         | Return a redacted retryable state; use bounded, idempotent retries; no partial extraction becomes a result automatically (Q13).                                                                                                                                                     |
| Connection lost during upload, review or interpretation                         | Explain whether work reached the server; reconnect by existing job/report identifier when possible; retain only in-memory unsaved edits; do not automatically upload a second report.                                                                                               |
| Expired guest session or deleted source                                         | Explain that the transient report/source is unavailable; start a new upload if necessary; never restore it from an undisclosed persistent copy.                                                                                                                                     |
| Unconfirmed fields, stale revision or two review tabs                           | Return a conflict and reload the current revision; do not use the earlier confirmation.                                                                                                                                                                                             |
| Draft, missing, invalid or unsupported threshold configuration                  | Block interpretation and return a service/configuration error; never fall back to hard-coded thresholds or an older unapproved rule set.                                                                                                                                            |
| Value falls in a precision gap or no applicable rule exists                     | Return `not_classified` and an approved explanation; never label it normal by default (Q02, Q06).                                                                                                                                                                                   |
| Very high or low confirmed value                                                | Surface an approved urgent notice prominently and in exports; exact action text and applicability remain subject to clinical review (Q03).                                                                                                                                          |
| No approved guidance or meal selection                                          | Show the unavailable section and clinician-review route; never generate replacement advice.                                                                                                                                                                                         |
| Login, verification or reset failure; rate limit                                | Give an accessible, non-enumerating message; respect retry timing; expired/used tokens require a new link.                                                                                                                                                                          |
| Cross-account resource request                                                  | Return a generic not-found response; do not disclose whether the report or export exists.                                                                                                                                                                                           |
| Missing date, one trend point or incomparable units                             | Explain what can be displayed; do not substitute upload date for an unknown test date or draw an unsupported trend.                                                                                                                                                                 |
| PDF generation failure or overflow of clinician sheet                           | Keep the confirmed result available; retry export; do not silently truncate results or shrink text below the agreed readability target (Q19).                                                                                                                                       |
| Image/report/account deletion fails or remains pending                          | Revoke access and stop new processing; show pending/failed status, retry deletion and alert operations without health data; do not claim removal is complete (Q09).                                                                                                                 |

## OCR accuracy target and evaluation

The following are selected release acceptance targets, not measured performance or a guarantee. Q10 defines dataset ownership roles, coverage and approval requirements; Q11 defines confidence and correction behavior. Partners, authorized reports, score calibration and measured acceptance remain outstanding. Character accuracy alone is insufficient because one changed decimal, unit or row association can alter the meaning of a report.

Evaluate the complete preprocessing, OCR and parsing pipeline before human correction, using consented, de-identified reports with independently checked ground truth. Keep evaluation reports separate from tuning data at the patient/report level and include unseen layouts. Avoid counting resizes or re-encodings of one report as independent reports. The proposed held-out set contains at least 300 distinct reports and 1,500 supported observations, with at least 30 reports in each input format and at least 30 observations for each supported test. Include representative Ghanaian lab layouts, both glucose units, percent HbA1c, mobile photographs, scans, multi-page PDFs, rotation, glare, blur, low contrast and decimal-comma notation. Report coverage gaps rather than claiming they were tested.

| Metric                          | Proposed target                                                                                        | Definition                                                                                                                                                                                                       |
| ------------------------------- | ------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Complete observation extraction | At least 95%                                                                                           | An annotated observation is correct only if test, exact decimal value, unit and reference interval or explicit absence all match; denominator is all supported ground-truth observations, including missed rows. |
| Value extraction                | At least 99%                                                                                           | Exact numeric and inequality match without rounding; denominator is all supported ground-truth observations, including missing and misassociated values.                                                         |
| Unit extraction                 | At least 99%                                                                                           | Correct source unit after an approved spelling-only normalization; missing units in output count as errors when present in the source.                                                                           |
| Test detection and association  | At least 98% precision and 98% recall                                                                  | Correct canonical test and source row; false rows count against precision and missed rows against recall; post-prandial and OGTT must remain distinct.                                                           |
| Reference range extraction      | At least 95%                                                                                           | Correct bounds, operators and unit where present; absent-reference handling is also reported separately to expose fabricated ranges.                                                                             |
| High-risk error detection       | No observed unflagged status-changing value, unit or test-association error in the held-out safety set | After approved thresholds exist, use a separate offline evaluation harness to identify status-changing errors; this never authorizes pre-confirmation interpretation in the user flow.                           |
| Confirmation gate               | 100% of attempted bypasses rejected                                                                    | Even perfect OCR does not permit interpretation without user confirmation of all included values and required context.                                                                                           |

Report numerator, denominator and uncertainty interval for each metric, plus breakdowns by format, test, unit, lab/layout and image-quality group. Do not hide a weak group inside the overall average. Publish rejected/unreadable-report counts and end-to-end success rate separately; poor images remain in the evaluation denominator unless a predefined unsupported-input rule applies. Flagged errors still count as extraction errors, and corrected values are not counted as raw OCR successes.

Each extracted field carries a normalized score between 0 and 1 or an explicit unavailable value, its source coordinates and review flags. The proposed initial low-confidence flag is below 0.90, but calibration must establish the operating point; it is not a probability of medical correctness. Missing units, unsupported tests, conflicting values, ambiguous decimal notation and source association problems are flagged regardless of score. Manually entered fields carry an entered-by-user state instead of a fabricated OCR score. All fields remain subject to confirmation (Q11).

Fixtures will live under `tests/fixtures/reports` only when they are authorized and de-identified. Synthetic reports can cover boundary and error cases but cannot establish real-report accuracy. No private patient documents are added in Phase 0. Q10, Q12 and Q13 select coverage, input limits, processing-latency and retry targets; later phases must validate them.

## Verification plan and Phase 0 exit check

Later phases must write meaningful tests alongside their implementation. Pytest covers validated schemas, parser behavior, the OCR interface, rule boundaries loaded from the configuration, eligibility, confirmation enforcement, revision conflicts, ownership, retention and deletion. Vitest covers review controls, translations, unit presentation and non-colour status labels. Playwright covers guest and verified-account flows, camera fallback, consent refusal, low-confidence correction, offline/error states, history, exports, deletion and keyboard access. PDF verification includes visual checks of both formats and the one-page constraint. Q22 selects Prettier, ESLint, Ruff, strict type checks and GitHub Actions, with additional evidence per phase. No application tests are implemented in Phase 0.

Phase 0 is complete when:

- `docs/spec.md`, `docs/phase-0-decisions.md`, `config/thresholds.json` and `docs/phase-log.md` exist and are readable.
- The spec covers stories, all screen sketches, the data model, API endpoints, error cases and measurable OCR targets.
- The thresholds file parses as JSON, has a version and a source note on every classification and urgent rule, and preserves the supplied boundaries and operators.
- There are no invented post-prandial diagnostic bands, random-glucose normal/prediabetes bands or HbA1c urgent triggers.
- Every unresolved choice identified in this spec and configuration is represented by a question in the final section.
- The phase log records the changes, checks and remaining decisions, and no application code has been added.

These checks establish a planning artifact, not a clinically approved or functioning application. Completing Phase 0 does not authorize beginning Phase 1.

## Decision questions and answers

The following original questions are retained for traceability. All 22 have answers in [the Phase 0 decision record](phase-0-decisions.md), under matching Q01-Q22 headings. Product and engineering defaults are selected. Clinical recommendations await professional approval, and the remaining external launch questions follow this list.

1. **Q01 - Clinical ownership and approval:** Who will review and sign off the thresholds, explanation copy and future revisions, what evidence and full-source review will they require before enabling clinical use, and how often will the configuration be checked against updated standards?
2. **Q02 - Precision, units and validity:** What native-unit comparison, decimal-comma normalization, precision, rounding and conversion policy should apply, how should gaps between the supplied rounded endpoints be handled, and what rules cover inequality results, zero or implausible values, unsupported units and HbA1c units other than percent?
3. **Q03 - Urgent notices:** Which low/high triggers, strict boundary operators, applicable tests/populations, report-age checks, symptom overrides, referral actions and locally appropriate urgent-contact wording will the clinical reviewer approve, including behavior for excluded users and historical results?
4. **Q04 - Eligibility:** What age defines a child, how should pregnancy and already-treated status be asked without collecting treatment details, how should uncertain answers be handled, and may excluded users use review, export or history without classification?
5. **Q05 - Clinical context:** Which exact questions establish fasting, specimen applicability, OGTT protocol/time point and classic symptoms, how are absent or unknown answers handled, and what HbA1c applicability or interference checks must block or qualify interpretation?
6. **Q06 - Post-prandial and other unsupported tests:** Should two-hour post-prandial values remain review-only with no screening category, or will the clinical reviewer supply separate sourced rules, and how should unsupported OGTT time points, aliases and specimen types be presented?
7. **Q07 - Overall result:** Should the summary use the highest applicable screening range, what happens when tests disagree or some remain unclassified, when must overall status be withheld, and which approved explanations cover incomplete panels, discordance and urgent notices alongside range status?
8. **Q08 - Guest session:** Does one report mean one file, one multi-page report or one successful interpretation per session, what session/processing expiry and cancellation rules apply, is memory-only server processing the intended meaning of storing nothing, and may a guest deliberately transfer a report to a newly verified account?
9. **Q09 - Retention and deletion:** What exact deadlines apply to unconfirmed uploads, originals, derivatives, raw OCR text, saved records, exports, queue state and backups, how long may opted-in originals remain, how is consent withdrawal handled, and what deletion receipt, retry/escalation and completion evidence should users receive?
10. **Q10 - OCR acceptance data:** Who will supply and authorize the de-identified Ghanaian evaluation reports and independent annotations, which lab/layout/quality strata must be covered, and are the proposed dataset size, extraction targets and zero-observed-unflagged-high-risk-error gate acceptable?
11. **Q11 - Confidence and correction:** How should engine scores become field-level confidence, what calibrated low-confidence cutoff and warning burden are acceptable, which flags force correction, and should manual entry/addition or unresolved extraction failures be allowed to proceed after explicit review?
12. **Q12 - Upload and review limits:** What file-size, image-resolution, page-count, format/decoder and concurrency limits apply, are multiple uploads allowed in one report, how should repeated panels or mixed-patient pages be resolved, and what re-upload/edit flow is available after source deletion?
13. **Q13 - Service targets:** What supported device/network conditions, processing latency, queue capacity, availability, timeout, retry, cancellation and abuse-rate budgets define an acceptable service, and who handles operational failures without accessing unnecessary health data?
14. **Q14 - Infrastructure and offline behavior:** Where will the API, PostgreSQL, Redis, OCR workers and encrypted assets run, how will encryption keys and backups be managed, how will guest jobs remain transient across the queue/worker boundary, and is offline use limited to already loaded in-memory content?
15. **Q15 - Data protection responsibilities:** Who is the controller and privacy contact, what registration, legal basis, notices, caregiver authority and processor/hosting arrangements are required under Act 843, and what retention exceptions, rights-handling and incident procedures must be approved before real health data is processed?
16. **Q16 - Guidance and food review:** Who will clinically and culturally review the guidance and Ghanaian food library, which portion measures and meal-slot/substitution rules should be used, what preferences, allergies, budgets or dietary restrictions belong in the first release, and what approved content covers follow-up timing and every lifestyle topic?
17. **Q17 - Account security:** Which email provider, verification/reset flow, password rules, authentication transport, CSRF protection, session lifetimes, rate limits and recent-auth checks should be used, how should unverified accounts interact with guest mode, and how should deletion-status access work after account sessions are revoked?
18. **Q18 - Ownership and history:** Is each account limited to one report subject or must caregivers manage separate consented profiles, should saving be an explicit action as proposed, and how should edits, duplicates, missing dates, repeat results and later threshold/content versions affect history and trends?
19. **Q19 - Exports:** Which page size, identifiers, date/unit conventions, language, source references and guidance sections belong in each PDF, how should many-test reports fit the required one-page clinician sheet without dropping results or reducing legibility, are original images ever included, and what download expiry and accessibility requirements apply?
20. **Q20 - Visual and accessibility baseline:** Which humanist sans, monospaced face, two weights, size scale, token values and line-icon family should be adopted within the fixed design rules, and which phones, browsers, screen readers, contrast checks and light/dark defaults define acceptance?
21. **Q21 - Language and copy governance:** What English reading level and clinical terminology should be used, who approves patient-facing and caregiver wording, how should interface/server/export copy and reviewed content share translation keys, and who will own a later Twi translation and review?
22. **Q22 - Engineering checks:** Which single formatter and linter per language and CI platform should enforce the code rules, who owns the fixture and clinical review checks, and what browser, accessibility, privacy, OCR and PDF checks must pass at each later phase's exit?

## Remaining launch questions

Default design choices have answers in the decision record. The following external facts, approvals and measurements remain outstanding; they do not prevent a separately requested phase from using synthetic data locally.

1. Who are the named Ghana-registered clinical lead, dietitian and English patient-copy reviewer, and when will they approve the recommended clinical and content policies (Q01-Q07, Q16, Q21)?
2. Which legal entity is the controller, who is the privacy contact, and what documented registration, sensitive-data basis, caregiver-consent, overseas-processing and retention conclusions apply (Q09, Q15)?
3. What Ghana FDA assessment, classification and authorization, if any, are required for the intended pilot and public release (Q15)?
4. Which laboratory partners and data steward will provide authorized evaluation reports and independently checked annotations (Q10)?
5. What hosting budget, sender domain and named engineering/operations owner are available for the proposed deployment, and do benchmarks justify its sizing (Q13, Q14, Q17, Q22)?
6. Do measured OCR, usability, accessibility, security, deletion and PDF results meet the selected targets before release (Q10-Q13, Q19-Q22)?
7. At the later Twi phase, which Twi variety and qualified reviewers should the project use (Q21)?
