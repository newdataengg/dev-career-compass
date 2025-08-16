"""
Base Agent for DevCareerCompass Phase 3.
Provides the foundation for all specialized AI agents.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from src.llm.llm_client import BaseLLMClient
from src.utils.logger import get_application_logger

logger = get_application_logger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all AI agents."""
    
    def __init__(self, name: str, llm_client: BaseLLMClient, **kwargs):
        """
        Initialize the base agent.
        
        Args:
            name: Agent name
            llm_client: LLM client for text generation
            **kwargs: Additional configuration
        """
        self.name = name
        self.llm_client = llm_client
        self.config = kwargs
        self.conversation_history = []
        self.task_results = {}
        
        logger.info(f"Initialized agent: {name}")
    
    @abstractmethod
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task with the agent's specialized capabilities.
        
        Args:
            task_data: Task data to process
            
        Returns:
            Processing results
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Get the agent's capabilities.
        
        Returns:
            List of capability descriptions
        """
        pass
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generate a response using the LLM client.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters
            
        Returns:
            Generated response
        """
        try:
            response = await self.llm_client.generate_text(prompt, **kwargs)
            
            # Log the interaction
            self.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'prompt': prompt,
                'response': response,
                'agent': self.name
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response for agent {self.name}: {e}")
            return f"Error: {str(e)}"
    
    async def analyze_with_llm(self, text: str, analysis_type: str) -> Dict[str, Any]:
        """
        Analyze text using the LLM client.
        
        Args:
            text: Text to analyze
            analysis_type: Type of analysis
            
        Returns:
            Analysis results
        """
        try:
            results = await self.llm_client.analyze_text(text, analysis_type)
            
            # Store results
            self.task_results[analysis_type] = {
                'timestamp': datetime.now().isoformat(),
                'text': text,
                'results': results
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing text for agent {self.name}: {e}")
            return {"error": str(e)}
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """
        Get the agent's conversation history.
        
        Returns:
            List of conversation entries
        """
        return self.conversation_history
    
    def get_task_results(self) -> Dict[str, Any]:
        """
        Get the agent's task results.
        
        Returns:
            Dictionary of task results
        """
        return self.task_results
    
    def clear_history(self):
        """Clear conversation history and task results."""
        self.conversation_history.clear()
        self.task_results.clear()
        logger.info(f"Cleared history for agent: {self.name}")
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get information about the agent.
        
        Returns:
            Agent information dictionary
        """
        return {
            'name': self.name,
            'capabilities': self.get_capabilities(),
            'config': self.config,
            'conversation_count': len(self.conversation_history),
            'task_count': len(self.task_results)
        } 