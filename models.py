from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

class QueryInput(BaseModel):
    """Model for query input"""
    query: str = Field(..., description="The user's query to process")
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context for the query"
    )

class WorkflowStep(BaseModel):
    """Model for a single workflow step"""
    action: Dict[str, Any] = Field(..., description="The action taken in this step")
    result: Dict[str, Any] = Field(..., description="The result of the action")
    timestamp: datetime = Field(..., description="When this step was executed")

class WorkflowResponse(BaseModel):
    """Model for workflow execution response"""
    workflow_id: str = Field(..., description="Unique identifier for the workflow")
    status: str = Field(..., description="Current status of the workflow")
    result: Dict[str, Any] = Field(..., description="Final result of the workflow")
    steps: List[WorkflowStep] = Field(..., description="Timeline of workflow execution")
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = Field(default=None)

class WorkflowStatus(BaseModel):
    """Model for workflow status updates"""
    workflow_id: str
    status: str
    steps_completed: int
    current_agent: Optional[str] = None
    last_update: datetime = Field(default_factory=datetime.utcnow)
    error: Optional[str] = None

class AgentUpdate(BaseModel):
    """Model for agent status updates"""
    agent_name: str
    action: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class DocumentInput(BaseModel):
    """Model for document input"""
    content: str = Field(..., description="The content of the document")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for the document"
    )

class HealthCheck(BaseModel):
    """Model for API health check response"""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"