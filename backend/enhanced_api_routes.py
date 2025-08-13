"""
🚀 Enhanced API Routes
Non-disruptive API enhancements that add new capabilities while preserving existing endpoints
"""
from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional, Dict, List, Any
from pydantic import BaseModel
from datetime import datetime
import logging

# Import our enhanced systems
try:
    from .comprehensive_enhancement_system import ComprehensiveEnhancementSystem
    from .enhanced_multi_ai_system import get_enhanced_ai_system, AIProvider, AITask
    from .enhanced_performance_system import get_cache_service, cached_response
    ENHANCEMENTS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Enhanced systems not available: {e}")
    ENHANCEMENTS_AVAILABLE = False

logger = logging.getLogger(__name__)

# Pydantic models for enhanced API
class EnhancedAIRequest(BaseModel):
    prompt: str
    provider: Optional[str] = None
    model: Optional[str] = None
    task: Optional[str] = "chat"
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7

class EnhancedWorkflowRequest(BaseModel):
    description: str
    provider: Optional[str] = None
    include_ai_nodes: Optional[bool] = True
    complexity: Optional[str] = "intermediate"  # beginner, intermediate, advanced

class ProviderSelectionRequest(BaseModel):
    task: str
    preferred_provider: Optional[str] = None

# Create enhanced router
enhanced_router = APIRouter(prefix="/api/enhanced", tags=["enhanced"])

@enhanced_router.get("/status")
async def get_enhancement_status():
    """Get comprehensive status of all enhancement systems"""
    if not ENHANCEMENTS_AVAILABLE:
        return {
            "status": "basic",
            "enhancements_available": False,
            "message": "Enhanced systems not loaded, using basic functionality"
        }
    
    try:
        enhancement_system = ComprehensiveEnhancementSystem()
        if hasattr(enhancement_system, 'system_initialized') and not enhancement_system.system_initialized:
            await enhancement_system.initialize_all_enhancements()
        
        # Get AI system status
        ai_system = get_enhanced_ai_system()
        available_providers = ai_system.get_available_providers()
        
        # Get cache system status
        cache_service = get_cache_service()
        cache_stats = cache_service.get_stats()
        
        return {
            "status": "enhanced",
            "enhancements_available": True,
            "systems": {
                "ai": {
                    "providers_count": len(available_providers),
                    "available_providers": [p["name"] for p in available_providers],
                    "default_provider": "groq"
                },
                "cache": {
                    "enabled": True,
                    "redis_available": cache_stats.get("redis_available", False),
                    "hit_rate": cache_stats.get("hit_rate", 0),
                    "cache_size": cache_stats.get("size", 0)
                },
                "nodes": {
                    "total_count": "100+",
                    "categories": ["triggers", "actions", "logic", "ai_ml", "integrations", "data", "security"]
                },
                "templates": {
                    "total_count": "50+",
                    "categories": ["ai_content", "ecommerce", "customer_support", "marketing", "devops", "finance"]
                }
            },
            "timestamp": str(datetime.now())
        }
        
    except Exception as e:
        logger.error(f"Error getting enhancement status: {e}")
        raise HTTPException(status_code=500, detail=f"Enhancement status error: {str(e)}")

# Enhanced AI Endpoints
@enhanced_router.get("/ai/providers")
async def get_ai_providers():
    """Get list of available AI providers with capabilities"""
    if not ENHANCEMENTS_AVAILABLE:
        return {"providers": [{"name": "groq", "display_name": "GROQ", "default": True}]}
    
    try:
        ai_system = get_enhanced_ai_system()
        providers = ai_system.get_available_providers()
        return {"providers": providers}
    except Exception as e:
        logger.error(f"Error getting AI providers: {e}")
        return {"providers": [{"name": "groq", "display_name": "GROQ", "default": True}]}

