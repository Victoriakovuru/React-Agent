from fastapi import Depends, HTTPException, status
from Config.llm import llm
from Graph.Agent.document_agent import DocumentInsertionAgent
from Graph.Tool.Tools import SearchEngine, VectorSearch
from Graph.Memory.memory import short_term_memory_store, load_and_save_long_term
from .config import get_settings, Settings
import time

class RAGSystem:
    def __init__(self, settings: Settings = Depends(get_settings)):
        self.settings = settings
        self.doc_agent = DocumentInsertionAgent()
        self.agents = self._initialize_agents()
        
    def _initialize_agents(self):
        from main import create_agents
        return create_agents()
    
    async def process_query(self, query: str, context: Dict = None):
        start_time = time.time()
        
        try:
            result = self._process_query(query, context)
            
            processing_time = time.time() - start_time
            
            return {
                "query": query,
                "response": result,
                "processing_time": processing_time,
                "timestamp": datetime.utcnow()
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing query: {str(e)}"
            )
    
    async def insert_document(self, content: str, metadata: Dict = None):
        try:
            result = self.doc_agent.insert_document(content, metadata)
            
            return {
                "document_id": result["insertion_result"]["document_ids"][0],
                "status": result["insertion_result"]["status"],
                "message": result["insertion_result"]["message"],
                "chunks_created": len(result["insertion_result"]["document_ids"]),
                "metadata": metadata,
                "timestamp": datetime.utcnow()
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error inserting document: {str(e)}"
            )

@lru_cache()
def get_rag_system(settings: Settings = Depends(get_settings)):
    return RAGSystem(settings)