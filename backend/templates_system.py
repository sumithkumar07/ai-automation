# Enhanced Template System with Categories and Community Features
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
import json

class TemplateSystem:
    """Enhanced template system with categorization and community features"""
    
    def __init__(self):
        self.templates = self._initialize_default_templates()
        self.categories = self._initialize_categories()
        self.user_templates = {}
        self.template_usage_stats = {}
    
    def _initialize_categories(self) -> Dict[str, Dict[str, Any]]:
        """Initialize template categories"""
        return {
            "business_automation": {
                "name": "Business Automation",
                "description": "Streamline business processes and operations",
                "icon": "🏢",
                "color": "blue"
            },
            "data_processing": {
                "name": "Data Processing",
                "description": "Transform, analyze, and manage data workflows",
                "icon": "📊",
                "color": "green"
            },
            "marketing": {
                "name": "Marketing & Sales",
                "description": "Automate marketing campaigns and sales processes",
                "icon": "📈",
                "color": "purple"
            },
            "customer_service": {
                "name": "Customer Service",
                "description": "Enhance customer support and communication",
                "icon": "🎧",
                "color": "orange"
            },
            "finance": {
                "name": "Finance & Accounting",
                "description": "Automate financial processes and reporting",
                "icon": "💰",
                "color": "yellow"
            },
            "healthcare": {
                "name": "Healthcare",
                "description": "Streamline healthcare operations and patient care",
                "icon": "🏥",
                "color": "red"
            },
            "ecommerce": {
                "name": "E-commerce",
                "description": "Optimize online store operations and sales",
                "icon": "🛒",
                "color": "indigo"
            },
            "ai_powered": {
                "name": "AI-Powered",
                "description": "Leverage artificial intelligence for automation",
                "icon": "🤖",
                "color": "cyan"
            }
        }
    
    def _initialize_default_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize comprehensive template library"""
        return {
            # Business Automation Templates
            "employee-onboarding": {
                "id": "employee-onboarding",
                "name": "Employee Onboarding Automation",
                "description": "Automate the complete employee onboarding process from document collection to account setup",
                "category": "business_automation",
                "difficulty": "intermediate",
                "rating": 4.8,
                "usage_count": 1250,
                "tags": ["hr", "onboarding", "automation", "documents"],
                "estimated_time_savings": "8 hours per employee",
                "workflow_data": {
                    "nodes": [
                        {
                            "id": "trigger-new-employee",
                            "type": "webhook-trigger",
                            "name": "New Employee Added",
                            "x": 100, "y": 100,
                            "config": {"webhook_url": "/webhooks/new-employee"}
                        },
                        {
                            "id": "collect-documents",
                            "type": "form-generator",
                            "name": "Collect Required Documents",
                            "x": 300, "y": 100,
                            "config": {"form_fields": ["id_document", "tax_forms", "emergency_contact"]}
                        },
                        {
                            "id": "create-accounts",
                            "type": "account-creator",
                            "name": "Create System Accounts",
                            "x": 500, "y": 100,
                            "config": {"systems": ["email", "slack", "hr_system"]}
                        },
                        {
                            "id": "send-welcome",
                            "type": "email-sender",
                            "name": "Send Welcome Package",
                            "x": 700, "y": 100,
                            "config": {"template": "welcome_employee"}
                        }
                    ],
                    "connections": [
                        {"from": "trigger-new-employee", "to": "collect-documents"},
                        {"from": "collect-documents", "to": "create-accounts"},
                        {"from": "create-accounts", "to": "send-welcome"}
                    ]
                },
                "created_at": "2024-01-15T10:00:00Z",
                "updated_at": "2024-01-20T15:30:00Z"
            },
            
            "invoice-processing": {
                "id": "invoice-processing",
                "name": "Automated Invoice Processing",
                "description": "Extract data from invoices, validate information, and update accounting systems automatically",
                "category": "finance",
                "difficulty": "advanced",
                "rating": 4.9,
                "usage_count": 890,
                "tags": ["finance", "ocr", "validation", "accounting"],
                "estimated_time_savings": "2 hours per invoice",
                "workflow_data": {
                    "nodes": [
                        {
                            "id": "invoice-received",
                            "type": "email-trigger",
                            "name": "Invoice Email Received",
                            "x": 100, "y": 100,
                            "config": {"filter": "subject contains 'invoice'"}
                        },
                        {
                            "id": "extract-data",
                            "type": "ai-ocr",
                            "name": "Extract Invoice Data",
                            "x": 300, "y": 100,
                            "config": {"fields": ["amount", "date", "vendor", "items"]}
                        },
                        {
                            "id": "validate-data",
                            "type": "data-validator",
                            "name": "Validate Extracted Data",
                            "x": 500, "y": 100,
                            "config": {"validation_rules": "invoice_validation"}
                        },
                        {
                            "id": "update-accounting",
                            "type": "accounting-system",
                            "name": "Update Accounting System",
                            "x": 700, "y": 100,
                            "config": {"system": "quickbooks"}
                        }
                    ],
                    "connections": [
                        {"from": "invoice-received", "to": "extract-data"},
                        {"from": "extract-data", "to": "validate-data"},
                        {"from": "validate-data", "to": "update-accounting"}
                    ]
                },
                "created_at": "2024-01-10T14:00:00Z",
                "updated_at": "2024-01-25T09:15:00Z"
            },
            
            # Marketing Templates
            "lead-nurturing": {
                "id": "lead-nurturing",
                "name": "AI-Powered Lead Nurturing",
                "description": "Automatically nurture leads with personalized content based on behavior and preferences",
                "category": "marketing",
                "difficulty": "intermediate",
                "rating": 4.7,
                "usage_count": 2100,
                "tags": ["marketing", "ai", "personalization", "email"],
                "estimated_time_savings": "20 hours per week",
                "workflow_data": {
                    "nodes": [
                        {
                            "id": "lead-scored",
                            "type": "crm-trigger",
                            "name": "Lead Score Updated",
                            "x": 100, "y": 100,
                            "config": {"threshold": 75}
                        },
                        {
                            "id": "analyze-behavior",
                            "type": "ai-analyzer",
                            "name": "Analyze Lead Behavior",
                            "x": 300, "y": 100,
                            "config": {"analysis_type": "behavioral_pattern"}
                        },
                        {
                            "id": "personalize-content",
                            "type": "ai-content-generator",
                            "name": "Generate Personalized Content",
                            "x": 500, "y": 100,
                            "config": {"content_type": "email", "personalization": True}
                        },
                        {
                            "id": "send-email",
                            "type": "email-sender",
                            "name": "Send Personalized Email",
                            "x": 700, "y": 100,
                            "config": {"tracking_enabled": True}
                        }
                    ],
                    "connections": [
                        {"from": "lead-scored", "to": "analyze-behavior"},
                        {"from": "analyze-behavior", "to": "personalize-content"},
                        {"from": "personalize-content", "to": "send-email"}
                    ]
                },
                "created_at": "2024-01-12T11:00:00Z",
                "updated_at": "2024-01-22T16:45:00Z"
            },
            
            # Data Processing Templates
            "data-pipeline": {
                "id": "data-pipeline",
                "name": "Advanced Data Processing Pipeline",
                "description": "Extract, transform, and load data from multiple sources with error handling and monitoring",
                "category": "data_processing",
                "difficulty": "advanced",
                "rating": 4.6,
                "usage_count": 650,
                "tags": ["etl", "data", "transformation", "monitoring"],
                "estimated_time_savings": "15 hours per week",
                "workflow_data": {
                    "nodes": [
                        {
                            "id": "schedule-trigger",
                            "type": "cron-scheduler",
                            "name": "Daily Data Sync",
                            "x": 100, "y": 100,
                            "config": {"cron": "0 2 * * *"}
                        },
                        {
                            "id": "extract-data",
                            "type": "database-extractor",
                            "name": "Extract Source Data",
                            "x": 300, "y": 100,
                            "config": {"sources": ["mysql", "api", "csv"]}
                        },
                        {
                            "id": "transform-data",
                            "type": "data-transformer",
                            "name": "Transform and Clean Data",
                            "x": 500, "y": 100,
                            "config": {"transformations": ["normalize", "validate", "enrich"]}
                        },
                        {
                            "id": "load-data",
                            "type": "data-loader",
                            "name": "Load to Data Warehouse",
                            "x": 700, "y": 100,
                            "config": {"destination": "snowflake"}
                        }
                    ],
                    "connections": [
                        {"from": "schedule-trigger", "to": "extract-data"},
                        {"from": "extract-data", "to": "transform-data"},
                        {"from": "transform-data", "to": "load-data"}
                    ]
                },
                "created_at": "2024-01-08T09:00:00Z",
                "updated_at": "2024-01-18T13:20:00Z"
            },
            
            # Customer Service Templates
            "support-ticket-automation": {
                "id": "support-ticket-automation",
                "name": "Intelligent Support Ticket Routing",
                "description": "Automatically categorize, prioritize, and route support tickets using AI",
                "category": "customer_service",
                "difficulty": "intermediate",
                "rating": 4.8,
                "usage_count": 1800,
                "tags": ["support", "ai", "categorization", "routing"],
                "estimated_time_savings": "3 hours per day",
                "workflow_data": {
                    "nodes": [
                        {
                            "id": "ticket-created",
                            "type": "support-system-trigger",
                            "name": "New Ticket Created",
                            "x": 100, "y": 100,
                            "config": {"system": "zendesk"}
                        },
                        {
                            "id": "analyze-ticket",
                            "type": "ai-text-analyzer",
                            "name": "Analyze Ticket Content",
                            "x": 300, "y": 100,
                            "config": {"analysis": ["sentiment", "category", "priority"]}
                        },
                        {
                            "id": "route-ticket",
                            "type": "ticket-router",
                            "name": "Route to Best Agent",
                            "x": 500, "y": 100,
                            "config": {"routing_rules": "expertise_based"}
                        },
                        {
                            "id": "notify-agent",
                            "type": "notification-sender",
                            "name": "Notify Assigned Agent",
                            "x": 700, "y": 100,
                            "config": {"channels": ["slack", "email"]}
                        }
                    ],
                    "connections": [
                        {"from": "ticket-created", "to": "analyze-ticket"},
                        {"from": "analyze-ticket", "to": "route-ticket"},
                        {"from": "route-ticket", "to": "notify-agent"}
                    ]
                },
                "created_at": "2024-01-14T12:00:00Z",
                "updated_at": "2024-01-24T10:30:00Z"
            },
            
            # E-commerce Templates
            "inventory-management": {
                "id": "inventory-management",
                "name": "Smart Inventory Management",
                "description": "Monitor stock levels, predict demand, and automate reordering with AI",
                "category": "ecommerce",
                "difficulty": "advanced",
                "rating": 4.9,
                "usage_count": 720,
                "tags": ["inventory", "prediction", "automation", "ai"],
                "estimated_time_savings": "10 hours per week",
                "workflow_data": {
                    "nodes": [
                        {
                            "id": "stock-check",
                            "type": "inventory-monitor",
                            "name": "Monitor Stock Levels",
                            "x": 100, "y": 100,
                            "config": {"check_interval": "hourly"}
                        },
                        {
                            "id": "demand-prediction",
                            "type": "ai-predictor",
                            "name": "Predict Future Demand",
                            "x": 300, "y": 100,
                            "config": {"model": "seasonal_trend", "horizon": "30_days"}
                        },
                        {
                            "id": "reorder-decision",
                            "type": "decision-maker",
                            "name": "Make Reorder Decision",
                            "x": 500, "y": 100,
                            "config": {"algorithm": "economic_order_quantity"}
                        },
                        {
                            "id": "create-order",
                            "type": "order-creator",
                            "name": "Create Purchase Order",
                            "x": 700, "y": 100,
                            "config": {"approval_required": False}
                        }
                    ],
                    "connections": [
                        {"from": "stock-check", "to": "demand-prediction"},
                        {"from": "demand-prediction", "to": "reorder-decision"},
                        {"from": "reorder-decision", "to": "create-order"}
                    ]
                },
                "created_at": "2024-01-16T08:00:00Z",
                "updated_at": "2024-01-26T14:15:00Z"
            }
        }
    
    def get_templates_by_category(self, category: str = None) -> List[Dict[str, Any]]:
        """Get templates by category or all templates"""
        templates = list(self.templates.values())
        
        if category:
            templates = [t for t in templates if t["category"] == category]
        
        # Sort by popularity (usage_count) and rating
        templates.sort(key=lambda x: (x["usage_count"] * x["rating"]), reverse=True)
        
        return templates
    
    def search_templates(self, query: str, category: str = None, difficulty: str = None) -> List[Dict[str, Any]]:
        """Search templates with filters"""
        templates = list(self.templates.values())
        query_lower = query.lower() if query else ""
        
        # Apply filters
        if category:
            templates = [t for t in templates if t["category"] == category]
        
        if difficulty:
            templates = [t for t in templates if t["difficulty"] == difficulty]
        
        if query:
            templates = [
                t for t in templates
                if (query_lower in t["name"].lower() or
                    query_lower in t["description"].lower() or
                    any(query_lower in tag for tag in t["tags"]))
            ]
        
        # Sort by relevance and popularity
        templates.sort(key=lambda x: (x["rating"] * x["usage_count"]), reverse=True)
        
        return templates
    
    def get_popular_templates(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular templates"""
        templates = list(self.templates.values())
        templates.sort(key=lambda x: x["usage_count"], reverse=True)
        return templates[:limit]
    
    def get_trending_templates(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending templates (recently popular)"""
        # Mock trending calculation based on recent usage growth
        templates = list(self.templates.values())
        
        # Add a trending score (mock calculation)
        for template in templates:
            # Simulate trending score based on usage and recency
            days_since_update = (datetime.utcnow() - datetime.fromisoformat(template["updated_at"].replace('Z', '+00:00'))).days
            trending_score = template["usage_count"] / max(1, days_since_update) * template["rating"]
            template["trending_score"] = trending_score
        
        templates.sort(key=lambda x: x.get("trending_score", 0), reverse=True)
        return templates[:limit]
    
    def get_template_by_id(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get template by ID"""
        return self.templates.get(template_id)
    
    def deploy_template(self, template_id: str, user_id: str, customizations: Dict = None) -> Dict[str, Any]:
        """Deploy template as a new workflow for user"""
        template = self.get_template_by_id(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        # Create workflow from template
        workflow_id = str(uuid.uuid4())
        workflow_data = template["workflow_data"].copy()
        
        # Apply customizations if provided
        if customizations:
            if "name" in customizations:
                workflow_data["name"] = customizations["name"]
            if "description" in customizations:
                workflow_data["description"] = customizations["description"]
        
        # Update usage statistics
        self.template_usage_stats[template_id] = self.template_usage_stats.get(template_id, 0) + 1
        self.templates[template_id]["usage_count"] += 1
        
        return {
            "id": workflow_id,
            "name": template["name"] + " (from template)",
            "description": template["description"],
            "nodes": workflow_data["nodes"],
            "connections": workflow_data["connections"],
            "triggers": workflow_data.get("triggers", []),
            "template_id": template_id,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    
    def get_categories(self) -> Dict[str, Dict[str, Any]]:
        """Get all template categories"""
        # Add template counts to categories
        categories = self.categories.copy()
        
        for category_id, category_info in categories.items():
            template_count = len([t for t in self.templates.values() if t["category"] == category_id])
            category_info["template_count"] = template_count
        
        return categories
    
    def get_template_stats(self) -> Dict[str, Any]:
        """Get template system statistics"""
        total_templates = len(self.templates)
        total_deployments = sum(self.template_usage_stats.values())
        avg_rating = sum(t["rating"] for t in self.templates.values()) / total_templates if total_templates > 0 else 0
        
        return {
            "total_templates": total_templates,
            "total_deployments": total_deployments,
            "average_rating": round(avg_rating, 2),
            "categories": len(self.categories),
            "most_popular": max(self.templates.values(), key=lambda x: x["usage_count"], default={}).get("name", "None")
        }

# Global template system instance
template_system = TemplateSystem()