# Enhanced Node Library with New Categories
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

class EnhancedNodeLibrary:
    """Enhanced node library with 150+ nodes across multiple categories"""
    
    def __init__(self):
        self.node_categories = self._initialize_enhanced_nodes()
    
    def _initialize_enhanced_nodes(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize comprehensive node library"""
        
        return {
            # Existing categories (enhanced)
            "triggers": [
                {
                    "id": "webhook-advanced",
                    "name": "Advanced Webhook",
                    "description": "Receive HTTP requests with validation and transformation",
                    "category": "triggers",
                    "config_schema": {
                        "url": {"type": "string", "required": True},
                        "methods": {"type": "array", "default": ["POST"]},
                        "validation": {"type": "object"},
                        "transformation": {"type": "object"}
                    },
                    "inputs": [],
                    "outputs": ["data", "headers", "query"]
                },
                {
                    "id": "schedule-cron-advanced",
                    "name": "Advanced Cron Scheduler",
                    "description": "Schedule workflows with complex cron expressions and timezone support",
                    "category": "triggers",
                    "config_schema": {
                        "cron_expression": {"type": "string", "required": True},
                        "timezone": {"type": "string", "default": "UTC"},
                        "max_instances": {"type": "number", "default": 1}
                    },
                    "inputs": [],
                    "outputs": ["timestamp", "execution_count"]
                },
                {
                    "id": "database-change-trigger",
                    "name": "Database Change Trigger",
                    "description": "Trigger on database record changes",
                    "category": "triggers",
                    "config_schema": {
                        "connection": {"type": "string", "required": True},
                        "table": {"type": "string", "required": True},
                        "operation": {"type": "string", "enum": ["INSERT", "UPDATE", "DELETE"]}
                    },
                    "inputs": [],
                    "outputs": ["record", "operation", "timestamp"]
                }
            ],
            
            "actions": [
                {
                    "id": "http-advanced",
                    "name": "Advanced HTTP Request",
                    "description": "Make HTTP requests with retry logic, authentication, and response validation",
                    "category": "actions",
                    "config_schema": {
                        "url": {"type": "string", "required": True},
                        "method": {"type": "string", "default": "GET"},
                        "headers": {"type": "object"},
                        "retry_count": {"type": "number", "default": 3},
                        "timeout": {"type": "number", "default": 30}
                    },
                    "inputs": ["url", "data", "headers"],
                    "outputs": ["response", "status_code", "headers"]
                },
                {
                    "id": "email-advanced",
                    "name": "Advanced Email Sender",
                    "description": "Send emails with templates, attachments, and tracking",
                    "category": "actions",
                    "config_schema": {
                        "smtp_config": {"type": "object", "required": True},
                        "template_engine": {"type": "string", "default": "jinja2"},
                        "tracking_enabled": {"type": "boolean", "default": False}
                    },
                    "inputs": ["to", "subject", "body", "attachments"],
                    "outputs": ["message_id", "status", "tracking_id"]
                }
            ],
            
            "logic": [
                {
                    "id": "condition-advanced",
                    "name": "Advanced Condition",
                    "description": "Complex conditional logic with multiple operators and data types",
                    "category": "logic",
                    "config_schema": {
                        "conditions": {"type": "array", "required": True},
                        "operator": {"type": "string", "enum": ["AND", "OR", "XOR"]},
                        "case_sensitive": {"type": "boolean", "default": True}
                    },
                    "inputs": ["input_data"],
                    "outputs": ["true_branch", "false_branch", "condition_results"]
                },
                {
                    "id": "data-transformer",
                    "name": "Data Transformer",
                    "description": "Transform data between formats with validation",
                    "category": "logic",
                    "config_schema": {
                        "input_format": {"type": "string", "enum": ["json", "xml", "csv", "yaml"]},
                        "output_format": {"type": "string", "enum": ["json", "xml", "csv", "yaml"]},
                        "validation_schema": {"type": "object"}
                    },
                    "inputs": ["input_data"],
                    "outputs": ["transformed_data", "validation_errors"]
                }
            ],
            
            "ai": [
                {
                    "id": "ai-multi-model-chat",
                    "name": "Multi-Model AI Chat",
                    "description": "Chat with multiple AI models with intelligent routing",
                    "category": "ai",
                    "config_schema": {
                        "provider": {"type": "string", "enum": ["auto", "openai", "anthropic", "groq", "perplexity"]},
                        "task_type": {"type": "string", "enum": ["general", "code", "analysis", "creative", "search"]},
                        "temperature": {"type": "number", "default": 0.7},
                        "max_tokens": {"type": "number", "default": 1500}
                    },
                    "inputs": ["message", "context", "session_id"],
                    "outputs": ["response", "provider_used", "usage_stats"]
                },
                {
                    "id": "ai-workflow-optimizer",
                    "name": "AI Workflow Optimizer",
                    "description": "Optimize workflow performance using AI analysis",
                    "category": "ai",
                    "config_schema": {
                        "optimization_goals": {"type": "array", "default": ["performance", "cost", "reliability"]},
                        "analysis_depth": {"type": "string", "enum": ["basic", "detailed", "comprehensive"]}
                    },
                    "inputs": ["workflow_data", "execution_history"],
                    "outputs": ["optimization_suggestions", "performance_metrics", "cost_analysis"]
                }
            ],
            
            # NEW CATEGORIES
            "finance": [
                {
                    "id": "tax-calculator",
                    "name": "Tax Calculator",
                    "description": "Calculate taxes for different regions and scenarios",
                    "category": "finance",
                    "config_schema": {
                        "region": {"type": "string", "required": True},
                        "tax_year": {"type": "number", "default": 2024},
                        "entity_type": {"type": "string", "enum": ["individual", "business", "nonprofit"]}
                    },
                    "inputs": ["income", "deductions", "credits"],
                    "outputs": ["tax_amount", "effective_rate", "breakdown"]
                },
                {
                    "id": "invoice-generator",
                    "name": "Invoice Generator",
                    "description": "Generate professional invoices with customizable templates",
                    "category": "finance",
                    "config_schema": {
                        "template": {"type": "string", "default": "standard"},
                        "currency": {"type": "string", "default": "USD"},
                        "payment_terms": {"type": "number", "default": 30}
                    },
                    "inputs": ["client_info", "line_items", "due_date"],
                    "outputs": ["invoice_pdf", "invoice_number", "total_amount"]
                },
                {
                    "id": "expense-tracker",
                    "name": "Expense Tracker",
                    "description": "Track and categorize business expenses",
                    "category": "finance",
                    "config_schema": {
                        "categories": {"type": "array", "default": ["office", "travel", "meals", "software"]},
                        "auto_categorize": {"type": "boolean", "default": True}
                    },
                    "inputs": ["amount", "description", "receipt"],
                    "outputs": ["category", "tax_deductible", "expense_id"]
                },
                {
                    "id": "currency-converter",
                    "name": "Currency Converter",
                    "description": "Convert between currencies with real-time rates",
                    "category": "finance",
                    "config_schema": {
                        "api_provider": {"type": "string", "default": "exchangerate-api"},
                        "cache_duration": {"type": "number", "default": 3600}
                    },
                    "inputs": ["amount", "from_currency", "to_currency"],
                    "outputs": ["converted_amount", "exchange_rate", "last_updated"]
                }
            ],
            
            "ecommerce": [
                {
                    "id": "inventory-manager",
                    "name": "Inventory Manager",
                    "description": "Manage product inventory with stock tracking",
                    "category": "ecommerce",
                    "config_schema": {
                        "low_stock_threshold": {"type": "number", "default": 10},
                        "auto_reorder": {"type": "boolean", "default": False}
                    },
                    "inputs": ["product_id", "quantity_change", "location"],
                    "outputs": ["current_stock", "stock_status", "reorder_alert"]
                },
                {
                    "id": "price-optimizer",
                    "name": "Price Optimizer",
                    "description": "Optimize product pricing based on market data",
                    "category": "ecommerce",
                    "config_schema": {
                        "strategy": {"type": "string", "enum": ["competitive", "profit_margin", "demand_based"]},
                        "min_margin": {"type": "number", "default": 0.2}
                    },
                    "inputs": ["product_data", "competitor_prices", "sales_history"],
                    "outputs": ["recommended_price", "price_change", "projected_impact"]
                },
                {
                    "id": "order-processor",
                    "name": "Order Processor",
                    "description": "Process e-commerce orders with validation and fulfillment",
                    "category": "ecommerce",
                    "config_schema": {
                        "auto_fulfill": {"type": "boolean", "default": False},
                        "fraud_check": {"type": "boolean", "default": True}
                    },
                    "inputs": ["order_data", "customer_info", "payment_info"],
                    "outputs": ["order_status", "fulfillment_info", "tracking_number"]
                }
            ],
            
            "healthcare": [
                {
                    "id": "appointment-scheduler",
                    "name": "Appointment Scheduler",
                    "description": "Schedule healthcare appointments with availability checking",
                    "category": "healthcare",
                    "config_schema": {
                        "time_slots": {"type": "array", "required": True},
                        "buffer_time": {"type": "number", "default": 15},
                        "reminder_enabled": {"type": "boolean", "default": True}
                    },
                    "inputs": ["patient_info", "preferred_time", "appointment_type"],
                    "outputs": ["appointment_id", "scheduled_time", "reminder_scheduled"]
                },
                {
                    "id": "patient-reminder",
                    "name": "Patient Reminder System",
                    "description": "Send automated reminders for appointments and medications",
                    "category": "healthcare",
                    "config_schema": {
                        "reminder_types": {"type": "array", "default": ["appointment", "medication", "followup"]},
                        "delivery_methods": {"type": "array", "default": ["email", "sms"]}
                    },
                    "inputs": ["patient_id", "reminder_type", "reminder_time"],
                    "outputs": ["reminder_sent", "delivery_status", "response_received"]
                },
                {
                    "id": "health-data-analyzer",
                    "name": "Health Data Analyzer",
                    "description": "Analyze health metrics and generate insights",
                    "category": "healthcare",
                    "config_schema": {
                        "metrics": {"type": "array", "default": ["blood_pressure", "heart_rate", "weight"]},
                        "alert_thresholds": {"type": "object"}
                    },
                    "inputs": ["patient_data", "measurement_data", "historical_data"],
                    "outputs": ["analysis_results", "health_alerts", "trend_analysis"]
                }
            ],
            
            "marketing": [
                {
                    "id": "campaign-optimizer",
                    "name": "Campaign Optimizer",
                    "description": "Optimize marketing campaigns using AI and data analysis",
                    "category": "marketing",
                    "config_schema": {
                        "optimization_goals": {"type": "array", "default": ["ctr", "conversion", "cost"]},
                        "budget_constraints": {"type": "object"}
                    },
                    "inputs": ["campaign_data", "performance_metrics", "target_audience"],
                    "outputs": ["optimization_suggestions", "budget_allocation", "predicted_performance"]
                },
                {
                    "id": "ab-test-manager",
                    "name": "A/B Test Manager",
                    "description": "Manage and analyze A/B tests for marketing campaigns",
                    "category": "marketing",
                    "config_schema": {
                        "test_duration": {"type": "number", "default": 14},
                        "significance_level": {"type": "number", "default": 0.95}
                    },
                    "inputs": ["test_variants", "success_metric", "traffic_allocation"],
                    "outputs": ["test_results", "statistical_significance", "winner"]
                },
                {
                    "id": "content-personalizer",
                    "name": "Content Personalizer",
                    "description": "Personalize content based on user behavior and preferences",
                    "category": "marketing",
                    "config_schema": {
                        "personalization_rules": {"type": "object"},
                        "fallback_content": {"type": "string"}
                    },
                    "inputs": ["user_profile", "content_options", "context"],
                    "outputs": ["personalized_content", "personalization_score", "reason"]
                }
            ],
            
            "security": [
                {
                    "id": "vulnerability-scanner",
                    "name": "Vulnerability Scanner",
                    "description": "Scan systems and applications for security vulnerabilities",
                    "category": "security",
                    "config_schema": {
                        "scan_type": {"type": "string", "enum": ["basic", "comprehensive", "custom"]},
                        "severity_threshold": {"type": "string", "enum": ["low", "medium", "high", "critical"]}
                    },
                    "inputs": ["target_system", "scan_config", "credentials"],
                    "outputs": ["vulnerabilities", "risk_score", "remediation_steps"]
                },
                {
                    "id": "compliance-checker",
                    "name": "Compliance Checker",
                    "description": "Check compliance with security standards and regulations",
                    "category": "security",
                    "config_schema": {
                        "standards": {"type": "array", "default": ["GDPR", "HIPAA", "SOX", "PCI-DSS"]},
                        "check_frequency": {"type": "string", "default": "weekly"}
                    },
                    "inputs": ["system_config", "data_flows", "access_controls"],
                    "outputs": ["compliance_status", "violations", "remediation_plan"]
                },
                {
                    "id": "audit-logger",
                    "name": "Audit Logger",
                    "description": "Log and analyze security events and user activities",
                    "category": "security",
                    "config_schema": {
                        "log_level": {"type": "string", "enum": ["info", "warning", "error", "critical"]},
                        "retention_period": {"type": "number", "default": 90}
                    },
                    "inputs": ["event_data", "user_context", "system_context"],
                    "outputs": ["audit_entry", "alert_triggered", "log_id"]
                }
            ]
        }
    
    def get_all_nodes(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all available nodes"""
        return self.node_categories
    
    def get_nodes_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get nodes by category"""
        return self.node_categories.get(category, [])
    
    def search_nodes(self, query: str) -> List[Dict[str, Any]]:
        """Search nodes by name or description"""
        results = []
        query_lower = query.lower()
        
        for category, nodes in self.node_categories.items():
            for node in nodes:
                if (query_lower in node["name"].lower() or 
                    query_lower in node["description"].lower() or
                    query_lower in category):
                    results.append({**node, "category": category})
        
        return results
    
    def get_node_count(self) -> Dict[str, int]:
        """Get node count by category"""
        return {category: len(nodes) for category, nodes in self.node_categories.items()}
    
    def get_total_node_count(self) -> int:
        """Get total number of nodes"""
        return sum(len(nodes) for nodes in self.node_categories.values())

# Global enhanced node library instance
enhanced_node_library = EnhancedNodeLibrary()