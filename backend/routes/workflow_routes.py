from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from models import Workflow, WorkflowCreate, WorkflowUpdate, WorkflowExecution
from auth import get_current_active_user
from database import get_database
from workflow_engine import workflow_engine
from node_types_engine import node_types_engine
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/workflows", tags=["workflows"])

@router.post("/", response_model=dict)
async def create_workflow(workflow_data: WorkflowCreate, current_user: dict = Depends(get_current_active_user)):
    """Create a new workflow"""
    db = get_database()
    
    workflow = Workflow(
        user_id=current_user["user_id"],
        name=workflow_data.name,
        description=workflow_data.description
    )
    
    workflow_dict = workflow.dict()
    await db.workflows.insert_one(workflow_dict)
    
    logger.info(f"Created workflow {workflow.id} for user {current_user['user_id']}")
    return workflow_dict

@router.get("/", response_model=List[dict])
async def get_workflows(
    page: int = 1,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user)
):
    """Get all workflows for the current user with pagination"""
    db = get_database()
    
    skip = (page - 1) * limit
    cursor = db.workflows.find({"user_id": current_user["user_id"]}).skip(skip).limit(limit)
    workflows = await cursor.to_list(length=limit)
    
    # Add execution statistics
    for workflow in workflows:
        # Get recent execution count and success rate
        execution_count = await db.workflow_executions.count_documents({"workflow_id": workflow["id"]})
        successful_count = await db.workflow_executions.count_documents({
            "workflow_id": workflow["id"],
            "status": "success"
        })
        
        workflow["execution_stats"] = {
            "total_executions": execution_count,
            "success_rate": (successful_count / execution_count * 100) if execution_count > 0 else 0
        }
    
    return workflows

@router.get("/node-types")
async def get_node_types():
    """Get all available node types for the workflow editor"""
    return node_types_engine.get_node_types()

@router.get("/node-types/search")
async def search_node_types(q: str):
    """Search node types by name or description"""
    return node_types_engine.search_node_types(q)

@router.get("/{workflow_id}")
async def get_workflow(workflow_id: str, current_user: dict = Depends(get_current_active_user)):
    """Get a specific workflow"""
    db = get_database()
    
    workflow = await db.workflows.find_one({"id": workflow_id, "user_id": current_user["user_id"]})
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return workflow

@router.put("/{workflow_id}")
async def update_workflow(workflow_id: str, workflow_update: WorkflowUpdate, current_user: dict = Depends(get_current_active_user)):
    """Update a workflow"""
    db = get_database()
    
    # Check if workflow exists and belongs to user
    existing_workflow = await db.workflows.find_one({"id": workflow_id, "user_id": current_user["user_id"]})
    if not existing_workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Update workflow
    update_data = {k: v for k, v in workflow_update.dict(exclude_unset=True).items()}
    update_data["updated_at"] = datetime.utcnow()
    
    await db.workflows.update_one(
        {"id": workflow_id},
        {"$set": update_data}
    )
    
    logger.info(f"Updated workflow {workflow_id} for user {current_user['user_id']}")
    return {"message": "Workflow updated successfully"}

@router.post("/{workflow_id}/autosave")
async def autosave_workflow(workflow_id: str, workflow_data: dict, current_user: dict = Depends(get_current_active_user)):
    """Auto-save workflow data"""
    db = get_database()
    
    # Check if workflow exists and belongs to user
    existing_workflow = await db.workflows.find_one({"id": workflow_id, "user_id": current_user["user_id"]})
    if not existing_workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Update workflow with autosave data
    update_data = {
        "nodes": workflow_data.get("nodes", []),
        "connections": workflow_data.get("connections", []),
        "updated_at": datetime.utcnow()
    }
    
    if "triggers" in workflow_data:
        update_data["triggers"] = workflow_data["triggers"]
    
    await db.workflows.update_one(
        {"id": workflow_id},
        {"$set": update_data}
    )
    
    return {"message": "Workflow auto-saved successfully", "timestamp": update_data["updated_at"]}

