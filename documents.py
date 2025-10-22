from fastapi import APIRouter, Depends, HTTPException
from ..models import DocumentInput, DocumentResponse
from ..dependencies import get_rag_system, RAGSystem
from typing import List

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/batch", response_model=List[DocumentResponse])
async def batch_insert_documents(
    documents: List[DocumentInput],
    rag_system: RAGSystem = Depends(get_rag_system)
):
    """Insert multiple documents at once"""
    responses = []
    for doc in documents:
        result = await rag_system.insert_document(
            content=doc.content,
            metadata=doc.metadata
        )
        responses.append(result)
    return responses

@router.get("/status/{document_id}")
async def get_document_status(
    document_id: str,
    rag_system: RAGSystem = Depends(get_rag_system)
):
    """Get the status of a document"""
    # Implementation would depend on your document tracking system
    pass