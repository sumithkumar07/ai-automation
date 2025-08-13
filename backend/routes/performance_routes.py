from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from auth import get_current_active_user
from cache_service import cache_service, cached, generate_cache_key, CACHE_CONFIGS
from database import get_database
import asyncio
import time
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/performance", tags=["performance"])

@router.get("/cache/stats")
async def get_cache_stats():
    """Get cache performance statistics."""
    stats = await cache_service.get_stats()
    return {
        "cache_stats": stats,
        "cache_configs": CACHE_CONFIGS,
        "status": "healthy"
    }

@router.delete("/cache/clear")
async def clear_cache(current_user: dict = Depends(get_current_active_user)):
    """Clear all cache entries (admin only)."""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    await cache_service.clear()
    return {"message": "Cache cleared successfully"}

@router.delete("/cache/pattern/{pattern}")
async def invalidate_cache_pattern(pattern: str, current_user: dict = Depends(get_current_active_user)):
    """Invalidate cache entries matching pattern."""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    count = await cache_service.invalidate_pattern(pattern)
    return {"message": f"Invalidated {count} cache entries", "pattern": pattern}

@router.get("/database/stats")
async def get_database_stats():
    """Get database performance statistics."""
    db = get_database()
    
    try:
        # Get collection stats
        collections = await db.list_collection_names()
        stats = {}
        
        for collection_name in collections:
            collection = db[collection_name]
            collection_stats = await collection.estimated_document_count()
            stats[collection_name] = {
                "document_count": collection_stats,
                "indexes": []
            }
            
            # Get index information
            try:
                async for index_info in collection.list_indexes():
                    stats[collection_name]["indexes"].append(index_info)
            except Exception as e:
                logger.warning(f"Could not get index info for {collection_name}: {e}")
        
        return {
            "collections": stats,
            "total_collections": len(collections),
            "status": "connected"
        }
    
    except Exception as e:
        logger.error(f"Database stats error: {e}")
        return {
            "error": str(e),
            "status": "error"
        }

