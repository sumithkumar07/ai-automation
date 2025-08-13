"""
Enhanced Server Additions - Integration point for all new features
This module integrates all enhanced features into the main FastAPI server
"""

from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)

def get_enhanced_router() -> APIRouter:
    """Get the router with all enhanced endpoints"""
    try:
        from enhanced_api_endpoints import router
        logger.info("Enhanced API endpoints loaded successfully")
        return router
    except ImportError as e:
        logger.warning(f"Failed to import enhanced endpoints: {e}")
        # Return empty router as fallback
        return APIRouter()