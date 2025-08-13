import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from .models import Workflow, WorkflowExecution, ExecutionStatus, NodeType
from .integrations_engine import integrations_engine
import logging

logger = logging.getLogger(__name__)

class WorkflowEngine:
    """Engine for executing workflows."""
    
    def __init__(self):
        self.running_workflows: Dict[str, asyncio.Task] = {}
    
    async def execute_workflow(self, workflow: Workflow, trigger_data: Dict[str, Any] = None) -> WorkflowExecution:
        """Execute a workflow."""
        execution = WorkflowExecution(
            workflow_id=workflow.id,
            user_id=workflow.user_id,
            status=ExecutionStatus.RUNNING,
            execution_data=trigger_data or {}
        )
        
        try:
            # Create execution task
            task = asyncio.create_task(self._run_workflow_nodes(workflow, execution))
            self.running_workflows[execution.id] = task
            
            # Wait for completion
            await task
            
            execution.status = ExecutionStatus.SUCCESS
            execution.completed_at = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            execution.status = ExecutionStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
        finally:
            # Clean up
            if execution.id in self.running_workflows:
                del self.running_workflows[execution.id]
        
        return execution
    
    async def _run_workflow_nodes(self, workflow: Workflow, execution: WorkflowExecution):
        """Execute workflow nodes in order."""
        # Find trigger nodes
        trigger_nodes = [node for node in workflow.nodes if node.type == NodeType.TRIGGER]
        if not trigger_nodes:
            raise ValueError("No trigger node found")
        
        # Start execution from trigger nodes
        for trigger_node in trigger_nodes:
            await self._execute_node_chain(workflow, trigger_node, execution)
    
    async def _execute_node_chain(self, workflow: Workflow, start_node, execution: WorkflowExecution, context: Dict[str, Any] = None):
        """Execute a chain of connected nodes."""
        if context is None:
            context = execution.execution_data.copy()
        
        current_node = start_node
        visited_nodes = set()
        
        while current_node and current_node.id not in visited_nodes:
            visited_nodes.add(current_node.id)
            
            # Execute current node
            node_result = await self._execute_node(current_node, context)
            context.update(node_result)
            
            # Find next nodes
            next_connections = [conn for conn in workflow.connections if conn.from_node == current_node.id]
            
            if not next_connections:
                break
            
            # For simplicity, take first connection
            # In a real implementation, this would handle conditions and multiple paths
            next_connection = next_connections[0]
            current_node = next(
                (node for node in workflow.nodes if node.id == next_connection.to_node),
                None
            )
        
        # Update execution data
        execution.execution_data.update(context)
    
    async def _execute_node(self, node, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow node."""
        result = {"node_id": node.id, "executed_at": datetime.utcnow().isoformat()}
        
        if node.type == NodeType.TRIGGER:
            result.update({
                "type": "trigger",
                "message": f"Workflow triggered: {node.name}"
            })
        
        elif node.type == NodeType.ACTION:
            if node.integration:
                # Execute integration action
                action_result = await integrations_engine.execute_action(
                    node.integration,
                    node.config.get("action_id", "default"),
                    node.config,
                    context
                )
                result.update({
                    "type": "action",
                    "integration": node.integration,
                    "result": action_result
                })
            else:
                result.update({
                    "type": "action",
                    "message": f"Custom action executed: {node.name}"
                })
        
        elif node.type == NodeType.CONDITION:
            # Evaluate condition
            condition_result = self._evaluate_condition(node.config, context)
            result.update({
                "type": "condition",
                "condition_met": condition_result,
                "message": f"Condition {node.name}: {'Met' if condition_result else 'Not met'}"
            })
        
        elif node.type == NodeType.DELAY:
            delay_seconds = node.config.get("delay_seconds", 1)
            await asyncio.sleep(delay_seconds)
            result.update({
                "type": "delay",
                "delay_seconds": delay_seconds,
                "message": f"Delayed for {delay_seconds} seconds"
            })
        
        elif node.type == NodeType.AI:
            # AI processing (mock for now)
            ai_result = await self._process_ai_node(node, context)
            result.update({
                "type": "ai",
                "ai_result": ai_result,
                "message": f"AI processing completed: {node.name}"
            })
        
        return result
    
    def _evaluate_condition(self, condition_config: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate a condition node."""
        # Simple condition evaluation
        field = condition_config.get("field")
        operator = condition_config.get("operator", "equals")
        value = condition_config.get("value")
        
        if field not in context:
            return False
        
        context_value = context[field]
        
        if operator == "equals":
            return context_value == value
        elif operator == "contains":
            return value in str(context_value)
        elif operator == "greater_than":
            return float(context_value) > float(value)
        elif operator == "less_than":
            return float(context_value) < float(value)
        
        return False
    
    async def _process_ai_node(self, node, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process an AI node (mock implementation)."""
        # In a real implementation, this would use EMERGENT_LLM_KEY or other AI services
        await asyncio.sleep(0.5)  # Simulate AI processing time
        
        return {
            "ai_response": f"AI processed node '{node.name}' with context keys: {list(context.keys())}",
            "confidence": 0.95,
            "suggestions": ["Consider adding error handling", "Optimize for performance"]
        }
    
    def cancel_workflow(self, execution_id: str) -> bool:
        """Cancel a running workflow."""
        if execution_id in self.running_workflows:
            task = self.running_workflows[execution_id]
            task.cancel()
            del self.running_workflows[execution_id]
            return True
        return False
    
    def get_running_workflows(self) -> List[str]:
        """Get list of currently running workflow execution IDs."""
        return list(self.running_workflows.keys())

# Global instance
workflow_engine = WorkflowEngine()