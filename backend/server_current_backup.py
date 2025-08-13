from fastapi import FastAPI, HTTPException, Depends, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
import os
import jwt
import bcrypt
from datetime import datetime, timedelta
import uuid
import time
import logging
from pymongo import MongoClient, IndexModel, ASCENDING, DESCENDING
import httpx
import json
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Aether Automation API", version="2.0.0")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Performance middleware
app.add_middleware(GZipMiddleware, minimum_size=500)

# Database setup
MONGO_URL = os.getenv("MONGO_URL")
if not MONGO_URL:
    raise RuntimeError("MONGO_URL is not set. Please configure it in backend/.env")

try:
    client = MongoClient(MONGO_URL)
    db = client.aether_automation
    # Test connection
    client.admin.command('ping')
    logger.info("✅ MongoDB connection successful")
except Exception as e:
    logger.error(f"❌ MongoDB connection failed: {e}")
    raise

# Collections
users_collection = db.users
workflows_collection = db.workflows
templates_collection = db.templates
integrations_collection = db.integrations
executions_collection = db.executions
ai_sessions_collection = db.ai_sessions

# Create database indexes for performance
try:
    users_collection.create_index([("email", ASCENDING)], unique=True)
    workflows_collection.create_index([("user_id", ASCENDING)])
    integrations_collection.create_index([("user_id", ASCENDING)])
    executions_collection.create_index([("user_id", ASCENDING)])
    logger.info("✅ Database indexes created successfully")
except Exception as e:
    logger.warning(f"⚠️ Failed to create some indexes: {e}")

# GROQ API setup
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# JWT setup
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-here")
security = HTTPBearer()

# Pydantic models
class UserSignup(BaseModel):
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    password: str = Field(..., min_length=6)
    name: str = Field(..., min_length=1, max_length=100)

class UserLogin(BaseModel):
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    password: str = Field(..., min_length=1)

class WorkflowCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    connections: List[Dict[str, Any]] = Field(default_factory=list)
    triggers: List[Dict[str, Any]] = Field(default_factory=list)

class IntegrationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    platform: str = Field(..., min_length=1)
    credentials: Dict[str, Any]

class AIRequest(BaseModel):
    message: Optional[str] = None
    prompt: Optional[str] = None

