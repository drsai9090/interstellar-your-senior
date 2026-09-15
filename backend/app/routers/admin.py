"""Admin API: document management, query log, and system health endpoints."""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.config import get_settings
from app.db.chroma import get_collection, is_connected
from app.models.schemas import (
    ChromaDBStatus,
    ConfidenceDecayStatus,
    DeleteDocumentResponse,
    DocumentInfo,
    QueryLogEntry,
    SystemHealth,
)

router = APIRouter(prefix="/admin", tags=["Admin"])

# In-memory query log — kept bounded by QUERY_LOG_MAX_ENTRIES.
_query_log: list[dict] = []


def append_query_log(entry: dict) -> None:
    """Prepend an entry to the query log, capping the list at the configured max."""
    settings = get_settings()
    _query_log.insert(0, entry)
    del _query_log[settings.query_log_max_entries:]


# ─── Documents ────────────────────────────────────────────────────────────────

@router.get("/documents", response_model=list[DocumentInfo])
async def list_documents():
    """Return all indexed documents with metadata and chunk counts."""
    collection = get_collection()
    result = collection.get(include=["metadatas"])

    docs: dict[str, dict] = {}
    for meta in result["metadatas"]:
        doc_id = meta.get("doc_id", "unknown")
        if doc_id not in docs:
            docs[doc_id] = {**meta, "chunk_count": 0}
        docs[doc_id]["chunk_count"] += 1

    output: list[DocumentInfo] = []
    for doc_id, info in docs.items():
        raw_date = info.get("date_ingested", datetime.now(timezone.utc).isoformat())
        date_ingested = datetime.fromisoformat(raw_date)
        if date_ingested.tzinfo is None:
            date_ingested = date_ingested.replace(tzinfo=timezone.utc)

        age_days = (datetime.now(timezone.utc) - date_ingested).days
        decay = (
            ConfidenceDecayStatus.FRESH
            if age_days < 7
            else ConfidenceDecayStatus.AGING
            if age_days < 30
            else ConfidenceDecayStatus.STALE
        )

        output.append(
            DocumentInfo(
                doc_id=doc_id,
                filename=info.get("source_file", "unknown"),
                source_type=info.get("source_type", "unknown"),
                file_size_bytes=info.get("file_size_bytes"),
                chunk_count=info["chunk_count"],
                date_ingested=date_ingested,
                author=info.get("author"),
                confidence_decay_status=decay,
            )
        )

    return sorted(output, key=lambda d: d.date_ingested, reverse=True)


@router.delete("/documents/{doc_id}", response_model=DeleteDocumentResponse)
async def delete_document(doc_id: str):
    """Remove all chunks belonging to a document from ChromaDB."""
    collection = get_collection()
    existing = collection.get(where={"doc_id": doc_id})

    if not existing["ids"]:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")

    count = len(existing["ids"])
    collection.delete(ids=existing["ids"])

    return DeleteDocumentResponse(
        doc_id=doc_id,
        deleted=True,
        chunks_removed=count,
        message=f"Removed {count} chunks for document '{doc_id}'.",
    )


@router.post("/documents/{doc_id}/reindex")
async def reindex_document(doc_id: str, background_tasks: BackgroundTasks):
    """Re-run ingestion for all documents (MVP: full re-sync from Drive)."""
    from app.ingestion.pipeline import run_ingestion_job
    job_id = str(uuid.uuid4())
    background_tasks.add_task(run_ingestion_job, job_id)
    return {
        "job_id": job_id,
        "message": "Re-ingestion job started. This will re-sync all documents from Drive.",
    }


# ─── Query Log ────────────────────────────────────────────────────────────────

@router.get("/query-log", response_model=list[QueryLogEntry])
async def get_query_log():
    """Return the last N questions asked, with evidence status."""
    return [QueryLogEntry(**entry) for entry in _query_log]


# ─── System Health ────────────────────────────────────────────────────────────

@router.get("/system-health", response_model=SystemHealth)
async def system_health():
    """ChromaDB stats and overall system status for the admin dashboard."""
    settings = get_settings()
    connected = is_connected()

    total_chunks = 0
    total_documents = 0
    last_ingestion: datetime | None = None

    if connected:
        collection = get_collection()
        total_chunks = collection.count()
        all_meta = collection.get(include=["metadatas"])
        total_documents = len({m.get("doc_id") for m in all_meta["metadatas"]})

        dates = [
            datetime.fromisoformat(m["date_ingested"])
            for m in all_meta["metadatas"]
            if m.get("date_ingested")
        ]
        if dates:
            last_ingestion = max(dates)

    return SystemHealth(
        app="Your Senior",
        backend_status="ok",
        chroma=ChromaDBStatus(
            connected=connected,
            total_documents=total_documents,
            total_chunks=total_chunks,
            last_ingestion=last_ingestion,
            collection_name=settings.chroma_collection_name,
        ),
        timestamp=datetime.now(timezone.utc),
    )
