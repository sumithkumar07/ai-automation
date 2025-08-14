#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Aether Automation Platform
Focus Areas: Template Detail Async Issue, AI Integrations Endpoint, Integration Count, Real vs Demo Data
"""

import requests
import sys
import json
import time
import uuid
from datetime import datetime

class AetherPriorityTester:
    def __init__(self, base_url="https://sub-plan-info.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_issues = []
        self.minor_issues = []
        self.created_template_id = None
        self.session_id = str(uuid.uuid4())

    def log_issue(self, severity, test_name, issue):
        """Log issues for reporting"""
        if severity == "critical":
            self.critical_issues.append(f"{test_name}: {issue}")
        else:
            self.minor_issues.append(f"{test_name}: {issue}")

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, params=None):
        """Run a single API test with detailed logging"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        print(f"   Method: {method}")
        
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
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return response_data
                except:
                    print(f"   Response: {response.text[:200]}...")
                    return response.text
            else:
                print(f"❌ FAILED - Expected: {expected_status}, Got: {response.status_code}")
                print(f"   Response: {response.text[:300]}...")
                
                # Determine if this is critical or minor
                if response.status_code >= 500:
                    self.log_issue("critical", name, f"Server error {response.status_code}: {response.text[:100]}")
                elif response.status_code == 404 and "ai" in endpoint.lower():
                    self.log_issue("critical", name, f"AI endpoint not found: {response.text[:100]}")
                else:
                    self.log_issue("minor", name, f"Status {response.status_code}: {response.text[:100]}")
                
                return None

        except requests.exceptions.Timeout:
            print(f"❌ TIMEOUT - Request timed out after 15 seconds")
            self.log_issue("critical", name, "Request timeout")
            return None
        except Exception as e:
            print(f"❌ ERROR - {str(e)}")
            self.log_issue("critical", name, f"Request error: {str(e)}")
            return None

    def authenticate(self):
        """Authenticate and get JWT token"""
        print("\n🔐 AUTHENTICATION TESTING")
        
        # Test user registration/login
        test_user = {
            "email": f"priority_test_{self.session_id[:8]}@aether.com",
            "password": "SecurePass123!",
            "first_name": "Priority",
            "last_name": "Tester"
        }
        
        # Try registration first
        register_response = self.run_test(
            "User Registration", 
            "POST", 
            "auth/register", 
            200, 
            test_user
        )
        
        if register_response and 'access_token' in register_response:
            self.token = register_response['access_token']
            self.user_id = register_response.get('user_id')
            print(f"✅ Authentication successful - Token: {self.token[:20]}...")
            return True
        
        # If registration fails, try login
        login_response = self.run_test(
            "User Login", 
            "POST", 
            "auth/login", 
            200, 
            {"email": test_user["email"], "password": test_user["password"]}
        )
        
        if login_response and 'access_token' in login_response:
            self.token = login_response['access_token']
            self.user_id = login_response.get('user_id')
            print(f"✅ Login successful - Token: {self.token[:20]}...")
            return True
            
        print("❌ Authentication failed")
        return False

    def test_template_system_priority(self):
        """Test template system focusing on the async issue"""
        print("\n📋 PRIORITY 1: TEMPLATE SYSTEM TESTING")
        
        # Test template listing
        templates_response = self.run_test(
            "Template Listing", 
            "GET", 
            "templates/", 
            200
        )
        
        if not templates_response:
            return
            
        # Test template creation
        template_data = {
            "name": f"Priority Test Template {self.session_id[:8]}",
            "description": "Template created for priority testing",
            "category": "automation",
            "nodes": [
                {
                    "id": "node1",
                    "type": "trigger",
                    "name": "Email Trigger",
                    "config": {"email_filter": "priority@test.com"}
                },
                {
                    "id": "node2", 
                    "type": "action",
                    "name": "Send Notification",
                    "config": {"message": "Priority test notification"}
                }
            ],
            "connections": [{"from": "node1", "to": "node2"}],
            "tags": ["priority", "test", "automation"]
        }
        
        create_response = self.run_test(
            "Template Creation",
            "POST",
            "templates/create",
            200,
            template_data
        )
        
        if create_response and 'id' in create_response:
            self.created_template_id = create_response['id']
            print(f"✅ Template created with ID: {self.created_template_id}")
            
            # Test template detail retrieval (the async issue)
            detail_response = self.run_test(
                "Template Detail Retrieval (Async Issue Test)",
                "GET",
                f"templates/{self.created_template_id}",
                200
            )
            
            if detail_response:
                print("✅ Template detail retrieval working - Async issue appears resolved")
            else:
                print("❌ Template detail retrieval failed - Async issue persists")
        
        # Test template search
        search_response = self.run_test(
            "Template Search",
            "GET",
            "templates/search",
            200,
            params={"query": "automation", "category": "automation"}
        )

    def test_ai_integrations_endpoint(self):
        """Test AI integrations endpoint that was returning 404"""
        print("\n🤖 PRIORITY 2: AI INTEGRATIONS ENDPOINT TESTING")
        
        # Test various AI-related endpoints
        ai_endpoints = [
            ("ai/integrations", "AI Integrations List"),
            ("ai/integrations/suggestions", "AI Integration Suggestions"),
            ("ai/workflow/generate", "AI Workflow Generation"),
            ("ai/chat", "AI Chat Endpoint"),
            ("integrations?category=ai", "AI Category Integrations")
        ]
        
        for endpoint, name in ai_endpoints:
            if "generate" in endpoint:
                # POST request for workflow generation
                test_data = {
                    "description": "Create a workflow that sends email notifications when new GitHub issues are created",
                    "integrations": ["github", "gmail"]
                }
                self.run_test(name, "POST", endpoint, 200, test_data)
            elif "chat" in endpoint:
                # POST request for chat
                test_data = {
                    "message": "How can I create an automation workflow?",
                    "context": "workflow_creation"
                }
                self.run_test(name, "POST", endpoint, 200, test_data)
            else:
                # GET request
                self.run_test(name, "GET", endpoint, 200)

    def test_integration_count_verification(self):
        """Verify integration count vs homepage promises"""
        print("\n🔗 PRIORITY 3: INTEGRATION COUNT VERIFICATION")
        
        # Get all integrations
        integrations_response = self.run_test(
            "All Integrations Count",
            "GET",
            "integrations",
            200
        )
        
        if integrations_response:
            total_count = len(integrations_response)
            print(f"📊 Total Integrations Found: {total_count}")
            
            if total_count >= 100:
                print("✅ Integration count meets homepage promise (100+)")
            elif total_count >= 62:
                print(f"⚠️ Integration count ({total_count}) approaching promise but not yet 100+")
            else:
                print(f"❌ Integration count ({total_count}) significantly below homepage promise of 100+")
                self.log_issue("critical", "Integration Count", f"Only {total_count} integrations vs 100+ promised")
        
        # Test integration categories
        categories_response = self.run_test(
            "Integration Categories",
            "GET",
            "integrations/categories",
            200
        )
        
        if categories_response:
            category_count = len(categories_response)
            print(f"📊 Integration Categories: {category_count}")
            
            # Test each category
            for category in categories_response[:5]:  # Test first 5 categories
                category_name = category.get('name', category.get('id', 'unknown'))
                self.run_test(
                    f"Category '{category_name}' Integrations",
                    "GET",
                    f"integrations?category={category_name}",
                    200
                )

    def test_real_vs_demo_data(self):
        """Test to verify real data vs demo/mock data"""
        print("\n🎯 PRIORITY 4: REAL VS DEMO DATA VERIFICATION")
        
        # Test dashboard analytics for real data patterns
        dashboard_response = self.run_test(
            "Dashboard Analytics (Real Data Check)",
            "GET",
            "dashboard/stats",
            200
        )
        
        if dashboard_response:
            # Check for realistic data patterns
            stats = dashboard_response
            workflows = stats.get('total_workflows', 0)
            executions = stats.get('total_executions', 0)
            
            print(f"📊 Workflow Stats - Workflows: {workflows}, Executions: {executions}")
            
            # Real data should have reasonable ratios
            if workflows > 0 and executions > workflows * 2:
                print("✅ Data patterns suggest real usage (executions > workflows * 2)")
            else:
                print("⚠️ Data patterns suggest demo/initial data")
        
        # Test workflow execution engine with real processing
        if self.token:
            workflow_data = {
                "name": f"Real Data Test Workflow {self.session_id[:8]}",
                "description": "Testing real workflow execution",
                "nodes": [
                    {
                        "id": "trigger1",
                        "type": "manual_trigger",
                        "name": "Manual Start",
                        "config": {}
                    },
                    {
                        "id": "action1",
                        "type": "data_processor",
                        "name": "Process Data",
                        "config": {"operation": "transform", "data": "test_data"}
                    }
                ],
                "connections": [{"from": "trigger1", "to": "action1"}]
            }
            
            create_workflow_response = self.run_test(
                "Real Workflow Creation",
                "POST",
                "workflows",
                200,
                workflow_data
            )
            
            if create_workflow_response and 'id' in create_workflow_response:
                workflow_id = create_workflow_response['id']
                
                # Test workflow execution
                execute_response = self.run_test(
                    "Real Workflow Execution",
                    "POST",
                    f"workflows/{workflow_id}/execute",
                    200,
                    {"input_data": {"test": "real_execution_data"}}
                )
                
                if execute_response:
                    print("✅ Workflow execution engine processing real data")

    def test_comprehensive_api_coverage(self):
        """Test comprehensive API coverage for all major features"""
        print("\n🚀 COMPREHENSIVE API TESTING")
        
        # Test node types engine
        self.run_test("Node Types Engine", "GET", "node-types", 200)
        
        # Test collaboration features
        self.run_test("Collaboration Stats", "GET", "collaboration/stats", 200)
        
        # Test analytics
        self.run_test("Analytics Dashboard", "GET", "analytics/dashboard/overview", 200)
        self.run_test("Analytics Integrations", "GET", "analytics/integrations/usage", 200)
        
        # Test performance monitoring
        self.run_test("Performance Metrics", "GET", "performance/metrics", 200)
        
        # Test integration testing capabilities
        if self.token:
            # Get first integration for testing
            integrations = self.run_test("Get Integrations for Testing", "GET", "integrations", 200)
            if integrations and len(integrations) > 0:
                integration_id = integrations[0].get('id')
                if integration_id:
                    self.run_test(
                        "Integration Connection Test",
                        "POST",
                        f"integration-testing/test-connection/{integration_id}",
                        200
                    )

    def run_all_tests(self):
        """Run all priority tests"""
        print("🎯 AETHER AUTOMATION - COMPREHENSIVE PRIORITY TESTING")
        print("=" * 60)
        print(f"Backend URL: {self.api_url}")
        print(f"Session ID: {self.session_id}")
        print("=" * 60)
        
        start_time = time.time()
        
        # Authentication is required for most tests
        if not self.authenticate():
            print("❌ Cannot proceed without authentication")
            return
        
        # Run priority tests
        self.test_template_system_priority()
        self.test_ai_integrations_endpoint()
        self.test_integration_count_verification()
        self.test_real_vs_demo_data()
        self.test_comprehensive_api_coverage()
        
        # Final report
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("🎯 COMPREHENSIVE PRIORITY TEST RESULTS")
        print("=" * 60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        print(f"Duration: {duration:.2f} seconds")
        
        if self.critical_issues:
            print(f"\n❌ CRITICAL ISSUES ({len(self.critical_issues)}):")
            for issue in self.critical_issues:
                print(f"   • {issue}")
        
        if self.minor_issues:
            print(f"\n⚠️ MINOR ISSUES ({len(self.minor_issues)}):")
            for issue in self.minor_issues:
                print(f"   • {issue}")
        
        if not self.critical_issues and not self.minor_issues:
            print("\n✅ NO ISSUES FOUND - ALL SYSTEMS OPERATIONAL")
        
        print("=" * 60)
        
        return {
            "tests_run": self.tests_run,
            "tests_passed": self.tests_passed,
            "success_rate": (self.tests_passed/self.tests_run)*100,
            "critical_issues": self.critical_issues,
            "minor_issues": self.minor_issues,
            "duration": duration
        }

if __name__ == "__main__":
    tester = AetherPriorityTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if results["critical_issues"]:
        sys.exit(1)
    else:
        sys.exit(0)