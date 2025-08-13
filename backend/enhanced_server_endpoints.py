"""
🚀 ENHANCED SERVER ENDPOINTS - All Phases Integration
New enhanced API endpoints that work seamlessly with existing FastAPI server
"""

from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from typing import Dict, List, Any, Optional
import logging

# Import server integration
from enhanced_server_integration import server_integration

# Import existing dependencies (assuming they exist in main server)
from server import verify_jwt_token, users_collection, workflows_collection, integrations_collection

logger = logging.getLogger(__name__)

# Create enhanced router
enhanced_router = APIRouter(prefix="/api/enhanced", tags=["enhanced"])

# =======================================
# ENHANCED DASHBOARD ENDPOINTS
# =======================================

@enhanced_router.get("/dashboard/quantum-stats")
async def get_quantum_dashboard_stats(user_id: str = Depends(verify_jwt_token)):
    """Get quantum-enhanced dashboard statistics - Works with existing UI"""
    try:
        # Get user context for personalization
        user_workflows = list(workflows_collection.find({"user_id": user_id}).limit(10))
        user_integrations = list(integrations_collection.find({"user_id": user_id}))
        
        user_context = {
            "workflows": user_workflows,
            "integrations": user_integrations,
            "workflow_count": len(user_workflows),
            "integration_count": len(user_integrations)
        }
        
        # Create base stats (simulate real dashboard data)
        base_stats = {
            "total_workflows": len(user_workflows),
            "total_executions": 156,
            "success_rate": 94.2,
            "failed_executions": 9,
            "total_integrations": len(user_integrations)
        }
        
        # Get quantum-enhanced stats
        enhanced_stats = await server_integration.get_enhanced_dashboard_stats(
            user_id, base_stats, user_context
        )
        
        return enhanced_stats
        
    except Exception as e:
        logger.error(f"Quantum dashboard stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve quantum dashboard stats")

# =======================================
# ENHANCED WORKFLOW ENDPOINTS
# =======================================

@enhanced_router.post("/workflows/{workflow_id}/execute-autonomous")
async def execute_autonomous_workflow(
    workflow_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(verify_jwt_token)
):
    """Execute workflow with full autonomous capabilities - Works with existing UI"""
    try:
        # Get workflow data
        workflow = workflows_collection.find_one({"_id": workflow_id, "user_id": user_id})
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Generate execution ID
        import uuid
        execution_id = str(uuid.uuid4())
        
        # Execute with autonomous enhancements
        enhanced_execution = await server_integration.execute_enhanced_workflow(
            execution_id, workflow_id, user_id, workflow, request, background_tasks
        )
        
        return enhanced_execution
        
    except Exception as e:
        logger.error(f"Autonomous execution error: {e}")
        raise HTTPException(status_code=500, detail="Failed to execute autonomous workflow")

# =======================================
# ENHANCED NODE LIBRARY ENDPOINTS
# =======================================

@enhanced_router.get("/nodes/quantum-library")
async def get_quantum_node_library():
    """Get quantum-enhanced node library - Works with existing UI"""
    try:
        # Create base node library (simulate existing nodes)
        base_nodes = {
            "categories": {
                "triggers": [
                    {"id": "http-webhook", "name": "HTTP Webhook", "description": "Receive HTTP webhooks"},
                    {"id": "schedule-trigger", "name": "Schedule Trigger", "description": "Time-based triggers"}
                ],
                "actions": [
                    {"id": "http-request", "name": "HTTP Request", "description": "Make HTTP requests"},
                    {"id": "email-send", "name": "Send Email", "description": "Send email notifications"}
                ]
            },
            "total_nodes": 45
        }
        
        # Enhance with quantum nodes
        enhanced_nodes = await server_integration.get_enhanced_node_types(base_nodes)
        
        return enhanced_nodes
        
    except Exception as e:
        logger.error(f"Quantum node library error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve quantum node library")

# =======================================
# ENHANCED AI ENDPOINTS
# =======================================

@enhanced_router.post("/ai/quantum-workflow-generation")
async def generate_quantum_ai_workflow(
    request_data: Dict[str, Any],
    user_id: str = Depends(verify_jwt_token)
):
    """Generate workflow with quantum AI consciousness - Works with existing UI"""
    try:
        prompt = request_data.get("prompt", "")
        structured = request_data.get("structured", True)
        session_id = request_data.get("session_id", f"session-{user_id}")
        
        # Get user context
        user_workflows = list(workflows_collection.find({"user_id": user_id}).limit(5))
        user_integrations = list(integrations_collection.find({"user_id": user_id}))
        
        user_context = {
            "existing_workflows": user_workflows,
            "integrations": user_integrations,
            "experience_level": "advanced" if len(user_workflows) > 5 else "beginner"
        }
        
        # Generate with quantum consciousness
        enhanced_response = await server_integration.generate_enhanced_ai_workflow(
            prompt, structured, session_id, user_context
        )
        
        return enhanced_response
        
    except Exception as e:
        logger.error(f"Quantum AI generation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate quantum AI workflow")

