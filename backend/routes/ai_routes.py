from fastapi import APIRouter, HTTPException, Depends
from models import AIWorkflowRequest, AIWorkflowResponse
from auth import get_current_active_user
from ai_service import ai_service
from database import get_database
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/generate-workflow", response_model=AIWorkflowResponse)
async def generate_workflow_from_description(
    request: AIWorkflowRequest, 
    enhanced: bool = False,
    session_id: str = None,
    current_user: dict = Depends(get_current_active_user)
):
    """Generate a workflow from natural language description"""
    try:
        logger.info(f"Generating workflow for user {current_user['user_id']}: {request.description[:50]}...")
        response = await ai_service.generate_workflow(request)
        
        # Log successful generation
        if session_id:
            logger.info(f"Generated workflow for session {session_id}")
        
        return response
    except Exception as e:
        logger.error(f"Failed to generate workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate workflow: {str(e)}")

@router.post("/optimize-workflow")
async def optimize_workflow(workflow_data: dict, current_user: dict = Depends(get_current_active_user)):
    """Optimize an existing workflow using AI"""
    try:
        optimization = await ai_service.optimize_workflow(workflow_data)
        return optimization
    except Exception as e:
        logger.error(f"Failed to optimize workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to optimize workflow: {str(e)}")

@router.get("/workflow-insights/{workflow_id}")
async def get_workflow_insights(workflow_id: str, current_user: dict = Depends(get_current_active_user)):
    """Get AI-powered insights for a workflow"""
    db = get_database()
    
    # Verify workflow belongs to user
    workflow = await db.workflows.find_one({"id": workflow_id, "user_id": current_user["user_id"]})
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Get execution history
    cursor = db.workflow_executions.find({"workflow_id": workflow_id}).limit(100)
    executions = await cursor.to_list(length=100)
    
    try:
        insights = await ai_service.analyze_workflow_performance(workflow_id, executions)
        return insights
    except Exception as e:
        logger.error(f"Failed to generate insights: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate insights: {str(e)}")

@router.post("/suggest-integrations")
async def suggest_integrations(request_data: dict = None, description: str = None, current_user: dict = Depends(get_current_active_user)):
    """Suggest integrations based on workflow description - accepts both JSON body and query parameter"""
    try:
        # Handle both API formats: JSON body with 'description' field or query parameter
        if request_data and isinstance(request_data, dict) and "description" in request_data:
            description_text = request_data["description"]
        elif description:
            description_text = description
        else:
            raise HTTPException(status_code=400, detail="Description required in JSON body or as query parameter")
        
        # Enhanced AI-powered suggestions using GROQ
        if ai_service.groq_client:
            suggestions_prompt = f"""
Analyze this workflow description and suggest the best integrations:
"{description_text}"

Available integrations: Gmail, Slack, Google Sheets, GitHub, Stripe, Twilio, Discord, Notion, Airtable, Google Drive, Dropbox, HubSpot, Salesforce, Mailchimp, OpenAI, GROQ AI

For each suggested integration, provide:
1. Integration name
2. Confidence score (0.0-1.0) 
3. Reason for suggestion
4. Specific use case

Format as JSON list.
"""
            
            ai_response = await ai_service.process_with_groq(suggestions_prompt)
            
            # Try to parse AI response as JSON
            import json
            try:
                ai_suggestions = json.loads(ai_response.get("response", "[]"))
                if isinstance(ai_suggestions, list) and ai_suggestions:
                    return {
                        "suggestions": ai_suggestions,
                        "description_analyzed": description_text,
                        "ai_powered": True,
                        "model": "llama-3.1-8b-instant"
                    }
            except json.JSONDecodeError:
                pass
        
        # Fallback to keyword-based suggestions
        description_lower = description_text.lower()
        suggestions = []
        
        # Enhanced keyword detection
        integration_keywords = {
            "gmail": ["email", "gmail", "send email", "mail", "notification", "alert"],
            "slack": ["slack", "chat", "message", "team", "notify team", "channel"],
            "google_sheets": ["spreadsheet", "sheets", "data", "csv", "excel", "table", "record"],
            "github": ["github", "git", "repository", "code", "issue", "pull request", "pr", "commit"],
            "stripe": ["payment", "billing", "stripe", "charge", "subscription", "money"],
            "twilio": ["sms", "text", "phone", "call", "twilio", "mobile"],
            "discord": ["discord", "gaming", "community", "server"],
            "notion": ["notion", "notes", "documentation", "wiki", "knowledge"],
            "airtable": ["airtable", "database", "crm", "base"],
            "groq": ["ai", "artificial intelligence", "analyze", "generate", "intelligent", "smart"],
            "openai": ["openai", "gpt", "chatgpt", "ai text", "language model"]
        }
        
        for integration_id, keywords in integration_keywords.items():
            for keyword in keywords:
                if keyword in description_lower:
                    confidence = 0.8 + (0.1 * len([k for k in keywords if k in description_lower]))
                    confidence = min(confidence, 0.95)
                    
                    suggestions.append({
                        "integration_id": integration_id,
                        "confidence": confidence,
                        "reason": f"Detected '{keyword}' in description",
                        "use_case": f"Integrate {integration_id} for {keyword} functionality"
                    })
                    break
        
        # Remove duplicates and sort by confidence
        unique_suggestions = {}
        for suggestion in suggestions:
            if suggestion["integration_id"] not in unique_suggestions:
                unique_suggestions[suggestion["integration_id"]] = suggestion
        
        final_suggestions = sorted(unique_suggestions.values(), key=lambda x: x["confidence"], reverse=True)
        
        return {
            "suggestions": final_suggestions[:5],  # Top 5 suggestions
            "description_analyzed": description,
            "ai_powered": False
        }
    
    except Exception as e:
        logger.error(f"Failed to suggest integrations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to suggest integrations: {str(e)}")

