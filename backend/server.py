from fastapi import FastAPI, APIRouter
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
