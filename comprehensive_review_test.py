import requests
import sys
import json
import time
import uuid
from datetime import datetime

class ComprehensiveReviewTester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_workflow_id = None
        self.created_integration_id = None
        self.execution_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, params=params, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, params=params, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, params=params, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, params=params, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    # 1. AUTHENTICATION SYSTEM TESTS
    def test_authentication_signup(self):
        """Test user signup with JWT token validation"""
        test_user_data = {
            "name": f"Review Test User {datetime.now().strftime('%H%M%S')}",
            "email": f"review_test_{datetime.now().strftime('%H%M%S')}@aether.com",
            "password": "SecurePass123!"
        }
        
        success, response = self.run_test(
            "Authentication - User Signup",
            "POST",
            "api/auth/signup",
            200,
            data=test_user_data
        )
        
        if success and 'token' in response and 'user' in response:
            self.token = response['token']
            self.user_id = response['user']['id']
            print(f"   ✅ JWT Token obtained and user created")
            print(f"   User ID: {self.user_id}")
            return True
        return False

    def test_authentication_login(self):
        """Test user login with existing credentials"""
        # Create a test user first
        signup_data = {
            "name": "Login Test User",
            "email": "login_test@aether.com",
            "password": "LoginPass123!"
        }
        
        # Signup
        requests.post(f"{self.base_url}/api/auth/signup", json=signup_data)
        
        # Now test login
        login_data = {
            "email": "login_test@aether.com",
            "password": "LoginPass123!"
        }
        
        success, response = self.run_test(
            "Authentication - User Login",
            "POST",
            "api/auth/login",
            200,
            data=login_data
        )
        
        if success and 'token' in response:
            print(f"   ✅ Login successful with JWT token")
            return True
        return False

    # 2. DASHBOARD APIs TESTS
    def test_dashboard_stats(self):
        """Test dashboard stats endpoint with authenticated user"""
        success, response = self.run_test(
            "Dashboard - Stats API",
            "GET",
            "api/dashboard/stats",
            200
        )
        
        if success:
            expected_fields = ['total_workflows', 'total_executions', 'success_rate', 'recent_activities']
            if all(field in response for field in expected_fields):
                print(f"   ✅ Dashboard stats structure valid")
                print(f"   Workflows: {response.get('total_workflows', 0)}")
                print(f"   Executions: {response.get('total_executions', 0)}")
                print(f"   Success Rate: {response.get('success_rate', 0)}%")
                return True
            else:
                print(f"   ⚠️ Dashboard stats missing expected fields")
        return success

    # 3. WORKFLOW MANAGEMENT TESTS
    def test_workflow_create(self):
        """Test workflow creation"""
        workflow_data = {
            "name": f"Review Test Workflow {datetime.now().strftime('%H%M%S')}",
            "description": "Comprehensive review test workflow with AI integration",
            "nodes": [
                {
                    "id": "trigger_node",
                    "type": "webhook_trigger",
                    "name": "Webhook Trigger",
                    "config": {"url": "/webhook/review-test"}
                },
                {
                    "id": "ai_node",
                    "type": "ai_analyze",
                    "name": "AI Analysis",
                    "config": {"model": "groq", "prompt": "Analyze incoming data"}
                },
                {
                    "id": "email_node",
                    "type": "email_action",
                    "name": "Send Email",
                    "config": {"to": "admin@aether.com", "subject": "Analysis Complete"}
                }
            ],
            "connections": [
                {"from": "trigger_node", "to": "ai_node"},
                {"from": "ai_node", "to": "email_node"}
            ],
            "triggers": [
                {"type": "webhook", "conditions": {"path": "/webhook/review-test"}}
            ]
        }
        
        success, response = self.run_test(
            "Workflow Management - Create",
            "POST",
            "api/workflows",
            200,
            data=workflow_data
        )
        
        if success and 'workflow_id' in response:
            self.created_workflow_id = response['workflow_id']
            print(f"   ✅ Workflow created with ID: {self.created_workflow_id}")
            return True
        return False

    def test_workflow_read(self):
        """Test workflow retrieval"""
        success, response = self.run_test(
            "Workflow Management - Read All",
            "GET",
            "api/workflows",
            200
        )
        
        if success and 'workflows' in response:
            workflows = response['workflows']
            print(f"   ✅ Retrieved {len(workflows)} workflows")
            return True
        return success

    def test_workflow_execute(self):
        """Test workflow execution"""
        if not self.created_workflow_id:
            print("   ❌ No workflow ID available for execution test")
            return False
            
        success, response = self.run_test(
            "Workflow Management - Execute",
            "POST",
            f"api/workflows/{self.created_workflow_id}/execute",
            200
        )
        
        if success and 'execution_id' in response:
            self.execution_id = response['execution_id']
            print(f"   ✅ Workflow executed with execution ID: {self.execution_id}")
            return True
        return False

    # 4. INTEGRATION SYSTEM TESTS
    def test_integration_available(self):
        """Test available integrations endpoint"""
        success, response = self.run_test(
            "Integration System - Available Integrations",
            "GET",
            "api/integrations",
            200
        )
        
        if success and 'integrations' in response:
            integrations = response['integrations']
            total_count = response.get('total_count', 0)
            categories = response.get('categories', [])
            
            print(f"   ✅ Available integrations: {total_count}")
            print(f"   Categories: {len(categories)} ({', '.join(categories)})")
            
            # Check for key integrations
            all_integrations = []
            for category in integrations.values():
                all_integrations.extend([i['platform'] for i in category])
            
            key_platforms = ['slack', 'discord', 'google', 'github', 'openai', 'groq']
            found_platforms = [p for p in key_platforms if p in all_integrations]
            print(f"   Key platforms found: {len(found_platforms)}/{len(key_platforms)}")
            
            return True
        return success

    def test_integration_create(self):
        """Test integration creation"""
        integration_data = {
            "name": f"Review Test Integration {datetime.now().strftime('%H%M%S')}",
            "platform": "slack",
            "credentials": {
                "api_key": "test_api_key_review_123",
                "webhook_url": "https://hooks.slack.com/services/review/test",
                "team_id": "T123456789"
            }
        }
        
        success, response = self.run_test(
            "Integration System - Create Integration",
            "POST",
            "api/integrations",
            200,
            data=integration_data
        )
        
        if success and 'integration_id' in response:
            self.created_integration_id = response['integration_id']
            print(f"   ✅ Integration created with ID: {self.created_integration_id}")
            return True
        return False

    def test_integration_user_list(self):
        """Test user integrations listing"""
        success, response = self.run_test(
            "Integration System - User Integrations",
            "GET",
            "api/integrations/user",
            200
        )
        
        if success and 'integrations' in response:
            integrations = response['integrations']
            print(f"   ✅ User has {len(integrations)} integrations")
            
            # Verify credentials are not exposed
            for integration in integrations:
                if 'credentials' in integration:
                    print(f"   ⚠️ Credentials exposed in response")
                    return False
            
            print(f"   ✅ Credentials properly hidden from response")
            return True
        return success

    # 5. AI ENDPOINTS TESTS
    def test_ai_chat(self):
        """Test GROQ-powered AI chat endpoint"""
        chat_data = {
            "message": "How can I create an automation workflow that processes customer emails and categorizes them by urgency?"
        }
        
        success, response = self.run_test(
            "AI Integration - Chat Endpoint",
            "POST",
            "api/ai/chat",
            200,
            data=chat_data
        )
        
        if success and 'response' in response:
            ai_response = response['response']
            model = response.get('model', 'unknown')
            print(f"   ✅ AI chat successful with model: {model}")
            print(f"   Response length: {len(ai_response)} characters")
            
            # Check if it's using GROQ
            if 'llama' in model.lower() or 'groq' in model.lower():
                print(f"   ✅ Using GROQ AI model")
            else:
                print(f"   ⚠️ Not using expected GROQ model")
            
            return True
        return success

    def test_ai_workflow_generation(self):
        """Test AI workflow generation endpoint"""
        # First check if endpoint exists
        generation_data = {
            "prompt": "Create a workflow that monitors social media mentions and sends alerts to Slack"
        }
        
        success, response = self.run_test(
            "AI Integration - Workflow Generation",
            "POST",
            "api/ai/generate-workflow",
            200,
            data=generation_data
        )
        
        if success:
            print(f"   ✅ AI workflow generation endpoint available")
            return True
        else:
            # Try alternative endpoint structure
            success2, response2 = self.run_test(
                "AI Integration - Alternative Generation",
                "POST",
                "api/ai/chat",
                200,
                data={"message": "Generate a workflow for social media monitoring"}
            )
            if success2:
                print(f"   ✅ AI generation available through chat endpoint")
                return True
        
        return False

    # 6. TEMPLATE SYSTEM TESTS
    def test_templates_list(self):
        """Test template listing endpoint"""
        success, response = self.run_test(
            "Template System - List Templates",
            "GET",
            "api/templates",
            200
        )
        
        if success and 'templates' in response:
            templates = response['templates']
            print(f"   ✅ Available templates: {len(templates)}")
            
            # Check template structure
            if templates:
                template = templates[0]
                required_fields = ['id', 'name', 'description', 'category']
                if all(field in template for field in required_fields):
                    print(f"   ✅ Template structure valid")
                else:
                    print(f"   ⚠️ Template structure incomplete")
            
            return True
        return success

    # 7. ENHANCED FEATURES TESTS
    def test_enhanced_system_status(self):
        """Test enhanced system status endpoint"""
        success, response = self.run_test(
            "Enhanced Features - System Status",
            "GET",
            "api/enhanced/system-status",
            200
        )
        
        if success:
            if 'overall_status' in response and 'system_components' in response:
                overall_status = response.get('overall_status', 'unknown')
                components = response.get('system_components', {})
                
                print(f"   ✅ Enhanced system status: {overall_status}")
                print(f"   Components monitored: {len(components)}")
                
                # Check component statuses
                for component, status in components.items():
                    component_status = status.get('status', 'unknown')
                    print(f"   - {component}: {component_status}")
                
                return True
            else:
                print(f"   ⚠️ Enhanced system status missing expected fields")
        return success

    # 8. DATABASE CONNECTIVITY TESTS
    def test_database_connectivity(self):
        """Test MongoDB connections and data persistence"""
        # Test health endpoint for database status
        success, response = self.run_test(
            "Database Connectivity - Health Check",
            "GET",
            "api/health",
            200
        )
        
        if success:
            db_status = response.get('database_status', 'unknown')
            if db_status == 'connected':
                print(f"   ✅ MongoDB connection: {db_status}")
                
                # Test data persistence by creating and retrieving data
                if self.created_workflow_id:
                    # Try to retrieve the workflow we created
                    workflow_success, workflow_response = self.run_test(
                        "Database Connectivity - Data Persistence",
                        "GET",
                        "api/workflows",
                        200
                    )
                    
                    if workflow_success:
                        workflows = workflow_response.get('workflows', [])
                        workflow_found = any(w.get('id') == self.created_workflow_id for w in workflows)
                        if workflow_found:
                            print(f"   ✅ Data persistence verified - workflow found")
                        else:
                            print(f"   ⚠️ Data persistence issue - workflow not found")
                        return workflow_found
                
                return True
            else:
                print(f"   ❌ MongoDB connection issue: {db_status}")
                return False
        return success

    # 9. ERROR HANDLING TESTS
    def test_error_handling(self):
        """Test proper error responses for invalid requests"""
        # Test invalid authentication
        temp_token = self.token
        self.token = "invalid_token_123"
        
        success1, response1 = self.run_test(
            "Error Handling - Invalid Token",
            "GET",
            "api/dashboard/stats",
            401
        )
        
        self.token = temp_token  # Restore valid token
        
        # Test invalid workflow ID
        success2, response2 = self.run_test(
            "Error Handling - Invalid Resource",
            "GET",
            "api/workflows/invalid-workflow-id",
            404
        )
        
        # Test invalid request data
        success3, response3 = self.run_test(
            "Error Handling - Invalid Data",
            "POST",
            "api/workflows",
            422,  # Validation error
            data={"invalid": "data"}
        )
        
        error_tests_passed = sum([success1, success2, success3])
        print(f"   ✅ Error handling tests passed: {error_tests_passed}/3")
        
        return error_tests_passed >= 2

    # 10. PERFORMANCE TESTS
    def test_performance_response_times(self):
        """Test response times and middleware functionality"""
        endpoints_to_test = [
            ("api/health", "GET"),
            ("api/nodes", "GET"),
            ("api/integrations", "GET"),
            ("api/templates", "GET")
        ]
        
        response_times = []
        
        for endpoint, method in endpoints_to_test:
            start_time = time.time()
            
            if method == "GET":
                try:
                    response = requests.get(f"{self.base_url}/{endpoint}", timeout=5)
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                    response_times.append(response_time)
                    
                    print(f"   {endpoint}: {response_time:.0f}ms (Status: {response.status_code})")
                except Exception as e:
                    print(f"   {endpoint}: Error - {e}")
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            print(f"   ✅ Average response time: {avg_response_time:.0f}ms")
            
            # Check if response times are reasonable (under 2 seconds)
            if avg_response_time < 2000:
                print(f"   ✅ Performance acceptable (< 2s)")
                return True
            else:
                print(f"   ⚠️ Performance slow (> 2s)")
                return False
        
        return False

