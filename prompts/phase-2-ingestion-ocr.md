Phase 2 only.

Read AGENTS.md and docs/phase-log.md. Build:

- the upload screen with drag and drop and mobile camera capture
- server-side validation of type, size and page count
- HEIC conversion
- image preprocessing with OpenCV (deskew, denoise, contrast)
- the Redis job queue
- the OCR engine behind an interface

Return raw text with word positions and per-word confidence. Run the pipeline over
tests/fixtures/reports and print a table of processing time and word count per file.

Exit check: text is extracted from every fixture in under 15 seconds per page. Update
docs/phase-log.md and stop.
