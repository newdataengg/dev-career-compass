"""
LLM Client for DevCareerCompass Phase 3.
Handles interactions with various LLM providers for advanced AI features.
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional, Union
from abc import ABC, abstractmethod
import openai
from openai import AsyncOpenAI
import anthropic
from anthropic import AsyncAnthropic

from src.config.settings import settings
from src.utils.logger import get_application_logger

logger = get_application_logger(__name__)


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt."""
        pass
    
    @abstractmethod
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        pass
    
    @abstractmethod
    async def analyze_text(self, text: str, analysis_type: str) -> Dict[str, Any]:
        """Analyze text for specific insights."""
        pass


class OpenAILLMClient(BaseLLMClient):
    """OpenAI LLM client implementation."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key (defaults to environment variable)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = "gpt-4-turbo-preview"  # Default model
        self.embedding_model = "text-embedding-3-small"
        
        logger.info("OpenAI LLM client initialized")
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Generate text using OpenAI's GPT model.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters (model, temperature, max_tokens, etc.)
            
        Returns:
            Generated text response
        """
        try:
            model = kwargs.get('model', self.model)
            temperature = kwargs.get('temperature', 0.7)
            max_tokens = kwargs.get('max_tokens', 1000)
            
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating text with OpenAI: {e}")
            return f"Error: {str(e)}"
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using OpenAI's embedding model.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            response = await self.client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )
            
            return [embedding.embedding for embedding in response.data]
            
        except Exception as e:
            logger.error(f"Error generating embeddings with OpenAI: {e}")
            return []
    
    async def analyze_text(self, text: str, analysis_type: str) -> Dict[str, Any]:
        """
        Analyze text for specific insights using OpenAI.
        
        Args:
            text: Text to analyze
            analysis_type: Type of analysis to perform
            
        Returns:
            Analysis results
        """
        try:
            analysis_prompts = {
                'skills': f"""
                Analyze the following text and extract programming skills, technologies, and tools mentioned.
                Return the results as a JSON object with the following structure:
                {{
                    "skills": ["skill1", "skill2", ...],
                    "technologies": ["tech1", "tech2", ...],
                    "tools": ["tool1", "tool2", ...],
                    "confidence": 0.95
                }}
                
                Text: {text}
                """,
                
                'career_level': f"""
                Analyze the following text to determine the career level and experience of the developer.
                Return the results as a JSON object with the following structure:
                {{
                    "career_level": "junior|mid|senior|expert",
                    "years_experience": 5,
                    "confidence": 0.9,
                    "reasoning": "explanation"
                }}
                
                Text: {text}
                """,
                
                'interests': f"""
                Analyze the following text to identify the developer's interests and focus areas.
                Return the results as a JSON object with the following structure:
                {{
                    "interests": ["interest1", "interest2", ...],
                    "focus_areas": ["area1", "area2", ...],
                    "passion_topics": ["topic1", "topic2", ...]
                }}
                
                Text: {text}
                """
            }
            
            prompt = analysis_prompts.get(analysis_type, f"Analyze: {text}")
            
            response = await self.generate_text(
                prompt,
                temperature=0.3,
                max_tokens=500
            )
            
            # Try to parse JSON response
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {"error": "Failed to parse response", "raw_response": response}
                
        except Exception as e:
            logger.error(f"Error analyzing text with OpenAI: {e}")
            return {"error": str(e)}


