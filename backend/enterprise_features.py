# Enterprise Features: Multi-user, Permissions, Audit Logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
import uuid
import json
import logging
from enum import Enum
from pymongo import MongoClient
import os

logger = logging.getLogger(__name__)

# Database connection
MONGO_URL = os.getenv("MONGO_URL")
client = MongoClient(MONGO_URL) if MONGO_URL else None
db = client.aether_automation if client else None

# Enterprise collections
organizations_collection = db.organizations if db else None
user_roles_collection = db.user_roles if db else None
audit_logs_collection = db.audit_logs if db else None
team_workspaces_collection = db.team_workspaces if db else None

class Permission(Enum):
    """System permissions"""
    # Workflow permissions
    WORKFLOW_CREATE = "workflow:create"
    WORKFLOW_READ = "workflow:read"
    WORKFLOW_UPDATE = "workflow:update"
    WORKFLOW_DELETE = "workflow:delete"
    WORKFLOW_EXECUTE = "workflow:execute"
    
    # Integration permissions
    INTEGRATION_CREATE = "integration:create"
    INTEGRATION_READ = "integration:read"
    INTEGRATION_UPDATE = "integration:update"
    INTEGRATION_DELETE = "integration:delete"
    INTEGRATION_TEST = "integration:test"
    
    # Template permissions
    TEMPLATE_CREATE = "template:create"
    TEMPLATE_READ = "template:read"
    TEMPLATE_UPDATE = "template:update"
    TEMPLATE_DELETE = "template:delete"
    TEMPLATE_DEPLOY = "template:deploy"
    
    # Organization permissions
    ORG_ADMIN = "org:admin"
    ORG_MEMBER_INVITE = "org:member:invite"
    ORG_MEMBER_REMOVE = "org:member:remove"
    ORG_SETTINGS = "org:settings"
    
    # System permissions
    SYSTEM_ADMIN = "system:admin"
    AUDIT_LOG_READ = "audit:read"
    METRICS_READ = "metrics:read"

class Role(Enum):
    """User roles"""
    SUPER_ADMIN = "super_admin"
    ORG_ADMIN = "org_admin"
    TEAM_LEAD = "team_lead"
    DEVELOPER = "developer"
    VIEWER = "viewer"

@dataclass
class Organization:
    id: str
    name: str
    plan: str  # free, pro, enterprise
    settings: Dict[str, Any]
    created_at: str
    updated_at: str
    owner_id: str
    member_limit: int = 10
    workflow_limit: int = 100
    storage_limit_gb: int = 10

@dataclass
class UserRole:
    user_id: str
    organization_id: str
    role: str
    permissions: List[str]
    granted_by: str
    granted_at: str
    expires_at: Optional[str] = None

@dataclass
class AuditLogEntry:
    id: str
    user_id: str
    organization_id: str
    action: str
    resource_type: str
    resource_id: str
    details: Dict[str, Any]
    ip_address: str
    user_agent: str
    timestamp: str
    result: str  # success, failure, partial

