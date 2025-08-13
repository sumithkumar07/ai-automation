from pydantic import BaseModel, Field, EmailStr
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid
from enum import Enum

# User Models
class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    PREMIUM = "premium"

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    company: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    first_name: str
    last_name: str
    company: Optional[str] = None
    role: UserRole = UserRole.USER
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Workflow Models
class WorkflowStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"

class NodeType(str, Enum):
    TRIGGER = "trigger"
    ACTION = "action"
    CONDITION = "condition"
    DELAY = "delay"
    AI = "ai"

class WorkflowNode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: NodeType
    name: str
    description: Optional[str] = None
    integration: Optional[str] = None
    config: Dict[str, Any] = {}
    position: Dict[str, float] = {"x": 0, "y": 0}

class WorkflowConnection(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    from_node: str
    to_node: str
    condition: Optional[Dict[str, Any]] = None

class Workflow(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    description: Optional[str] = None
    status: WorkflowStatus = WorkflowStatus.DRAFT
    nodes: List[WorkflowNode] = []
    connections: List[WorkflowConnection] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_run: Optional[datetime] = None
    run_count: int = 0
    success_count: int = 0

class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = None

class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[WorkflowStatus] = None
    nodes: Optional[List[WorkflowNode]] = None
    connections: Optional[List[WorkflowConnection]] = None

# Integration Models
class IntegrationCategory(str, Enum):
    COMMUNICATION = "communication"
    PRODUCTIVITY = "productivity"
    CRM = "crm"
    MARKETING = "marketing"
    DEVELOPMENT = "development"
    DEVELOPER = "developer"  # Alias for development
    FINANCE = "finance"
    STORAGE = "storage"
    AI = "ai"
    ECOMMERCE = "ecommerce"
    ANALYTICS = "analytics"
    SUPPORT = "support"
    DATABASE = "database"
    CONTENT = "content"

class Integration(BaseModel):
    id: str
    name: str
    description: str
    icon_url: str
    category: IntegrationCategory
    is_premium: bool = False
    auth_type: str = "oauth2"  # oauth2, api_key, basic
    config_fields: List[Dict[str, Any]] = []
    actions: List[Dict[str, Any]] = []
    triggers: List[Dict[str, Any]] = []

class UserIntegration(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    integration_id: str
    name: str
    config: Dict[str, Any] = {}
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

# AI Models
class AIWorkflowRequest(BaseModel):
    description: str
    integrations: Optional[List[str]] = None

class AIWorkflowResponse(BaseModel):
    workflow: Dict[str, Any]
    confidence: float
    suggestions: List[str] = []

# Execution Models
class ExecutionStatus(str, Enum):
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

class WorkflowExecution(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str
    user_id: str
    status: ExecutionStatus
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    execution_data: Dict[str, Any] = {}

# Analytics Models
class DashboardStats(BaseModel):
    total_workflows: int
    active_workflows: int
    total_executions: int
    successful_executions: int
    integrations_connected: int
    recent_executions: List[WorkflowExecution]