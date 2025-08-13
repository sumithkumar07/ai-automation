# Advanced Node Library - Industry-Specific & Specialized Nodes
from typing import Dict, List, Any
import json

class AdvancedNodeLibrary:
    """Expanded node library with industry-specific and specialized nodes"""
    
    def __init__(self):
        self.industry_nodes = self._build_industry_nodes()
        self.specialized_nodes = self._build_specialized_nodes()
    
    def _build_industry_nodes(self) -> Dict[str, List[Dict[str, Any]]]:
        """Build industry-specific node categories"""
        return {
            "finance": [
                {
                    "id": "crypto-price-monitor",
                    "name": "Crypto Price Monitor",
                    "description": "Monitor cryptocurrency prices and market changes",
                    "icon": "currency-bitcoin",
                    "category": "trigger",
                    "industry": "finance",
                    "config_schema": {
                        "symbols": ["BTC", "ETH", "ADA"],
                        "threshold_percentage": 5.0,
                        "direction": "both"  # up, down, both
                    }
                },
                {
                    "id": "stock-analysis",
                    "name": "Stock Market Analysis",
                    "description": "Analyze stock market data and trends",
                    "icon": "chart-line",
                    "category": "action",
                    "industry": "finance",
                    "config_schema": {
                        "symbols": ["AAPL", "GOOGL", "MSFT"],
                        "analysis_type": "technical",  # technical, fundamental, sentiment
                        "time_period": "1D"
                    }
                },
                {
                    "id": "payment-processor",
                    "name": "Advanced Payment Processing",
                    "description": "Process payments with fraud detection",
                    "icon": "credit-card",
                    "category": "action",
                    "industry": "finance",
                    "config_schema": {
                        "payment_methods": ["stripe", "paypal", "square"],
                        "fraud_check": True,
                        "currency": "USD"
                    }
                },
                {
                    "id": "invoice-generator",
                    "name": "Smart Invoice Generator",
                    "description": "Generate and send invoices automatically",
                    "icon": "document-text",
                    "category": "action",
                    "industry": "finance",
                    "config_schema": {
                        "template": "professional",
                        "auto_send": True,
                        "payment_terms": 30
                    }
                }
            ],
            "healthcare": [
                {
                    "id": "patient-reminder",
                    "name": "Patient Appointment Reminder",
                    "description": "Send automated appointment reminders",
                    "icon": "calendar-clock",
                    "category": "action",
                    "industry": "healthcare",
                    "config_schema": {
                        "reminder_times": ["24h", "2h", "30m"],
                        "channels": ["sms", "email", "call"],
                        "language": "en"
                    }
                },
                {
                    "id": "health-data-analyzer",
                    "name": "Health Data Analyzer",
                    "description": "Analyze patient health metrics and trends",
                    "icon": "heart",
                    "category": "ai",
                    "industry": "healthcare",
                    "config_schema": {
                        "metrics": ["blood_pressure", "heart_rate", "weight"],
                        "alert_thresholds": True,
                        "hipaa_compliant": True
                    }
                }
            ],
            "ecommerce": [
                {
                    "id": "inventory-monitor",
                    "name": "Smart Inventory Monitor",
                    "description": "Monitor inventory levels and auto-reorder",
                    "icon": "cube",
                    "category": "trigger",
                    "industry": "ecommerce",
                    "config_schema": {
                        "low_stock_threshold": 10,
                        "auto_reorder": True,
                        "suppliers": []
                    }
                },
                {
                    "id": "price-optimizer",
                    "name": "Dynamic Price Optimizer",
                    "description": "Optimize pricing based on market conditions",
                    "icon": "trending-up",
                    "category": "ai",
                    "industry": "ecommerce",
                    "config_schema": {
                        "strategy": "competitive",  # competitive, demand-based, cost-plus
                        "min_margin": 20,
                        "update_frequency": "daily"
                    }
                },
                {
                    "id": "review-analyzer",
                    "name": "Customer Review Analyzer",
                    "description": "Analyze customer reviews and sentiment",
                    "icon": "star",
                    "category": "ai",
                    "industry": "ecommerce",
                    "config_schema": {
                        "platforms": ["amazon", "google", "yelp"],
                        "sentiment_analysis": True,
                        "auto_response": False
                    }
                }
            ],
            "marketing": [
                {
                    "id": "lead-scorer",
                    "name": "AI Lead Scoring",
                    "description": "Score and qualify leads automatically",
                    "icon": "target",
                    "category": "ai",
                    "industry": "marketing",
                    "config_schema": {
                        "scoring_model": "ml_based",
                        "factors": ["engagement", "demographics", "behavior"],
                        "threshold": 70
                    }
                },
                {
                    "id": "content-personalizer",
                    "name": "Content Personalizer",
                    "description": "Personalize content for different audiences",
                    "icon": "user-group",
                    "category": "ai",
                    "industry": "marketing",
                    "config_schema": {
                        "segments": ["new_visitor", "returning", "customer"],
                        "content_types": ["email", "web", "social"],
                        "personalization_level": "high"
                    }
                }
            ],
            "real_estate": [
                {
                    "id": "property-valuation",
                    "name": "AI Property Valuation",
                    "description": "Estimate property values using AI",
                    "icon": "home",
                    "category": "ai",
                    "industry": "real_estate",
                    "config_schema": {
                        "valuation_model": "comparative_market_analysis",
                        "factors": ["location", "size", "condition", "market_trends"],
                        "confidence_interval": 0.95
                    }
                },
                {
                    "id": "market-trends",
                    "name": "Real Estate Market Trends",
                    "description": "Analyze real estate market trends and predictions",
                    "icon": "trending-up",
                    "category": "ai",
                    "industry": "real_estate",
                    "config_schema": {
                        "geographic_scope": "city",  # neighborhood, city, region, national
                        "property_types": ["residential", "commercial"],
                        "forecast_period": "6_months"
                    }
                }
            ]
        }
    
    def _build_specialized_nodes(self) -> Dict[str, List[Dict[str, Any]]]:
        """Build specialized utility nodes"""
        return {
            "advanced_integrations": [
                {
                    "id": "multi-platform-poster",
                    "name": "Multi-Platform Social Poster",
                    "description": "Post content to multiple social platforms simultaneously",
                    "icon": "share",
                    "category": "action",
                    "specialty": "social_media",
                    "config_schema": {
                        "platforms": ["twitter", "linkedin", "facebook", "instagram"],
                        "scheduling": True,
                        "content_adaptation": True,
                        "hashtag_optimization": True
                    }
                },
                {
                    "id": "api-aggregator",
                    "name": "API Data Aggregator",
                    "description": "Combine data from multiple APIs intelligently",
                    "icon": "puzzle-piece",
                    "category": "action",
                    "specialty": "data_processing",
                    "config_schema": {
                        "apis": [],
                        "merge_strategy": "smart_match",
                        "deduplication": True,
                        "rate_limiting": True
                    }
                }
            ],
            "performance_nodes": [
                {
                    "id": "batch-processor",
                    "name": "High-Performance Batch Processor",
                    "description": "Process large datasets in optimized batches",
                    "icon": "server",
                    "category": "action",
                    "specialty": "performance",
                    "config_schema": {
                        "batch_size": 1000,
                        "parallel_workers": 4,
                        "memory_optimization": True,
                        "progress_tracking": True
                    }
                },
                {
                    "id": "cache-manager",
                    "name": "Intelligent Cache Manager",
                    "description": "Manage caching strategies for optimal performance",
                    "icon": "lightning-bolt",
                    "category": "logic",
                    "specialty": "performance",
                    "config_schema": {
                        "cache_strategy": "lru",  # lru, lfu, fifo
                        "ttl": 3600,
                        "size_limit": "100MB",
                        "distribution": "redis"
                    }
                }
            ],
            "security_nodes": [
                {
                    "id": "data-encryption",
                    "name": "Advanced Data Encryption",
                    "description": "Encrypt/decrypt data with multiple algorithms",
                    "icon": "lock-closed",
                    "category": "action",
                    "specialty": "security",
                    "config_schema": {
                        "algorithm": "AES-256",
                        "key_management": "vault",
                        "compliance": ["gdpr", "hipaa", "pci"]
                    }
                },
                {
                    "id": "security-scanner",
                    "name": "Security Vulnerability Scanner",
                    "description": "Scan for security vulnerabilities and threats",
                    "icon": "shield-exclamation",
                    "category": "trigger",
                    "specialty": "security",
                    "config_schema": {
                        "scan_types": ["dependency", "code", "infrastructure"],
                        "severity_threshold": "medium",
                        "auto_remediation": False
                    }
                }
            ]
        }
    
    def get_all_enhanced_nodes(self) -> Dict[str, Any]:
        """Get complete enhanced node library"""
        enhanced_nodes = {
            "categories": {
                "triggers": [],
                "actions": [],
                "logic": [],
                "ai": [],
                # New industry-specific categories
                "finance": [],
                "healthcare": [],
                "ecommerce": [],
                "marketing": [],
                "real_estate": [],
                "security": [],
                "performance": []
            },
            "metadata": {
                "total_nodes": 0,
                "industry_specific": 0,
                "specialized": 0,
                "last_updated": "2025-01-20"
            }
        }
        
        # Add industry nodes
        for industry, nodes in self.industry_nodes.items():
            if industry not in enhanced_nodes["categories"]:
                enhanced_nodes["categories"][industry] = []
            enhanced_nodes["categories"][industry].extend(nodes)
            enhanced_nodes["metadata"]["industry_specific"] += len(nodes)
        
        # Add specialized nodes
        for specialty, nodes in self.specialized_nodes.items():
            for node in nodes:
                category = node.get("category", "action")
                if category in enhanced_nodes["categories"]:
                    enhanced_nodes["categories"][category].append(node)
                enhanced_nodes["metadata"]["specialized"] += 1
        
        # Calculate total
        enhanced_nodes["metadata"]["total_nodes"] = sum(
            len(nodes) for nodes in enhanced_nodes["categories"].values()
        )
        
        return enhanced_nodes
    
    def get_nodes_by_industry(self, industry: str) -> List[Dict[str, Any]]:
        """Get nodes specific to an industry"""
        return self.industry_nodes.get(industry, [])
    
    def get_nodes_by_specialty(self, specialty: str) -> List[Dict[str, Any]]:
        """Get nodes by specialty area"""
        specialty_nodes = []
        for nodes in self.specialized_nodes.values():
            specialty_nodes.extend([
                node for node in nodes 
                if node.get("specialty") == specialty
            ])
        return specialty_nodes

# Global instance
advanced_node_library = AdvancedNodeLibrary()