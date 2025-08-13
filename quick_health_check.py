#!/usr/bin/env python3
"""
Quick Health Check for Aether Automation Backend
Tests all critical endpoints mentioned in the review request
"""

import requests
import json
import uuid
from datetime import datetime

class QuickHealthChecker:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_passed = 0
        self.tests_run = 0
        
    def log(self, message, status="INFO"):
        print(f"[{status}] {message}")
        
    def test_endpoint(self, name, method, endpoint, expected_status=200, data=None, headers=None):
        """Test a single endpoint"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        if headers:
            test_headers.update(headers)
            
        self.tests_run += 1
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)
                
            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                self.log(f"✅ {name} - Status: {response.status_code}", "PASS")
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                self.log(f"❌ {name} - Expected {expected_status}, got {response.status_code}", "FAIL")
                try:
                    error_data = response.json()
                    self.log(f"   Error: {error_data.get('detail', 'Unknown error')}", "ERROR")
                except:
                    self.log(f"   Error: {response.text[:100]}", "ERROR")
                return False, {}
                
        except Exception as e:
            self.log(f"❌ {name} - Exception: {str(e)}", "FAIL")
            return False, {}
    
    def run_health_check(self):
        """Run comprehensive health check"""
        self.log("🎯 COMPREHENSIVE BACKEND HEALTH CHECK", "START")
        self.log("=" * 60)
        
        # 1. Authentication System
        self.log("\n🔐 1. AUTHENTICATION SYSTEM", "SECTION")
        self.log("-" * 30)
        
        # Test signup
        signup_data = {
            "name": f"Health Check User {datetime.now().strftime('%H%M%S')}",
            "email": f"health_{datetime.now().strftime('%H%M%S')}@example.com",
            "password": "securepassword123"
        }
        
        success, response = self.test_endpoint("User Signup", "POST", "api/auth/signup", 200, signup_data)
        if success and 'token' in response:
            self.token = response['token']
            self.user_id = response['user']['id']
            self.log(f"   Token obtained for user: {response['user']['name']}")
        
        # Test login with existing user
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        self.test_endpoint("User Login (fallback)", "POST", "api/auth/login", 200, login_data)
        
        # 2. Dashboard Stats API
        self.log("\n📊 2. DASHBOARD STATS API", "SECTION")
        self.log("-" * 30)
        
        success, response = self.test_endpoint("Dashboard Stats", "GET", "api/dashboard/stats", 200)
        if success:
            required_fields = ['total_workflows', 'total_executions', 'success_rate']
            if all(field in response for field in required_fields):
                self.log("   ✅ Dashboard stats structure valid")
            else:
                self.log("   ⚠️ Dashboard stats missing some fields")
        
        # 3. Workflow CRUD Operations
        self.log("\n⚙️ 3. WORKFLOW CRUD OPERATIONS", "SECTION")
        self.log("-" * 30)
        
        # Create workflow
        workflow_data = {
            "name": f"Health Check Workflow {datetime.now().strftime('%H%M%S')}",
            "description": "Test workflow for health check",
            "nodes": [
                {
                    "id": "node1",
                    "type": "trigger",
                    "name": "Test Trigger",
                    "config": {"test": True}
                }
            ],
            "connections": [],
            "triggers": []
        }
        
        workflow_id = None
        success, response = self.test_endpoint("Create Workflow", "POST", "api/workflows", 200, workflow_data)
        if success and 'workflow_id' in response:
            workflow_id = response['workflow_id']
            self.log(f"   Created workflow ID: {workflow_id}")
        
        # Get workflows
        self.test_endpoint("Get Workflows", "GET", "api/workflows", 200)
        
        # Execute workflow
        if workflow_id:
            success, response = self.test_endpoint("Execute Workflow", "POST", f"api/workflows/{workflow_id}/execute", 200)
            if success and 'execution_id' in response:
                self.log(f"   Execution ID: {response['execution_id']}")
        
        # 4. Integration Management (200+ integrations)
        self.log("\n🔗 4. INTEGRATION MANAGEMENT", "SECTION")
        self.log("-" * 30)
        
        # Get available integrations
        success, response = self.test_endpoint("Get Available Integrations", "GET", "api/integrations", 200)
        if success:
            if 'integrations' in response:
                total_integrations = response.get('total_count', 0)
                categories = response.get('categories', [])
                self.log(f"   Available integrations: {total_integrations}")
                self.log(f"   Categories: {len(categories)} ({', '.join(categories)})")
            
        # Create integration
        integration_data = {
            "name": f"Health Check Integration {datetime.now().strftime('%H%M%S')}",
            "platform": "slack",
            "credentials": {
                "api_key": "test_key_health_check",
                "webhook_url": "https://hooks.slack.com/test"
            }
        }
        
        success, response = self.test_endpoint("Create Integration", "POST", "api/integrations", 200, integration_data)
        if success and 'integration_id' in response:
            self.log(f"   Created integration ID: {response['integration_id']}")
        
        # Get user integrations
        self.test_endpoint("Get User Integrations", "GET", "api/integrations/user", 200)
        
        # 5. AI Endpoints (GROQ multi-agent system)
        self.log("\n🤖 5. AI ENDPOINTS (GROQ)", "SECTION")
        self.log("-" * 30)
        
        # Test AI chat
        ai_chat_data = {
            "message": "How do I create an automation workflow for email processing?"
        }
        
        success, response = self.test_endpoint("AI Chat", "POST", "api/ai/chat", 200, ai_chat_data)
        if success:
            if 'response' in response and 'model' in response:
                model = response.get('model', 'unknown')
                self.log(f"   AI model: {model}")
                if model.startswith('llama'):
                    self.log("   ✅ GROQ AI integration working")
                else:
                    self.log("   ⚠️ Using fallback AI response")
        
        # 6. Template System
        self.log("\n📋 6. TEMPLATE SYSTEM", "SECTION")
        self.log("-" * 30)
        
        success, response = self.test_endpoint("Get Templates", "GET", "api/templates", 200)
        if success and 'templates' in response:
            template_count = len(response['templates'])
            self.log(f"   Available templates: {template_count}")
        
        # 7. Enhanced Features
        self.log("\n🚀 7. ENHANCED FEATURES", "SECTION")
        self.log("-" * 30)
        
        # System status
        success, response = self.test_endpoint("Enhanced System Status", "GET", "api/enhanced/system-status", 200)
        if success:
            overall_status = response.get('overall_status', 'unknown')
            self.log(f"   System status: {overall_status}")
            
            components = response.get('system_components', {})
            for component, status in components.items():
                component_status = status.get('status', 'unknown')
                self.log(f"   {component}: {component_status}")
        
        # User checklist
        success, response = self.test_endpoint("User Checklist", "GET", "api/user/checklist", 200)
        if success and 'completion_percentage' in response:
            completion = response['completion_percentage']
            self.log(f"   Onboarding completion: {completion}%")
        
        # 8. Database Integration (MongoDB)
        self.log("\n🗄️ 8. DATABASE INTEGRATION", "SECTION")
        self.log("-" * 30)
        
        success, response = self.test_endpoint("Health Check", "GET", "api/health", 200)
        if success:
            db_status = response.get('database_status', 'unknown')
            version = response.get('version', 'unknown')
            self.log(f"   Database status: {db_status}")
            self.log(f"   API version: {version}")
        
        # 9. Node Types API
        self.log("\n🔧 9. NODE TYPES API", "SECTION")
        self.log("-" * 30)
        
        success, response = self.test_endpoint("Get Node Types", "GET", "api/nodes", 200)
        if success and isinstance(response, list):
            node_count = len(response)
            categories = set(node.get('category', 'unknown') for node in response)
            self.log(f"   Available nodes: {node_count}")
            self.log(f"   Node categories: {', '.join(categories)}")
        
        # 10. Performance & Error Handling
        self.log("\n⚡ 10. PERFORMANCE & ERROR HANDLING", "SECTION")
        self.log("-" * 30)
        
        # Test invalid endpoint
        self.test_endpoint("Invalid Endpoint", "GET", "api/invalid-endpoint", 404)
        
        # Test unauthorized access
        temp_token = self.token
        self.token = None
        self.test_endpoint("Unauthorized Access", "GET", "api/dashboard/stats", 403)
        self.token = temp_token
        
        # Final Results
        self.log("\n" + "=" * 60)
        self.log("📊 HEALTH CHECK RESULTS", "FINAL")
        self.log("=" * 60)
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        self.log(f"Tests passed: {self.tests_passed}/{self.tests_run}")
        self.log(f"Success rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            self.log("🎉 EXCELLENT - All critical systems operational!", "SUCCESS")
            status = "EXCELLENT"
        elif success_rate >= 80:
            self.log("✅ GOOD - Most systems working properly", "SUCCESS")
            status = "GOOD"
        elif success_rate >= 70:
            self.log("⚠️ FAIR - Some issues found but core functionality works", "WARNING")
            status = "FAIR"
        else:
            self.log("❌ POOR - Major issues found requiring attention", "ERROR")
            status = "POOR"
            
        return {
            "status": status,
            "success_rate": success_rate,
            "tests_passed": self.tests_passed,
            "tests_run": self.tests_run,
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    checker = QuickHealthChecker()
    results = checker.run_health_check()
    
    # Exit with appropriate code
    if results["success_rate"] >= 70:
        exit(0)
    else:
        exit(1)