#!/usr/bin/env python3

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Debug Server")

# Add middleware exactly like the main server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=500)

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Debug server working"}

# Test the next-gen integration
try:
    from next_gen_integration_system import integrate_next_generation_system, add_feature_discovery_api
    
    # Integrate Next-Gen system with zero disruption
    integration_success = integrate_next_generation_system(app)
    
    # Add feature discovery API for frontend
    add_feature_discovery_api(app)
    
    if integration_success:
        logger.info("🌟 Next-Generation Enhancement System: FULLY OPERATIONAL")
    else:
        logger.info("⚠️ Running with standard system + partial enhancements")
        
except Exception as e:
    logger.warning(f"Next-Gen integration failed, running standard system: {e}")
    logger.exception("Full error details:")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)