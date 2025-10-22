from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.endpoints import router as api_router

app = FastAPI(
    title="RAG System API",
    description="API for document ingestion and query processing using RAG system",
    version="1.0.0",
    openapi_tags=[
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
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API router
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["api", "Graph"]
    )