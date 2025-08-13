from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import jwt
import bcrypt
from datetime import datetime, timedelta
import uuid
import time
import logging
from pymongo import MongoClient, ASCENDING, DESCENDING
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
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

# Database setup
MONGO_URL = os.getenv("MONGO_URL")
if not MONGO_URL:
    raise RuntimeError("MONGO_URL is not set. Please configure it in backend/.env")
client = MongoClient(MONGO_URL)
db = client.aether_automation

# Collections
users_collection = db.users
workflows_collection = db.workflows
templates_collection = db.templates
integrations_collection = db.integrations
executions_collection = db.executions

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
    start_time = time.time()
    try:
        # Test database connection
        db.command('ping')
        db_status = "ok"
        db_latency = time.time() - start_time
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "error"
        db_latency = None
    
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "database": {
            "status": db_status,
            "latency_ms": round(db_latency * 1000, 2) if db_latency else None
        }
    }

@app.post("/api/auth/signup")
async def signup(user_data: UserSignup):
    # Check if user exists
    existing_user = users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(user_data.password)
    
    user_doc = {
        "_id": user_id,
        "email": user_data.email,
        "name": user_data.name,
        "password": hashed_password,
        "created_at": datetime.utcnow(),
        "workflows_count": 0,
        "integrations_count": 0
    }
    
    users_collection.insert_one(user_doc)
    
    # Generate JWT token
    token = create_jwt_token(user_id)
    
    return {
        "token": token,
        "user": {
            "id": user_id,
            "email": user_data.email,
            "name": user_data.name
        }
    }

@app.post("/api/auth/login")
async def login(user_data: UserLogin):
    # Find user
    user = users_collection.find_one({"email": user_data.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not verify_password(user_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate JWT token
    token = create_jwt_token(user["_id"])
    
    return {
        "token": token,
        "user": {
            "id": user["_id"],
            "email": user["email"],
            "name": user["name"]
        }
    }

@app.get("/api/dashboard/stats")
async def get_dashboard_stats(user_id: str = Depends(verify_jwt_token)):
    """Get dashboard statistics"""
    try:
        # Get basic stats
        total_workflows = workflows_collection.count_documents({"user_id": user_id})
        total_executions = executions_collection.count_documents({"user_id": user_id})
        successful_executions = executions_collection.count_documents({"user_id": user_id, "status": "success"})
        failed_executions = executions_collection.count_documents({"user_id": user_id, "status": "failed"})
        
        success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
        
        return {
            "total_workflows": total_workflows,
            "total_executions": total_executions,
            "success_rate": round(success_rate, 2),
            "failed_executions": failed_executions,
            "recent_activities": []
        }
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dashboard statistics")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)