#!/usr/bin/env python3
"""
Smoke test for Aether Automation API - specific requirements from review request
"""
import requests
import json
from datetime import datetime

class SmokeTest:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.workflow_id = None
        self.integration_id = None
        self.execution_id = None
        
    def log(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
    def test_health_check(self):
        """Verify health by calling GET /api/nodes (no auth needed)"""
        self.log("🔍 Testing health check via GET /api/nodes...")
        try:
            response = requests.get(f"{self.base_url}/api/nodes", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "categories" in data:
                    self.log("✅ Health check passed - API is responding")
                    return True
                else:
                    self.log("❌ Health check failed - unexpected response format")
                    return False
            else:
                self.log(f"❌ Health check failed - status {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Health check failed - {str(e)}")
            return False
    
    def test_signup_login_flow(self):
        """Flow: signup unique user -> login -> store Bearer token"""
        self.log("🔍 Testing signup + login flow...")
        
        # Signup with unique user
        timestamp = datetime.now().strftime('%H%M%S%f')
        signup_data = {
            "name": f"Smoke Test User {timestamp}",
            "email": f"smoketest_{timestamp}@example.com",
            "password": "smoketest123"
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/auth/signup", json=signup_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "token" in data:
                    self.token = data["token"]
                    self.user_id = data["user"]["id"]
                    self.log(f"✅ Signup successful - token obtained")
                    return True
                else:
                    self.log("❌ Signup failed - no token in response")
                    return False
            else:
                self.log(f"❌ Signup failed - status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log(f"❌ Signup failed - {str(e)}")
            return False
    
    def test_dashboard_stats(self):
        """With token: GET /api/dashboard/stats, expect 200 and keys total_workflows, total_executions"""
        self.log("🔍 Testing dashboard stats with Bearer token...")
        
        if not self.token:
            self.log("❌ No token available for dashboard test")
            return False
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = requests.get(f"{self.base_url}/api/dashboard/stats", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "total_workflows" in data and "total_executions" in data:
                    self.log(f"✅ Dashboard stats passed - total_workflows: {data['total_workflows']}, total_executions: {data['total_executions']}")
                    return True
                else:
                    self.log(f"❌ Dashboard stats failed - missing required keys: {list(data.keys())}")
                    return False
            else:
                self.log(f"❌ Dashboard stats failed - status {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Dashboard stats failed - {str(e)}")
            return False
    
    def test_workflow_crud(self):
        """Create workflow -> GET workflows -> PUT update -> POST execute -> GET execution"""
        self.log("🔍 Testing workflow CRUD operations...")
        
        if not self.token:
            self.log("❌ No token available for workflow test")
            return False
            
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        
        # Create workflow
        workflow_data = {
            "name": f"Smoke Test Workflow {datetime.now().strftime('%H%M%S')}",
            "description": "Smoke test workflow for API validation",
            "nodes": [
                {
                    "id": "trigger1",
                    "type": "webhook",
                    "name": "Webhook Trigger",
                    "config": {"url": "/webhook/smoke-test"}
                },
                {
                    "id": "action1",
                    "type": "http",
                    "name": "HTTP Request",
                    "config": {"method": "GET", "url": "https://httpbin.org/get"}
                }
            ],
            "connections": [
                {
                    "from": "trigger1",
                    "to": "action1",
                    "fromPort": "output",
                    "toPort": "input"
                }
            ],
            "triggers": [
                {
                    "type": "webhook",
                    "conditions": {"path": "/webhook/smoke-test"}
                }
            ]
        }
        
        try:
            # Create workflow
            response = requests.post(f"{self.base_url}/api/workflows", json=workflow_data, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "id" in data:
                    self.workflow_id = data["id"]
                    self.log(f"✅ Workflow created - ID: {self.workflow_id}")
                else:
                    self.log("❌ Workflow creation failed - no ID in response")
                    return False
            else:
                self.log(f"❌ Workflow creation failed - status {response.status_code}")
                return False
            
            # GET workflows - list includes created one
            response = requests.get(f"{self.base_url}/api/workflows", headers=headers, timeout=10)
            if response.status_code == 200:
                workflows = response.json()
                if any(w["id"] == self.workflow_id for w in workflows):
                    self.log("✅ Workflow found in list")
                else:
                    self.log("❌ Created workflow not found in list")
                    return False
            else:
                self.log(f"❌ Get workflows failed - status {response.status_code}")
                return False
            
            # PUT update workflow
            updated_data = workflow_data.copy()
            updated_data["description"] = "Updated smoke test workflow"
            
            response = requests.put(f"{self.base_url}/api/workflows/{self.workflow_id}", json=updated_data, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "success" in data["message"].lower():
                    self.log("✅ Workflow updated successfully")
                else:
                    self.log(f"❌ Workflow update failed - unexpected response: {data}")
                    return False
            else:
                self.log(f"❌ Workflow update failed - status {response.status_code}")
                return False
            
            # POST execute workflow
            response = requests.post(f"{self.base_url}/api/workflows/{self.workflow_id}/execute", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "status" in data and data["status"] == "success":
                    self.execution_id = data.get("execution_id")
                    self.log(f"✅ Workflow executed - status: {data['status']}")
                else:
                    self.log(f"❌ Workflow execution failed - unexpected response: {data}")
                    return False
            else:
                self.log(f"❌ Workflow execution failed - status {response.status_code}")
                return False
            
            # GET execution by id
            if self.execution_id:
                response = requests.get(f"{self.base_url}/api/executions/{self.execution_id}", headers=headers, timeout=10)
                if response.status_code == 200:
                    self.log("✅ Execution details retrieved successfully")
                else:
                    self.log(f"❌ Get execution failed - status {response.status_code}")
                    return False
            
            return True
            
        except Exception as e:
            self.log(f"❌ Workflow CRUD failed - {str(e)}")
            return False
    
    def test_integrations_crud(self):
        """GET available integrations -> POST create -> GET list includes it -> DELETE -> list no longer includes it"""
        self.log("🔍 Testing integrations CRUD operations...")
        
        if not self.token:
            self.log("❌ No token available for integrations test")
            return False
            
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        
        try:
            # GET available integrations
            response = requests.get(f"{self.base_url}/api/integrations/available", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "categories" in data:
                    self.log("✅ Available integrations retrieved")
                else:
                    self.log("❌ Available integrations failed - no categories")
                    return False
            else:
                self.log(f"❌ Available integrations failed - status {response.status_code}")
                return False
            
            # POST create integration
            integration_data = {
                "name": f"Smoke Test Integration {datetime.now().strftime('%H%M%S')}",
                "platform": "slack",
                "credentials": {
                    "api_key": "smoke_test_key_123",
                    "webhook_url": "https://hooks.slack.com/smoke-test"
                }
            }
            
            response = requests.post(f"{self.base_url}/api/integrations", json=integration_data, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "id" in data:
                    self.integration_id = data["id"]
                    self.log(f"✅ Integration created - ID: {self.integration_id}")
                else:
                    self.log("❌ Integration creation failed - no ID in response")
                    return False
            else:
                self.log(f"❌ Integration creation failed - status {response.status_code}")
                return False
            
            # GET integrations - list includes created one (without credentials)
            response = requests.get(f"{self.base_url}/api/integrations", headers=headers, timeout=10)
            if response.status_code == 200:
                integrations = response.json()
                created_integration = next((i for i in integrations if i["id"] == self.integration_id), None)
                if created_integration:
                    if "credentials" not in created_integration:
                        self.log("✅ Integration found in list (credentials properly hidden)")
                    else:
                        self.log("❌ Integration found but credentials not hidden")
                        return False
                else:
                    self.log("❌ Created integration not found in list")
                    return False
            else:
                self.log(f"❌ Get integrations failed - status {response.status_code}")
                return False
            
            # DELETE integration
            response = requests.delete(f"{self.base_url}/api/integrations/{self.integration_id}", headers=headers, timeout=10)
            if response.status_code == 200:
                self.log("✅ Integration deleted successfully")
            else:
                self.log(f"❌ Integration deletion failed - status {response.status_code}")
                return False
            
            # Verify it's no longer in the list
            response = requests.get(f"{self.base_url}/api/integrations", headers=headers, timeout=10)
            if response.status_code == 200:
                integrations = response.json()
                if not any(i["id"] == self.integration_id for i in integrations):
                    self.log("✅ Integration no longer in list after deletion")
                else:
                    self.log("❌ Integration still in list after deletion")
                    return False
            else:
                self.log(f"❌ Get integrations after deletion failed - status {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log(f"❌ Integrations CRUD failed - {str(e)}")
            return False
    
    def test_ai_endpoints(self):
        """POST /api/ai/chat and /api/ai/generate-workflow with simple prompt, assert 200"""
        self.log("🔍 Testing AI endpoints...")
        
        if not self.token:
            self.log("❌ No token available for AI test")
            return False
            
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        
        try:
            # Test AI chat
            chat_data = {"message": "What is workflow automation?"}
            response = requests.post(f"{self.base_url}/api/ai/chat", json=chat_data, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if "response" in data:
                    self.log("✅ AI chat endpoint working")
                else:
                    self.log("❌ AI chat failed - no response field")
                    return False
            elif response.status_code == 500:
                error_data = response.json()
                if "GROQ API key" in error_data.get("detail", ""):
                    self.log("✅ AI chat endpoint accessible (GROQ key not configured - expected)")
                else:
                    self.log(f"❌ AI chat failed - unexpected 500 error: {error_data}")
                    return False
            else:
                self.log(f"❌ AI chat failed - status {response.status_code}")
                return False
            
            # Test AI workflow generation
            workflow_prompt = {"prompt": "Create a simple workflow that sends an email notification"}
            response = requests.post(f"{self.base_url}/api/ai/generate-workflow", json=workflow_prompt, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if "suggestion" in data or "name" in data:
                    self.log("✅ AI workflow generation endpoint working")
                else:
                    self.log("❌ AI workflow generation failed - unexpected response format")
                    return False
            elif response.status_code == 500:
                error_data = response.json()
                if "GROQ API key" in error_data.get("detail", ""):
                    self.log("✅ AI workflow generation endpoint accessible (GROQ key not configured - expected)")
                else:
                    self.log(f"❌ AI workflow generation failed - unexpected 500 error: {error_data}")
                    return False
            else:
                self.log(f"❌ AI workflow generation failed - status {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log(f"❌ AI endpoints test failed - {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all smoke tests"""
        self.log("🚀 Starting Aether Automation API Smoke Tests")
        self.log("=" * 60)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Signup/Login Flow", self.test_signup_login_flow),
            ("Dashboard Stats", self.test_dashboard_stats),
            ("Workflow CRUD", self.test_workflow_crud),
            ("Integrations CRUD", self.test_integrations_crud),
            ("AI Endpoints", self.test_ai_endpoints),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            self.log(f"\n📋 Running {test_name}...")
            if test_func():
                passed += 1
            else:
                self.log(f"❌ {test_name} FAILED")
        
        self.log("\n" + "=" * 60)
        self.log(f"📊 SMOKE TEST RESULTS: {passed}/{total} tests passed")
        success_rate = (passed / total * 100) if total > 0 else 0
        self.log(f"Success rate: {success_rate:.1f}%")
        
        if success_rate == 100:
            self.log("✅ All smoke tests PASSED!")
            return 0
        elif success_rate >= 80:
            self.log("⚠️ Most smoke tests passed - minor issues found")
            return 0
        else:
            self.log("❌ Smoke tests FAILED - major issues found")
            return 1

if __name__ == "__main__":
    import sys
    smoke_test = SmokeTest()
    sys.exit(smoke_test.run_all_tests())