class AnthropicLLMClient(BaseLLMClient):
    """Anthropic Claude LLM client implementation."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Anthropic client.
        
        Args:
            api_key: Anthropic API key (defaults to environment variable)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required")
        
        self.client = AsyncAnthropic(api_key=self.api_key)
        self.model = "claude-3-sonnet-20240229"
        
        logger.info("Anthropic LLM client initialized")
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Generate text using Anthropic's Claude model.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters (model, temperature, max_tokens, etc.)
            
        Returns:
            Generated text response
        """
        try:
            model = kwargs.get('model', self.model)
            temperature = kwargs.get('temperature', 0.7)
            max_tokens = kwargs.get('max_tokens', 1000)
            
            response = await self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Error generating text with Anthropic: {e}")
            return f"Error: {str(e)}"
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using Anthropic's embedding model.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            embeddings = []
            for text in texts:
                response = await self.client.messages.embed(
                    model="claude-3-sonnet-20240229",
                    input=text
                )
                embeddings.append(response.embedding)
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings with Anthropic: {e}")
            return []
    
    async def analyze_text(self, text: str, analysis_type: str) -> Dict[str, Any]:
        """
        Analyze text for specific insights using Anthropic.
        
        Args:
            text: Text to analyze
            analysis_type: Type of analysis to perform
            
        Returns:
            Analysis results
        """
        try:
            analysis_prompts = {
                'skills': f"""
                Analyze the following text and extract programming skills, technologies, and tools mentioned.
                Return the results as a JSON object with the following structure:
                {{
                    "skills": ["skill1", "skill2", ...],
                    "technologies": ["tech1", "tech2", ...],
                    "tools": ["tool1", "tool2", ...],
                    "confidence": 0.95
                }}
                
                Text: {text}
                """,
                
                'career_level': f"""
                Analyze the following text to determine the career level and experience of the developer.
                Return the results as a JSON object with the following structure:
                {{
                    "career_level": "junior|mid|senior|expert",
                    "years_experience": 5,
                    "confidence": 0.9,
                    "reasoning": "explanation"
                }}
                
                Text: {text}
                """,
                
                'interests': f"""
                Analyze the following text to identify the developer's interests and focus areas.
                Return the results as a JSON object with the following structure:
                {{
                    "interests": ["interest1", "interest2", ...],
                    "focus_areas": ["area1", "area2", ...],
                    "passion_topics": ["topic1", "topic2", ...]
                }}
                
                Text: {text}
                """
            }
            
            prompt = analysis_prompts.get(analysis_type, f"Analyze: {text}")
            
            response = await self.generate_text(
                prompt,
                temperature=0.3,
                max_tokens=500
            )
            
            # Try to parse JSON response
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {"error": "Failed to parse response", "raw_response": response}
                
        except Exception as e:
            logger.error(f"Error analyzing text with Anthropic: {e}")
            return {"error": str(e)}


class MockLLMClient(BaseLLMClient):
    """Mock LLM client for testing and development."""
    
    def __init__(self):
        """Initialize mock client."""
        logger.info("Mock LLM client initialized")
    
    async def initialize(self):
        """Initialize the mock LLM client."""
        logger.info("Mock LLM client initialized")
        return True
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Generate mock text response.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters
            
        Returns:
            Mock text response
        """
        # Enhanced mock responses based on prompt content
        if "ai trend" in prompt.lower() or "latest ai" in prompt.lower():
            return """## Latest AI Trends and Developments (2024-2025)

**🔥 Current AI Trends:**

**1. RAG (Retrieval-Augmented Generation)**
• **What it is**: Combines large language models with external knowledge bases
• **Why it's trending**: Solves hallucination issues and provides accurate, up-to-date information
• **Applications**: AI assistants, knowledge management, research tools

**2. MCP (Model Context Protocol)**
• **What it is**: Standardized protocol for AI tool integration
• **Why it's trending**: Enables AI models to use external tools and APIs seamlessly
• **Applications**: AI agents, automation, workflow integration

**3. Vector Databases & Embeddings**
• **What it is**: Specialized databases for similarity search and semantic understanding
• **Why it's trending**: Essential for RAG systems and semantic search
• **Applications**: Recommendation systems, search engines, content discovery

**4. Prompt Engineering & Optimization**
• **What it is**: Techniques for optimizing AI model interactions
• **Why it's trending**: Critical for getting the best results from LLMs
• **Applications**: AI product development, content generation, automation

**5. AI Safety & Guardrails**
• **What it is**: Systems to ensure AI behaves safely and predictably
• **Why it's trending**: Essential for responsible AI deployment
• **Applications**: Content filtering, bias detection, safety protocols

