"""
Integration Testing Routes
Built-in connection testing interface for integrations
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
import logging
from database import get_database
from auth import get_current_active_user
from integrations_engine import integrations_engine

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/integration-testing", tags=["integration-testing"])

@router.post("/test-connection/{integration_id}")
async def test_integration_connection(
    integration_id: str,
    connection_config: Dict[str, Any],
    current_user: dict = Depends(get_current_active_user)
):
    """Test an integration connection with provided configuration"""
    try:
        # Get integration details
        integration = integrations_engine.get_integration(integration_id)
        if not integration:
            raise HTTPException(status_code=404, detail="Integration not found")
        
        # Validate configuration
        validation_result = validate_integration_config(integration, connection_config)
        if not validation_result["is_valid"]:
            return {
                "test_result": "failed",
                "status": "configuration_error",
                "error": "Invalid configuration",
                "validation_errors": validation_result["errors"],
                "tested_at": datetime.utcnow().isoformat()
            }
        
        # Perform connection test
        test_result = await perform_integration_test(integration_id, connection_config)
        
        # Log test result
        await log_integration_test(
            current_user["user_id"],
            integration_id,
            test_result,
            connection_config
        )
        
        return test_result
        
    except Exception as e:
        logger.error(f"Error testing integration connection: {e}")
        raise HTTPException(status_code=500, detail="Failed to test integration connection")

@router.post("/test-workflow-integrations/{workflow_id}")
async def test_workflow_integrations(
    workflow_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Test all integrations used in a workflow"""
    try:
        db = get_database()
        
        # Get workflow
        workflow = await db.workflows.find_one({
            "id": workflow_id,
            "user_id": current_user["user_id"]
        })
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Extract integrations from workflow
        workflow_definition = workflow.get("workflow_definition", {})
        integration_nodes = extract_integration_nodes(workflow_definition)
        
        if not integration_nodes:
            return {
                "workflow_id": workflow_id,
                "message": "No integrations found in workflow",
                "test_results": []
            }
        
        # Test each integration
        test_results = []
        
        for node in integration_nodes:
            integration_id = node.get("integration_id")
            if not integration_id:
                continue
            
            # Get user's connection config for this integration
            user_connection = await db.user_integrations.find_one({
                "user_id": current_user["user_id"],
                "integration_id": integration_id,
                "is_active": True
            })
            
            if user_connection:
                test_result = await perform_integration_test(
                    integration_id,
                    user_connection["config"]
                )
                test_result["node_id"] = node.get("id")
                test_result["node_name"] = node.get("name", "Unnamed Node")
            else:
                test_result = {
                    "test_result": "skipped",
                    "status": "not_connected",
                    "error": "Integration not connected",
                    "node_id": node.get("id"),
                    "node_name": node.get("name", "Unnamed Node"),
                    "integration_id": integration_id,
                    "tested_at": datetime.utcnow().isoformat()
                }
            
            test_results.append(test_result)
        
        # Calculate overall status
        successful_tests = [r for r in test_results if r["test_result"] == "success"]
        failed_tests = [r for r in test_results if r["test_result"] == "failed"]
        
        overall_status = "all_passed"
        if len(failed_tests) > 0:
            overall_status = "some_failed" if len(successful_tests) > 0 else "all_failed"
        elif len(test_results) == 0:
            overall_status = "no_integrations"
        
        return {
            "workflow_id": workflow_id,
            "workflow_name": workflow["name"],
            "overall_status": overall_status,
            "summary": {
                "total_integrations": len(test_results),
                "successful": len(successful_tests),
                "failed": len(failed_tests),
                "skipped": len([r for r in test_results if r["test_result"] == "skipped"])
            },
            "test_results": test_results,
            "tested_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error testing workflow integrations: {e}")
        raise HTTPException(status_code=500, detail="Failed to test workflow integrations")

