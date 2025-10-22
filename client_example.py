import asyncio
import websockets
import json

async def connect_to_rag_system():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        # Subscribe to agent updates
        await websocket.send(json.dumps({
            "type": "subscribe",
            "agents": ["parser", "search", "retrieval"]
        }))
        
        # Listen for updates
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            
            if data["type"] == "agent_update":
                print(f"Agent {data['agent']} update:")
                print(json.dumps(data['data'], indent=2))

asyncio.get_event_loop().run_until_complete(connect_to_rag_system())