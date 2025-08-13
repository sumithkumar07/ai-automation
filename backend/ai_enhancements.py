"""
AI Enhancements - Advanced AI Capabilities and Multi-LLM Support
Expanding AI features with multiple providers and sophisticated capabilities
"""

import os
import asyncio
import json
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime

class AIProviderManager:
    """Manage multiple AI providers with fallback and load balancing"""
    
    def __init__(self):
        self.providers = {
            "openai": {
                "api_key": os.getenv("OPENAI_API_KEY"),
                "base_url": "https://api.openai.com/v1",
                "models": {
                    "gpt-4": {"context": 8192, "cost_per_1k": 0.03},
                    "gpt-4-turbo": {"context": 128000, "cost_per_1k": 0.01},
                    "gpt-3.5-turbo": {"context": 16385, "cost_per_1k": 0.001}
                }
            },
            "anthropic": {
                "api_key": os.getenv("ANTHROPIC_API_KEY"),
                "base_url": "https://api.anthropic.com/v1",
                "models": {
                    "claude-3-opus": {"context": 200000, "cost_per_1k": 0.015},
                    "claude-3-sonnet": {"context": 200000, "cost_per_1k": 0.003},
                    "claude-3-haiku": {"context": 200000, "cost_per_1k": 0.00025}
                }
            },
            "groq": {
                "api_key": os.getenv("GROQ_API_KEY"),
                "base_url": "https://api.groq.com/openai/v1",
                "models": {
                    "llama-3.3-70b-versatile": {"context": 32768, "cost_per_1k": 0.0008},
                    "llama-3.1-8b-instant": {"context": 131072, "cost_per_1k": 0.0001},
                    "mixtral-8x7b-32768": {"context": 32768, "cost_per_1k": 0.0006}
                }
            },
            "perplexity": {
                "api_key": os.getenv("PERPLEXITY_API_KEY"),
                "base_url": "https://api.perplexity.ai",
                "models": {
                    "sonar-small-online": {"context": 12000, "cost_per_1k": 0.0002},
                    "sonar-medium-online": {"context": 12000, "cost_per_1k": 0.0006},
                    "sonar-large-online": {"context": 12000, "cost_per_1k": 0.002}
                }
            },
            "mistral": {
                "api_key": os.getenv("MISTRAL_API_KEY"),
                "base_url": "https://api.mistral.ai/v1",
                "models": {
                    "mistral-large-latest": {"context": 128000, "cost_per_1k": 0.008},
                    "mistral-medium": {"context": 32000, "cost_per_1k": 0.0025},
                    "mistral-small": {"context": 32000, "cost_per_1k": 0.001}
                }
            },
            "cohere": {
                "api_key": os.getenv("COHERE_API_KEY"),
                "base_url": "https://api.cohere.ai/v1",
                "models": {
                    "command": {"context": 4096, "cost_per_1k": 0.0015},
                    "command-light": {"context": 4096, "cost_per_1k": 0.0003},
                    "command-nightly": {"context": 128000, "cost_per_1k": 0.015}
                }
            }
        }
        
    async def get_best_provider(self, requirements: Dict[str, Any]) -> str:
        """Select the best provider based on requirements"""
        context_needed = requirements.get("context_length", 4000)
        budget = requirements.get("max_cost_per_1k", 0.01)
        speed_priority = requirements.get("speed_priority", False)
        
        best_providers = []
        
        for provider, config in self.providers.items():
            if not config["api_key"]:
                continue
                
            for model, specs in config["models"].items():
                if (specs["context"] >= context_needed and 
                    specs["cost_per_1k"] <= budget):
                    score = 100 - specs["cost_per_1k"] * 1000  # Lower cost = higher score
                    if speed_priority and provider == "groq":
                        score += 50  # GROQ bonus for speed
                    best_providers.append((provider, model, score))
        
        if best_providers:
            best_providers.sort(key=lambda x: x[2], reverse=True)
            return best_providers[0][0], best_providers[0][1]
        
        return "groq", "llama-3.3-70b-versatile"  # Default fallback

