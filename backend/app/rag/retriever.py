"""Retrieves the top-K semantically similar chunks from ChromaDB for a query."""

from app.db.chroma import get_collection
from app.models.schemas import ChunkSource
from app.rag.embedder import embed_query


async def retrieve_chunks(
    question: str, top_k: int
) -> tuple[list[ChunkSource], float]:
    """
    Embeds the question, queries ChromaDB for the closest chunks,
    and returns (chunks, similarity signal). Similarity is not answer accuracy.
    """
    collection = get_collection()
    total = collection.count()
    if total == 0:
        return [], 0.0

    embedding = await embed_query(question)

    results = collection.query(
        query_embeddings=[embedding],
        n_results=min(top_k, total),
        include=["documents", "metadatas", "distances"],
    )

    ids = results["ids"][0]
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    if not ids:
        return [], 0.0

    # ChromaDB cosine space stores (1 − similarity) as distance.
    # Invert so relevance_score = 1.0 means perfect match.
    relevance_scores = [max(0.0, min(1.0, 1.0 - d)) for d in distances]

    # Weighted retrieval confidence: top result counts for 50%, rest decay exponentially.
    # This rewards a strong top hit even if lower results are weak.
    weights = [0.5**i for i in range(len(relevance_scores))]
    total_weight = sum(weights)
    retrieval_confidence = sum(
        s * w for s, w in zip(relevance_scores, weights)
    ) / total_weight

    chunks = [
        ChunkSource(
            chunk_id=chunk_id,
            content=doc,
            source_file=meta.get("source_file", "unknown"),
            source_type=meta.get("source_type", "txt"),
            page_number=meta.get("page_number"),
            section_heading=meta.get("section_heading"),
            date_ingested=meta.get("date_ingested", ""),
            author=meta.get("author"),
            relevance_score=round(score, 4),
        )
        for chunk_id, doc, meta, score in zip(ids, documents, metadatas, relevance_scores)
    ]

    return chunks, round(retrieval_confidence, 4)
