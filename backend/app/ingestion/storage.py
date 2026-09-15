"""Replace a document only after its new embeddings and chunks are stored."""

from app.db.chroma import get_collection
from app.rag.embedder import embed_texts


async def replace_document_chunks(chunks) -> None:
    if not chunks:
        return
    if len({chunk.doc_id for chunk in chunks}) != 1:
        raise ValueError("One document per replacement is required.")
    texts = [chunk.content for chunk in chunks]
    embeddings = await embed_texts(texts)
    collection = get_collection()
    existing = collection.get(where={"doc_id": chunks[0].doc_id})["ids"]
    new_ids = [chunk.chunk_id for chunk in chunks]
    if set(existing) & set(new_ids):
        raise ValueError("Replacement chunks must have new identifiers.")
    # No await between snapshot, add and delete in this single-worker prototype.
    # ponytail: Chroma has no transaction here; deletion failure can leave duplicate
    # generations. Add atomic generation publication before multi-worker ingestion.
    collection.add(ids=new_ids, documents=texts, embeddings=embeddings,
                   metadatas=[chunk.metadata for chunk in chunks])
    if existing:
        collection.delete(ids=existing)
