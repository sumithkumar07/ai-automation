"""
WebSocket Manager for Real-time Collaboration
Supports multi-user workflow editing and live updates
"""
import json
import asyncio
import logging
from typing import Dict, List, Set, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class CollaborationRoom:
    """Manages a single workflow collaboration session"""
    
    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        self.connections: Dict[str, WebSocket] = {}
        self.user_cursors: Dict[str, Dict] = {}
        self.active_editors: Dict[str, Dict] = {}
        self.last_activity = datetime.utcnow()
        
    async def add_user(self, websocket: WebSocket, user_id: str, user_info: Dict):
        """Add user to collaboration room"""
        connection_id = str(uuid.uuid4())
        self.connections[connection_id] = websocket
        self.active_editors[connection_id] = {
            "user_id": user_id,
            "user_info": user_info,
            "joined_at": datetime.utcnow(),
            "connection_id": connection_id
        }
        
        # Notify other users about new collaborator
        await self.broadcast_user_joined(connection_id, user_info)
        
        # Send current collaborators to new user
        await self.send_current_collaborators(websocket, connection_id)
        
        return connection_id
    
    async def remove_user(self, connection_id: str):
        """Remove user from collaboration room"""
        if connection_id in self.connections:
            user_info = self.active_editors.get(connection_id, {}).get("user_info", {})
            del self.connections[connection_id]
            
            if connection_id in self.active_editors:
                del self.active_editors[connection_id]
                
            if connection_id in self.user_cursors:
                del self.user_cursors[connection_id]
            
            # Notify other users
            await self.broadcast_user_left(connection_id, user_info)
    
    async def broadcast_user_joined(self, new_connection_id: str, user_info: Dict):
        """Notify all users about new collaborator"""
        message = {
            "type": "user_joined",
            "user": user_info,
            "connection_id": new_connection_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_to_others(new_connection_id, message)
    
    async def broadcast_user_left(self, left_connection_id: str, user_info: Dict):
        """Notify all users about user leaving"""
        message = {
            "type": "user_left", 
            "user": user_info,
            "connection_id": left_connection_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_to_all(message)
    
    async def send_current_collaborators(self, websocket: WebSocket, excluding_connection_id: str):
        """Send list of current collaborators to new user"""
        collaborators = [
            {
                "connection_id": conn_id,
                **editor_info
            }
            for conn_id, editor_info in self.active_editors.items()
            if conn_id != excluding_connection_id
        ]
        
        message = {
            "type": "current_collaborators",
            "collaborators": collaborators,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Failed to send collaborators list: {e}")
    
    async def handle_workflow_change(self, connection_id: str, change_data: Dict):
        """Handle workflow changes from a user"""
        user_info = self.active_editors.get(connection_id, {}).get("user_info", {})
        
        message = {
            "type": "workflow_change",
            "change": change_data,
            "user": user_info,
            "connection_id": connection_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Broadcast to all other users
        await self.broadcast_to_others(connection_id, message)
        self.last_activity = datetime.utcnow()
    
    async def handle_cursor_update(self, connection_id: str, cursor_data: Dict):
        """Handle cursor position updates"""
        self.user_cursors[connection_id] = {
            **cursor_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        user_info = self.active_editors.get(connection_id, {}).get("user_info", {})
        
        message = {
            "type": "cursor_update",
            "cursor": cursor_data,
            "user": user_info,
            "connection_id": connection_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.broadcast_to_others(connection_id, message)
    
    async def broadcast_to_all(self, message: Dict):
        """Broadcast message to all users in room"""
        if not self.connections:
            return
            
        message_json = json.dumps(message)
        disconnected = []
        
        for connection_id, websocket in self.connections.items():
            try:
                await websocket.send_text(message_json)
            except Exception as e:
                logger.error(f"Failed to send message to {connection_id}: {e}")
                disconnected.append(connection_id)
        
        # Clean up disconnected connections
        for connection_id in disconnected:
            await self.remove_user(connection_id)
    
    async def broadcast_to_others(self, sender_connection_id: str, message: Dict):
        """Broadcast message to all users except sender"""
        message_json = json.dumps(message)
        disconnected = []
        
        for connection_id, websocket in self.connections.items():
            if connection_id == sender_connection_id:
                continue
                
            try:
                await websocket.send_text(message_json)
            except Exception as e:
                logger.error(f"Failed to send message to {connection_id}: {e}")
                disconnected.append(connection_id)
        
        # Clean up disconnected connections
        for connection_id in disconnected:
            await self.remove_user(connection_id)
    
    def is_empty(self) -> bool:
        """Check if room has no active connections"""
        return len(self.connections) == 0


class WebSocketManager:
    """Manages WebSocket connections for real-time collaboration"""
    
    def __init__(self):
        self.rooms: Dict[str, CollaborationRoom] = {}
        self.connection_to_room: Dict[str, str] = {}
        
    async def connect_to_workflow(self, websocket: WebSocket, workflow_id: str, user_id: str, user_info: Dict) -> str:
        """Connect user to workflow collaboration room"""
        await websocket.accept()
        
        # Create room if it doesn't exist
        if workflow_id not in self.rooms:
            self.rooms[workflow_id] = CollaborationRoom(workflow_id)
        
        room = self.rooms[workflow_id]
        connection_id = await room.add_user(websocket, user_id, user_info)
        self.connection_to_room[connection_id] = workflow_id
        
        logger.info(f"User {user_id} connected to workflow {workflow_id} with connection {connection_id}")
        return connection_id
    
    async def disconnect(self, connection_id: str):
        """Disconnect user from collaboration"""
        if connection_id not in self.connection_to_room:
            return
            
        workflow_id = self.connection_to_room[connection_id]
        room = self.rooms.get(workflow_id)
        
        if room:
            await room.remove_user(connection_id)
            
            # Clean up empty rooms
            if room.is_empty():
                del self.rooms[workflow_id]
                logger.info(f"Removed empty collaboration room for workflow {workflow_id}")
        
        del self.connection_to_room[connection_id]
        logger.info(f"Disconnected connection {connection_id} from workflow {workflow_id}")
    
    async def handle_message(self, connection_id: str, message: Dict):
        """Handle incoming WebSocket message"""
        if connection_id not in self.connection_to_room:
            logger.error(f"Message from unknown connection {connection_id}")
            return
            
        workflow_id = self.connection_to_room[connection_id]
        room = self.rooms.get(workflow_id)
        
        if not room:
            logger.error(f"Room not found for workflow {workflow_id}")
            return
        
        message_type = message.get("type")
        
        if message_type == "workflow_change":
            await room.handle_workflow_change(connection_id, message.get("data", {}))
        elif message_type == "cursor_update":
            await room.handle_cursor_update(connection_id, message.get("data", {}))
        elif message_type == "ping":
            # Respond to ping for connection health
            await self.send_to_connection(connection_id, {"type": "pong"})
        else:
            logger.warning(f"Unknown message type: {message_type}")
    
    async def send_to_connection(self, connection_id: str, message: Dict):
        """Send message to specific connection"""
        if connection_id not in self.connection_to_room:
            return False
            
        workflow_id = self.connection_to_room[connection_id]
        room = self.rooms.get(workflow_id)
        
        if room and connection_id in room.connections:
            try:
                websocket = room.connections[connection_id]
                await websocket.send_text(json.dumps(message))
                return True
            except Exception as e:
                logger.error(f"Failed to send message to {connection_id}: {e}")
                await self.disconnect(connection_id)
                return False
        
        return False
    
    async def broadcast_workflow_execution_update(self, workflow_id: str, execution_data: Dict):
        """Broadcast workflow execution updates to all collaborators"""
        room = self.rooms.get(workflow_id)
        if room:
            message = {
                "type": "workflow_execution_update",
                "execution": execution_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            await room.broadcast_to_all(message)
    
    async def get_active_collaborators(self, workflow_id: str) -> List[Dict]:
        """Get list of active collaborators for a workflow"""
        room = self.rooms.get(workflow_id)
        if room:
            return [
                {
                    "connection_id": conn_id,
                    **editor_info
                }
                for conn_id, editor_info in room.active_editors.items()
            ]
        return []
    
    def get_stats(self) -> Dict:
        """Get WebSocket connection statistics"""
        total_connections = sum(len(room.connections) for room in self.rooms.values())
        active_rooms = len(self.rooms)
        
        return {
            "active_rooms": active_rooms,
            "total_connections": total_connections,
            "rooms": {
                workflow_id: {
                    "connections": len(room.connections),
                    "last_activity": room.last_activity.isoformat()
                }
                for workflow_id, room in self.rooms.items()
            }
        }

# Global WebSocket manager instance
websocket_manager = WebSocketManager()