**🎯 Career Opportunities**: These trends create high demand for AI engineers with expertise in RAG systems, vector databases, and prompt engineering."""
        
        elif "skill" in prompt.lower():
            return json.dumps({
                "skills": ["Python", "JavaScript", "React"],
                "technologies": ["Docker", "AWS"],
                "tools": ["Git", "VS Code"],
                "confidence": 0.85
            })
        elif "career" in prompt.lower():
            return json.dumps({
                "career_level": "senior",
                "years_experience": 5,
                "confidence": 0.8,
                "reasoning": "Based on the complexity of projects and technologies used"
            })
        elif "interest" in prompt.lower():
            return json.dumps({
                "interests": ["Web Development", "AI/ML"],
                "focus_areas": ["Full-Stack", "Backend"],
                "passion_topics": ["Open Source", "Performance Optimization"]
            })
        else:
            return "This is a mock response for testing purposes."
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate mock embeddings.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            Mock embedding vectors
        """
        import numpy as np
        
        embeddings = []
        for text in texts:
            # Generate deterministic mock embeddings
            np.random.seed(hash(text) % (2**32 - 1))
            embedding = np.random.normal(0, 1, 384).tolist()
            embeddings.append(embedding)
        
        return embeddings
    
    async def analyze_text(self, text: str, analysis_type: str) -> Dict[str, Any]:
        """
        Analyze text with mock responses.
        
        Args:
            text: Text to analyze
            analysis_type: Type of analysis to perform
            
        Returns:
            Mock analysis results
        """
        mock_analyses = {
            'skills': {
                "skills": ["Python", "JavaScript", "React", "Node.js"],
                "technologies": ["Docker", "AWS", "MongoDB"],
                "tools": ["Git", "VS Code", "Postman"],
                "confidence": 0.9
            },
            'career_level': {
                "career_level": "senior",
                "years_experience": 6,
                "confidence": 0.85,
                "reasoning": "Based on project complexity and technology stack"
            },
            'interests': {
                "interests": ["Web Development", "AI/ML", "DevOps"],
                "focus_areas": ["Full-Stack", "Backend", "Cloud"],
                "passion_topics": ["Open Source", "Performance", "Security"]
            }
        }
        
        return mock_analyses.get(analysis_type, {"error": "Unknown analysis type"})


class LLMClientFactory:
    """Factory for creating LLM clients."""
    
    @staticmethod
    def create_client(client_type: str = "mock", **kwargs) -> BaseLLMClient:
        """
        Create an LLM client of the specified type.
        
        Args:
            client_type: Type of client ("openai", "anthropic", "mock")
            **kwargs: Additional arguments for client initialization
            
        Returns:
            LLM client instance
        """
        if client_type.lower() == "openai":
            return OpenAILLMClient(**kwargs)
        elif client_type.lower() == "anthropic":
            return AnthropicLLMClient(**kwargs)
        elif client_type.lower() == "mock":
            return MockLLMClient()
        else:
            raise ValueError(f"Unknown LLM client type: {client_type}")


# Global LLM client instance (defaults to mock for development)
try:
    if os.getenv("OPENAI_API_KEY"):
        try:
            llm_client = LLMClientFactory.create_client("openai")
            logger.info("✅ OpenAI LLM client initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI client: {e}")
            llm_client = LLMClientFactory.create_client("mock")
            logger.info("🔄 Falling back to mock LLM client")
    elif os.getenv("ANTHROPIC_API_KEY"):
        try:
            llm_client = LLMClientFactory.create_client("anthropic")
            logger.info("✅ Anthropic LLM client initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Anthropic client: {e}")
            llm_client = LLMClientFactory.create_client("mock")
            logger.info("🔄 Falling back to mock LLM client")
    else:
        llm_client = LLMClientFactory.create_client("mock")
        logger.info("ℹ️ Using mock LLM client - set OPENAI_API_KEY or ANTHROPIC_API_KEY for real LLM")
except Exception as e:
    logger.warning(f"Failed to initialize LLM client: {e}")
    llm_client = LLMClientFactory.create_client("mock")
    logger.info("🔄 Using mock LLM client as fallback") 