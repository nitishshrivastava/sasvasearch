"""
Planning tools for Deep Agent, including the TODO list tool.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

from onyx.utils.logger import setup_logger

logger = setup_logger()


class TaskStatus(Enum):
    """Status of a task in the TODO list."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Priority levels for tasks."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class TodoItem(BaseModel):
    """Individual TODO item with metadata."""
    id: str = Field(description="Unique identifier for the task")
    title: str = Field(description="Short description of the task")
    description: Optional[str] = Field(None, description="Detailed task description")
    status: TaskStatus = Field(TaskStatus.PENDING, description="Current task status")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="Task priority")
    dependencies: List[str] = Field(default_factory=list, description="IDs of tasks this depends on")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    assigned_to: Optional[str] = Field(None, description="Sub-agent ID if assigned")
    notes: List[str] = Field(default_factory=list, description="Additional notes")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class TodoList:
    """
    TODO list planning tool for Deep Agent.
    This is a no-op tool that helps with context engineering and task tracking.
    """
    
    def __init__(self):
        self.items: Dict[str, TodoItem] = {}
        self.next_id = 1
        
    def add_task(
        self,
        title: str,
        description: Optional[str] = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        dependencies: Optional[List[str]] = None
    ) -> TodoItem:
        """Add a new task to the TODO list."""
        task_id = f"task_{self.next_id}"
        self.next_id += 1
        
        task = TodoItem(
            id=task_id,
            title=title,
            description=description,
            priority=priority,
            dependencies=dependencies or []
        )
        
        self.items[task_id] = task
        logger.debug(f"Added task {task_id}: {title}")
        return task
    
    def update_task_status(self, task_id: str, status: TaskStatus) -> Optional[TodoItem]:
        """Update the status of a task."""
        if task_id not in self.items:
            logger.warning(f"Task {task_id} not found")
            return None
            
        task = self.items[task_id]
        task.status = status
        task.updated_at = datetime.now()
        
        if status == TaskStatus.COMPLETED:
            task.completed_at = datetime.now()
            
        logger.debug(f"Updated task {task_id} status to {status.value}")
        return task
    
    def add_note_to_task(self, task_id: str, note: str) -> Optional[TodoItem]:
        """Add a note to a task."""
        if task_id not in self.items:
            logger.warning(f"Task {task_id} not found")
            return None
            
        task = self.items[task_id]
        task.notes.append(note)
        task.updated_at = datetime.now()
        return task
    
    def assign_task(self, task_id: str, agent_id: str) -> Optional[TodoItem]:
        """Assign a task to a sub-agent."""
        if task_id not in self.items:
            logger.warning(f"Task {task_id} not found")
            return None
            
        task = self.items[task_id]
        task.assigned_to = agent_id
        task.updated_at = datetime.now()
        logger.debug(f"Assigned task {task_id} to agent {agent_id}")
        return task
    
    def get_ready_tasks(self) -> List[TodoItem]:
        """Get tasks that are ready to be executed (no pending dependencies)."""
        ready_tasks = []
        
        for task in self.items.values():
            if task.status != TaskStatus.PENDING:
                continue
                
            # Check if all dependencies are completed
            dependencies_met = all(
                self.items.get(dep_id, TodoItem(id="", title="", status=TaskStatus.COMPLETED)).status == TaskStatus.COMPLETED
                for dep_id in task.dependencies
            )
            
            if dependencies_met:
                ready_tasks.append(task)
                
        # Sort by priority (highest first)
        ready_tasks.sort(key=lambda t: t.priority.value, reverse=True)
        return ready_tasks
    
    def get_task_summary(self) -> Dict[str, Any]:
        """Get a summary of the TODO list status."""
        status_counts = {status: 0 for status in TaskStatus}
        for task in self.items.values():
            status_counts[task.status] += 1
            
        return {
            "total_tasks": len(self.items),
            "status_breakdown": {s.value: c for s, c in status_counts.items()},
            "ready_tasks": len(self.get_ready_tasks()),
            "completion_rate": (
                status_counts[TaskStatus.COMPLETED] / len(self.items) * 100
                if self.items else 0
            )
        }
    
    def to_markdown(self) -> str:
        """Export TODO list as markdown for display."""
        lines = ["# TODO List\n"]
        
        # Group by status
        for status in TaskStatus:
            tasks_in_status = [t for t in self.items.values() if t.status == status]
            if not tasks_in_status:
                continue
                
            lines.append(f"\n## {status.value.replace('_', ' ').title()}\n")
            
            for task in tasks_in_status:
                checkbox = "x" if task.status == TaskStatus.COMPLETED else " "
                priority_marker = "!" * task.priority.value
                lines.append(f"- [{checkbox}] {priority_marker} {task.title}")
                
                if task.description:
                    lines.append(f"  - {task.description}")
                    
                if task.assigned_to:
                    lines.append(f"  - Assigned to: {task.assigned_to}")
                    
                if task.dependencies:
                    deps = ", ".join(task.dependencies)
                    lines.append(f"  - Dependencies: {deps}")
                    
                if task.notes:
                    lines.append("  - Notes:")
                    for note in task.notes:
                        lines.append(f"    - {note}")
                        
        # Add summary
        summary = self.get_task_summary()
        lines.append(f"\n---\n**Summary**: {summary['total_tasks']} tasks, "
                    f"{summary['completion_rate']:.1f}% complete")
        
        return "\n".join(lines)
    
    def clear_completed(self):
        """Remove completed tasks from the list."""
        completed_ids = [
            task_id for task_id, task in self.items.items()
            if task.status == TaskStatus.COMPLETED
        ]
        
        for task_id in completed_ids:
            del self.items[task_id]
            
        logger.debug(f"Cleared {len(completed_ids)} completed tasks")
