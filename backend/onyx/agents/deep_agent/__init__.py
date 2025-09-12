"""
Deep Agent implementation based on LangChain's deep-agents architecture.
Provides enhanced capabilities for complex, multi-step tasks with planning,
sub-agents, and virtual memory management.
"""

from onyx.agents.deep_agent.core import DeepAgent
from onyx.agents.deep_agent.memory import VirtualFileSystem
from onyx.agents.deep_agent.planning import TodoList
from onyx.agents.deep_agent.sub_agents import SubAgentManager

__all__ = [
    "DeepAgent",
    "VirtualFileSystem",
    "TodoList",
    "SubAgentManager",
]
