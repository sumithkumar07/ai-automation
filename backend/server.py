from fastapi import FastAPI, APIRouter, Depends, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List
import uuid
from datetime import datetime

# Import new modules
from database import connect_to_mongo, close_mongo_connection
from routes import auth_routes, workflow_routes, integration_routes, ai_routes, dashboard_routes, collaboration_routes, analytics_routes, templates_routes, integration_testing_routes, performance_routes
from node_types_engine import node_types_engine

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create the main app without a prefix
app = FastAPI(
    title="Aether Automation API",
    description="AI-Powered Workflow Automation Platform",
    version="1.0.0"
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Legacy endpoint for backward compatibility
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

# Node types endpoints
@api_router.get("/node-types")
async def get_node_types():
    """Get all available node types"""
    return node_types_engine.get_node_types()

@api_router.get("/nodes")
async def get_nodes():
    """Get all available nodes (alias for node-types for better API compatibility)"""
    return node_types_engine.get_node_types()

@api_router.get("/nodes/search")
async def search_nodes(q: str = None, query: str = None):
    """Search node types by name or description"""
    search_term = q or query
    if not search_term:
        return node_types_engine.get_node_types()
    
    return {
        "results": node_types_engine.search_node_types(search_term),
        "query": search_term
    }

# Legacy status check models and endpoints
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    from database import get_database
    db = get_database()
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    from database import get_database
    db = get_database()
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Additional execution status endpoints for better API compatibility
@api_router.get("/executions/{execution_id}/status")
async def get_execution_status_alternative(execution_id: str, current_user: dict = Depends(auth_routes.get_current_active_user)):
    """Alternative execution status endpoint for compatibility"""
    try:
        from database import get_database
        from workflow_engine import workflow_engine
        
        db = get_database()
        
        # Get execution from database
        execution = await db.workflow_executions.find_one({"id": execution_id})
        if not execution:
            # Check if it's a running execution
            running_ids = workflow_engine.get_running_workflows()
            if execution_id in running_ids:
                return {
                    "execution_id": execution_id,
                    "status": "running",
                    "progress": "in_progress",
                    "started_at": datetime.utcnow().isoformat(),
                    "is_running": True
                }
            else:
                raise HTTPException(status_code=404, detail="Execution not found")
        
        # Verify user has access to this execution
        workflow = await db.workflows.find_one({"id": execution["workflow_id"]})
        if not workflow or workflow["user_id"] != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return {
            "execution_id": execution_id,
            "status": execution.get("status", "unknown"),
            "progress": execution.get("progress", "unknown"),
            "started_at": execution.get("started_at", "").isoformat() if execution.get("started_at") else None,
            "completed_at": execution.get("completed_at", "").isoformat() if execution.get("completed_at") else None,
            "duration": execution.get("duration", 0),
            "result": execution.get("result", {}),
            "error": execution.get("error"),
            "is_running": execution.get("status") == "running"
        }
        
    except Exception as e:
        logger.error(f"Error getting execution status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get execution status")

# Include all new route modules
api_router.include_router(auth_routes.router)
api_router.include_router(workflow_routes.router)
api_router.include_router(integration_routes.router)
api_router.include_router(ai_routes.router)
api_router.include_router(dashboard_routes.router)
api_router.include_router(collaboration_routes.router)
api_router.include_router(analytics_routes.router)
api_router.include_router(templates_routes.router)
api_router.include_router(integration_testing_routes.router)
api_router.include_router(performance_routes.router)

# Include enhanced router for new capabilities
try:
    from enhanced_api_routes import get_enhanced_router
    enhanced_router = get_enhanced_router()
    # Remove prefix since we're including it in api_router which already has /api prefix
    enhanced_router.prefix = "/enhanced"  
    api_router.include_router(enhanced_router)
    logging.info("✅ Enhanced API routes loaded successfully")
except ImportError as e:
    logging.warning(f"⚠️ Enhanced API routes not available: {e}")
except Exception as e:
    logging.error(f"❌ Error loading enhanced API routes: {e}")

# Include the router in the main app
app.include_router(api_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection events
@app.on_event("startup")
async def startup_db_client():
    """Initialize database connection"""
    await connect_to_mongo()
    logging.info("Connected to MongoDB")

@app.on_event("shutdown")
async def shutdown_db_client():
    """Close database connection"""
    await close_mongo_connection()
    logging.info("Disconnected from MongoDB")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