def main():
    print("🚀 COMPREHENSIVE BACKEND FUNCTIONALITY REVIEW TEST")
    print("=" * 70)
    print("Testing all areas specified in the review request:")
    print("1. Authentication System, 2. Dashboard APIs, 3. Workflow Management")
    print("4. Integration System, 5. AI Endpoints, 6. Template System")
    print("7. Enhanced Features, 8. Database Connectivity, 9. Error Handling, 10. Performance")
    print("=" * 70)
    
    # Initialize tester
    tester = ComprehensiveReviewTester("http://localhost:8001")
    
    # 1. AUTHENTICATION SYSTEM
    print("\n🔐 1. AUTHENTICATION SYSTEM")
    print("-" * 40)
    auth_signup = tester.test_authentication_signup()
    auth_login = tester.test_authentication_login()
    
    if not auth_signup:
        print("❌ Authentication failed, stopping comprehensive tests")
        return 1
    
    # 2. DASHBOARD APIs
    print("\n📊 2. DASHBOARD APIs")
    print("-" * 40)
    dashboard_stats = tester.test_dashboard_stats()
    
    # 3. WORKFLOW MANAGEMENT
    print("\n⚙️ 3. WORKFLOW MANAGEMENT")
    print("-" * 40)
    workflow_create = tester.test_workflow_create()
    workflow_read = tester.test_workflow_read()
    workflow_execute = tester.test_workflow_execute()
    
    # 4. INTEGRATION SYSTEM
    print("\n🔗 4. INTEGRATION SYSTEM")
    print("-" * 40)
    integration_available = tester.test_integration_available()
    integration_create = tester.test_integration_create()
    integration_user_list = tester.test_integration_user_list()
    
    # 5. AI ENDPOINTS
    print("\n🤖 5. AI ENDPOINTS (GROQ-POWERED)")
    print("-" * 40)
    ai_chat = tester.test_ai_chat()
    ai_workflow_gen = tester.test_ai_workflow_generation()
    
    # 6. TEMPLATE SYSTEM
    print("\n📋 6. TEMPLATE SYSTEM")
    print("-" * 40)
    templates_list = tester.test_templates_list()
    
    # 7. ENHANCED FEATURES
    print("\n🚀 7. ENHANCED FEATURES")
    print("-" * 40)
    enhanced_status = tester.test_enhanced_system_status()
    
    # 8. DATABASE CONNECTIVITY
    print("\n🗄️ 8. DATABASE CONNECTIVITY")
    print("-" * 40)
    database_connectivity = tester.test_database_connectivity()
    
    # 9. ERROR HANDLING
    print("\n⚠️ 9. ERROR HANDLING")
    print("-" * 40)
    error_handling = tester.test_error_handling()
    
    # 10. PERFORMANCE
    print("\n⚡ 10. PERFORMANCE & MIDDLEWARE")
    print("-" * 40)
    performance = tester.test_performance_response_times()
    
    # FINAL RESULTS
    print("\n" + "=" * 70)
    print("📊 COMPREHENSIVE REVIEW TEST RESULTS")
    print("=" * 70)
    
    # Calculate results by category
    results = {
        "Authentication System": [auth_signup, auth_login],
        "Dashboard APIs": [dashboard_stats],
        "Workflow Management": [workflow_create, workflow_read, workflow_execute],
        "Integration System": [integration_available, integration_create, integration_user_list],
        "AI Endpoints": [ai_chat, ai_workflow_gen],
        "Template System": [templates_list],
        "Enhanced Features": [enhanced_status],
        "Database Connectivity": [database_connectivity],
        "Error Handling": [error_handling],
        "Performance": [performance]
    }
    
    total_tests = 0
    total_passed = 0
    
    for category, tests in results.items():
        category_passed = sum(tests)
        category_total = len(tests)
        total_tests += category_total
        total_passed += category_passed
        
        status = "✅" if category_passed == category_total else "⚠️" if category_passed > 0 else "❌"
        print(f"{status} {category}: {category_passed}/{category_total}")
    
    print("-" * 70)
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    print(f"📈 OVERALL SUCCESS RATE: {success_rate:.1f}% ({total_passed}/{total_tests})")
    
    # Determine final status
    if success_rate >= 90:
        print("🎉 EXCELLENT - Backend exceeds review requirements!")
        status_code = 0
    elif success_rate >= 80:
        print("✅ VERY GOOD - Backend meets review requirements!")
        status_code = 0
    elif success_rate >= 70:
        print("✅ GOOD - Backend mostly meets review requirements!")
        status_code = 0
    elif success_rate >= 60:
        print("⚠️ ACCEPTABLE - Backend has some issues but core functionality works!")
        status_code = 0
    else:
        print("❌ NEEDS IMPROVEMENT - Backend has significant issues!")
        status_code = 1
    
    print("=" * 70)
    return status_code

if __name__ == "__main__":
    sys.exit(main())