class EnterpriseManager:
    """Manage enterprise features"""
    
    def __init__(self):
        self.role_permissions = self._define_role_permissions()
        self._create_indexes()
    
    def _define_role_permissions(self) -> Dict[str, List[Permission]]:
        """Define permissions for each role"""
        return {
            Role.SUPER_ADMIN.value: [p for p in Permission],
            
            Role.ORG_ADMIN.value: [
                Permission.WORKFLOW_CREATE,
                Permission.WORKFLOW_READ,
                Permission.WORKFLOW_UPDATE,
                Permission.WORKFLOW_DELETE,
                Permission.WORKFLOW_EXECUTE,
                Permission.INTEGRATION_CREATE,
                Permission.INTEGRATION_READ,
                Permission.INTEGRATION_UPDATE,
                Permission.INTEGRATION_DELETE,
                Permission.INTEGRATION_TEST,
                Permission.TEMPLATE_CREATE,
                Permission.TEMPLATE_READ,
                Permission.TEMPLATE_UPDATE,
                Permission.TEMPLATE_DELETE,
                Permission.TEMPLATE_DEPLOY,
                Permission.ORG_ADMIN,
                Permission.ORG_MEMBER_INVITE,
                Permission.ORG_MEMBER_REMOVE,
                Permission.ORG_SETTINGS,
                Permission.AUDIT_LOG_READ,
                Permission.METRICS_READ
            ],
            
            Role.TEAM_LEAD.value: [
                Permission.WORKFLOW_CREATE,
                Permission.WORKFLOW_READ,
                Permission.WORKFLOW_UPDATE,
                Permission.WORKFLOW_DELETE,
                Permission.WORKFLOW_EXECUTE,
                Permission.INTEGRATION_CREATE,
                Permission.INTEGRATION_READ,
                Permission.INTEGRATION_UPDATE,
                Permission.INTEGRATION_DELETE,
                Permission.TEMPLATE_READ,
                Permission.TEMPLATE_DEPLOY,
                Permission.METRICS_READ
            ],
            
            Role.DEVELOPER.value: [
                Permission.WORKFLOW_CREATE,
                Permission.WORKFLOW_READ,
                Permission.WORKFLOW_UPDATE,
                Permission.WORKFLOW_EXECUTE,
                Permission.INTEGRATION_CREATE,
                Permission.INTEGRATION_READ,
                Permission.INTEGRATION_UPDATE,
                Permission.TEMPLATE_READ,
                Permission.TEMPLATE_DEPLOY
            ],
            
            Role.VIEWER.value: [
                Permission.WORKFLOW_READ,
                Permission.INTEGRATION_READ,
                Permission.TEMPLATE_READ
            ]
        }
    
    def _create_indexes(self):
        """Create database indexes for enterprise collections"""
        if not db:
            return
        
        try:
            # Organization indexes
            organizations_collection.create_index("owner_id")
            organizations_collection.create_index("name")
            
            # User roles indexes
            user_roles_collection.create_index([("user_id", 1), ("organization_id", 1)], unique=True)
            user_roles_collection.create_index("organization_id")
            user_roles_collection.create_index("expires_at", expireAfterSeconds=0)
            
            # Audit log indexes
            audit_logs_collection.create_index([("user_id", 1), ("timestamp", -1)])
            audit_logs_collection.create_index([("organization_id", 1), ("timestamp", -1)])
            audit_logs_collection.create_index("resource_type")
            audit_logs_collection.create_index("action")
            
            # TTL index for audit logs (keep for 2 years)
            audit_logs_collection.create_index("timestamp", expireAfterSeconds=63072000)
            
            logger.info("Enterprise database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create enterprise indexes: {e}")
    
    # Organization Management
    def create_organization(self, name: str, owner_id: str, plan: str = "free") -> Organization:
        """Create a new organization"""
        if not organizations_collection:
            raise Exception("Database not available")
        
        org_id = str(uuid.uuid4())
        
        # Define plan limits
        plan_limits = {
            "free": {"member_limit": 5, "workflow_limit": 10, "storage_limit_gb": 1},
            "pro": {"member_limit": 25, "workflow_limit": 100, "storage_limit_gb": 10},
            "enterprise": {"member_limit": 500, "workflow_limit": 1000, "storage_limit_gb": 100}
        }
        
        limits = plan_limits.get(plan, plan_limits["free"])
        
        organization = Organization(
            id=org_id,
            name=name,
            plan=plan,
            settings={
                "security": {"require_2fa": False, "session_timeout": 3600},
                "notifications": {"slack_webhook": "", "email_alerts": True},
                "features": {"advanced_monitoring": plan in ["pro", "enterprise"]}
            },
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            owner_id=owner_id,
            **limits
        )
        
        # Save to database
        organizations_collection.insert_one(organization.__dict__)
        
        # Assign owner role
        self.assign_user_role(owner_id, org_id, Role.ORG_ADMIN.value, owner_id)
        
        return organization
    
    def get_user_organizations(self, user_id: str) -> List[Organization]:
        """Get organizations where user is a member"""
        if not user_roles_collection or not organizations_collection:
            return []
        
        # Find user roles
        user_roles = list(user_roles_collection.find({"user_id": user_id}))
        org_ids = [role["organization_id"] for role in user_roles]
        
        # Get organizations
        organizations = list(organizations_collection.find({"id": {"$in": org_ids}}))
        
        return [Organization(**org) for org in organizations]
    
    # Role and Permission Management
    def assign_user_role(self, user_id: str, organization_id: str, role: str, granted_by: str, expires_at: str = None):
        """Assign role to user"""
        if not user_roles_collection:
            raise Exception("Database not available")
        
        if role not in self.role_permissions:
            raise ValueError(f"Invalid role: {role}")
        
        user_role = UserRole(
            user_id=user_id,
            organization_id=organization_id,
            role=role,
            permissions=[p.value for p in self.role_permissions[role]],
            granted_by=granted_by,
            granted_at=datetime.utcnow().isoformat(),
            expires_at=expires_at
        )
        
        # Upsert user role
        user_roles_collection.replace_one(
            {"user_id": user_id, "organization_id": organization_id},
            user_role.__dict__,
            upsert=True
        )
        
        # Log action
        self.log_action(
            granted_by, organization_id, "role_assigned", "user_role", user_id,
            {"role": role, "target_user": user_id}, "127.0.0.1", "system"
        )
    
    def check_permission(self, user_id: str, organization_id: str, permission: Permission) -> bool:
        """Check if user has specific permission"""
        if not user_roles_collection:
            return False
        
        user_role = user_roles_collection.find_one({
            "user_id": user_id,
            "organization_id": organization_id
        })
        
        if not user_role:
            return False
        
        # Check if role has expired
        if user_role.get("expires_at"):
            expires_at = datetime.fromisoformat(user_role["expires_at"].replace('Z', '+00:00'))
            if datetime.utcnow() > expires_at:
                return False
        
        return permission.value in user_role.get("permissions", [])
    
    def get_user_permissions(self, user_id: str, organization_id: str) -> List[str]:
        """Get all permissions for user in organization"""
        if not user_roles_collection:
            return []
        
        user_role = user_roles_collection.find_one({
            "user_id": user_id,
            "organization_id": organization_id
        })
        
        if not user_role:
            return []
        
        return user_role.get("permissions", [])
    
    # Audit Logging
    def log_action(self, user_id: str, organization_id: str, action: str, resource_type: str, 
                   resource_id: str, details: Dict[str, Any], ip_address: str, user_agent: str, result: str = "success"):
        """Log user action for audit trail"""
        if not audit_logs_collection:
            return
        
        audit_entry = AuditLogEntry(
            id=str(uuid.uuid4()),
            user_id=user_id,
            organization_id=organization_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow().isoformat(),
            result=result
        )
        
        audit_logs_collection.insert_one(audit_entry.__dict__)
    
    def get_audit_logs(self, organization_id: str, limit: int = 100, offset: int = 0, 
                       user_id: str = None, action: str = None, resource_type: str = None) -> List[AuditLogEntry]:
        """Get audit logs with filters"""
        if not audit_logs_collection:
            return []
        
        query = {"organization_id": organization_id}
        
        if user_id:
            query["user_id"] = user_id
        if action:
            query["action"] = action
        if resource_type:
            query["resource_type"] = resource_type
        
        logs = list(audit_logs_collection.find(query)
                   .sort("timestamp", -1)
                   .skip(offset)
                   .limit(limit))
        
        return [AuditLogEntry(**log) for log in logs]
    
    # Team Workspaces
    def create_team_workspace(self, name: str, organization_id: str, created_by: str, 
                             description: str = "", members: List[str] = None) -> Dict[str, Any]:
        """Create team workspace"""
        if not team_workspaces_collection:
            raise Exception("Database not available")
        
        workspace_id = str(uuid.uuid4())
        workspace = {
            "id": workspace_id,
            "name": name,
            "description": description,
            "organization_id": organization_id,
            "created_by": created_by,
            "members": members or [created_by],
            "settings": {
                "visibility": "team",  # team, organization, private
                "collaboration": {
                    "allow_member_invite": True,
                    "require_approval": False
                }
            },
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        team_workspaces_collection.insert_one(workspace)
        
        # Log action
        self.log_action(
            created_by, organization_id, "workspace_created", "team_workspace", workspace_id,
            {"name": name, "members": len(workspace["members"])}, "127.0.0.1", "system"
        )
        
        return workspace
    
    def get_user_workspaces(self, user_id: str, organization_id: str) -> List[Dict[str, Any]]:
        """Get workspaces where user is a member"""
        if not team_workspaces_collection:
            return []
        
        workspaces = list(team_workspaces_collection.find({
            "organization_id": organization_id,
            "members": user_id
        }))
        
        return workspaces
    
    # Analytics and Reporting
    def get_organization_analytics(self, organization_id: str) -> Dict[str, Any]:
        """Get comprehensive organization analytics"""
        analytics = {
            "users": self._get_user_analytics(organization_id),
            "workflows": self._get_workflow_analytics(organization_id),
            "integrations": self._get_integration_analytics(organization_id),
            "security": self._get_security_analytics(organization_id),
            "usage": self._get_usage_analytics(organization_id)
        }
        
        return analytics
    
    def _get_user_analytics(self, organization_id: str) -> Dict[str, Any]:
        """Get user analytics for organization"""
        if not user_roles_collection:
            return {}
        
        users = list(user_roles_collection.find({"organization_id": organization_id}))
        
        role_distribution = {}
        for user in users:
            role = user.get("role", "unknown")
            role_distribution[role] = role_distribution.get(role, 0) + 1
        
        return {
            "total_users": len(users),
            "role_distribution": role_distribution,
            "active_users_30d": len(users),  # Simplified - would need activity tracking
            "new_users_30d": len([u for u in users if self._is_recent(u.get("granted_at"), 30)])
        }
    
    def _get_security_analytics(self, organization_id: str) -> Dict[str, Any]:
        """Get security analytics"""
        if not audit_logs_collection:
            return {}
        
        # Get recent audit logs
        recent_logs = list(audit_logs_collection.find({
            "organization_id": organization_id,
            "timestamp": {"$gte": (datetime.utcnow() - timedelta(days=30)).isoformat()}
        }))
        
        failed_actions = len([log for log in recent_logs if log.get("result") == "failure"])
        
        return {
            "total_actions_30d": len(recent_logs),
            "failed_actions_30d": failed_actions,
            "success_rate": ((len(recent_logs) - failed_actions) / max(len(recent_logs), 1)) * 100,
            "most_active_users": self._get_most_active_users(recent_logs)
        }
    
    def _get_most_active_users(self, logs: List[Dict]) -> List[Dict[str, Any]]:
        """Get most active users from logs"""
        user_activity = {}
        for log in logs:
            user_id = log.get("user_id", "unknown")
            user_activity[user_id] = user_activity.get(user_id, 0) + 1
        
        sorted_users = sorted(user_activity.items(), key=lambda x: x[1], reverse=True)[:10]
        return [{"user_id": user_id, "actions": count} for user_id, count in sorted_users]
    
    def _is_recent(self, timestamp_str: str, days: int) -> bool:
        """Check if timestamp is within recent days"""
        if not timestamp_str:
            return False
        
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            return datetime.utcnow() - timestamp <= timedelta(days=days)
        except:
            return False
    
    def _get_workflow_analytics(self, organization_id: str) -> Dict[str, Any]:
        """Get workflow analytics (placeholder - would integrate with workflow collection)"""
        return {
            "total_workflows": 0,
            "active_workflows": 0,
            "avg_execution_time": 0,
            "success_rate": 0
        }
    
    def _get_integration_analytics(self, organization_id: str) -> Dict[str, Any]:
        """Get integration analytics (placeholder)"""
        return {
            "total_integrations": 0,
            "active_integrations": 0,
            "most_used_platforms": []
        }
    
    def _get_usage_analytics(self, organization_id: str) -> Dict[str, Any]:
        """Get usage analytics"""
        return {
            "api_calls_30d": 0,
            "storage_used_gb": 0,
            "execution_minutes": 0
        }

# Global enterprise manager instance
enterprise_manager = EnterpriseManager()