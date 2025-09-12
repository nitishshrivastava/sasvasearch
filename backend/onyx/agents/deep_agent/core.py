"""
Core Deep Agent implementation that orchestrates planning, sub-agents, and memory.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional, Iterator
from datetime import datetime
from pydantic import BaseModel, Field

from onyx.agents.deep_agent.planning import TodoList, TaskPriority, TaskStatus
from onyx.agents.deep_agent.memory import VirtualFileSystem
from onyx.agents.deep_agent.sub_agents import SubAgentManager, SubAgentType
from onyx.agents.deep_agent.prompts import DEEP_AGENT_SYSTEM_PROMPT, PLANNING_PROMPT
from onyx.chat.models import AnswerStream
from onyx.llm.interfaces import LLM
from onyx.tools.tool import Tool
from onyx.utils.logger import setup_logger

logger = setup_logger()


class DeepAgentConfig(BaseModel):
    """Configuration for Deep Agent."""
    enable_planning: bool = Field(default=True, description="Enable TODO list planning")
    enable_sub_agents: bool = Field(default=True, description="Enable sub-agent spawning")
    enable_memory: bool = Field(default=True, description="Enable virtual file system")
    max_sub_agents: int = Field(default=5, description="Maximum concurrent sub-agents")
    max_iterations: int = Field(default=20, description="Maximum iterations for task completion")
    verbose: bool = Field(default=False, description="Enable verbose logging")
    

class DeepAgentState(BaseModel):
    """State of the Deep Agent execution."""
    query: str
    todo_list: Optional[Dict[str, Any]] = None
    memory_summary: Optional[Dict[str, Any]] = None
    sub_agents_summary: Optional[Dict[str, Any]] = None
    iterations_completed: int = 0
    start_time: datetime = Field(default_factory=datetime.now)
    

class DeepAgent:
    """
    Deep Agent implementation with planning, sub-agents, and virtual memory.
    Designed for handling complex, multi-step queries with depth and thoroughness.
    """
    
    def __init__(
        self,
        llm: LLM,
        tools: List[Tool],
        config: Optional[DeepAgentConfig] = None
    ):
        self.llm = llm
        self.tools = tools
        self.config = config or DeepAgentConfig()
        
        # Initialize components
        self.todo_list = TodoList() if self.config.enable_planning else None
        self.filesystem = VirtualFileSystem() if self.config.enable_memory else None
        self.sub_agent_manager = SubAgentManager(self.filesystem) if self.config.enable_sub_agents else None
        
        self.state: Optional[DeepAgentState] = None
        self.current_iteration = 0
        
    def _log(self, message: str, level: str = "info"):
        """Log a message with appropriate level."""
        if self.config.verbose or level in ["error", "warning"]:
            logger_func = getattr(logger, level, logger.info)
            logger_func(f"[DeepAgent] {message}")
            
    def _save_to_memory(self, path: str, content: str) -> bool:
        """Save content to virtual memory if enabled."""
        if self.filesystem:
            return self.filesystem.write_file(path, content)
        return False
    
    def _read_from_memory(self, path: str) -> Optional[str]:
        """Read content from virtual memory if enabled."""
        if self.filesystem:
            return self.filesystem.read_file(path)
        return None
    
    async def _create_plan(self, query: str) -> List[Dict[str, Any]]:
        """Create a TODO list plan for the query."""
        if not self.todo_list:
            return []
            
        # Generate planning prompt
        planning_prompt = PLANNING_PROMPT.format(query=query)
        
        # Get plan from LLM
        response = self.llm.invoke(planning_prompt)
        plan_text = response.content if hasattr(response, 'content') else str(response)
        
        # Parse plan and create TODO items
        tasks = []
        lines = plan_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('*') or line[0].isdigit()):
                # Extract task description
                task_desc = line.lstrip('-*0123456789. ').strip()
                
                if task_desc:
                    # Determine priority based on keywords
                    priority = TaskPriority.MEDIUM
                    if any(word in task_desc.lower() for word in ['critical', 'urgent', 'important']):
                        priority = TaskPriority.HIGH
                    elif any(word in task_desc.lower() for word in ['optional', 'nice to have']):
                        priority = TaskPriority.LOW
                        
                    # Add task to TODO list
                    task = self.todo_list.add_task(
                        title=task_desc,
                        priority=priority
                    )
                    tasks.append(task.model_dump())
                    
        # Save plan to memory
        self._save_to_memory(
            "/research/initial_plan.md",
            self.todo_list.to_markdown()
        )
        
        self._log(f"Created plan with {len(tasks)} tasks")
        return tasks
    
    async def _spawn_sub_agent(
        self,
        task_description: str,
        objectives: List[str],
        context: Dict[str, Any]
    ) -> Optional[Any]:
        """Spawn a sub-agent for a specific task."""
        if not self.sub_agent_manager:
            return None
            
        # Check if we've reached the limit
        active_agents = self.sub_agent_manager.get_active_agents()
        if len(active_agents) >= self.config.max_sub_agents:
            self._log(f"Maximum sub-agents limit reached ({self.config.max_sub_agents})", "warning")
            return None
            
        # Create sub-agent
        agent = self.sub_agent_manager.create_agent(
            name=f"SubAgent_{self.current_iteration}",
            type=SubAgentType.RESEARCH,
            task_description=task_description,
            objectives=objectives,
            context=context
        )
        
        # Execute sub-agent
        result = await self.sub_agent_manager.execute_agent(agent.id)
        
        if result and result.status.value == "completed":
            # Save sub-agent results to memory
            self._save_to_memory(
                f"/subagents/{agent.id}/final_result.json",
                json.dumps(result.model_dump(), indent=2, default=str)
            )
            
            return result.result
        else:
            self._log(f"Sub-agent {agent.id} failed: {result.error if result else 'Unknown error'}", "error")
            return None
    
    async def _execute_task(self, task_id: str) -> bool:
        """Execute a single task from the TODO list."""
        if not self.todo_list:
            return False
            
        task = self.todo_list.items.get(task_id)
        if not task:
            return False
            
        self._log(f"Executing task: {task.title}")
        
        # Update task status
        self.todo_list.update_task_status(task_id, TaskStatus.IN_PROGRESS)
        
        try:
            # Determine if this task needs a sub-agent
            needs_sub_agent = any(word in task.title.lower() for word in [
                'research', 'analyze', 'investigate', 'explore', 'deep dive'
            ])
            
            if needs_sub_agent and self.config.enable_sub_agents:
                # Spawn sub-agent for this task
                result = await self._spawn_sub_agent(
                    task_description=task.title,
                    objectives=[task.description] if task.description else [task.title],
                    context={"parent_query": self.state.query if self.state else ""}
                )
                
                if result:
                    self.todo_list.add_note_to_task(task_id, f"Sub-agent result: {result}")
                    
            else:
                # Execute task directly using tools
                # This is a simplified implementation - in practice, would use the actual tools
                self.todo_list.add_note_to_task(task_id, f"Executed at iteration {self.current_iteration}")
                
            # Mark task as completed
            self.todo_list.update_task_status(task_id, TaskStatus.COMPLETED)
            return True
            
        except Exception as e:
            self._log(f"Task execution failed: {e}", "error")
            self.todo_list.update_task_status(task_id, TaskStatus.BLOCKED)
            self.todo_list.add_note_to_task(task_id, f"Error: {str(e)}")
            return False
    
    async def _synthesize_results(self) -> str:
        """Synthesize all results into a comprehensive answer."""
        synthesis_parts = []
        
        # Gather TODO list summary
        if self.todo_list:
            summary = self.todo_list.get_task_summary()
            synthesis_parts.append(f"Completed {summary['completion_rate']:.1f}% of planned tasks")
            
        # Gather sub-agent results
        if self.sub_agent_manager:
            sub_summary = self.sub_agent_manager.get_summary()
            synthesis_parts.append(f"Executed {sub_summary['total_agents']} sub-agents")
            
        # Read key findings from memory
        if self.filesystem:
            findings_files = self.filesystem.search_files("findings", "/research")
            for file_path in findings_files[:3]:  # Limit to top 3 findings
                content = self.filesystem.read_file(file_path)
                if content:
                    synthesis_parts.append(f"Finding: {content[:200]}...")
                    
        # Generate final synthesis using LLM
        synthesis_prompt = f"""
        Based on the following research components, provide a comprehensive answer to: {self.state.query if self.state else ''}
        
        Components:
        {chr(10).join(f'- {part}' for part in synthesis_parts)}
        
        Provide a thorough, well-structured response that addresses all aspects of the query.
        """
        
        response = self.llm.invoke(synthesis_prompt)
        return response.content if hasattr(response, 'content') else str(response)
    
    async def process(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Iterator[Dict[str, Any]]:
        """
        Process a query using the Deep Agent architecture.
        Yields status updates and intermediate results.
        """
        self.state = DeepAgentState(query=query)
        self.current_iteration = 0
        
        # Initialize context in memory
        if self.filesystem and context:
            self._save_to_memory(
                "/context/initial_context.json",
                json.dumps(context, indent=2, default=str)
            )
            
        try:
            # Phase 1: Planning
            if self.config.enable_planning:
                yield {"type": "status", "message": "Creating task plan..."}
                tasks = await self._create_plan(query)
                self.state.todo_list = {"tasks": tasks}
                yield {"type": "plan", "data": tasks}
                
            # Phase 2: Execution
            max_iterations = min(self.config.max_iterations, len(self.todo_list.items) if self.todo_list else 5)
            
            for iteration in range(max_iterations):
                self.current_iteration = iteration + 1
                
                # Get ready tasks
                if self.todo_list:
                    ready_tasks = self.todo_list.get_ready_tasks()
                    
                    if not ready_tasks:
                        # No more tasks ready
                        break
                        
                    # Execute the highest priority ready task
                    task = ready_tasks[0]
                    yield {"type": "status", "message": f"Executing: {task.title}"}
                    
                    success = await self._execute_task(task.id)
                    
                    yield {
                        "type": "task_complete",
                        "task": task.title,
                        "success": success
                    }
                    
                # Update state
                self.state.iterations_completed = self.current_iteration
                
                # Save progress to memory
                if self.filesystem:
                    self._save_to_memory(
                        f"/research/progress_iteration_{self.current_iteration}.json",
                        json.dumps({
                            "iteration": self.current_iteration,
                            "todo_summary": self.todo_list.get_task_summary() if self.todo_list else None,
                            "memory_summary": self.filesystem.get_summary(),
                            "sub_agents_summary": self.sub_agent_manager.get_summary() if self.sub_agent_manager else None
                        }, indent=2, default=str)
                    )
                    
            # Phase 3: Synthesis
            yield {"type": "status", "message": "Synthesizing results..."}
            final_answer = await self._synthesize_results()
            
            # Save final results
            if self.filesystem:
                self._save_to_memory(
                    "/results/final_answer.md",
                    final_answer
                )
                
                # Export entire memory for debugging/analysis
                memory_export = self.filesystem.export_to_json()
                self._save_to_memory(
                    "/results/memory_export.json",
                    memory_export
                )
                
            yield {
                "type": "answer",
                "content": final_answer,
                "metadata": {
                    "iterations": self.state.iterations_completed,
                    "tasks_completed": len([t for t in self.todo_list.items.values() if t.status == TaskStatus.COMPLETED]) if self.todo_list else 0,
                    "execution_time": (datetime.now() - self.state.start_time).total_seconds()
                }
            }
            
        except Exception as e:
            self._log(f"Processing failed: {e}", "error")
            yield {
                "type": "error",
                "message": str(e)
            }
            
        finally:
            # Cleanup
            if self.sub_agent_manager:
                self.sub_agent_manager.cleanup_completed()
                
            if self.todo_list:
                self.todo_list.clear_completed()
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get a summary of the current Deep Agent state."""
        if not self.state:
            return {"status": "Not initialized"}
            
        return {
            "query": self.state.query,
            "iterations_completed": self.state.iterations_completed,
            "execution_time": (datetime.now() - self.state.start_time).total_seconds(),
            "todo_summary": self.todo_list.get_task_summary() if self.todo_list else None,
            "memory_summary": self.filesystem.get_summary() if self.filesystem else None,
            "sub_agents_summary": self.sub_agent_manager.get_summary() if self.sub_agent_manager else None
        }
    
    def reset(self):
        """Reset the Deep Agent to initial state."""
        self.state = None
        self.current_iteration = 0
        
        if self.todo_list:
            self.todo_list = TodoList()
            
        if self.filesystem:
            self.filesystem = VirtualFileSystem()
            
        if self.sub_agent_manager:
            self.sub_agent_manager = SubAgentManager(self.filesystem)
            
        self._log("Deep Agent reset to initial state")
