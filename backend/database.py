from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import os

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None

    def get_database(self) -> AsyncIOMotorDatabase:
        if self.database is None:
            raise ValueError("Database not initialized")
        return self.database

# Global database instance
db_instance = Database()

async def connect_to_mongo():
    """Create database connection"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'aether_automation')
    
    db_instance.client = AsyncIOMotorClient(mongo_url)
    db_instance.database = db_instance.client[db_name]
    
    # Create indexes for better performance
    await create_indexes()

async def create_indexes():
    """Create database indexes"""
    db = db_instance.get_database()
    
    # Users indexes
    await db.users.create_index("email", unique=True)
    await db.users.create_index("created_at")
    
    # Workflows indexes
    await db.workflows.create_index([("user_id", 1), ("created_at", -1)])
    await db.workflows.create_index("status")
    
    # Executions indexes
    await db.workflow_executions.create_index([("workflow_id", 1), ("started_at", -1)])
    await db.workflow_executions.create_index("user_id")
    
    # Integrations indexes
    await db.user_integrations.create_index([("user_id", 1), ("integration_id", 1)])

async def close_mongo_connection():
    """Close database connection"""
    if db_instance.client:
        db_instance.client.close()

def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    return db_instance.get_database()