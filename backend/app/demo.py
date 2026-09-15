"""Author-written provider stub over fixed synthetic documents, never live AI."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.db.chroma import get_collection
from app.ingestion.parsers.txt_parser import TXTParser
from app.rag.embedder import embed_texts

FIXTURES = Path(__file__).parent / "fixtures"
CORPUS_ID = "northstar-synthetic-v1"
ANSWERS = json.loads((FIXTURES / "answers.json").read_text(encoding="utf-8"))
router = APIRouter()


def documents() -> list[dict]:
    return [{"filename": p.name, "content": p.read_text(encoding="utf-8").strip()}
            for p in sorted(FIXTURES.glob("*.txt"))]


async def seed_demo() -> None:
    """Parse only bundled TXT files into a fresh, memory-only Chroma corpus."""
    collection = get_collection()
    # Fixed files each contain one short paragraph; no tokenizer/model downloads.
    ids, texts, metadata = [], [], []
    for doc in documents():
        parsed = await TXTParser().parse(doc["content"].encode(), doc["filename"])
        for index, paragraph in enumerate(parsed.paragraphs):
            ids.append(f"{Path(doc['filename']).stem}-{index}")
            texts.append(paragraph)
            metadata.append({
                "source_file": doc["filename"], "source_type": "txt",
                "doc_id": Path(doc["filename"]).stem,
                "date_ingested": "2026-09-15T00:00:00+00:00",
                "author": "Interstellar synthetic fixture",
                "section_heading": "Synthetic policy",
            })
    embeddings = await embed_texts(texts)
    existing = collection.get()["ids"]
    if existing:
        collection.delete(ids=existing)
    collection.add(ids=ids, documents=texts, metadatas=metadata,
                   embeddings=embeddings)


def fixture_answer(question: str) -> str:
    # Exact-match scenarios exercise the provider boundary; no AI generation.
    return json.dumps(ANSWERS.get(question.strip(), {
        "status": "unsupported", "answer": "This question has no fixture answer.",
        "reason": "The provider stub supports only its labelled sample questions.",
        "cited_chunk_ids": [],
    }))


@router.get("/demo")
async def demo_info():
    if not get_settings().demo_mode:
        raise HTTPException(status_code=404, detail="Demo is disabled.")
    return {
        "response_mode": "fixture", "corpus_id": CORPUS_ID,
        "description": "Three fictional workplace policies written for this synthetic demo.",
        "questions": list(ANSWERS), "documents": documents(),
    }