@router.post("/database/optimize")
async def optimize_database(current_user: dict = Depends(get_current_active_user)):
    """Optimize database performance (admin only)."""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = get_database()
    optimization_results = []
    
    try:
        # Create indexes for better performance
        indexes_to_create = [
            ("users", [("email", 1)], {"unique": True}),
            ("users", [("created_at", -1)]),
            ("workflows", [("user_id", 1)]),
            ("workflows", [("status", 1)]),
            ("workflows", [("created_at", -1)]),
            ("workflow_executions", [("workflow_id", 1)]),
            ("workflow_executions", [("status", 1)]),
            ("workflow_executions", [("started_at", -1)]),
            ("user_integrations", [("user_id", 1)]),
            ("user_integrations", [("integration_id", 1)]),
            ("templates", [("category", 1)]),
            ("templates", [("is_featured", 1)]),
        ]
        
        for collection_name, index_spec, options in indexes_to_create:
            try:
                collection = db[collection_name]
                result = await collection.create_index(index_spec, **options)
                optimization_results.append({
                    "collection": collection_name,
                    "index": str(index_spec),
                    "result": result,
                    "status": "created"
                })
            except Exception as e:
                if "already exists" in str(e).lower():
                    optimization_results.append({
                        "collection": collection_name,
                        "index": str(index_spec),
                        "status": "exists"
                    })
                else:
                    optimization_results.append({
                        "collection": collection_name,
                        "index": str(index_spec),
                        "error": str(e),
                        "status": "error"
                    })
        
        return {
            "message": "Database optimization completed",
            "results": optimization_results
        }
    
    except Exception as e:
        logger.error(f"Database optimization error: {e}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

@router.get("/system/health")
async def system_health_check():
    """Comprehensive system health check."""
    start_time = time.time()
    health_status = {
        "timestamp": datetime.utcnow().isoformat(),
        "status": "healthy",
        "components": {}
    }
    
    # Check cache service
    try:
        cache_stats = await cache_service.get_stats()
        health_status["components"]["cache"] = {
            "status": "healthy",
            "stats": cache_stats
        }
    except Exception as e:
        health_status["components"]["cache"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Check database connection
    try:
        db = get_database()
        await db.command("ping")
        health_status["components"]["database"] = {
            "status": "healthy",
            "connection": "active"
        }
    except Exception as e:
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"
    
    # Check AI services (GROQ)
    try:
        from ai_service import ai_service
        health_status["components"]["ai_services"] = {
            "status": "healthy",
            "groq_configured": ai_service.groq_client is not None,
            "openai_configured": ai_service.openai_client is not None,
            "anthropic_configured": ai_service.anthropic_client is not None,
            "gemini_configured": ai_service.gemini_client is not None
        }
    except Exception as e:
        health_status["components"]["ai_services"] = {
            "status": "degraded",
            "error": str(e)
        }
    
    # Check integrations engine
    try:
        from integrations_engine import integrations_engine
        total_integrations = len(integrations_engine.get_all_integrations())
        health_status["components"]["integrations"] = {
            "status": "healthy",
            "total_integrations": total_integrations
        }
    except Exception as e:
        health_status["components"]["integrations"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Response time
    response_time = (time.time() - start_time) * 1000  # in milliseconds
    health_status["response_time_ms"] = response_time
    
    # Overall health determination
    component_statuses = [comp["status"] for comp in health_status["components"].values()]
    if "unhealthy" in component_statuses:
        health_status["status"] = "unhealthy"
    elif "degraded" in component_statuses:
        health_status["status"] = "degraded"
    
    return health_status

@router.get("/metrics")
async def get_performance_metrics():
    """Get detailed performance metrics."""
    metrics = {
        "timestamp": datetime.utcnow().isoformat(),
        "system": {},
        "application": {}
    }
    
    # System metrics (basic)
    try:
        import psutil
        metrics["system"] = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent
        }
    except ImportError:
        metrics["system"] = {"note": "psutil not available for system metrics"}
    
    # Application metrics
    try:
        # Database metrics
        db = get_database()
        collections = await db.list_collection_names()
        
        total_documents = 0
        for collection_name in collections:
            count = await db[collection_name].estimated_document_count()
            total_documents += count
        
        metrics["application"]["database"] = {
            "total_collections": len(collections),
            "total_documents": total_documents
        }
        
        # Cache metrics
        cache_stats = await cache_service.get_stats()
        metrics["application"]["cache"] = cache_stats
        
        # Integration metrics
        from integrations_engine import integrations_engine
        metrics["application"]["integrations"] = {
            "total_integrations": len(integrations_engine.get_all_integrations()),
            "categories": len(set(integration.category for integration in integrations_engine.get_all_integrations()))
        }
        
    except Exception as e:
        metrics["application"]["error"] = str(e)
    
    return metrics

@router.post("/preload/cache")
async def preload_cache(current_user: dict = Depends(get_current_active_user)):
    """Preload frequently accessed data into cache."""
    preload_results = []
    
    try:
        # Preload integrations data
        from integrations_engine import integrations_engine
        integrations = integrations_engine.get_all_integrations()
        cache_key = generate_cache_key("integrations", "all")
        await cache_service.set(cache_key, [integration.dict() for integration in integrations], 
                               CACHE_CONFIGS['integration_data']['ttl'])
        preload_results.append({"type": "integrations", "count": len(integrations), "cached": True})
        
        # Preload node types
        from node_types_engine import node_types_engine
        node_types = node_types_engine.get_all_node_types()
        cache_key = generate_cache_key("node_types", "all")
        await cache_service.set(cache_key, node_types, CACHE_CONFIGS['node_types']['ttl'])
        preload_results.append({"type": "node_types", "cached": True})
        
        # Preload user's frequent data
        db = get_database()
        
        # Recent workflows
        recent_workflows = await db.workflows.find(
            {"user_id": current_user["user_id"]}, 
            limit=10
        ).sort("updated_at", -1).to_list(length=10)
        
        cache_key = generate_cache_key("user_workflows", current_user["user_id"], "recent")
        await cache_service.set(cache_key, recent_workflows, CACHE_CONFIGS['workflow_execution']['ttl'])
        preload_results.append({"type": "recent_workflows", "count": len(recent_workflows), "cached": True})
        
        return {
            "message": "Cache preload completed",
            "results": preload_results
        }
    
    except Exception as e:
        logger.error(f"Cache preload error: {e}")
        raise HTTPException(status_code=500, detail=f"Preload failed: {str(e)}")

# Background tasks for performance optimization
@router.post("/tasks/cleanup")
async def start_cleanup_tasks(current_user: dict = Depends(get_current_active_user)):
    """Start background cleanup tasks (admin only)."""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    tasks_started = []
    
    try:
        # Cleanup expired cache entries
        expired_count = await cache_service.cleanup_expired()
        tasks_started.append({"task": "cache_cleanup", "expired_entries": expired_count})
        
        # Cleanup old execution logs (older than 30 days)
        db = get_database()
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        result = await db.workflow_executions.delete_many({
            "completed_at": {"$lt": cutoff_date},
            "status": {"$in": ["success", "failed"]}
        })
        tasks_started.append({"task": "execution_cleanup", "deleted_count": result.deleted_count})
        
        return {
            "message": "Cleanup tasks completed",
            "tasks": tasks_started
        }
    
    except Exception as e:
        logger.error(f"Cleanup tasks error: {e}")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")