"""Query endpoint — accepts a question and returns a RAG-powered answer."""

from fastapi import APIRouter, HTTPException, status

from app.models.schemas import QueryRequest, QueryResponse
from app.rag.engine import answer_question

router = APIRouter(prefix="/query", tags=["Query"])


@router.post("", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Ask a question. Returns validated citations or an explicit unsupported answer.
    """
    try:
        return await answer_question(request.question, request.top_k)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document retrieval is unavailable. Please try again later.",
        )
