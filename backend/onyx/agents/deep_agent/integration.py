"""
Integration layer for Deep Agent with existing chat/search flow.
"""

import asyncio
from typing import Iterator, Dict, Any, Optional, List
from collections.abc import AsyncIterator

from onyx.agents.deep_agent.core import DeepAgent, DeepAgentConfig
from onyx.chat.models import (
    AnswerStream,
    OnyxAnswerPiece, 
    StreamStopInfo,
    StreamStopReason,
    QADocsResponse,
    CitationInfo,
    MessageSpecificCitations
)
from onyx.llm.interfaces import LLM
from onyx.tools.tool import Tool
from onyx.server.query_and_chat.models import CreateChatMessageRequest
from onyx.server.query_and_chat.streaming_models import Packet
from onyx.utils.logger import setup_logger

logger = setup_logger()


class DeepAgentIntegration:
    """
    Integration layer that bridges Deep Agent with the existing Onyx chat system.
    """
    
    def __init__(self, llm: LLM, tools: List[Tool]):
        self.llm = llm
        self.tools = tools
        self.deep_agent: Optional[DeepAgent] = None
        
    def _initialize_deep_agent(self, verbose: bool = False) -> DeepAgent:
        """Initialize a Deep Agent instance."""
        config = DeepAgentConfig(
            enable_planning=True,
            enable_sub_agents=True,
            enable_memory=True,
            max_sub_agents=3,  # Conservative limit for initial implementation
            max_iterations=15,
            verbose=verbose
        )
        
        return DeepAgent(
            llm=self.llm,
            tools=self.tools,
            config=config
        )
    
    async def process_with_deep_agent(
        self,
        chat_request: CreateChatMessageRequest,
        context: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[AnswerStream]:
        """
        Process a chat request using Deep Agent and yield compatible stream objects.
        """
        # Initialize Deep Agent
        self.deep_agent = self._initialize_deep_agent(verbose=False)
        
        # Extract query and context
        query = chat_request.message
        
        # Build context from chat request
        enhanced_context = {
            "chat_session_id": str(chat_request.chat_session_id),
            "retrieval_options": chat_request.retrieval_options.model_dump() if chat_request.retrieval_options else None,
            "search_doc_ids": chat_request.search_doc_ids,
            "query_override": chat_request.query_override,
            "temperature_override": chat_request.temperature_override,
            **(context or {})
        }
        
        try:
            # Process with Deep Agent
            async for update in self._deep_agent_to_stream(query, enhanced_context):
                yield update
                
        except Exception as e:
            logger.error(f"Deep Agent processing error: {e}")
            # Fall back to error response
            yield Packet(
                error=str(e),
                stack_trace=None
            )
            
        finally:
            # Clean up
            if self.deep_agent:
                self.deep_agent.reset()
    
    async def _deep_agent_to_stream(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> AsyncIterator[AnswerStream]:
        """
        Convert Deep Agent updates to Onyx streaming format.
        """
        if not self.deep_agent:
            raise ValueError("Deep Agent not initialized")
            
        answer_pieces = []
        documents = []
        citations = []
        
        # Process query with Deep Agent
        async for update in self.deep_agent.process(query, context):
            update_type = update.get("type")
            
            if update_type == "status":
                # Send status updates as answer pieces with metadata
                yield Packet(
                    answer_piece=OnyxAnswerPiece(
                        answer_piece=f"[Deep Agent] {update.get('message', '')}\n"
                    )
                )
                
            elif update_type == "plan":
                # Send plan as a structured update
                tasks = update.get("data", [])
                plan_text = "\n📋 **Task Plan:**\n"
                for i, task in enumerate(tasks, 1):
                    plan_text += f"{i}. {task.get('title', 'Unknown task')}\n"
                    
                yield Packet(
                    answer_piece=OnyxAnswerPiece(
                        answer_piece=plan_text
                    )
                )
                
            elif update_type == "task_complete":
                # Send task completion updates
                task_name = update.get("task", "Unknown")
                success = update.get("success", False)
                status_emoji = "✅" if success else "❌"
                
                yield Packet(
                    answer_piece=OnyxAnswerPiece(
                        answer_piece=f"{status_emoji} Task completed: {task_name}\n"
                    )
                )
                
            elif update_type == "answer":
                # Send the final synthesized answer
                content = update.get("content", "")
                metadata = update.get("metadata", {})
                
                # Split answer into pieces for streaming
                # (In practice, might want to stream character by character)
                sentences = content.split('. ')
                for sentence in sentences:
                    if sentence.strip():
                        answer_piece = sentence + ('. ' if not sentence.endswith('.') else ' ')
                        answer_pieces.append(answer_piece)
                        
                        yield Packet(
                            answer_piece=OnyxAnswerPiece(
                                answer_piece=answer_piece
                            )
                        )
                        
                # Add metadata summary
                summary = f"\n\n---\n📊 **Deep Agent Summary:**\n"
                summary += f"• Iterations: {metadata.get('iterations', 0)}\n"
                summary += f"• Tasks completed: {metadata.get('tasks_completed', 0)}\n"
                summary += f"• Execution time: {metadata.get('execution_time', 0):.2f}s\n"
                
                yield Packet(
                    answer_piece=OnyxAnswerPiece(
                        answer_piece=summary
                    )
                )
                
            elif update_type == "error":
                # Handle errors
                error_msg = update.get("message", "Unknown error")
                logger.error(f"Deep Agent error: {error_msg}")
                
                yield Packet(
                    error=error_msg,
                    stack_trace=None
                )
                
        # Send completion signal
        yield Packet(
            stop_info=StreamStopInfo(
                stop_reason=StreamStopReason.FINISHED
            )
        )
    
    def should_use_deep_agent(
        self,
        chat_request: CreateChatMessageRequest,
        query_complexity: Optional[float] = None
    ) -> bool:
        """
        Determine whether to use Deep Agent based on request and query characteristics.
        """
        # Check if explicitly requested
        if chat_request.use_deep_agent:
            return True
            
        # Check if agentic search is requested (similar to deep agent)
        if chat_request.use_agentic_search:
            return True
            
        # Auto-detection based on query characteristics
        query = chat_request.message.lower()
        
        # Keywords that suggest complex, multi-step tasks
        deep_keywords = [
            "deep dive", "comprehensive", "detailed analysis", "research",
            "investigate", "explore thoroughly", "multiple aspects",
            "step by step", "complete guide", "everything about",
            "compare and contrast", "pros and cons", "full breakdown"
        ]
        
        # Check for deep keywords
        for keyword in deep_keywords:
            if keyword in query:
                logger.info(f"Auto-enabling Deep Agent due to keyword: {keyword}")
                return True
                
        # Check query length (longer queries might benefit from deep agent)
        if len(query.split()) > 50:
            logger.info("Auto-enabling Deep Agent due to query length")
            return True
            
        # Check if query contains multiple questions
        question_marks = query.count('?')
        if question_marks > 2:
            logger.info(f"Auto-enabling Deep Agent due to multiple questions ({question_marks})")
            return True
            
        # Use complexity score if provided
        if query_complexity and query_complexity > 0.7:
            logger.info(f"Auto-enabling Deep Agent due to complexity score: {query_complexity}")
            return True
            
        return False


async def stream_with_deep_agent(
    chat_request: CreateChatMessageRequest,
    llm: LLM,
    tools: List[Tool],
    context: Optional[Dict[str, Any]] = None,
    force_deep_agent: bool = False
) -> AsyncIterator[AnswerStream]:
    """
    Convenience function to stream chat responses using Deep Agent.
    
    Args:
        chat_request: The chat message request
        llm: Language model instance
        tools: Available tools
        context: Additional context
        force_deep_agent: Force use of deep agent regardless of auto-detection
        
    Yields:
        Stream of answer packets
    """
    integration = DeepAgentIntegration(llm, tools)
    
    # Check if Deep Agent should be used
    if force_deep_agent or integration.should_use_deep_agent(chat_request):
        logger.info("Using Deep Agent for query processing")
        async for packet in integration.process_with_deep_agent(chat_request, context):
            yield packet
    else:
        # Return None to indicate standard flow should be used
        logger.info("Using standard chat flow (Deep Agent not needed)")
        return
