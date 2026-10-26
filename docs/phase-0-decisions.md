# Phase 0 decisions for the first release

Date: 2026-10-26. These answers select a practical baseline for the Ghana-first, mobile-first application at the project owner's request. They supplement `docs/spec.md`. Product and engineering choices are selected for implementation; clinical policies are recommendations awaiting a named clinician's approval. External appointments, permissions, infrastructure costs and measured results are not assumed to exist.

The first release serves consenting adults reading their own laboratory results, including adults assisted by a caregiver. It is a screening and education tool with explicit review of every value. This document adds no application code and does not start Phase 1. `config/thresholds.json` remains the sole numerical classification source, at version `0.1.0-draft`, with clinical use disabled.

Operational limits and retention periods below are project defaults, not statutory deadlines or measured performance. Clinical sources support review of the policies; they do not constitute approval of this application.

## Q01

**Clinical ownership and approval.** Appoint a Ghana-registered physician experienced in adult diabetes care as clinical lead, and a registered dietitian familiar with Ghanaian foods as nutrition reviewer. The project owner arranges these appointments; the engineering maintainer implements approved changes. Do not invent reviewer names or approval dates.

Require recorded approval of thresholds, applicability checks, urgent notices, explanations, follow-up wording and boundary cases before patient use. The physician signs clinical policies; the dietitian signs food portions and meal content, with physician review of clinical restrictions. Record reviewer identity, date, sources and version in each approved artifact.

