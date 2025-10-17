"""Unified AI service - efficient and minimal."""
from typing import Optional, Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from app.ai.llm_factory import LLMFactory
from app.ai.config import LLMConfig


class AIService:
    """Single efficient service for all AI operations."""
    
    def __init__(self, llm_config: Optional[LLMConfig] = None):
        """Initialize with LLM."""
        self.llm = LLMFactory.create_llm(llm_config)
    
    async def chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Chat with AI.
        
        Args:
            message: User message
            system_prompt: Optional system instructions
            context: Additional context
            
        Returns:
            AI response
        """
        messages = []
        
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        
        if context:
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            messages.append(SystemMessage(content=f"Context:\n{context_str}"))
        
        messages.append(HumanMessage(content=message))
        
        response = await self.llm.ainvoke(messages)
        return response.content
    
    async def generate_ideas(
        self,
        topic: str,
        context: Optional[str] = None
    ) -> str:
        """Generate ideas on a topic."""
        prompt = f"""Generate 3-5 practical ideas about: {topic}

{f"Context: {context}" if context else ""}

Provide clear, actionable ideas:"""
        
        return await self.chat(prompt)
    
    async def enhance_content(
        self,
        content: str,
        instruction: str = "improve"
    ) -> str:
        """
        Enhance content.
        
        Args:
            content: Original content
            instruction: improve, expand, summarize, professional
        """
        prompts = {
            "improve": "Improve the following text to be clearer and more engaging:",
            "expand": "Expand the following text with more details:",
            "summarize": "Summarize the following text concisely:",
            "professional": "Rewrite the following text in a professional tone:",
        }
        
        instruction_text = prompts.get(instruction, prompts["improve"])
        prompt = f"{instruction_text}\n\n{content}\n\nEnhanced version:"
        
        return await self.chat(prompt)
    
    async def auto_fill(
        self,
        field_name: str,
        existing_data: Dict[str, Any]
    ) -> str:
        """Suggest value for a field based on existing data."""
        data_str = "\n".join([f"{k}: {v}" for k, v in existing_data.items()])
        
        prompt = f"""Based on this data, suggest a value for "{field_name}":

{data_str}

Provide only the suggested value, no explanation:"""
        
        result = await self.chat(prompt)
        return result.strip()

