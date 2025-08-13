import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from .models import AIWorkflowRequest, AIWorkflowResponse, WorkflowNode, WorkflowConnection, NodeType
from .integrations_engine import integrations_engine

class AIService:
    """AI service for workflow generation and optimization."""
    
    def __init__(self):
        self.emergent_key = os.getenv("EMERGENT_LLM_KEY")
        
    async def generate_workflow(self, request: AIWorkflowRequest) -> AIWorkflowResponse:
        """Generate a workflow based on natural language description."""
        
        # Mock AI workflow generation for demo
        # In production, this would use EMERGENT_LLM_KEY to call actual AI services
        
        workflow_data = await self._mock_ai_generation(request.description, request.integrations)
        
        return AIWorkflowResponse(
            workflow=workflow_data,
            confidence=0.85,
            suggestions=[
                "Consider adding error handling nodes",
                "Add notifications for workflow completion",
                "Consider using conditions for branching logic"
            ]
        )
    
    async def _mock_ai_generation(self, description: str, integrations: List[str] = None) -> Dict[str, Any]:
        """Mock AI workflow generation."""
        await asyncio.sleep(1)  # Simulate AI processing time
        
        # Analyze description and generate appropriate workflow
        nodes = []
        connections = []
        
        # Always start with a trigger
        trigger_node = WorkflowNode(
            type=NodeType.TRIGGER,
            name="Manual Trigger",
            description="Manually trigger this workflow",
            position={"x": 100, "y": 100}
        )
        nodes.append(trigger_node)
        
        # Generate nodes based on keywords in description
        description_lower = description.lower()
        
        if "email" in description_lower or "gmail" in description_lower:
            email_node = WorkflowNode(
                type=NodeType.ACTION,
                name="Send Email",
                description="Send an email notification",
                integration="gmail",
                config={"action_id": "send_email"},
                position={"x": 300, "y": 100}
            )
            nodes.append(email_node)
            connections.append(WorkflowConnection(from_node=trigger_node.id, to_node=email_node.id))
        
        if "slack" in description_lower or "message" in description_lower:
            slack_node = WorkflowNode(
                type=NodeType.ACTION,
                name="Send Slack Message",
                description="Send a message to Slack",
                integration="slack",
                config={"action_id": "send_message"},
                position={"x": 300, "y": 200}
            )
            nodes.append(slack_node)
            connections.append(WorkflowConnection(from_node=trigger_node.id, to_node=slack_node.id))
        
        if "spreadsheet" in description_lower or "google sheets" in description_lower:
            sheets_node = WorkflowNode(
                type=NodeType.ACTION,
                name="Add to Google Sheets",
                description="Add data to Google Sheets",
                integration="google_sheets",
                config={"action_id": "add_row"},
                position={"x": 300, "y": 300}
            )
            nodes.append(sheets_node)
            connections.append(WorkflowConnection(from_node=trigger_node.id, to_node=sheets_node.id))
        
        if "ai" in description_lower or "analyze" in description_lower or "generate" in description_lower:
            ai_node = WorkflowNode(
                type=NodeType.AI,
                name="AI Processing",
                description="Process data with AI",
                integration="openai",
                config={"action_id": "generate_text"},
                position={"x": 500, "y": 150}
            )
            nodes.append(ai_node)
            # Connect to last node if exists, otherwise to trigger
            last_node = nodes[-2] if len(nodes) > 1 else trigger_node
            connections.append(WorkflowConnection(from_node=last_node.id, to_node=ai_node.id))
        
        # If no specific integrations detected, add a generic action
        if len(nodes) == 1:  # Only trigger node
            generic_node = WorkflowNode(
                type=NodeType.ACTION,
                name="Custom Action",
                description="Custom action based on your description",
                position={"x": 300, "y": 100}
            )
            nodes.append(generic_node)
            connections.append(WorkflowConnection(from_node=trigger_node.id, to_node=generic_node.id))
        
        return {
            "name": f"AI Generated: {description[:50]}...",
            "description": f"Workflow generated from: {description}",
            "nodes": [node.dict() for node in nodes],
            "connections": [conn.dict() for conn in connections]
        }
    
    async def optimize_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize an existing workflow."""
        # Mock optimization
        await asyncio.sleep(0.5)
        
        optimizations = {
            "suggestions": [
                "Add error handling between critical steps",
                "Consider parallel execution for independent actions",
                "Add logging nodes for better debugging",
                "Use conditions to handle different scenarios"
            ],
            "performance_score": 85,
            "reliability_score": 90
        }
        
        return optimizations
    
    async def analyze_workflow_performance(self, workflow_id: str, executions_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze workflow performance and provide insights."""
        await asyncio.sleep(0.3)
        
        # Mock analysis
        total_executions = len(executions_data)
        successful_executions = len([ex for ex in executions_data if ex.get("status") == "success"])
        success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
        
        return {
            "success_rate": success_rate,
            "total_executions": total_executions,
            "performance_insights": [
                "Workflow performs well under normal conditions",
                "Consider adding retry logic for better reliability",
                "Average execution time is within acceptable range"
            ],
            "optimization_opportunities": [
                "Reduce delay nodes where possible",
                "Combine similar actions into single nodes",
                "Add conditional branches for error scenarios"
            ]
        }

# Global instance
ai_service = AIService()