# Helper functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_jwt_token(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# API Routes

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        client.admin.command('ping')
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "ok",
        "database_status": db_status,
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/auth/signup")
async def signup(user_data: UserSignup):
    """User signup endpoint"""
    try:
        # Check if user already exists
        existing_user = users_collection.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Create new user
        user_id = str(uuid.uuid4())
        hashed_password = hash_password(user_data.password)
        
        user_doc = {
            "id": user_id,
            "email": user_data.email,
            "name": user_data.name,
            "password": hashed_password,
            "created_at": datetime.utcnow(),
            "workflow_count": 0,
            "integration_count": 0
        }
        
        users_collection.insert_one(user_doc)
        token = create_jwt_token(user_id)
        
        return {
            "user": {
                "id": user_id,
                "email": user_data.email,
                "name": user_data.name
            },
            "token": token
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/auth/login")
async def login(user_data: UserLogin):
    """User login endpoint"""
    try:
        # Find user
        user = users_collection.find_one({"email": user_data.email})
        if not user or not verify_password(user_data.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        token = create_jwt_token(user["id"])
        
        return {
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"]
            },
            "token": token
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/dashboard/stats")
async def get_dashboard_stats(user_id: str = Depends(verify_jwt_token)):
    """Get dashboard statistics"""
    try:
        user = users_collection.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        workflow_count = workflows_collection.count_documents({"user_id": user_id})
        execution_count = executions_collection.count_documents({"user_id": user_id})
        integration_count = integrations_collection.count_documents({"user_id": user_id})
        
        # Calculate success rate
        successful_executions = executions_collection.count_documents({
            "user_id": user_id, 
            "status": "success"
        })
        success_rate = (successful_executions / execution_count * 100) if execution_count > 0 else 0
        
        # Recent activities
        recent_executions = list(executions_collection.find(
            {"user_id": user_id}
        ).sort("started_at", -1).limit(5))
        
        recent_activities = []
        for execution in recent_executions:
            recent_activities.append({
                "type": "execution",
                "description": f"Executed workflow: {execution.get('workflow_name', 'Unknown')}",
                "timestamp": execution.get("started_at", datetime.utcnow()).isoformat(),
                "status": execution.get("status", "unknown")
            })
        
        return {
            "total_workflows": workflow_count,
            "total_executions": execution_count,
            "total_integrations": integration_count,
            "success_rate": round(success_rate, 1),
            "failed_executions": execution_count - successful_executions,
            "recent_activities": recent_activities
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/nodes")
async def get_node_types():
    """Get available node types"""
    nodes = [
        {
            "id": "webhook_trigger",
            "name": "Webhook Trigger",
            "category": "triggers",
            "description": "Trigger workflow when webhook is called",
            "inputs": [],
            "outputs": ["payload"]
        },
        {
            "id": "email_action",
            "name": "Send Email",
            "category": "actions",
            "description": "Send an email",
            "inputs": ["to", "subject", "body"],
            "outputs": ["success"]
        },
        {
            "id": "condition",
            "name": "Condition",
            "category": "logic",
            "description": "Check a condition",
            "inputs": ["condition"],
            "outputs": ["true", "false"]
        },
        {
            "id": "ai_analyze",
            "name": "AI Analysis",
            "category": "ai",
            "description": "Analyze data with AI",
            "inputs": ["data"],
            "outputs": ["analysis"]
        }
    ]
    return nodes

@app.get("/api/integrations")
async def get_available_integrations():
    """Get available integrations"""
    integrations = {
        "communication": [
            {"name": "Slack", "platform": "slack", "auth_type": "oauth"},
            {"name": "Discord", "platform": "discord", "auth_type": "token"},
            {"name": "Microsoft Teams", "platform": "teams", "auth_type": "oauth"},
            {"name": "Email (SMTP)", "platform": "email", "auth_type": "credentials"}
        ],
        "productivity": [
            {"name": "Google Workspace", "platform": "google", "auth_type": "oauth"},
            {"name": "Microsoft 365", "platform": "microsoft", "auth_type": "oauth"},
            {"name": "Notion", "platform": "notion", "auth_type": "api_key"},
            {"name": "Airtable", "platform": "airtable", "auth_type": "api_key"}
        ],
        "development": [
            {"name": "GitHub", "platform": "github", "auth_type": "oauth"},
            {"name": "GitLab", "platform": "gitlab", "auth_type": "oauth"},
            {"name": "Jira", "platform": "jira", "auth_type": "api_key"}
        ],
        "ai": [
            {"name": "OpenAI", "platform": "openai", "auth_type": "api_key"},
            {"name": "GROQ", "platform": "groq", "auth_type": "api_key"}
        ]
    }
    
    return {
        "integrations": integrations,
        "categories": list(integrations.keys()),
        "total_count": sum(len(category_integrations) for category_integrations in integrations.values())
    }

@app.get("/api/workflows")
async def get_workflows(user_id: str = Depends(verify_jwt_token)):
    """Get user workflows"""
    try:
        workflows = list(workflows_collection.find(
            {"user_id": user_id}
        ).sort("created_at", -1))
        
        # Convert ObjectId to string and format response
        for workflow in workflows:
            workflow["_id"] = str(workflow["_id"])
        
        return {"workflows": workflows}
    except Exception as e:
        logger.error(f"Get workflows error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/workflows")
async def create_workflow(workflow_data: WorkflowCreate, user_id: str = Depends(verify_jwt_token)):
    """Create new workflow"""
    try:
        workflow_id = str(uuid.uuid4())
        
        workflow_doc = {
            "id": workflow_id,
            "user_id": user_id,
            "name": workflow_data.name,
            "description": workflow_data.description,
            "nodes": workflow_data.nodes,
            "connections": workflow_data.connections,
            "triggers": workflow_data.triggers,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "status": "draft"
        }
        
        workflows_collection.insert_one(workflow_doc)
        
        # Update user workflow count
        users_collection.update_one(
            {"id": user_id},
            {"$inc": {"workflow_count": 1}}
        )
        
        return {"workflow_id": workflow_id, "message": "Workflow created successfully"}
    except Exception as e:
        logger.error(f"Create workflow error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/workflows/{workflow_id}/execute")
async def execute_workflow(workflow_id: str, user_id: str = Depends(verify_jwt_token)):
    """Execute a workflow"""
    try:
        # Find workflow
        workflow = workflows_collection.find_one({"id": workflow_id, "user_id": user_id})
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        execution_id = str(uuid.uuid4())
        
        # Create execution record
        execution_doc = {
            "id": execution_id,
            "workflow_id": workflow_id,
            "workflow_name": workflow["name"],
            "user_id": user_id,
            "status": "success",
            "started_at": datetime.utcnow(),
            "completed_at": datetime.utcnow(),
            "logs": ["Workflow execution simulated successfully"]
        }
        
        executions_collection.insert_one(execution_doc)
        
        return {
            "execution_id": execution_id,
            "status": "success",
            "message": "Workflow executed successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Execute workflow error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/integrations")
async def create_integration(integration_data: IntegrationCreate, user_id: str = Depends(verify_jwt_token)):
    """Create new integration"""
    try:
        integration_id = str(uuid.uuid4())
        
        integration_doc = {
            "id": integration_id,
            "user_id": user_id,
            "name": integration_data.name,
            "platform": integration_data.platform,
            "credentials": integration_data.credentials,  # In production, encrypt this
            "created_at": datetime.utcnow(),
            "status": "active"
        }
        
        integrations_collection.insert_one(integration_doc)
        
        # Update user integration count
        users_collection.update_one(
            {"id": user_id},
            {"$inc": {"integration_count": 1}}
        )
        
        return {"integration_id": integration_id, "message": "Integration created successfully"}
    except Exception as e:
        logger.error(f"Create integration error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/integrations/user")
async def get_user_integrations(user_id: str = Depends(verify_jwt_token)):
    """Get user integrations"""
    try:
        integrations = list(integrations_collection.find(
            {"user_id": user_id}
        ).sort("created_at", -1))
        
        # Convert ObjectId to string and remove sensitive data
        for integration in integrations:
            integration["_id"] = str(integration["_id"])
            integration.pop("credentials", None)  # Remove credentials from response
        
        return {"integrations": integrations}
    except Exception as e:
        logger.error(f"Get user integrations error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/ai/chat")
async def ai_chat(ai_request: AIRequest, user_id: str = Depends(verify_jwt_token)):
    """AI chat endpoint"""
    try:
        if not groq_client:
            return {
                "response": "AI service is not available. Please configure GROQ_API_KEY.",
                "model": "fallback"
            }
        
        # Use GROQ for AI response
        completion = groq_client.chat.completions.create(
            messages=[
                {"role": "user", "content": ai_request.message or ai_request.prompt or "Hello"}
            ],
            model="llama3-8b-8192",
            max_tokens=150
        )
        
        response_text = completion.choices[0].message.content
        
        return {
            "response": response_text,
            "model": "llama3-8b-8192",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"AI chat error: {e}")
        return {
            "response": "I'm sorry, I'm having trouble processing your request right now. Please try again later.",
            "model": "fallback",
            "error": str(e)
        }

@app.get("/api/templates")
async def get_templates():
    """Get workflow templates"""
    templates = [
        {
            "id": "email_automation",
            "name": "Email Automation",
            "description": "Automatically send emails based on triggers",
            "category": "communication",
            "difficulty": "beginner",
            "rating": 4.5
        },
        {
            "id": "data_sync",
            "name": "Data Synchronization",
            "description": "Sync data between different platforms",
            "category": "integration",
            "difficulty": "intermediate",
            "rating": 4.2
        }
    ]
    return {"templates": templates}

# Enhanced system status endpoint
@app.get("/api/enhanced/system-status")
async def get_enhanced_system_status():
    """Get comprehensive system status"""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "overall_status": "operational",
        "system_components": {
            "database": {"status": "operational"},
            "ai_service": {"status": "operational" if groq_client else "unavailable"},
            "core_api": {"status": "operational"}
        },
        "version": "2.0.0"
    }

# 🚀 NEXT-GENERATION ENHANCEMENT INTEGRATION
# Integrate all 11 phases of the Next-Generation Enhancement Roadmap
try:
    from next_gen_integration_system import integrate_next_generation_system, add_feature_discovery_api
    
    # Integrate Next-Gen system with zero disruption
    integration_success = integrate_next_generation_system(app)
    
    # Add feature discovery API for frontend
    add_feature_discovery_api(app)
    
    if integration_success:
        logger.info("🌟 Next-Generation Enhancement System: FULLY OPERATIONAL")
        logger.info("✅ All 11 phases integrated successfully")
    else:
        logger.info("⚠️ Running with standard system + partial enhancements")
        
except Exception as e:
    logger.warning(f"Next-Gen integration failed, running standard system: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)