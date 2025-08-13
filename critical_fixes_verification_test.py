#!/usr/bin/env python3
"""
Critical Fixes Verification Test for Aether Automation Platform
Target: 100% Success Rate (31/31 tests passed)

This test specifically verifies the critical fixes implemented:
1. Execution Status Endpoints (both routes)
2. AI Integration Suggestions (flexible parameter formats)
3. Integration Search Enhanced (expanded parameter support)
4. AI Chat Endpoint (validation fixes)
5. Node Types Count (should return 35 nodes)
6. Template System (API contract flexibility)
7. Authentication System (JWT token fixes)
"""

import requests
import sys
import json
import time
import uuid
from datetime import datetime

class CriticalFixesVerificationTester:
    def __init__(self, base_url="https://integration-verify-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_workflow_id = None
        self.created_execution_id = None
        self.session_id = str(uuid.uuid4())
        self.test_results = []

    def log_result(self, test_name, success, details=""):
        """Log test result for summary"""
        self.test_results.append({
            "name": test_name,
            "success": success,
            "details": details
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, params=None, description=""):
        """Run a single API test with detailed logging"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Test {self.tests_run}: {name}")
        if description:
            print(f"   📝 {description}")
        print(f"   🌐 URL: {url}")
        print(f"   📡 Method: {method}")
        if data:
            print(f"   📦 Data: {json.dumps(data, indent=2)}")
        if params:
            print(f"   🔗 Params: {params}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, params=params, timeout=15)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, params=params, timeout=15)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, params=params, timeout=15)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, params=params, timeout=15)

            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"✅ PASSED - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   📄 Response: {json.dumps(response_data, indent=2)[:200]}...")
                    self.log_result(name, True, f"Status: {response.status_code}")
                    return response_data
                except:
                    print(f"   📄 Response: {response.text[:200]}...")
                    self.log_result(name, True, f"Status: {response.status_code}")
                    return response.text
            else:
                print(f"❌ FAILED - Expected: {expected_status}, Got: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   ⚠️  Error: {json.dumps(error_data, indent=2)}")
                    self.log_result(name, False, f"Expected {expected_status}, got {response.status_code}: {error_data}")
                except:
                    print(f"   ⚠️  Error: {response.text}")
                    self.log_result(name, False, f"Expected {expected_status}, got {response.status_code}: {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ FAILED - Network Error: {e}")
            self.log_result(name, False, f"Network error: {str(e)}")
            return None
        except Exception as e:
            print(f"❌ FAILED - Unexpected Error: {e}")
            self.log_result(name, False, f"Unexpected error: {str(e)}")
            return None

    def setup_authentication(self):
        """Setup authentication for protected endpoints"""
        print("\n🔐 AUTHENTICATION SETUP")
        print("=" * 50)
        
        # Test user data
        test_email = f"criticaltest_{self.session_id[:8]}@example.com"
        test_password = "CriticalTest123!"
        
        # Register user
        register_data = {
            "email": test_email,
            "password": test_password,
            "first_name": "Critical",
            "last_name": "Tester"
        }
        
        response = self.run_test(
            "User Registration", 
            "POST", 
            "api/auth/register", 
            200, 
            register_data,
            description="Register new user for testing"
        )
        
        if response and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response.get('user_id')
            print(f"🎯 Authentication successful - User ID: {self.user_id}")
            return True
        else:
            print("❌ Authentication failed - cannot proceed with protected endpoint tests")
            return False

    def test_execution_status_endpoints(self):
        """Test both execution status endpoint variants"""
        print("\n🚀 EXECUTION STATUS ENDPOINTS TESTING")
        print("=" * 50)
        
        # First create a workflow to get an execution
        workflow_data = {
            "name": "Critical Test Workflow",
            "description": "Test workflow for execution status testing",
            "workflow_definition": {
                "nodes": [
                    {
                        "id": "start",
                        "type": "trigger",
                        "name": "Manual Trigger",
                        "config": {}
                    }
                ],
                "connections": []
            }
        }
        
        workflow_response = self.run_test(
            "Create Test Workflow",
            "POST",
            "api/workflows/",
            200,
            workflow_data,
            description="Create workflow for execution testing"
        )
        
        if workflow_response and 'id' in workflow_response:
            self.created_workflow_id = workflow_response['id']
            
            # Execute the workflow
            execution_response = self.run_test(
                "Execute Workflow",
                "POST",
                f"api/workflows/{self.created_workflow_id}/execute",
                200,
                {},
                description="Execute workflow to create execution record"
            )
            
            if execution_response and 'execution_id' in execution_response:
                self.created_execution_id = execution_response['execution_id']
                
                # Test original execution status endpoint
                self.run_test(
                    "Execution Status - Original Route",
                    "GET",
                    f"api/workflows/executions/{self.created_execution_id}/status",
                    200,
                    description="Test original execution status endpoint"
                )
                
                # Test alternative execution status endpoint
                self.run_test(
                    "Execution Status - Alternative Route",
                    "GET",
                    f"api/executions/{self.created_execution_id}/status",
                    200,
                    description="Test new alternative execution status endpoint"
                )
            else:
                print("⚠️ Could not create execution - testing with dummy ID")
                dummy_execution_id = str(uuid.uuid4())
                
                # Test with dummy ID (should return 404)
                self.run_test(
                    "Execution Status - Original Route (404 test)",
                    "GET",
                    f"api/workflows/executions/{dummy_execution_id}/status",
                    404,
                    description="Test original execution status endpoint with non-existent ID"
                )
                
                self.run_test(
                    "Execution Status - Alternative Route (404 test)",
                    "GET",
                    f"api/executions/{dummy_execution_id}/status",
                    404,
                    description="Test alternative execution status endpoint with non-existent ID"
                )

    def test_ai_integration_suggestions(self):
        """Test AI integration suggestions with flexible parameter formats"""
        print("\n🤖 AI INTEGRATION SUGGESTIONS TESTING")
        print("=" * 50)
        
        # Test 1: JSON body with 'description' field
        self.run_test(
            "AI Suggestions - JSON body with 'description'",
            "POST",
            "api/ai/suggest-integrations",
            200,
            {"description": "I need to send emails when new customers sign up"},
            description="Test JSON body format with 'description' field"
        )
        
        # Test 2: JSON body with 'workflow_description' field
        self.run_test(
            "AI Suggestions - JSON body with 'workflow_description'",
            "POST",
            "api/ai/suggest-integrations",
            200,
            {"workflow_description": "Automate social media posting when blog is published"},
            description="Test JSON body format with 'workflow_description' field"
        )
        
        # Test 3: JSON body with 'prompt' field
        self.run_test(
            "AI Suggestions - JSON body with 'prompt'",
            "POST",
            "api/ai/suggest-integrations",
            200,
            {"prompt": "Create workflow for customer onboarding process"},
            description="Test JSON body format with 'prompt' field"
        )
        
        # Test 4: JSON body with 'query' field
        self.run_test(
            "AI Suggestions - JSON body with 'query'",
            "POST",
            "api/ai/suggest-integrations",
            200,
            {"query": "Help me automate invoice processing"},
            description="Test JSON body format with 'query' field"
        )
        
        # Test 5: Query parameter format with 'description'
        self.run_test(
            "AI Suggestions - Query param 'description'",
            "GET",
            "api/ai/suggest-integrations",
            200,
            params={"description": "Sync data between CRM and email marketing"},
            description="Test query parameter format with 'description'"
        )
        
        # Test 6: Query parameter format with 'query'
        self.run_test(
            "AI Suggestions - Query param 'query'",
            "GET",
            "api/ai/suggest-integrations",
            200,
            params={"query": "Automate backup processes"},
            description="Test query parameter format with 'query'"
        )

    def test_integration_search_enhanced(self):
        """Test enhanced integration search with expanded parameter support"""
        print("\n🔍 INTEGRATION SEARCH ENHANCED TESTING")
        print("=" * 50)
        
        # Test 1: 'query' parameter (existing)
        self.run_test(
            "Integration Search - 'query' parameter",
            "GET",
            "api/integrations/search",
            200,
            params={"query": "slack"},
            description="Test existing 'query' parameter"
        )
        
        # Test 2: 'q' parameter (existing)
        self.run_test(
            "Integration Search - 'q' parameter",
            "GET",
            "api/integrations/search",
            200,
            params={"q": "google"},
            description="Test existing 'q' parameter"
        )
        
        # Test 3: 'search' parameter (new)
        self.run_test(
            "Integration Search - 'search' parameter",
            "GET",
            "api/integrations/search",
            200,
            params={"search": "github"},
            description="Test new 'search' parameter"
        )
        
        # Test 4: 'term' parameter (new)
        self.run_test(
            "Integration Search - 'term' parameter",
            "GET",
            "api/integrations/search",
            200,
            params={"term": "stripe"},
            description="Test new 'term' parameter"
        )
        
        # Test 5: Category-only search (new)
        self.run_test(
            "Integration Search - Category only",
            "GET",
            "api/integrations/search",
            200,
            params={"category": "communication"},
            description="Test category-only search functionality"
        )
        
        # Test 6: Enhanced search with tags
        self.run_test(
            "Integration Search - Enhanced with tags",
            "GET",
            "api/integrations/search",
            200,
            params={"q": "ai", "category": "ai"},
            description="Test enhanced search including tags and categories"
        )

    def test_ai_chat_endpoint(self):
        """Test AI chat endpoint validation fixes"""
        print("\n💬 AI CHAT ENDPOINT TESTING")
        print("=" * 50)
        
        # Test 1: JSON body format with 'message' field
        self.run_test(
            "AI Chat - JSON body with 'message'",
            "POST",
            "api/ai/chat",
            200,
            {"message": "How do I create a workflow?"},
            description="Test JSON body format with 'message' field"
        )
        
        # Test 2: Query parameter format
        self.run_test(
            "AI Chat - Query parameter format",
            "GET",
            "api/ai/chat",
            200,
            params={"message": "What integrations are available?"},
            description="Test query parameter format"
        )
        
        # Test 3: Error handling - empty message
        self.run_test(
            "AI Chat - Empty message validation",
            "POST",
            "api/ai/chat",
            422,
            {"message": ""},
            description="Test validation with empty message"
        )

    def test_node_types_count(self):
        """Test node types count - should return 35 nodes"""
        print("\n🔧 NODE TYPES COUNT TESTING")
        print("=" * 50)
        
        # Test node types endpoint
        response = self.run_test(
            "Node Types - Count Verification",
            "GET",
            "api/node-types",
            200,
            description="Verify node types returns 35 total nodes across 4 categories"
        )
        
        if response:
            # Count total nodes
            total_nodes = 0
            categories = response.get('categories', {})
            
            for category_name, category_data in categories.items():
                if isinstance(category_data, dict) and 'nodes' in category_data:
                    total_nodes += len(category_data['nodes'])
            
            print(f"   📊 Total nodes found: {total_nodes}")
            print(f"   📊 Categories found: {len(categories)}")
            
            if total_nodes >= 35:
                print(f"✅ Node count verification PASSED - Found {total_nodes} nodes (≥35)")
                self.log_result("Node Types Count Verification", True, f"Found {total_nodes} nodes")
            else:
                print(f"❌ Node count verification FAILED - Found {total_nodes} nodes (<35)")
                self.log_result("Node Types Count Verification", False, f"Found only {total_nodes} nodes, expected ≥35")
        
        # Test nodes alias endpoint
        self.run_test(
            "Nodes Alias - Endpoint Test",
            "GET",
            "api/nodes",
            200,
            description="Test /api/nodes alias endpoint"
        )
        
        # Test nodes search functionality
        self.run_test(
            "Nodes Search - Functionality Test",
            "GET",
            "api/nodes/search",
            200,
            params={"q": "trigger"},
            description="Test nodes search functionality"
        )

    def test_template_system(self):
        """Test template system API contract flexibility"""
        print("\n📋 TEMPLATE SYSTEM TESTING")
        print("=" * 50)
        
        # Test 1: Template creation with 'nodes' format
        template_data_nodes = {
            "name": "Critical Test Template - Nodes Format",
            "description": "Test template with nodes format",
            "category": "automation",
            "nodes": [
                {
                    "id": "start",
                    "type": "trigger",
                    "name": "Manual Trigger"
                }
            ]
        }
        
        response1 = self.run_test(
            "Template Creation - 'nodes' format",
            "POST",
            "api/templates/create",
            200,
            template_data_nodes,
            description="Test template creation with 'nodes' format"
        )
        
        # Test 2: Template creation with 'workflow_definition' format
        template_data_workflow = {
            "name": "Critical Test Template - Workflow Format",
            "description": "Test template with workflow_definition format",
            "category": "automation",
            "workflow_definition": {
                "nodes": [
                    {
                        "id": "start",
                        "type": "trigger",
                        "name": "Manual Trigger"
                    }
                ],
                "connections": []
            }
        }
        
        response2 = self.run_test(
            "Template Creation - 'workflow_definition' format",
            "POST",
            "api/templates/create",
            200,
            template_data_workflow,
            description="Test template creation with 'workflow_definition' format"
        )
        
        # Test 3: Template listing
        self.run_test(
            "Template Listing",
            "GET",
            "api/templates/",
            200,
            description="Test template listing functionality"
        )
        
        # Test 4: Template detail retrieval (if we created one successfully)
        if response1 and 'id' in response1:
            template_id = response1['id']
            self.run_test(
                "Template Detail Retrieval",
                "GET",
                f"api/templates/{template_id}",
                200,
                description="Test template detail retrieval"
            )

    def test_authentication_system(self):
        """Test authentication system JWT token fixes"""
        print("\n🔐 AUTHENTICATION SYSTEM TESTING")
        print("=" * 50)
        
        # Test 1: Login endpoint
        login_data = {
            "email": f"criticaltest_{self.session_id[:8]}@example.com",
            "password": "CriticalTest123!"
        }
        
        self.run_test(
            "Authentication - Login",
            "POST",
            "api/auth/login",
            200,
            login_data,
            description="Test login endpoint with JWT token generation"
        )
        
        # Test 2: Token validation via /me endpoint
        self.run_test(
            "Authentication - Token Validation",
            "GET",
            "api/auth/me",
            200,
            description="Test JWT token validation via /me endpoint"
        )
        
        # Test 3: Signup endpoint (alternative registration)
        signup_data = {
            "email": f"criticaltest_signup_{self.session_id[:8]}@example.com",
            "password": "CriticalTest123!",
            "first_name": "Critical",
            "last_name": "Signup"
        }
        
        self.run_test(
            "Authentication - Signup Alternative",
            "POST",
            "api/auth/signup",
            200,
            signup_data,
            description="Test signup endpoint as alternative to register"
        )

    def run_comprehensive_test(self):
        """Run all critical fixes verification tests"""
        print("🎯 CRITICAL FIXES VERIFICATION TEST")
        print("=" * 60)
        print("Target: 100% Success Rate (31/31 tests passed)")
        print("=" * 60)
        
        start_time = time.time()
        
        # Setup authentication
        if not self.setup_authentication():
            print("❌ Cannot proceed without authentication")
            return
        
        # Run all test suites
        self.test_execution_status_endpoints()
        self.test_ai_integration_suggestions()
        self.test_integration_search_enhanced()
        self.test_ai_chat_endpoint()
        self.test_node_types_count()
        self.test_template_system()
        self.test_authentication_system()
        
        # Calculate results
        end_time = time.time()
        duration = end_time - start_time
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        
        # Print comprehensive summary
        print("\n" + "=" * 60)
        print("🎯 CRITICAL FIXES VERIFICATION RESULTS")
        print("=" * 60)
        print(f"📊 Tests Run: {self.tests_run}")
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        
        # Target achievement check
        if success_rate >= 100.0:
            print(f"🎉 TARGET ACHIEVED! 100% success rate reached!")
        elif success_rate >= 90.0:
            print(f"🎯 EXCELLENT! {success_rate:.1f}% success rate - very close to target")
        elif success_rate >= 75.0:
            print(f"✅ GOOD! {success_rate:.1f}% success rate - significant improvement")
        else:
            print(f"⚠️  NEEDS WORK! {success_rate:.1f}% success rate - more fixes needed")
        
        # Detailed results by category
        print("\n📋 DETAILED RESULTS BY TEST:")
        print("-" * 60)
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status} {result['name']}")
            if result["details"] and not result["success"]:
                print(f"     💡 {result['details']}")
        
        print("\n" + "=" * 60)
        
        return success_rate >= 100.0

if __name__ == "__main__":
    tester = CriticalFixesVerificationTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("🎉 ALL CRITICAL FIXES VERIFIED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("⚠️  SOME CRITICAL FIXES NEED ATTENTION")
        sys.exit(1)