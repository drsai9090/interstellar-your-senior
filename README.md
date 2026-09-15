# Interstellar — Your Senior

An evidence-backed document assistant prototype, extending [Your Senior](https://github.com/Saisugun9090/YOUR-SENIOR-) under its [MIT license](LICENSE).

**The default demo uses three synthetic documents and an author-written provider stub. It is not live AI, a recorded model response, or a real company knowledge base.** The five sample questions show supported, partial and unsupported answers. Other questions, including paraphrases, abstain. No employer or client information is included.

## Try it locally

Python 3.12 and Node.js 22 are the tested runtime targets. From the repository root on Windows:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r backend/requirements-demo.txt
cd frontend
npm.cmd ci
npm.cmd run build
cd ..
$env:DEMO_MODE = 'true'
$env:STATIC_DIR = (Resolve-Path frontend/dist).Path
.venv/Scripts/python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

Open [the demo](http://localhost:8000). No `.env`, paid model, embedding download, Google account or cloud subscription is needed. On macOS/Linux use `.venv/bin/python` and set `DEMO_MODE=true STATIC_DIR="$PWD/frontend/dist"` for the uvicorn command.

For frontend development, run the backend on port 8000 and `npm run dev` in `frontend`; Vite proxies API requests. Browser builds contain no operator/provider key. `VITE_API_URL` is optional for an explicitly configured separate backend origin.

## What the slice does

```text
Bundled synthetic TXT → TXT parser → fixed paragraph chunks
  → deterministic hashed word vectors → memory-only Chroma
  → actual top-K retrieval → author-written provider stub
  → strict Pydantic validation + citation-ID checks → answer or abstention
```

The React/JSX UI lets visitors inspect the complete corpus and the exact cited excerpts. Results carry `response_mode: fixture`. There are no confidence percentages: source similarity and a model's self-assessment do not establish accuracy.

The output validator rejects malformed JSON, extra fields, invalid statuses, wrong types, empty answers, duplicate or unknown citation IDs and unsupported answers that claim citations. Supported/partial answers must cite retrieved IDs. Invalid provider output and provider errors return a neutral unsupported answer with no fallback sources or raw provider text. **Citation membership does not prove factual support**; live answers still need evaluated grounding and human review.

## Access and storage boundaries

- `DEMO_MODE=true` is the default. `/query`, `/demo` and health/docs are public. Every `/ingest` and `/admin` route is disabled, even with an operator key.
- The demo reads only the three checked-in TXT files. Its ephemeral Chroma collection is rebuilt at startup and never opens the configured private persistent directory. Public questions are not added to the private query log.
- Queries are limited to 2,000 characters, 16 KiB request bodies and 60 requests per minute per worker. This global budget can be exhausted by one visitor; it is not a distributed quota or monetary cap.
- For **private local development**, install `backend/requirements.txt`, set `DEMO_MODE=false`, and configure a randomly generated operator key of at least 32 characters as `YOUR_SENIOR_API_KEY`. Supply it only from an operator/CLI using `X-API-Key`. Never put it in a frontend env file or build argument. Missing/short keys disable protected routes; incorrect keys receive 401.
- Private mode keeps the existing sentence-transformer, persistent Chroma and Anthropic path. It needs server-side `ANTHROPIC_API_KEY` and may download `all-MiniLM-L6-v2`. No paid live-model call has been validated in this milestone. It is not a multi-user authentication design.
- Upload, pasted text and Drive ingestion now prepare embeddings and add replacement chunks before deleting the old chunks. A failure before successful insertion preserves the previous working set. Chroma does not provide an atomic generation switch here: interrupted insertion/deletion can leave duplicate generations. Keep ingestion single-worker and private until transactional publication and recovery are verified.

## Run the evidence checks

```powershell
cd backend
../.venv/Scripts/python.exe -m unittest discover -s tests -v
../.venv/Scripts/python.exe -m app.evaluate --output ../outputs/evaluation.json
cd ../frontend
npm.cmd run build
```

The [evaluation cases](backend/app/fixtures/evaluation-cases.json) check three supported questions, one partial answer, missing/out-of-corpus information, an injected instruction and an unsupported paraphrase. [Evaluation output](outputs/evaluation.json) records corpus/fixture/prompt hashes, dependency versions, configuration and actual per-case outcomes. These are regression checks for authored scenarios, **not a measured AI quality score**. The injection scenario exercises the stub, not live-model resistance.

[Evidence report](outputs/evidence-report.md) records actual checks and remaining gaps. GitHub Actions runs the same offline suite and build; a workflow file alone is not proof of a passing run.

## Corpus provenance

`backend/app/fixtures/northstar-*.txt` and `answers.json` were authored for this personal prototype on 15 September 2026 and are covered by this repository's MIT license. Northstar Studio, its policies and `.example` email address are fictional. The displayed ingestion date is a fixed fixture timestamp. The documents contain no real employee, employer, client or legal case data.

## Deployment and next milestone

A [single-container demo and Azure Container Apps template](deploy/README.md) are prepared. Azure provisioning needs an existing authorised environment and an approved cost ceiling. No cloud deployment is implied by local verification.

Next: run a separately labelled live-provider evaluation on held-out synthetic questions, assess answer support rather than just citation IDs, and verify atomic storage replacement and per-user identity before private document hosting.
