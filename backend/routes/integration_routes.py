from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from models import Integration, UserIntegration, IntegrationCategory
from auth import get_current_active_user
from database import get_database
from integrations_engine import integrations_engine
from cache_service import cache_service, cached, generate_cache_key, CACHE_CONFIGS
from datetime import datetime

router = APIRouter(prefix="/integrations", tags=["integrations"])

@router.get("/", response_model=List[Integration])
async def get_all_integrations():
    """Get all available integrations with caching."""
    cache_key = generate_cache_key("integrations", "all")
    
    # Try to get from cache first
    cached_integrations = await cache_service.get(cache_key)
    if cached_integrations:
        return [Integration(**integration) for integration in cached_integrations]
    
    # Get from engine and cache
    integrations = integrations_engine.get_all_integrations()
    integration_dicts = [integration.dict() for integration in integrations]
    
    # Cache for 30 minutes
    await cache_service.set(cache_key, integration_dicts, CACHE_CONFIGS['integration_data']['ttl'])
    
    return integrations

@router.get("/categories")
async def get_integration_categories():
    """Get all integration categories"""
    return [{"id": cat.value, "name": cat.value.replace("_", " ").title()} for cat in IntegrationCategory]

@router.get("/category/{category}")
async def get_integrations_by_category(category: str):
    """Get integrations by category"""
    try:
        category_enum = IntegrationCategory(category)
        integrations = integrations_engine.get_integrations_by_category(category_enum)
        return integrations
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid category")

@router.get("/search")
async def search_integrations(q: str):
    """Search integrations by name or description"""
    all_integrations = integrations_engine.get_all_integrations()
    
    query = q.lower()
    filtered = [
        integration for integration in all_integrations
        if query in integration.name.lower() or query in integration.description.lower()
    ]
    
    return filtered

@router.get("/{integration_id}")
async def get_integration(integration_id: str):
    """Get a specific integration"""
    integration = integrations_engine.get_integration(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return integration

@router.get("/user/connected")
async def get_user_integrations(current_user: dict = Depends(get_current_active_user)):
    """Get user's connected integrations"""
    db = get_database()
    
    cursor = db.user_integrations.find({"user_id": current_user["user_id"], "is_active": True})
    user_integrations = await cursor.to_list(length=100)
    
    # Add integration details
    for user_integration in user_integrations:
        integration = integrations_engine.get_integration(user_integration["integration_id"])
        if integration:
            user_integration["integration"] = integration.dict()
    
    return user_integrations

@router.post("/{integration_id}/connect")
async def connect_integration(integration_id: str, config: dict, current_user: dict = Depends(get_current_active_user)):
    """Connect an integration for the user"""
    db = get_database()
    
    # Check if integration exists
    integration = integrations_engine.get_integration(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    # Validate configuration
    if not integrations_engine.validate_config(integration_id, config):
        raise HTTPException(status_code=400, detail="Invalid configuration")
    
    # Check if already connected
    existing = await db.user_integrations.find_one({
        "user_id": current_user["user_id"],
        "integration_id": integration_id,
        "is_active": True
    })
    
    if existing:
        # Update existing connection
        await db.user_integrations.update_one(
            {"id": existing["id"]},
            {"$set": {"config": config, "updated_at": datetime.utcnow()}}
        )
        connection_id = existing["id"]
    else:
        # Create new connection
        user_integration = UserIntegration(
            user_id=current_user["user_id"],
            integration_id=integration_id,
            name=f"{integration.name} Connection",
            config=config
        )
        
        await db.user_integrations.insert_one(user_integration.dict())
        connection_id = user_integration.id
    
    return {
        "connection_id": connection_id,
        "message": f"{integration.name} connected successfully"
    }

@router.delete("/{integration_id}/disconnect")
async def disconnect_integration(integration_id: str, current_user: dict = Depends(get_current_active_user)):
    """Disconnect an integration"""
    db = get_database()
    
    result = await db.user_integrations.update_one(
        {
            "user_id": current_user["user_id"],
            "integration_id": integration_id,
            "is_active": True
        },
        {"$set": {"is_active": False}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Integration connection not found")
    
    return {"message": "Integration disconnected successfully"}

@router.post("/{integration_id}/test")
async def test_integration_connection(integration_id: str, current_user: dict = Depends(get_current_active_user)):
    """Test an integration connection"""
    db = get_database()
    
    # Get user's integration config
    user_integration = await db.user_integrations.find_one({
        "user_id": current_user["user_id"],
        "integration_id": integration_id,
        "is_active": True
    })
    
    if not user_integration:
        raise HTTPException(status_code=404, detail="Integration not connected")
    
    # Test connection (mock for demo)
    try:
        # In a real implementation, this would test the actual API connection
        test_result = await integrations_engine.execute_action(
            integration_id,
            "test_connection",
            user_integration["config"],
            {"test": True}
        )
        
        return {
            "status": "success",
            "message": "Integration connection is working",
            "test_result": test_result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Integration test failed: {str(e)}"
        }

@router.get("/{integration_id}/actions")
async def get_integration_actions(integration_id: str):
    """Get available actions for an integration"""
    integration = integrations_engine.get_integration(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    return integration.actions

@router.get("/{integration_id}/triggers")
async def get_integration_triggers(integration_id: str):
    """Get available triggers for an integration"""
    integration = integrations_engine.get_integration(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    return integration.triggers