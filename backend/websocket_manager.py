# Real-time WebSocket Manager for Live Updates
import asyncio
import json
from typing import Dict, List, Set, Optional, Any
from datetime import datetime
import logging
from fastapi import WebSocket, WebSocketDisconnect
from dataclasses import dataclass, asdict
import uuid

logger = logging.getLogger(__name__)

@dataclass
class WebSocketMessage:
    type: str
    data: Dict[str, Any]
    user_id: Optional[str] = None
    workflow_id: Optional[str] = None
    execution_id: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()

class WebSocketConnectionManager:
    """Manage WebSocket connections for real-time updates"""
    
    def __init__(self):
        # Store active connections by user
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Store connection metadata
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
        # Store subscriptions (user_id -> set of topics they're subscribed to)
        self.subscriptions: Dict[str, Set[str]] = {}
        # Connection statistics
        self.connection_stats = {
            "total_connections": 0,
            "current_connections": 0,
            "messages_sent": 0,
            "messages_received": 0
        }
    
    async def connect(self, websocket: WebSocket, user_id: str, client_info: Dict = None):
        """Accept a new WebSocket connection"""
        try:
            await websocket.accept()
            
            # Initialize user connections if not exists
            if user_id not in self.active_connections:
                self.active_connections[user_id] = set()
            
            # Add connection
            self.active_connections[user_id].add(websocket)
            
            # Store metadata
            self.connection_metadata[websocket] = {
                "user_id": user_id,
                "connected_at": datetime.utcnow().isoformat(),
                "client_info": client_info or {},
                "connection_id": str(uuid.uuid4())[:8]
            }
            
            # Initialize subscriptions
            if user_id not in self.subscriptions:
                self.subscriptions[user_id] = set()
            
            # Update stats
            self.connection_stats["total_connections"] += 1
            self.connection_stats["current_connections"] += 1
            
            logger.info(f"WebSocket connected for user {user_id}. Total connections: {self.connection_stats['current_connections']}")
            
            # Send connection confirmation
            await self.send_personal_message({
                "type": "connection_established",
                "data": {
                    "connection_id": self.connection_metadata[websocket]["connection_id"],
                    "server_time": datetime.utcnow().isoformat(),
                    "supported_events": [
                        "workflow_execution_started",
                        "workflow_execution_progress", 
                        "workflow_execution_completed",
                        "workflow_execution_failed",
                        "node_execution_update",
                        "system_notification"
                    ]
                }
            }, websocket)
            
        except Exception as e:
            logger.error(f"Error connecting WebSocket for user {user_id}: {e}")
            raise
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        try:
            metadata = self.connection_metadata.get(websocket)
            if metadata:
                user_id = metadata["user_id"]
                
                # Remove from active connections
                if user_id in self.active_connections:
                    self.active_connections[user_id].discard(websocket)
                    
                    # Clean up empty user connections
                    if not self.active_connections[user_id]:
                        del self.active_connections[user_id]
                        if user_id in self.subscriptions:
                            del self.subscriptions[user_id]
                
                # Remove metadata
                del self.connection_metadata[websocket]
                
                # Update stats
                self.connection_stats["current_connections"] -= 1
                
                logger.info(f"WebSocket disconnected for user {user_id}. Remaining connections: {self.connection_stats['current_connections']}")
            
        except Exception as e:
            logger.error(f"Error disconnecting WebSocket: {e}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send message to a specific WebSocket connection"""
        try:
            await websocket.send_text(json.dumps(message))
            self.connection_stats["messages_sent"] += 1
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def send_user_message(self, user_id: str, message: Dict[str, Any]):
        """Send message to all connections for a specific user"""
        if user_id in self.active_connections:
            disconnected_connections = set()
            
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_text(json.dumps(message))
                    self.connection_stats["messages_sent"] += 1
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {e}")
                    disconnected_connections.add(websocket)
            
            # Clean up disconnected connections
            for websocket in disconnected_connections:
                self.disconnect(websocket)
    
    async def broadcast_to_subscribers(self, topic: str, message: Dict[str, Any]):
        """Broadcast message to all users subscribed to a topic"""
        for user_id, topics in self.subscriptions.items():
            if topic in topics:
                await self.send_user_message(user_id, message)
    
    async def subscribe_user_to_topic(self, user_id: str, topic: str):
        """Subscribe a user to a specific topic"""
        if user_id not in self.subscriptions:
            self.subscriptions[user_id] = set()
        
        self.subscriptions[user_id].add(topic)
        
        # Notify user about subscription
        await self.send_user_message(user_id, {
            "type": "subscription_confirmed",
            "data": {
                "topic": topic,
                "subscribed_at": datetime.utcnow().isoformat()
            }
        })
    
    async def unsubscribe_user_from_topic(self, user_id: str, topic: str):
        """Unsubscribe a user from a specific topic"""
        if user_id in self.subscriptions:
            self.subscriptions[user_id].discard(topic)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            **self.connection_stats,
            "users_connected": len(self.active_connections),
            "active_subscriptions": sum(len(topics) for topics in self.subscriptions.values()),
            "connections_by_user": {
                user_id: len(connections) 
                for user_id, connections in self.active_connections.items()
            }
        }
    
    def get_user_connections(self, user_id: str) -> List[Dict[str, Any]]:
        """Get connection info for a specific user"""
        connections = []
        if user_id in self.active_connections:
            for websocket in self.active_connections[user_id]:
                metadata = self.connection_metadata.get(websocket, {})
                connections.append({
                    "connection_id": metadata.get("connection_id"),
                    "connected_at": metadata.get("connected_at"),
                    "client_info": metadata.get("client_info", {})
                })
        return connections