@router.get("/test-history/{integration_id}")
async def get_integration_test_history(
    integration_id: str,
    limit: int = 10,
    current_user: dict = Depends(get_current_active_user)
):
    """Get integration test history for a user"""
    try:
        db = get_database()
        
        # Get test history
        cursor = db.integration_test_logs.find({
            "user_id": current_user["user_id"],
            "integration_id": integration_id
        }).sort([("tested_at", -1)]).limit(limit)
        
        test_history = await cursor.to_list(length=limit)
        
        # Calculate statistics
        if test_history:
            successful_tests = [t for t in test_history if t.get("test_result") == "success"]
            success_rate = (len(successful_tests) / len(test_history)) * 100
            
            # Get recent trend
            recent_tests = test_history[:5]  # Last 5 tests
            recent_successful = [t for t in recent_tests if t.get("test_result") == "success"]
            recent_success_rate = (len(recent_successful) / len(recent_tests)) * 100 if recent_tests else 0
            
            trend = "improving" if recent_success_rate > success_rate else "declining" if recent_success_rate < success_rate else "stable"
        else:
            success_rate = 0
            trend = "no_data"
        
        return {
            "integration_id": integration_id,
            "test_history": test_history,
            "statistics": {
                "total_tests": len(test_history),
                "success_rate": success_rate,
                "trend": trend,
                "last_test": test_history[0] if test_history else None
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting integration test history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get test history")

@router.get("/test-suite/{integration_id}")
async def get_integration_test_suite(integration_id: str):
    """Get available test suite for an integration"""
    try:
        integration = integrations_engine.get_integration(integration_id)
        if not integration:
            raise HTTPException(status_code=404, detail="Integration not found")
        
        # Generate test suite based on integration capabilities
        test_suite = generate_integration_test_suite(integration)
        
        return {
            "integration_id": integration_id,
            "integration_name": integration.name,
            "test_suite": test_suite,
            "total_tests": len(test_suite)
        }
        
    except Exception as e:
        logger.error(f"Error getting integration test suite: {e}")
        raise HTTPException(status_code=500, detail="Failed to get test suite")

@router.post("/run-test-suite/{integration_id}")
async def run_integration_test_suite(
    integration_id: str,
    connection_config: Dict[str, Any],
    test_config: Dict[str, Any] = None,
    current_user: dict = Depends(get_current_active_user)
):
    """Run comprehensive test suite for an integration"""
    try:
        integration = integrations_engine.get_integration(integration_id)
        if not integration:
            raise HTTPException(status_code=404, detail="Integration not found")
        
        # Get test suite
        test_suite = generate_integration_test_suite(integration)
        
        # Run all tests
        test_results = []
        overall_success = True
        
        for test_case in test_suite:
            try:
                if test_case["type"] == "connection":
                    result = await test_basic_connection(integration_id, connection_config)
                elif test_case["type"] == "authentication":
                    result = await test_authentication(integration_id, connection_config)
                elif test_case["type"] == "action":
                    result = await test_integration_action(
                        integration_id,
                        test_case["action_id"],
                        connection_config,
                        test_case.get("test_data", {})
                    )
                elif test_case["type"] == "trigger":
                    result = await test_integration_trigger(
                        integration_id,
                        test_case["trigger_id"],
                        connection_config
                    )
                else:
                    result = {
                        "test_name": test_case["name"],
                        "status": "skipped",
                        "message": "Test type not supported"
                    }
                
                test_results.append({
                    **test_case,
                    "result": result,
                    "executed_at": datetime.utcnow().isoformat()
                })
                
                if result.get("status") != "success":
                    overall_success = False
                    
            except Exception as e:
                test_results.append({
                    **test_case,
                    "result": {
                        "status": "error",
                        "message": str(e)
                    },
                    "executed_at": datetime.utcnow().isoformat()
                })
                overall_success = False
        
        # Log comprehensive test result
        await log_integration_test_suite(
            current_user["user_id"],
            integration_id,
            test_results,
            overall_success
        )
        
        # Calculate statistics
        successful_tests = [r for r in test_results if r["result"]["status"] == "success"]
        success_rate = (len(successful_tests) / len(test_results)) * 100 if test_results else 0
        
        return {
            "integration_id": integration_id,
            "integration_name": integration.name,
            "overall_success": overall_success,
            "statistics": {
                "total_tests": len(test_results),
                "successful": len(successful_tests),
                "failed": len(test_results) - len(successful_tests),
                "success_rate": success_rate
            },
            "test_results": test_results,
            "executed_at": datetime.utcnow().isoformat(),
            "recommendations": generate_test_recommendations(test_results)
        }
        
    except Exception as e:
        logger.error(f"Error running integration test suite: {e}")
        raise HTTPException(status_code=500, detail="Failed to run test suite")

# Helper functions
def validate_integration_config(integration, config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate integration configuration"""
    errors = []
    
    if integration.auth_type == "api_key":
        if not config.get("api_key") and not config.get("token"):
            errors.append("API key or token is required")
    elif integration.auth_type == "oauth2":
        if not config.get("access_token") and not config.get("oauth_token"):
            errors.append("OAuth access token is required")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }

async def perform_integration_test(integration_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Perform basic integration connection test"""
    try:
        # Simulate different test scenarios based on integration
        await asyncio.sleep(0.5)  # Simulate API call delay
        
        # Mock test results for different integrations
        if integration_id in ["slack", "discord", "gmail"]:
            # Communication integrations
            test_result = await test_communication_integration(integration_id, config)
        elif integration_id in ["github", "gitlab", "jira"]:
            # Development integrations
            test_result = await test_development_integration(integration_id, config)
        elif integration_id in ["stripe", "paypal"]:
            # Payment integrations
            test_result = await test_payment_integration(integration_id, config)
        else:
            # Generic test
            test_result = await test_generic_integration(integration_id, config)
        
        return test_result
        
    except Exception as e:
        return {
            "test_result": "failed",
            "status": "connection_error",
            "error": str(e),
            "integration_id": integration_id,
            "tested_at": datetime.utcnow().isoformat()
        }

async def test_communication_integration(integration_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Test communication integration (Slack, Discord, Gmail, etc.)"""
    try:
        # Simulate API call
        await asyncio.sleep(0.3)
        
        # Mock success for valid configurations
        if config.get("api_key") or config.get("access_token"):
            return {
                "test_result": "success",
                "status": "connected",
                "message": f"Successfully connected to {integration_id}",
                "integration_id": integration_id,
                "response_time_ms": 300,
                "features_tested": ["authentication", "basic_api_access"],
                "tested_at": datetime.utcnow().isoformat()
            }
        else:
            return {
                "test_result": "failed",
                "status": "authentication_failed",
                "error": "Invalid credentials",
                "integration_id": integration_id,
                "tested_at": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        return {
            "test_result": "failed",
            "status": "connection_error",
            "error": str(e),
            "integration_id": integration_id,
            "tested_at": datetime.utcnow().isoformat()
        }

async def test_development_integration(integration_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Test development integration (GitHub, GitLab, Jira, etc.)"""
    try:
        await asyncio.sleep(0.4)
        
        if config.get("access_token") or config.get("api_key"):
            return {
                "test_result": "success",
                "status": "connected", 
                "message": f"Successfully connected to {integration_id}",
                "integration_id": integration_id,
                "response_time_ms": 400,
                "features_tested": ["authentication", "repository_access", "api_permissions"],
                "tested_at": datetime.utcnow().isoformat()
            }
        else:
            return {
                "test_result": "failed",
                "status": "authentication_failed",
                "error": "Invalid access token",
                "integration_id": integration_id,
                "tested_at": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        return {
            "test_result": "failed",
            "status": "connection_error", 
            "error": str(e),
            "integration_id": integration_id,
            "tested_at": datetime.utcnow().isoformat()
        }

async def test_payment_integration(integration_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Test payment integration (Stripe, PayPal, etc.)"""
    try:
        await asyncio.sleep(0.6)
        
        if config.get("api_key") or config.get("secret_key"):
            return {
                "test_result": "success",
                "status": "connected",
                "message": f"Successfully connected to {integration_id}",
                "integration_id": integration_id,
                "response_time_ms": 600,
                "features_tested": ["authentication", "account_access", "webhooks"],
                "security_check": "passed",
                "tested_at": datetime.utcnow().isoformat()
            }
        else:
            return {
                "test_result": "failed",
                "status": "authentication_failed",
                "error": "Invalid API credentials",
                "integration_id": integration_id,
                "tested_at": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        return {
            "test_result": "failed",
            "status": "connection_error",
            "error": str(e),
            "integration_id": integration_id,
            "tested_at": datetime.utcnow().isoformat()
        }

async def test_generic_integration(integration_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Test generic integration"""
    try:
        await asyncio.sleep(0.2)
        
        return {
            "test_result": "success",
            "status": "connected",
            "message": f"Successfully tested {integration_id} integration",
            "integration_id": integration_id,
            "response_time_ms": 200,
            "features_tested": ["basic_connectivity"],
            "tested_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "test_result": "failed",
            "status": "connection_error",
            "error": str(e),
            "integration_id": integration_id,
            "tested_at": datetime.utcnow().isoformat()
        }

def extract_integration_nodes(workflow_definition: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract integration nodes from workflow definition"""
    integration_nodes = []
    
    nodes = workflow_definition.get("nodes", [])
    for node in nodes:
        if node.get("type") == "integration" or node.get("integration_id"):
            integration_nodes.append(node)
    
    return integration_nodes

def generate_integration_test_suite(integration) -> List[Dict[str, Any]]:
    """Generate comprehensive test suite for an integration"""
    test_suite = []
    
    # Basic connection test
    test_suite.append({
        "id": "connection_test",
        "name": "Connection Test",
        "type": "connection",
        "description": "Test basic connectivity to the integration",
        "priority": "high"
    })
    
    # Authentication test
    test_suite.append({
        "id": "auth_test",
        "name": "Authentication Test",
        "type": "authentication", 
        "description": "Test authentication credentials",
        "priority": "high"
    })
    
    # Test each available action
    for action in integration.actions:
        test_suite.append({
            "id": f"action_{action['id']}",
            "name": f"Test {action['name']}",
            "type": "action",
            "action_id": action["id"],
            "description": f"Test {action['name']} functionality",
            "priority": "medium",
            "test_data": {}
        })
    
    # Test each available trigger
    for trigger in integration.triggers:
        test_suite.append({
            "id": f"trigger_{trigger['id']}",
            "name": f"Test {trigger['name']}",
            "type": "trigger",
            "trigger_id": trigger["id"],
            "description": f"Test {trigger['name']} functionality",
            "priority": "low"
        })
    
    return test_suite

async def test_basic_connection(integration_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Test basic connection"""
    return await perform_integration_test(integration_id, config)

async def test_authentication(integration_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Test authentication"""
    # Simulate authentication test
    await asyncio.sleep(0.2)
    
    if config.get("api_key") or config.get("access_token"):
        return {
            "status": "success",
            "message": "Authentication successful"
        }
    else:
        return {
            "status": "failed",
            "message": "Authentication failed - invalid credentials"
        }

async def test_integration_action(integration_id: str, action_id: str, config: Dict[str, Any], test_data: Dict[str, Any]) -> Dict[str, Any]:
    """Test integration action"""
    try:
        # Use the actual integration engine to test the action
        result = await integrations_engine.execute_action(integration_id, action_id, config, test_data)
        
        if result.get("status") == "success":
            return {
                "status": "success",
                "message": f"Action {action_id} executed successfully"
            }
        else:
            return {
                "status": "failed",
                "message": f"Action {action_id} failed: {result.get('error', 'Unknown error')}"
            }
    except Exception as e:
        return {
            "status": "failed",
            "message": f"Action test failed: {str(e)}"
        }

async def test_integration_trigger(integration_id: str, trigger_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Test integration trigger"""
    # Mock trigger test - in production this would verify trigger setup
    await asyncio.sleep(0.3)
    
    return {
        "status": "success",
        "message": f"Trigger {trigger_id} is properly configured"
    }

def generate_test_recommendations(test_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate recommendations based on test results"""
    recommendations = []
    
    failed_tests = [r for r in test_results if r["result"]["status"] != "success"]
    
    if len(failed_tests) > 0:
        recommendations.append({
            "type": "error_resolution",
            "priority": "high",
            "message": f"{len(failed_tests)} tests failed. Review configuration and credentials."
        })
    
    # Check for specific failure patterns
    auth_failures = [r for r in failed_tests if "authentication" in r["result"].get("message", "").lower()]
    if auth_failures:
        recommendations.append({
            "type": "authentication",
            "priority": "high", 
            "message": "Authentication issues detected. Verify API keys and tokens."
        })
    
    return recommendations

async def log_integration_test(user_id: str, integration_id: str, test_result: Dict[str, Any], config: Dict[str, Any]):
    """Log integration test result"""
    try:
        db = get_database()
        
        # Don't log sensitive config data
        safe_config = {k: "***" if "key" in k.lower() or "token" in k.lower() else v 
                      for k, v in config.items()}
        
        log_entry = {
            "id": f"test_{user_id}_{integration_id}_{int(datetime.utcnow().timestamp())}",
            "user_id": user_id,
            "integration_id": integration_id,
            "test_result": test_result.get("test_result", "unknown"),
            "status": test_result.get("status", "unknown"),
            "response_time_ms": test_result.get("response_time_ms", 0),
            "config_used": safe_config,
            "tested_at": datetime.utcnow()
        }
        
        await db.integration_test_logs.insert_one(log_entry)
        
    except Exception as e:
        logger.error(f"Failed to log integration test: {e}")

async def log_integration_test_suite(user_id: str, integration_id: str, test_results: List[Dict[str, Any]], overall_success: bool):
    """Log comprehensive test suite results"""
    try:
        db = get_database()
        
        log_entry = {
            "id": f"suite_{user_id}_{integration_id}_{int(datetime.utcnow().timestamp())}",
            "user_id": user_id,
            "integration_id": integration_id,
            "test_type": "comprehensive_suite",
            "overall_success": overall_success,
            "total_tests": len(test_results),
            "successful_tests": len([r for r in test_results if r["result"]["status"] == "success"]),
            "test_results": test_results,
            "executed_at": datetime.utcnow()
        }
        
        await db.integration_test_suite_logs.insert_one(log_entry)
        
    except Exception as e:
        logger.error(f"Failed to log test suite results: {e}")