from typing import Dict, Any
from langgraph.graph import Graph, END
from agents import InputParserAgent, RetrievalAgent, SearchAgent
from vector_store import ChromaVectorStore
from llm_config import get_llm

class AgenticRAGSystem:
    def __init__(self):
        self.vector_store = ChromaVectorStore()
        self.input_parser = InputParserAgent()
        self.retrieval_agent = RetrievalAgent(self.vector_store)
        self.search_agent = SearchAgent()
        self.llm = get_llm()
        self.workflow = self._create_workflow()

    def _create_workflow(self) -> Graph:
        def parse_input(state):
            query = state["query"]
            parsed = self.input_parser.parse_input(query)
            state["parsed_query"] = parsed
            return {"next": "retrieve"}

        def retrieve_docs(state):
            query = state["query"]
            docs = self.retrieval_agent.retrieve_relevant_docs(query)
            state["retrieved_docs"] = docs
            return {"next": "search"}

        def search_web(state):
            query = state["query"]
            search_results = self.search_agent.search(query)
            state["search_results"] = search_results
            return {"next": "generate_response"}

        def generate_response(state):
            prompt = f"""
            Based on the following information, provide a comprehensive response:
            
            Original Query: {state['query']}
            Parsed Query: {state['parsed_query']}
            Retrieved Documents: {state['retrieved_docs']}
            Web Search Results: {state['search_results']}
            """
            response = self.llm.invoke(prompt)
            state["final_response"] = response.content
            return END

        workflow = Graph()
        
        workflow.add_node("parse", parse_input)
        workflow.add_node("retrieve", retrieve_docs)
        workflow.add_node("search", search_web)
        workflow.add_node("generate_response", generate_response)
        
        workflow.set_entry_point("parse")
        
        workflow.add_edge("parse", "retrieve")
        workflow.add_edge("retrieve", "search")
        workflow.add_edge("search", "generate_response")
        
        return workflow.compile()

    def process_query(self, query: str) -> Dict[str, Any]:
        """Process a query through the entire RAG system"""
        config = {"query": query}
        return self.workflow.invoke(config)