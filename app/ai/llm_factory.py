"""LLM factory for multi-provider support."""
from typing import Optional
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from app.ai.config import LLMProvider, LLMConfig
from app.config import settings


class LLMFactory:
    """Create LLM instances for any provider."""
    
    @staticmethod
    def create_llm(config: Optional[LLMConfig] = None) -> BaseChatModel:
        """
        Create LLM from config or settings.
        
        Args:
            config: Optional LLM configuration
            
        Returns:
            LLM instance
        """
        if config is None:
            config = LLMConfig(
                provider=LLMProvider(settings.AI_PROVIDER),
                model=settings.AI_MODEL,
                temperature=settings.AI_TEMPERATURE,
                max_tokens=settings.AI_MAX_TOKENS,
                api_key=settings.OPENAI_API_KEY or settings.ANTHROPIC_API_KEY
            )
        
        if config.provider == LLMProvider.OPENAI:
            return ChatOpenAI(
                model=config.model,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                api_key=config.api_key or settings.OPENAI_API_KEY,
            )
        
        elif config.provider == LLMProvider.ANTHROPIC:
            return ChatAnthropic(
                model=config.model,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                api_key=config.api_key or settings.ANTHROPIC_API_KEY,
            )
        
        else:
            raise ValueError(f"Unsupported provider: {config.provider}")
    
    @staticmethod
    def get_models(provider: str) -> list[str]:
        """Get available models for provider."""
        from app.ai.config import PROVIDER_MODELS
        return PROVIDER_MODELS.get(provider, [])

