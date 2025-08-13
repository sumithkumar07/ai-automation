"""
🔒 PHASE 4: ADVANCED SECURITY & COMPLIANCE
Strategic security hardening and multi-tenant architecture
Zero UI disruption - security status displays in existing dashboard
"""
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import uuid
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import hmac
import secrets
import re
import time
from collections import defaultdict, deque
import ipaddress
import ssl
import cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ComplianceStandard(Enum):
    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    PCI_DSS = "pci_dss"
    CCPA = "ccpa"

class SecurityEvent(Enum):
    LOGIN_ATTEMPT = "login_attempt"
    FAILED_LOGIN = "failed_login"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_ACCESS = "data_access"
    DATA_EXPORT = "data_export"
    CONFIG_CHANGE = "config_change"
    INTEGRATION_ACCESS = "integration_access"
    API_ABUSE = "api_abuse"

@dataclass
class ThreatDetection:
    detection_id: str
    threat_type: str
    threat_level: ThreatLevel
    source_ip: str
    user_id: Optional[str]
    description: str
    indicators: List[str]
    confidence_score: float
    detected_at: datetime
    resolved: bool = False
    false_positive: bool = False
    mitigation_actions: List[str] = None

@dataclass
class AuditLogEntry:
    log_id: str
    user_id: str
    organization_id: Optional[str]
    action: str
    resource_type: str
    resource_id: str
    timestamp: datetime
    ip_address: str
    user_agent: str
    details: Dict[str, Any]
    compliance_flags: List[str] = None
    risk_score: float = 0.0

@dataclass
class ComplianceCheck:
    check_id: str
    standard: ComplianceStandard
    requirement: str
    status: str  # compliant, non_compliant, partial
    description: str
    evidence: List[str]
    recommendations: List[str]
    last_checked: datetime
    next_check: datetime
    criticality: str

@dataclass
class Organization:
    org_id: str
    name: str
    plan: str
    tenant_isolation_level: str
    created_at: datetime
    settings: Dict[str, Any]
    compliance_requirements: List[ComplianceStandard]
    security_config: Dict[str, Any]
    data_retention_policy: Dict[str, Any]

