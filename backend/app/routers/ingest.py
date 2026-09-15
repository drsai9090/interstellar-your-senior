"""Ingestion API: Drive sync, file upload, and raw-text ingestion endpoints."""

import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile

from app.config import get_settings
from app.ingestion.parsers.base import ParsedDocument
from app.models.schemas import (
    IngestRequest,
    IngestResponse,
    IngestStatus,
    TextIngestRequest,
    UploadIngestResponse,
)
from app.ingestion.storage import replace_document_chunks

router = APIRouter(prefix="/ingest", tags=["Ingestion"])

_SUPPORTED_EXTENSIONS = {
    ".pdf":  "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".txt":  "text/plain",
}

_MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB


# ─── Google Drive ingestion ───────────────────────────────────────────────────

@router.post("/drive", response_model=IngestResponse)
async def ingest_from_drive(request: IngestRequest, background_tasks: BackgroundTasks):
    """Start a background job that pulls files from Google Drive and indexes them."""
    from app.ingestion.pipeline import run_ingestion_job
    job_id = str(uuid.uuid4())
    background_tasks.add_task(run_ingestion_job, job_id, request.folder_id)
    return IngestResponse(
        job_id=job_id,
        status=IngestStatus.PENDING,
        message=f"Ingestion started. Poll /ingest/status/{job_id} for progress.",
    )


@router.get("/status/{job_id}", response_model=IngestResponse)
async def ingestion_status(job_id: str):
    """Check the status of a running or completed ingestion job."""
    from app.ingestion.pipeline import get_job_status
    job = get_job_status(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")

    return IngestResponse(
        job_id=job_id,
        status=IngestStatus(job["status"]),
        message=job.get("error", ""),
        documents_found=job.get("documents_found"),
        chunks_created=job.get("chunks_created"),
    )


# ─── Local file upload ingestion ─────────────────────────────────────────────

@router.post("/upload", response_model=UploadIngestResponse)
async def upload_and_ingest(file: UploadFile = File(...)):
    """
    Upload a PDF, DOCX, or TXT file and ingest it immediately.
    Re-uploading the same filename replaces its previous chunks.
    """
    from app.ingestion.chunker import chunk_document
    from app.ingestion.registry import get_parser
    filename = file.filename or "uploaded_file"
    ext = Path(filename).suffix.lower()

    if ext not in _SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type '{ext}'. "
                f"Accepted: {', '.join(_SUPPORTED_EXTENSIONS)}"
            ),
        )

    mime_type = _SUPPORTED_EXTENSIONS[ext]
    parser = get_parser(filename, mime_type)
    if not parser:
        raise HTTPException(status_code=400, detail=f"No parser registered for '{ext}'.")

    content = await file.read(_MAX_UPLOAD_BYTES + 1)

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(content) > _MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds the 50 MB upload limit ({len(content) // (1024 * 1024)} MB received).",
        )

    try:
        parsed = await parser.parse(content, filename)
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail="Could not parse the uploaded document.",
        )

    if not parsed.paragraphs:
        return UploadIngestResponse(
            filename=filename,
            chunks_created=0,
            status="completed",
            message="File parsed but contained no readable text.",
        )

    settings = get_settings()
    # Stable doc_id from filename — re-uploading replaces chunks cleanly.
    doc_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"upload:{filename}"))
    chunks = chunk_document(parsed, doc_id, settings.max_chunk_tokens, settings.chunk_overlap_tokens)

    if not chunks:
        return UploadIngestResponse(
            filename=filename,
            chunks_created=0,
            status="completed",
            message="Document produced no chunks after splitting.",
        )

    await replace_document_chunks(chunks)

    return UploadIngestResponse(
        filename=filename,
        chunks_created=len(chunks),
        status="completed",
        message=f"Successfully ingested {len(chunks)} chunks from '{filename}'.",
    )


# ─── Raw text ingestion ───────────────────────────────────────────────────────

@router.post("/text", response_model=UploadIngestResponse)
async def ingest_raw_text(request: TextIngestRequest):
    """
    Ingest raw text as JSON — no file upload needed.
    Re-posting with the same filename replaces its previous chunks.
    """
    from app.ingestion.chunker import chunk_document
    paragraphs = [p.strip() for p in request.text.split("\n\n") if p.strip()]
    if not paragraphs:
        return UploadIngestResponse(
            filename=request.filename,
            chunks_created=0,
            status="completed",
            message="Text contained no non-empty paragraphs after splitting.",
        )

    parsed = ParsedDocument(
        raw_text=request.text,
        paragraphs=paragraphs,
        metadata={
            "filename": request.filename,
            "source_type": "txt",
            "page_count": None,
            "author": None,
            "file_size_bytes": len(request.text.encode()),
        },
    )

    settings = get_settings()
    doc_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"text:{request.filename}"))
    chunks = chunk_document(parsed, doc_id, settings.max_chunk_tokens, settings.chunk_overlap_tokens)

    if not chunks:
        return UploadIngestResponse(
            filename=request.filename,
            chunks_created=0,
            status="completed",
            message="Text produced no chunks after splitting.",
        )

    await replace_document_chunks(chunks)

    return UploadIngestResponse(
        filename=request.filename,
        chunks_created=len(chunks),
        status="completed",
        message=f"Successfully ingested {len(chunks)} chunks from '{request.filename}'.",
    )
