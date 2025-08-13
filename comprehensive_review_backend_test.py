#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND ANALYSIS & BUG IDENTIFICATION TEST
=======================================================

This test suite addresses the 10 critical areas requested in the review:
1. Complete System Health Check
2. Automation Workflow Deep Testing  
3. Integration System Validation
4. AI System Comprehensive Testing
5. Template System Validation
6. Authentication & Security
7. Database & Performance
8. Error Handling & Logging
9. API Contract Compliance
10. Missing Functionality Gaps

Focus: Identify ALL current issues and bugs with specific error details and reproduction steps.
"""

import requests
import sys
import json
import time
import uuid
import asyncio
import concurrent.futures
from datetime import datetime
from typing import Dict, List, Any

class ComprehensiveBackendReviewTester:
    def __init__(self, base_url="https://workflow-optimizer-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_issues = []
        self.high_issues = []
        self.medium_issues = []
        self.low_issues = []
        self.created_resources = []
        self.session_id = str(uuid.uuid4())
        
        # Test data
        self.test_user = {
            "email": f"comprehensive_test_{self.session_id[:8]}@example.com",
            "password": "ComprehensiveTest123!",
            "first_name": "Comprehensive",
            "last_name": "Tester"
        }

    def log_issue(self, severity: str, title: str, description: str, endpoint: str = None, reproduction_steps: List[str] = None):
        """Log an issue with severity classification"""
        issue = {
            "severity": severity,
            "title": title,
            "description": description,
            "endpoint": endpoint,
            "reproduction_steps": reproduction_steps or [],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if severity == "Critical":
            self.critical_issues.append(issue)
        elif severity == "High":
            self.high_issues.append(issue)
        elif severity == "Medium":
            self.medium_issues.append(issue)
        else:
            self.low_issues.append(issue)

    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                 data: Dict = None, headers: Dict = None, params: Dict = None, 
                 timeout: int = 10) -> Dict[str, Any]:
        """Run a single API test with comprehensive error tracking"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 [{self.tests_run}] Testing {name}...")
        
        try:
            start_time = time.time()
            
            if method == 'GET':
                response = requests.get(url, headers=test_headers, params=params, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, params=params, timeout=timeout)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, params=params, timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, params=params, timeout=timeout)
            
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            success = response.status_code == expected_status
            
            result = {
                "name": name,
                "success": success,
                "status_code": response.status_code,
                "expected_status": expected_status,
                "response_time_ms": round(response_time, 2),
                "endpoint": endpoint,
                "method": method,
                "response_data": None,
                "error": None
            }
            
            try:
                result["response_data"] = response.json()
            except:
                result["response_data"] = response.text[:500] if response.text else None
            
            if success:
                self.tests_passed += 1
                print(f"✅ PASSED - Status: {response.status_code} ({response_time:.1f}ms)")
            else:
                print(f"❌ FAILED - Expected: {expected_status}, Got: {response.status_code} ({response_time:.1f}ms)")
                if response.text:
                    print(f"   Response: {response.text[:200]}...")
                
                # Log as issue based on severity
                if response.status_code >= 500:
                    severity = "Critical"
                elif response.status_code in [401, 403, 404]:
                    severity = "High"
                else:
                    severity = "Medium"
                
                self.log_issue(
                    severity=severity,
                    title=f"{name} - Status Code Mismatch",
                    description=f"Expected {expected_status}, got {response.status_code}. Response: {response.text[:200]}",
                    endpoint=endpoint,
                    reproduction_steps=[
                        f"Send {method} request to {endpoint}",
                        f"With data: {json.dumps(data) if data else 'None'}",
                        f"Expected {expected_status}, got {response.status_code}"
                    ]
                )
            
            return result
            
        except requests.exceptions.Timeout:
            print(f"❌ TIMEOUT - Request took longer than {timeout}s")
            self.log_issue(
                severity="High",
                title=f"{name} - Request Timeout",
                description=f"Request to {endpoint} timed out after {timeout}s",
                endpoint=endpoint,
                reproduction_steps=[f"Send {method} request to {endpoint}", f"Wait more than {timeout}s"]
            )
            return {"name": name, "success": False, "error": "timeout", "endpoint": endpoint}
            
        except requests.exceptions.ConnectionError:
            print(f"❌ CONNECTION ERROR - Could not connect to {url}")
            self.log_issue(
                severity="Critical",
                title=f"{name} - Connection Error",
                description=f"Could not connect to {url}",
                endpoint=endpoint,
                reproduction_steps=[f"Send {method} request to {endpoint}", "Connection fails"]
            )
            return {"name": name, "success": False, "error": "connection_error", "endpoint": endpoint}
            
        except Exception as e:
            print(f"❌ ERROR - {str(e)}")
            self.log_issue(
                severity="High",
                title=f"{name} - Unexpected Error",
                description=f"Unexpected error: {str(e)}",
                endpoint=endpoint,
                reproduction_steps=[f"Send {method} request to {endpoint}", f"Error occurs: {str(e)}"]
            )
            return {"name": name, "success": False, "error": str(e), "endpoint": endpoint}

    def test_1_complete_system_health_check(self):
        """1. COMPLETE SYSTEM HEALTH CHECK"""
        print("\n" + "="*80)
        print("1. COMPLETE SYSTEM HEALTH CHECK")
        print("="*80)
        
        # Basic connectivity
        self.run_test("System Root Endpoint", "GET", "api/", 200)
        
        # Health check endpoints
        self.run_test("System Status Check", "GET", "api/status", 200)
        
        # Database connectivity test
        result = self.run_test("Database Connectivity Test", "POST", "api/status", 200, {
            "client_name": f"health_check_{self.session_id}"
        })
        
        # Node types availability (should have 35+ nodes)
        node_result = self.run_test("Node Types Availability", "GET", "api/node-types", 200)
        if node_result.get("success") and node_result.get("response_data"):
            node_data = node_result["response_data"]
            if isinstance(node_data, dict) and "categories" in node_data:
                total_nodes = sum(len(category.get("nodes", [])) for category in node_data["categories"])
                if total_nodes < 35:
                    self.log_issue(
                        severity="Medium",
                        title="Node Types Count Below Expected",
                        description=f"Expected 35+ nodes, found {total_nodes}",
                        endpoint="api/node-types",
                        reproduction_steps=["GET /api/node-types", f"Count nodes in categories: {total_nodes}"]
                    )
                else:
                    print(f"✅ Node types count: {total_nodes} (meets 35+ requirement)")

    def test_2_authentication_security(self):
        """6. AUTHENTICATION & SECURITY (moved up for token dependency)"""
        print("\n" + "="*80)
        print("2. AUTHENTICATION & SECURITY")
        print("="*80)
        
        # Test user registration
        reg_result = self.run_test("User Registration", "POST", "api/auth/register", 200, self.test_user)
        
        # Test duplicate registration (should fail)
        self.run_test("Duplicate Registration Prevention", "POST", "api/auth/register", 400, self.test_user)
        
        # Test login
        login_result = self.run_test("User Login", "POST", "api/auth/login", 200, {
            "email": self.test_user["email"],
            "password": self.test_user["password"]
        })
        
        if login_result.get("success") and login_result.get("response_data"):
            token_data = login_result["response_data"]
            if "access_token" in token_data:
                self.token = token_data["access_token"]
                self.user_id = token_data.get("user_id")
                print(f"✅ Authentication token acquired: {self.token[:20]}...")
            else:
                self.log_issue(
                    severity="Critical",
                    title="Login Response Missing Access Token",
                    description="Login successful but no access_token in response",
                    endpoint="api/auth/login",
                    reproduction_steps=["POST /api/auth/login with valid credentials", "Check response for access_token field"]
                )
        
        # Test token validation
        if self.token:
            self.run_test("Token Validation", "GET", "api/auth/me", 200)
            
            # Test invalid token
            invalid_headers = {"Authorization": "Bearer invalid_token_12345"}
            self.run_test("Invalid Token Rejection", "GET", "api/auth/me", 401, headers=invalid_headers)
            
            # Test expired token (simulate by using malformed token)
            expired_headers = {"Authorization": "Bearer expired.token.here"}
            self.run_test("Expired Token Rejection", "GET", "api/auth/me", 401, headers=expired_headers)
        
        # Test protected endpoints without token
        no_auth_headers = {}
        self.run_test("Protected Endpoint Without Auth", "GET", "api/workflows/", 401, headers=no_auth_headers)

    def test_3_automation_workflow_deep_testing(self):
        """2. AUTOMATION WORKFLOW DEEP TESTING"""
        print("\n" + "="*80)
        print("3. AUTOMATION WORKFLOW DEEP TESTING")
        print("="*80)
        
        if not self.token:
            self.log_issue(
                severity="Critical",
                title="Cannot Test Workflows - No Authentication Token",
                description="Workflow testing requires authentication token",
                endpoint="api/workflows/",
                reproduction_steps=["Attempt to test workflows without authentication"]
            )
            return
        
        # Test workflow listing
        self.run_test("Workflow Listing", "GET", "api/workflows/", 200)
        
        # Test workflow creation with comprehensive node types
        workflow_data = {
            "name": f"Comprehensive Test Workflow {self.session_id[:8]}",
            "description": "Test workflow for comprehensive backend analysis",
            "nodes": [
                {
                    "id": "trigger_1",
                    "type": "webhook_trigger",
                    "name": "Webhook Trigger",
                    "config": {"webhook_url": "https://example.com/webhook"},
                    "position": {"x": 100, "y": 100}
                },
                {
                    "id": "action_1", 
                    "type": "email_action",
                    "name": "Send Email",
                    "config": {"to": "test@example.com", "subject": "Test"},
                    "position": {"x": 300, "y": 100}
                },
                {
                    "id": "logic_1",
                    "type": "condition_logic",
                    "name": "Condition Check",
                    "config": {"condition": "data.status == 'active'"},
                    "position": {"x": 500, "y": 100}
                },
                {
                    "id": "ai_1",
                    "type": "ai_text_generation",
                    "name": "AI Text Generation",
                    "config": {"prompt": "Generate a summary"},
                    "position": {"x": 700, "y": 100}
                }
            ],
            "connections": [
                {"from": "trigger_1", "to": "action_1"},
                {"from": "action_1", "to": "logic_1"},
                {"from": "logic_1", "to": "ai_1"}
            ],
            "settings": {
                "enabled": True,
                "retry_count": 3,
                "timeout": 300
            }
        }
        
        create_result = self.run_test("Workflow Creation", "POST", "api/workflows/", 201, workflow_data)
        
        workflow_id = None
        if create_result.get("success") and create_result.get("response_data"):
            workflow_id = create_result["response_data"].get("id")
            self.created_resources.append(("workflow", workflow_id))
            print(f"✅ Created workflow ID: {workflow_id}")
        
        if workflow_id:
            # Test workflow retrieval
            self.run_test("Workflow Retrieval", "GET", f"api/workflows/{workflow_id}", 200)
            
            # Test workflow update
            update_data = {
                "name": f"Updated Workflow {self.session_id[:8]}",
                "description": "Updated description for testing"
            }
            self.run_test("Workflow Update", "PUT", f"api/workflows/{workflow_id}", 200, update_data)
            
            # Test workflow execution
            exec_result = self.run_test("Workflow Execution", "POST", f"api/workflows/{workflow_id}/execute", 200, {
                "input_data": {"test": "data", "status": "active"}
            })
            
            execution_id = None
            if exec_result.get("success") and exec_result.get("response_data"):
                execution_id = exec_result["response_data"].get("execution_id")
                print(f"✅ Workflow execution started: {execution_id}")
            
            # Test execution status tracking
            if execution_id:
                self.run_test("Execution Status Tracking", "GET", f"api/workflows/executions/{execution_id}/status", 200)
                self.run_test("Alternative Execution Status", "GET", f"api/executions/{execution_id}/status", 200)
            
            # Test workflow duplication
            self.run_test("Workflow Duplication", "POST", f"api/workflows/{workflow_id}/duplicate", 201)
            
            # Test workflow autosave
            autosave_data = {
                "nodes": workflow_data["nodes"],
                "connections": workflow_data["connections"],
                "auto_save": True
            }
            self.run_test("Workflow Autosave", "PUT", f"api/workflows/{workflow_id}/autosave", 200, autosave_data)

    def test_4_integration_system_validation(self):
        """3. INTEGRATION SYSTEM VALIDATION"""
        print("\n" + "="*80)
        print("4. INTEGRATION SYSTEM VALIDATION")
        print("="*80)
        
        # Test integration listing (should have 103+ integrations)
        list_result = self.run_test("Integration Listing", "GET", "api/integrations", 200)
        
        integration_count = 0
        if list_result.get("success") and list_result.get("response_data"):
            integrations = list_result["response_data"]
            if isinstance(integrations, list):
                integration_count = len(integrations)
            elif isinstance(integrations, dict) and "integrations" in integrations:
                integration_count = len(integrations["integrations"])
            
            if integration_count < 103:
                self.log_issue(
                    severity="High",
                    title="Integration Count Below Homepage Promise",
                    description=f"Homepage promises 100+ integrations, found {integration_count}",
                    endpoint="api/integrations",
                    reproduction_steps=["GET /api/integrations", f"Count integrations: {integration_count}"]
                )
            else:
                print(f"✅ Integration count: {integration_count} (meets 100+ promise)")
        
        # Test integration categories
        self.run_test("Integration Categories", "GET", "api/integrations/categories", 200)
        
        # Test integration search functionality
        search_tests = [
            ("slack", "Slack integration search"),
            ("google", "Google integrations search"),
            ("ai", "AI integrations search"),
            ("payment", "Payment integrations search")
        ]
        
        for search_term, test_name in search_tests:
            # Test both 'q' and 'query' parameters
            self.run_test(f"{test_name} (q param)", "GET", "api/integrations/search", 200, params={"q": search_term})
            self.run_test(f"{test_name} (query param)", "GET", "api/integrations/search", 200, params={"query": search_term})
        
        # Test integration connection testing
        if integration_count > 0:
            # Use a common integration ID for testing
            test_integration_ids = ["slack", "github", "gmail", "stripe"]
            for integration_id in test_integration_ids:
                self.run_test(f"Integration Connection Test - {integration_id}", 
                            "POST", f"api/integration-testing/test-connection/{integration_id}", 200)

    def test_5_ai_system_comprehensive_testing(self):
        """4. AI SYSTEM COMPREHENSIVE TESTING"""
        print("\n" + "="*80)
        print("5. AI SYSTEM COMPREHENSIVE TESTING")
        print("="*80)
        
        # Test AI workflow generation
        workflow_gen_data = {
            "description": "Create a workflow that processes customer emails and sends automated responses",
            "requirements": ["email processing", "automated response", "customer data"],
            "complexity": "medium"
        }
        self.run_test("AI Workflow Generation", "POST", "api/ai/generate-workflow", 200, workflow_gen_data)
        
        # Test AI integration suggestions
        integration_suggestion_data = {
            "description": "I need to process payments and send confirmation emails",
            "workflow_type": "payment_processing"
        }
        self.run_test("AI Integration Suggestions", "POST", "api/ai/suggest-integrations", 200, integration_suggestion_data)
        
        # Test AI workflow explanation
        explanation_data = {
            "workflow": {
                "nodes": [{"type": "webhook_trigger"}, {"type": "email_action"}],
                "connections": [{"from": "trigger", "to": "action"}]
            }
        }
        self.run_test("AI Workflow Explanation", "POST", "api/ai/explain-workflow", 200, explanation_data)
        
        # Test AI dashboard insights
        self.run_test("AI Dashboard Insights", "GET", "api/ai/dashboard-insights", 200)
        
        # Test AI system status
        self.run_test("AI System Status", "GET", "api/ai/system-status", 200)
        
        # Test AI chat functionality
        chat_data = {
            "message": "How do I create a workflow that integrates Slack with Google Sheets?",
            "context": "workflow_creation"
        }
        self.run_test("AI Chat System", "POST", "api/ai/chat", 200, chat_data)
        
        # Test AI chat with empty message (should fail validation)
        empty_chat_data = {"message": "", "context": "test"}
        self.run_test("AI Chat Empty Message Validation", "POST", "api/ai/chat", 422, empty_chat_data)

    def test_6_template_system_validation(self):
        """5. TEMPLATE SYSTEM VALIDATION"""
        print("\n" + "="*80)
        print("6. TEMPLATE SYSTEM VALIDATION")
        print("="*80)
        
        # Test template listing
        list_result = self.run_test("Template Listing", "GET", "api/templates/", 200)
        
        # Test template creation with 'nodes' format
        template_nodes_data = {
            "name": f"Test Template Nodes {self.session_id[:8]}",
            "description": "Test template with nodes format",
            "category": "automation",
            "nodes": [
                {
                    "id": "trigger_1",
                    "type": "webhook_trigger",
                    "name": "Webhook Trigger",
                    "config": {"webhook_url": "https://example.com/webhook"}
                },
                {
                    "id": "action_1",
                    "type": "email_action", 
                    "name": "Send Email",
                    "config": {"to": "test@example.com", "subject": "Test"}
                }
            ],
            "connections": [{"from": "trigger_1", "to": "action_1"}],
            "tags": ["test", "automation", "email"]
        }
        
        nodes_result = self.run_test("Template Creation (nodes format)", "POST", "api/templates/create", 201, template_nodes_data)
        
        template_id_nodes = None
        if nodes_result.get("success") and nodes_result.get("response_data"):
            template_id_nodes = nodes_result["response_data"].get("id")
            self.created_resources.append(("template", template_id_nodes))
        
        # Test template creation with 'workflow_definition' format
        template_workflow_data = {
            "name": f"Test Template Workflow {self.session_id[:8]}",
            "description": "Test template with workflow_definition format",
            "category": "productivity",
            "workflow_definition": {
                "nodes": [
                    {
                        "id": "trigger_1",
                        "type": "schedule_trigger",
                        "name": "Schedule Trigger",
                        "config": {"schedule": "0 9 * * *"}
                    }
                ],
                "connections": [],
                "settings": {"enabled": True}
            },
            "tags": ["test", "productivity", "schedule"]
        }
        
        workflow_result = self.run_test("Template Creation (workflow_definition format)", "POST", "api/templates/create", 201, template_workflow_data)
        
        template_id_workflow = None
        if workflow_result.get("success") and workflow_result.get("response_data"):
            template_id_workflow = workflow_result["response_data"].get("id")
            self.created_resources.append(("template", template_id_workflow))
        
        # Test template retrieval
        if template_id_nodes:
            self.run_test("Template Detail Retrieval", "GET", f"api/templates/{template_id_nodes}", 200)
        
        # Test template search
        self.run_test("Template Search", "GET", "api/templates/search", 200, params={"q": "automation"})
        
        # Test template rating system
        if template_id_nodes:
            rating_data = {"rating": 5, "review": "Excellent template for automation"}
            self.run_test("Template Rating", "POST", f"api/templates/{template_id_nodes}/rate", 200, rating_data)

    def test_7_database_performance(self):
        """7. DATABASE & PERFORMANCE"""
        print("\n" + "="*80)
        print("7. DATABASE & PERFORMANCE")
        print("="*80)
        
        # Test concurrent requests
        print("\n🔍 Testing concurrent request handling...")
        start_time = time.time()
        
        # Create multiple concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for i in range(5):
                future = executor.submit(self.run_concurrent_test, f"Concurrent Request {i+1}")
                futures.append(future)
            
            concurrent_results = []
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                concurrent_results.append(result)
        
        total_time = time.time() - start_time
        successful_requests = sum(1 for r in concurrent_results if r.get("success"))
        
        print(f"✅ Concurrent Performance: {successful_requests}/5 requests successful in {total_time:.2f}s")
        
        if successful_requests < 4:
            self.log_issue(
                severity="Medium",
                title="Poor Concurrent Request Performance",
                description=f"Only {successful_requests}/5 concurrent requests successful",
                endpoint="multiple",
                reproduction_steps=["Send 5 concurrent requests", f"Only {successful_requests} succeed"]
            )
        
        # Test data persistence
        if self.token:
            # Create a workflow and verify it persists
            persistence_data = {
                "name": f"Persistence Test {self.session_id[:8]}",
                "description": "Testing data persistence",
                "nodes": [{"id": "test", "type": "webhook_trigger"}],
                "connections": []
            }
            
            create_result = self.run_test("Data Persistence - Create", "POST", "api/workflows/", 201, persistence_data)
            
            if create_result.get("success"):
                workflow_id = create_result["response_data"].get("id")
                if workflow_id:
                    # Verify it can be retrieved
                    self.run_test("Data Persistence - Retrieve", "GET", f"api/workflows/{workflow_id}", 200)
                    self.created_resources.append(("workflow", workflow_id))

    def run_concurrent_test(self, name):
        """Helper method for concurrent testing"""
        return self.run_test(name, "GET", "api/integrations", 200)

    def test_8_error_handling_logging(self):
        """8. ERROR HANDLING & LOGGING"""
        print("\n" + "="*80)
        print("8. ERROR HANDLING & LOGGING")
        print("="*80)
        
        # Test 404 errors
        self.run_test("404 Error Handling", "GET", "api/nonexistent-endpoint", 404)
        
        # Test 401 errors (unauthorized)
        no_auth_headers = {}
        self.run_test("401 Error Handling", "GET", "api/workflows/", 401, headers=no_auth_headers)
        
        # Test 422 validation errors
        invalid_user_data = {
            "email": "invalid-email",
            "password": "123",  # Too short
            "first_name": "",   # Empty
            "last_name": ""     # Empty
        }
        self.run_test("422 Validation Error Handling", "POST", "api/auth/register", 422, invalid_user_data)
        
        # Test 500 errors (try to trigger server error)
        if self.token:
            # Try to create workflow with invalid data structure
            invalid_workflow = {
                "name": None,  # Invalid name
                "nodes": "invalid_nodes_format",  # Should be array
                "connections": {"invalid": "format"}  # Should be array
            }
            self.run_test("500 Error Handling", "POST", "api/workflows/", 500, invalid_workflow)

    def test_9_api_contract_compliance(self):
        """9. API CONTRACT COMPLIANCE"""
        print("\n" + "="*80)
        print("9. API CONTRACT COMPLIANCE")
        print("="*80)
        
        # Test response format consistency
        endpoints_to_test = [
            ("GET", "api/integrations", 200, None),
            ("GET", "api/node-types", 200, None),
            ("GET", "api/templates/", 200, None),
            ("GET", "api/dashboard/stats", 200, None)
        ]
        
        for method, endpoint, expected_status, data in endpoints_to_test:
            result = self.run_test(f"API Contract - {endpoint}", method, endpoint, expected_status, data)
            
            if result.get("success") and result.get("response_data"):
                response_data = result["response_data"]
                
                # Check if response is valid JSON
                if not isinstance(response_data, (dict, list)):
                    self.log_issue(
                        severity="Medium",
                        title=f"Invalid JSON Response Format - {endpoint}",
                        description=f"Response is not valid JSON: {type(response_data)}",
                        endpoint=endpoint,
                        reproduction_steps=[f"{method} {endpoint}", "Check response format"]
                    )
        
        # Test parameter validation
        if self.token:
            # Test workflow creation with missing required fields
            incomplete_workflow = {"name": "Test"}  # Missing required fields
            self.run_test("Parameter Validation - Missing Fields", "POST", "api/workflows/", 422, incomplete_workflow)

    def test_10_missing_functionality_gaps(self):
        """10. MISSING FUNCTIONALITY GAPS"""
        print("\n" + "="*80)
        print("10. MISSING FUNCTIONALITY GAPS")
        print("="*80)
        
        # Test for promised features that might be missing
        missing_features = []
        
        # Check for advanced analytics
        analytics_result = self.run_test("Advanced Analytics", "GET", "api/analytics/dashboard/overview", 200)
        if not analytics_result.get("success"):
            missing_features.append("Advanced Analytics Dashboard")
        
        # Check for collaboration features
        collab_result = self.run_test("Collaboration Features", "GET", "api/collaboration/stats", 200)
        if not collab_result.get("success"):
            missing_features.append("Real-time Collaboration")
        
        # Check for performance monitoring
        perf_result = self.run_test("Performance Monitoring", "GET", "api/performance/metrics", 200)
        if not perf_result.get("success"):
            missing_features.append("Performance Monitoring")
        
        # Check for integration usage analytics
        usage_result = self.run_test("Integration Usage Analytics", "GET", "api/analytics/integrations/usage", 200)
        if not usage_result.get("success"):
            missing_features.append("Integration Usage Analytics")
        
        if missing_features:
            self.log_issue(
                severity="Medium",
                title="Missing Promised Features",
                description=f"The following features appear to be missing or non-functional: {', '.join(missing_features)}",
                endpoint="multiple",
                reproduction_steps=[f"Test each feature endpoint" for feature in missing_features]
            )
        else:
            print("✅ All promised features appear to be implemented")

    def cleanup_resources(self):
        """Clean up created test resources"""
        print("\n🧹 Cleaning up test resources...")
        
        for resource_type, resource_id in self.created_resources:
            try:
                if resource_type == "workflow":
                    self.run_test(f"Cleanup Workflow {resource_id}", "DELETE", f"api/workflows/{resource_id}", 200)
                elif resource_type == "template":
                    self.run_test(f"Cleanup Template {resource_id}", "DELETE", f"api/templates/{resource_id}", 200)
            except Exception as e:
                print(f"⚠️ Could not cleanup {resource_type} {resource_id}: {e}")

    def generate_comprehensive_report(self):
        """Generate comprehensive bug report"""
        print("\n" + "="*100)
        print("COMPREHENSIVE BACKEND ANALYSIS & BUG IDENTIFICATION REPORT")
        print("="*100)
        
        total_issues = len(self.critical_issues) + len(self.high_issues) + len(self.medium_issues) + len(self.low_issues)
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        print(f"\n📊 OVERALL ASSESSMENT:")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Total Issues Found: {total_issues}")
        
        # Critical Issues
        if self.critical_issues:
            print(f"\n🚨 CRITICAL ISSUES ({len(self.critical_issues)}):")
            for i, issue in enumerate(self.critical_issues, 1):
                print(f"\n   {i}. {issue['title']}")
                print(f"      Endpoint: {issue.get('endpoint', 'N/A')}")
                print(f"      Description: {issue['description']}")
                if issue.get('reproduction_steps'):
                    print(f"      Reproduction Steps:")
                    for step in issue['reproduction_steps']:
                        print(f"        - {step}")
        
        # High Priority Issues
        if self.high_issues:
            print(f"\n⚠️ HIGH PRIORITY ISSUES ({len(self.high_issues)}):")
            for i, issue in enumerate(self.high_issues, 1):
                print(f"\n   {i}. {issue['title']}")
                print(f"      Endpoint: {issue.get('endpoint', 'N/A')}")
                print(f"      Description: {issue['description']}")
        
        # Medium Priority Issues
        if self.medium_issues:
            print(f"\n🔶 MEDIUM PRIORITY ISSUES ({len(self.medium_issues)}):")
            for i, issue in enumerate(self.medium_issues, 1):
                print(f"   {i}. {issue['title']} - {issue['description']}")
        
        # Low Priority Issues
        if self.low_issues:
            print(f"\n🔷 LOW PRIORITY ISSUES ({len(self.low_issues)}):")
            for i, issue in enumerate(self.low_issues, 1):
                print(f"   {i}. {issue['title']} - {issue['description']}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if self.critical_issues:
            print("   1. Address all CRITICAL issues immediately - these block core functionality")
        if self.high_issues:
            print("   2. Fix HIGH priority issues - these significantly impact user experience")
        if success_rate < 80:
            print("   3. Overall success rate is below 80% - comprehensive fixes needed")
        if success_rate >= 90:
            print("   1. Excellent success rate! Focus on remaining edge cases")
        
        print(f"\n🎯 PRIORITY FIX ORDER:")
        print("   1. Critical Issues (system-breaking)")
        print("   2. High Issues (user-impacting)")
        print("   3. Medium Issues (quality improvements)")
        print("   4. Low Issues (nice-to-have fixes)")
        
        return {
            "success_rate": success_rate,
            "total_tests": self.tests_run,
            "passed_tests": self.tests_passed,
            "critical_issues": len(self.critical_issues),
            "high_issues": len(self.high_issues),
            "medium_issues": len(self.medium_issues),
            "low_issues": len(self.low_issues),
            "total_issues": total_issues
        }

    def run_all_tests(self):
        """Run all comprehensive tests"""
        print("🚀 STARTING COMPREHENSIVE BACKEND ANALYSIS & BUG IDENTIFICATION")
        print(f"Session ID: {self.session_id}")
        print(f"Base URL: {self.base_url}")
        print(f"Test User: {self.test_user['email']}")
        
        try:
            # Run all test suites
            self.test_1_complete_system_health_check()
            self.test_2_authentication_security()
            self.test_3_automation_workflow_deep_testing()
            self.test_4_integration_system_validation()
            self.test_5_ai_system_comprehensive_testing()
            self.test_6_template_system_validation()
            self.test_7_database_performance()
            self.test_8_error_handling_logging()
            self.test_9_api_contract_compliance()
            self.test_10_missing_functionality_gaps()
            
        except KeyboardInterrupt:
            print("\n⚠️ Testing interrupted by user")
        except Exception as e:
            print(f"\n❌ Unexpected error during testing: {e}")
            self.log_issue(
                severity="Critical",
                title="Testing Framework Error",
                description=f"Unexpected error during testing: {str(e)}",
                endpoint="testing_framework",
                reproduction_steps=["Run comprehensive test suite", f"Error occurs: {str(e)}"]
            )
        finally:
            # Always cleanup and generate report
            self.cleanup_resources()
            return self.generate_comprehensive_report()

def main():
    """Main execution function"""
    tester = ComprehensiveBackendReviewTester()
    report = tester.run_all_tests()
    
    # Exit with appropriate code
    if report["critical_issues"] > 0:
        sys.exit(1)  # Critical issues found
    elif report["success_rate"] < 80:
        sys.exit(2)  # Low success rate
    else:
        sys.exit(0)  # Success

if __name__ == "__main__":
    main()