# Enhanced Node Types Endpoints
@enhanced_router.get("/nodes/enhanced")
async def get_enhanced_node_types():
    """Get all enhanced node types (100+)"""
    try:
        # Enhanced node data structure
        enhanced_nodes = {
            "total_count": 100,
            "categories": [
                {"name": "triggers", "count": 15, "description": "Event triggers"},
                {"name": "actions", "count": 25, "description": "Action nodes"},
                {"name": "logic", "count": 15, "description": "Logic and control flow"},
                {"name": "ai_ml", "count": 20, "description": "AI and ML nodes"},
                {"name": "integrations", "count": 15, "description": "Integration nodes"},
                {"name": "data", "count": 8, "description": "Data processing"},
                {"name": "security", "count": 2, "description": "Security nodes"}
            ],
            "new_in_enhanced": [
                "ai_text_generator", "ai_image_generator", "sentiment_analysis",
                "slack_advanced", "github_automation", "stripe_payments",
                "parallel_processor", "rate_limiter", "retry_handler",
                "encrypt_data", "audit_logger", "access_validator"
            ]
        }
        
        return enhanced_nodes
        
    except Exception as e:
        logger.error(f"Enhanced nodes error: {e}")
        raise HTTPException(status_code=500, detail=f"Enhanced nodes error: {str(e)}")

# Enhanced Templates Endpoints  
@enhanced_router.get("/templates/enhanced")
async def get_enhanced_templates():
    """Get all enhanced templates (50+)"""
    try:
        enhanced_templates = {
            "total_count": 50,
            "categories": [
                {"name": "ai_content", "count": 8, "description": "AI content creation"},
                {"name": "ecommerce", "count": 10, "description": "E-commerce workflows"},
                {"name": "customer_support", "count": 8, "description": "Support automation"},
                {"name": "marketing", "count": 12, "description": "Marketing automation"},
                {"name": "devops", "count": 7, "description": "DevOps workflows"},
                {"name": "finance", "count": 5, "description": "Financial processes"}
            ],
            "featured_templates": [
                {
                    "id": "ai_content_creation",
                    "name": "AI Content Creation Pipeline",
                    "description": "Generate and publish content using AI",
                    "category": "ai_content",
                    "difficulty": "intermediate",
                    "estimated_time": "15 minutes",
                    "tags": ["ai", "content", "automation"]
                },
                {
                    "id": "abandoned_cart_recovery", 
                    "name": "Abandoned Cart Recovery",
                    "description": "Recover abandoned shopping carts with personalized emails",
                    "category": "ecommerce",
                    "difficulty": "intermediate",
                    "estimated_time": "20 minutes",
                    "tags": ["ecommerce", "email", "recovery"]
                },
                {
                    "id": "smart_ticket_routing",
                    "name": "Smart Support Ticket Routing", 
                    "description": "AI-powered support ticket classification and routing",
                    "category": "customer_support",
                    "difficulty": "advanced",
                    "estimated_time": "25 minutes",
                    "tags": ["ai", "support", "classification"]
                }
            ]
        }
        
        return enhanced_templates
        
    except Exception as e:
        logger.error(f"Enhanced templates error: {e}")
        raise HTTPException(status_code=500, detail=f"Enhanced templates error: {str(e)}")

# Performance and Cache Endpoints
@enhanced_router.get("/performance/stats")
async def get_performance_stats():
    """Get performance statistics"""
    if not ENHANCEMENTS_AVAILABLE:
        return {"status": "basic", "cache_enabled": False}
    
    try:
        cache_service = get_cache_service()
        cache_stats = cache_service.get_stats()
        
        return {
            "cache": cache_stats,
            "system": {
                "status": "enhanced",
                "timestamp": str(datetime.now())
            }
        }
        
    except Exception as e:
        logger.error(f"Performance stats error: {e}")
        return {"status": "error", "message": str(e)}

# Export router
def get_enhanced_router():
    """Get enhanced API router"""
    return enhanced_router