# 🤖 ENHANCED MULTI-AGENT AI SYSTEM
# Zero frontend disruption - Pure backend enhancement

import asyncio
import json
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import uuid
from groq import Groq
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class AgentRole(Enum):
    PLANNER = "planner"
    EXECUTOR = "executor"
    VALIDATOR = "validator"
    OPTIMIZER = "optimizer"
    COORDINATOR = "coordinator"

@dataclass
class AgentResponse:
    agent_id: str
    role: AgentRole
    content: str
    confidence: float
    metadata: Dict[str, Any]
    timestamp: datetime

class MultiAgentConversation:
    def __init__(self, conversation_id: str, context: Dict[str, Any]):
        self.conversation_id = conversation_id
        self.context = context
        self.history: List[AgentResponse] = []
        self.active_agents: Set[str] = set()
        
    def add_response(self, response: AgentResponse):
        self.history.append(response)
        self.active_agents.add(response.agent_id)

class EnhancedMultiAgentSystem:
    def __init__(self, groq_client: Groq, db):
        self.groq_client = groq_client
        self.db = db
        self.agents = {}
        self.conversations = {}
        self.performance_metrics = {
            "total_conversations": 0,
            "success_rate": 0.0,
            "avg_response_time": 0.0,
            "agent_coordination_score": 0.0
        }
        
        # Initialize specialized agents
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize specialized AI agents with distinct roles"""
        self.agents = {
            AgentRole.PLANNER: {
                "model": "llama-3.1-8b-instant",
                "system_prompt": """You are a strategic planning AI agent. Your role is to:
                1. Break down complex tasks into actionable steps
                2. Identify potential challenges and solutions
                3. Coordinate with other agents for optimal workflow planning
                4. Provide clear, structured planning guidance
                Focus on strategic thinking and comprehensive planning.""",
                "temperature": 0.3,
                "max_tokens": 1000
            },
            AgentRole.EXECUTOR: {
                "model": "llama3-8b-8192",
                "system_prompt": """You are an execution-focused AI agent. Your role is to:
                1. Convert plans into specific, actionable tasks
                2. Provide detailed implementation instructions
                3. Handle technical specifications and configurations
                4. Focus on practical, executable solutions
                Be precise, technical, and implementation-focused.""",
                "temperature": 0.2,
                "max_tokens": 1200
            },
            AgentRole.VALIDATOR: {
                "model": "llama-3.1-8b-instant",
                "system_prompt": """You are a validation and quality assurance AI agent. Your role is to:
                1. Review and validate proposed solutions
                2. Identify potential issues or improvements
                3. Ensure quality and consistency
                4. Provide constructive feedback and suggestions
                Be thorough, analytical, and quality-focused.""",
                "temperature": 0.1,
                "max_tokens": 800
            },
            AgentRole.OPTIMIZER: {
                "model": "llama-3.1-8b-instant",
                "system_prompt": """You are an optimization AI agent. Your role is to:
                1. Analyze workflows for efficiency improvements
                2. Suggest performance enhancements
                3. Identify cost-saving opportunities
                4. Optimize resource utilization
                Focus on efficiency, performance, and optimization.""",
                "temperature": 0.4,
                "max_tokens": 900
            },
            AgentRole.COORDINATOR: {
                "model": "llama-3.1-8b-instant",
                "system_prompt": """You are a coordination AI agent. Your role is to:
                1. Synthesize inputs from multiple agents
                2. Resolve conflicts between different approaches
                3. Ensure coherent final recommendations
                4. Coordinate multi-agent responses
                Be diplomatic, comprehensive, and solution-oriented.""",
                "temperature": 0.2,
                "max_tokens": 1000
            }
        }

    async def start_multi_agent_conversation(
        self, 
        user_query: str, 
        user_id: str,
        context: Dict[str, Any] = None
    ) -> str:
        """Start a new multi-agent conversation"""
        conversation_id = f"conv_{uuid.uuid4().hex[:12]}"
        
        # Enhanced context building
        full_context = {
            "user_query": user_query,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "conversation_type": "multi_agent",
            **(context or {})
        }
        
        conversation = MultiAgentConversation(conversation_id, full_context)
        self.conversations[conversation_id] = conversation
        
        try:
            # Phase 1: Planning Agent analyzes the query
            planner_response = await self._get_agent_response(
                AgentRole.PLANNER, 
                user_query, 
                full_context
            )
            conversation.add_response(planner_response)
            
            # Phase 2: Executor provides implementation details
            executor_context = {**full_context, "planner_input": planner_response.content}
            executor_response = await self._get_agent_response(
                AgentRole.EXECUTOR,
                f"Based on this plan: {planner_response.content}\nProvide detailed implementation for: {user_query}",
                executor_context
            )
            conversation.add_response(executor_response)
            
            # Phase 3: Validator reviews the approach
            validator_context = {
                **full_context, 
                "planner_input": planner_response.content,
                "executor_input": executor_response.content
            }
            validator_response = await self._get_agent_response(
                AgentRole.VALIDATOR,
                f"Review this approach:\nPlan: {planner_response.content}\nImplementation: {executor_response.content}\nOriginal query: {user_query}",
                validator_context
            )
            conversation.add_response(validator_response)
            
            # Phase 4: Optimizer suggests improvements
            optimizer_context = {**validator_context, "validator_input": validator_response.content}
            optimizer_response = await self._get_agent_response(
                AgentRole.OPTIMIZER,
                f"Optimize this solution:\n{executor_response.content}\nConsidering: {validator_response.content}",
                optimizer_context
            )
            conversation.add_response(optimizer_response)
            
            # Phase 5: Coordinator synthesizes final response
            final_context = {
                **optimizer_context,
                "all_agent_responses": [
                    {"role": r.role.value, "content": r.content, "confidence": r.confidence}
                    for r in [planner_response, executor_response, validator_response, optimizer_response]
                ]
            }
            
            coordinator_response = await self._get_agent_response(
                AgentRole.COORDINATOR,
                f"Synthesize the best solution from all agents for: {user_query}\n\nAgent inputs available in context.",
                final_context
            )
            conversation.add_response(coordinator_response)
            
            # Store conversation in database
            await self._store_conversation(conversation)
            
            # Update performance metrics
            self._update_performance_metrics(conversation)
            
            return coordinator_response.content
            
        except Exception as e:
            logger.error(f"Multi-agent conversation error: {e}")
            return f"I apologize, but I encountered an issue coordinating the multi-agent response. Please try again."

    async def _get_agent_response(
        self, 
        role: AgentRole, 
        query: str, 
        context: Dict[str, Any]
    ) -> AgentResponse:
        """Get response from a specific agent"""
        agent_config = self.agents[role]
        agent_id = f"{role.value}_{uuid.uuid4().hex[:8]}"
        
        try:
            # Enhanced prompt with context awareness
            messages = [
                {"role": "system", "content": agent_config["system_prompt"]},
                {"role": "user", "content": f"Query: {query}\n\nContext: {json.dumps(context, default=str, indent=2)}"}
            ]
            
            response = self.groq_client.chat.completions.create(
                model=agent_config["model"],
                messages=messages,
                temperature=agent_config["temperature"],
                max_tokens=agent_config["max_tokens"]
            )
            
            content = response.choices[0].message.content
            
            # Calculate confidence based on response characteristics
            confidence = self._calculate_confidence(content, role)
            
            return AgentResponse(
                agent_id=agent_id,
                role=role,
                content=content,
                confidence=confidence,
                metadata={
                    "model_used": agent_config["model"],
                    "temperature": agent_config["temperature"],
                    "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else 0
                },
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Agent {role.value} error: {e}")
            return AgentResponse(
                agent_id=agent_id,
                role=role,
                content=f"Agent {role.value} encountered an error. Please try again.",
                confidence=0.1,
                metadata={"error": str(e)},
                timestamp=datetime.utcnow()
            )

    def _calculate_confidence(self, content: str, role: AgentRole) -> float:
        """Calculate confidence score based on response characteristics"""
        confidence = 0.7  # Base confidence
        
        # Length-based confidence adjustment
        if len(content) > 100:
            confidence += 0.1
        if len(content) > 500:
            confidence += 0.1
        
        # Role-specific confidence adjustments
        if role == AgentRole.PLANNER and "step" in content.lower():
            confidence += 0.1
        elif role == AgentRole.EXECUTOR and any(word in content.lower() for word in ["implement", "configure", "setup"]):
            confidence += 0.1
        elif role == AgentRole.VALIDATOR and any(word in content.lower() for word in ["review", "check", "validate"]):
            confidence += 0.1
        
        return min(confidence, 1.0)

    async def _store_conversation(self, conversation: MultiAgentConversation):
        """Store conversation in database"""
        try:
            conversation_data = {
                "_id": conversation.conversation_id,
                "context": conversation.context,
                "responses": [
                    {
                        "agent_id": r.agent_id,
                        "role": r.role.value,
                        "content": r.content,
                        "confidence": r.confidence,
                        "metadata": r.metadata,
                        "timestamp": r.timestamp.isoformat()
                    }
                    for r in conversation.history
                ],
                "created_at": datetime.utcnow(),
                "performance_score": self._calculate_conversation_score(conversation)
            }
            
            self.db.multi_agent_conversations.insert_one(conversation_data)
            
        except Exception as e:
            logger.error(f"Failed to store conversation: {e}")

    def _calculate_conversation_score(self, conversation: MultiAgentConversation) -> float:
        """Calculate overall conversation performance score"""
        if not conversation.history:
            return 0.0
        
        avg_confidence = sum(r.confidence for r in conversation.history) / len(conversation.history)
        agent_diversity = len(conversation.active_agents) / len(self.agents)
        
        return (avg_confidence * 0.7) + (agent_diversity * 0.3)

    def _update_performance_metrics(self, conversation: MultiAgentConversation):
        """Update system performance metrics"""
        self.performance_metrics["total_conversations"] += 1
        score = self._calculate_conversation_score(conversation)
        
        # Update running average
        total = self.performance_metrics["total_conversations"]
        current_success = self.performance_metrics["success_rate"]
        self.performance_metrics["success_rate"] = ((current_success * (total - 1)) + score) / total
        
        # Update agent coordination score
        coordination_score = len(conversation.active_agents) / len(self.agents)
        current_coord = self.performance_metrics["agent_coordination_score"]
        self.performance_metrics["agent_coordination_score"] = ((current_coord * (total - 1)) + coordination_score) / total

    async def get_conversation_history(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation history"""
        try:
            return self.db.multi_agent_conversations.find_one({"_id": conversation_id})
        except Exception as e:
            logger.error(f"Failed to retrieve conversation: {e}")
            return None

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        return {
            **self.performance_metrics,
            "active_agents": len(self.agents),
            "active_conversations": len(self.conversations),
            "timestamp": datetime.utcnow().isoformat()
        }

    async def enhance_conversation_quality(
        self, 
        conversation_history: List[Dict[str, Any]], 
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance conversation quality using multi-agent analysis"""
        try:
            # Use coordinator to analyze and improve conversation
            analysis_query = f"Analyze this conversation for quality improvements:\n{json.dumps(conversation_history, indent=2)}"
            
            coordinator_response = await self._get_agent_response(
                AgentRole.COORDINATOR,
                analysis_query,
                user_context
            )
            
            return {
                "enhanced_response": coordinator_response.content,
                "quality_score": coordinator_response.confidence,
                "improvements_suggested": True,
                "agent_analysis": {
                    "agent_id": coordinator_response.agent_id,
                    "role": coordinator_response.role.value,
                    "confidence": coordinator_response.confidence
                }
            }
            
        except Exception as e:
            logger.error(f"Conversation quality enhancement error: {e}")
            return {
                "enhanced_response": "Quality enhancement temporarily unavailable.",
                "quality_score": 0.5,
                "improvements_suggested": False,
                "error": str(e)
            }

# Initialize the multi-agent system
def initialize_multi_agent_system(groq_client: Groq, db) -> EnhancedMultiAgentSystem:
    """Initialize the enhanced multi-agent system"""
    return EnhancedMultiAgentSystem(groq_client, db)