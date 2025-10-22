from langchain.agents import Tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_community.tools import TavilySearchResults
from typing import Dict, List, Any
from vector_store import ChromaVectorStore
from llm_config import get_llm

class InputParserAgent:
    def __init__(self):
        self.llm = get_llm()
        self.prompt = PromptTemplate.from_template(
            """You are an input parsing agent. Your role is to analyze and structure the user's query.
            Please parse the following input and identify the key elements:
            
            User Query: {query}
            
            Provide a structured analysis including:
            1. Main topic
            2. Key terms
            3. Type of information requested
            """
        )

    def parse_input(self, query: str) -> Dict[str, Any]:
        """Parse and structure the user's input query"""
        response = self.llm.invoke(self.prompt.format(query=query))
        return {"parsed_query": response.content}

class RetrievalAgent:
    def __init__(self, vector_store: ChromaVectorStore):
        self.vector_store = vector_store
        self.llm = get_llm()
        
    def retrieve_relevant_docs(self, query: str, k: int = 3) -> List[str]:
        """Retrieve relevant documents from the vector store"""
        docs_and_scores = self.vector_store.similarity_search_with_score(query, k=k)
        return [doc.page_content for doc, score in docs_and_scores]

class SearchAgent:
    def __init__(self):
        self.llm = get_llm()
        self.tools = [
            Tool(
                name="Tavily Search",
                description="Search the internet for current information",
                func=TavilySearchResults().run
            )
        ]
        
        self.prompt = PromptTemplate.from_template(
            """You are a search agent that helps find additional information from the internet.
            Use the Tavily search tool when you need to find current or supplementary information.
            
            Question: {question}
            
            Think about what specific information you need to search for, then use the search tool accordingly.
            """
        )
        
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True
        )

    def search(self, query: str) -> str:
        """Perform an internet search using Tavily"""
        return self.agent_executor.invoke({"question": query})["output"]