class AdvancedAICapabilities:
    """Advanced AI capabilities for workflow automation"""
    
    def __init__(self, provider_manager: AIProviderManager):
        self.provider_manager = provider_manager
        
    async def generate_code(self, prompt: str, language: str = "python", 
                          framework: str = None, style: str = "clean") -> Dict[str, Any]:
        """Generate code with AI"""
        system_prompt = f"""You are an expert {language} developer. Generate clean, production-ready code.
        
        Requirements:
        - Language: {language}
        - Framework: {framework or 'standard library'}
        - Style: {style}
        - Include error handling
        - Add comprehensive comments
        - Follow best practices
        
        Return the code with explanations."""
        
        provider, model = await self.provider_manager.get_best_provider({
            "context_length": 8000,
            "max_cost_per_1k": 0.01
        })
        
        response = await self._make_ai_request(provider, model, system_prompt, prompt)
        
        return {
            "code": response,
            "language": language,
            "framework": framework,
            "provider": provider,
            "model": model,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def analyze_sentiment(self, text: str, detailed: bool = False) -> Dict[str, Any]:
        """Analyze sentiment with AI"""
        system_prompt = """You are a sentiment analysis expert. Analyze the sentiment of the given text.
        
        Return a JSON object with:
        - sentiment: "positive", "negative", or "neutral"
        - confidence: 0.0 to 1.0
        - emotions: array of detected emotions
        - key_phrases: important phrases that influenced the sentiment
        """
        
        provider, model = await self.provider_manager.get_best_provider({
            "context_length": 4000,
            "max_cost_per_1k": 0.005,
            "speed_priority": True
        })
        
        response = await self._make_ai_request(provider, model, system_prompt, text)
        
        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            # Fallback parsing
            result = {
                "sentiment": "neutral",
                "confidence": 0.5,
                "emotions": [],
                "key_phrases": []
            }
        
        return {
            **result,
            "provider": provider,
            "model": model,
            "analyzed_at": datetime.utcnow().isoformat()
        }
    
    async def extract_entities(self, text: str, entity_types: List[str] = None) -> Dict[str, Any]:
        """Extract entities from text with AI"""
        entity_types = entity_types or ["PERSON", "ORGANIZATION", "LOCATION", "DATE", "EMAIL", "PHONE"]
        
        system_prompt = f"""Extract named entities from the text. Look for these types:
        {', '.join(entity_types)}
        
        Return a JSON object with:
        - entities: array of objects with 'text', 'type', 'start', 'end', 'confidence'
        - summary: brief summary of key entities found
        """
        
        provider, model = await self.provider_manager.get_best_provider({
            "context_length": 8000,
            "max_cost_per_1k": 0.01
        })
        
        response = await self._make_ai_request(provider, model, system_prompt, text)
        
        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            result = {"entities": [], "summary": "No entities extracted"}
        
        return {
            **result,
            "provider": provider,
            "model": model,
            "extracted_at": datetime.utcnow().isoformat()
        }
    
    async def summarize_content(self, content: str, style: str = "concise", 
                               length: str = "medium") -> Dict[str, Any]:
        """Summarize content with AI"""
        length_guide = {
            "short": "1-2 sentences",
            "medium": "1-2 paragraphs", 
            "long": "3-4 paragraphs"
        }
        
        system_prompt = f"""Create a {style} summary of the content.
        
        Requirements:
        - Length: {length_guide.get(length, '1-2 paragraphs')}
        - Style: {style}
        - Capture key points and main ideas
        - Maintain original tone where appropriate
        """
        
        provider, model = await self.provider_manager.get_best_provider({
            "context_length": len(content) + 2000,
            "max_cost_per_1k": 0.008
        })
        
        summary = await self._make_ai_request(provider, model, system_prompt, content)
        
        return {
            "summary": summary,
            "original_length": len(content),
            "summary_length": len(summary),
            "compression_ratio": len(summary) / len(content),
            "style": style,
            "length": length,
            "provider": provider,
            "model": model,
            "summarized_at": datetime.utcnow().isoformat()
        }
    
    async def classify_content(self, content: str, categories: List[str], 
                             multi_label: bool = False) -> Dict[str, Any]:
        """Classify content into categories with AI"""
        system_prompt = f"""Classify the content into one or more of these categories:
        {', '.join(categories)}
        
        {'Select multiple categories if applicable.' if multi_label else 'Select only one category.'}
        
        Return a JSON object with:
        - predicted_categories: array of category names
        - confidence_scores: object with category: confidence pairs
        - reasoning: brief explanation of the classification
        """
        
        provider, model = await self.provider_manager.get_best_provider({
            "context_length": len(content) + 1000,
            "max_cost_per_1k": 0.005
        })
        
        response = await self._make_ai_request(provider, model, system_prompt, content)
        
        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            result = {
                "predicted_categories": [categories[0]] if categories else [],
                "confidence_scores": {},
                "reasoning": "Classification failed"
            }
        
        return {
            **result,
            "available_categories": categories,
            "multi_label": multi_label,
            "provider": provider,
            "model": model,
            "classified_at": datetime.utcnow().isoformat()
        }
    
    async def detect_language(self, text: str) -> Dict[str, Any]:
        """Detect language of text with AI"""
        system_prompt = """Detect the language of the given text.
        
        Return a JSON object with:
        - language: ISO 639-1 language code (e.g., 'en', 'es', 'fr')
        - language_name: full language name
        - confidence: 0.0 to 1.0
        - script: writing script used (e.g., 'Latin', 'Cyrillic')
        """
        
        provider, model = await self.provider_manager.get_best_provider({
            "context_length": 2000,
            "max_cost_per_1k": 0.002,
            "speed_priority": True
        })
        
        response = await self._make_ai_request(provider, model, system_prompt, text)
        
        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            result = {
                "language": "en",
                "language_name": "English",
                "confidence": 0.5,
                "script": "Latin"
            }
        
        return {
            **result,
            "provider": provider,
            "model": model,
            "detected_at": datetime.utcnow().isoformat()
        }
    
    async def optimize_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and optimize workflow with AI"""
        system_prompt = """You are a workflow optimization expert. Analyze the workflow and provide optimization suggestions.
        
        Look for:
        - Bottlenecks and inefficiencies
        - Redundant steps
        - Missing error handling
        - Performance improvements
        - Better node arrangements
        - Resource optimization
        
        Return a JSON object with:
        - optimization_score: 0-100 (current efficiency)
        - suggestions: array of specific improvements
        - estimated_improvement: percentage improvement possible
        - priority_fixes: top 3 most important changes
        - alternative_approaches: different ways to achieve the same goal
        """
        
        workflow_str = json.dumps(workflow_data, indent=2)
        
        provider, model = await self.provider_manager.get_best_provider({
            "context_length": len(workflow_str) + 3000,
            "max_cost_per_1k": 0.015
        })
        
        response = await self._make_ai_request(provider, model, system_prompt, workflow_str)
        
        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            result = {
                "optimization_score": 75,
                "suggestions": ["Review workflow structure"],
                "estimated_improvement": 15,
                "priority_fixes": ["Add error handling"],
                "alternative_approaches": []
            }
        
        return {
            **result,
            "workflow_id": workflow_data.get("id"),
            "node_count": len(workflow_data.get("nodes", [])),
            "connection_count": len(workflow_data.get("connections", [])),
            "provider": provider,
            "model": model,
            "analyzed_at": datetime.utcnow().isoformat()
        }
    
    async def _make_ai_request(self, provider: str, model: str, system_prompt: str, 
                              user_prompt: str) -> str:
        """Make request to AI provider"""
        config = self.provider_manager.providers[provider]
        
        if not config["api_key"]:
            raise ValueError(f"API key not configured for {provider}")
        
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        # Adjust headers for different providers
        if provider == "anthropic":
            headers["x-api-key"] = config["api_key"]
            del headers["Authorization"]
            headers["anthropic-version"] = "2023-06-01"
        
        # Prepare request body based on provider
        if provider == "anthropic":
            body = {
                "model": model,
                "max_tokens": 4096,
                "messages": [
                    {"role": "user", "content": f"{system_prompt}\n\n{user_prompt}"}
                ]
            }
            endpoint = "/messages"
        else:
            body = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 4096,
                "temperature": 0.7
            }
            endpoint = "/chat/completions"
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{config['base_url']}{endpoint}",
                headers=headers,
                json=body
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Extract content based on provider response format
            if provider == "anthropic":
                return result["content"][0]["text"]
            else:
                return result["choices"][0]["message"]["content"]

# Initialize AI capabilities
ai_capabilities = AdvancedAICapabilities(AIProviderManager())

# Export functions for use in main server
async def generate_ai_code(prompt: str, **kwargs) -> Dict[str, Any]:
    return await ai_capabilities.generate_code(prompt, **kwargs)

async def analyze_ai_sentiment(text: str, **kwargs) -> Dict[str, Any]:
    return await ai_capabilities.analyze_sentiment(text, **kwargs)

async def extract_ai_entities(text: str, **kwargs) -> Dict[str, Any]:
    return await ai_capabilities.extract_entities(text, **kwargs)

async def summarize_ai_content(content: str, **kwargs) -> Dict[str, Any]:
    return await ai_capabilities.summarize_content(content, **kwargs)

async def classify_ai_content(content: str, categories: List[str], **kwargs) -> Dict[str, Any]:
    return await ai_capabilities.classify_content(content, categories, **kwargs)

async def detect_ai_language(text: str) -> Dict[str, Any]:
    return await ai_capabilities.detect_language(text)

async def optimize_ai_workflow(workflow_data: Dict[str, Any]) -> Dict[str, Any]:
    return await ai_capabilities.optimize_workflow(workflow_data)