@router.post("/explain-workflow")
async def explain_workflow(workflow_data: dict, current_user: dict = Depends(get_current_active_user)):
    """Generate human-readable explanation of a workflow"""
    try:
        if ai_service.groq_client:
            # Use AI to generate better explanation
            explanation_prompt = f"""
Explain this workflow in simple, human-readable terms:

Workflow: {workflow_data}

Provide:
1. A clear step-by-step explanation
2. The workflow's purpose
3. Expected outcomes
4. Complexity assessment
5. Estimated execution time

Make it easy to understand for non-technical users.
"""
            
            ai_response = await ai_service.process_with_groq(explanation_prompt)
            
            return {
                "explanation": ai_response.get("response", "AI explanation not available"),
                "complexity": "AI-assessed",
                "estimated_execution_time": "AI-estimated",
                "ai_powered": True,
                "model": "llama-3.1-8b-instant"
            }
        
        # Fallback explanation generation
        nodes = workflow_data.get("nodes", [])
        connections = workflow_data.get("connections", [])
        
        explanation = []
        
        trigger_nodes = [node for node in nodes if node.get("type") == "trigger"]
        if trigger_nodes:
            explanation.append(f"This workflow starts when: {trigger_nodes[0].get('name', 'trigger occurs')}")
        
        action_nodes = [node for node in nodes if node.get("type") == "action"]
        for i, action in enumerate(action_nodes, 1):
            integration = action.get("integration", "system")
            explanation.append(f"Step {i}: {action.get('name')} using {integration}")
        
        ai_nodes = [node for node in nodes if node.get("type") == "ai"]
        for ai_node in ai_nodes:
            explanation.append(f"AI processing: {ai_node.get('name')}")
        
        complexity = "Simple" if len(nodes) <= 3 else "Medium" if len(nodes) <= 6 else "Complex"
        execution_time = f"{len(nodes) * 2}-{len(nodes) * 5} seconds"
        
        return {
            "explanation": ". ".join(explanation) if explanation else "No workflow steps found",
            "complexity": complexity,
            "estimated_execution_time": execution_time,
            "ai_powered": False
        }
    
    except Exception as e:
        logger.error(f"Failed to explain workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to explain workflow: {str(e)}")

@router.post("/chat")
async def ai_chat(
    message: str,
    session_id: str = None,
    current_user: dict = Depends(get_current_active_user)
):
    """Chat with AI assistant about workflows"""
    try:
        # Create a workflow-focused prompt
        chat_prompt = f"""
You are an expert workflow automation assistant. Help the user with their workflow automation question:

User question: {message}

Provide helpful, practical advice about workflow automation, integrations, and best practices.
Keep your response concise but informative.
"""
        
        ai_response = await ai_service.process_with_groq(chat_prompt)
        
        return {
            "response": ai_response.get("response", "I'm sorry, I couldn't process your request."),
            "session_id": session_id,
            "timestamp": ai_response.get("processing_time", 0),
            "model": "llama-3.1-8b-instant"
        }
    
    except Exception as e:
        logger.error(f"AI chat failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI chat failed: {str(e)}")

@router.get("/dashboard-insights")
async def get_enhanced_dashboard_insights(current_user: dict = Depends(get_current_active_user)):
    """Get AI-powered dashboard insights"""
    try:
        db = get_database()
        user_id = current_user["user_id"]
        
        # Get user's workflow and execution data
        workflows_count = await db.workflows.count_documents({"user_id": user_id})
        executions_count = await db.workflow_executions.count_documents({"user_id": user_id})
        
        # Generate AI insights about user's workflow usage
        insights_prompt = f"""
Analyze this user's workflow automation usage and provide insights:

- Total workflows: {workflows_count}
- Total executions: {executions_count}

Provide 3-5 actionable insights and recommendations for improving their automation.
Focus on practical advice and optimization opportunities.
"""
        
        ai_response = await ai_service.process_with_groq(insights_prompt)
        
        return {
            "ai_provider": "groq_llama_3.1_8b",
            "cost_optimized": True,
            "insights": {
                "metrics": {
                    "ai_confidence_score": "High",
                    "optimization_potential": "Medium" if workflows_count > 5 else "High",
                    "predicted_time_savings": f"{max(2, workflows_count // 2)}"
                },
                "recommendations": ai_response.get("response", "No recommendations available")
            }
        }
    
    except Exception as e:
        logger.error(f"Failed to get dashboard insights: {str(e)}")
        return {"error": str(e)}

@router.get("/system-status")  
async def get_enhanced_system_status(current_user: dict = Depends(get_current_active_user)):
    """Get enhanced system status"""
    try:
        # Check if GROQ AI is working
        test_response = await ai_service.process_with_groq("Test message")
        
        return {
            "system_status": "fully_operational",
            "ai_status": "active" if test_response.get("confidence", 0) > 0 else "degraded",
            "features": {
                "groq_ai": bool(ai_service.groq_client),
                "workflow_execution": True,
                "integrations": True
            }
        }
    
    except Exception as e:
        logger.error(f"System status check failed: {str(e)}")
        return {
            "system_status": "degraded",
            "error": str(e)
        }