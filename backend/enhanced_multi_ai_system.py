"""
🤖 Enhanced Multi-Provider AI System
Non-disruptive AI enhancement that adds OpenAI, Claude, Gemini while keeping GROQ as default
"""
import os
import asyncio
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import logging
from datetime import datetime
from dataclasses import dataclass
from cachetools import TTLCache

# AI Provider Imports
try:
    from groq import Groq
except ImportError:
    Groq = None

try:
    from emergentintegrations import AI
except ImportError:
    AI = None

try:
    import openai
except ImportError:
    openai = None

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

logger = logging.getLogger(__name__)

class AIProvider(str, Enum):
    """Available AI providers"""
    GROQ = "groq"           # Default - existing
    OPENAI = "openai"       # New
    CLAUDE = "claude"       # New  
    GEMINI = "gemini"       # New
    EMERGENT = "emergent"   # Unified key system

class AITask(str, Enum):
    """AI task types for optimal provider selection"""
    WORKFLOW_GENERATION = "workflow_generation"
    INTEGRATION_SUGGESTIONS = "integration_suggestions"
    CODE_GENERATION = "code_generation"
    ANALYSIS = "analysis"
    CHAT = "chat"
    OPTIMIZATION = "optimization"

@dataclass
class AIResponse:
    """Standardized AI response format"""
    content: str
    provider: AIProvider
    model: str
    confidence: float = 0.0
    tokens_used: int = 0
    response_time: float = 0.0
    metadata: Dict[str, Any] = None

@dataclass
class AIProviderConfig:
    """Configuration for each AI provider"""
    name: AIProvider
    models: List[str]
    strengths: List[AITask]
    max_tokens: int
    enabled: bool = True
    priority: int = 1  # Lower is higher priority

