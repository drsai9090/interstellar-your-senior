"""Pydantic request and response schemas for every API endpoint."""

from datetime import datetime
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


AnswerStatus = Literal["supported", "partial", "unsupported"]


class ModelAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, str_strip_whitespace=True)
    status: AnswerStatus
    answer: str = Field(min_length=1, max_length=6000)
    reason: str = Field(min_length=1, max_length=1000)
    cited_chunk_ids: list[str] = Field(max_length=20)


# ─── Query ────────────────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, str_strip_whitespace=True)
    question: str = Field(..., min_length=1, max_length=2000)
    top_k: Optional[int] = Field(None, ge=1, le=20)


class ChunkSource(BaseModel):
    chunk_id: str
    content: str
    source_file: str
    source_type: str = "txt"
    page_number: Optional[int] = None
    section_heading: Optional[str] = None
    date_ingested: str
    author: Optional[str] = None
    relevance_score: float


class QueryResponse(BaseModel):
    query_id: str
    question: str
    answer: str
    status: AnswerStatus
    reason: str
    response_mode: Literal["fixture", "live"]
    sources: list[ChunkSource]
    timestamp: datetime
    app: str = "Your Senior"


# ─── Ingestion ────────────────────────────────────────────────────────────────

class IngestRequest(BaseModel):
    folder_id: Optional[str] = None  # overrides GOOGLE_DRIVE_FOLDER_ID from env


class IngestStatus(str, Enum):
    PENDING   = "pending"
    RUNNING   = "running"
    COMPLETED = "completed"
    FAILED    = "failed"


class IngestResponse(BaseModel):
    job_id: str
    status: IngestStatus
    message: str
    documents_found: Optional[int] = None
    chunks_created: Optional[int] = None


class UploadIngestResponse(BaseModel):
    filename: str
    chunks_created: int
    status: str   # "completed" | "failed"
    message: str = ""


class TextIngestRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=500_000)
    filename: str = Field(default="pasted-text.txt", max_length=255)


# ─── Admin — Documents ────────────────────────────────────────────────────────

class ConfidenceDecayStatus(str, Enum):
    FRESH = "fresh"  # ingested < 7 days ago
    AGING = "aging"  # 7–30 days
    STALE = "stale"  # > 30 days


class DocumentInfo(BaseModel):
    doc_id: str
    filename: str
    source_type: str           # "pdf" | "docx" | "gdoc" | "txt"
    file_size_bytes: Optional[int] = None
    chunk_count: int
    date_ingested: datetime
    author: Optional[str] = None
    confidence_decay_status: ConfidenceDecayStatus


class DeleteDocumentResponse(BaseModel):
    doc_id: str
    deleted: bool
    chunks_removed: int
    message: str


# ─── Admin — Query Log ────────────────────────────────────────────────────────

class QueryLogEntry(BaseModel):
    query_id: str
    question: str
    status: AnswerStatus
    chunks_retrieved: int
    timestamp: datetime


# ─── Admin — System Health ────────────────────────────────────────────────────

class ChromaDBStatus(BaseModel):
    connected: bool
    total_documents: int
    total_chunks: int
    last_ingestion: Optional[datetime] = None
    collection_name: str


class SystemHealth(BaseModel):
    app: str = "Your Senior"
    backend_status: str
    chroma: ChromaDBStatus
    timestamp: datetime


# ─── Health endpoint ──────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    app: str = "Your Senior"
    version: str
    chroma_connected: bool
    timestamp: datetime