@router.delete("/{workflow_id}")
async def delete_workflow(workflow_id: str, current_user: dict = Depends(get_current_active_user)):
    """Delete a workflow"""
    db = get_database()
    
    result = await db.workflows.delete_one({"id": workflow_id, "user_id": current_user["user_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Also delete associated executions
    await db.workflow_executions.delete_many({"workflow_id": workflow_id})
    
    logger.info(f"Deleted workflow {workflow_id} for user {current_user['user_id']}")
    return {"message": "Workflow deleted successfully"}

@router.post("/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: str, 
    trigger_data: dict = None,
    idempotency_key: str = None,
    current_user: dict = Depends(get_current_active_user)
):
    """Execute a workflow"""
    db = get_database()
    
    # Get workflow
    workflow_data = await db.workflows.find_one({"id": workflow_id, "user_id": current_user["user_id"]})
    if not workflow_data:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Check for duplicate execution if idempotency key provided
    if idempotency_key:
        existing_execution = await db.workflow_executions.find_one({
            "workflow_id": workflow_id,
            "idempotency_key": idempotency_key
        })
        if existing_execution:
            return existing_execution
    
    # Create workflow object
    workflow = Workflow(**workflow_data)
    
    # Execute workflow
    execution = await workflow_engine.execute_workflow(workflow, trigger_data or {})
    
    # Add idempotency key if provided
    execution_dict = execution.dict()
    if idempotency_key:
        execution_dict["idempotency_key"] = idempotency_key
    
    # Save execution to database
    await db.workflow_executions.insert_one(execution_dict)
    
    # Update workflow stats
    await db.workflows.update_one(
        {"id": workflow_id},
        {
            "$set": {"last_run": datetime.utcnow()},
            "$inc": {
                "run_count": 1,
                "success_count": 1 if execution.status == "success" else 0
            }
        }
    )
    
    logger.info(f"Executed workflow {workflow_id} with execution ID {execution.id}")
    return {
        "execution_id": execution.id,
        "status": execution.status.value,
        "message": "Workflow execution started successfully" if execution.status.value == "running" else f"Workflow execution {execution.status.value}"
    }

@router.get("/{workflow_id}/executions")
async def get_workflow_executions(workflow_id: str, limit: int = 50, current_user: dict = Depends(get_current_active_user)):
    """Get workflow execution history"""
    db = get_database()
    
    # Verify workflow belongs to user
    workflow = await db.workflows.find_one({"id": workflow_id, "user_id": current_user["user_id"]})
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Get executions
    cursor = db.workflow_executions.find({"workflow_id": workflow_id}).sort("started_at", -1).limit(limit)
    executions = await cursor.to_list(length=limit)
    
    return executions

@router.post("/{workflow_id}/duplicate")
async def duplicate_workflow(workflow_id: str, current_user: dict = Depends(get_current_active_user)):
    """Duplicate a workflow"""
    db = get_database()
    
    # Get original workflow
    original = await db.workflows.find_one({"id": workflow_id, "user_id": current_user["user_id"]})
    if not original:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Create duplicate
    duplicate = Workflow(
        user_id=current_user["user_id"],
        name=f"{original['name']} (Copy)",
        description=original.get("description"),
        nodes=original.get("nodes", []),
        connections=original.get("connections", [])
    )
    
    duplicate_dict = duplicate.dict()
    await db.workflows.insert_one(duplicate_dict)
    
    logger.info(f"Duplicated workflow {workflow_id} as {duplicate.id} for user {current_user['user_id']}")
    return duplicate_dict

@router.post("/{execution_id}/cancel")
async def cancel_workflow_execution(execution_id: str, current_user: dict = Depends(get_current_active_user)):
    """Cancel a running workflow execution"""
    success = workflow_engine.cancel_workflow(execution_id)
    if not success:
        raise HTTPException(status_code=404, detail="Running execution not found")
    
    logger.info(f"Cancelled workflow execution {execution_id}")
    return {"message": "Workflow execution cancelled"}

@router.get("/executions/running")
async def get_running_executions(current_user: dict = Depends(get_current_active_user)):
    """Get currently running workflow executions"""
    running_ids = workflow_engine.get_running_workflows()
    return {"running_executions": running_ids, "count": len(running_ids)}