# Real-time Event Handlers
class RealTimeEventHandler:
    """Handle real-time events and notifications"""
    
    def __init__(self, connection_manager: WebSocketConnectionManager):
        self.connection_manager = connection_manager
        self.event_queue = asyncio.Queue()
        self.is_processing = False
    
    async def start_event_processor(self):
        """Start the event processing loop"""
        if self.is_processing:
            return
        
        self.is_processing = True
        logger.info("Real-time event processor started")
        
        while self.is_processing:
            try:
                # Wait for events with timeout
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                await self._process_event(event)
                self.event_queue.task_done()
            except asyncio.TimeoutError:
                continue  # No events, continue loop
            except Exception as e:
                logger.error(f"Error processing real-time event: {e}")
    
    async def stop_event_processor(self):
        """Stop the event processing loop"""
        self.is_processing = False
        logger.info("Real-time event processor stopped")
    
    async def emit_event(self, event_type: str, data: Dict[str, Any], user_id: str = None, workflow_id: str = None):
        """Emit a real-time event"""
        event = WebSocketMessage(
            type=event_type,
            data=data,
            user_id=user_id,
            workflow_id=workflow_id
        )
        await self.event_queue.put(event)
    
    async def _process_event(self, event: WebSocketMessage):
        """Process a single event"""
        try:
            message = asdict(event)
            
            if event.user_id:
                # Send to specific user
                await self.connection_manager.send_user_message(event.user_id, message)
            else:
                # Broadcast to all subscribed users
                topic = f"workflow_{event.workflow_id}" if event.workflow_id else "global"
                await self.connection_manager.broadcast_to_subscribers(topic, message)
                
        except Exception as e:
            logger.error(f"Error processing event {event.type}: {e}")
    
    # Specific event handlers
    async def workflow_execution_started(self, user_id: str, workflow_id: str, execution_id: str, workflow_name: str = ""):
        """Handle workflow execution started event"""
        await self.emit_event(
            "workflow_execution_started",
            {
                "execution_id": execution_id,
                "workflow_id": workflow_id,
                "workflow_name": workflow_name,
                "status": "running",
                "started_at": datetime.utcnow().isoformat()
            },
            user_id=user_id,
            workflow_id=workflow_id
        )
    
    async def workflow_execution_progress(self, user_id: str, workflow_id: str, execution_id: str, progress: Dict[str, Any]):
        """Handle workflow execution progress event"""
        await self.emit_event(
            "workflow_execution_progress",
            {
                "execution_id": execution_id,
                "workflow_id": workflow_id,
                "progress": progress,
                "updated_at": datetime.utcnow().isoformat()
            },
            user_id=user_id,
            workflow_id=workflow_id
        )
    
    async def workflow_execution_completed(self, user_id: str, workflow_id: str, execution_id: str, result: Dict[str, Any]):
        """Handle workflow execution completed event"""
        await self.emit_event(
            "workflow_execution_completed",
            {
                "execution_id": execution_id,
                "workflow_id": workflow_id,
                "status": "success",
                "result": result,
                "completed_at": datetime.utcnow().isoformat()
            },
            user_id=user_id,
            workflow_id=workflow_id
        )
    
    async def workflow_execution_failed(self, user_id: str, workflow_id: str, execution_id: str, error: str):
        """Handle workflow execution failed event"""
        await self.emit_event(
            "workflow_execution_failed",
            {
                "execution_id": execution_id,
                "workflow_id": workflow_id,
                "status": "failed",
                "error": error,
                "failed_at": datetime.utcnow().isoformat()
            },
            user_id=user_id,
            workflow_id=workflow_id
        )
    
    async def node_execution_update(self, user_id: str, workflow_id: str, execution_id: str, node_id: str, node_data: Dict[str, Any]):
        """Handle individual node execution update"""
        await self.emit_event(
            "node_execution_update",
            {
                "execution_id": execution_id,
                "workflow_id": workflow_id,
                "node_id": node_id,
                "node_data": node_data,
                "updated_at": datetime.utcnow().isoformat()
            },
            user_id=user_id,
            workflow_id=workflow_id
        )
    
    async def system_notification(self, user_id: str, notification_type: str, title: str, message: str, priority: str = "normal"):
        """Send system notification to user"""
        await self.emit_event(
            "system_notification",
            {
                "notification_type": notification_type,
                "title": title,
                "message": message,
                "priority": priority,
                "created_at": datetime.utcnow().isoformat()
            },
            user_id=user_id
        )

# Global instances
websocket_manager = WebSocketConnectionManager()
realtime_event_handler = RealTimeEventHandler(websocket_manager)

# Start event processor on module load
async def start_realtime_services():
    """Start real-time services"""
    await realtime_event_handler.start_event_processor()

async def stop_realtime_services():
    """Stop real-time services"""
    await realtime_event_handler.stop_event_processor()