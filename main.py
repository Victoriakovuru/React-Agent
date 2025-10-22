from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
from Graph.Tool.Tools import SearchEngine, VectorSearch, VectorStore

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    search_type: Optional[str] = "both"

class DocumentRequest(BaseModel):
    content: str
    metadata: Dict[str, Any]

@app.get("/")
async def root():
    """Root endpoint to verify API is working"""
    return {
        "status": "online",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "RAG System API is running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.post("/api/search")
async def search(request: QueryRequest):
    """Search endpoint"""
    try:
        results = {}
        
        if request.search_type in ["web", "both"]:
            web_results = await SearchEngine.arun(query=request.query)
            results["web_search"] = web_results
        
        if request.search_type in ["vector", "both"]:
            vector_results = await VectorSearch.arun(query=request.query)
            results["vector_search"] = vector_results
        
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/document")
async def add_document(request: DocumentRequest):
    """Document addition endpoint"""
    try:
        result = await VectorStore.arun(
            content=request.content,
            metadata=request.metadata
        )
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add documentation tags
app.openapi_tags = [
    {
        "name": "default",
        "description": "Default endpoints"
    },
    {
        "name": "search",
        "description": "Search operations"
    },
    {
        "name": "document",
        "description": "Document operations"
    }
]