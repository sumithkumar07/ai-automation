from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from models import Workflow, WorkflowCreate, WorkflowUpdate, WorkflowExecution
from auth import get_current_active_user
from database import get_database
from workflow_engine import workflow_engine
from datetime import datetime

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
    
    return workflow_dict

@router.get("/", response_model=List[dict])
async def get_workflows(current_user: dict = Depends(get_current_active_user)):
    """Get all workflows for the current user"""
    db = get_database()
    
    cursor = db.workflows.find({"user_id": current_user["user_id"]})
    workflows = await cursor.to_list(length=100)
    
    return workflows

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
    
    return {"message": "Workflow updated successfully"}

@router.delete("/{workflow_id}")
async def delete_workflow(workflow_id: str, current_user: dict = Depends(get_current_active_user)):
    """Delete a workflow"""
    db = get_database()
    
    result = await db.workflows.delete_one({"id": workflow_id, "user_id": current_user["user_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return {"message": "Workflow deleted successfully"}

@router.post("/{workflow_id}/execute")
async def execute_workflow(workflow_id: str, trigger_data: dict = None, current_user: dict = Depends(get_current_active_user)):
    """Execute a workflow"""
    db = get_database()
    
    # Get workflow
    workflow_data = await db.workflows.find_one({"id": workflow_id, "user_id": current_user["user_id"]})
    if not workflow_data:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Create workflow object
    workflow = Workflow(**workflow_data)
    
    # Execute workflow
    execution = await workflow_engine.execute_workflow(workflow, trigger_data or {})
    
    # Save execution to database
    await db.workflow_executions.insert_one(execution.dict())
    
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
    
    return execution.dict()

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
    
    return duplicate_dict

@router.get("/{workflow_id}/cancel")
async def cancel_workflow_execution(execution_id: str, current_user: dict = Depends(get_current_active_user)):
    """Cancel a running workflow execution"""
    success = workflow_engine.cancel_workflow(execution_id)
    if not success:
        raise HTTPException(status_code=404, detail="Running execution not found")
    
    return {"message": "Workflow execution cancelled"}