class EnhancedMultiAISystem:
    """
    Enhanced AI System with multiple providers
    - Keeps GROQ as default (backward compatible)
    - Adds OpenAI, Claude, Gemini as options
    - Smart provider selection based on task
    - Caching for performance
    - Fallback mechanisms
    """
    
    def __init__(self):
        self.providers = {}
        self.cache = TTLCache(maxsize=1000, ttl=1800)  # 30 min cache
        self.provider_configs = self._setup_provider_configs()
        self._initialize_providers()
    
    def _setup_provider_configs(self) -> Dict[AIProvider, AIProviderConfig]:
        """Setup provider configurations"""
        return {
            AIProvider.GROQ: AIProviderConfig(
                name=AIProvider.GROQ,
                models=["llama-3.1-8b-instant", "llama-3.1-70b-versatile"],
                strengths=[AITask.WORKFLOW_GENERATION, AITask.CHAT, AITask.ANALYSIS],
                max_tokens=8192,
                priority=1  # Highest priority (default)
            ),
            AIProvider.EMERGENT: AIProviderConfig(
                name=AIProvider.EMERGENT,
                models=["gpt-4o-mini", "claude-3-haiku", "gemini-1.5-flash"],
                strengths=[AITask.WORKFLOW_GENERATION, AITask.INTEGRATION_SUGGESTIONS],
                max_tokens=8192,
                priority=2
            ),
            AIProvider.OPENAI: AIProviderConfig(
                name=AIProvider.OPENAI,
                models=["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
                strengths=[AITask.CODE_GENERATION, AITask.OPTIMIZATION],
                max_tokens=16384,
                priority=3
            ),
            AIProvider.CLAUDE: AIProviderConfig(
                name=AIProvider.CLAUDE,
                models=["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
                strengths=[AITask.ANALYSIS, AITask.OPTIMIZATION],
                max_tokens=8192,
                priority=4
            ),
            AIProvider.GEMINI: AIProviderConfig(
                name=AIProvider.GEMINI,
                models=["gemini-1.5-flash", "gemini-1.5-pro"],
                strengths=[AITask.INTEGRATION_SUGGESTIONS, AITask.ANALYSIS],
                max_tokens=8192,
                priority=5
            )
        }
    
    def _initialize_providers(self):
        """Initialize available AI providers"""
        # GROQ (existing - highest priority)
        if Groq and os.getenv("GROQ_API_KEY"):
            self.providers[AIProvider.GROQ] = Groq(api_key=os.getenv("GROQ_API_KEY"))
            logger.info("✅ GROQ AI initialized (default provider)")
        
        # Emergent Integration (unified key system)
        if AI and os.getenv("EMERGENT_LLM_KEY"):
            self.providers[AIProvider.EMERGENT] = AI(api_key=os.getenv("EMERGENT_LLM_KEY"))
            logger.info("✅ Emergent AI initialized (multi-provider)")
        
        # OpenAI
        if openai and os.getenv("OPENAI_API_KEY"):
            self.providers[AIProvider.OPENAI] = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            logger.info("✅ OpenAI initialized")
        
        # Claude
        if anthropic and os.getenv("ANTHROPIC_API_KEY"):
            self.providers[AIProvider.CLAUDE] = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            logger.info("✅ Claude AI initialized")
        
        # Gemini
        if genai and os.getenv("GOOGLE_API_KEY"):
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            self.providers[AIProvider.GEMINI] = genai
            logger.info("✅ Gemini AI initialized")
    
    def get_available_providers(self) -> List[Dict[str, Any]]:
        """Get list of available providers with metadata"""
        available = []
        for provider, config in self.provider_configs.items():
            if provider in self.providers:
                available.append({
                    "name": provider.value,
                    "display_name": provider.value.replace("_", " ").title(),
                    "models": config.models,
                    "strengths": [task.value for task in config.strengths],
                    "max_tokens": config.max_tokens,
                    "priority": config.priority
                })
        
        return sorted(available, key=lambda x: x["priority"])
    
    def _select_optimal_provider(self, task: AITask, preferred_provider: Optional[AIProvider] = None) -> AIProvider:
        """Select optimal provider based on task and availability"""
        if preferred_provider and preferred_provider in self.providers:
            return preferred_provider
        
        # Find providers that excel at this task
        suitable_providers = []
        for provider, config in self.provider_configs.items():
            if provider in self.providers and task in config.strengths:
                suitable_providers.append((provider, config.priority))
        
        if suitable_providers:
            # Return provider with highest priority (lowest number)
            return min(suitable_providers, key=lambda x: x[1])[0]
        
        # Fallback to GROQ (default) or first available
        if AIProvider.GROQ in self.providers:
            return AIProvider.GROQ
        
        return list(self.providers.keys())[0] if self.providers else None
    
    async def generate_completion(
        self,
        prompt: str,
        task: AITask = AITask.CHAT,
        provider: Optional[AIProvider] = None,
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> AIResponse:
        """
        Generate AI completion with smart provider selection
        Backward compatible with existing GROQ implementation
        """
        # Cache key for performance
        cache_key = f"{task.value}:{provider}:{hash(prompt[:100])}"
        if cache_key in self.cache:
            logger.info(f"🚀 Cache hit for {task.value}")
            return self.cache[cache_key]
        
        start_time = datetime.now()
        selected_provider = self._select_optimal_provider(task, provider)
        
        if not selected_provider:
            raise ValueError("No AI providers available")
        
        try:
            response = await self._call_provider(
                provider=selected_provider,
                prompt=prompt,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Cache successful responses
            self.cache[cache_key] = response
            
            logger.info(f"✅ AI completion via {selected_provider.value}: {len(response.content)} chars")
            return response
            
        except Exception as e:
            logger.error(f"❌ AI generation failed with {selected_provider.value}: {e}")
            
            # Fallback to GROQ if available and not already tried
            if selected_provider != AIProvider.GROQ and AIProvider.GROQ in self.providers:
                return await self._call_provider(AIProvider.GROQ, prompt, model, max_tokens, temperature)
            
            raise e
    
    async def _call_provider(
        self,
        provider: AIProvider,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> AIResponse:
        """Call specific AI provider"""
        start_time = datetime.now()
        
        try:
            if provider == AIProvider.GROQ:
                return await self._call_groq(prompt, model, max_tokens, temperature, start_time)
            elif provider == AIProvider.EMERGENT:
                return await self._call_emergent(prompt, model, max_tokens, temperature, start_time)
            elif provider == AIProvider.OPENAI:
                return await self._call_openai(prompt, model, max_tokens, temperature, start_time)
            elif provider == AIProvider.CLAUDE:
                return await self._call_claude(prompt, model, max_tokens, temperature, start_time)
            elif provider == AIProvider.GEMINI:
                return await self._call_gemini(prompt, model, max_tokens, temperature, start_time)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
                
        except Exception as e:
            logger.error(f"Provider {provider.value} failed: {e}")
            raise
    
    async def _call_groq(self, prompt: str, model: str, max_tokens: int, temperature: float, start_time: datetime) -> AIResponse:
        """Call GROQ AI (existing implementation preserved)"""
        client = self.providers[AIProvider.GROQ]
        if not model:
            model = "llama-3.1-8b-instant"
        
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        
        response_time = (datetime.now() - start_time).total_seconds()
        
        return AIResponse(
            content=response.choices[0].message.content,
            provider=AIProvider.GROQ,
            model=model,
            confidence=0.85,  # GROQ default confidence
            tokens_used=response.usage.total_tokens if response.usage else 0,
            response_time=response_time
        )
    
    async def _call_emergent(self, prompt: str, model: str, max_tokens: int, temperature: float, start_time: datetime) -> AIResponse:
        """Call Emergent AI (unified key system)"""
        client = self.providers[AIProvider.EMERGENT]
        if not model:
            model = "gpt-4o-mini"
        
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        response_time = (datetime.now() - start_time).total_seconds()
        
        return AIResponse(
            content=response.choices[0].message.content,
            provider=AIProvider.EMERGENT,
            model=model,
            confidence=0.90,
            tokens_used=getattr(response, 'usage', {}).get('total_tokens', 0),
            response_time=response_time
        )
    
    async def _call_openai(self, prompt: str, model: str, max_tokens: int, temperature: float, start_time: datetime) -> AIResponse:
        """Call OpenAI"""
        client = self.providers[AIProvider.OPENAI]
        if not model:
            model = "gpt-4o-mini"
        
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        response_time = (datetime.now() - start_time).total_seconds()
        
        return AIResponse(
            content=response.choices[0].message.content,
            provider=AIProvider.OPENAI,
            model=model,
            confidence=0.92,
            tokens_used=response.usage.total_tokens,
            response_time=response_time
        )
    
    async def _call_claude(self, prompt: str, model: str, max_tokens: int, temperature: float, start_time: datetime) -> AIResponse:
        """Call Claude AI"""
        client = self.providers[AIProvider.CLAUDE]
        if not model:
            model = "claude-3-5-sonnet-20241022"
        
        response = await client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_time = (datetime.now() - start_time).total_seconds()
        
        return AIResponse(
            content=response.content[0].text,
            provider=AIProvider.CLAUDE,
            model=model,
            confidence=0.94,
            tokens_used=response.usage.input_tokens + response.usage.output_tokens,
            response_time=response_time
        )
    
    async def _call_gemini(self, prompt: str, model: str, max_tokens: int, temperature: float, start_time: datetime) -> AIResponse:
        """Call Gemini AI"""
        genai_client = self.providers[AIProvider.GEMINI]
        if not model:
            model = "gemini-1.5-flash"
        
        model_instance = genai_client.GenerativeModel(model)
        response = await model_instance.generate_content_async(
            prompt,
            generation_config={
                "max_output_tokens": max_tokens,
                "temperature": temperature
            }
        )
        
        response_time = (datetime.now() - start_time).total_seconds()
        
        return AIResponse(
            content=response.text,
            provider=AIProvider.GEMINI,
            model=model,
            confidence=0.88,
            tokens_used=response.usage_metadata.total_token_count if response.usage_metadata else 0,
            response_time=response_time
        )
    
    # Backward Compatible Methods (existing API preserved)
    async def generate_workflow(self, description: str, provider: Optional[str] = None) -> Dict[str, Any]:
        """Generate workflow - backward compatible with existing API"""
        ai_provider = AIProvider(provider) if provider else None
        
        response = await self.generate_completion(
            prompt=f"Generate a detailed workflow automation for: {description}",
            task=AITask.WORKFLOW_GENERATION,
            provider=ai_provider,
            max_tokens=2000
        )
        
        return {
            "workflow": response.content,
            "provider": response.provider.value,
            "model": response.model,
            "confidence": response.confidence,
            "metadata": {
                "tokens_used": response.tokens_used,
                "response_time": response.response_time
            }
        }
    
    async def suggest_integrations(self, context: str, provider: Optional[str] = None) -> List[Dict[str, Any]]:
        """Suggest integrations - backward compatible"""
        ai_provider = AIProvider(provider) if provider else None
        
        response = await self.generate_completion(
            prompt=f"Suggest relevant integrations for workflow context: {context}",
            task=AITask.INTEGRATION_SUGGESTIONS,
            provider=ai_provider,
            max_tokens=1500
        )
        
        # Parse suggestions (simplified for demo)
        suggestions = []
        lines = response.content.split('\n')
        for line in lines:
            if line.strip() and ('integration' in line.lower() or 'app' in line.lower()):
                suggestions.append({
                    "name": line.strip(),
                    "relevance": 0.8,
                    "provider": response.provider.value
                })
        
        return suggestions[:5]  # Return top 5
    
    async def chat(self, message: str, context: List[Dict] = None, provider: Optional[str] = None) -> Dict[str, Any]:
        """AI Chat - backward compatible"""
        ai_provider = AIProvider(provider) if provider else None
        
        # Build context-aware prompt
        prompt = message
        if context:
            context_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in context[-3:]])
            prompt = f"Context:\n{context_str}\n\nUser: {message}"
        
        response = await self.generate_completion(
            prompt=prompt,
            task=AITask.CHAT,
            provider=ai_provider,
            max_tokens=1000
        )
        
        return {
            "response": response.content,
            "provider": response.provider.value,
            "model": response.model,
            "confidence": response.confidence
        }

# Global instance (singleton pattern for compatibility)
enhanced_ai_system = None

def get_enhanced_ai_system() -> EnhancedMultiAISystem:
    """Get global enhanced AI system instance"""
    global enhanced_ai_system
    if enhanced_ai_system is None:
        enhanced_ai_system = EnhancedMultiAISystem()
    return enhanced_ai_system

# Backward Compatible Functions (preserve existing API)
async def generate_workflow_with_ai(description: str, provider: Optional[str] = None) -> Dict[str, Any]:
    """Backward compatible workflow generation"""
    ai_system = get_enhanced_ai_system()
    return await ai_system.generate_workflow(description, provider)

async def suggest_integrations_with_ai(context: str, provider: Optional[str] = None) -> List[Dict[str, Any]]:
    """Backward compatible integration suggestions"""
    ai_system = get_enhanced_ai_system()
    return await ai_system.suggest_integrations(context, provider)

async def chat_with_ai(message: str, context: List[Dict] = None, provider: Optional[str] = None) -> Dict[str, Any]:
    """Backward compatible AI chat"""
    ai_system = get_enhanced_ai_system()
    return await ai_system.chat(message, context, provider)