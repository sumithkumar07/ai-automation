"""
🏢 PHASE 3: Enterprise Collaboration & Scale (Q3 2025)
ZERO UI DISRUPTION - Advanced collaboration features hidden by default
"""

import os
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class UserRole(Enum):
    """Enterprise user roles with specific permissions"""
    OWNER = "owner"
    ADMIN = "admin"  
    EDITOR = "editor"
    VIEWER = "viewer"
    COLLABORATOR = "collaborator"

class Permission(Enum):
    """Fine-grained permissions for enterprise features"""
    # Organization permissions
    ORG_CREATE = "org_create"
    ORG_DELETE = "org_delete"
    ORG_MEMBER_INVITE = "org_member_invite"
    ORG_MEMBER_REMOVE = "org_member_remove"
    ORG_SETTINGS_EDIT = "org_settings_edit"
    
    # Workspace permissions
    WORKSPACE_CREATE = "workspace_create"
    WORKSPACE_DELETE = "workspace_delete"
    WORKSPACE_EDIT = "workspace_edit"
    WORKSPACE_VIEW = "workspace_view"
    
    # Workflow permissions
    WORKFLOW_CREATE = "workflow_create"
    WORKFLOW_EDIT = "workflow_edit"
    WORKFLOW_DELETE = "workflow_delete"
    WORKFLOW_EXECUTE = "workflow_execute"
    WORKFLOW_SHARE = "workflow_share"
    
    # Data permissions
    DATA_READ = "data_read"
    DATA_WRITE = "data_write"
    DATA_DELETE = "data_delete"
    
    # Audit permissions
    AUDIT_LOG_READ = "audit_log_read"
    AUDIT_LOG_EXPORT = "audit_log_export"
    
    # Metrics permissions
    METRICS_READ = "metrics_read"
    METRICS_EXPORT = "metrics_export"

@dataclass
class Organization:
    """Enterprise organization structure"""
    id: str
    name: str
    description: str
    owner_id: str
    plan: str  # free, pro, enterprise
    created_at: datetime
    settings: Dict[str, Any]
    member_count: int = 0
    workspace_count: int = 0

@dataclass
class TeamWorkspace:
    """Collaborative team workspace"""
    id: str
    name: str
    description: str
    organization_id: str
    created_by: str
    created_at: datetime
    members: List[str]
    settings: Dict[str, Any]
    shared_resources: List[str]

@dataclass
class UserRoleAssignment:
    """User role assignment in organization/workspace"""
    user_id: str
    organization_id: str
    workspace_id: Optional[str]
    role: UserRole
    permissions: List[Permission]
    assigned_by: str
    assigned_at: datetime
    expires_at: Optional[datetime] = None

@dataclass
class AuditLogEntry:
    """Comprehensive audit log entry"""
    id: str
    user_id: str
    organization_id: str
    workspace_id: Optional[str]
    action: str
    resource_type: str
    resource_id: str
    details: Dict[str, Any]
    timestamp: datetime
    ip_address: str
    user_agent: str

