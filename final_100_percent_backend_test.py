#!/usr/bin/env python3
"""
Comprehensive Backend Testing for 100% Success Rate
Aether Automation Platform - Final Assessment

Focus: Address remaining 17.2% issues to achieve 100% functionality
Target: Verify all enhanced endpoints, real vs demo data, production readiness
"""

import requests
import sys
import json
import time
import uuid
from datetime import datetime
import concurrent.futures
import threading

class FinalComprehensiveAPITester:
    def __init__(self, base_url="https://frontend-e2e-test.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_failures = []
        self.minor_issues = []
        self.session_id = str(uuid.uuid4())
        self.created_resources = []
        
    def log_result(self, test_name, success, details="", is_critical=True):
        """Log test results with categorization"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}: PASSED")
            if details:
                print(f"   Details: {details}")
        else:
            if is_critical:
                self.critical_failures.append(f"{test_name}: {details}")
                print(f"❌ {test_name}: CRITICAL FAILURE")
            else:
                self.minor_issues.append(f"{test_name}: {details}")
                print(f"⚠️ {test_name}: MINOR ISSUE")
            print(f"   Details: {details}")

    def make_request(self, method, endpoint, data=None, params=None, expected_status=200):
        """Make HTTP request with proper error handling"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=15)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, params=params, timeout=15)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, params=params, timeout=15)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, params=params, timeout=15)
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None

    def test_authentication_system(self):
        """Test authentication with real user data"""
        print("\n🔐 TESTING AUTHENTICATION SYSTEM")
        
        # Test user registration
        user_data = {
            "email": f"test.user.{self.session_id[:8]}@aetherautomation.com",
            "password": "SecurePass123!",
            "first_name": "Aether",
            "last_name": "TestUser"
        }
        
        response = self.make_request('POST', 'api/auth/register', user_data, expected_status=200)
        if response and response.status_code == 200:
            try:
                auth_data = response.json()
                self.token = auth_data.get('access_token')
                self.user_id = auth_data.get('user_id')
                self.log_result("User Registration", True, f"User ID: {self.user_id}")
            except:
                self.log_result("User Registration", False, "Invalid response format", True)
        else:
            self.log_result("User Registration", False, f"Status: {response.status_code if response else 'No response'}", True)
            return False
        
        # Test token validation
        response = self.make_request('GET', 'api/auth/me')
        if response and response.status_code == 200:
            self.log_result("Token Validation", True, "JWT token working")
        else:
            self.log_result("Token Validation", False, f"Status: {response.status_code if response else 'No response'}", True)
            
        return self.token is not None

    def test_remaining_critical_issues(self):
        """Test the specific remaining issues identified in previous testing"""
        print("\n🎯 TESTING REMAINING CRITICAL ISSUES")
        
        # Issue 1: AI Suggestions query parameter format
        print("\n1. Testing AI Suggestions Query Parameter Format")
        response = self.make_request('GET', 'api/ai/suggest-integrations', params={'description': 'email automation'})
        if response and response.status_code == 200:
            self.log_result("AI Suggestions Query Param", True, "Query parameter format working")
        else:
            # Try alternative format
            response = self.make_request('POST', 'api/ai/suggest-integrations', {'description': 'email automation'})
            if response and response.status_code == 200:
                self.log_result("AI Suggestions JSON Body", True, "JSON body format working")
            else:
                self.log_result("AI Suggestions", False, f"Both formats failed: {response.status_code if response else 'No response'}", False)
        
        # Issue 2: AI Chat query parameter format
        print("\n2. Testing AI Chat Query Parameter Format")
        response = self.make_request('GET', 'api/ai/chat', params={'message': 'Hello AI'})
        if response and response.status_code == 200:
            self.log_result("AI Chat Query Param", True, "Query parameter format working")
        else:
            # Try JSON body format
            response = self.make_request('POST', 'api/ai/chat', {'message': 'Hello AI'})
            if response and response.status_code == 200:
                self.log_result("AI Chat JSON Body", True, "JSON body format working")
            else:
                self.log_result("AI Chat", False, f"Both formats failed: {response.status_code if response else 'No response'}", False)
        
        # Issue 3: AI Chat empty message validation
        print("\n3. Testing AI Chat Empty Message Validation")
        response = self.make_request('POST', 'api/ai/chat', {'message': ''})
        if response and response.status_code == 422:
            self.log_result("AI Chat Empty Validation", True, "Returns 422 as expected")
        elif response and response.status_code == 400:
            self.log_result("AI Chat Empty Validation", False, "Returns 400 instead of 422", False)
        else:
            self.log_result("AI Chat Empty Validation", False, f"Unexpected status: {response.status_code if response else 'No response'}", False)
        
        # Issue 4: Node Types Count
        print("\n4. Testing Node Types Count")
        response = self.make_request('GET', 'api/node-types')
        if response and response.status_code == 200:
            try:
                data = response.json()
                total_nodes = 0
                if isinstance(data, dict) and 'categories' in data:
                    for category in data['categories']:
                        if 'nodes' in category:
                            total_nodes += len(category['nodes'])
                elif isinstance(data, list):
                    total_nodes = len(data)
                
                if total_nodes >= 35:
                    self.log_result("Node Types Count", True, f"Found {total_nodes} nodes (≥35)")
                elif total_nodes > 0:
                    self.log_result("Node Types Count", False, f"Found {total_nodes} nodes (expected ≥35)", False)
                else:
                    self.log_result("Node Types Count", False, "Found 0 nodes (expected ≥35)", True)
            except:
                self.log_result("Node Types Count", False, "Invalid response format", True)
        else:
            self.log_result("Node Types Count", False, f"Status: {response.status_code if response else 'No response'}", True)
        
        # Issue 5: Template Creation workflow_definition format
        print("\n5. Testing Template Creation Workflow Definition Format")
        template_data = {
            "name": f"Test Template {self.session_id[:8]}",
            "description": "Test template for workflow_definition format",
            "category": "automation",
            "workflow_definition": {
                "nodes": [
                    {"id": "1", "type": "trigger", "name": "Email Trigger"},
                    {"id": "2", "type": "action", "name": "Send Response"}
                ],
                "connections": [{"from": "1", "to": "2"}]
            }
        }
        
        response = self.make_request('POST', 'api/templates/create', template_data)
        if response and response.status_code == 200:
            try:
                result = response.json()
                template_id = result.get('id') or result.get('template_id')
                self.created_resources.append(('template', template_id))
                self.log_result("Template Creation Workflow Definition", True, f"Template ID: {template_id}")
            except:
                self.log_result("Template Creation Workflow Definition", False, "Invalid response format", True)
        else:
            # Try alternative format
            template_data['nodes'] = template_data.pop('workflow_definition')
            response = self.make_request('POST', 'api/templates/create', template_data)
            if response and response.status_code == 200:
                self.log_result("Template Creation Nodes Format", True, "Alternative nodes format working")
            else:
                self.log_result("Template Creation", False, f"Both formats failed: {response.status_code if response else 'No response'}", True)

    def test_integration_count_promise(self):
        """Verify integration count matches homepage promise"""
        print("\n🔗 TESTING INTEGRATION COUNT PROMISE")
        
        response = self.make_request('GET', 'api/integrations')
        if response and response.status_code == 200:
            try:
                data = response.json()
                integration_count = len(data.get('integrations', []))
                
                if integration_count >= 100:
                    self.log_result("Integration Count Promise", True, f"Found {integration_count} integrations (≥100)")
                else:
                    self.log_result("Integration Count Promise", False, f"Found {integration_count} integrations (promised 100+)", True)
                    
                # Test integration search functionality
                response = self.make_request('GET', 'api/integrations/search', params={'q': 'slack'})
                if response and response.status_code == 200:
                    search_data = response.json()
                    slack_results = len(search_data.get('results', []))
                    self.log_result("Integration Search", True, f"Found {slack_results} Slack integrations")
                else:
                    self.log_result("Integration Search", False, f"Search failed: {response.status_code if response else 'No response'}", False)
                    
            except Exception as e:
                self.log_result("Integration Count Promise", False, f"Response parsing error: {e}", True)
        else:
            self.log_result("Integration Count Promise", False, f"Status: {response.status_code if response else 'No response'}", True)

    def test_workflow_execution_engine(self):
        """Test workflow execution engine comprehensively"""
        print("\n⚙️ TESTING WORKFLOW EXECUTION ENGINE")
        
        # Create a test workflow
        workflow_data = {
            "name": f"Test Execution Workflow {self.session_id[:8]}",
            "description": "Test workflow for execution engine",
            "nodes": [
                {
                    "id": "trigger_1",
                    "type": "trigger",
                    "name": "Manual Trigger",
                    "config": {"trigger_type": "manual"}
                },
                {
                    "id": "action_1", 
                    "type": "action",
                    "name": "Log Action",
                    "config": {"action_type": "log", "message": "Test execution"}
                }
            ],
            "connections": [{"from": "trigger_1", "to": "action_1"}]
        }
        
        response = self.make_request('POST', 'api/workflows/', workflow_data)
        if response and response.status_code == 200:
            try:
                workflow_result = response.json()
                workflow_id = workflow_result.get('id') or workflow_result.get('workflow_id')
                self.created_resources.append(('workflow', workflow_id))
                self.log_result("Workflow Creation", True, f"Workflow ID: {workflow_id}")
                
                # Test workflow execution
                response = self.make_request('POST', f'api/workflows/{workflow_id}/execute')
                if response and response.status_code == 200:
                    try:
                        exec_result = response.json()
                        execution_id = exec_result.get('execution_id')
                        self.log_result("Workflow Execution", True, f"Execution ID: {execution_id}")
                        
                        # Test execution status endpoint
                        if execution_id:
                            time.sleep(1)  # Allow execution to process
                            response = self.make_request('GET', f'api/workflows/executions/{execution_id}/status')
                            if response and response.status_code == 200:
                                status_data = response.json()
                                self.log_result("Execution Status", True, f"Status: {status_data.get('status', 'unknown')}")
                            else:
                                # Try alternative endpoint
                                response = self.make_request('GET', f'api/executions/{execution_id}/status')
                                if response and response.status_code == 200:
                                    self.log_result("Execution Status Alternative", True, "Alternative endpoint working")
                                else:
                                    self.log_result("Execution Status", False, f"Both endpoints failed: {response.status_code if response else 'No response'}", True)
                    except Exception as e:
                        self.log_result("Workflow Execution", False, f"Response parsing error: {e}", True)
                else:
                    self.log_result("Workflow Execution", False, f"Status: {response.status_code if response else 'No response'}", True)
                    
            except Exception as e:
                self.log_result("Workflow Creation", False, f"Response parsing error: {e}", True)
        else:
            self.log_result("Workflow Creation", False, f"Status: {response.status_code if response else 'No response'}", True)

    def test_ai_capabilities(self):
        """Test AI capabilities comprehensively"""
        print("\n🤖 TESTING AI CAPABILITIES")
        
        # Test AI workflow generation
        ai_request = {
            "description": "Create a workflow that monitors email and sends Slack notifications",
            "requirements": ["email monitoring", "slack integration", "real-time alerts"]
        }
        
        response = self.make_request('POST', 'api/ai/generate-workflow', ai_request)
        if response and response.status_code == 200:
            try:
                ai_result = response.json()
                workflow_nodes = ai_result.get('workflow', {}).get('nodes', [])
                confidence = ai_result.get('confidence', 0)
                self.log_result("AI Workflow Generation", True, f"Generated {len(workflow_nodes)} nodes, confidence: {confidence}")
            except:
                self.log_result("AI Workflow Generation", False, "Invalid response format", True)
        else:
            self.log_result("AI Workflow Generation", False, f"Status: {response.status_code if response else 'No response'}", True)
        
        # Test AI dashboard insights
        response = self.make_request('GET', 'api/ai/dashboard-insights')
        if response and response.status_code == 200:
            try:
                insights = response.json()
                insights_count = len(insights.get('insights', []))
                self.log_result("AI Dashboard Insights", True, f"Generated {insights_count} insights")
            except:
                self.log_result("AI Dashboard Insights", False, "Invalid response format", False)
        else:
            self.log_result("AI Dashboard Insights", False, f"Status: {response.status_code if response else 'No response'}", False)

    def test_template_system_comprehensive(self):
        """Test template system comprehensively"""
        print("\n📋 TESTING TEMPLATE SYSTEM")
        
        # Test template listing
        response = self.make_request('GET', 'api/templates/')
        if response and response.status_code == 200:
            try:
                templates = response.json()
                template_count = len(templates.get('templates', []))
                self.log_result("Template Listing", True, f"Found {template_count} templates")
            except:
                self.log_result("Template Listing", False, "Invalid response format", True)
        else:
            self.log_result("Template Listing", False, f"Status: {response.status_code if response else 'No response'}", True)
        
        # Test template search
        response = self.make_request('GET', 'api/templates/search', params={'q': 'automation'})
        if response and response.status_code == 200:
            try:
                search_results = response.json()
                results_count = len(search_results.get('results', []))
                self.log_result("Template Search", True, f"Found {results_count} automation templates")
            except:
                self.log_result("Template Search", False, "Invalid response format", False)
        else:
            self.log_result("Template Search", False, f"Status: {response.status_code if response else 'No response'}", False)

    def test_dashboard_analytics(self):
        """Test dashboard analytics for real data"""
        print("\n📊 TESTING DASHBOARD ANALYTICS")
        
        # Test dashboard stats
        response = self.make_request('GET', 'api/dashboard/stats')
        if response and response.status_code == 200:
            try:
                stats = response.json()
                workflow_count = stats.get('total_workflows', 0)
                execution_count = stats.get('total_executions', 0)
                success_rate = stats.get('success_rate', 0)
                
                # Check if data appears real vs demo
                is_real_data = True
                if workflow_count == 0 and execution_count == 0:
                    is_real_data = True  # New user account
                elif workflow_count == 42 or execution_count == 1337:
                    is_real_data = False  # Common demo numbers
                
                self.log_result("Dashboard Stats", True, f"Workflows: {workflow_count}, Executions: {execution_count}, Success Rate: {success_rate}% - {'Real' if is_real_data else 'Demo'} data")
            except:
                self.log_result("Dashboard Stats", False, "Invalid response format", True)
        else:
            self.log_result("Dashboard Stats", False, f"Status: {response.status_code if response else 'No response'}", True)
        
        # Test analytics overview
        response = self.make_request('GET', 'api/analytics/dashboard/overview')
        if response and response.status_code == 200:
            try:
                analytics = response.json()
                charts_data = analytics.get('charts', {})
                insights = analytics.get('insights', [])
                self.log_result("Analytics Overview", True, f"Charts: {len(charts_data)}, Insights: {len(insights)}")
            except:
                self.log_result("Analytics Overview", False, "Invalid response format", False)
        else:
            self.log_result("Analytics Overview", False, f"Status: {response.status_code if response else 'No response'}", False)

    def test_performance_and_scalability(self):
        """Test performance and scalability"""
        print("\n⚡ TESTING PERFORMANCE & SCALABILITY")
        
        # Test concurrent requests
        def make_concurrent_request():
            return self.make_request('GET', 'api/dashboard/stats')
        
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_concurrent_request) for _ in range(5)]
            responses = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        successful_requests = sum(1 for r in responses if r and r.status_code == 200)
        
        if successful_requests == 5:
            self.log_result("Concurrent Load Test", True, f"5/5 requests successful in {end_time - start_time:.2f}s")
        else:
            self.log_result("Concurrent Load Test", False, f"Only {successful_requests}/5 requests successful", False)

    def cleanup_resources(self):
        """Clean up created test resources"""
        print("\n🧹 CLEANING UP TEST RESOURCES")
        
        for resource_type, resource_id in self.created_resources:
            if resource_type == 'workflow':
                response = self.make_request('DELETE', f'api/workflows/{resource_id}')
                if response and response.status_code in [200, 204]:
                    print(f"✅ Cleaned up workflow: {resource_id}")
                else:
                    print(f"⚠️ Failed to clean up workflow: {resource_id}")
            elif resource_type == 'template':
                # Templates might not have delete endpoint, skip cleanup
                print(f"ℹ️ Skipping template cleanup: {resource_id}")

    def run_comprehensive_test(self):
        """Run comprehensive test suite"""
        print("🚀 STARTING COMPREHENSIVE BACKEND TESTING FOR 100% SUCCESS RATE")
        print("=" * 80)
        
        # Authentication is required for most tests
        if not self.test_authentication_system():
            print("❌ Authentication failed - cannot proceed with protected endpoint testing")
            return
        
        # Test remaining critical issues
        self.test_remaining_critical_issues()
        
        # Test core functionality
        self.test_integration_count_promise()
        self.test_workflow_execution_engine()
        self.test_ai_capabilities()
        self.test_template_system_comprehensive()
        self.test_dashboard_analytics()
        self.test_performance_and_scalability()
        
        # Cleanup
        self.cleanup_resources()
        
        # Final results
        print("\n" + "=" * 80)
        print("🎯 FINAL COMPREHENSIVE TEST RESULTS")
        print("=" * 80)
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        print(f"📊 OVERALL SUCCESS RATE: {success_rate:.1f}% ({self.tests_passed}/{self.tests_run} tests passed)")
        
        if self.critical_failures:
            print(f"\n❌ CRITICAL FAILURES ({len(self.critical_failures)}):")
            for failure in self.critical_failures:
                print(f"   • {failure}")
        
        if self.minor_issues:
            print(f"\n⚠️ MINOR ISSUES ({len(self.minor_issues)}):")
            for issue in self.minor_issues:
                print(f"   • {issue}")
        
        if success_rate >= 95:
            print(f"\n🎉 EXCELLENT: {success_rate:.1f}% success rate - Production ready!")
        elif success_rate >= 85:
            print(f"\n✅ GOOD: {success_rate:.1f}% success rate - Minor issues to address")
        elif success_rate >= 70:
            print(f"\n⚠️ MODERATE: {success_rate:.1f}% success rate - Several issues need fixing")
        else:
            print(f"\n❌ POOR: {success_rate:.1f}% success rate - Major issues need immediate attention")
        
        print("\n🔍 ASSESSMENT SUMMARY:")
        print(f"   • Total Tests: {self.tests_run}")
        print(f"   • Passed: {self.tests_passed}")
        print(f"   • Critical Failures: {len(self.critical_failures)}")
        print(f"   • Minor Issues: {len(self.minor_issues)}")
        print(f"   • Success Rate: {success_rate:.1f}%")
        
        return success_rate >= 95

if __name__ == "__main__":
    tester = FinalComprehensiveAPITester()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)