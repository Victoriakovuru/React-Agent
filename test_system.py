import asyncio
import httpx
import json
from datetime import datetime

async def test_system():
    async with httpx.AsyncClient() as client:
        # Test health check
        response = await client.get("http://localhost:8000/health")
        print("Health check:", response.json())

        # Test document addition
        doc_response = await client.post(
            "http://localhost:8000/document",
            json={
                "content": "This is a test document about artificial intelligence.",
                "metadata": {
                    "title": "AI Test",
                    "author": "Victoriakovuru",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        )
        print("\nDocument addition:", json.dumps(doc_response.json(), indent=2))

        # Test search
        search_response = await client.post(
            "http://localhost:8000/search",
            json={
                "query": "What is artificial intelligence?",
                "search_type": "both"
            }
        )
        print("\nSearch results:", json.dumps(search_response.json(), indent=2))

if __name__ == "__main__":
    asyncio.run(test_system())