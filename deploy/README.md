# Synthetic demo packaging

The root Dockerfile builds React and serves it from FastAPI on port 8000. The demo uses checked-in synthetic documents, an in-memory Chroma collection recreated at startup, and a deterministic provider stub. It does not call a live model. There are no uploads, provider keys, admin keys or persistent client documents in this deployment.

## Local container

From the repository root, with Docker running:

```sh
docker compose config --quiet
docker compose up --build
```

Open <http://localhost:8000>. The compose binding only exposes the service on the local machine. Run the sample question and unsupported-question flows, confirm the fixture label and citations, then restart and check that only the fixed corpus remains. `docker compose down` stops and removes the demo container; there is no demo data volume.

The separate `backend/Dockerfile` retains the upstream full dependency path for private development. Use the root Dockerfile for this public demo. Never inject credentials into a frontend build.

## Azure: prepared, not deployed

`azure/main.bicep` creates one Container App in an **existing authorised Consumption environment**, using a **publicly pullable image**. It creates no environment, registry, storage account or identity. The image must be the checked and published root Dockerfile build, preferably an immutable digest. No image has been published by these instructions.

The app has HTTPS ingress, startup/readiness probes, 0–1 replicas, 0.5 vCPU and 1 GiB per replica. These resource limits are **not a monetary spending cap**. The environment, request traffic, logs and other existing services may still incur charges. Obtain a concrete approved cost ceiling and confirm the existing environment before provisioning. There is no deployment workflow or automatic cloud write in CI.

After local checks, compile without provisioning:

```sh
az bicep build --file deploy/azure/main.bicep --stdout
```

Before a separately authorised deployment, review a what-if using the approved subscription context, existing resource group, matching location, existing environment ID and published image digest:

```sh
az deployment group what-if --resource-group <existing-resource-group> --template-file deploy/azure/main.bicep --parameters environmentId=<existing-environment-resource-id> location=<environment-location> containerImage=<public-image-at-digest>
```

A deployed instance must pass the same sample, unsupported-answer and denied-ingestion checks. Cold starts rebuild only the synthetic corpus; this design is not durable storage or tenant isolation. Add verified persistent storage and user identity controls before any private document use.

Reference: [Microsoft Container Apps Bicep schema, API 2025-01-01](https://learn.microsoft.com/en-us/azure/templates/microsoft.app/2025-01-01/containerapps).

## Verification status

- Docker CLI is installed; the Docker Desktop Linux daemon was unavailable (`dockerDesktopLinuxEngine` pipe missing), so image build/runtime checks were not run locally.
- Azure CLI and Bicep CLI were not installed, so Bicep compilation and Azure validation were not run locally. The template was checked against the Microsoft schema; this is not a successful deployment.
- GitHub Actions configuration runs backend checks, the labelled evaluation and the frontend build without model credentials. Workflow presence alone is not evidence that a hosted run passed.
