# Enhanced AI Module - Multi-LLM Support with Fallbacks
import os
import httpx
import asyncio
from typing import Dict, List, Optional, Any
from groq import Groq
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MultiLLMProvider:
    """Advanced multi-LLM provider with intelligent fallbacks and optimization"""
    
    def __init__(self):
        self.groq_client = None
        self.openai_client = None
        self.claude_client = None
        
        # Initialize available providers
        self._init_providers()
        
        # Provider priority order (based on speed and reliability)
        self.provider_priority = ['groq', 'openai', 'claude', 'gemini']
        
        # Model mappings for different providers
        self.model_mappings = {
            'groq': {
                'fast': 'llama-3.1-8b-instant',
                'balanced': 'llama-3.3-70b-versatile', 
                'powerful': 'llama-3.3-70b-versatile'
            },
            'openai': {
                'fast': 'gpt-3.5-turbo',
                'balanced': 'gpt-4o-mini',
                'powerful': 'gpt-4o'
            },
            'claude': {
                'fast': 'claude-3-haiku-20240307',
                'balanced': 'claude-3-sonnet-20240229',
                'powerful': 'claude-3-opus-20240229'
            }
        }
    
    def _init_providers(self):
        """Initialize available AI providers"""
        try:
            groq_key = os.getenv("GROQ_API_KEY")
            if groq_key:
                self.groq_client = Groq(api_key=groq_key)
                logger.info("GROQ client initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize GROQ: {e}")
        
        try:
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                # We'll use httpx for OpenAI API calls
                logger.info("OpenAI client ready for initialization")
        except Exception as e:
            logger.warning(f"OpenAI not available: {e}")
    
    async def generate_text(
        self, 
        prompt: str, 
        mode: str = 'balanced',
        max_tokens: int = 1000,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
        preferred_provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate text with intelligent provider selection and fallbacks
        
        Args:
            prompt: The user prompt
            mode: 'fast', 'balanced', or 'powerful'
            max_tokens: Maximum tokens to generate
            temperature: Creativity level (0.0-1.0)
            system_prompt: Optional system message
            preferred_provider: Preferred provider to try first
        """
        
        # Determine provider order
        providers_to_try = [preferred_provider] if preferred_provider else []
        providers_to_try.extend([p for p in self.provider_priority if p != preferred_provider])
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        for provider in providers_to_try:
            try:
                if provider == 'groq' and self.groq_client:
                    result = await self._generate_groq(messages, mode, max_tokens, temperature)
                    if result:
                        return {
                            "content": result,
                            "provider": "groq",
                            "model": self.model_mappings['groq'][mode],
                            "tokens_used": len(result.split()) * 1.3  # Rough estimate
                        }
                
                elif provider == 'openai':
                    result = await self._generate_openai(messages, mode, max_tokens, temperature)
                    if result:
                        return result
                
                # Add more providers as needed
                        
            except Exception as e:
                logger.warning(f"Provider {provider} failed: {e}")
                continue
        
        raise Exception("All AI providers failed to generate response")
    
    async def _generate_groq(self, messages: List[Dict], mode: str, max_tokens: int, temperature: float):
        """Generate using GROQ"""
        try:
            response = self.groq_client.chat.completions.create(
                model=self.model_mappings['groq'][mode],
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"GROQ generation failed: {e}")
            return None
    
    async def _generate_openai(self, messages: List[Dict], mode: str, max_tokens: int, temperature: float):
        """Generate using OpenAI (via HTTP)"""
        try:
            openai_key = os.getenv("OPENAI_API_KEY")
            if not openai_key:
                return None
                
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {openai_key}"},
                    json={
                        "model": self.model_mappings['openai'][mode],
                        "messages": messages,
                        "max_tokens": max_tokens,
                        "temperature": temperature
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data['choices'][0]['message']['content']
                    return {
                        "content": content,
                        "provider": "openai",
                        "model": self.model_mappings['openai'][mode],
                        "tokens_used": data['usage']['total_tokens']
                    }
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            return None
    
    async def analyze_workflow_performance(self, workflow_data: Dict) -> Dict[str, Any]:
        """AI-powered workflow performance analysis"""
        
        analysis_prompt = f"""
        Analyze this workflow for performance optimization opportunities:
        
        Workflow: {workflow_data.get('name', 'Unnamed')}
        Nodes: {len(workflow_data.get('nodes', []))}
        Connections: {len(workflow_data.get('connections', []))}
        
        Provide specific recommendations for:
        1. Performance bottlenecks
        2. Resource optimization 
        3. Error handling improvements
        4. Scalability enhancements
        5. Alternative approaches
        
        Return as JSON with structured recommendations.
        """
        
        system_prompt = """You are an expert workflow optimization consultant. 
        Analyze workflows and provide actionable performance recommendations in JSON format."""
        
        try:
            result = await self.generate_text(
                prompt=analysis_prompt,
                system_prompt=system_prompt,
                mode='balanced',
                temperature=0.3,
                max_tokens=1500
            )
            
            # Try to parse as JSON, fallback to text if needed
            try:
                recommendations = json.loads(result['content'])
            except:
                recommendations = {"analysis": result['content']}
                
            return {
                "workflow_id": workflow_data.get('_id'),
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "provider_used": result.get('provider'),
                "recommendations": recommendations,
                "confidence_score": 0.85  # AI confidence estimate
            }
            
        except Exception as e:
            logger.error(f"Workflow analysis failed: {e}")
            return {
                "error": "Analysis failed",
                "message": str(e)
            }
    
    async def detect_workflow_errors(self, workflow_data: Dict, execution_history: List[Dict]) -> Dict[str, Any]:
        """Intelligent error detection and fix suggestions"""
        
        error_patterns = []
        for execution in execution_history[-5:]:  # Last 5 executions
            if execution.get('status') == 'failed':
                error_patterns.append({
                    "error": execution.get('error', 'Unknown'),
                    "timestamp": execution.get('started_at'),
                    "logs": execution.get('logs', [])[-3:]  # Last 3 log entries
                })
        
        analysis_prompt = f"""
        Analyze this workflow for errors and provide specific fixes:
        
        Workflow Structure:
        - Nodes: {len(workflow_data.get('nodes', []))}
        - Connections: {len(workflow_data.get('connections', []))}
        
        Recent Error Patterns:
        {json.dumps(error_patterns, indent=2)}
        
        Provide:
        1. Root cause analysis
        2. Specific fix recommendations
        3. Prevention strategies
        4. Code examples where applicable
        
        Format as JSON with actionable solutions.
        """
        
        system_prompt = """You are an expert automation debugger. 
        Identify workflow issues and provide specific, actionable fixes in JSON format."""
        
        try:
            result = await self.generate_text(
                prompt=analysis_prompt,
                system_prompt=system_prompt,
                mode='powerful',
                temperature=0.2,
                max_tokens=2000
            )
            
            try:
                fixes = json.loads(result['content'])
            except:
                fixes = {"analysis": result['content']}
            
            return {
                "workflow_id": workflow_data.get('_id'),
                "error_count": len(error_patterns),
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "provider_used": result.get('provider'),
                "fixes": fixes,
                "priority": "high" if len(error_patterns) > 2 else "medium"
            }
            
        except Exception as e:
            logger.error(f"Error detection failed: {e}")
            return {
                "error": "Error detection failed",
                "message": str(e)
            }

# Global instance
multi_llm = MultiLLMProvider()