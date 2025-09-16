## Fix Plan for AI Research Buddy

This plan addresses the issues identified during the review and organizes them into prioritized, actionable steps. Each task lists target files, concrete actions, and acceptance criteria.

### Phase 1 — Parsing and Security Hardening (High Priority)
1) Harden JSON extraction and parsing
   - Files: `main.py`
   - Actions:
     - Replace the simple `re.search(r'\{.*?\}', ...)` with a brace-balanced JSON extractor that selects the largest valid JSON object, preferring content near the end of the response; also support ```json fenced blocks.
     - Attempt JSON cleanup (dangling commas, unescaped quotes) only when strict parsing fails.
     - Log/print a short diagnostic if parsing fails (length and first/last 500 chars of output).
   - Acceptance: Robustly parse valid full responses from both OpenAI and Gemini; no truncation of nested objects.

2) Prefer structured output when available
   - Files: `main.py`
   - Actions:
     - Where supported, use LangChain providers’ structured output helpers (e.g., `with_structured_output(ResearchResponse)` or `PydanticTools`) to reduce parsing failures.
     - Fallback to improved JSON extraction if provider lacks native structured output.
   - Acceptance: For supported providers, parser step is bypassed or becomes trivial; fewer parse failures in logs.

3) Secure report rendering
   - Files: `app.py`
   - Actions:
     - Render the user/LLM-generated markdown preview with `unsafe_allow_html=False` to avoid HTML execution in content sections.
     - Keep custom CSS and UI elements outside the report content area.
   - Acceptance: No raw HTML from the report is executed; visual output remains correct as markdown.

4) Developer diagnostics on parse errors
   - Files: `app.py`, `config.py`
   - Actions:
     - Add `UI_CONFIG["SHOW_DEBUG"] = False`.
     - On parse failure, if `SHOW_DEBUG` is true, show an `st.expander` with the first/last 2000 chars of the raw output for debugging.
   - Acceptance: When enabled, developers can quickly inspect model output that failed parsing.

### Phase 2 — Configuration Alignment and Consistency (High)
5) Source example topics from config
   - Files: `app.py`, `config.py`
   - Actions:
     - Replace hardcoded `example_topics` in `app.py` with `EXAMPLE_TOPICS` from `config.py`.
   - Acceptance: UI example buttons reflect `EXAMPLE_TOPICS` without duplication.

6) Wire `API_CONFIG` into LLM setup
   - Files: `main.py`, `config.py`, `app.py`
   - Actions:
     - In `set_llm`, read `API_CONFIG` for default model names and temperature.
     - Centralize UI model-choice → internal identifier mapping in one dictionary and reference it from both UI and backend.
   - Acceptance: Model selection honors config; temperature and defaults are applied consistently.

7) Align documentation with actual support
   - Files: `README.md`
   - Actions:
     - Update supported models and CLI usage strings to match code (e.g., `gemini-1.5-flash`, `gemini-2.0-flash`, `gemini-2.0-flash-lite`, `openai`).
     - Optionally document alias mapping (e.g., `google_genai` → `gemini-1.5-flash`) if implemented.
   - Acceptance: README instructions work as written.

### Phase 3 — Rate Limiting and UX (Medium)
8) Improve cooldown visibility in main area
   - Files: `app.py`
   - Actions:
     - When button is disabled due to limits, show a clear in-page message with countdown (minutes:seconds) mirroring the sidebar.
   - Acceptance: Users see why the button is disabled and time remaining.

9) Refine decrement behavior (optional)
   - Files: `app.py`
   - Actions:
     - Keep decrement-on-start (prevents double-submits), but refund on hard, immediate failures (e.g., LLM/network exceptions before any output) by incrementing `requests_remaining` in `except`.
   - Acceptance: Transient failures don’t permanently consume a request; no concurrency race reintroduced.

### Phase 4 — Tools and Dependencies (Medium)
10) Finalize image verification tool usage
   - Files: `tools.py`, `main.py`
   - Actions:
     - Either: add `verify_image_tool` to `TOOLS` and mention in the system prompt when images are referenced, or remove from code if not planned.
   - Acceptance: Tool list and prompt are consistent; no dead code.

<!-- 11) Trim or comment optional dependencies — removed per decision to keep deps for future features -->

### Phase 5 — Consistency and Sanitization (Medium)
12) Unify filename sanitization
   - Files: `app.py`, `tools.py`
   - Actions:
     - Import and reuse `sanitize_topic_for_filename` in `app.py` download filename generation to match saved files.
   - Acceptance: Downloaded and auto-saved filenames follow the same rules.

13) Standardize model aliases
   - Files: `main.py`, `app.py`
   - Actions:
     - Accept friendly aliases (`google_genai`) in CLI and map to supported Gemini model; centralize mapping dict.
   - Acceptance: CLI and UI accept documented names; mapping is defined in one place.

### Phase 6 — Optional Enhancements (Future)
14) Markdown fallback parser and chunked parsing
   - Files: `main.py` (utilities)
   - Actions:
     - Implement markdown-to-structured fallback per `scope.md` and chunked parsing for very large outputs.
   - Acceptance: Oversized responses from larger models succeed via fallback.

15) Basic tests and smoke checks
   - Files: `tests/` (new)
   - Actions:
     - Add minimal tests that mock LLM outputs to validate parsing pipeline and filename sanitization.
   - Acceptance: CI runs green; regressions caught early.

---

## Implementation Order Checklist
- [x] 1 Harden JSON extraction
- [x] 2 Prefer structured output where available
  - Implemented for OpenAI and Gemini (second-pass normalization)
- [x] 3 Secure report rendering (no unsafe HTML in content)
- [x] 4 Add developer diagnostics toggle
- [x] 5 Use `EXAMPLE_TOPICS` from config
- [x] 6 Wire `API_CONFIG` into `set_llm` and centralize mapping
- [x] 7 Update README model list and CLI examples
- [x] 8 Improve cooldown message in main area
- [x] 9 Refund on early hard failures (optional)
- [x] 12 Reuse `sanitize_topic_for_filename` in `app.py`
- [x] 13 Standardize model aliases (CLI/UI)
- [x] 14 Add markdown fallback + chunking (future)
- [x] 15 Add basic tests (future)

### Additional Completed Items
- [x] PDF export with WeasyPrint first and ReportLab fallback
- [x] PDF formatting polish (headings, bullets, nested bullets, inline bold/italic)
- [x] Refactor: `pdf_export.py` extracted and imported by `app.py`

---

## Rollback Plan
- Changes are mostly localized. Commit per phase with clear messages.
- If parsing changes cause issues, revert to previous `generate_report` and re-enable improved diagnostics only.
- If UI security change breaks formatting, temporarily gate it behind a config flag while fixing rendering.


