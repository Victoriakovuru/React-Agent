from .base_agent import BaseAgent
from Graph.Tool.Tools import SearchEngine, VectorSearch

class SearchAgent(BaseAgent):
    def __init__(self):
        super().__init__("search")
        self.web_search = SearchEngine
        self.vector_search = VectorSearch
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        parsed_query = input_data.get("parsed_query", "")
        suggested_tools = input_data.get("suggested_tools", [])
        
        self.log_interaction("search_started", {
            "parsed_query": parsed_query,
            "suggested_tools": suggested_tools
        })
        
        results = {}
        
        if "web_search" in suggested_tools:
            web_results = await self._execute_web_search(parsed_query)
            results["web_results"] = web_results
            
        if "vector_search" in suggested_tools:
            vector_results = await self._execute_vector_search(parsed_query)
            results["vector_results"] = vector_results
        
        self.log_interaction("search_completed", results)
        
        return results
    
    async def _execute_web_search(self, query: str) -> Dict[str, Any]:
        # Execute web search
        return await self.web_search.arun(query)
    
    async def _execute_vector_search(self, query: str) -> Dict[str, Any]:
        # Execute vector search
        return await self.vector_search.arun(query)