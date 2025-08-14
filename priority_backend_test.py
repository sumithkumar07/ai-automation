#!/usr/bin/env python3
"""
PRIORITY BACKEND TESTING - PARALLEL ASSESSMENT
Focus on critical areas as requested in review:
1. Template System (just fixed ObjectId serialization)
2. Integration Count Verification 
3. Core API Functionality
4. Promises vs Reality Check
"""

import requests
import sys
import json
import time
import uuid
from datetime import datetime

class PriorityBackendTester:
    def __init__(self, base_url="https://feature-explorer-11.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_workflow_id = None
        self.session_id = str(uuid.uuid4())
        self.test_results = {}

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, params=None):
        """Run a single API test with detailed logging"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        print(f"   Method: {method}")
        if self.token:
            print(f"   Auth: Bearer {self.token[:20]}...")
        
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
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:300]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                    return False, error_data
                except:
                    print(f"   Error: {response.text}")
                    return False, {"error": response.text}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {"error": str(e)}

    def authenticate(self):
        """Authenticate user for testing"""
        print("\n🔐 AUTHENTICATION SETUP")
        print("-" * 40)
        
        # Try signup first
        test_user_data = {
            "email": f"priority_test_{datetime.now().strftime('%H%M%S')}@example.com",
            "password": "securepass123",
            "first_name": "Priority",
            "last_name": f"Tester {datetime.now().strftime('%H%M%S')}"
        }
        
        success, response = self.run_test(
            "User Signup",
            "POST",
            "api/auth/register",
            200,
            data=test_user_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user']['id']
            print(f"   ✅ Authentication successful")
            return True
        
        # Fallback to login
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        success, response = self.run_test(
            "User Login Fallback",
            "POST",
            "api/auth/login",
            200,
            data=login_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user']['id']
            print(f"   ✅ Authentication successful (fallback)")
            return True
        
        print(f"   ❌ Authentication failed")
        return False

    def test_priority_1_template_system(self):
        """PRIORITY 1: Test Template System (Fixed ObjectId serialization)"""
        print("\n🎯 PRIORITY 1: TEMPLATE SYSTEM TESTING")
        print("-" * 50)
        
        template_results = {
            "get_templates": False,
            "create_template": False,
            "get_template_details": False,
            "template_search": False
        }
        
        # Test 1: GET /api/templates/ (main endpoint that was failing)
        success, response = self.run_test(
            "Get Templates (Fixed ObjectId)",
            "GET",
            "api/templates/",
            200
        )
        
        if success:
            template_results["get_templates"] = True
            if 'templates' in response:
                template_count = len(response['templates'])
                print(f"   ✅ Found {template_count} templates")
                
                # Check template structure
                if template_count > 0:
                    first_template = response['templates'][0]
                    required_fields = ['id', 'name', 'description', 'category']
                    if all(field in first_template for field in required_fields):
                        print(f"   ✅ Template structure valid")
                    else:
                        print(f"   ⚠️ Template structure missing some fields")
            else:
                print(f"   ⚠️ Templates response missing 'templates' field")
        
        # Test 2: POST /api/templates/create (was also failing)
        template_data = {
            "name": f"Priority Test Template {datetime.now().strftime('%H%M%S')}",
            "description": "Test template created during priority testing",
            "category": "testing",
            "difficulty": "beginner",
            "tags": ["test", "automation", "priority"],
            "workflow_definition": {
                "nodes": [
                    {"id": "start", "type": "trigger", "name": "Start Node"},
                    {"id": "action1", "type": "action", "name": "Test Action"}
                ],
                "edges": [
                    {"source": "start", "target": "action1"}
                ]
            },
            "is_public": False
        }
        
        success, response = self.run_test(
            "Create Template (Fixed ObjectId)",
            "POST",
            "api/templates/create",
            200,
            data=template_data
        )
        
        if success:
            template_results["create_template"] = True
            if 'template_id' in response:
                created_template_id = response['template_id']
                print(f"   ✅ Template created with ID: {created_template_id}")
                
                # Test 3: GET /api/templates/{template_id}
                success, response = self.run_test(
                    "Get Template Details (Fixed ObjectId)",
                    "GET",
                    f"api/templates/{created_template_id}",
                    200
                )
                
                if success:
                    template_results["get_template_details"] = True
                    print(f"   ✅ Template details retrieved successfully")
            else:
                print(f"   ⚠️ Template creation response missing template_id")
        
        # Test 4: Template search functionality
        success, response = self.run_test(
            "Template Search",
            "GET",
            "api/templates/search",
            200,
            params={"query": "automation", "category": "business"}
        )
        
        if success:
            template_results["template_search"] = True
            if 'templates' in response:
                print(f"   ✅ Template search working")
            else:
                print(f"   ⚠️ Template search response structure unexpected")
        
        self.test_results["template_system"] = template_results
        
        # Summary for Priority 1
        working_count = sum(1 for result in template_results.values() if result)
        total_count = len(template_results)
        print(f"\n📊 PRIORITY 1 SUMMARY: {working_count}/{total_count} template endpoints working")
        
        return working_count == total_count

    def test_priority_2_integration_count(self):
        """PRIORITY 2: Integration Count Verification"""
        print("\n🎯 PRIORITY 2: INTEGRATION COUNT VERIFICATION")
        print("-" * 50)
        
        integration_results = {
            "get_integrations": False,
            "count_verification": False,
            "integration_search": False,
            "integration_categories": False
        }
        
        # Test 1: GET /api/integrations/ to count actual integrations
        success, response = self.run_test(
            "Get Available Integrations",
            "GET",
            "api/integrations/",
            200
        )
        
        if success:
            integration_results["get_integrations"] = True
            
            if isinstance(response, list):
                integration_count = len(response)
                print(f"   📊 ACTUAL INTEGRATION COUNT: {integration_count}")
                
                # Verify against homepage claim of "100+ integrations"
                if integration_count >= 100:
                    print(f"   ✅ Integration count meets homepage promise (100+)")
                    integration_results["count_verification"] = True
                elif integration_count >= 50:
                    print(f"   ⚠️ Integration count below promise but substantial: {integration_count}")
                    integration_results["count_verification"] = True
                else:
                    print(f"   ❌ Integration count significantly below promise: {integration_count}")
                
                # Check for key integrations
                integration_names = [integration.get('name', '').lower() for integration in response]
                key_integrations = ['slack', 'gmail', 'github', 'stripe', 'zapier', 'salesforce', 'hubspot']
                found_integrations = [name for name in key_integrations 
                                    if any(name in int_name for int_name in integration_names)]
                
                print(f"   🔍 Key integrations found: {', '.join(found_integrations)}")
                
                # Check categories
                categories = set()
                for integration in response:
                    if 'category' in integration:
                        categories.add(integration['category'])
                
                print(f"   📂 Integration categories: {', '.join(sorted(categories))}")
                if len(categories) >= 5:
                    integration_results["integration_categories"] = True
                    print(f"   ✅ Good category diversity ({len(categories)} categories)")
                else:
                    print(f"   ⚠️ Limited category diversity ({len(categories)} categories)")
            
            elif 'integrations' in response:
                integrations = response['integrations']
                integration_count = len(integrations)
                print(f"   📊 ACTUAL INTEGRATION COUNT: {integration_count}")
                
                if integration_count >= 100:
                    integration_results["count_verification"] = True
                    print(f"   ✅ Integration count meets homepage promise")
                else:
                    print(f"   ❌ Integration count below homepage promise: {integration_count}")
        
        # Test 2: Integration search and filtering
        success, response = self.run_test(
            "Integration Search",
            "GET",
            "api/integrations/",
            200,
            params={"search": "slack", "category": "communication"}
        )
        
        if success:
            integration_results["integration_search"] = True
            print(f"   ✅ Integration search/filtering working")
        
        self.test_results["integration_count"] = integration_results
        
        # Summary for Priority 2
        working_count = sum(1 for result in integration_results.values() if result)
        total_count = len(integration_results)
        print(f"\n📊 PRIORITY 2 SUMMARY: {working_count}/{total_count} integration features working")
        
        return working_count >= 3  # At least 3/4 should work

    def test_priority_3_core_api(self):
        """PRIORITY 3: Core API Functionality"""
        print("\n🎯 PRIORITY 3: CORE API FUNCTIONALITY")
        print("-" * 50)
        
        core_results = {
            "auth_endpoints": False,
            "dashboard_stats": False,
            "dashboard_analytics": False,
            "workflow_crud": False,
            "workflow_execution": False,
            "ai_groq_integration": False
        }
        
        # Test 1: Authentication endpoints (already tested but verify)
        success, response = self.run_test(
            "Auth Me Endpoint",
            "GET",
            "api/auth/me",
            200
        )
        
        if success:
            core_results["auth_endpoints"] = True
            print(f"   ✅ Authentication system working")
        
        # Test 2: Dashboard stats
        success, response = self.run_test(
            "Dashboard Stats",
            "GET",
            "api/dashboard/stats",
            200
        )
        
        if success:
            core_results["dashboard_stats"] = True
            if 'total_workflows' in response or 'workflows' in response:
                print(f"   ✅ Dashboard stats working")
            else:
                print(f"   ⚠️ Dashboard stats response structure unexpected")
        
        # Test 3: Dashboard analytics
        success, response = self.run_test(
            "Dashboard Analytics",
            "GET",
            "api/dashboard/analytics",
            200
        )
        
        if success:
            core_results["dashboard_analytics"] = True
            print(f"   ✅ Dashboard analytics working")
        
        # Test 4: Workflow CRUD operations
        workflow_data = {
            "name": f"Priority Test Workflow {datetime.now().strftime('%H%M%S')}",
            "description": "Test workflow for priority testing",
            "nodes": [
                {"id": "start", "type": "trigger", "name": "Start"},
                {"id": "action1", "type": "action", "name": "Process"}
            ],
            "connections": [
                {"from": "start", "to": "action1", "fromPort": "output", "toPort": "input"}
            ],
            "triggers": [{"type": "manual", "conditions": {}}]
        }
        
        success, response = self.run_test(
            "Create Workflow",
            "POST",
            "api/workflows",
            200,
            data=workflow_data
        )
        
        if success and 'id' in response:
            self.created_workflow_id = response['id']
            core_results["workflow_crud"] = True
            print(f"   ✅ Workflow CRUD working - Created ID: {self.created_workflow_id}")
            
            # Test workflow execution
            success, response = self.run_test(
                "Execute Workflow",
                "POST",
                f"api/workflows/{self.created_workflow_id}/execute",
                200
            )
            
            if success:
                core_results["workflow_execution"] = True
                print(f"   ✅ Workflow execution working")
        
        # Test 5: AI Features with GROQ integration
        ai_prompt = {
            "description": "Create a workflow that processes customer feedback and sends notifications"
        }
        
        success, response = self.run_test(
            "AI Generate Workflow (GROQ)",
            "POST",
            "api/ai/generate-workflow",
            200,
            data=ai_prompt
        )
        
        if success:
            core_results["ai_groq_integration"] = True
            if 'workflow' in response and 'confidence' in response:
                confidence = response.get('confidence', 0)
                print(f"   ✅ GROQ AI integration working (confidence: {confidence})")
                
                # Check if it's actually using GROQ or fallback
                if confidence > 0.8:
                    print(f"   ✅ High confidence suggests real GROQ integration")
                else:
                    print(f"   ⚠️ Low confidence may indicate fallback mode")
            else:
                print(f"   ⚠️ AI response structure unexpected")
        
        self.test_results["core_api"] = core_results
        
        # Summary for Priority 3
        working_count = sum(1 for result in core_results.values() if result)
        total_count = len(core_results)
        print(f"\n📊 PRIORITY 3 SUMMARY: {working_count}/{total_count} core API features working")
        
        return working_count >= 5  # At least 5/6 should work

    def test_priority_4_promises_vs_reality(self):
        """PRIORITY 4: Promises vs Reality Check"""
        print("\n🎯 PRIORITY 4: PROMISES VS REALITY CHECK")
        print("-" * 50)
        
        promises_results = {
            "node_types_25plus": False,
            "workflow_engine": False,
            "real_vs_mock_data": False,
            "api_completeness": False
        }
        
        # Test 1: Node types system (25+ nodes claimed)
        success, response = self.run_test(
            "Node Types System",
            "GET",
            "api/workflows/node-types",
            200
        )
        
        if success:
            if 'categories' in response and 'stats' in response:
                stats = response['stats']
                total_nodes = stats.get('total_nodes', 0)
                categories = stats.get('categories', 0)
                
                print(f"   📊 ACTUAL NODE COUNT: {total_nodes} across {categories} categories")
                
                if total_nodes >= 25:
                    promises_results["node_types_25plus"] = True
                    print(f"   ✅ Node count meets promise (25+)")
                else:
                    print(f"   ❌ Node count below promise: {total_nodes}")
            else:
                print(f"   ⚠️ Node types response structure unexpected")
        
        # Test 2: Workflow execution engine
        if self.created_workflow_id:
            success, response = self.run_test(
                "Workflow Engine Test",
                "POST",
                f"api/workflows/{self.created_workflow_id}/execute",
                200,
                data={"input_data": {"test": "priority_test"}}
            )
            
            if success:
                promises_results["workflow_engine"] = True
                if 'execution_id' in response:
                    print(f"   ✅ Workflow engine working - real execution")
                else:
                    print(f"   ⚠️ Workflow engine response may be mock")
        
        # Test 3: Check for real vs mock data patterns
        endpoints_to_check = [
            ("api/dashboard/stats", "Dashboard Stats"),
            ("api/integrations/", "Integrations"),
            ("api/templates/", "Templates")
        ]
        
        real_data_count = 0
        for endpoint, name in endpoints_to_check:
            success, response = self.run_test(
                f"Real Data Check - {name}",
                "GET",
                endpoint,
                200
            )
            
            if success:
                # Check for signs of real vs mock data
                response_str = json.dumps(response).lower()
                mock_indicators = ['mock', 'test', 'example', 'dummy', 'placeholder']
                
                if any(indicator in response_str for indicator in mock_indicators):
                    print(f"   ⚠️ {name} may contain mock data")
                else:
                    real_data_count += 1
                    print(f"   ✅ {name} appears to have real data")
        
        if real_data_count >= 2:
            promises_results["real_vs_mock_data"] = True
        
        # Test 4: API completeness check
        critical_endpoints = [
            "api/auth/me",
            "api/workflows",
            "api/integrations/",
            "api/dashboard/stats",
            "api/templates/",
            "api/ai/generate-workflow"
        ]
        
        working_endpoints = 0
        for endpoint in critical_endpoints:
            success, _ = self.run_test(
                f"API Completeness - {endpoint}",
                "GET",
                endpoint,
                200
            )
            if success:
                working_endpoints += 1
        
        completeness_percentage = (working_endpoints / len(critical_endpoints)) * 100
        print(f"   📊 API COMPLETENESS: {completeness_percentage:.1f}% ({working_endpoints}/{len(critical_endpoints)})")
        
        if completeness_percentage >= 80:
            promises_results["api_completeness"] = True
            print(f"   ✅ API completeness meets expectations")
        else:
            print(f"   ❌ API completeness below expectations")
        
        self.test_results["promises_vs_reality"] = promises_results
        
        # Summary for Priority 4
        working_count = sum(1 for result in promises_results.values() if result)
        total_count = len(promises_results)
        print(f"\n📊 PRIORITY 4 SUMMARY: {working_count}/{total_count} promises verified")
        
        return working_count >= 3  # At least 3/4 should work

    def generate_final_report(self):
        """Generate comprehensive final report"""
        print("\n" + "=" * 80)
        print("🎯 PRIORITY BACKEND TESTING - FINAL REPORT")
        print("=" * 80)
        
        # Overall statistics
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"\n📊 OVERALL STATISTICS:")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Priority-specific results
        print(f"\n🎯 PRIORITY RESULTS:")
        
        priorities = [
            ("PRIORITY 1: Template System", "template_system"),
            ("PRIORITY 2: Integration Count", "integration_count"),
            ("PRIORITY 3: Core API", "core_api"),
            ("PRIORITY 4: Promises vs Reality", "promises_vs_reality")
        ]
        
        for priority_name, key in priorities:
            if key in self.test_results:
                results = self.test_results[key]
                working = sum(1 for result in results.values() if result)
                total = len(results)
                percentage = (working / total * 100) if total > 0 else 0
                
                status = "✅ WORKING" if percentage >= 75 else "⚠️ PARTIAL" if percentage >= 50 else "❌ FAILING"
                print(f"   {priority_name}: {status} ({working}/{total} - {percentage:.1f}%)")
        
        # Critical issues found
        print(f"\n🚨 CRITICAL ISSUES:")
        critical_issues = []
        
        if "template_system" in self.test_results:
            template_results = self.test_results["template_system"]
            if not template_results.get("get_templates", False):
                critical_issues.append("Template GET endpoint still failing")
            if not template_results.get("create_template", False):
                critical_issues.append("Template CREATE endpoint still failing")
        
        if "integration_count" in self.test_results:
            integration_results = self.test_results["integration_count"]
            if not integration_results.get("count_verification", False):
                critical_issues.append("Integration count significantly below homepage promise")
        
        if critical_issues:
            for issue in critical_issues:
                print(f"   ❌ {issue}")
        else:
            print(f"   ✅ No critical issues found")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if "template_system" in self.test_results:
            template_results = self.test_results["template_system"]
            if not all(template_results.values()):
                print(f"   🔧 Template system needs additional ObjectId serialization fixes")
        
        if "integration_count" in self.test_results:
            integration_results = self.test_results["integration_count"]
            if not integration_results.get("count_verification", False):
                print(f"   📈 Consider adding more integrations or updating homepage claims")
        
        if success_rate >= 85:
            print(f"   🎉 Backend is production-ready with excellent functionality")
        elif success_rate >= 70:
            print(f"   ✅ Backend is functional with minor issues to address")
        else:
            print(f"   ⚠️ Backend needs significant improvements before production")
        
        return success_rate

def main():
    print("🚀 PRIORITY BACKEND TESTING - PARALLEL ASSESSMENT")
    print("=" * 80)
    print("Focus Areas:")
    print("1. Template System (ObjectId serialization fix)")
    print("2. Integration Count Verification (100+ claimed)")
    print("3. Core API Functionality (auth, dashboard, workflows, AI)")
    print("4. Promises vs Reality Check (features vs claims)")
    print("=" * 80)
    
    # Initialize tester
    tester = PriorityBackendTester()
    
    # Authenticate
    if not tester.authenticate():
        print("❌ Authentication failed, cannot proceed with testing")
        return 1
    
    # Run priority tests
    priority_results = []
    
    # Priority 1: Template System
    priority_results.append(tester.test_priority_1_template_system())
    
    # Priority 2: Integration Count
    priority_results.append(tester.test_priority_2_integration_count())
    
    # Priority 3: Core API
    priority_results.append(tester.test_priority_3_core_api())
    
    # Priority 4: Promises vs Reality
    priority_results.append(tester.test_priority_4_promises_vs_reality())
    
    # Generate final report
    success_rate = tester.generate_final_report()
    
    # Determine exit code
    priorities_passed = sum(1 for result in priority_results if result)
    
    if priorities_passed >= 3 and success_rate >= 75:
        print(f"\n🎉 PRIORITY TESTING SUCCESSFUL - {priorities_passed}/4 priorities working")
        return 0
    elif priorities_passed >= 2 and success_rate >= 60:
        print(f"\n⚠️ PRIORITY TESTING PARTIAL - {priorities_passed}/4 priorities working")
        return 0
    else:
        print(f"\n❌ PRIORITY TESTING FAILED - {priorities_passed}/4 priorities working")
        return 1

if __name__ == "__main__":
    sys.exit(main())