Check standards quarterly and within 30 days of a new annual ADA edition, correction or relevant safety update. Review affected content immediately when a safety issue is found. Preserve older versions for saved results. The [ADA 2026 diagnostic criteria](https://diabetesjournals.org/care/article-pdf/49/Supplement_1/S27/848854/dc26s002.pdf) remain the draft source; a reviewer must obtain the full source because direct retrieval was blocked during Phase 0.

**Status:** Governance selected; reviewer appointment and clinical approval remain launch requirements.

## Q02

**Precision, units and validity.** Compare exact decimal values in the reported unit, preserving the original text and precision. Do not round before classification. Accept a decimal comma only when its meaning is unambiguous and explicitly reviewed; mixed separators or ambiguous grouping require correction. Never guess units from magnitude.

For the first release, keep the supplied bounds exactly as written in the configuration. Values in gaps between rounded endpoints return `not_classified` and a clinician-review explanation. This is a deliberate conservative policy, not permission to silently extend a band. Any later continuous-interval policy needs clinical approval and a new configuration version.

Display source units. Split trends by test and unit; defer conversion and HbA1c units other than percent. Preserve inequality results such as a reported less-than value as inequalities, with no exact-value classification or numeric urgent inference in this release. Reject malformed and non-finite input. Require correction or exclusion of negative or zero measurements without substituting another value. Do not invent an upper physiological cutoff: a very large positive value must be rechecked against the source and, once confirmed and applicable, assessed using the configured rules.

**Status:** Comparison behavior selected; clinical approval of applicability and exception wording remains pending. Numeric bounds are unchanged.

## Q03

**Urgent notices.** Retain the four provisional triggers and their strict comparison operators in `config/thresholds.json`. They require physician approval; do not reinterpret them as diagnostic criteria. For eligible users, evaluate approved numeric urgent rules only after confirmation, across the glucose tests listed by each rule. Do not add an HbA1c urgent trigger.

Show the collection date beside every notice. On historical reports, say that the flag describes the result at the time of that test. Never erase a concerning flag because a report is old, or imply that an old value proves a current emergency. Unknown dates remain explicit. Current severe symptoms take priority over report age; do not introduce an unsupported age cutoff.

Provide a separate, always-available emergency-help message that does not inspect OCR values. Recommended symptom examples for clinical review are unconsciousness, a seizure, severe confusion or difficulty breathing. Direct such users to emergency care without requiring upload or account creation. [NHS high-glucose information](https://www.nhs.uk/conditions/high-blood-sugar-hyperglycaemia/) and [low-glucose information](https://www.nhs.uk/conditions/low-blood-sugar-hypoglycaemia/) support these symptom concerns; Ghana's [National Ambulance Service](https://nas.gov.gh/terms-of-use.php) identifies 112 as the emergency number.

For excluded users, offer the general emergency-help and clinician-referral messages, without applying numeric classification or tailored guidance. Urgent result text must direct prompt clinical assessment, remain visible in exports, and take precedence over routine meal/activity suggestions. The physician must approve the exact action and timing language before release.

**Status:** Presentation and routing selected; numeric trigger applicability and patient wording need clinical approval.

## Q04

**Eligibility.** Limit classification to adults aged 18 or older who are not pregnant and have not already been diagnosed with diabetes or begun diabetes care. Ask three short questions with Yes, No and Not sure options; age needs only an adult-eligibility answer, not a date of birth. Extending exclusion to known diabetes avoids suggesting that a person with an established diagnosis can be reclassified as normal.

Pregnancy, age below 18, established diabetes/care, or uncertainty prevents classification and tailored guidance. If adult eligibility is not established, stop before upload and offer clinician referral and general emergency information. Adults excluded by pregnancy, known diabetes or uncertain clinical eligibility may consent to upload, correct, download and explicitly save a reviewed transcription. Mark it `out_of_scope` or `not_classified`, with no screening category, and direct them to their clinician. These records may appear as raw values in their own history without diagnostic bands. Do not collect treatment details.

**Status:** First-release scope selected; screening questions and referral copy require clinical review.

## Q05

**Clinical context.** Ask only questions relevant to the extracted test, before final confirmation:

- Fasting: whether there was no calorie intake for at least eight hours before collection; water is allowed. Offer Not sure.
- Specimen: whether the report identifies a laboratory plasma result. A laboratory name or user guess alone cannot establish specimen type. Unknown or unsupported specimen information withholds the affected classification.
- OGTT: whether the report documents the standard 75 g oral glucose tolerance test and a two-hour sample. A result after an ordinary meal does not satisfy this condition.
- Random glucose: whether unusual thirst, increased urination or unexplained weight loss was present around the time of the sample. Record each answer, including uncertainty. The physician must approve how these answers establish classic symptoms; no app diagnosis of a hyperglycemic crisis is attempted.
- HbA1c: whether the report is a laboratory test in percent and whether the report or clinician has warned it may be unreliable. Ask about known blood disorders, anemia, recent transfusion/blood loss or other clinician-identified interference without requesting detailed medical history. A positive or uncertain interference answer withholds HbA1c classification and requests review.

Store context with the observation and report revision, not as a permanent assumption about future reports. Missing context withholds only affected tests; it also prevents an unqualified overall result. Protocol and interference requirements derive from the [ADA diagnostic section](https://diabetesjournals.org/care/article/49/Supplement_1/S27/163926/2-Diagnosis-and-Classification-of-Diabetes). The clinical lead must review assay applicability and make the short questionnaire usable for local laboratory reports.

**Status:** Required context selected; symptom mapping, HbA1c questionnaire and lab applicability need approval.

## Q06

**Post-prandial and unsupported tests.** Extract two-hour post-prandial values, but do not assign a diagnostic category. Show a reviewed value, its lab reference interval and an explicit explanation that this test has no screening band in the app. Approved glucose urgent rules may still apply under Q03. Do not borrow OGTT bands.

Recognize common labels through a versioned alias dictionary, while distinguishing an alias from evidence of test protocol or specimen. Unknown labels, unsupported OGTT time points and unsupported specimen types remain review-only. Reference ranges are source information, never substitutes for the configured screening bands.

**Status:** Selected. Adding classification to these tests requires a later sourced and approved change.

## Q07

**Overall result.** Return the highest applicable range among confirmed, eligible, classifiable tests, but describe it as a summary of those tests, not a diagnosis. Always show every per-test result and a coverage count. Different ranges produce a discordance message; never average them.

Withhold an overall normal label if any included test is unclassified, context is missing, or an urgent notice exists. If valid tests indicate an elevated range while others are unclassified, show the elevated summary with an explicit incomplete-coverage qualifier. If no test is classifiable, overall status is null with a reason. Excluded people receive an out-of-scope outcome.

An urgent notice becomes the leading result message, even when a per-test range would otherwise say normal. Never infer a diabetes subtype. Diabetes-range wording must request confirmatory testing and clinician review.

**Status:** Recommended aggregation policy selected for review; no production aggregation is approved yet.

## Q08

**Guest sessions.** One report means one logical report for one person and collection episode, submitted as one file containing up to five pages. Allow correction, re-upload before successful confirmation, and safe retries of that report. After completion, the session may view and download it but cannot interpret a second report; the user must explicitly end the session and start again. This is a session limit, not a lifetime limit enforced by fingerprinting.

Use memory-only server processing. Show plain consent text explaining that the report is held temporarily during use and is not saved to history. Start with a 30-minute inactivity timeout and a two-hour renewable session window. Warn two minutes before expiry, provide an accessible extension action, and allow at least ten extensions for an admitted session. Reject new sessions before upload if capacity is unavailable; do not evict an active review to admit another user. Background polling does not count as user activity.

End-session and cancellation erase transient data promptly; a closed browser is cleaned up by timeout because immediate server detection is not guaranteed. A crash loses guest work. Guests cannot opt to retain originals or transfer data to an account in this release. Creating an account is a separate flow and requires a fresh upload.

**Status:** Selected. Persistence and timeout behavior must be demonstrated in later tests.

## Q09

**Retention and deletion.** Use the following first-release schedule, subject to documented privacy review before real data:

| Data                                       | Selected lifecycle                                                                                                                                                                                                                                                              |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Guest data                                 | Memory only; remove at end-session, cancellation or expiry under Q08. Never back it up.                                                                                                                                                                                         |
| Account work not explicitly saved          | Expire 24 hours after upload, including unconfirmed and confirmed-but-unsaved work. Show the expiry time.                                                                                                                                                                       |
| Original images, derivatives and raw OCR   | Revoke source access at confirmation when retention is off; purge within five minutes, retry failures and alert operations. Never include temporary source material in backups.                                                                                                 |
| Opted-in originals                         | Explicit choice for each saved account report; retain up to 12 months, or until earlier report/account deletion. An unsaved report still expires after 24 hours. Give 30 days' notice before retained-source expiry. Derived images and raw OCR are still removed after review. |
| Saved reviewed values and result snapshots | Retain until the user deletes them or the account is removed. After 24 months without sign-in, give 30 days' notice and delete an inactive account unless the owner returns.                                                                                                    |
| Prepared account exports                   | Private and available for 15 minutes, then purge. Guest exports remain in session memory. Downloaded copies are controlled by the user.                                                                                                                                         |
| Queue payloads and job results             | Opaque identifiers only; remove on completion or cancellation. No OCR result, traceback containing values, or image in Redis.                                                                                                                                                   |
| Full report/account deletion               | Revoke access and cancel work immediately; remove active data within 24 hours; expire remaining backup copies within 31 days.                                                                                                                                                   |
| Operational logs                           | Redacted events only, 30 days. Short-lived abuse-control keys expire within 24 hours and contain no health data.                                                                                                                                                                |

Use a short-lived, scoped deletion receipt to show active deletion and backup-expiry dates. Keep encrypted opaque deletion tombstones for 35 days solely to prevent restoration of deleted records; remove them afterwards. Restore backups in isolation and apply tombstones before allowing access. Delete linked consent/account records according to the approved schedule; do not assume an indefinite audit exemption.

Consent withdrawal stops processing and starts the same deletion flow. Do not claim that backups have been erased while their retention window remains. Any legal retention exception requires a documented basis, restricted access and truthful notice; it is not a default exemption.

**Status:** Engineering schedule selected; lawful retention, notices and exceptions need privacy review.

## Q10

**OCR acceptance data.** The project owner obtains written cooperation from at least three Ghanaian laboratories or clinical partners. A designated data steward verifies permission and de-identification before reports enter fixtures. Two independent annotators check test, exact value, unit, reference interval and row association; a clinician adjudicates discrepancies.

Keep the proposed held-out minimum of 300 independent reports and 1,500 supported observations, at least 30 reports per input format and 30 observations per supported test. Include both glucose units, percent HbA1c, unseen layouts and difficult photographs. Split by original report/person; resized copies cannot appear in both tuning and evaluation sets. Add a separate curated safety set for boundaries, missing decimals, wrong units and row swaps.

Retain the specification's targets: 95% complete observations and reference ranges, 99% values and units, 98% test detection precision and recall, and no observed unflagged status-changing error in the held-out safety set. Report uncertainty and subgroup performance. A failing or inadequately represented subgroup is not approved by a good aggregate score. Synthetic data supports development, not a claim of real-world accuracy. The mandatory confirmation gate must reject every tested bypass.

**Status:** Evaluation plan selected; partners, authorized fixtures and measured results remain outstanding.

## Q11

**Confidence and correction.** Preserve the engine's raw score and derive a separate field score. Start conservatively with the lowest valid confidence among tokens needed for a field, normalized to 0-1; document engine-specific behavior. The initial review flag is below 0.90, not a claim of calibrated probability. Calibrate on development data, freeze the mapping, then evaluate on untouched reports. Label the UI score as extraction confidence.

Missing units, ambiguous separators, overlapping rows, conflicting readings and unsupported labels always trigger review regardless of score. Missing confidence displays as unavailable. Reference intervals may be confirmed absent only when the user has checked the source.

Allow manual correction and addition while the source is visible, requiring a selected page and source location plus an explicit user-entered label. Do not offer free-standing home-reading entry in this release. The user must confirm every included test/value/unit/reference field and context; there is no bulk action that substitutes for review. Exclusions require a reason, remain visible in the summary, and affect coverage. Re-enter a corrected value independently when a decimal or row-association flag is present. Confirmation still cannot prove the source itself is correct.

**Status:** Review workflow selected; calibration and usability must be measured in Phase 3.

## Q12

**Upload and review limits.** Start with one JPEG, PNG, HEIC or PDF file per report, at most 20 MiB, five pages and ten supported or ambiguous candidate observations. Validate actual file content. Refuse encrypted PDFs, embedded attachments and corrupt decodes. An animated or multi-image image container requires selection of one still image; it must not silently discard frames.

Limit decoded images to 20 megapixels per page and 60 megapixels per report. Process pages sequentially; sandbox decoders with memory/time limits and no network. Render PDFs at up to 300 dpi within these limits. Preview rotations and any necessary resize before submission; if text becomes unreadable, ask for a clearer source. Final decoder dependencies and their licenses must be verified in Phase 2.

One report contains one person and one collection episode. Multiple test panels within that episode are permitted within the limits; unresolved duplicates and mixed people block confirmation. Never silently drop excess supported rows: explain the limit and ask for separate source files/panels or clinician review. A report exceeding the limit cannot produce an incomplete clinician sheet.

Allow one active OCR job per session/account. Before confirmation, edits create a new revision and invalidate affected confirmations. After confirmation, correcting values creates a superseding revision; if sources were deleted, require re-upload and review again. Preserve old saved snapshots and mark them superseded rather than rewriting them.

**Status:** Initial limits selected; validate them against real Ghanaian reports and typical phones.

## Q13

**Service targets.** For a small pilot, target 95% of single-page OCR jobs ready for review within 30 seconds and supported five-page jobs within 90 seconds after upload completes. These targets include queue time and are not measured results. Test ordinary mid-range Android phones on a simulated 1 Mbps upload, 5 Mbps download and 150 ms network delay; show upload progress independently.

Start with two OCR workers and a bounded queue of ten waiting jobs, with no more than ten simultaneous guest sessions holding payloads. Reserve guest capacity before accepting a file. Queue wait expires after 60 seconds; a processing attempt has a 120-second ceiling. Allow one automatic retry only for a transient infrastructure error within a five-minute overall budget. Decode/content errors require user action. Cancellation revokes access immediately and must stop processing within ten seconds; cleanup follows Q09.

Use 99.5% monthly availability as the pilot objective, a four-hour recovery-time target and a 15-minute recovery-point target for saved account data. Guest sessions intentionally have no recovery guarantee. The named operations owner handles redacted alerts. Start at five new OCR reports per hour and 20 per day per account/session, with generous shared-IP ceilings and progressive throttling. Idempotent retries do not consume another report allowance. These are abuse controls, not a paid quota or clinical restriction.

**Status:** Targets selected; load tests and the hosting budget must substantiate them before pilot launch.

## Q14

**Infrastructure and offline behavior.** Use local containers and synthetic fixtures during development. For the first hosted pilot, use AWS Africa (Cape Town), `af-south-1`, as the deployment candidate: containerized web/API and OCR workers on EC2, managed RDS PostgreSQL, private S3 storage, KMS-managed encryption and SES for account email. Keep the application on one origin. Start without Kubernetes or public health-data CDNs. [RDS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RegionsAndAvailabilityZones.html) and [SES](https://docs.aws.amazon.com/general/latest/gr/ses.html) document Cape Town availability. Select exact instance sizes from Phase 2 benchmarks and a current cost estimate.

Use RQ behind the OCR job interface with private Redis. Disable Redis persistence, snapshots and payload-bearing results; reconstruct account job state from PostgreSQL after a restart. Guest report bytes and extracted values live in a separate bounded memory service, accessed by short-lived internal capabilities, never in queue arguments. All worker transport is authenticated and encrypted. [RQ](https://python-rq.org/docs/) supplies the queue mechanism; [Redis documentation](https://redis.io/docs/latest/management/persistence/) describes persistence controls. Guest jobs lost on restart fail clearly and require a new upload.

The memory-only promise must cover reverse-proxy buffering, multipart parsing, temporary files, OCR/PDF tools, swap, core dumps, logs and backups. Use bounded RAM-backed temporary storage with swap and core dumps disabled; never fall back to disk when memory is full. Candidates and raw OCR for account review also stay outside backed-up database tables. Persist only deliberately saved reviewed snapshots and approved retained originals; account work in progress may use an encrypted temporary store with Q09 expiry and no backups.

Use TLS, encrypted database/storage/backups, least-privilege service roles, separate secrets, private database access and no public bucket permissions. Temporary-source and retained-source buckets have separate policies; do not leave noncurrent object versions behind after deletion. Do not enable cross-region replication by default. Offshore processing, support access and processor terms require Q15 review; regional deployment alone does not establish legal compliance.

Offline use is limited to already loaded content in active page memory. Cache only public static assets. No health data, tokens or report URLs in persistent browser storage or service-worker caches. Show a privacy screen after session expiry and clear loaded health data on logout.

**Status:** Architecture selected for development; cost, operational sizing and cross-border review precede hosted health-data processing.

## Q15

**Data protection and regulatory responsibility.** The legal entity operating the app should be the data controller; the project owner must identify it and appoint an accountable privacy contact before real reports are processed. Obtain appropriate Data Protection Commission registration, complete a data-protection impact assessment, document purpose-specific consent and processor agreements, and publish accessible notices. These responsibilities follow the DPC's [compliance guidance](https://dpc.gov.gh/compliance/); the exact legal basis and sensitive-data conditions require Ghana-qualified advice.

Use separate affirmative choices for processing and keeping originals. Do not condition core use on research, advertising or model training, and do not use reports for those purposes in this release. For caregiver assistance, the adult report subject must be able to give informed permission and participate in consent. Independent proxy accounts for people unable to consent are outside the first-release workflow.

Document overseas hosting and provider/subprocessor access, rights requests, identity checks, deletion and incident response. Use an internal one-business-day target to acknowledge privacy requests and a 30-day completion target unless applicable law requires sooner. A suspected breach alerts the privacy owner immediately; statutory reporting recipients and timing must be confirmed, not borrowed from another country's law.

Commission a documented Ghana FDA assessment of the intended screening and interpretation functions. FDA Ghana publishes [software-as-medical-device guidance](https://fdaghana.gov.gh/wp-content/uploads/2024/09/GUIDELINE-FOR-REGISTRATION-OF-SOFTWARE-AS-MEDICAL-DEVICE.pdf) covering medically intended software, including screening functions. It is a reasonable inference that this app needs assessment; this document does not determine its regulatory class or assert exemption. Obtain any required authorization before the applicable patient-facing pilot or release.

**Status:** Governance approach selected; named controller, privacy review, registrations and regulatory assessment are external launch requirements.

## Q16

**Guidance and food review.** Use a physician-reviewed lifestyle library and a dietitian-reviewed Ghanaian food library. Every item needs a source, reviewer, approval date and content version. Cover all foods and lifestyle topics listed in `AGENTS.md`; descriptions must include preparation, household measure and a reviewed portion reference. Do not infer nutrient content or portions from a food name alone.

Offer seven days with breakfast, lunch and an evening meal, built from a fixed approved template and reviewed substitutions. Prefer familiar, affordable foods. Ask about allergies, foods avoided and vegetarian preference; preserve the same portion logic when swapping foods. If a restriction cannot be safely satisfied by the reviewed library, withhold the sample plan and direct the user to a dietitian. Do not claim the plan is safe for every allergy or coexisting condition.

Do not calculate individualized energy targets, weight-loss prescriptions or condition-specific diets in the first release. General portions, hydration, activity and follow-up text must come from reviewed content; avoid universal fluid targets or instructions that ignore restrictions. Urgent and excluded outcomes receive the appropriate referral content rather than routine personalized plans. Follow-up timing is selected by approved rules and content, with the clinical lead responsible for its exact wording.

**Status:** Content structure and personalization limits selected; actual guidance, portions and follow-up schedules need named reviewers.

## Q17

**Account security.** Use email/password accounts with verification, and AWS SES in Cape Town for generic verification and recovery messages. Do not email reports, results or health details. Configure the sender domain and authentication records before delivery tests. Verification links expire after 24 hours; reset links after 15 minutes. Tokens are random, single-use and stored only as hashes. Remove abandoned unverified accounts after seven days. Local development uses a test email sink.

Require 15-128 characters, allow passphrases, spaces, Unicode, paste and password managers, reject commonly compromised passwords, and avoid composition rules or scheduled password changes. This follows the direction of [NIST SP 800-63B-4](https://pages.nist.gov/800-63-4/sp800-63b.html). Store salted Argon2id hashes, initially at least 19 MiB memory, two iterations and one parallel lane, then benchmark and increase where practical; these minima come from [OWASP password-storage guidance](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html).

Use opaque server-side sessions in Secure, HttpOnly, SameSite=Lax cookies, with host-only scope and no tokens in localStorage, sessionStorage or IndexedDB. Rotate identifiers at login and reauthentication. Require a CSRF token and origin checks for state-changing requests; SameSite alone is insufficient. Use a 30-minute idle timeout, a 12-hour maximum session and reauthentication within five minutes for account deletion. Warn before timeout and preserve saved work through reauthentication. [OWASP session guidance](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html) and [CSRF guidance](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html) inform this design.

Use generic account-existence responses. Start with five failed login attempts per account per 15 minutes, progressive delays and an IP ceiling that accommodates shared networks; avoid permanent lockout. Limit verification/reset requests to three per hour per address and enforce an IP ceiling. Reset and deletion revoke all sessions. A deletion receipt grants only redacted progress access for up to 35 days. Unverified users may use a separate guest session but cannot persist reports. Operator access requires MFA even though consumer MFA is deferred.

**Status:** Selected; threat-model, rate-limit, email and session tests belong to later phases.

## Q18

**Ownership and history.** Use one consenting adult report subject per account. A caregiver may assist that person in their own account with permission; do not mix family members in one history or provide independent caregiver delegation in this release. Include a ReportSubject entity from the start, constrained to one per account, so future authorized profiles need not change report ownership semantics. A display name is optional; do not require national identifiers.

Saving is explicit. Save the confirmed snapshot, including a non-classification outcome where applicable, with rules/content versions and context. Do not persist guest work or silently save an account upload to history. Warn about duplicate files within the same account using scoped comparison; do not expose cross-account matching. Retain distinct repeat results and never average them automatically.

Use confirmed collection dates; unknown dates appear in a separate undated list and do not enter time-series charts. Split series by test, source unit and relevant test context. Superseded snapshots remain inspectable but are excluded from the default trend. New threshold/content releases do not rewrite history; a deliberate reassessment creates a new versioned result and rechecks required context.

**Status:** Selected; multi-person caregiver accounts and delegated access are deferred.

## Q19

**Exports.** Use A4 portrait. The full PDF contains every included and excluded supported observation, reference interval, confirmed context, interpretation or reason for non-classification, urgent notices, approved guidance, collection date and rules/content provenance. The clinician sheet is exactly one page with up to ten observations, values, source units, lab reference intervals, status/reason, urgent/context flags, changes made during review and a brief limitations statement. The weekly meal plan belongs in the full PDF.

Use an optional user-entered display name and opaque report identifier, with no email, date of birth or original filename by default. Dates use an unambiguous day-month-name-year format; timestamps identify Africa/Accra. Preserve source units and meaningful decimal precision. Include source references and approval/version details. Exclude original images from both PDFs in this release.

Use embedded fonts, selectable text, semantic reading order and tagged output where the chosen renderer supports it; provide an equivalent accessible HTML summary. Target PDF text of at least 10.5 pt, with 12 pt body text where space permits. Test the ten-observation worst case with long labels and all notices. If it cannot fit without omitting information or reducing readability, block that export, offer the full summary and fix the template. Do not label a multi-page fallback as a one-page sheet. Serve private downloads through the owned API, not public share links; apply Q09's 15-minute expiry.

**Status:** Selected; page fit and accessibility require actual render-and-verify checks in Phase 6.

## Q20

**Visual and accessibility baseline.** Use self-hosted Source Sans 3 for the interface and Source Code Pro for values, at weights 400 and 600 only. Use sizes 14, 16, 20, 24 and 32 CSS px, implemented as rem tokens; body text and inputs start at 16 px. Keep font licenses with the assets. Adobe publishes [Source Sans 3](https://github.com/adobe-fonts/source-sans) and [Source Code](https://fonts.adobe.com/fonts/source-code-pro) as open-source families. Use one line-icon family, Lucide, at a fixed 2 px stroke with visible labels for primary navigation.

Use spacing tokens of 4, 8, 12, 16, 24, 32 and 48 px; radii 0, 4 and 6 px; solid borders and no shadows or gradients. Follow the system theme initially with a manual preference. A 1024 px breakpoint switches the bottom tabs to the left rail. Both use Report, History and Account. Keep source and fields side by side on desktop and stacked on phones.

| Semantic token              | Light     | Dark      |
| --------------------------- | --------- | --------- |
| Background                  | `#F7F8F5` | `#101A17` |
| Surface                     | `#FFFFFF` | `#182520` |
| Primary text                | `#1D2B28` | `#EDF4EE` |
| Secondary text              | `#53645E` | `#AABCB2` |
| Control boundary            | `#74867E` | `#718B7D` |
| Accent and focus            | `#155E55` | `#83C8BA` |
| Text on accent              | `#FFFFFF` | `#101A17` |
| High/low result text        | `#A1262F` | `#FFB4AB` |
| High/low result surface     | `#FFF0EF` | `#3C1F20` |
| Intermediate result text    | `#805000` | `#F5CD77` |
| Intermediate result surface | `#FFF4D9` | `#332B17` |

Reserve red and amber for clinical result status. Use neutral text, an icon and a visible border for validation errors and destructive controls. Normal ranges use neutral labels. Confidence is labelled Needs checking with a neutral marker, not an amber result badge. Flat range bars and trends have visible values and text/table equivalents.

The proposed text pairs pass 4.5:1 and control boundaries pass 3:1 in computed contrast checks; actual focus, hover, disabled and rendered states still need testing. Use 44 by 44 CSS px touch targets as the product standard. WCAG 2.2 AA's target-size minimum is 24 by 24 CSS px with exceptions; the larger product choice is intentional. Test keyboard operation, visible unobscured focus, 200% text enlargement, 320 CSS px reflow, reduced motion and password-manager support against [WCAG 2.2](https://www.w3.org/TR/WCAG22/).

Cover current and previous major Chrome/Android and Safari/iOS releases, plus desktop Chrome, Edge and Firefox at implementation time. Run Chromium, Firefox and WebKit automation; manually test Android TalkBack, iPhone VoiceOver and Windows NVDA, including a real mid-range Android phone. Browser emulation alone is insufficient for camera/HEIC validation.

**Status:** Tokens and acceptance baseline selected; no interface has been implemented or audited yet.

## Q21

**Language and copy governance.** Use plain Ghanaian English, short sentences and roughly a primary-six reading level, confirmed by usability testing rather than a readability score alone. Introduce the everyday term first, followed by the lab term; explain a screening range without declaring a diagnosis. The clinical lead approves clinical meaning, the dietitian food wording, and a Ghanaian editor/patient reviewer checks clarity and cultural fit.

Use one shared English UI/server/export message catalog at `content/locales/en-GH.json`. The web build consumes it; the API returns stable message keys and structured parameters; the exporter resolves the same keys. Approved guidance lives in locale-specific versioned content under `content/guidance`, and foods under `content/foods`, linked by stable identifiers. Translation keys must cover errors, emails, PDF labels and accessibility text as well as visible screens. Do not concatenate sentences or freely generate translations at runtime.

A later Twi release needs a professional Twi translator, independent language review, clinical back-checking and testing with intended users. Select the intended Twi variety with those reviewers at that phase. Do not ship machine-translated clinical content without review.

**Status:** English structure selected; named reviewers and future Twi variety remain external/later-phase work.

## Q22

**Engineering checks.** Use Prettier as the single JavaScript/TypeScript formatter and ESLint with TypeScript and React rules as the single linter. Use Ruff for both Python linting and formatting; do not add competing formatters. Type-check with TypeScript strict mode and mypy for Python. Enforce checks in GitHub Actions using pinned dependencies and reproducible lockfiles. The tools' roles are documented by [Prettier](https://prettier.io/docs/), [ESLint](https://eslint.org/docs/latest/use/) and [Ruff](https://docs.astral.sh/ruff/formatter/).

Keep the original exit checks in each phase prompt and add checks relevant to that phase:

| Phase             | Required additional evidence                                                                                                                                                             |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1: Foundation     | App boots; lint, format, type and tests pass; migrations work against an empty test database; no-gradient check; light/dark token contrast and keyboard navigation smoke checks.         |
| 2: Ingestion/OCR  | All four formats, decoder limits, failure/cancel/retry, memory-only guest path, no sensitive logs and transient cleanup; de-identified evaluation report with honest dataset coverage.   |
| 3: Review         | Every-field confirmation, context checks, manual corrections, duplicates, confidence flags, revision conflicts, mixed subjects, offline recovery and inaccessible-state prevention.      |
| 4: Interpretation | Config-derived boundaries, precision gaps, exclusions, missing context, random-only constraints, aggregation/urgent precedence, draft-config rejection and clinical approval gate.       |
| 5: Guidance       | Approved-only content selection, every required topic/food, allergy/restriction handling and reproducible meal selection.                                                                |
| 6: History/export | Ownership isolation, explicit save, scoped trends, superseding revisions, rule provenance and visual PDF verification including one-page worst cases.                                    |
| 7: Hardening      | Authentication/CSRF/rate limits, retention/deletion/backup-restore drills, accessibility audit, performance targets, sensitive-data leakage and dependency/security checks.              |
| 8: Release        | All original release checks, deployment smoke tests, rollback/restore evidence, named operations ownership, measured acceptance and completed clinical/privacy/regulatory prerequisites. |

Use pytest, Vitest and Playwright as specified. Add a simple domain-specific content scan for forbidden wording and missing translation keys, backed by human review. Numerical clinical thresholds appear only in the configuration; tests load boundary values from it and independently assert expected behavior. Clinical reviewers own scenario correctness, the data steward owns fixtures, and the engineering maintainer owns reproducible checks. Use synthetic data in public CI and keep authorized sensitive evaluation artifacts out of repositories and build logs. Do not introduce arbitrary coverage percentages in place of required scenarios.

**Status:** Tooling and phase checks selected. Current implementation progress is recorded in `docs/phase-log.md`.

## Remaining launch questions

These are the remaining external facts and approvals, not unanswered default design choices. Local work with synthetic data can proceed when its phase is requested.

1. Who are the named Ghana-registered clinical lead, dietitian and English patient-copy reviewer, and when will they approve the recommended clinical and content policies (Q01-Q07, Q16, Q21)?
2. Which legal entity is the controller, who is the privacy contact, and what documented registration, sensitive-data basis, caregiver-consent, overseas-processing and retention conclusions apply (Q09, Q15)?
3. What Ghana FDA assessment, classification and authorization, if any, are required for the intended pilot and public release (Q15)?
4. Which laboratory partners and data steward will provide authorized evaluation reports and independently checked annotations (Q10)?
5. What hosting budget, sender domain and named engineering/operations owner are available for the proposed deployment, and do benchmarks justify its sizing (Q13, Q14, Q17, Q22)?
6. Do measured OCR, usability, accessibility, security, deletion and PDF results meet these selected targets before release (Q10-Q13, Q19-Q22)?
7. At the later Twi phase, which Twi variety and qualified reviewers should the project use (Q21)?
