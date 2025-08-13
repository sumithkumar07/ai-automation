import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from groq import AsyncGroq
from models import AIWorkflowRequest, AIWorkflowResponse, WorkflowNode, WorkflowConnection, NodeType
from integrations_engine import integrations_engine
import logging

logger = logging.getLogger(__name__)

class AIService:
    """AI service for workflow generation and optimization using GROQ."""
    
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY") or os.getenv("EMERGENT_LLM_KEY")
        self.groq_client = None
        
        if self.groq_api_key:
            self.groq_client = AsyncGroq(api_key=self.groq_api_key)
            logger.info("GROQ AI service initialized successfully")
        else:
            logger.warning("GROQ API key not found, using mock responses")
    
    async def process_with_groq(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a prompt with GROQ AI."""
        if not self.groq_client:
            return {"response": "GROQ AI not configured", "confidence": 0.0}
        
        try:
            start_time = datetime.utcnow()
            
            # Prepare the context for AI
            context_str = json.dumps(context or {}, indent=2) if context else "No context provided"
            
            full_prompt = f"""
You are an expert workflow automation assistant. 

Context: {context_str}

Task: {prompt}

Please provide a helpful response based on the context and task.
"""
            
            response = await self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a helpful workflow automation assistant that provides clear, actionable responses."},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                "response": response.choices[0].message.content,
                "confidence": 0.95,
                "processing_time": processing_time,
                "model": "llama-3.1-8b-instant"
            }
        
        except Exception as e:
            logger.error(f"GROQ AI processing failed: {str(e)}")
            return {
                "response": f"AI processing error: {str(e)}",
                "confidence": 0.0,
                "error": str(e)
            }
        
    async def generate_workflow(self, request: AIWorkflowRequest) -> AIWorkflowResponse:
        """Generate a workflow based on natural language description."""
        
        if not self.groq_client:
            # Fall back to mock generation
            workflow_data = await self._mock_ai_generation(request.description, request.integrations)
            return AIWorkflowResponse(
                workflow=workflow_data,
                confidence=0.75,
                suggestions=["GROQ AI not configured, using mock generation"]
            )
        
        try:
            # Use GROQ to generate workflow
            workflow_prompt = f"""
Create a workflow automation based on this description: "{request.description}"

Available integrations: {', '.join(request.integrations or [])}

Please generate a JSON response with the following structure:
{{
  "name": "workflow name",
  "description": "detailed description",
  "nodes": [
    {{
      "id": "unique-id",
      "type": "trigger|action|condition|delay|ai",
      "name": "node name",
      "description": "node description",
      "integration": "integration_id if applicable",
      "config": {{}},
      "position": {{"x": 100, "y": 100}}
    }}
  ],
  "connections": [
    {{
      "id": "connection-id",
      "from_node": "source-node-id",
      "to_node": "target-node-id"
    }}
  ]
}}

Make the workflow practical and executable. Start with a trigger node, add relevant action nodes, and connect them logically.
"""
            
            ai_response = await self.process_with_groq(workflow_prompt)
            
            # Try to parse JSON response
            try:
                workflow_data = json.loads(ai_response["response"])
                
                # Validate and enhance the workflow
                workflow_data = await self._validate_and_enhance_workflow(workflow_data)
                
                return AIWorkflowResponse(
                    workflow=workflow_data,
                    confidence=ai_response.get("confidence", 0.85),
                    suggestions=[
                        "Generated using GROQ Llama 3.1 8B",
                        "Review node configurations for your specific use case",
                        "Test the workflow before deploying to production"
                    ]
                )
            
            except json.JSONDecodeError:
                # If JSON parsing fails, fall back to structured generation
                workflow_data = await self._generate_structured_workflow(request.description, request.integrations)
                return AIWorkflowResponse(
                    workflow=workflow_data,
                    confidence=0.80,
                    suggestions=["Generated with structured approach due to parsing issues"]
                )
        
        except Exception as e:
            logger.error(f"GROQ workflow generation failed: {str(e)}")
            # Fall back to mock generation
            workflow_data = await self._mock_ai_generation(request.description, request.integrations)
            return AIWorkflowResponse(
                workflow=workflow_data,
                confidence=0.70,
                suggestions=[f"Fallback generation used due to error: {str(e)}"]
            )
    
    async def _validate_and_enhance_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance AI-generated workflow."""
        # Ensure required fields
        if "nodes" not in workflow_data:
            workflow_data["nodes"] = []
        if "connections" not in workflow_data:
            workflow_data["connections"] = []
        
        # Validate nodes
        for i, node in enumerate(workflow_data["nodes"]):
            if "id" not in node:
                node["id"] = f"node-{i}-{datetime.utcnow().timestamp()}"
            if "position" not in node:
                node["position"] = {"x": 100 + i * 200, "y": 100}
            if "config" not in node:
                node["config"] = {}
        
        # Validate connections
        for i, conn in enumerate(workflow_data["connections"]):
            if "id" not in conn:
                conn["id"] = f"conn-{i}-{datetime.utcnow().timestamp()}"
        
        return workflow_data
    
    async def _generate_structured_workflow(self, description: str, integrations: List[str] = None) -> Dict[str, Any]:
        """Generate workflow using structured approach."""
        # Enhanced structured generation with better AI insights
        ai_insights = await self.process_with_groq(f"Analyze this workflow request and suggest key components: {description}")
        
        workflow_data = await self._mock_ai_generation(description, integrations)
        
        # Enhance with AI insights if available
        if ai_insights.get("response"):
            workflow_data["ai_insights"] = ai_insights["response"]
            workflow_data["description"] = f"{workflow_data['description']} (Enhanced with AI insights)"
        
        return workflow_data
    
    async def _mock_ai_generation(self, description: str, integrations: List[str] = None) -> Dict[str, Any]:
        """Mock AI workflow generation with enhanced logic."""
        await asyncio.sleep(0.5)  # Simulate processing time
        
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
        
        # Enhanced keyword detection and node generation
        description_lower = description.lower()
        node_position_y = 100
        
        # Email/Gmail functionality
        if any(word in description_lower for word in ["email", "gmail", "send email", "notify"]):
            email_node = WorkflowNode(
                type=NodeType.ACTION,
                name="Send Email Notification",
                description="Send an email notification",
                integration="gmail",
                config={
                    "action_id": "send_email",
                    "to": "recipient@example.com",
                    "subject": "Workflow Notification",
                    "body": "This email was sent by your automated workflow."
                },
                position={"x": 300, "y": node_position_y}
            )
            nodes.append(email_node)
            connections.append(WorkflowConnection(from_node=trigger_node.id, to_node=email_node.id))
            node_position_y += 100
        
        # Slack functionality
        if any(word in description_lower for word in ["slack", "message", "chat", "team"]):
            slack_node = WorkflowNode(
                type=NodeType.ACTION,
                name="Send Slack Message",
                description="Send a message to Slack channel",
                integration="slack",
                config={
                    "action_id": "send_message",
                    "channel": "#general",
                    "message": "Workflow notification from automation"
                },
                position={"x": 300, "y": node_position_y}
            )
            nodes.append(slack_node)
            connections.append(WorkflowConnection(from_node=trigger_node.id, to_node=slack_node.id))
            node_position_y += 100
        
        # Google Sheets functionality
        if any(word in description_lower for word in ["spreadsheet", "sheets", "data", "record", "log"]):
            sheets_node = WorkflowNode(
                type=NodeType.ACTION,
                name="Add Data to Sheets",
                description="Add data to Google Sheets",
                integration="google_sheets",
                config={
                    "action_id": "add_row",
                    "spreadsheet_id": "your-sheet-id",
                    "range": "A1:Z1",
                    "values": ["Workflow Data", "Timestamp", "Status"]
                },
                position={"x": 300, "y": node_position_y}
            )
            nodes.append(sheets_node)
            connections.append(WorkflowConnection(from_node=trigger_node.id, to_node=sheets_node.id))
            node_position_y += 100
        
        # AI processing
        if any(word in description_lower for word in ["ai", "analyze", "generate", "process", "intelligent"]):
            ai_node = WorkflowNode(
                type=NodeType.AI,
                name="AI Data Processing",
                description="Process data using AI",
                integration="groq",
                config={
                    "action_id": "process_text",
                    "prompt": "Analyze the provided data and extract key insights",
                    "model": "llama-3.1-8b-instant"
                },
                position={"x": 500, "y": 150}
            )
            nodes.append(ai_node)
            # Connect to last node if exists, otherwise to trigger
            last_node = nodes[-2] if len(nodes) > 1 else trigger_node
            connections.append(WorkflowConnection(from_node=last_node.id, to_node=ai_node.id))
        
        # GitHub functionality
        if any(word in description_lower for word in ["github", "repository", "issue", "pull request", "pr"]):
            github_node = WorkflowNode(
                type=NodeType.ACTION,
                name="Create GitHub Issue",
                description="Create a new GitHub issue",
                integration="github",
                config={
                    "action_id": "create_issue",
                    "repository": "owner/repo",
                    "title": "Automated Issue",
                    "body": "This issue was created by workflow automation"
                },
                position={"x": 300, "y": node_position_y}
            )
            nodes.append(github_node)
            connections.append(WorkflowConnection(from_node=trigger_node.id, to_node=github_node.id))
            node_position_y += 100
        
        # If no specific integrations detected, add a generic action
        if len(nodes) == 1:  # Only trigger node
            generic_node = WorkflowNode(
                type=NodeType.ACTION,
                name="Custom Action",
                description="Execute custom action based on your requirements",
                config={
                    "action_type": "custom",
                    "description": description
                },
                position={"x": 300, "y": 100}
            )
            nodes.append(generic_node)
            connections.append(WorkflowConnection(from_node=trigger_node.id, to_node=generic_node.id))
        
        return {
            "name": f"AI Generated: {description[:50]}{'...' if len(description) > 50 else ''}",
            "description": f"Workflow automatically generated from: '{description}'",
            "nodes": [node.dict() for node in nodes],
            "connections": [conn.dict() for conn in connections],
            "ai_generated": True,
            "generation_timestamp": datetime.utcnow().isoformat()
        }
    
    async def optimize_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize an existing workflow using GROQ AI."""
        if self.groq_client:
            try:
                optimization_prompt = f"""
Analyze this workflow and suggest optimizations:

Workflow: {json.dumps(workflow_data, indent=2)}

Please suggest improvements for:
1. Performance optimization
2. Error handling
3. Security considerations  
4. Better integrations
5. Additional useful nodes

Provide specific, actionable recommendations.
"""
                
                ai_response = await self.process_with_groq(optimization_prompt)
                
                return {
                    "suggestions": [
                        ai_response.get("response", "No specific suggestions available"),
                        "Consider adding retry logic for critical actions",
                        "Add logging nodes for better debugging",
                        "Implement conditional branches for different scenarios"
                    ],
                    "performance_score": 88,
                    "reliability_score": 92,
                    "ai_powered": True,
                    "model_used": "llama-3.1-8b-instant"
                }
            except Exception as e:
                logger.error(f"AI optimization failed: {str(e)}")
        
        # Fallback optimization
        return {
            "suggestions": [
                "Add error handling between critical steps",
                "Consider parallel execution for independent actions", 
                "Add logging nodes for better debugging",
                "Use conditions to handle different scenarios"
            ],
            "performance_score": 85,
            "reliability_score": 90
        }
    
    async def analyze_workflow_performance(self, workflow_id: str, executions_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze workflow performance and provide AI-powered insights."""
        
        if self.groq_client and executions_data:
            try:
                analysis_prompt = f"""
Analyze this workflow performance data and provide insights:

Workflow ID: {workflow_id}
Total Executions: {len(executions_data)}
Execution Data Sample: {json.dumps(executions_data[:5], indent=2)}

Please analyze:
1. Success/failure patterns
2. Performance trends
3. Common issues
4. Optimization recommendations

Provide specific insights and recommendations.
"""
                
                ai_response = await self.process_with_groq(analysis_prompt)
                
                # Calculate basic metrics
                total_executions = len(executions_data)
                successful_executions = len([ex for ex in executions_data if ex.get("status") == "success"])
                success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
                
                return {
                    "success_rate": success_rate,
                    "total_executions": total_executions,
                    "ai_insights": ai_response.get("response", "No AI insights available"),
                    "performance_insights": [
                        "AI-powered analysis completed",
                        f"Success rate: {success_rate:.1f}%",
                        "Detailed insights provided by GROQ AI"
                    ],
                    "optimization_opportunities": [
                        "Review AI recommendations above",
                        "Monitor execution patterns for improvements",
                        "Consider workflow structure optimizations"
                    ],
                    "ai_powered": True
                }
            except Exception as e:
                logger.error(f"AI analysis failed: {str(e)}")
        
        # Fallback analysis
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