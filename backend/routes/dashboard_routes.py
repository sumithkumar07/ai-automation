from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from models import DashboardStats, WorkflowExecution
from auth import get_current_active_user
from database import get_database
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/stats")
async def get_dashboard_stats(current_user: dict = Depends(get_current_active_user)) -> Dict[str, Any]:
    """Get dashboard statistics for the current user"""
    db = get_database()
    user_id = current_user["user_id"]
    
    # Get workflow stats
    total_workflows = await db.workflows.count_documents({"user_id": user_id})
    active_workflows = await db.workflows.count_documents({"user_id": user_id, "status": "active"})
    
    # Get execution stats
    total_executions = await db.workflow_executions.count_documents({"user_id": user_id})
    successful_executions = await db.workflow_executions.count_documents({
        "user_id": user_id, 
        "status": "success"
    })
    failed_executions = await db.workflow_executions.count_documents({
        "user_id": user_id,
        "status": "failed"
    })
    
    # Calculate success rate
    success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 100
    
    # Get integration stats
    integrations_connected = await db.user_integrations.count_documents({
        "user_id": user_id, 
        "is_active": True
    })
    
    # Get recent executions
    cursor = db.workflow_executions.find({"user_id": user_id}).sort("started_at", -1).limit(10)
    recent_executions_data = await cursor.to_list(length=10)
    
    return {
        "total_workflows": total_workflows,
        "active_workflows": active_workflows,
        "total_executions": total_executions,
        "successful_executions": successful_executions,
        "failed_executions": failed_executions,
        "success_rate": round(success_rate, 1),
        "integrations_connected": integrations_connected,
        "recent_executions": recent_executions_data
    }

@router.get("/checklist")
async def get_user_checklist(current_user: dict = Depends(get_current_active_user)) -> Dict[str, Any]:
    """Get user onboarding checklist"""
    db = get_database()
    user_id = current_user["user_id"]
    
    # Check completion criteria
    has_any_workflow = await db.workflows.count_documents({"user_id": user_id}) > 0
    has_any_integration = await db.user_integrations.count_documents({"user_id": user_id, "is_active": True}) > 0
    has_any_execution = await db.workflow_executions.count_documents({"user_id": user_id}) > 0
    
    # Calculate completion percentage
    completed_items = sum([has_any_workflow, has_any_integration, has_any_execution])
    completion_percentage = (completed_items / 3) * 100
    
    return {
        "has_any_workflow": has_any_workflow,
        "has_any_integration": has_any_integration,
        "has_any_execution": has_any_execution,
        "completion_percentage": completion_percentage,
        "total_items": 3,
        "completed_items": completed_items
    }

@router.get("/activity")
async def get_activity_feed(current_user: dict = Depends(get_current_active_user), limit: int = 20):
    """Get recent activity feed"""
    db = get_database()
    user_id = current_user["user_id"]
    
    # Combine different types of activities
    activities = []
    
    # Recent workflow executions
    cursor = db.workflow_executions.find({"user_id": user_id}).sort("started_at", -1).limit(limit // 2)
    executions = await cursor.to_list(length=limit // 2)
    
    for execution in executions:
        workflow = await db.workflows.find_one({"id": execution["workflow_id"]})
        activities.append({
            "type": "execution",
            "timestamp": execution["started_at"],
            "message": f"Workflow '{workflow['name'] if workflow else 'Unknown'}' {'completed successfully' if execution['status'] == 'success' else 'failed'}",
            "status": execution["status"],
            "workflow_id": execution["workflow_id"]
        })
    
    # Recent workflow creations/updates
    cursor = db.workflows.find({"user_id": user_id}).sort("updated_at", -1).limit(limit // 2)
    workflows = await cursor.to_list(length=limit // 2)
    
    for workflow in workflows:
        if workflow["created_at"] == workflow["updated_at"]:
            message = f"Created workflow '{workflow['name']}'"
        else:
            message = f"Updated workflow '{workflow['name']}'"
        
        activities.append({
            "type": "workflow",
            "timestamp": workflow["updated_at"],
            "message": message,
            "workflow_id": workflow["id"]
        })
    
    # Sort all activities by timestamp
    activities.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return activities[:limit]

@router.get("/analytics/execution-trends")
async def get_execution_trends(current_user: dict = Depends(get_current_active_user), days: int = 30):
    """Get execution trends over time"""
    db = get_database()
    user_id = current_user["user_id"]
    
    # Get executions from the last N days
    start_date = datetime.utcnow() - timedelta(days=days)
    
    cursor = db.workflow_executions.find({
        "user_id": user_id,
        "started_at": {"$gte": start_date}
    }).sort("started_at", 1)
    
    executions = await cursor.to_list(length=1000)
    
    # Group by day
    daily_stats = {}
    for execution in executions:
        date_key = execution["started_at"].date().isoformat()
        if date_key not in daily_stats:
            daily_stats[date_key] = {"total": 0, "successful": 0}
        
        daily_stats[date_key]["total"] += 1
        if execution["status"] == "success":
            daily_stats[date_key]["successful"] += 1
    
    # Convert to list format for charts
    trends = []
    for date_str, stats in daily_stats.items():
        trends.append({
            "date": date_str,
            "total_executions": stats["total"],
            "successful_executions": stats["successful"],
            "success_rate": (stats["successful"] / stats["total"] * 100) if stats["total"] > 0 else 0
        })
    
    return sorted(trends, key=lambda x: x["date"])

@router.get("/analytics/workflow-performance")
async def get_workflow_performance(current_user: dict = Depends(get_current_active_user)):
    """Get workflow performance metrics"""
    db = get_database()
    user_id = current_user["user_id"]
    
    # Get workflows with their execution stats
    workflows = await db.workflows.find({"user_id": user_id}).to_list(length=100)
    
    performance_data = []
    for workflow in workflows:
        # Get execution stats for this workflow
        total_executions = await db.workflow_executions.count_documents({"workflow_id": workflow["id"]})
        successful_executions = await db.workflow_executions.count_documents({
            "workflow_id": workflow["id"],
            "status": "success"
        })
        
        success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
        
        performance_data.append({
            "workflow_id": workflow["id"],
            "workflow_name": workflow["name"],
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "success_rate": success_rate,
            "status": workflow["status"],
            "last_run": workflow.get("last_run")
        })
    
    # Sort by total executions desc
    performance_data.sort(key=lambda x: x["total_executions"], reverse=True)
    
    return performance_data

@router.get("/analytics/integration-usage")
async def get_integration_usage(current_user: dict = Depends(get_current_active_user)):
    """Get integration usage statistics"""
    db = get_database()
    user_id = current_user["user_id"]
    
    # Get all user's workflows
    workflows = await db.workflows.find({"user_id": user_id}).to_list(length=100)
    
    integration_usage = {}
    
    for workflow in workflows:
        nodes = workflow.get("nodes", [])
        for node in nodes:
            integration = node.get("integration")
            if integration:
                if integration not in integration_usage:
                    integration_usage[integration] = {
                        "integration_id": integration,
                        "usage_count": 0,
                        "workflows": []
                    }
                
                integration_usage[integration]["usage_count"] += 1
                if workflow["id"] not in [w["id"] for w in integration_usage[integration]["workflows"]]:
                    integration_usage[integration]["workflows"].append({
                        "id": workflow["id"],
                        "name": workflow["name"]
                    })
    
    return list(integration_usage.values())