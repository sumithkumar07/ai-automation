#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND VERIFICATION TEST - 100% SUCCESS TARGET
Focuses on the specific issues identified in the review request:
1. Template creation returning 500 error
2. Integration search parameter format issues  
3. Execution status endpoint 404 error
4. Node types response format issues
5. AI integration suggestions returning 422 validation errors
"""

import requests
import sys
import json
import time
import uuid
from datetime import datetime
import concurrent.futures

class ComprehensiveBackendVerificationTester:
    def __init__(self, base_url="https://complete-qa-suite.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.critical_issues = []
        self.minor_issues = []
        self.created_workflow_id = None
        self.created_template_id = None
        self.session_id = str(uuid.uuid4())

    def log_result(self, test_name, success, status_code, response_data=None, error_msg=None):
        """Log test results with detailed information"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name} - Status: {status_code}")
        else:
            self.failed_tests.append({
                'test': test_name,
                'status_code': status_code,
                'error': error_msg,
                'response': response_data
            })
            print(f"❌ {test_name} - Status: {status_code}")
            if error_msg:
                print(f"   Error: {error_msg}")

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, params=None):
        """Run a single API test with detailed logging"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        print(f"   Method: {method}")
        if params:
            print(f"   Params: {params}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)[:200]}...")
        
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
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}

            if success:
                self.log_result(name, True, response.status_code, response_data)
                return True, response_data
            else:
                error_msg = f"Expected {expected_status}, got {response.status_code}"
                self.log_result(name, False, response.status_code, response_data, error_msg)
                return False, response_data

        except Exception as e:
            error_msg = str(e)
            self.log_result(name, False, 0, None, error_msg)
            return False, {}

    def authenticate(self):
        """Authenticate and get JWT token"""
        print("\n🔐 AUTHENTICATION PHASE")
        
        # Try to create a new user for testing
        test_user_data = {
            "email": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com",
            "password": "TestPass123!",
            "first_name": "Test",
            "last_name": f"User{datetime.now().strftime('%H%M%S')}"
        }
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "api/auth/register",
            200,
            data=test_user_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user']['id']
            print(f"   ✅ Authentication successful - Token: {self.token[:20]}...")
            return True
        
        # Fallback to login with existing user
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        success, response = self.run_test(
            "User Login (Fallback)",
            "POST",
            "api/auth/login",
            200,
            data=login_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user']['id']
            print(f"   ✅ Login successful - Token: {self.token[:20]}...")
            return True
            
        print("   ❌ Authentication failed")
        return False

    def test_template_system_issues(self):
        """Test template system - Focus on 500 errors"""
        print("\n🎯 TESTING TEMPLATE SYSTEM ISSUES")
        
        # Test 1: Template listing
        success, response = self.run_test(
            "Template Listing",
            "GET",
            "api/templates/",
            200
        )
        
        if not success:
            self.critical_issues.append("Template listing endpoint failing")
        
        # Test 2: Template creation (known to cause 500 error)
        template_data = {
            "name": f"Test Template {datetime.now().strftime('%H%M%S')}",
            "description": "Automated test template for verification",
            "category": "automation",
            "nodes": [
                {
                    "id": "trigger1",
                    "type": "webhook_trigger",
                    "name": "Webhook Trigger",
                    "config": {"method": "POST", "path": "/webhook"}
                },
                {
                    "id": "action1",
                    "type": "email_action",
                    "name": "Send Email",
                    "config": {"to": "test@example.com", "subject": "Test"}
                }
            ],
            "connections": [
                {"from": "trigger1", "to": "action1"}
            ]
        }
        
        success, response = self.run_test(
            "Template Creation (Known Issue)",
            "POST",
            "api/templates/create",
            200,
            data=template_data
        )
        
        if success and 'id' in response:
            self.created_template_id = response['id']
            print(f"   ✅ Template created with ID: {self.created_template_id}")
        elif not success:
            self.critical_issues.append("Template creation returning 500 error - ObjectId serialization issue")
        
        # Test 3: Template detail retrieval (if template was created)
        if self.created_template_id:
            success, response = self.run_test(
                "Template Detail Retrieval",
                "GET",
                f"api/templates/{self.created_template_id}",
                200
            )
            
            if not success:
                self.critical_issues.append("Template detail retrieval failing after creation")
        
        # Test 4: Template search
        success, response = self.run_test(
            "Template Search",
            "GET",
            "api/templates/search",
            200,
            params={"query": "automation", "category": "automation"}
        )
        
        if not success:
            self.critical_issues.append("Template search functionality failing")

    def test_integration_search_issues(self):
        """Test integration search parameter format issues"""
        print("\n🎯 TESTING INTEGRATION SEARCH PARAMETER ISSUES")
        
        # Test 1: Basic integration listing
        success, response = self.run_test(
            "Integration Listing",
            "GET",
            "api/integrations",
            200
        )
        
        if success:
            integration_count = len(response.get('integrations', []))
            print(f"   📊 Found {integration_count} integrations")
            
            if integration_count < 100:
                self.minor_issues.append(f"Integration count ({integration_count}) below homepage promise of 100+")
        
        # Test 2: Integration search with different parameter formats
        search_tests = [
            {"query": "slack", "description": "Simple text search"},
            {"q": "slack", "description": "Alternative query parameter"},
            {"search": "slack", "description": "Search parameter variant"},
            {"term": "slack", "description": "Term parameter variant"},
            {"query": "slack", "category": "communication", "description": "Query with category"},
            {"query": "ai", "limit": 10, "description": "Query with limit"},
            {"category": "ai", "description": "Category only search"}
        ]
        
        for test_params in search_tests:
            description = test_params.pop("description")
            success, response = self.run_test(
                f"Integration Search - {description}",
                "GET",
                "api/integrations/search",
                200,
                params=test_params
            )
            
            if not success:
                self.critical_issues.append(f"Integration search failing with parameters: {test_params}")
        
        # Test 3: Integration categories
        success, response = self.run_test(
            "Integration Categories",
            "GET",
            "api/integrations/categories",
            200
        )
        
        if not success:
            self.critical_issues.append("Integration categories endpoint failing")

    def test_execution_status_endpoint(self):
        """Test execution status endpoint 404 error"""
        print("\n🎯 TESTING EXECUTION STATUS ENDPOINT ISSUES")
        
        # First create a workflow to test execution
        workflow_data = {
            "name": f"Test Execution Workflow {datetime.now().strftime('%H%M%S')}",
            "description": "Workflow for testing execution status",
            "nodes": [
                {
                    "id": "trigger1",
                    "type": "manual_trigger",
                    "name": "Manual Trigger",
                    "config": {}
                },
                {
                    "id": "action1",
                    "type": "delay_action",
                    "name": "Delay Action",
                    "config": {"delay_seconds": 1}
                }
            ],
            "connections": [
                {"from": "trigger1", "to": "action1"}
            ]
        }
        
        success, response = self.run_test(
            "Create Workflow for Execution Testing",
            "POST",
            "api/workflows/",
            200,
            data=workflow_data
        )
        
        if success and 'id' in response:
            workflow_id = response['id']
            self.created_workflow_id = workflow_id
            
            # Execute the workflow
            success, exec_response = self.run_test(
                "Execute Workflow",
                "POST",
                f"api/workflows/{workflow_id}/execute",
                200,
                data={"input_data": {"test": "execution"}}
            )
            
            if success and 'execution_id' in exec_response:
                execution_id = exec_response['execution_id']
                
                # Test different execution status endpoint formats
                status_endpoints = [
                    f"api/workflows/{workflow_id}/executions/{execution_id}/status",
                    f"api/executions/{execution_id}/status",
                    f"api/workflow-executions/{execution_id}/status",
                    f"api/workflows/{workflow_id}/execution-status/{execution_id}",
                    f"api/execution-status/{execution_id}"
                ]
                
                for endpoint in status_endpoints:
                    success, response = self.run_test(
                        f"Execution Status - {endpoint.split('/')[-2:]}",
                        "GET",
                        endpoint,
                        200
                    )
                    
                    if success:
                        print(f"   ✅ Working execution status endpoint: {endpoint}")
                        break
                else:
                    self.critical_issues.append("All execution status endpoint variants returning 404")
            else:
                self.critical_issues.append("Workflow execution failed - cannot test status endpoints")
        else:
            self.critical_issues.append("Cannot create workflow for execution testing")

    def test_node_types_response_format(self):
        """Test node types response format issues"""
        print("\n🎯 TESTING NODE TYPES RESPONSE FORMAT ISSUES")
        
        success, response = self.run_test(
            "Node Types Endpoint",
            "GET",
            "api/node-types",
            200
        )
        
        if success:
            # Validate response format
            if isinstance(response, dict):
                if 'node_types' in response or 'nodes' in response or 'categories' in response:
                    node_count = 0
                    if 'node_types' in response:
                        node_count = len(response['node_types'])
                    elif 'nodes' in response:
                        node_count = len(response['nodes'])
                    elif 'categories' in response:
                        # Count nodes in categories
                        for category in response['categories']:
                            if 'nodes' in category:
                                node_count += len(category['nodes'])
                    
                    print(f"   📊 Found {node_count} node types")
                    
                    if node_count < 20:
                        self.minor_issues.append(f"Node types count ({node_count}) seems low for comprehensive platform")
                else:
                    self.critical_issues.append("Node types response missing expected structure (node_types/nodes/categories)")
            elif isinstance(response, list):
                print(f"   📊 Found {len(response)} node types (list format)")
                if len(response) < 20:
                    self.minor_issues.append(f"Node types count ({len(response)}) seems low for comprehensive platform")
            else:
                self.critical_issues.append("Node types response format unexpected - not dict or list")
        else:
            self.critical_issues.append("Node types endpoint failing")

    def test_ai_integration_suggestions(self):
        """Test AI integration suggestions 422 validation errors"""
        print("\n🎯 TESTING AI INTEGRATION SUGGESTIONS VALIDATION ISSUES")
        
        # Test different AI suggestion request formats
        ai_suggestion_tests = [
            {
                "data": {"description": "I want to automate email notifications when new customers sign up"},
                "description": "Basic workflow description"
            },
            {
                "data": {"workflow_description": "Send Slack messages for new GitHub issues"},
                "description": "Alternative field name"
            },
            {
                "data": {"prompt": "Create automation for social media posting"},
                "description": "Prompt field"
            },
            {
                "data": {"query": "Automate invoice processing"},
                "description": "Query field"
            },
            {
                "data": {
                    "description": "Email automation workflow",
                    "industry": "ecommerce",
                    "use_case": "customer_onboarding"
                },
                "description": "Detailed request with context"
            }
        ]
        
        for test_case in ai_suggestion_tests:
            success, response = self.run_test(
                f"AI Integration Suggestions - {test_case['description']}",
                "POST",
                "api/ai/suggest-integrations",
                200,
                data=test_case["data"]
            )
            
            if not success:
                # Check if it's a 422 validation error
                if hasattr(response, 'get') and response.get('status_code') == 422:
                    self.critical_issues.append(f"AI integration suggestions returning 422 validation error for: {test_case['description']}")
                else:
                    self.critical_issues.append(f"AI integration suggestions failing for: {test_case['description']}")
        
        # Test other AI endpoints for comparison
        ai_endpoints = [
            ("api/ai/generate-workflow", "POST", {"description": "Test workflow generation"}),
            ("api/ai/dashboard-insights", "GET", None),
            ("api/ai/system-status", "GET", None),
            ("api/ai/chat", "POST", {"message": "Hello, can you help me create a workflow?"})
        ]
        
        for endpoint, method, data in ai_endpoints:
            success, response = self.run_test(
                f"AI Endpoint - {endpoint.split('/')[-1]}",
                method,
                endpoint,
                200,
                data=data
            )
            
            if not success:
                self.minor_issues.append(f"AI endpoint {endpoint} not working properly")

    def test_performance_and_real_data(self):
        """Test performance and verify real vs demo data"""
        print("\n🎯 TESTING PERFORMANCE AND REAL DATA VERIFICATION")
        
        # Performance test - concurrent requests
        def make_request(endpoint):
            try:
                url = f"{self.base_url}/{endpoint}"
                headers = {'Authorization': f'Bearer {self.token}'} if self.token else {}
                response = requests.get(url, headers=headers, timeout=10)
                return response.status_code == 200
            except:
                return False
        
        endpoints = [
            "api/dashboard/stats",
            "api/integrations",
            "api/node-types",
            "api/workflows",
            "api/ai/system-status"
        ]
        
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, endpoint) for endpoint in endpoints]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        performance_time = end_time - start_time
        success_rate = sum(results) / len(results) * 100
        
        print(f"   📊 Performance Test: {len(endpoints)} concurrent requests")
        print(f"   ⏱️  Total time: {performance_time:.2f} seconds")
        print(f"   ✅ Success rate: {success_rate:.1f}%")
        
        if performance_time > 10:
            self.minor_issues.append(f"Performance concern: {performance_time:.2f}s for {len(endpoints)} requests")
        
        # Real data verification
        success, dashboard_data = self.run_test(
            "Dashboard Real Data Check",
            "GET",
            "api/dashboard/stats",
            200
        )
        
        if success:
            # Check for demo/fake data patterns
            demo_patterns = ["demo", "fake", "test", "sample", "placeholder"]
            real_data_score = 0
            total_checks = 0
            
            for key, value in dashboard_data.items():
                total_checks += 1
                if isinstance(value, str):
                    if not any(pattern in value.lower() for pattern in demo_patterns):
                        real_data_score += 1
                elif isinstance(value, (int, float)):
                    if value > 0:  # Non-zero values suggest real data
                        real_data_score += 1
            
            if total_checks > 0:
                real_data_percentage = (real_data_score / total_checks) * 100
                print(f"   📊 Real data assessment: {real_data_percentage:.1f}% appears real")
                
                if real_data_percentage < 70:
                    self.minor_issues.append(f"Potential demo data detected in dashboard ({real_data_percentage:.1f}% real)")

    def run_comprehensive_verification(self):
        """Run all verification tests"""
        print("🚀 STARTING COMPREHENSIVE BACKEND VERIFICATION TEST")
        print("=" * 80)
        print("Target: 100% Success Rate - Focus on Known Issues")
        print("=" * 80)
        
        # Authentication
        if not self.authenticate():
            print("❌ Cannot proceed without authentication")
            return False
        
        # Run all test categories
        self.test_template_system_issues()
        self.test_integration_search_issues()
        self.test_execution_status_endpoint()
        self.test_node_types_response_format()
        self.test_ai_integration_suggestions()
        self.test_performance_and_real_data()
        
        # Generate comprehensive report
        self.generate_final_report()
        
        return True

    def generate_final_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE BACKEND VERIFICATION REPORT")
        print("=" * 80)
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        if self.critical_issues:
            print(f"\n🚨 CRITICAL ISSUES FOUND ({len(self.critical_issues)}):")
            for i, issue in enumerate(self.critical_issues, 1):
                print(f"   {i}. {issue}")
        
        if self.minor_issues:
            print(f"\n⚠️  MINOR ISSUES FOUND ({len(self.minor_issues)}):")
            for i, issue in enumerate(self.minor_issues, 1):
                print(f"   {i}. {issue}")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS DETAILS:")
            for test in self.failed_tests:
                print(f"   • {test['test']}: Status {test['status_code']} - {test['error']}")
        
        print(f"\n🎯 RECOMMENDATIONS FOR 100% SUCCESS:")
        if self.critical_issues:
            print("   1. Address critical issues first (blocking core functionality)")
        if self.minor_issues:
            print("   2. Review minor issues for production readiness")
        if success_rate < 100:
            print("   3. Investigate and fix remaining failing endpoints")
        
        if success_rate >= 90:
            print("✅ SYSTEM IS PRODUCTION-READY with minor fixes needed")
        elif success_rate >= 70:
            print("⚠️  SYSTEM NEEDS ATTENTION before production deployment")
        else:
            print("❌ SYSTEM REQUIRES SIGNIFICANT FIXES before production")

if __name__ == "__main__":
    tester = ComprehensiveBackendVerificationTester()
    tester.run_comprehensive_verification()