"""
Advanced Analytics Routes
Provides detailed performance charts and metrics for workflows
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from database import get_database
from auth import get_current_active_user
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/workflow/{workflow_id}/performance")
async def get_workflow_performance_analytics(
    workflow_id: str,
    period: str = Query("7d", description="Time period: 1d, 7d, 30d, 90d"),
    current_user: dict = Depends(get_current_active_user)
):
    """Get detailed performance analytics for a specific workflow"""
    try:
        db = get_database()
        
        # Verify access to workflow
        workflow = await db.workflows.find_one({
            "id": workflow_id,
            "user_id": current_user["user_id"]
        })
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Calculate time range
        period_map = {"1d": 1, "7d": 7, "30d": 30, "90d": 90}
        days = period_map.get(period, 7)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get execution data
        execution_cursor = db.workflow_executions.find({
            "workflow_id": workflow_id,
            "created_at": {"$gte": start_date}
        }).sort([("created_at", 1)])
        
        executions = await execution_cursor.to_list(length=None)
        
        # Process analytics
        analytics = {
            "workflow_id": workflow_id,
            "period": period,
            "summary": {
                "total_executions": len(executions),
                "success_rate": 0,
                "average_duration": 0,
                "total_runtime": 0,
                "error_rate": 0
            },
            "timeline": {
                "executions_per_day": {},
                "success_rate_per_day": {},
                "average_duration_per_day": {}
            },
            "performance_trends": {
                "execution_count_trend": [],
                "duration_trend": [],
                "error_trend": []
            },
            "node_performance": {},
            "error_analysis": {
                "error_types": {},
                "failing_nodes": {},
                "error_timeline": []
            },
            "resource_usage": {
                "cpu_usage": [],
                "memory_usage": [],
                "api_calls": []
            }
        }
        
        if executions:
            # Calculate summary metrics
            successful = [e for e in executions if e.get("status") == "completed"]
            failed = [e for e in executions if e.get("status") == "failed"]
            
            analytics["summary"]["success_rate"] = (len(successful) / len(executions)) * 100
            analytics["summary"]["error_rate"] = (len(failed) / len(executions)) * 100
            
            if successful:
                durations = [e.get("duration", 0) for e in successful if e.get("duration")]
                if durations:
                    analytics["summary"]["average_duration"] = sum(durations) / len(durations)
                    analytics["summary"]["total_runtime"] = sum(durations)
            
            # Daily timeline analysis
            daily_data = defaultdict(lambda: {"executions": 0, "successes": 0, "durations": []})
            
            for execution in executions:
                day = execution.get("created_at", datetime.utcnow()).strftime("%Y-%m-%d")
                daily_data[day]["executions"] += 1
                
                if execution.get("status") == "completed":
                    daily_data[day]["successes"] += 1
                    if execution.get("duration"):
                        daily_data[day]["durations"].append(execution["duration"])
            
            # Fill timeline data
            for day, data in daily_data.items():
                analytics["timeline"]["executions_per_day"][day] = data["executions"]
                
                if data["executions"] > 0:
                    success_rate = (data["successes"] / data["executions"]) * 100
                    analytics["timeline"]["success_rate_per_day"][day] = success_rate
                
                if data["durations"]:
                    avg_duration = sum(data["durations"]) / len(data["durations"])
                    analytics["timeline"]["average_duration_per_day"][day] = avg_duration
            
            # Node performance analysis
            node_stats = defaultdict(lambda: {"executions": 0, "successes": 0, "failures": 0, "avg_duration": 0})
            
            for execution in executions:
                execution_log = execution.get("execution_log", [])
                for log_entry in execution_log:
                    node_id = log_entry.get("node_id")
                    if node_id:
                        node_stats[node_id]["executions"] += 1
                        
                        if log_entry.get("status") == "success":
                            node_stats[node_id]["successes"] += 1
                        else:
                            node_stats[node_id]["failures"] += 1
                            
                            # Track error for error analysis
                            error_type = log_entry.get("error", "Unknown error")
                            analytics["error_analysis"]["error_types"][error_type] = \
                                analytics["error_analysis"]["error_types"].get(error_type, 0) + 1
                            
                            analytics["error_analysis"]["failing_nodes"][node_id] = \
                                analytics["error_analysis"]["failing_nodes"].get(node_id, 0) + 1
            
            # Convert node stats
            analytics["node_performance"] = dict(node_stats)
            
            # Generate performance trends (simplified)
            sorted_days = sorted(daily_data.keys())
            for day in sorted_days[-30:]:  # Last 30 days
                data = daily_data[day]
                analytics["performance_trends"]["execution_count_trend"].append({
                    "date": day,
                    "value": data["executions"]
                })
                
                if data["durations"]:
                    avg_duration = sum(data["durations"]) / len(data["durations"])
                    analytics["performance_trends"]["duration_trend"].append({
                        "date": day,
                        "value": avg_duration
                    })
                
                error_count = data["executions"] - data["successes"]
                analytics["performance_trends"]["error_trend"].append({
                    "date": day,
                    "value": error_count
                })
        
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting workflow analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get workflow analytics")

@router.get("/dashboard/overview")
async def get_dashboard_analytics_overview(
    current_user: dict = Depends(get_current_active_user)
):
    """Get comprehensive dashboard analytics overview"""
    try:
        db = get_database()
        
        # Get user's workflows
        workflows_cursor = db.workflows.find({"user_id": current_user["user_id"]})
        workflows = await workflows_cursor.to_list(length=None)
        workflow_ids = [w["id"] for w in workflows]
        
        # Get recent executions (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        executions_cursor = db.workflow_executions.find({
            "workflow_id": {"$in": workflow_ids},
            "created_at": {"$gte": thirty_days_ago}
        })
        executions = await executions_cursor.to_list(length=None)
        
        # Calculate overview metrics
        overview = {
            "user_id": current_user["user_id"],
            "summary": {
                "total_workflows": len(workflows),
                "total_executions": len(executions),
                "active_workflows": 0,
                "success_rate": 0,
                "total_runtime_hours": 0,
                "executions_this_month": len(executions),
                "most_used_integrations": {},
                "workflow_efficiency_score": 0
            },
            "charts": {
                "executions_over_time": [],
                "success_rate_trend": [], 
                "workflow_performance": [],
                "integration_usage": [],
                "error_distribution": []
            },
            "insights": {
                "top_performing_workflows": [],
                "workflows_needing_attention": [],
                "integration_opportunities": [],
                "performance_recommendations": []
            }
        }
        
        if executions:
            # Success rate calculation
            successful = [e for e in executions if e.get("status") == "completed"]
            overview["summary"]["success_rate"] = (len(successful) / len(executions)) * 100
            
            # Runtime calculation
            total_runtime_seconds = sum(e.get("duration", 0) for e in successful)
            overview["summary"]["total_runtime_hours"] = total_runtime_seconds / 3600
            
            # Active workflows (executed in last 7 days)
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            recent_workflow_ids = {
                e["workflow_id"] for e in executions 
                if e.get("created_at", datetime.utcnow()) > seven_days_ago
            }
            overview["summary"]["active_workflows"] = len(recent_workflow_ids)
            
            # Integration usage analysis
            integration_usage = defaultdict(int)
            for execution in executions:
                execution_log = execution.get("execution_log", [])
                for log_entry in execution_log:
                    if log_entry.get("node_type") == "integration":
                        integration_name = log_entry.get("integration_name", "Unknown")
                        integration_usage[integration_name] += 1
            
            overview["summary"]["most_used_integrations"] = dict(
                sorted(integration_usage.items(), key=lambda x: x[1], reverse=True)[:5]
            )
            
            # Workflow performance analysis
            workflow_performance = defaultdict(lambda: {"executions": 0, "successes": 0, "avg_duration": 0})
            
            for execution in executions:
                workflow_id = execution["workflow_id"]
                workflow_performance[workflow_id]["executions"] += 1
                
                if execution.get("status") == "completed":
                    workflow_performance[workflow_id]["successes"] += 1
                    
                duration = execution.get("duration", 0)
                current_avg = workflow_performance[workflow_id]["avg_duration"]
                current_count = workflow_performance[workflow_id]["executions"]
                
                # Update running average
                workflow_performance[workflow_id]["avg_duration"] = \
                    ((current_avg * (current_count - 1)) + duration) / current_count
            
            # Generate insights
            for workflow_id, perf in workflow_performance.items():
                success_rate = (perf["successes"] / perf["executions"]) * 100 if perf["executions"] > 0 else 0
                
                # Find workflow name
                workflow_name = next((w["name"] for w in workflows if w["id"] == workflow_id), "Unknown")
                
                workflow_insight = {
                    "workflow_id": workflow_id,
                    "workflow_name": workflow_name,
                    "executions": perf["executions"],
                    "success_rate": success_rate,
                    "avg_duration": perf["avg_duration"]
                }
                
                if success_rate >= 95 and perf["executions"] >= 10:
                    overview["insights"]["top_performing_workflows"].append(workflow_insight)
                elif success_rate < 80 or perf["avg_duration"] > 300:  # 5+ minutes
                    overview["insights"]["workflows_needing_attention"].append(workflow_insight)
            
            # Sort insights
            overview["insights"]["top_performing_workflows"].sort(key=lambda x: x["success_rate"], reverse=True)
            overview["insights"]["workflows_needing_attention"].sort(key=lambda x: x["success_rate"])
            
            # Calculate efficiency score
            avg_success_rate = sum(p["success_rate"] for p in workflow_performance.values()) / len(workflow_performance)
            avg_execution_frequency = sum(p["executions"] for p in workflow_performance.values()) / len(workflow_performance)
            
            # Simple efficiency score (0-100)
            overview["summary"]["workflow_efficiency_score"] = min(100, 
                (avg_success_rate * 0.7) + (min(avg_execution_frequency, 50) * 0.6)
            )
        
        return overview
        
    except Exception as e:
        logger.error(f"Error getting dashboard analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard analytics")

@router.get("/integrations/usage")
async def get_integration_usage_analytics(
    period: str = Query("30d", description="Time period: 7d, 30d, 90d"),
    current_user: dict = Depends(get_current_active_user)
):
    """Get detailed integration usage analytics"""
    try:
        db = get_database()
        
        # Calculate time range
        period_map = {"7d": 7, "30d": 30, "90d": 90}
        days = period_map.get(period, 30)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get user's workflows
        workflows_cursor = db.workflows.find({"user_id": current_user["user_id"]})
        workflows = await workflows_cursor.to_list(length=None)
        workflow_ids = [w["id"] for w in workflows]
        
        # Get executions in period
        executions_cursor = db.workflow_executions.find({
            "workflow_id": {"$in": workflow_ids},
            "created_at": {"$gte": start_date}
        })
        executions = await executions_cursor.to_list(length=None)
        
        # Analyze integration usage
        integration_analytics = {
            "period": period,
            "total_integration_calls": 0,
            "unique_integrations_used": 0,
            "integration_breakdown": {},
            "success_rates_by_integration": {},
            "performance_by_integration": {},
            "cost_analysis": {
                "api_calls_by_integration": {},
                "estimated_costs": {}
            },
            "trends": {
                "daily_usage": {},
                "integration_adoption": []
            },
            "recommendations": []
        }
        
        integration_data = defaultdict(lambda: {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "avg_response_time": 0,
            "daily_usage": defaultdict(int),
            "error_types": defaultdict(int)
        })
        
        for execution in executions:
            execution_log = execution.get("execution_log", [])
            day = execution.get("created_at", datetime.utcnow()).strftime("%Y-%m-%d")
            
            for log_entry in execution_log:
                if log_entry.get("node_type") == "integration":
                    integration_name = log_entry.get("integration_name", "Unknown")
                    
                    integration_data[integration_name]["total_calls"] += 1
                    integration_data[integration_name]["daily_usage"][day] += 1
                    
                    if log_entry.get("status") == "success":
                        integration_data[integration_name]["successful_calls"] += 1
                    else:
                        integration_data[integration_name]["failed_calls"] += 1
                        error = log_entry.get("error", "Unknown error")
                        integration_data[integration_name]["error_types"][error] += 1
                    
                    # Response time analysis
                    response_time = log_entry.get("duration", 0)
                    current_avg = integration_data[integration_name]["avg_response_time"]
                    current_total = integration_data[integration_name]["total_calls"]
                    
                    # Update running average
                    integration_data[integration_name]["avg_response_time"] = \
                        ((current_avg * (current_total - 1)) + response_time) / current_total
        
        # Process results
        integration_analytics["total_integration_calls"] = sum(
            data["total_calls"] for data in integration_data.values()
        )
        integration_analytics["unique_integrations_used"] = len(integration_data)
        
        for integration_name, data in integration_data.items():
            # Success rate
            success_rate = (data["successful_calls"] / data["total_calls"] * 100) if data["total_calls"] > 0 else 0
            
            integration_analytics["integration_breakdown"][integration_name] = data["total_calls"]
            integration_analytics["success_rates_by_integration"][integration_name] = success_rate
            integration_analytics["performance_by_integration"][integration_name] = data["avg_response_time"]
            
            # Cost estimation (mock values)
            estimated_cost = data["total_calls"] * 0.01  # $0.01 per API call
            integration_analytics["cost_analysis"]["api_calls_by_integration"][integration_name] = data["total_calls"]
            integration_analytics["cost_analysis"]["estimated_costs"][integration_name] = estimated_cost
            
            # Generate recommendations
            if success_rate < 90:
                integration_analytics["recommendations"].append({
                    "type": "reliability",
                    "integration": integration_name,
                    "message": f"{integration_name} has {success_rate:.1f}% success rate. Consider reviewing configuration or error handling.",
                    "priority": "high" if success_rate < 80 else "medium"
                })
            
            if data["avg_response_time"] > 5000:  # 5+ seconds
                integration_analytics["recommendations"].append({
                    "type": "performance", 
                    "integration": integration_name,
                    "message": f"{integration_name} average response time is {data['avg_response_time']/1000:.1f}s. Consider optimizing requests.",
                    "priority": "medium"
                })
        
        return integration_analytics
        
    except Exception as e:
        logger.error(f"Error getting integration analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get integration analytics")

@router.get("/workflows/comparison")
async def get_workflow_comparison_analytics(
    workflow_ids: List[str] = Query(..., description="List of workflow IDs to compare"),
    current_user: dict = Depends(get_current_active_user)
):
    """Compare performance metrics across multiple workflows"""
    try:
        db = get_database()
        
        # Verify access to all workflows
        workflows_cursor = db.workflows.find({
            "id": {"$in": workflow_ids},
            "user_id": current_user["user_id"]
        })
        workflows = await workflows_cursor.to_list(length=None)
        
        if len(workflows) != len(workflow_ids):
            raise HTTPException(status_code=404, detail="One or more workflows not found")
        
        # Get executions for all workflows (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        executions_cursor = db.workflow_executions.find({
            "workflow_id": {"$in": workflow_ids},
            "created_at": {"$gte": thirty_days_ago}
        })
        executions = await executions_cursor.to_list(length=None)
        
        # Analyze each workflow
        comparison = {
            "workflow_comparison": {},
            "summary": {
                "best_performing": None,
                "most_reliable": None,
                "fastest_execution": None,
                "highest_volume": None
            },
            "recommendations": []
        }
        
        workflow_metrics = {}
        
        for workflow in workflows:
            workflow_id = workflow["id"]
            workflow_executions = [e for e in executions if e["workflow_id"] == workflow_id]
            
            if workflow_executions:
                successful = [e for e in workflow_executions if e.get("status") == "completed"]
                success_rate = (len(successful) / len(workflow_executions)) * 100
                
                avg_duration = 0
                if successful:
                    durations = [e.get("duration", 0) for e in successful]
                    avg_duration = sum(durations) / len(durations) if durations else 0
                
                metrics = {
                    "workflow_name": workflow["name"],
                    "total_executions": len(workflow_executions),
                    "success_rate": success_rate,
                    "average_duration": avg_duration,
                    "total_runtime": sum(e.get("duration", 0) for e in successful),
                    "executions_per_day": len(workflow_executions) / 30,
                    "last_execution": max(e.get("created_at", datetime.min) for e in workflow_executions).isoformat()
                }
            else:
                metrics = {
                    "workflow_name": workflow["name"],
                    "total_executions": 0,
                    "success_rate": 0,
                    "average_duration": 0,
                    "total_runtime": 0,
                    "executions_per_day": 0,
                    "last_execution": None
                }
            
            workflow_metrics[workflow_id] = metrics
            comparison["workflow_comparison"][workflow_id] = metrics
        
        # Determine best performers
        if workflow_metrics:
            # Best overall (combination of success rate and execution volume)
            best_overall = max(workflow_metrics.items(), 
                             key=lambda x: x[1]["success_rate"] * 0.7 + min(x[1]["total_executions"], 100) * 0.3)
            comparison["summary"]["best_performing"] = {
                "workflow_id": best_overall[0],
                "workflow_name": best_overall[1]["workflow_name"],
                "score": best_overall[1]["success_rate"] * 0.7 + min(best_overall[1]["total_executions"], 100) * 0.3
            }
            
            # Most reliable (highest success rate with minimum executions)
            reliable_workflows = {k: v for k, v in workflow_metrics.items() if v["total_executions"] >= 5}
            if reliable_workflows:
                most_reliable = max(reliable_workflows.items(), key=lambda x: x[1]["success_rate"])
                comparison["summary"]["most_reliable"] = {
                    "workflow_id": most_reliable[0],
                    "workflow_name": most_reliable[1]["workflow_name"],
                    "success_rate": most_reliable[1]["success_rate"]
                }
            
            # Fastest execution
            fast_workflows = {k: v for k, v in workflow_metrics.items() if v["average_duration"] > 0}
            if fast_workflows:
                fastest = min(fast_workflows.items(), key=lambda x: x[1]["average_duration"])
                comparison["summary"]["fastest_execution"] = {
                    "workflow_id": fastest[0],
                    "workflow_name": fastest[1]["workflow_name"],
                    "average_duration": fastest[1]["average_duration"]
                }
            
            # Highest volume
            highest_volume = max(workflow_metrics.items(), key=lambda x: x[1]["total_executions"])
            comparison["summary"]["highest_volume"] = {
                "workflow_id": highest_volume[0],
                "workflow_name": highest_volume[1]["workflow_name"],
                "total_executions": highest_volume[1]["total_executions"]
            }
        
        return comparison
        
    except Exception as e:
        logger.error(f"Error getting workflow comparison: {e}")
        raise HTTPException(status_code=500, detail="Failed to compare workflows")