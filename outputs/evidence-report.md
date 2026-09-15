# Interstellar milestone 1 — evidence report

Date: 15 September 2026. Branch: `codex/interstellar-evidence` in `drsai9090/interstellar-your-senior`. The draft PR carries the exact delivered commit and hosted check status. Upstream is read-only.

## Baseline observed

- Starting commit: `b6e5e52` (project scope), following upstream `c1308a9`.
- Existing React 18 / JSX / Vite / Tailwind frontend built successfully after `npm ci`.
- Python 3.12.3 was available; baseline backend sources compiled, but Chroma, Anthropic, sentence-transformers and pydantic-settings were absent. No baseline live-query success is claimed.
- The browser bundled a shared operator key; invalid model JSON could be displayed as an answer and uncited answers inherited retrieved sources. Ingestion removed the previous chunks before embedding/insertion.

## Implemented and locally verified

- Three fictional Northstar TXT documents are parsed and indexed in memory-only Chroma. The demo does not open private persistent storage or call any paid model. Five sample questions use an author-written exact-match provider stub.
- Strict structured output and citation validation. Supported/partial answers require known retrieved IDs; invalid output, provider failures and unsupported answers expose no fallback source list or raw provider/error text. No confidence score is presented as accuracy.
- Demo `/ingest` and `/admin` routes deny requests regardless of operator credentials. Private query/admin/ingest routes fail closed without a strong server-only key. No browser key remains.
- All three private ingestion paths prepare embeddings and add new chunks before deleting the working generation. Tests cover embedding and insertion failure without old-chunk deletion. Atomic/crash-safe generation publication remains future work.
- Public UI provides exact sample questions, clear stub labels, corpus inspection, cited source excerpts, keyboard controls, loading and error states. Legacy public administration UI was removed.
- A same-origin production build runs locally at `http://127.0.0.1:8000`; health returned 200/ok and an annual-leave query returned 24 days with `northstar-leave-0`, labelled `fixture`.

## Checks

| Check | Actual result |
| --- | --- |
| `python -m unittest discover -s tests -v` (backend) | 19 passed, no skips; real Chroma retrieval plus provider/storage failure mocks |
| `python -m app.evaluate --output ../outputs/evaluation.json` | 8/8 authored scenarios passed; no live model calls |
| `node --test src/api/client.test.js` (frontend) | 1 passed, shared-secret absence and request/error handling |
| `npm run build` (frontend) | Passed, Vite 6.4.3, 30 modules |
| `npm audit --audit-level=moderate` | 0 known vulnerabilities after compatible lockfile fixes and removal of unused React Router |
| `python -m pip check` | No broken requirements |
| Backend compile / `git diff --check` / compose config | Passed |
| Backend environment example | Validates; safe demo mode and blank secrets |

Chroma 0.5's telemetry integration required its compatible PostHog 3.25.0 API; the pin removes startup/query compatibility warnings. Telemetry remains disabled. Direct runtime dependencies are pinned; transitive Python versions are not a complete cross-platform lock. `pip check` checks dependency compatibility, not security advisories.

## Evaluation meaning and provenance

See [evaluation.json](evaluation.json) for actual status/citation/content outcomes and corpus, fixture and prompt hashes. Corpus and expected answers were authored for this prototype and released under the repository MIT license. The fixed timestamp is fixture metadata. All names, policies and the `.example` email are fictional.

**8/8 is a software regression result, not AI accuracy.** The same authored scenarios define the stub behaviour; no live model, held-out quality evaluation, production adoption, retrieval benchmark or prompt-injection resistance has been demonstrated. Paraphrases deliberately abstain. A valid citation ID does not prove entailment.

## Deployment and remaining work

The root Dockerfile packages React + FastAPI with in-memory Chroma and no credentials. Azure Bicep uses an existing authorised environment, one Consumption app and 0–1 replicas. It has not been provisioned; replica limits are not a monetary cost cap.

- Docker CLI is installed but its Linux daemon is unavailable. Container image build and runtime have not been verified.
- Azure/Bicep CLI is absent. Bicep is schema-reviewed, not compiled or deployed. No cloud resources or paid commitments were created.
- GitHub Actions configuration is included; consult the draft PR for exact-commit hosted results rather than treating local tests or workflow presence as hosted success.
- Full private ingestion against persistent Chroma, Google Drive, the live Anthropic provider and sentence-transformer downloads are not end-to-end verified in this milestone.
- Single-worker query limits and add-before-delete publication are prototype controls. Verify transactional document publication, user identity/permissions, retention and storage recovery before hosting private documents.

Next milestone: a separately labelled live-provider run on held-out synthetic questions, with answer-support review, followed by atomic index publication and user identity before private document use.

## Browser verification

The built frontend was inspected through the in-app browser at `http://127.0.0.1:8000`:

- Annual leave returned the supported 24-day answer with the expected source ID and excerpt.
- The compound annual/parental question returned a partial answer with the missing entitlement stated.
- Parental leave alone returned unsupported with no citations.
- Full corpus documents expanded, and Ctrl+Enter submitted the expense question successfully.
- Explicit accessible names were added to source/document summaries after accessibility-tree inspection. Completed answers receive focus and scroll into view.
- At a 390-pixel viewport, measured document width showed no horizontal overflow. The browser tool's narrow screenshot rendering was duplicated/scaled, so narrow visual appearance is not fully verified. Desktop appearance was inspected.

## Ponytail cleanup

Removed slogans, repeated explanation panels, query-reference display and unused styles. The demo retains one concise synthetic/prewritten-answer disclosure and per-answer source status. Removed the unused Tailwind/PostCSS configuration, 64 dependency packages, the pass-through App component, an unused request model/server settings and the discarded aggregate retrieval score.

Rechecked: 19 backend tests, the frontend client test and build, 8/8 synthetic evaluation cases, zero npm audit findings and compose configuration. Browser checks verified supported/unsupported answers and document expansion; widths of 327 and 1280 pixels had no horizontal overflow.
