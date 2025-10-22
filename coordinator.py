from typing import Dict, Any, List
from .base_agent import BaseAgent
from fastapi import WebSocket
import asyncio
import json

class AgentCoordinator:
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.active_workflows: Dict[str, List[str]] = {
            "query_processing": ["parser", "search", "retrieval"],
            "document_ingestion": ["validator", "processor", "indexer"]
        }
        self.websocket_connections: List[WebSocket] = []
    
    def register_agent(self, agent: BaseAgent):
        self.agents[agent.name] = agent
    
    async def broadcast_agent_update(self, agent_name: str, update: Dict[str, Any]):
        """Broadcast agent state updates to all connected clients"""
        message = {
            "type": "agent_update",
            "agent": agent_name,
            "data": update,
            "timestamp": datetime.utcnow().isoformat()
        }
        for ws in self.websocket_connections:
            try:
                await ws.send_json(message)
            except:
                continue

    async def execute_workflow(self, 
                             workflow_name: str, 
                             initial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow by coordinating multiple agents"""
        if workflow_name not in self.active_workflows:
            raise ValueError(f"Unknown workflow: {workflow_name}")
        
        workflow_results = []
        current_data = initial_data
        
        for agent_name in self.active_workflows[workflow_name]:
            if agent_name not in self.agents:
                continue
                
            agent = self.agents[agent_name]
            
            # Process with current agent
            result = await agent.process(current_data)
            
            # Broadcast update
            await self.broadcast_agent_update(agent_name, result)
            
            workflow_results.append({
                "agent": agent_name,
                "result": result
            })
            
            # Update data for next agent
            current_data.update(result)
        
        return {
            "workflow": workflow_name,
            "results": workflow_results,
            "final_state": current_data
        }