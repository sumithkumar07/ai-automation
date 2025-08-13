# Enhanced Multi-Model AI Provider System
import os
import asyncio
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from groq import Groq
import httpx
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class AIProviderConfig:
    name: str
    api_key: str
    base_url: str
    models: List[str]
    max_tokens: int
    supports_streaming: bool = True
    rate_limit_rpm: int = 60

class MultiModelAIProvider:
    """Enhanced AI provider with fallback support and intelligent routing"""
    
    def __init__(self):
        self.providers = {}
        self.fallback_order = []
        self.usage_stats = {}
        self.model_capabilities = {}
        self.load_providers()
    
    def load_providers(self):
        """Load and configure all AI providers"""
        
        # GROQ Provider (existing)
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            self.providers["groq"] = AIProviderConfig(
                name="groq",
                api_key=groq_key,
                base_url="https://api.groq.com/openai/v1",
                models=["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
                max_tokens=4000,
                rate_limit_rpm=100
            )
        
        # OpenAI Provider (enhanced)
        openai_key = os.getenv("OPENAI_API_KEY") or os.getenv("EMERGENT_LLM_KEY")
        if openai_key:
            self.providers["openai"] = AIProviderConfig(
                name="openai",
                api_key=openai_key,
                base_url="https://api.openai.com/v1",
                models=["gpt-4-turbo", "gpt-4", "gpt-3.5-turbo", "gpt-4o"],
                max_tokens=4096,
                rate_limit_rpm=500
            )
        
        # Anthropic Provider (enhanced)
        anthropic_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("EMERGENT_LLM_KEY")
        if anthropic_key:
            self.providers["anthropic"] = AIProviderConfig(
                name="anthropic",
                api_key=anthropic_key,
                base_url="https://api.anthropic.com/v1",
                models=["claude-3-sonnet-20240229", "claude-3-haiku-20240307", "claude-3-opus-20240229"],
                max_tokens=4096,
                rate_limit_rpm=300
            )
        
        # Perplexity Provider (new)
        perplexity_key = os.getenv("PERPLEXITY_API_KEY") or os.getenv("EMERGENT_LLM_KEY")
        if perplexity_key:
            self.providers["perplexity"] = AIProviderConfig(
                name="perplexity",
                api_key=perplexity_key,
                base_url="https://api.perplexity.ai",
                models=["llama-3.1-sonar-large-128k-online", "llama-3.1-sonar-small-128k-online"],
                max_tokens=4096,
                rate_limit_rpm=200
            )
        
        # Set fallback order
        self.fallback_order = ["groq", "openai", "anthropic", "perplexity"]
        
        # Initialize model capabilities
        self.model_capabilities = {
            "workflow_generation": ["groq", "openai", "anthropic"],
            "code_generation": ["openai", "anthropic", "groq"],
            "data_analysis": ["openai", "anthropic", "groq"],
            "creative_writing": ["anthropic", "openai", "groq"],
            "web_search": ["perplexity"],
            "conversation": ["anthropic", "openai", "groq"],
            "optimization": ["openai", "groq", "anthropic"]
        }
        
        logger.info(f"Loaded {len(self.providers)} AI providers: {list(self.providers.keys())}")
    
    def get_best_provider(self, task_type: str = "general", model_preference: str = None) -> Optional[str]:
        """Get the best provider for a specific task"""
        if model_preference and model_preference in self.providers:
            return model_preference
        
        # Get providers capable of this task
        capable_providers = self.model_capabilities.get(task_type, self.fallback_order)
        
        # Return first available provider
        for provider in capable_providers:
            if provider in self.providers:
                return provider
        
        return None
    
    async def generate_completion(
        self, 
        messages: List[Dict[str, str]], 
        task_type: str = "general",
        model_preference: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1500,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate completion with intelligent provider selection and fallback"""
        
        provider_name = self.get_best_provider(task_type, model_preference)
        if not provider_name:
            raise Exception("No available AI providers configured")
        
        provider = self.providers[provider_name]
        attempts = 0
        max_attempts = 3
        
        while attempts < max_attempts:
            try:
                # Update usage stats
                self.usage_stats[provider_name] = self.usage_stats.get(provider_name, 0) + 1
                
                if provider_name == "groq":
                    result = await self._call_groq(provider, messages, temperature, max_tokens)
                elif provider_name == "openai":
                    result = await self._call_openai(provider, messages, temperature, max_tokens)
                elif provider_name == "anthropic":
                    result = await self._call_anthropic(provider, messages, temperature, max_tokens)
                elif provider_name == "perplexity":
                    result = await self._call_perplexity(provider, messages, temperature, max_tokens)
                else:
                    raise Exception(f"Unknown provider: {provider_name}")
                
                return {
                    "content": result,
                    "provider": provider_name,
                    "model": provider.models[0],
                    "usage": {
                        "provider": provider_name,
                        "timestamp": datetime.utcnow().isoformat(),
                        "task_type": task_type
                    }
                }
                
            except Exception as e:
                logger.warning(f"Provider {provider_name} failed (attempt {attempts + 1}): {e}")
                attempts += 1
                
                # Try fallback provider
                if attempts < max_attempts:
                    fallback_providers = [p for p in self.fallback_order if p != provider_name and p in self.providers]
                    if fallback_providers:
                        provider_name = fallback_providers[0]
                        provider = self.providers[provider_name]
                        logger.info(f"Falling back to provider: {provider_name}")
                    else:
                        break
        
        raise Exception(f"All AI providers failed after {max_attempts} attempts")
    
    async def _call_groq(self, provider: AIProviderConfig, messages: List[Dict], temperature: float, max_tokens: int) -> str:
        """Call GROQ API"""
        client = Groq(api_key=provider.api_key)
        response = client.chat.completions.create(
            model=provider.models[0],
            messages=messages,
            temperature=temperature,
            max_tokens=min(max_tokens, provider.max_tokens)
        )
        return response.choices[0].message.content
    
    async def _call_openai(self, provider: AIProviderConfig, messages: List[Dict], temperature: float, max_tokens: int) -> str:
        """Call OpenAI API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{provider.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {provider.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": provider.models[0],
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": min(max_tokens, provider.max_tokens)
                },
                timeout=60.0
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
    
    async def _call_anthropic(self, provider: AIProviderConfig, messages: List[Dict], temperature: float, max_tokens: int) -> str:
        """Call Anthropic API"""
        async with httpx.AsyncClient() as client:
            # Convert messages to Anthropic format
            system_message = ""
            anthropic_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    anthropic_messages.append(msg)
            
            response = await client.post(
                f"{provider.base_url}/messages",
                headers={
                    "x-api-key": provider.api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": provider.models[0],
                    "messages": anthropic_messages,
                    "system": system_message,
                    "temperature": temperature,
                    "max_tokens": min(max_tokens, provider.max_tokens)
                },
                timeout=60.0
            )
            response.raise_for_status()
            return response.json()["content"][0]["text"]
    
    async def _call_perplexity(self, provider: AIProviderConfig, messages: List[Dict], temperature: float, max_tokens: int) -> str:
        """Call Perplexity API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{provider.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {provider.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": provider.models[0],
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": min(max_tokens, provider.max_tokens)
                },
                timeout=60.0
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
    
    def get_provider_stats(self) -> Dict[str, Any]:
        """Get usage statistics for all providers"""
        return {
            "providers": list(self.providers.keys()),
            "usage_stats": self.usage_stats,
            "capabilities": self.model_capabilities,
            "fallback_order": self.fallback_order
        }

# Global AI provider instance
ai_provider = MultiModelAIProvider()