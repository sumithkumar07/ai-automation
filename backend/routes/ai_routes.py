from fastapi import APIRouter, HTTPException, Depends
from models import AIWorkflowRequest, AIWorkflowResponse
from auth import get_current_active_user
from ai_service import ai_service
from database import get_database

router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/generate-workflow", response_model=AIWorkflowResponse)
async def generate_workflow_from_description(request: AIWorkflowRequest, current_user: dict = Depends(get_current_active_user)):
    """Generate a workflow from natural language description"""
    try:
        response = await ai_service.generate_workflow(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate workflow: {str(e)}")

@router.post("/optimize-workflow")
async def optimize_workflow(workflow_data: dict, current_user: dict = Depends(get_current_active_user)):
    """Optimize an existing workflow using AI"""
    try:
        optimization = await ai_service.optimize_workflow(workflow_data)
        return optimization
    except Exception as e:
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
        raise HTTPException(status_code=500, detail=f"Failed to generate insights: {str(e)}")

@router.post("/suggest-integrations")
async def suggest_integrations(description: str, current_user: dict = Depends(get_current_active_user)):
    """Suggest integrations based on workflow description"""
    # Mock AI suggestion for demo
    description_lower = description.lower()
    suggestions = []
    
    if "email" in description_lower:
        suggestions.append({"integration_id": "gmail", "confidence": 0.9, "reason": "Email functionality detected"})
    
    if "slack" in description_lower or "chat" in description_lower:
        suggestions.append({"integration_id": "slack", "confidence": 0.85, "reason": "Chat/messaging functionality detected"})
    
    if "spreadsheet" in description_lower or "data" in description_lower:
        suggestions.append({"integration_id": "google_sheets", "confidence": 0.8, "reason": "Data management functionality detected"})
    
    if "payment" in description_lower or "billing" in description_lower:
        suggestions.append({"integration_id": "stripe", "confidence": 0.75, "reason": "Payment functionality detected"})
    
    if "ai" in description_lower or "intelligence" in description_lower:
        suggestions.append({"integration_id": "openai", "confidence": 0.95, "reason": "AI functionality detected"})
    
    return {
        "suggestions": suggestions,
        "description_analyzed": description
    }

@router.post("/explain-workflow")
async def explain_workflow(workflow_data: dict, current_user: dict = Depends(get_current_active_user)):
    """Generate human-readable explanation of a workflow"""
    nodes = workflow_data.get("nodes", [])
    connections = workflow_data.get("connections", [])
    
    # Simple explanation generation (mock AI)
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
    
    return {
        "explanation": ". ".join(explanation),
        "complexity": "Simple" if len(nodes) <= 3 else "Medium" if len(nodes) <= 6 else "Complex",
        "estimated_execution_time": f"{len(nodes) * 2}-{len(nodes) * 5} seconds"
    }