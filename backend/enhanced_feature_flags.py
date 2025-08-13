"""
🎛️ FEATURE FLAG SYSTEM - ZERO UI DISRUPTION CONTROLLER
Centralized feature flag management for all 5 phases
"""

import os
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class FeaturePhase(Enum):
    """Feature phases for progressive enhancement"""
    CORE = "core"
    PHASE_2 = "phase_2_ai_automation"
    PHASE_3 = "phase_3_enterprise_collaboration"
    PHASE_4 = "phase_4_next_gen_platform"
    PHASE_5 = "phase_5_future_tech"

@dataclass
class FeatureFlag:
    """Feature flag definition"""
    key: str
    name: str
    description: str
    phase: FeaturePhase
    enabled_by_default: bool = False
    requires_premium: bool = False
    ui_visible: bool = False  # Controls if feature appears in UI
    beta: bool = False

class FeatureFlagManager:
    """Centralized feature flag management system"""
    
    def __init__(self, db):
        self.db = db
        self.user_preferences_collection = db.user_feature_preferences
        
        # Initialize all feature flags
        self._initialize_feature_flags()
        
        logger.info("🎛️ Feature Flag System initialized - ZERO UI DISRUPTION mode active")

    def _initialize_feature_flags(self):
        """Initialize all feature flags for the 5 phases"""
        self.flags = {
            # PHASE 2: Advanced Intelligence & Automation
            "ai_enhanced_dashboard": FeatureFlag(
                key="ai_enhanced_dashboard",
                name="AI Enhanced Dashboard Insights",
                description="AI-powered analytics and insights on dashboard",
                phase=FeaturePhase.PHASE_2,
                ui_visible=False  # Hidden by default
            ),
            "smart_workflow_suggestions": FeatureFlag(
                key="smart_workflow_suggestions",
                name="Smart Workflow Suggestions",
                description="AI-generated workflow recommendations",
                phase=FeaturePhase.PHASE_2,
                ui_visible=False
            ),
            "predictive_analytics": FeatureFlag(
                key="predictive_analytics",
                name="Predictive Analytics",
                description="AI-powered predictive insights",
                phase=FeaturePhase.PHASE_2,
                ui_visible=False
            ),
            "voice_workflow_creation": FeatureFlag(
                key="voice_workflow_creation",
                name="Voice Workflow Creation",
                description="Create workflows using voice commands",
                phase=FeaturePhase.PHASE_2,
                ui_visible=False,
                beta=True
            ),
            "auto_workflow_optimization": FeatureFlag(
                key="auto_workflow_optimization",
                name="Auto Workflow Optimization",
                description="Automatically optimize workflows for performance",
                phase=FeaturePhase.PHASE_2,
                ui_visible=False
            ),
            
            # PHASE 3: Enterprise Collaboration & Scale
            "team_workspaces": FeatureFlag(
                key="team_workspaces",
                name="Team Workspaces",
                description="Collaborative team workspaces with shared resources",
                phase=FeaturePhase.PHASE_3,
                requires_premium=True,
                ui_visible=False
            ),
            "advanced_user_roles": FeatureFlag(
                key="advanced_user_roles",
                name="Advanced User Roles & Permissions",
                description="Fine-grained access control and user management",
                phase=FeaturePhase.PHASE_3,
                requires_premium=True,
                ui_visible=False
            ),
            "realtime_collaboration": FeatureFlag(
                key="realtime_collaboration",
                name="Real-time Collaboration",
                description="Live collaboration on workflows with team members",
                phase=FeaturePhase.PHASE_3,
                ui_visible=False
            ),
            "organization_management": FeatureFlag(
                key="organization_management",
                name="Organization Management",
                description="Multi-organization management with hierarchies",
                phase=FeaturePhase.PHASE_3,
                requires_premium=True,
                ui_visible=False
            ),
            "advanced_audit_logging": FeatureFlag(
                key="advanced_audit_logging",
                name="Advanced Audit Logging",
                description="Comprehensive audit trails and compliance reporting",
                phase=FeaturePhase.PHASE_3,
                requires_premium=True,
                ui_visible=False
            ),
            
            # PHASE 4: Next-Generation Platform Features
            "advanced_analytics_dashboard": FeatureFlag(
                key="advanced_analytics_dashboard",
                name="Advanced Analytics Dashboard",
                description="Comprehensive business intelligence dashboard",
                phase=FeaturePhase.PHASE_4,
                ui_visible=False
            ),
            "business_intelligence_widgets": FeatureFlag(
                key="business_intelligence_widgets",
                name="Business Intelligence Widgets",
                description="Customizable BI widgets and reporting tools",
                phase=FeaturePhase.PHASE_4,
                ui_visible=False
            ),
            "smart_marketplace": FeatureFlag(
                key="smart_marketplace",
                name="Smart Marketplace",
                description="AI-curated marketplace for workflows and integrations",
                phase=FeaturePhase.PHASE_4,
                ui_visible=False
            ),
            "custom_integrations_builder": FeatureFlag(
                key="custom_integrations_builder",
                name="Custom Integrations Builder",
                description="Visual builder for custom API integrations",
                phase=FeaturePhase.PHASE_4,
                ui_visible=False,
                beta=True
            ),
            "workflow_versioning": FeatureFlag(
                key="workflow_versioning",
                name="Advanced Workflow Versioning",
                description="Git-like versioning system for workflows",
                phase=FeaturePhase.PHASE_4,
                ui_visible=False
            ),
            
            # PHASE 5: Innovation & Future Technologies
            "iot_device_integration": FeatureFlag(
                key="iot_device_integration",
                name="IoT Device Integration",
                description="Connect and automate IoT devices",
                phase=FeaturePhase.PHASE_5,
                ui_visible=False,
                beta=True
            ),
            "blockchain_verification": FeatureFlag(
                key="blockchain_verification",
                name="Blockchain Verification System",
                description="Blockchain-based workflow verification and audit",
                phase=FeaturePhase.PHASE_5,
                ui_visible=False,
                beta=True
            ),
            "custom_ai_model_training": FeatureFlag(
                key="custom_ai_model_training",
                name="Custom AI Model Training",
                description="Train custom AI models for specific workflows",
                phase=FeaturePhase.PHASE_5,
                requires_premium=True,
                ui_visible=False,
                beta=True
            ),
            "quantum_enhanced_processing": FeatureFlag(
                key="quantum_enhanced_processing",
                name="Quantum-Enhanced Processing",
                description="Quantum computing optimizations for complex workflows",
                phase=FeaturePhase.PHASE_5,
                ui_visible=False,
                beta=True
            ),
            "ar_vr_workflow_builder": FeatureFlag(
                key="ar_vr_workflow_builder",
                name="AR/VR Workflow Builder",
                description="Build workflows in augmented/virtual reality",
                phase=FeaturePhase.PHASE_5,
                ui_visible=False,
                beta=True
            ),
            
            # PERFORMANCE & CORE ENHANCEMENTS (Always hidden)
            "enhanced_caching": FeatureFlag(
                key="enhanced_caching",
                name="Enhanced Caching System",
                description="Advanced Redis-based caching for better performance",
                phase=FeaturePhase.CORE,
                enabled_by_default=True,
                ui_visible=False
            ),
            "advanced_monitoring": FeatureFlag(
                key="advanced_monitoring",
                name="Advanced System Monitoring",
                description="Real-time system health and performance monitoring",
                phase=FeaturePhase.CORE,
                enabled_by_default=True,
                ui_visible=False
            ),
            "database_optimizations": FeatureFlag(
                key="database_optimizations",
                name="Database Performance Optimizations",
                description="Advanced database indexing and query optimization",
                phase=FeaturePhase.CORE,
                enabled_by_default=True,
                ui_visible=False
            )
        }

    def is_feature_enabled(self, user_id: str, feature_key: str) -> bool:
        """Check if a feature is enabled for a specific user"""
        try:
            flag = self.flags.get(feature_key)
            if not flag:
                return False

            # Check user preferences
            user_prefs = self.user_preferences_collection.find_one({"user_id": user_id})
            if user_prefs and feature_key in user_prefs.get("enabled_features", {}):
                return user_prefs["enabled_features"][feature_key]

            # Return default state (most features are disabled by default for ZERO UI DISRUPTION)
            return flag.enabled_by_default

        except Exception as e:
            logger.error(f"Error checking feature flag {feature_key}: {e}")
            return False

    def enable_feature_for_user(self, user_id: str, feature_key: str) -> bool:
        """Enable a specific feature for a user"""
        try:
            flag = self.flags.get(feature_key)
            if not flag:
                return False

            # Update user preferences
            self.user_preferences_collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        f"enabled_features.{feature_key}": True,
                        "updated_at": datetime.utcnow()
                    }
                },
                upsert=True
            )

            logger.info(f"Feature '{feature_key}' enabled for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error enabling feature {feature_key} for user {user_id}: {e}")
            return False

    def disable_feature_for_user(self, user_id: str, feature_key: str) -> bool:
        """Disable a specific feature for a user"""
        try:
            self.user_preferences_collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        f"enabled_features.{feature_key}": False,
                        "updated_at": datetime.utcnow()
                    }
                },
                upsert=True
            )

            logger.info(f"Feature '{feature_key}' disabled for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error disabling feature {feature_key} for user {user_id}: {e}")
            return False

    def get_user_feature_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get all feature preferences for a user"""
        try:
            user_prefs = self.user_preferences_collection.find_one({"user_id": user_id})
            if not user_prefs:
                return {"enabled_features": {}}

            return {
                "enabled_features": user_prefs.get("enabled_features", {}),
                "updated_at": user_prefs.get("updated_at")
            }

        except Exception as e:
            logger.error(f"Error getting user feature preferences: {e}")
            return {"enabled_features": {}}

    def get_available_features_for_user(self, user_id: str, include_beta: bool = False) -> List[Dict[str, Any]]:
        """Get all available features for a user (for settings UI)"""
        try:
            available_features = []
            user_prefs = self.get_user_feature_preferences(user_id)
            enabled_features = user_prefs.get("enabled_features", {})

            for key, flag in self.flags.items():
                # Skip beta features unless explicitly requested
                if flag.beta and not include_beta:
                    continue
                
                # Skip UI-invisible features (ZERO UI DISRUPTION)
                if not flag.ui_visible:
                    continue

                available_features.append({
                    "key": key,
                    "name": flag.name,
                    "description": flag.description,
                    "phase": flag.phase.value,
                    "enabled": enabled_features.get(key, flag.enabled_by_default),
                    "requires_premium": flag.requires_premium,
                    "beta": flag.beta
                })

            return available_features

        except Exception as e:
            logger.error(f"Error getting available features: {e}")
            return []

    def get_enhanced_response_data(self, user_id: str, base_data: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Enhance response data based on enabled features"""
        try:
            enhanced_data = base_data.copy()

            # Add feature-specific enhancements based on user preferences
            if self.is_feature_enabled(user_id, "ai_enhanced_dashboard") and context == "dashboard":
                enhanced_data["ai_enhanced"] = True
                enhanced_data["ai_insights_available"] = True

            if self.is_feature_enabled(user_id, "advanced_analytics_dashboard"):
                enhanced_data["advanced_analytics_available"] = True

            if self.is_feature_enabled(user_id, "realtime_collaboration"):
                enhanced_data["realtime_features"] = True

            # Add phase indicators (completely hidden from UI)
            enhanced_data["_feature_phases_active"] = []
            for flag in self.flags.values():
                if self.is_feature_enabled(user_id, flag.key):
                    if flag.phase.value not in enhanced_data["_feature_phases_active"]:
                        enhanced_data["_feature_phases_active"].append(flag.phase.value)

            return enhanced_data

        except Exception as e:
            logger.error(f"Error enhancing response data: {e}")
            return base_data

# Global instance
feature_flag_manager = None

def initialize_feature_flag_manager(db):
    """Initialize the feature flag management system"""
    global feature_flag_manager
    feature_flag_manager = FeatureFlagManager(db)
    return feature_flag_manager