class EnterpriseCollaborationManager:
    """Advanced enterprise collaboration and scaling features"""
    
    def __init__(self, db):
        self.db = db
        self.organizations_collection = db.organizations
        self.workspaces_collection = db.team_workspaces
        self.user_roles_collection = db.user_roles
        self.audit_logs_collection = db.audit_logs
        self.collaboration_sessions_collection = db.collaboration_sessions
        
        # Define role permissions
        self.role_permissions = {
            UserRole.OWNER: [p for p in Permission],  # All permissions
            UserRole.ADMIN: [
                Permission.ORG_MEMBER_INVITE, Permission.ORG_MEMBER_REMOVE,
                Permission.ORG_SETTINGS_EDIT, Permission.WORKSPACE_CREATE,
                Permission.WORKSPACE_DELETE, Permission.WORKSPACE_EDIT,
                Permission.WORKFLOW_CREATE, Permission.WORKFLOW_EDIT,
                Permission.WORKFLOW_DELETE, Permission.WORKFLOW_EXECUTE,
                Permission.WORKFLOW_SHARE, Permission.DATA_READ,
                Permission.DATA_WRITE, Permission.AUDIT_LOG_READ,
                Permission.METRICS_READ
            ],
            UserRole.EDITOR: [
                Permission.WORKSPACE_VIEW, Permission.WORKSPACE_EDIT,
                Permission.WORKFLOW_CREATE, Permission.WORKFLOW_EDIT,
                Permission.WORKFLOW_EXECUTE, Permission.WORKFLOW_SHARE,
                Permission.DATA_READ, Permission.DATA_WRITE
            ],
            UserRole.COLLABORATOR: [
                Permission.WORKSPACE_VIEW, Permission.WORKFLOW_EDIT,
                Permission.WORKFLOW_EXECUTE, Permission.DATA_READ
            ],
            UserRole.VIEWER: [
                Permission.WORKSPACE_VIEW, Permission.DATA_READ,
                Permission.WORKFLOW_EXECUTE
            ]
        }
        
        logger.info("🏢 Enterprise Collaboration Manager initialized")

    def create_organization(self, name: str, owner_id: str, plan: str = "free") -> Organization:
        """Create a new organization"""
        try:
            org_id = str(uuid.uuid4())
            organization = Organization(
                id=org_id,
                name=name,
                description="",
                owner_id=owner_id,
                plan=plan,
                created_at=datetime.utcnow(),
                settings={
                    "allow_public_workspaces": False,
                    "require_2fa": False,
                    "data_retention_days": 365,
                    "allowed_integrations": [],
                    "workflow_approval_required": False
                }
            )
            
            # Insert organization
            org_doc = organization.__dict__.copy()
            self.organizations_collection.insert_one(org_doc)
            
            # Assign owner role
            self.assign_user_role(owner_id, org_id, UserRole.OWNER, owner_id)
            
            # Log audit entry
            self._log_audit_entry(
                user_id=owner_id,
                organization_id=org_id,
                action="organization_created",
                resource_type="organization",
                resource_id=org_id,
                details={"name": name, "plan": plan}
            )
            
            logger.info(f"Organization '{name}' created by user {owner_id}")
            return organization
            
        except Exception as e:
            logger.error(f"Failed to create organization: {e}")
            raise

    def get_user_organizations(self, user_id: str) -> List[Organization]:
        """Get all organizations where user is a member"""
        try:
            # Get user roles
            user_roles = list(self.user_roles_collection.find({"user_id": user_id}))
            org_ids = [role["organization_id"] for role in user_roles]
            
            # Get organizations
            organizations = []
            for org_doc in self.organizations_collection.find({"id": {"$in": org_ids}}):
                org = Organization(**org_doc)
                organizations.append(org)
            
            return organizations
            
        except Exception as e:
            logger.error(f"Failed to get user organizations: {e}")
            return []

    def assign_user_role(self, user_id: str, organization_id: str, role: UserRole, assigned_by: str, workspace_id: Optional[str] = None):
        """Assign role to user in organization/workspace"""
        try:
            assignment = UserRoleAssignment(
                user_id=user_id,
                organization_id=organization_id,
                workspace_id=workspace_id,
                role=role,
                permissions=self.role_permissions.get(role, []),
                assigned_by=assigned_by,
                assigned_at=datetime.utcnow()
            )
            
            # Insert role assignment
            role_doc = assignment.__dict__.copy()
            role_doc["permissions"] = [p.value for p in role_doc["permissions"]]
            role_doc["role"] = role_doc["role"].value
            
            self.user_roles_collection.insert_one(role_doc)
            
            # Log audit entry
            self._log_audit_entry(
                user_id=assigned_by,
                organization_id=organization_id,
                action="user_role_assigned",
                resource_type="user_role",
                resource_id=user_id,
                details={"role": role.value, "target_user": user_id}
            )
            
            logger.info(f"Role {role.value} assigned to user {user_id} in org {organization_id}")
            
        except Exception as e:
            logger.error(f"Failed to assign user role: {e}")
            raise

    def check_permission(self, user_id: str, organization_id: str, permission: Permission, workspace_id: Optional[str] = None) -> bool:
        """Check if user has specific permission"""
        try:
            # Get user roles
            query = {"user_id": user_id, "organization_id": organization_id}
            if workspace_id:
                query["workspace_id"] = workspace_id
            
            user_roles = list(self.user_roles_collection.find(query))
            
            for role_doc in user_roles:
                if permission.value in role_doc.get("permissions", []):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to check permission: {e}")
            return False

    def create_team_workspace(self, name: str, organization_id: str, created_by: str, description: str = "", members: List[str] = None) -> Dict[str, Any]:
        """Create collaborative team workspace"""
        try:
            workspace_id = str(uuid.uuid4())
            workspace = TeamWorkspace(
                id=workspace_id,
                name=name,
                description=description,
                organization_id=organization_id,
                created_by=created_by,
                created_at=datetime.utcnow(),
                members=members or [created_by],
                settings={
                    "auto_save_enabled": True,
                    "version_control": True,
                    "real_time_sync": True,
                    "access_level": "private"
                },
                shared_resources=[]
            )
            
            # Insert workspace
            workspace_doc = workspace.__dict__.copy()
            self.workspaces_collection.insert_one(workspace_doc)
            
            # Assign creator as workspace admin
            self.assign_user_role(created_by, organization_id, UserRole.ADMIN, created_by, workspace_id)
            
            # Log audit entry
            self._log_audit_entry(
                user_id=created_by,
                organization_id=organization_id,
                action="workspace_created",
                resource_type="workspace",
                resource_id=workspace_id,
                details={"name": name, "members_count": len(workspace.members)}
            )
            
            logger.info(f"Team workspace '{name}' created by user {created_by}")
            return workspace_doc
            
        except Exception as e:
            logger.error(f"Failed to create team workspace: {e}")
            raise

    def get_user_workspaces(self, user_id: str, organization_id: str) -> List[Dict[str, Any]]:
        """Get workspaces where user is a member"""
        try:
            # Get workspaces where user is a member
            workspaces = list(self.workspaces_collection.find({
                "organization_id": organization_id,
                "$or": [
                    {"members": user_id},
                    {"created_by": user_id}
                ]
            }))
            
            return workspaces
            
        except Exception as e:
            logger.error(f"Failed to get user workspaces: {e}")
            return []

    def get_audit_logs(self, organization_id: str, limit: int = 100, offset: int = 0, user_id_filter: str = None, action_filter: str = None) -> List[AuditLogEntry]:
        """Get audit logs for organization"""
        try:
            query = {"organization_id": organization_id}
            
            if user_id_filter:
                query["user_id"] = user_id_filter
            if action_filter:
                query["action"] = action_filter
            
            logs = list(self.audit_logs_collection.find(query)
                       .sort("timestamp", -1)
                       .skip(offset)
                       .limit(limit))
            
            audit_entries = []
            for log_doc in logs:
                entry = AuditLogEntry(**log_doc)
                audit_entries.append(entry)
            
            return audit_entries
            
        except Exception as e:
            logger.error(f"Failed to get audit logs: {e}")
            return []

    def get_organization_analytics(self, organization_id: str) -> Dict[str, Any]:
        """Get comprehensive organization analytics"""
        try:
            # Get organization data
            org = self.organizations_collection.find_one({"id": organization_id})
            if not org:
                return {}
            
            # Get member count
            member_count = self.user_roles_collection.count_documents({"organization_id": organization_id})
            
            # Get workspace count
            workspace_count = self.workspaces_collection.count_documents({"organization_id": organization_id})
            
            # Get workflow count (across all members)
            member_ids = [role["user_id"] for role in self.user_roles_collection.find({"organization_id": organization_id})]
            workflow_count = self.db.workflows.count_documents({"user_id": {"$in": member_ids}})
            
            # Get execution statistics
            execution_stats = list(self.db.executions.aggregate([
                {"$match": {"user_id": {"$in": member_ids}}},
                {"$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }}
            ]))
            
            # Calculate activity metrics
            recent_activity = self.audit_logs_collection.count_documents({
                "organization_id": organization_id,
                "timestamp": {"$gte": datetime.utcnow() - timedelta(days=30)}
            })
            
            analytics = {
                "organization": {
                    "id": organization_id,
                    "name": org["name"],
                    "plan": org["plan"],
                    "created_at": org["created_at"]
                },
                "metrics": {
                    "total_members": member_count,
                    "total_workspaces": workspace_count,
                    "total_workflows": workflow_count,
                    "recent_activity_30d": recent_activity
                },
                "execution_stats": {stat["_id"]: stat["count"] for stat in execution_stats},
                "growth_trends": {
                    "member_growth_rate": 0.0,  # Would calculate based on historical data
                    "workflow_creation_rate": 0.0,
                    "collaboration_activity": recent_activity
                },
                "generated_at": datetime.utcnow()
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get organization analytics: {e}")
            return {}

    def start_collaboration_session(self, workspace_id: str, user_id: str, resource_id: str, resource_type: str) -> str:
        """Start real-time collaboration session"""
        try:
            session_id = str(uuid.uuid4())
            session_doc = {
                "id": session_id,
                "workspace_id": workspace_id,
                "user_id": user_id,
                "resource_id": resource_id,
                "resource_type": resource_type,
                "started_at": datetime.utcnow(),
                "status": "active",
                "participants": [user_id],
                "changes": []
            }
            
            self.collaboration_sessions_collection.insert_one(session_doc)
            logger.info(f"Collaboration session started: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to start collaboration session: {e}")
            raise

    def join_collaboration_session(self, session_id: str, user_id: str) -> bool:
        """Join existing collaboration session"""
        try:
            result = self.collaboration_sessions_collection.update_one(
                {"id": session_id, "status": "active"},
                {
                    "$addToSet": {"participants": user_id},
                    "$set": {"last_activity": datetime.utcnow()}
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"User {user_id} joined collaboration session {session_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to join collaboration session: {e}")
            return False

    def _log_audit_entry(self, user_id: str, organization_id: str, action: str, resource_type: str, resource_id: str, details: Dict[str, Any], workspace_id: str = None):
        """Log audit entry for enterprise compliance"""
        try:
            entry = AuditLogEntry(
                id=str(uuid.uuid4()),
                user_id=user_id,
                organization_id=organization_id,
                workspace_id=workspace_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details,
                timestamp=datetime.utcnow(),
                ip_address="",  # Would be populated from request context
                user_agent=""   # Would be populated from request context
            )
            
            audit_doc = entry.__dict__.copy()
            self.audit_logs_collection.insert_one(audit_doc)
            
        except Exception as e:
            logger.error(f"Failed to log audit entry: {e}")

    def cleanup_expired_sessions(self):
        """Cleanup expired collaboration sessions"""
        try:
            # Clean up sessions older than 24 hours
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            result = self.collaboration_sessions_collection.delete_many({
                "started_at": {"$lt": cutoff_time},
                "status": {"$ne": "active"}
            })
            
            if result.deleted_count > 0:
                logger.info(f"Cleaned up {result.deleted_count} expired collaboration sessions")
                
        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")

# Global instance
enterprise_collaboration_manager = None

def initialize_enterprise_collaboration_manager(db):
    """Initialize the Enterprise Collaboration Manager"""
    global enterprise_collaboration_manager
    enterprise_collaboration_manager = EnterpriseCollaborationManager(db)
    return enterprise_collaboration_manager