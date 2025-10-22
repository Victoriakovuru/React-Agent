import chromadb
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from typing import List, Tuple
from langchain.docstore.document import Document

class ChromaVectorStore:
    def __init__(self, collection_name: str = "default_collection"):
        self.embeddings = HuggingFaceEmbeddings()
        self.collection_name = collection_name
        self.vector_store = None

    def initialize_store(self, documents: List[Document]):
        """Initialize the vector store with documents"""
        self.vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            collection_name=self.collection_name
        )

    def similarity_search_with_score(self, query: str, k: int = 3) -> List[Tuple[Document, float]]:
        """Perform similarity search and return documents with scores"""
        if not self.vector_store:
            raise ValueError("Vector store not initialized")
        return self.vector_store.similarity_search_with_score(query, k=k)