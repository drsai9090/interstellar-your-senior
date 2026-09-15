# Contributing to Interstellar

Follow [AGENTS.md](AGENTS.md). This fork is a personal synthetic-data prototype and retains upstream attribution and the existing React/JSX, FastAPI and Chroma stack.

Use the safe no-credential setup in [README.md](README.md). Run the offline unittest suite, labelled synthetic evaluation and frontend build before opening a focused PR. Include the actual command results and any unverified behaviour; do not call stub output live AI or measured accuracy.

Keep all provider/operator keys server-side. Public demo ingestion remains disabled. New parser or storage changes must preserve the previous working index on preparation/write failures and include a focused regression check.

Open PRs against this fork. Do not write to the upstream repository. Include only synthetic/openly licensed documents with provenance; never include employer source, client information, credentials or adjacent workspace files.
