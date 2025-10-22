from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_agent import BaseAgent
from langchain_core.prompts import PromptTemplate
from Config.llm import llm

class WorkflowState:
    """Helper class to manage workflow state"""
    def __init__(self, workflow_id: str, initial_data: Dict[str, Any]):
        self.workflow_id = workflow_id
        self.current_state = initial_data
        self.steps = []
        self.start_time = datetime.utcnow()
        self.end_time = None
        self.status = "running"
        self.error = None

    def add_step(self, action: Dict[str, Any], result: Dict[str, Any]):
        self.steps.append({
            "step_id": len(self.steps) + 1,
            "action": action,
            "result": result,
            "timestamp": datetime.utcnow()
        })
        self.current_state.update(result)

    def complete(self, final_state: Dict[str, Any]):
        self.status = "completed"
        self.end_time = datetime.utcnow()
        self.current_state = final_state

    def fail(self, error: str):
        self.status = "failed"
        self.end_time = datetime.utcnow()
        self.error = error

class SupervisorAgent(BaseAgent):
    def __init__(self):
        super().__init__("supervisor")
        self.supervision_prompt = PromptTemplate(
            input_variables=["current_time", "current_user", "system_state", "task", "previous_steps"],
            template="""
            You are the supervisor agent responsible for orchestrating the entire RAG system.
            Current time: {current_time}
            User: {current_user}
            
            Available Agents:
            - Parser Agent: Analyzes and structures queries
            - Search Agent: Performs web and vector searches
            - Retrieval Agent: Synthesizes information
            - Document Agent: Handles document processing
            
            Current System State:
            {system_state}
            
            Task to Process:
            {task}
            
            Previous Steps:
            {previous_steps}
            
            Decide:
            1. Which agent(s) to invoke next
            2. What parameters to pass to them
            3. How to handle any errors or edge cases
            4. Whether to continue or terminate processing
            
            Your reasoning and decision:
            """
        )
        
        self.active_workflows: Dict[str, WorkflowState] = {}
        self.available_agents: Dict[str, BaseAgent] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.max_retries = 3
        self.retry_delay = 1  # seconds

    def register_agent(self, agent: BaseAgent):
        """Register an agent with the supervisor"""
        self.available_agents[agent.name] = agent
        self.log_interaction("agent_registered", {"agent_name": agent.name})

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main entry point for processing workflows"""
        workflow_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        workflow_state = WorkflowState(workflow_id, input_data)
        self.active_workflows[workflow_id] = workflow_state

        try:
            self.log_interaction("workflow_started", {
                "workflow_id": workflow_id,
                "input_data": input_data
            })

            result = await self._execute_workflow(workflow_state)
            
            workflow_state.complete(result)
            self.log_interaction("workflow_completed", {
                "workflow_id": workflow_id,
                "result": result
            })

            return self._prepare_workflow_response(workflow_state)

        except Exception as e:
            workflow_state.fail(str(e))
            self.log_interaction("workflow_failed", {
                "workflow_id": workflow_id,
                "error": str(e)
            })
            raise

    async def _execute_workflow(self, workflow_state: WorkflowState) -> Dict[str, Any]:
        """Execute the workflow with supervision"""
        while True:
            next_action = await self._get_next_action(
                workflow_state.current_state,
                workflow_state.steps
            )
            
            if next_action["action"] == "terminate":
                break
            
            step_result = await self._execute_step(
                workflow_state.workflow_id,
                next_action,
                workflow_state.current_state
            )
            
            workflow_state.add_step(next_action, step_result)
            
            # Check for completion conditions
            if self._should_terminate_workflow(workflow_state):
                break
        
        return workflow_state.current_state

    async def _get_next_action(
        self,
        current_state: Dict[str, Any],
        previous_steps: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Determine the next action using the supervision prompt"""
        prompt_response = await llm.ainvoke(
            self.supervision_prompt.format(
                current_time=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                current_user=current_state.get("user", "system"),
                system_state=self._format_system_state(current_state),
                task=current_state.get("original_task", "No task specified"),
                previous_steps=self._format_previous_steps(previous_steps)
            )
        )
        
        return self._parse_supervisor_decision(prompt_response.content)

    async def _execute_step(
        self,
        workflow_id: str,
        action: Dict[str, Any],
        current_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single step with retry logic"""
        agent_name = action["agent"]
        if agent_name not in self.available_agents:
            raise ValueError(f"Unknown agent: {agent_name}")
        
        agent = self.available_agents[agent_name]
        retry_count = 0
        
        while retry_count <= self.max_retries:
            try:
                result = await agent.process({
                    **current_state,
                    **action.get("parameters", {}),
                    "workflow_id": workflow_id,
                    "attempt": retry_count + 1
                })
                
                return {
                    "status": "success",
                    "agent": agent_name,
                    "result": result,
                    "attempts": retry_count + 1
                }
                
            except Exception as e:
                retry_count += 1
                if retry_count <= self.max_retries:
                    await asyncio.sleep(self.retry_delay * retry_count)
                    continue
                
                return {
                    "status": "error",
                    "agent": agent_name,
                    "error": str(e),
                    "attempts": retry_count
                }

    def _should_terminate_workflow(self, workflow_state: WorkflowState) -> bool:
        """Determine if the workflow should be terminated"""
        # Check for error conditions
        if workflow_state.error:
            return True
            
        # Check for completion conditions
        if len(workflow_state.steps) >= 10:  # Maximum steps safety limit
            return True
            
        # Check for successful completion
        last_step = workflow_state.steps[-1] if workflow_state.steps else None
        if last_step and last_step["result"].get("status") == "success":
            if "final_response" in last_step["result"].get("result", {}):
                return True
        
        return False

    def _prepare_workflow_response(self, workflow_state: WorkflowState) -> Dict[str, Any]:
        """Prepare the final workflow response"""
        return {
            "workflow_id": workflow_state.workflow_id,
            "status": workflow_state.status,
            "start_time": workflow_state.start_time,
            "end_time": workflow_state.end_time,
            "duration": (workflow_state.end_time - workflow_state.start_time).total_seconds() if workflow_state.end_time else None,
            "steps_executed": len(workflow_state.steps),
            "final_state": workflow_state.current_state,
            "error": workflow_state.error,
            "execution_timeline": workflow_state.steps
        }

    def _format_system_state(self, state: Dict[str, Any]) -> str:
        """Format the current system state for the prompt"""
        formatted_state = ["Current System State:"]
        
        for key, value in state.items():
            if isinstance(value, dict):
                formatted_state.append(f"{key}:")
                for sub_key, sub_value in value.items():
                    formatted_state.append(f"  {sub_key}: {sub_value}")
            else:
                formatted_state.append(f"{key}: {value}")
        
        return "\n".join(formatted_state)

    def _format_previous_steps(self, steps: List[Dict[str, Any]]) -> str:
        """Format previous steps for the prompt"""
        if not steps:
            return "No previous steps executed."
        
        formatted_steps = ["Previous Steps:"]
        
        for i, step in enumerate(steps, 1):
            formatted_steps.extend([
                f"Step {i}:",
                f"  Agent: {step['action']['agent']}",
                f"  Status: {step['result']['status']}",
                f"  Timestamp: {step['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}"
            ])
            
            if "error" in step["result"]:
                formatted_steps.append(f"  Error: {step['result']['error']}")
        
        return "\n".join(formatted_steps)

    def _parse_supervisor_decision(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into a structured decision"""
        try:
            # Check for termination signal
            if "terminate" in response.lower():
                return {"action": "terminate"}
            
            # Extract agent and parameters
            for agent_name in self.available_agents.keys():
                if agent_name.lower() in response.lower():
                    return {
                        "action": "execute",
                        "agent": agent_name,
                        "parameters": self._extract_parameters(response),
                        "retry_on_error": True,
                        "max_retries": self.max_retries
                    }
            
            # Default to termination if no clear decision
            return {
                "action": "terminate",
                "reason": "No clear agent decision from supervisor"
            }
            
        except Exception as e:
            return {
                "action": "terminate",
                "reason": f"Error parsing supervisor decision: {str(e)}"
            }

    def _extract_parameters(self, response: str) -> Dict[str, Any]:
        """Extract parameters from the LLM response"""
        parameters = {}
        
        try:
            # Look for parameter section
            if "parameters:" in response.lower():
                params_section = response.lower().split("parameters:")[1].split("\n")[0]
                
                # Extract key-value pairs
                pairs = params_section.split(",")
                for pair in pairs:
                    if ":" in pair:
                        key, value = pair.split(":", 1)
                        parameters[key.strip()] = value.strip()
            
            # Add timestamp
            parameters["timestamp"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            
        except Exception as e:
            parameters["error"] = f"Parameter extraction failed: {str(e)}"
        
        return parameters

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific workflow"""
        if workflow_id not in self.active_workflows:
            return None
        
        workflow_state = self.active_workflows[workflow_id]
        return self._prepare_workflow_response(workflow_state)

    def get_active_workflows(self) -> List[Dict[str, Any]]:
        """Get all active workflows"""
        return [
            {
                "workflow_id": workflow_id,
                "status": state.status,
                "start_time": state.start_time,
                "steps_completed": len(state.steps)
            }
            for workflow_id, state in self.active_workflows.items()
        ]

    def cleanup_workflow(self, workflow_id: str):
        """Clean up completed workflow data"""
        if workflow_id in self.active_workflows:
            workflow_state = self.active_workflows[workflow_id]
            if workflow_state.status in ["completed", "failed"]:
                # Archive workflow data if needed
                self.execution_history.append(self._prepare_workflow_response(workflow_state))
                # Remove from active workflows
                del self.active_workflows[workflow_id]