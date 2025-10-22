from fastapi import APIRouter, Depends
from ..models import QueryInput, SearchResponse
from ..dependencies import get_rag_system, RAGSystem
from typing import List

router = APIRouter(prefix="/query", tags=["query"])

@router.post("/stream")
async def stream_query(
    query_input: QueryInput,
    rag_system: RAGSystem = Depends(get_rag_system)
):
    """Stream the query processing results"""
    # Implementation would depend on your streaming requirements
    pass

@router.get("/history")
async def get_query_history(
    rag_system: RAGSystem = Depends(get_rag_system)
):
    """Get the query processing history"""
    return {
        "history": load_and_save_long_term()
    }