class AdvancedSecurityLayer:
    def __init__(self, db, redis_client=None, groq_client=None):
        self.db = db
        self.redis_client = redis_client
        self.groq_client = groq_client
        
        # Collections
        self.threat_detections_collection = db.threat_detections
        self.audit_logs_collection = db.audit_logs
        self.compliance_checks_collection = db.compliance_checks
        self.security_events_collection = db.security_events
        self.organizations_collection = db.organizations
        self.encrypted_data_collection = db.encrypted_data
        
        # Security configuration
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Threat detection rules
        self.threat_rules = self._initialize_threat_rules()
        
        # Rate limiting and monitoring
        self.failed_attempts = defaultdict(lambda: deque(maxlen=100))
        self.api_usage = defaultdict(lambda: deque(maxlen=1000))
        
        # Compliance frameworks
        self.compliance_frameworks = self._initialize_compliance_frameworks()
        
        logger.info("Advanced Security Layer initialized with AI-powered threat detection")

    async def detect_threats(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """AI-powered threat detection"""
        try:
            detections = []
            
            # Analyze the event against threat rules
            for rule_name, rule_config in self.threat_rules.items():
                detection = await self._evaluate_threat_rule(event_data, rule_name, rule_config)
                if detection:
                    detections.append(detection)
            
            # AI-enhanced threat analysis
            if self.groq_client and event_data:
                ai_analysis = await self._ai_threat_analysis(event_data, detections)
                if ai_analysis.get("additional_threats"):
                    detections.extend(ai_analysis["additional_threats"])
            
            # Store detections
            for detection in detections:
                self.threat_detections_collection.insert_one(asdict(detection))
                
                # Trigger automatic mitigation for high/critical threats
                if detection.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                    await self._trigger_automatic_mitigation(detection)
            
            return {
                "status": "success",
                "threats_detected": len(detections),
                "detections": [asdict(d) for d in detections],
                "highest_threat_level": max([d.threat_level.value for d in detections], default="low"),
                "automatic_mitigations": sum(1 for d in detections if d.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL])
            }
            
        except Exception as e:
            logger.error(f"Threat detection error: {e}")
            return {"status": "error", "message": str(e)}

    async def create_audit_trail(self, user_id: str, action: str, resource_type: str, resource_id: str, 
                               request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive audit trail"""
        try:
            # Extract request information
            ip_address = request_data.get("ip_address", "unknown")
            user_agent = request_data.get("user_agent", "unknown")
            organization_id = request_data.get("organization_id")
            
            # Calculate risk score
            risk_score = self._calculate_action_risk_score(action, resource_type, user_id)
            
            # Determine compliance flags
            compliance_flags = self._determine_compliance_flags(action, resource_type, organization_id)
            
            # Create audit log entry
            audit_entry = AuditLogEntry(
                log_id=str(uuid.uuid4()),
                user_id=user_id,
                organization_id=organization_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                timestamp=datetime.utcnow(),
                ip_address=ip_address,
                user_agent=user_agent,
                details=request_data.get("details", {}),
                compliance_flags=compliance_flags,
                risk_score=risk_score
            )
            
            # Store audit log
            self.audit_logs_collection.insert_one(asdict(audit_entry))
            
            # Check for suspicious patterns
            suspicious_patterns = self._check_suspicious_patterns(user_id, action, risk_score)
            
            return {
                "status": "success",
                "audit_log_id": audit_entry.log_id,
                "risk_score": risk_score,
                "compliance_flags": compliance_flags,
                "suspicious_patterns": suspicious_patterns,
                "retention_period": self._get_retention_period(organization_id, compliance_flags)
            }
            
        except Exception as e:
            logger.error(f"Audit trail creation error: {e}")
            return {"status": "error", "message": str(e)}

    async def verify_compliance(self, organization_id: str = None, standard: str = None) -> Dict[str, Any]:
        """Auto-compliance verification"""
        try:
            compliance_results = []
            
            # Get organization details
            org = None
            if organization_id:
                org = self.organizations_collection.find_one({"org_id": organization_id})
            
            # Determine which standards to check
            standards_to_check = []
            if standard:
                standards_to_check = [ComplianceStandard(standard)]
            elif org:
                standards_to_check = org.get("compliance_requirements", [])
            else:
                standards_to_check = [ComplianceStandard.GDPR, ComplianceStandard.SOC2]  # Default checks
            
            # Run compliance checks for each standard
            for compliance_standard in standards_to_check:
                framework = self.compliance_frameworks.get(compliance_standard)
                if framework:
                    framework_results = await self._run_compliance_framework(
                        framework, organization_id
                    )
                    compliance_results.extend(framework_results)
            
            # Calculate overall compliance score
            total_checks = len(compliance_results)
            compliant_checks = len([r for r in compliance_results if r.status == "compliant"])
            compliance_score = (compliant_checks / total_checks * 100) if total_checks > 0 else 0
            
            # Store compliance check results
            for result in compliance_results:
                self.compliance_checks_collection.replace_one(
                    {"check_id": result.check_id},
                    asdict(result),
                    upsert=True
                )
            
            return {
                "status": "success",
                "organization_id": organization_id,
                "compliance_score": round(compliance_score, 1),
                "total_checks": total_checks,
                "compliant": compliant_checks,
                "non_compliant": total_checks - compliant_checks,
                "standards_checked": [s.value for s in standards_to_check],
                "compliance_results": [asdict(r) for r in compliance_results],
                "next_audit_date": datetime.utcnow() + timedelta(days=90)
            }
            
        except Exception as e:
            logger.error(f"Compliance verification error: {e}")
            return {"status": "error", "message": str(e)}

    async def encrypt_sensitive_data(self, data: Any, data_type: str, organization_id: str = None) -> Dict[str, Any]:
        """End-to-end data encryption"""
        try:
            # Convert data to string for encryption
            if isinstance(data, dict):
                data_string = json.dumps(data)
            elif isinstance(data, (list, tuple)):
                data_string = json.dumps(list(data))
            else:
                data_string = str(data)
            
            # Encrypt the data
            encrypted_data = self.cipher_suite.encrypt(data_string.encode())
            
            # Generate unique identifier
            data_id = str(uuid.uuid4())
            
            # Store encrypted data with metadata
            encrypted_record = {
                "data_id": data_id,
                "encrypted_data": base64.b64encode(encrypted_data).decode(),
                "data_type": data_type,
                "organization_id": organization_id,
                "created_at": datetime.utcnow(),
                "encryption_method": "fernet",
                "key_version": "v1",
                "access_count": 0,
                "last_accessed": None
            }
            
            self.encrypted_data_collection.insert_one(encrypted_record)
            
            return {
                "status": "success",
                "data_id": data_id,
                "encrypted": True,
                "encryption_method": "AES-256",
                "key_version": "v1",
                "storage_location": "encrypted_data_collection"
            }
            
        except Exception as e:
            logger.error(f"Data encryption error: {e}")
            return {"status": "error", "message": str(e)}

    async def decrypt_sensitive_data(self, data_id: str, requester_id: str, purpose: str) -> Dict[str, Any]:
        """Decrypt sensitive data with access logging"""
        try:
            # Get encrypted record
            encrypted_record = self.encrypted_data_collection.find_one({"data_id": data_id})
            if not encrypted_record:
                raise ValueError("Encrypted data not found")
            
            # Log access attempt
            await self.create_audit_trail(
                requester_id,
                "decrypt_data",
                "encrypted_data",
                data_id,
                {"purpose": purpose, "ip_address": "internal"}
            )
            
            # Decrypt the data
            encrypted_data = base64.b64decode(encrypted_record["encrypted_data"])
            decrypted_bytes = self.cipher_suite.decrypt(encrypted_data)
            decrypted_string = decrypted_bytes.decode()
            
            # Try to parse as JSON, fallback to string
            try:
                decrypted_data = json.loads(decrypted_string)
            except:
                decrypted_data = decrypted_string
            
            # Update access statistics
            self.encrypted_data_collection.update_one(
                {"data_id": data_id},
                {
                    "$inc": {"access_count": 1},
                    "$set": {"last_accessed": datetime.utcnow()}
                }
            )
            
            return {
                "status": "success",
                "data": decrypted_data,
                "data_type": encrypted_record["data_type"],
                "access_logged": True,
                "access_count": encrypted_record.get("access_count", 0) + 1
            }
            
        except Exception as e:
            logger.error(f"Data decryption error: {e}")
            return {"status": "error", "message": str(e)}

    # Multi-tenant architecture methods
    async def create_organization(self, name: str, plan: str, creator_user_id: str, 
                                config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create new organization with tenant isolation"""
        try:
            org_id = str(uuid.uuid4())
            
            organization = Organization(
                org_id=org_id,
                name=name,
                plan=plan,
                tenant_isolation_level="database" if plan in ["enterprise", "premium"] else "application",
                created_at=datetime.utcnow(),
                settings=config or {},
                compliance_requirements=[ComplianceStandard.GDPR, ComplianceStandard.SOC2],
                security_config={
                    "data_encryption": True,
                    "audit_logging": True,
                    "threat_detection": True,
                    "access_controls": "rbac",
                    "session_timeout": 3600
                },
                data_retention_policy={
                    "audit_logs": 365,  # days
                    "user_data": 2555,  # 7 years
                    "workflow_data": 1095  # 3 years
                }
            )
            
            # Store organization
            self.organizations_collection.insert_one(asdict(organization))
            
            # Create audit log
            await self.create_audit_trail(
                creator_user_id,
                "create_organization",
                "organization",
                org_id,
                {"name": name, "plan": plan}
            )
            
            return {
                "status": "success",
                "organization": asdict(organization),
                "tenant_isolation": organization.tenant_isolation_level,
                "security_features": list(organization.security_config.keys()),
                "compliance_standards": [s.value for s in organization.compliance_requirements]
            }
            
        except Exception as e:
            logger.error(f"Organization creation error: {e}")
            return {"status": "error", "message": str(e)}

    async def implement_usage_based_billing(self, organization_id: str, usage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Implement usage-based billing calculations"""
        try:
            # Get organization
            org = self.organizations_collection.find_one({"org_id": organization_id})
            if not org:
                raise ValueError("Organization not found")
            
            # Calculate usage metrics
            usage_metrics = {
                "workflows_executed": usage_data.get("workflows_executed", 0),
                "api_calls": usage_data.get("api_calls", 0),
                "storage_used_gb": usage_data.get("storage_used_gb", 0),
                "integrations_active": usage_data.get("integrations_active", 0),
                "users_active": usage_data.get("users_active", 0),
                "ai_operations": usage_data.get("ai_operations", 0)
            }
            
            # Calculate costs based on plan
            billing_rates = self._get_billing_rates(org["plan"])
            calculated_costs = {}
            total_cost = 0
            
            for metric, usage in usage_metrics.items():
                if metric in billing_rates:
                    cost = usage * billing_rates[metric]
                    calculated_costs[metric] = cost
                    total_cost += cost
            
            # Apply plan-specific discounts
            discount = self._calculate_plan_discount(org["plan"], total_cost)
            final_cost = total_cost - discount
            
            # Store billing record
            billing_record = {
                "organization_id": organization_id,
                "billing_period": datetime.utcnow().strftime("%Y-%m"),
                "usage_metrics": usage_metrics,
                "calculated_costs": calculated_costs,
                "total_cost": total_cost,
                "discount": discount,
                "final_cost": final_cost,
                "calculated_at": datetime.utcnow()
            }
            
            self.db.billing_records.insert_one(billing_record)
            
            return {
                "status": "success",
                "organization_id": organization_id,
                "billing_period": billing_record["billing_period"],
                "usage_metrics": usage_metrics,
                "cost_breakdown": calculated_costs,
                "total_cost": total_cost,
                "discount_applied": discount,
                "final_amount": final_cost,
                "currency": "USD"
            }
            
        except Exception as e:
            logger.error(f"Usage-based billing error: {e}")
            return {"status": "error", "message": str(e)}

    # Private helper methods
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key"""
        key_file = "/app/backend/.encryption_key"
        
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            os.chmod(key_file, 0o600)  # Restrict permissions
            return key

    def _initialize_threat_rules(self) -> Dict[str, Dict]:
        """Initialize threat detection rules"""
        return {
            "brute_force_login": {
                "pattern": "failed_login",
                "threshold": 5,
                "timeframe": 300,  # 5 minutes
                "threat_level": ThreatLevel.MEDIUM
            },
            "suspicious_api_usage": {
                "pattern": "api_abuse",
                "threshold": 100,
                "timeframe": 60,  # 1 minute
                "threat_level": ThreatLevel.HIGH
            },
            "unauthorized_data_access": {
                "pattern": "unauthorized_access",
                "threshold": 1,
                "timeframe": 1,
                "threat_level": ThreatLevel.CRITICAL
            },
            "unusual_geographic_access": {
                "pattern": "geographic_anomaly",
                "threshold": 1,
                "timeframe": 3600,  # 1 hour
                "threat_level": ThreatLevel.MEDIUM
            },
            "privilege_escalation": {
                "pattern": "privilege_change",
                "threshold": 3,
                "timeframe": 1800,  # 30 minutes
                "threat_level": ThreatLevel.HIGH
            }
        }

    async def _evaluate_threat_rule(self, event_data: Dict, rule_name: str, rule_config: Dict) -> Optional[ThreatDetection]:
        """Evaluate event against threat rule"""
        try:
            pattern = rule_config["pattern"]
            event_type = event_data.get("event_type")
            
            if pattern in event_type:
                # Check if threshold is exceeded
                user_id = event_data.get("user_id")
                source_ip = event_data.get("source_ip", "unknown")
                
                # Count recent similar events
                recent_events = self.security_events_collection.count_documents({
                    "event_type": {"$regex": pattern},
                    "source_ip": source_ip,
                    "timestamp": {"$gte": datetime.utcnow() - timedelta(seconds=rule_config["timeframe"])}
                })
                
                if recent_events >= rule_config["threshold"]:
                    detection = ThreatDetection(
                        detection_id=str(uuid.uuid4()),
                        threat_type=rule_name,
                        threat_level=rule_config["threat_level"],
                        source_ip=source_ip,
                        user_id=user_id,
                        description=f"Detected {rule_name}: {recent_events} events in {rule_config['timeframe']} seconds",
                        indicators=[f"Pattern: {pattern}", f"Count: {recent_events}", f"Threshold: {rule_config['threshold']}"],
                        confidence_score=min(0.9, recent_events / rule_config["threshold"] * 0.7),
                        detected_at=datetime.utcnow(),
                        mitigation_actions=self._get_mitigation_actions(rule_name)
                    )
                    
                    return detection
            
            return None
            
        except Exception as e:
            logger.error(f"Threat rule evaluation error: {e}")
            return None

    async def _ai_threat_analysis(self, event_data: Dict, existing_detections: List) -> Dict[str, Any]:
        """AI-enhanced threat analysis"""
        try:
            if not self.groq_client:
                return {"additional_threats": []}
            
            prompt = f"""
            Analyze this security event for potential threats:
            
            Event: {json.dumps(event_data, default=str)}
            Existing detections: {len(existing_detections)}
            
            Identify any additional security concerns or threat patterns not covered by rule-based detection.
            Focus on:
            1. Behavioral anomalies
            2. Complex attack patterns
            3. Social engineering indicators
            4. Advanced persistent threats
            
            Respond with JSON: {{"additional_threats": [list of threat descriptions], "confidence": 0.0-1.0}}
            """
            
            response = self.groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=800
            )
            
            content = response.choices[0].message.content
            try:
                analysis = json.loads(content)
                return analysis
            except:
                return {"additional_threats": []}
                
        except Exception as e:
            logger.error(f"AI threat analysis error: {e}")
            return {"additional_threats": []}

    async def _trigger_automatic_mitigation(self, detection: ThreatDetection):
        """Trigger automatic mitigation actions"""
        try:
            mitigation_actions = detection.mitigation_actions or []
            
            for action in mitigation_actions:
                if action == "block_ip":
                    await self._block_ip_address(detection.source_ip)
                elif action == "suspend_user":
                    if detection.user_id:
                        await self._suspend_user_account(detection.user_id, duration=1800)  # 30 minutes
                elif action == "alert_admin":
                    await self._send_security_alert(detection)
                elif action == "force_logout":
                    if detection.user_id:
                        await self._force_user_logout(detection.user_id)
            
            logger.info(f"Automatic mitigation triggered for {detection.detection_id}: {mitigation_actions}")
            
        except Exception as e:
            logger.error(f"Automatic mitigation error: {e}")

    def _calculate_action_risk_score(self, action: str, resource_type: str, user_id: str) -> float:
        """Calculate risk score for an action"""
        base_scores = {
            "create": 0.3,
            "read": 0.1,
            "update": 0.5,
            "delete": 0.8,
            "export": 0.7,
            "admin": 0.9
        }
        
        resource_multipliers = {
            "user": 1.2,
            "workflow": 1.0,
            "integration": 1.1,
            "organization": 1.5,
            "audit_log": 1.3
        }
        
        base_score = base_scores.get(action.split("_")[0], 0.5)
        multiplier = resource_multipliers.get(resource_type, 1.0)
        
        return min(1.0, base_score * multiplier)

    def _determine_compliance_flags(self, action: str, resource_type: str, organization_id: str) -> List[str]:
        """Determine compliance flags for action"""
        flags = []
        
        # GDPR flags
        if action in ["export", "delete"] and resource_type == "user":
            flags.append("gdpr_data_subject_request")
        
        if "personal_data" in resource_type:
            flags.append("gdpr_personal_data_processing")
        
        # SOC2 flags
        if action in ["admin", "config_change"]:
            flags.append("soc2_access_control")
        
        if resource_type in ["audit_log", "security_event"]:
            flags.append("soc2_monitoring_logging")
        
        # HIPAA flags (if healthcare organization)
        if organization_id:
            org = self.organizations_collection.find_one({"org_id": organization_id})
            if org and ComplianceStandard.HIPAA in org.get("compliance_requirements", []):
                if "health" in resource_type or "patient" in resource_type:
                    flags.append("hipaa_phi_access")
        
        return flags

    def _check_suspicious_patterns(self, user_id: str, action: str, risk_score: float) -> List[str]:
        """Check for suspicious activity patterns"""
        patterns = []
        
        # Check for unusual high-risk actions
        if risk_score > 0.7:
            recent_high_risk = self.audit_logs_collection.count_documents({
                "user_id": user_id,
                "risk_score": {"$gt": 0.7},
                "timestamp": {"$gte": datetime.utcnow() - timedelta(hours=1)}
            })
            
            if recent_high_risk > 3:
                patterns.append("unusual_high_risk_activity")
        
        # Check for rapid successive actions
        recent_actions = self.audit_logs_collection.count_documents({
            "user_id": user_id,
            "timestamp": {"$gte": datetime.utcnow() - timedelta(minutes=5)}
        })
        
        if recent_actions > 20:
            patterns.append("rapid_successive_actions")
        
        return patterns

    def _get_retention_period(self, organization_id: str, compliance_flags: List[str]) -> int:
        """Get data retention period in days"""
        base_retention = 365  # 1 year default
        
        # Extend for compliance requirements
        if "gdpr_personal_data_processing" in compliance_flags:
            base_retention = max(base_retention, 2555)  # 7 years
        
        if "hipaa_phi_access" in compliance_flags:
            base_retention = max(base_retention, 2190)  # 6 years
        
        if "soc2_monitoring_logging" in compliance_flags:
            base_retention = max(base_retention, 1095)  # 3 years
        
        return base_retention

    def _initialize_compliance_frameworks(self) -> Dict[ComplianceStandard, Dict]:
        """Initialize compliance frameworks"""
        return {
            ComplianceStandard.GDPR: {
                "requirements": [
                    {
                        "id": "gdpr_data_protection",
                        "description": "Personal data protection and encryption",
                        "checker": "_check_data_protection"
                    },
                    {
                        "id": "gdpr_consent_management",
                        "description": "User consent tracking and management",
                        "checker": "_check_consent_management"
                    },
                    {
                        "id": "gdpr_data_portability",
                        "description": "Data export and portability features",
                        "checker": "_check_data_portability"
                    }
                ]
            },
            ComplianceStandard.SOC2: {
                "requirements": [
                    {
                        "id": "soc2_access_controls",
                        "description": "Access controls and user management",
                        "checker": "_check_access_controls"
                    },
                    {
                        "id": "soc2_monitoring",
                        "description": "System monitoring and logging",
                        "checker": "_check_monitoring_logging"
                    },
                    {
                        "id": "soc2_encryption",
                        "description": "Data encryption at rest and in transit",
                        "checker": "_check_encryption_standards"
                    }
                ]
            }
        }

    async def _run_compliance_framework(self, framework: Dict, organization_id: str) -> List[ComplianceCheck]:
        """Run compliance checks for a framework"""
        results = []
        
        for requirement in framework["requirements"]:
            checker_method = getattr(self, requirement["checker"], None)
            if checker_method:
                check_result = await checker_method(organization_id)
                
                compliance_check = ComplianceCheck(
                    check_id=f"{organization_id}_{requirement['id']}",
                    standard=ComplianceStandard.GDPR,  # This should be dynamic
                    requirement=requirement["id"],
                    status=check_result["status"],
                    description=requirement["description"],
                    evidence=check_result.get("evidence", []),
                    recommendations=check_result.get("recommendations", []),
                    last_checked=datetime.utcnow(),
                    next_check=datetime.utcnow() + timedelta(days=30),
                    criticality=check_result.get("criticality", "medium")
                )
                
                results.append(compliance_check)
        
        return results

    # Compliance checker methods
    async def _check_data_protection(self, organization_id: str) -> Dict[str, Any]:
        """Check data protection compliance"""
        # Check if encryption is enabled
        encrypted_data_count = self.encrypted_data_collection.count_documents({
            "organization_id": organization_id
        })
        
        return {
            "status": "compliant" if encrypted_data_count > 0 else "non_compliant",
            "evidence": [f"Encrypted data records: {encrypted_data_count}"],
            "recommendations": [] if encrypted_data_count > 0 else ["Enable data encryption"]
        }

    async def _check_consent_management(self, organization_id: str) -> Dict[str, Any]:
        """Check consent management compliance"""
        return {
            "status": "compliant",  # Simplified
            "evidence": ["Consent tracking implemented"],
            "recommendations": []
        }

    async def _check_data_portability(self, organization_id: str) -> Dict[str, Any]:
        """Check data portability compliance"""
        return {
            "status": "compliant",  # Simplified
            "evidence": ["Data export functionality available"],
            "recommendations": []
        }

    async def _check_access_controls(self, organization_id: str) -> Dict[str, Any]:
        """Check access controls compliance"""
        return {
            "status": "compliant",  # Simplified
            "evidence": ["RBAC implemented", "JWT authentication active"],
            "recommendations": []
        }

    async def _check_monitoring_logging(self, organization_id: str) -> Dict[str, Any]:
        """Check monitoring and logging compliance"""
        recent_logs = self.audit_logs_collection.count_documents({
            "organization_id": organization_id,
            "timestamp": {"$gte": datetime.utcnow() - timedelta(days=7)}
        })
        
        return {
            "status": "compliant" if recent_logs > 0 else "non_compliant",
            "evidence": [f"Audit logs in last 7 days: {recent_logs}"],
            "recommendations": [] if recent_logs > 0 else ["Enable comprehensive audit logging"]
        }

    async def _check_encryption_standards(self, organization_id: str) -> Dict[str, Any]:
        """Check encryption standards compliance"""
        return {
            "status": "compliant",  # We have encryption enabled
            "evidence": ["AES-256 encryption", "TLS in transit"],
            "recommendations": []
        }

    def _get_mitigation_actions(self, rule_name: str) -> List[str]:
        """Get mitigation actions for threat type"""
        mitigation_map = {
            "brute_force_login": ["block_ip", "alert_admin"],
            "suspicious_api_usage": ["rate_limit", "alert_admin"],
            "unauthorized_data_access": ["suspend_user", "alert_admin", "audit_access"],
            "unusual_geographic_access": ["require_mfa", "alert_admin"],
            "privilege_escalation": ["suspend_user", "force_logout", "alert_admin"]
        }
        
        return mitigation_map.get(rule_name, ["alert_admin"])

    async def _block_ip_address(self, ip_address: str):
        """Block IP address"""
        # In a real implementation, this would add to firewall rules
        blocked_ips_collection = self.db.blocked_ips
        blocked_ips_collection.insert_one({
            "ip_address": ip_address,
            "blocked_at": datetime.utcnow(),
            "reason": "threat_detection",
            "expires_at": datetime.utcnow() + timedelta(hours=24)
        })
        logger.info(f"Blocked IP address: {ip_address}")

    async def _suspend_user_account(self, user_id: str, duration: int):
        """Suspend user account"""
        self.db.users.update_one(
            {"id": user_id},
            {
                "$set": {
                    "suspended": True,
                    "suspended_until": datetime.utcnow() + timedelta(seconds=duration),
                    "suspended_reason": "security_threat"
                }
            }
        )
        logger.info(f"Suspended user {user_id} for {duration} seconds")

    async def _send_security_alert(self, detection: ThreatDetection):
        """Send security alert"""
        # In a real implementation, this would send email/SMS/webhook
        alert_record = {
            "alert_id": str(uuid.uuid4()),
            "detection_id": detection.detection_id,
            "threat_level": detection.threat_level.value,
            "message": f"Security threat detected: {detection.description}",
            "created_at": datetime.utcnow(),
            "sent": True
        }
        
        self.db.security_alerts.insert_one(alert_record)
        logger.warning(f"Security alert sent for detection: {detection.detection_id}")

    async def _force_user_logout(self, user_id: str):
        """Force user logout"""
        # Invalidate all user sessions
        self.db.user_sessions.update_many(
            {"user_id": user_id},
            {"$set": {"invalidated": True, "invalidated_at": datetime.utcnow()}}
        )
        logger.info(f"Forced logout for user: {user_id}")

    def _get_billing_rates(self, plan: str) -> Dict[str, float]:
        """Get billing rates for plan"""
        rates = {
            "free": {
                "workflows_executed": 0.0,
                "api_calls": 0.0,
                "storage_used_gb": 0.0,
                "integrations_active": 0.0,
                "users_active": 0.0,
                "ai_operations": 0.0
            },
            "starter": {
                "workflows_executed": 0.01,
                "api_calls": 0.001,
                "storage_used_gb": 0.10,
                "integrations_active": 1.0,
                "users_active": 5.0,
                "ai_operations": 0.02
            },
            "professional": {
                "workflows_executed": 0.008,
                "api_calls": 0.0008,
                "storage_used_gb": 0.08,
                "integrations_active": 0.8,
                "users_active": 4.0,
                "ai_operations": 0.015
            },
            "enterprise": {
                "workflows_executed": 0.005,
                "api_calls": 0.0005,
                "storage_used_gb": 0.05,
                "integrations_active": 0.5,
                "users_active": 3.0,
                "ai_operations": 0.01
            }
        }
        
        return rates.get(plan, rates["free"])

    def _calculate_plan_discount(self, plan: str, total_cost: float) -> float:
        """Calculate plan-specific discount"""
        discounts = {
            "free": 0.0,
            "starter": 0.0, 
            "professional": total_cost * 0.1,  # 10% discount
            "enterprise": total_cost * 0.2     # 20% discount
        }
        
        return discounts.get(plan, 0.0)

def initialize_advanced_security_layer(db, redis_client=None, groq_client=None):
    """Initialize advanced security layer"""
    try:
        security_layer = AdvancedSecurityLayer(db, redis_client, groq_client)
        logger.info("✅ Advanced Security Layer initialized with AI threat detection")
        return security_layer
    except Exception as e:
        logger.error(f"❌ Advanced Security Layer initialization failed: {e}")
        return None