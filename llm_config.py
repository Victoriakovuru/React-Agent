from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

def get_llm(temperature=0):
    """Initialize Groq LLM with llama-3.1-8b-instant"""
    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=temperature,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )