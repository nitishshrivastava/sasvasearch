"""
Sub-agent management for Deep Agent.
"""

import uuid
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

from onyx.agents.deep_agent.prompts import SUB_AGENT_PROMPT_TEMPLATE
from onyx.agents.deep_agent.memory import VirtualFileSystem
from onyx.utils.logger import setup_logger

logger = setup_logger()


class SubAgentStatus(Enum):
    """Status of a sub-agent."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SubAgentType(Enum):
    """Types of sub-agents."""
    RESEARCH = "research"
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    VALIDATION = "validation"
    CUSTOM = "custom"


class SubAgentConfig(BaseModel):
    """Configuration for a sub-agent."""
    name: str = Field(description="Name of the sub-agent")
    type: SubAgentType = Field(description="Type of sub-agent")
    task_description: str = Field(description="Description of the task")
    objectives: List[str] = Field(description="Specific objectives")
    context: Dict[str, Any] = Field(default_factory=dict, description="Context from parent")
    max_iterations: int = Field(default=10, description="Maximum iterations allowed")
    timeout_seconds: int = Field(default=300, description="Timeout in seconds")
    
    
class SubAgentResult(BaseModel):
    """Result from a sub-agent execution."""
    agent_id: str
    status: SubAgentStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    iterations: int = 0
    logs: List[str] = Field(default_factory=list)
    

class SubAgent:
    """Individual sub-agent instance."""
    
    def __init__(
        self,
        config: SubAgentConfig,
        filesystem: VirtualFileSystem,
        execute_func: Optional[Callable] = None
    ):
        self.id = str(uuid.uuid4())
        self.config = config
        self.filesystem = filesystem
        self.execute_func = execute_func
        self.status = SubAgentStatus.IDLE
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.logs: List[str] = []
        self.result: Optional[Any] = None
        self.error: Optional[str] = None
        self.iterations = 0
        
        # Create dedicated workspace
        self.workspace_path = f"/subagents/{self.id}"
        self.filesystem.create_directory(self.workspace_path)
        
    def log(self, message: str):
        """Add a log message."""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        logger.debug(f"SubAgent {self.id}: {message}")
        
    def get_prompt(self) -> str:
        """Generate the prompt for this sub-agent."""
        objectives_str = "\n".join(f"- {obj}" for obj in self.config.objectives)
        context_str = "\n".join(f"- {k}: {v}" for k, v in self.config.context.items())
        
        return SUB_AGENT_PROMPT_TEMPLATE.format(
            task_description=self.config.task_description,
            objectives=objectives_str,
            context=context_str
        )
    
    def save_to_workspace(self, filename: str, content: str) -> bool:
        """Save content to the agent's workspace."""
        filepath = f"{self.workspace_path}/{filename}"
        return self.filesystem.write_file(filepath, content)
    
    def read_from_workspace(self, filename: str) -> Optional[str]:
        """Read content from the agent's workspace."""
        filepath = f"{self.workspace_path}/{filename}"
        return self.filesystem.read_file(filepath)
    
    async def execute(self) -> SubAgentResult:
        """Execute the sub-agent task."""
        self.status = SubAgentStatus.RUNNING
        self.started_at = datetime.now()
        self.log(f"Starting execution: {self.config.task_description}")
        
        try:
            if self.execute_func:
                # Use custom execution function if provided
                self.result = await self.execute_func(self)
            else:
                # Default execution logic
                self.result = await self._default_execute()
                
            self.status = SubAgentStatus.COMPLETED
            self.log("Execution completed successfully")
            
        except Exception as e:
            self.status = SubAgentStatus.FAILED
            self.error = str(e)
            self.log(f"Execution failed: {e}")
            
        finally:
            self.completed_at = datetime.now()
            execution_time = (self.completed_at - self.started_at).total_seconds()
            
            # Save execution summary
            summary = {
                "agent_id": self.id,
                "task": self.config.task_description,
                "status": self.status.value,
                "result": str(self.result) if self.result else None,
                "error": self.error,
                "execution_time": execution_time,
                "iterations": self.iterations,
                "logs": self.logs
            }
            
            import json
            self.save_to_workspace("execution_summary.json", json.dumps(summary, indent=2))
            
            return SubAgentResult(
                agent_id=self.id,
                status=self.status,
                result=self.result,
                error=self.error,
                execution_time=execution_time,
                iterations=self.iterations,
                logs=self.logs
            )
    
    async def _default_execute(self) -> Any:
        """Default execution logic for sub-agents."""
        # This is a placeholder for the default execution
        # In practice, this would integrate with the existing agent system
        self.log("Executing default sub-agent logic")
        
        # Simulate some work
        for i in range(min(3, self.config.max_iterations)):
            self.iterations += 1
            self.log(f"Iteration {self.iterations}")
            
            # Save intermediate results
            self.save_to_workspace(
                f"iteration_{self.iterations}.txt",
                f"Results from iteration {self.iterations}"
            )
        
        return f"Completed {self.config.task_description}"
    

class SubAgentManager:
    """Manager for coordinating multiple sub-agents."""
    
    def __init__(self, filesystem: VirtualFileSystem):
        self.filesystem = filesystem
        self.agents: Dict[str, SubAgent] = {}
        self.execution_history: List[SubAgentResult] = []
        
    def create_agent(
        self,
        name: str,
        type: SubAgentType,
        task_description: str,
        objectives: List[str],
        context: Optional[Dict[str, Any]] = None,
        execute_func: Optional[Callable] = None
    ) -> SubAgent:
        """Create a new sub-agent."""
        config = SubAgentConfig(
            name=name,
            type=type,
            task_description=task_description,
            objectives=objectives,
            context=context or {}
        )
        
        agent = SubAgent(config, self.filesystem, execute_func)
        self.agents[agent.id] = agent
        
        logger.info(f"Created sub-agent {agent.id} ({name}) for: {task_description}")
        return agent
    
    async def execute_agent(self, agent_id: str) -> Optional[SubAgentResult]:
        """Execute a specific sub-agent."""
        if agent_id not in self.agents:
            logger.error(f"Agent {agent_id} not found")
            return None
            
        agent = self.agents[agent_id]
        result = await agent.execute()
        self.execution_history.append(result)
        
        return result
    
    async def execute_parallel(
        self,
        agent_ids: List[str]
    ) -> Dict[str, SubAgentResult]:
        """Execute multiple sub-agents in parallel."""
        import asyncio
        
        tasks = []
        for agent_id in agent_ids:
            if agent_id in self.agents:
                tasks.append(self.execute_agent(agent_id))
            else:
                logger.warning(f"Agent {agent_id} not found, skipping")
                
        results = await asyncio.gather(*tasks)
        
        return {
            agent_id: result
            for agent_id, result in zip(agent_ids, results)
            if result is not None
        }
    
    def get_agent_status(self, agent_id: str) -> Optional[SubAgentStatus]:
        """Get the status of a sub-agent."""
        if agent_id in self.agents:
            return self.agents[agent_id].status
        return None
    
    def get_agent_result(self, agent_id: str) -> Optional[Any]:
        """Get the result of a sub-agent execution."""
        if agent_id in self.agents:
            return self.agents[agent_id].result
        return None
    
    def get_active_agents(self) -> List[SubAgent]:
        """Get all currently active sub-agents."""
        return [
            agent for agent in self.agents.values()
            if agent.status == SubAgentStatus.RUNNING
        ]
    
    def cancel_agent(self, agent_id: str) -> bool:
        """Cancel a running sub-agent."""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            if agent.status == SubAgentStatus.RUNNING:
                agent.status = SubAgentStatus.CANCELLED
                agent.log("Agent cancelled by manager")
                return True
        return False
    
    def cleanup_completed(self):
        """Remove completed agents from memory."""
        completed_ids = [
            agent_id for agent_id, agent in self.agents.items()
            if agent.status in [SubAgentStatus.COMPLETED, SubAgentStatus.FAILED, SubAgentStatus.CANCELLED]
        ]
        
        for agent_id in completed_ids:
            del self.agents[agent_id]
            
        logger.debug(f"Cleaned up {len(completed_ids)} completed agents")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all sub-agents."""
        status_counts = {status: 0 for status in SubAgentStatus}
        for agent in self.agents.values():
            status_counts[agent.status] += 1
            
        return {
            "total_agents": len(self.agents),
            "status_breakdown": {s.value: c for s, c in status_counts.items()},
            "active_agents": len(self.get_active_agents()),
            "execution_history_count": len(self.execution_history)
        }
