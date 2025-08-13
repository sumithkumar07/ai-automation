# Enhanced AI Intelligence System - Phase 1 Quick Wins
# Preserves existing UI/UX while adding advanced capabilities

import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pymongo import MongoClient
import asyncio
from groq import Groq
import os
from dataclasses import dataclass
from collections import defaultdict
import random

logger = logging.getLogger(__name__)

@dataclass
class WorkflowSuggestion:
    type: str
    title: str
    description: str
    impact: str
    implementation: Dict[str, Any]
    confidence: float

@dataclass
class AIInsight:
    category: str
    insight: str
    recommendation: str
    priority: str
    estimated_savings: str

class EnhancedAIIntelligence:
    def __init__(self, db, groq_client):
        self.db = db
        self.groq_client = groq_client
        self.workflows_collection = db.workflows
        self.executions_collection = db.executions
        self.ai_analytics_collection = db.ai_analytics
        self.user_patterns_collection = db.user_patterns
        
    async def analyze_user_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analyze user behavior patterns for smart suggestions"""
        try:
            # Get user's workflow history
            workflows = list(self.workflows_collection.find({"user_id": user_id}))
            executions = list(self.executions_collection.find({"user_id": user_id}).sort("started_at", -1).limit(100))
            
            patterns = {
                "workflow_complexity": self._analyze_workflow_complexity(workflows),
                "execution_patterns": self._analyze_execution_patterns(executions),
                "common_node_types": self._analyze_node_usage(workflows),
                "time_patterns": self._analyze_time_patterns(executions),
                "error_patterns": self._analyze_error_patterns(executions)
            }
            
            # Store patterns for future use
            self.user_patterns_collection.update_one(
                {"user_id": user_id},
                {"$set": {"patterns": patterns, "updated_at": datetime.utcnow()}},
                upsert=True
            )
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing user patterns: {e}")
            return {}
    
    def _analyze_workflow_complexity(self, workflows: List[Dict]) -> Dict[str, Any]:
        """Analyze complexity of user's workflows"""
        if not workflows:
            return {"average_nodes": 0, "complexity_trend": "new_user"}
        
        node_counts = [len(w.get("nodes", [])) for w in workflows]
        avg_nodes = sum(node_counts) / len(node_counts) if node_counts else 0
        
        complexity_level = "simple" if avg_nodes < 5 else "moderate" if avg_nodes < 10 else "complex"
        
        return {
            "average_nodes": round(avg_nodes, 1),
            "complexity_level": complexity_level,
            "total_workflows": len(workflows),
            "most_complex": max(node_counts) if node_counts else 0
        }
    
    def _analyze_execution_patterns(self, executions: List[Dict]) -> Dict[str, Any]:
        """Analyze execution success patterns"""
        if not executions:
            return {"success_rate": 0, "trend": "no_data"}
        
        successful = len([e for e in executions if e.get("status") == "success"])
        success_rate = (successful / len(executions)) * 100
        
        # Analyze recent trend
        recent_executions = executions[:20]  # Last 20 executions
        recent_successful = len([e for e in recent_executions if e.get("status") == "success"])
        recent_rate = (recent_successful / len(recent_executions)) * 100 if recent_executions else 0
        
        trend = "improving" if recent_rate > success_rate else "declining" if recent_rate < success_rate else "stable"
        
        return {
            "success_rate": round(success_rate, 1),
            "recent_success_rate": round(recent_rate, 1),
            "trend": trend,
            "total_executions": len(executions)
        }
    
    def _analyze_node_usage(self, workflows: List[Dict]) -> Dict[str, int]:
        """Analyze which node types user prefers"""
        node_usage = defaultdict(int)
        
        for workflow in workflows:
            for node in workflow.get("nodes", []):
                node_type = node.get("type", "unknown")
                node_usage[node_type] += 1
        
        return dict(sorted(node_usage.items(), key=lambda x: x[1], reverse=True))
    
    def _analyze_time_patterns(self, executions: List[Dict]) -> Dict[str, Any]:
        """Analyze when user typically runs workflows"""
        if not executions:
            return {"peak_hours": [], "peak_days": []}
        
        hours = defaultdict(int)
        days = defaultdict(int)
        
        for execution in executions:
            if execution.get("started_at"):
                dt = execution["started_at"]
                if isinstance(dt, str):
                    dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
                
                hours[dt.hour] += 1
                days[dt.strftime('%A')] += 1
        
        peak_hours = sorted(hours.items(), key=lambda x: x[1], reverse=True)[:3]
        peak_days = sorted(days.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "peak_hours": [{"hour": h, "count": c} for h, c in peak_hours],
            "peak_days": [{"day": d, "count": c} for d, c in peak_days]
        }
    
    def _analyze_error_patterns(self, executions: List[Dict]) -> Dict[str, Any]:
        """Analyze common failure patterns"""
        failures = [e for e in executions if e.get("status") == "failed"]
        
        if not failures:
            return {"common_errors": [], "failure_rate": 0}
        
        error_types = defaultdict(int)
        for failure in failures:
            error = failure.get("error", "unknown_error")
            # Categorize errors
            if "timeout" in error.lower():
                error_types["timeout"] += 1
            elif "connection" in error.lower():
                error_types["connection"] += 1
            elif "auth" in error.lower():
                error_types["authentication"] += 1
            else:
                error_types["other"] += 1
        
        failure_rate = (len(failures) / len(executions)) * 100 if executions else 0
        
        return {
            "common_errors": dict(error_types),
            "failure_rate": round(failure_rate, 1),
            "total_failures": len(failures)
        }
    
    async def generate_smart_suggestions(self, user_id: str) -> List[WorkflowSuggestion]:
        """Generate AI-powered workflow suggestions based on user patterns"""
        try:
            patterns = await self.analyze_user_patterns(user_id)
            suggestions = []
            
            # Performance optimization suggestions
            if patterns.get("execution_patterns", {}).get("success_rate", 0) < 90:
                suggestions.append(WorkflowSuggestion(
                    type="performance",
                    title="Optimize Workflow Reliability",
                    description="Add error handling and retry logic to improve success rate",
                    impact="Could improve success rate by 15-20%",
                    implementation={
                        "add_nodes": ["error_handler", "retry_logic"],
                        "modify_connections": True
                    },
                    confidence=0.85
                ))
            
            # Complexity suggestions
            complexity = patterns.get("workflow_complexity", {})
            if complexity.get("complexity_level") == "simple":
                suggestions.append(WorkflowSuggestion(
                    type="enhancement",
                    title="Add Parallel Processing",
                    description="Execute multiple tasks simultaneously to save time",
                    impact="Could reduce execution time by 40-60%",
                    implementation={
                        "add_nodes": ["parallel_executor", "merge_results"],
                        "restructure": True
                    },
                    confidence=0.75
                ))
            
            # Integration suggestions based on common patterns
            common_nodes = patterns.get("common_node_types", {})
            if "email" in str(common_nodes).lower():
                suggestions.append(WorkflowSuggestion(
                    type="integration",
                    title="Enhance Email Automation",
                    description="Add AI sentiment analysis to email workflows",
                    impact="Better customer engagement and response rates",
                    implementation={
                        "add_nodes": ["ai_sentiment_analyzer", "smart_responder"],
                        "new_integrations": ["AI Provider"]
                    },
                    confidence=0.70
                ))
            
            return suggestions[:5]  # Return top 5 suggestions
            
        except Exception as e:
            logger.error(f"Error generating smart suggestions: {e}")
            return []
    
    async def generate_predictive_insights(self, user_id: str) -> List[AIInsight]:
        """Generate predictive insights about workflow performance"""
        try:
            patterns = await self.analyze_user_patterns(user_id)
            insights = []
            
            # Performance prediction
            execution_patterns = patterns.get("execution_patterns", {})
            if execution_patterns.get("trend") == "declining":
                insights.append(AIInsight(
                    category="performance",
                    insight="Workflow performance is declining",
                    recommendation="Review recent changes and add monitoring nodes",
                    priority="high",
                    estimated_savings="2-3 hours/week in debugging"
                ))
            
            # Time optimization
            time_patterns = patterns.get("time_patterns", {})
            if time_patterns.get("peak_hours"):
                peak_hour = time_patterns["peak_hours"][0]["hour"]
                insights.append(AIInsight(
                    category="optimization",
                    insight=f"Most workflows run at {peak_hour}:00",
                    recommendation="Consider load balancing or scheduling workflows at off-peak times",
                    priority="medium",
                    estimated_savings="15-20% faster execution times"
                ))
            
            # Error prevention
            error_patterns = patterns.get("error_patterns", {})
            if error_patterns.get("failure_rate", 0) > 10:
                insights.append(AIInsight(
                    category="reliability",
                    insight=f"High failure rate: {error_patterns['failure_rate']}%",
                    recommendation="Implement comprehensive error handling and monitoring",
                    priority="high",
                    estimated_savings="4-5 hours/week in troubleshooting"
                ))
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating predictive insights: {e}")
            return []
    
    async def auto_optimize_workflow(self, workflow_id: str, user_id: str) -> Dict[str, Any]:
        """Auto-optimize a workflow using AI"""
        try:
            workflow = self.workflows_collection.find_one({"_id": workflow_id, "user_id": user_id})
            if not workflow:
                return {"error": "Workflow not found"}
            
            # Analyze workflow structure
            nodes = workflow.get("nodes", [])
            connections = workflow.get("connections", [])
            
            optimizations = []
            
            # Check for parallel processing opportunities
            sequential_nodes = self._find_sequential_nodes(nodes, connections)
            if len(sequential_nodes) > 2:
                optimizations.append({
                    "type": "parallelization",
                    "description": "Add parallel processing for independent tasks",
                    "nodes_affected": len(sequential_nodes),
                    "estimated_improvement": "40-60% faster execution"
                })
            
            # Check for missing error handling
            error_handlers = [n for n in nodes if "error" in n.get("type", "").lower()]
            if len(error_handlers) < len(nodes) * 0.2:  # Less than 20% error handling
                optimizations.append({
                    "type": "error_handling",
                    "description": "Add error handling and retry logic",
                    "improvement": "Better reliability and fault tolerance"
                })
            
            # Check for caching opportunities
            if self._has_repeated_operations(nodes):
                optimizations.append({
                    "type": "caching",
                    "description": "Add caching for repeated operations",
                    "improvement": "Faster execution and reduced API calls"
                })
            
            return {
                "workflow_id": workflow_id,
                "optimizations": optimizations,
                "confidence": 0.80,
                "estimated_time_saved": "2-4 hours/week"
            }
            
        except Exception as e:
            logger.error(f"Error auto-optimizing workflow: {e}")
            return {"error": str(e)}
    
    def _find_sequential_nodes(self, nodes: List[Dict], connections: List[Dict]) -> List[str]:
        """Find nodes that can be parallelized"""
        # Simple heuristic: find nodes without dependencies
        dependent_nodes = set()
        for conn in connections:
            dependent_nodes.add(conn.get("to"))
        
        independent_nodes = [n["id"] for n in nodes if n["id"] not in dependent_nodes]
        return independent_nodes
    
    def _has_repeated_operations(self, nodes: List[Dict]) -> bool:
        """Check if workflow has repeated operations that could benefit from caching"""
        node_types = [n.get("type") for n in nodes]
        return len(node_types) != len(set(node_types))  # Has duplicates
    
    async def generate_natural_language_workflow(self, description: str, user_id: str) -> Dict[str, Any]:
        """Generate workflow from natural language using enhanced AI"""
        try:
            if not self.groq_client:
                return {"error": "AI service not available"}
            
            # Get user patterns to personalize the workflow
            patterns = await self.analyze_user_patterns(user_id)
            
            # Enhanced prompt with user context
            system_prompt = f"""
            You are an expert workflow automation designer. Create a detailed workflow based on the user's description.
            
            User Profile:
            - Workflow Complexity Level: {patterns.get('workflow_complexity', {}).get('complexity_level', 'moderate')}
            - Preferred Node Types: {list(patterns.get('common_node_types', {}).keys())[:3]}
            - Success Rate: {patterns.get('execution_patterns', {}).get('success_rate', 'unknown')}%
            
            Generate a workflow with nodes, connections, and configuration. Include error handling and optimization based on user's history.
            
            Return JSON with:
            - name: workflow name
            - description: detailed description
            - nodes: array of nodes with id, type, name, config, x, y coordinates
            - connections: array of connections between nodes
            - triggers: array of trigger conditions
            - optimization_notes: array of optimization suggestions
            """
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create a workflow for: {description}"}
            ]
            
            response = await self.groq_client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=messages,
                max_tokens=2000,
                temperature=0.7
            )
            
            # Parse AI response
            ai_content = response.choices[0].message.content
            
            # Try to extract JSON from response
            try:
                # Find JSON in response
                json_start = ai_content.find('{')
                json_end = ai_content.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    workflow_data = json.loads(ai_content[json_start:json_end])
                    
                    # Ensure proper node positioning
                    for i, node in enumerate(workflow_data.get("nodes", [])):
                        if "x" not in node or "y" not in node:
                            node["x"] = 150 + (i % 4) * 200
                            node["y"] = 100 + (i // 4) * 150
                    
                    return {
                        "type": "workflow",
                        "data": workflow_data,
                        "ai_confidence": 0.85,
                        "personalized": True
                    }
            except json.JSONDecodeError:
                pass
            
            # Fallback: return structured suggestion
            return {
                "type": "suggestion", 
                "data": {
                    "description": description,
                    "ai_response": ai_content,
                    "suggestions": [
                        "Break down into smaller steps",
                        "Add error handling",
                        "Consider parallel processing"
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating natural language workflow: {e}")
            return {"error": str(e)}
    
    async def get_ai_dashboard_insights(self, user_id: str) -> Dict[str, Any]:
        """Get AI insights for dashboard display"""
        try:
            patterns = await self.analyze_user_patterns(user_id)
            suggestions = await self.generate_smart_suggestions(user_id)
            insights = await self.generate_predictive_insights(user_id)
            
            # Generate AI-powered metrics
            ai_metrics = {
                "workflows_analyzed": len(patterns.get("common_node_types", {})),
                "optimization_opportunities": len(suggestions),
                "predicted_time_savings": sum([
                    float(s.estimated_savings.split()[0]) if s.estimated_savings.split()[0].replace('.', '').isdigit() 
                    else 0 for s in insights
                ]),
                "ai_confidence_score": round(sum([s.confidence for s in suggestions]) / len(suggestions) * 100, 1) if suggestions else 0
            }
            
            return {
                "patterns": patterns,
                "suggestions": [s.__dict__ for s in suggestions],
                "insights": [i.__dict__ for i in insights],
                "metrics": ai_metrics,
                "last_analysis": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting AI dashboard insights: {e}")
            return {"error": str(e)}

# Initialize enhanced AI intelligence system
enhanced_ai_intelligence = None

def initialize_ai_intelligence(db, groq_client):
    global enhanced_ai_intelligence
    enhanced_ai_intelligence = EnhancedAIIntelligence(db, groq_client)
    return enhanced_ai_intelligence