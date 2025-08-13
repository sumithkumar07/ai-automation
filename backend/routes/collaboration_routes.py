"""
Real-time Collaboration Routes
Supports WebSocket connections for multi-user workflow editing
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Dict, Any
import json
import logging
from auth import get_current_active_user_ws
from websocket_manager import websocket_manager
from database import get_database

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/collaboration", tags=["collaboration"])

@router.websocket("/workflow/{workflow_id}")
async def workflow_collaboration_websocket(
    websocket: WebSocket,
    workflow_id: str,
    token: str = None
):
    """WebSocket endpoint for real-time workflow collaboration"""
    try:
        # Authenticate user (implement token-based auth for WebSocket)
        if not token:
            await websocket.close(code=4001, reason="Missing authentication token")
            return
        
        # For now, mock user info - in production, decode JWT token
        user_info = {
            "id": "user_123",
            "name": "Test User", 
            "email": "test@example.com",
            "avatar": None
        }
        
        # Connect to collaboration room
        connection_id = await websocket_manager.connect_to_workflow(
            websocket, workflow_id, user_info["id"], user_info
        )
        
        try:
            while True:
                # Receive messages from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle the message
                await websocket_manager.handle_message(connection_id, message)
                
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for connection {connection_id}")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        await websocket.close(code=4000, reason="Connection error")
    finally:
        # Clean up connection
        if 'connection_id' in locals():
            await websocket_manager.disconnect(connection_id)

@router.get("/workflow/{workflow_id}/collaborators")
async def get_workflow_collaborators(
    workflow_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Get active collaborators for a workflow"""
    try:
        # Verify user has access to workflow
        db = get_database()
        workflow = await db.workflows.find_one({
            "id": workflow_id,
            "user_id": current_user["user_id"]
        })
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        collaborators = await websocket_manager.get_active_collaborators(workflow_id)
        
        return {
            "workflow_id": workflow_id,
            "collaborators": collaborators,
            "total": len(collaborators)
        }
        
    except Exception as e:
        logger.error(f"Error getting collaborators: {e}")
        raise HTTPException(status_code=500, detail="Failed to get collaborators")

@router.post("/workflow/{workflow_id}/share")
async def share_workflow_for_collaboration(
    workflow_id: str,
    share_data: Dict[str, Any],
    current_user: dict = Depends(get_current_active_user)
):
    """Share workflow for collaboration with other users"""
    try:
        db = get_database()
        
        # Verify ownership
        workflow = await db.workflows.find_one({
            "id": workflow_id,
            "user_id": current_user["user_id"]
        })
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Create collaboration invitation
        collaboration = {
            "id": f"collab_{workflow_id}_{len(share_data.get('emails', []))}",
            "workflow_id": workflow_id,
            "owner_id": current_user["user_id"],
            "invited_users": share_data.get("emails", []),
            "permissions": share_data.get("permissions", "edit"),  # edit, view
            "created_at": datetime.utcnow(),
            "expires_at": share_data.get("expires_at"),
            "is_active": True
        }
        
        await db.collaborations.insert_one(collaboration)
        
        return {
            "message": "Workflow shared successfully",
            "collaboration_id": collaboration["id"],
            "invited_users": collaboration["invited_users"]
        }
        
    except Exception as e:
        logger.error(f"Error sharing workflow: {e}")
        raise HTTPException(status_code=500, detail="Failed to share workflow")

@router.get("/stats")
async def get_collaboration_stats(current_user: dict = Depends(get_current_active_user)):
    """Get collaboration statistics"""
    try:
        stats = websocket_manager.get_stats()
        
        return {
            "collaboration_stats": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting collaboration stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get stats")

@router.post("/workflow/{workflow_id}/broadcast")
async def broadcast_to_collaborators(
    workflow_id: str,
    message_data: Dict[str, Any],
    current_user: dict = Depends(get_current_active_user)
):
    """Broadcast message to all workflow collaborators"""
    try:
        # Verify access
        db = get_database()
        workflow = await db.workflows.find_one({
            "id": workflow_id,
            "user_id": current_user["user_id"]
        })
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Broadcast execution update to all collaborators
        await websocket_manager.broadcast_workflow_execution_update(
            workflow_id, 
            message_data
        )
        
        return {"message": "Broadcast sent successfully"}
        
    except Exception as e:
        logger.error(f"Error broadcasting message: {e}")
        raise HTTPException(status_code=500, detail="Failed to broadcast message")