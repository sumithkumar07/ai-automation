from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Aether Test API", version="1.0.0")

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
if MONGO_URL:
    try:
        client = MongoClient(MONGO_URL)
        db = client.aether_automation
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {e}"
        db = None
else:
    db_status = "no MONGO_URL"
    db = None

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "database_status": db_status,
        "version": "1.0.0"
    }

@app.get("/api/nodes")
async def get_node_types():
    """Get available node types"""
    return [
        {"id": "trigger", "name": "Trigger", "category": "triggers"},
        {"id": "action", "name": "Action", "category": "actions"},
        {"id": "condition", "name": "Condition", "category": "logic"}
    ]

@app.get("/api/integrations")
async def get_integrations():
    """Get available integrations"""
    return {
        "integrations": [
            {"name": "Slack", "platform": "slack", "category": "communication"},
            {"name": "Gmail", "platform": "gmail", "category": "communication"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)