#!/usr/bin/env python3
"""
Final Comprehensive Aether Automation Backend API Test Suite
Tests all backend functionality as requested in the review.
"""

import requests
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

class AetherBackendTester:
    def __init__(self, base_url: str = "https://pricing-flow-test.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.test_results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": []
        }
        self.created_workflow_id = None
        self.test_user_email = f"test_{datetime.now().strftime('%H%M%S')}@example.com"
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        self.test_results["total_tests"] += 1
        if success:
            self.test_results["passed_tests"] += 1
            status = "✅ PASS"
        else:
            self.test_results["failed_tests"] += 1
            status = "❌ FAIL"
            
        self.test_results["test_details"].append({
            "test": test_name,
            "status": status,
            "details": details,
            "response": response_data
        })
        
        print(f"{status} - {test_name}")
        if details:
            print(f"    {details}")
        if not success and response_data:
            print(f"    Response: {json.dumps(response_data, indent=2)[:200]}...")
        print()

    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None, 
                    expected_status: int = 200, auth_required: bool = True) -> tuple[bool, Dict]:
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}/api/{endpoint.lstrip('/')}"
        headers = {'Content-Type': 'application/json'}
        
        if auth_required and self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, params=params, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, params=params, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, params=params, timeout=10)
            else:
                return False, {"error": f"Unsupported method: {method}"}
            
            success = response.status_code == expected_status
            try:
                response_data = response.json()
            except:
                response_data = {"text": response.text, "status_code": response.status_code}
                
            return success, response_data
            
        except Exception as e:
            return False, {"error": str(e)}

    def test_basic_health_check(self):
        """Test 1: Basic Health Check - GET /api/"""
        print("🔍 Testing Basic Health Check...")
        success, response = self.make_request('GET', '/', auth_required=False)
        
        if success and response.get("message") == "Hello World":
            self.log_test("Basic Health Check", True, "Server responding correctly")
        else:
            self.log_test("Basic Health Check", False, "Server not responding as expected", response)

    def test_user_registration(self):
        """Test 2: User Registration - POST /api/auth/register"""
        print("🔍 Testing User Registration...")
        user_data = {
            "email": self.test_user_email,
            "password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User",
            "company": "Test Company"
        }
        
        success, response = self.make_request('POST', 'auth/register', data=user_data, auth_required=False)
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user']['id']
            self.log_test("User Registration", True, f"User registered successfully, token obtained")
        else:
            self.log_test("User Registration", False, "Registration failed", response)

    def test_user_login(self):
        """Test 3: User Login - POST /api/auth/login"""
        print("🔍 Testing User Login...")
        login_data = {
            "email": self.test_user_email,
            "password": "TestPassword123!"
        }
        
        success, response = self.make_request('POST', 'auth/login', data=login_data, auth_required=False)
        
        if success and 'access_token' in response:
            # Update token in case it's different
            self.token = response['access_token']
            self.log_test("User Login", True, "Login successful")
        else:
            self.log_test("User Login", False, "Login failed", response)

    def test_get_current_user(self):
        """Test 4: Get Current User - GET /api/auth/me"""
        print("🔍 Testing Get Current User...")
        success, response = self.make_request('GET', 'auth/me')
        
        if success and 'email' in response:
            self.log_test("Get Current User", True, f"User info retrieved: {response.get('email')}")
        else:
            self.log_test("Get Current User", False, "Failed to get user info", response)

    def test_update_current_user(self):
        """Test 5: Update Current User - PUT /api/auth/me"""
        print("🔍 Testing Update Current User...")
        update_data = {
            "first_name": "Updated",
            "last_name": "TestUser",
            "company": "Updated Company"
        }
        
        success, response = self.make_request('PUT', 'auth/me', data=update_data)
        
        if success:
            self.log_test("Update Current User", True, "User updated successfully")
        else:
            self.log_test("Update Current User", False, "Failed to update user", response)

    def test_create_workflow(self):
        """Test 6: Create Workflow - POST /api/workflows/"""
        print("🔍 Testing Create Workflow...")
        workflow_data = {
            "name": f"Test Workflow {datetime.now().strftime('%H%M%S')}",
            "description": "A comprehensive test workflow"
        }
        
        success, response = self.make_request('POST', 'workflows/', data=workflow_data)
        
        if success and 'id' in response:
            self.created_workflow_id = response['id']
            self.log_test("Create Workflow", True, f"Workflow created with ID: {self.created_workflow_id}")
        else:
            self.log_test("Create Workflow", False, "Failed to create workflow", response)

    def test_get_workflows(self):
        """Test 7: Get Workflows - GET /api/workflows/"""
        print("🔍 Testing Get Workflows...")
        success, response = self.make_request('GET', 'workflows/')
        
        if success and isinstance(response, list):
            self.log_test("Get Workflows", True, f"Retrieved {len(response)} workflows")
        else:
            self.log_test("Get Workflows", False, "Failed to get workflows", response)

    def test_get_node_types(self):
        """Test 8: Get Node Types - GET /api/workflows/node-types"""
        print("🔍 Testing Get Node Types...")
        success, response = self.make_request('GET', 'workflows/node-types', auth_required=False)
        
        if success and ('categories' in response or 'nodes' in response or isinstance(response, list)):
            self.log_test("Get Node Types", True, "Node types retrieved successfully")
        else:
            self.log_test("Get Node Types", False, "Failed to get node types", response)

    def test_get_specific_workflow(self):
        """Test 9: Get Specific Workflow - GET /api/workflows/{id}"""
        print("🔍 Testing Get Specific Workflow...")
        if not self.created_workflow_id:
            self.log_test("Get Specific Workflow", False, "No workflow ID available")
            return
            
        success, response = self.make_request('GET', f'workflows/{self.created_workflow_id}')
        
        if success and response.get('id') == self.created_workflow_id:
            self.log_test("Get Specific Workflow", True, "Workflow retrieved successfully")
        else:
            self.log_test("Get Specific Workflow", False, "Failed to get specific workflow", response)

    def test_update_workflow(self):
        """Test 10: Update Workflow - PUT /api/workflows/{id}"""
        print("🔍 Testing Update Workflow...")
        if not self.created_workflow_id:
            self.log_test("Update Workflow", False, "No workflow ID available")
            return
            
        update_data = {
            "name": f"Updated Test Workflow {datetime.now().strftime('%H%M%S')}",
            "description": "Updated description"
        }
        
        success, response = self.make_request('PUT', f'workflows/{self.created_workflow_id}', data=update_data)
        
        if success:
            self.log_test("Update Workflow", True, "Workflow updated successfully")
        else:
            self.log_test("Update Workflow", False, "Failed to update workflow", response)

    def test_workflow_autosave(self):
        """Test 11: Workflow Autosave - POST /api/workflows/{id}/autosave"""
        print("🔍 Testing Workflow Autosave...")
        if not self.created_workflow_id:
            self.log_test("Workflow Autosave", False, "No workflow ID available")
            return
            
        autosave_data = {
            "nodes": [
                {
                    "id": "node1",
                    "type": "trigger",
                    "name": "Test Trigger",
                    "config": {"test": "data"}
                }
            ],
            "connections": []
        }
        
        success, response = self.make_request('POST', f'workflows/{self.created_workflow_id}/autosave', data=autosave_data)
        
        if success:
            self.log_test("Workflow Autosave", True, "Autosave successful")
        else:
            self.log_test("Workflow Autosave", False, "Autosave failed", response)

    def test_execute_workflow(self):
        """Test 12: Execute Workflow - POST /api/workflows/{id}/execute"""
        print("🔍 Testing Execute Workflow...")
        if not self.created_workflow_id:
            self.log_test("Execute Workflow", False, "No workflow ID available")
            return
            
        success, response = self.make_request('POST', f'workflows/{self.created_workflow_id}/execute')
        
        if success and 'execution_id' in response:
            self.log_test("Execute Workflow", True, f"Workflow executed, execution ID: {response['execution_id']}")
        else:
            self.log_test("Execute Workflow", False, "Failed to execute workflow", response)

    def test_duplicate_workflow(self):
        """Test 13: Duplicate Workflow - POST /api/workflows/{id}/duplicate"""
        print("🔍 Testing Duplicate Workflow...")
        if not self.created_workflow_id:
            self.log_test("Duplicate Workflow", False, "No workflow ID available")
            return
            
        success, response = self.make_request('POST', f'workflows/{self.created_workflow_id}/duplicate')
        
        if success and 'id' in response:
            self.log_test("Duplicate Workflow", True, f"Workflow duplicated, new ID: {response['id']}")
        else:
            self.log_test("Duplicate Workflow", False, "Failed to duplicate workflow", response)

    def test_dashboard_stats(self):
        """Test 14: Dashboard Stats - GET /api/dashboard/stats"""
        print("🔍 Testing Dashboard Stats...")
        success, response = self.make_request('GET', 'dashboard/stats')
        
        expected_fields = ['total_workflows', 'active_workflows', 'total_executions']
        if success and all(field in response for field in expected_fields):
            self.log_test("Dashboard Stats", True, f"Stats retrieved successfully")
        else:
            self.log_test("Dashboard Stats", False, "Failed to get dashboard stats", response)

    def test_dashboard_checklist(self):
        """Test 15: Dashboard Checklist - GET /api/dashboard/checklist"""
        print("🔍 Testing Dashboard Checklist...")
        success, response = self.make_request('GET', 'dashboard/checklist')
        
        expected_fields = ['has_any_workflow', 'has_any_integration', 'completion_percentage']
        if success and all(field in response for field in expected_fields):
            self.log_test("Dashboard Checklist", True, f"Checklist retrieved: {response['completion_percentage']}% complete")
        else:
            self.log_test("Dashboard Checklist", False, "Failed to get checklist", response)

    def test_dashboard_activity(self):
        """Test 16: Dashboard Activity - GET /api/dashboard/activity"""
        print("🔍 Testing Dashboard Activity...")
        success, response = self.make_request('GET', 'dashboard/activity')
        
        if success and isinstance(response, list):
            self.log_test("Dashboard Activity", True, f"Activity feed retrieved: {len(response)} items")
        else:
            self.log_test("Dashboard Activity", False, "Failed to get activity feed", response)

    def test_execution_trends(self):
        """Test 17: Execution Trends - GET /api/dashboard/analytics/execution-trends"""
        print("🔍 Testing Execution Trends...")
        success, response = self.make_request('GET', 'dashboard/analytics/execution-trends')
        
        if success and isinstance(response, list):
            self.log_test("Execution Trends", True, f"Trends retrieved: {len(response)} data points")
        else:
            self.log_test("Execution Trends", False, "Failed to get execution trends", response)

    def test_workflow_performance(self):
        """Test 18: Workflow Performance - GET /api/dashboard/analytics/workflow-performance"""
        print("🔍 Testing Workflow Performance...")
        success, response = self.make_request('GET', 'dashboard/analytics/workflow-performance')
        
        if success and isinstance(response, list):
            self.log_test("Workflow Performance", True, f"Performance data retrieved: {len(response)} workflows")
        else:
            self.log_test("Workflow Performance", False, "Failed to get workflow performance", response)

    def test_integration_usage(self):
        """Test 19: Integration Usage - GET /api/dashboard/analytics/integration-usage"""
        print("🔍 Testing Integration Usage...")
        success, response = self.make_request('GET', 'dashboard/analytics/integration-usage')
        
        if success and isinstance(response, list):
            self.log_test("Integration Usage", True, f"Integration usage retrieved: {len(response)} integrations")
        else:
            self.log_test("Integration Usage", False, "Failed to get integration usage", response)

    def test_get_integrations(self):
        """Test 20: Get All Integrations - GET /api/integrations/"""
        print("🔍 Testing Get All Integrations...")
        success, response = self.make_request('GET', 'integrations/', auth_required=False)
        
        if success and isinstance(response, list):
            self.log_test("Get All Integrations", True, f"Retrieved {len(response)} integrations")
        else:
            self.log_test("Get All Integrations", False, "Failed to get integrations", response)

    def test_integration_categories(self):
        """Test 21: Get Integration Categories - GET /api/integrations/categories"""
        print("🔍 Testing Integration Categories...")
        success, response = self.make_request('GET', 'integrations/categories', auth_required=False)
        
        if success and isinstance(response, list):
            self.log_test("Integration Categories", True, f"Retrieved {len(response)} categories")
        else:
            self.log_test("Integration Categories", False, "Failed to get categories", response)

    def test_search_integrations(self):
        """Test 22: Search Integrations - GET /api/integrations/search"""
        print("🔍 Testing Search Integrations...")
        params = {"q": "slack"}
        success, response = self.make_request('GET', 'integrations/search', params=params, auth_required=False)
        
        if success and isinstance(response, list):
            self.log_test("Search Integrations", True, f"Search returned {len(response)} results")
        else:
            self.log_test("Search Integrations", False, "Failed to search integrations", response)

    def test_ai_generate_workflow(self):
        """Test 23: AI Generate Workflow - POST /api/ai/generate-workflow"""
        print("🔍 Testing AI Generate Workflow...")
        ai_request = {
            "description": "Create a workflow that sends a Slack notification when a new email arrives"
        }
        
        success, response = self.make_request('POST', 'ai/generate-workflow', data=ai_request)
        
        if success and 'workflow' in response:
            self.log_test("AI Generate Workflow", True, f"AI workflow generated with confidence: {response.get('confidence', 'N/A')}")
        else:
            self.log_test("AI Generate Workflow", False, "Failed to generate AI workflow", response)

    def test_ai_suggest_integrations(self):
        """Test 24: AI Suggest Integrations - POST /api/ai/suggest-integrations"""
        print("🔍 Testing AI Suggest Integrations...")
        params = {"description": "I want to send notifications when someone submits a form"}
        success, response = self.make_request('POST', 'ai/suggest-integrations', params=params)
        
        if success and 'suggestions' in response:
            self.log_test("AI Suggest Integrations", True, f"AI suggested {len(response['suggestions'])} integrations")
        else:
            self.log_test("AI Suggest Integrations", False, "Failed to get AI suggestions", response)

    def test_ai_chat(self):
        """Test 25: AI Chat - POST /api/ai/chat"""
        print("🔍 Testing AI Chat...")
        params = {"message": "How do I create a workflow that processes CSV files?"}
        success, response = self.make_request('POST', 'ai/chat', params=params)
        
        if success and 'response' in response:
            self.log_test("AI Chat", True, "AI chat response received")
        else:
            self.log_test("AI Chat", False, "Failed to get AI chat response", response)

    def test_database_connectivity(self):
        """Test 26: Database Connectivity (via workflow creation/retrieval)"""
        print("🔍 Testing Database Connectivity...")
        # Test by creating and retrieving a workflow
        workflow_data = {
            "name": f"DB Test Workflow {datetime.now().strftime('%H%M%S')}",
            "description": "Testing database connectivity"
        }
        
        # Create workflow
        success1, response1 = self.make_request('POST', 'workflows/', data=workflow_data)
        if not success1:
            self.log_test("Database Connectivity", False, "Failed to create workflow for DB test", response1)
            return
            
        workflow_id = response1.get('id')
        
        # Retrieve workflow
        success2, response2 = self.make_request('GET', f'workflows/{workflow_id}')
        
        if success2 and response2.get('id') == workflow_id:
            self.log_test("Database Connectivity", True, "Database CRUD operations working")
        else:
            self.log_test("Database Connectivity", False, "Database retrieval failed", response2)

    def test_error_handling(self):
        """Test 27: Error Handling"""
        print("🔍 Testing Error Handling...")
        
        # Test 404 error
        success, response = self.make_request('GET', 'workflows/nonexistent-id', expected_status=404)
        
        if success:
            self.log_test("Error Handling (404)", True, "404 error handled correctly")
        else:
            self.log_test("Error Handling (404)", False, "404 error not handled properly", response)

    def test_delete_workflow(self):
        """Test 28: Delete Workflow - DELETE /api/workflows/{id}"""
        print("🔍 Testing Delete Workflow...")
        if not self.created_workflow_id:
            self.log_test("Delete Workflow", False, "No workflow ID available")
            return
            
        success, response = self.make_request('DELETE', f'workflows/{self.created_workflow_id}')
        
        if success:
            self.log_test("Delete Workflow", True, "Workflow deleted successfully")
        else:
            self.log_test("Delete Workflow", False, "Failed to delete workflow", response)

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Comprehensive Aether Automation Backend API Tests")
        print("=" * 80)
        
        # Basic Health
        self.test_basic_health_check()
        
        # Authentication System
        print("\n📝 AUTHENTICATION SYSTEM TESTS")
        print("-" * 40)
        self.test_user_registration()
        self.test_user_login()
        self.test_get_current_user()
        self.test_update_current_user()
        
        # Workflow Management
        print("\n⚙️ WORKFLOW MANAGEMENT TESTS")
        print("-" * 40)
        self.test_create_workflow()
        self.test_get_workflows()
        self.test_get_node_types()
        self.test_get_specific_workflow()
        self.test_update_workflow()
        self.test_workflow_autosave()
        self.test_execute_workflow()
        self.test_duplicate_workflow()
        
        # Dashboard Analytics
        print("\n📊 DASHBOARD ANALYTICS TESTS")
        print("-" * 40)
        self.test_dashboard_stats()
        self.test_dashboard_checklist()
        self.test_dashboard_activity()
        self.test_execution_trends()
        self.test_workflow_performance()
        self.test_integration_usage()
        
        # Integration System
        print("\n🔗 INTEGRATION SYSTEM TESTS")
        print("-" * 40)
        self.test_get_integrations()
        self.test_integration_categories()
        self.test_search_integrations()
        
        # AI Features
        print("\n🤖 AI FEATURES TESTS")
        print("-" * 40)
        self.test_ai_generate_workflow()
        self.test_ai_suggest_integrations()
        self.test_ai_chat()
        
        # Database and System
        print("\n💾 DATABASE & SYSTEM TESTS")
        print("-" * 40)
        self.test_database_connectivity()
        self.test_error_handling()
        
        # Cleanup
        print("\n🗑️ CLEANUP TESTS")
        print("-" * 40)
        self.test_delete_workflow()
        
        # Final Results
        self.print_final_results()

    def print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE BACKEND TEST RESULTS")
        print("=" * 80)
        
        total = self.test_results["total_tests"]
        passed = self.test_results["passed_tests"]
        failed = self.test_results["failed_tests"]
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\n🎯 SUMMARY:")
        print("-" * 40)
        
        if success_rate >= 90:
            print("✅ EXCELLENT: Backend is fully functional!")
        elif success_rate >= 80:
            print("✅ GOOD: Backend is mostly functional with minor issues")
        elif success_rate >= 70:
            print("⚠️ FAIR: Backend has some functionality but needs attention")
        elif success_rate >= 50:
            print("⚠️ POOR: Backend has significant issues")
        else:
            print("❌ CRITICAL: Backend has major problems")
        
        # Show failed tests
        failed_tests = [test for test in self.test_results["test_details"] if "❌" in test["status"]]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            print("-" * 40)
            for test in failed_tests:
                print(f"• {test['test']}: {test['details']}")

if __name__ == "__main__":
    tester = AetherBackendTester()
    tester.run_all_tests()