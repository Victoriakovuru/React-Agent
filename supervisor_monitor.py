import asyncio
import websockets
import json
from datetime import datetime

async def monitor_supervisor():
    uri = "ws://localhost:8000/ws/supervisor"
    
    async with websockets.connect(uri) as websocket:
        # Subscribe to all workflow updates
        await websocket.send(json.dumps({
            "type": "subscribe_all"
        }))
        
        print("Monitoring supervisor activities...")
        
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)
                
                if data["type"] == "workflow_update":
                    print(f"\nWorkflow Update at {datetime.utcnow()}")
                    print(f"Workflow ID: {data['workflow_id']}")
                    print(f"Status: {data['status']['status']}")
                    print("Steps completed:", len(data['status'].get('steps', [])))
                
                elif data["type"] == "active_workflows":
                    print("\nActive Workflows:")
                    for workflow in data["workflows"]:
                        print(f"- {workflow['workflow_id']}: {workflow['status']}")
            
            except Exception as e:
                print(f"Error: {e}")
                await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(monitor_supervisor())