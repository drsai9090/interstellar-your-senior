# Interstellar — Your Senior

This repository extends Your Senior as an evidence-backed document assistant. Preserve upstream attribution and the existing React/JSX, Python/FastAPI and ChromaDB architecture. Prefer existing dependencies and small tested changes.

## Scope

- Work only in this repository. Do not modify adjacent repositories or read unrelated CV/credential files in parent directories.
- Use synthetic or openly licensed documents with provenance. No employer code, prompts, datasets, client information or branding.
- Read the complete relevant request/query/ingestion paths and all callers before changing shared behaviour.
- Validate model responses and citation identifiers. Never present model self-confidence as measured accuracy.
- Browser-delivered shared API keys are not an authentication boundary. Privileged ingestion must be server protected; provider secrets remain server-side.
- Public demos must be bounded, explicitly synthetic and safe when model credentials are absent. Clearly distinguish recorded fixtures from live responses.

## Delivery

- Work on short, descriptive feature branches in this fork. Do not push or open PRs against the upstream repository without an explicit user request.
- Add runnable checks for changed logic, including errors and access boundaries. Run the existing frontend build when changing it.
- Establish a small labelled evaluation baseline before promising quality improvements. Record corpus, model, prompt, configuration and actual results.
- Keep commits and PRs focused. Stage explicit paths; inspect staged content for secrets and unrelated files.
- Use only already authorised credentials through their normal tools. Never print tokens or copy credential files into this repository.
- Prepare Azure deployment as code and validate a local demonstration first. Do not provision paid resources without a concrete cost ceiling confirmed by the user. Do not treat missing hosted CI or model access as a passed check.

## First milestone

Make one document-query path reproducible and tested; harden output/citation validation and public-demo access; add a small synthetic evaluation baseline and clear local demo instructions. Subsequent work adds review and operational evidence. A complete multi-tenant platform is not the first increment.
