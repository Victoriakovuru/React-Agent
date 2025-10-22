from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.state = {}
        self.conversation_history = []
    
    def log_interaction(self, action: str, data: Dict[str, Any]):
        timestamp = datetime.utcnow()
        log_entry = {
            "agent": self.name,
            "timestamp": timestamp,
            "action": action,
            "data": data
        }
        self.conversation_history.append(log_entry)
        return log_entry
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Abstract method that must be implemented by all agents
        Args:
            input_data: Dictionary containing input data for processing
        Returns:
            Dictionary containing processing results
        """
        pass