# =======================================
# ENHANCED TEMPLATE ENDPOINTS
# =======================================

@enhanced_router.get("/templates/futuristic")
async def get_futuristic_templates(category: Optional[str] = None):
    """Get futuristic templates with next-gen capabilities - Works with existing UI"""
    try:
        enhanced_templates = await server_integration.get_enhanced_templates(category)
        return enhanced_templates
        
    except Exception as e:
        logger.error(f"Futuristic templates error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve futuristic templates")

# =======================================
# ENHANCED COLLABORATION ENDPOINTS
# =======================================

@enhanced_router.get("/collaboration/enterprise-features")
async def get_enterprise_collaboration_features(
    workspace_id: Optional[str] = None,
    user_id: str = Depends(verify_jwt_token)
):
    """Get enterprise collaboration features - Minimal UI changes"""
    try:
        collaboration_features = await server_integration.get_enhanced_collaboration_features(
            user_id, workspace_id
        )
        
        return collaboration_features
        
    except Exception as e:
        logger.error(f"Enterprise collaboration error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve collaboration features")

# =======================================
# SYSTEM ENHANCEMENT ENDPOINTS
# =======================================

@enhanced_router.get("/system/enhancement-status")
async def get_enhancement_status():
    """Get comprehensive enhancement system status"""
    try:
        status = await server_integration.get_enhancement_status()
        return status
        
    except Exception as e:
        logger.error(f"Enhancement status error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve enhancement status")

# =======================================
# COMPATIBILITY ENDPOINTS (Zero UI Changes)
# =======================================

@enhanced_router.get("/compatibility/dashboard-stats")
async def get_compatible_dashboard_stats(user_id: str = Depends(verify_jwt_token)):
    """
    Enhanced dashboard stats that work with existing frontend components
    Returns enhanced data in exact same format as original /api/dashboard/stats
    """
    try:
        # Get enhanced stats in compatible format
        enhanced_stats = await get_quantum_dashboard_stats(user_id)
        
        # Ensure backward compatibility with existing UI
        compatible_stats = {
            # Original fields (required for existing UI)
            "total_workflows": enhanced_stats.get("total_workflows", 0),
            "total_executions": enhanced_stats.get("total_executions", 0),
            "success_rate": enhanced_stats.get("success_rate", 0),
            "failed_executions": enhanced_stats.get("failed_executions", 0),
            "recent_activities": enhanced_stats.get("recent_activities", []),
            
            # Enhanced fields (automatically displayed if UI supports them)
            **{k: v for k, v in enhanced_stats.items() 
               if k not in ["total_workflows", "total_executions", "success_rate", "failed_executions", "recent_activities"]}
        }
        
        return compatible_stats
        
    except Exception as e:
        logger.error(f"Compatible dashboard stats error: {e}")
        # Fallback to basic stats if enhancement fails
        return {
            "total_workflows": 0,
            "total_executions": 0,
            "success_rate": 0,
            "failed_executions": 0,
            "recent_activities": [],
            "enhancement_error": str(e)
        }

@enhanced_router.get("/compatibility/nodes")
async def get_compatible_nodes():
    """
    Enhanced nodes that work with existing workflow editor
    Returns enhanced nodes in exact same format as original /api/nodes
    """
    try:
        enhanced_nodes = await get_quantum_node_library()
        
        # Ensure backward compatibility
        compatible_nodes = {
            "categories": enhanced_nodes.get("categories", {}),
            # Additional enhanced data available but not disruptive
            **{k: v for k, v in enhanced_nodes.items() if k != "categories"}
        }
        
        return compatible_nodes
        
    except Exception as e:
        logger.error(f"Compatible nodes error: {e}")
        # Fallback to basic nodes
        return {
            "categories": {
                "triggers": [],
                "actions": [],
                "logic": []
            },
            "enhancement_error": str(e)
        }

# Export the enhanced router
def get_enhanced_router():
    """Get the enhanced API router for integration with main server"""
    return enhanced_router