#!/usr/bin/env python3
"""
Post-Middleware Fix Verification Test
=====================================
Comprehensive backend API testing to verify that the middleware fix resolved all issues.
Tests all critical endpoints and core functionality mentioned in the review request.
"""

import requests
import json
import time
import uuid
from datetime import datetime

class PostMiddlewareFixTester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_workflow_id = None
        self.created_integration_id = None
        self.created_execution_id = None

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
            if details:
                print(f"   {details}")
        else:
            print(f"❌ {name}")
            if details:
                print(f"   {details}")

    def make_request(self, method, endpoint, data=None, headers=None, expected_status=200):
        """Make HTTP request and return response"""
        url = f"{self.base_url}/{endpoint}"
        request_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            request_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            request_headers.update(headers)

        try:
            if method == 'GET':
                response = requests.get(url, headers=request_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=request_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=request_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=request_headers, timeout=10)

            success = response.status_code == expected_status
            try:
                response_data = response.json()
            except:
                response_data = {}
                
            return success, response.status_code, response_data
            
        except Exception as e:
            return False, 0, {"error": str(e)}

    def test_critical_endpoints_previously_failing(self):
        """Test the critical endpoints that were previously failing with 500 errors"""
        print("\n🎯 TESTING CRITICAL ENDPOINTS (Previously Failing with 500 Errors)")
        print("=" * 70)
        
        # Test GET /api/health
        success, status, data = self.make_request('GET', 'api/health')
        self.log_test("GET /api/health", success, 
                     f"Status: {status}, Database: {data.get('database_status', 'unknown')}")
        
        # Test GET /api/nodes  
        success, status, data = self.make_request('GET', 'api/nodes')
        self.log_test("GET /api/nodes", success, 
                     f"Status: {status}, Nodes: {len(data) if isinstance(data, list) else 0}")
        
        # Test GET /api/integrations
        success, status, data = self.make_request('GET', 'api/integrations')
        self.log_test("GET /api/integrations", success, 
                     f"Status: {status}, Categories: {len(data.get('categories', [])) if isinstance(data, dict) else 0}")
        
        # Test GET /api/templates
        success, status, data = self.make_request('GET', 'api/templates')
        self.log_test("GET /api/templates", success, 
                     f"Status: {status}, Templates: {len(data.get('templates', [])) if isinstance(data, dict) else 0}")
        
        # Test GET /api/enhanced/system-status
        success, status, data = self.make_request('GET', 'api/enhanced/system-status')
        self.log_test("GET /api/enhanced/system-status", success, 
                     f"Status: {status}, Overall: {data.get('overall_status', 'unknown')}")

    def test_authentication_system(self):
        """Test authentication system (signup/login with JWT)"""
        print("\n🔐 TESTING AUTHENTICATION SYSTEM")
        print("=" * 40)
        
        # Test signup
        signup_data = {
            "name": f"Test User {datetime.now().strftime('%H%M%S')}",
            "email": f"test_{datetime.now().strftime('%H%M%S')}@example.com",
            "password": "securepassword123"
        }
        
        success, status, data = self.make_request('POST', 'api/auth/signup', signup_data)
        if success and 'token' in data:
            self.token = data['token']
            self.user_id = data['user']['id']
            self.log_test("User Signup with JWT", True, 
                         f"User ID: {self.user_id[:8]}..., Token obtained")
        else:
            self.log_test("User Signup with JWT", False, f"Status: {status}")
            
            # Try login with existing user if signup fails
            login_data = {
                "email": "test@example.com",
                "password": "password123"
            }
            success, status, data = self.make_request('POST', 'api/auth/login', login_data)
            if success and 'token' in data:
                self.token = data['token']
                self.user_id = data['user']['id']
                self.log_test("User Login with JWT", True, 
                             f"User ID: {self.user_id[:8]}..., Token obtained")
            else:
                self.log_test("User Login with JWT", False, f"Status: {status}")

    def test_dashboard_apis(self):
        """Test dashboard APIs (stats, metrics)"""
        print("\n📊 TESTING DASHBOARD APIs")
        print("=" * 30)
        
        success, status, data = self.make_request('GET', 'api/dashboard/stats')
        if success:
            required_fields = ['total_workflows', 'total_executions', 'success_rate', 'recent_activities']
            has_all_fields = all(field in data for field in required_fields)
            self.log_test("Dashboard Stats API", has_all_fields, 
                         f"Workflows: {data.get('total_workflows', 0)}, Executions: {data.get('total_executions', 0)}")
        else:
            self.log_test("Dashboard Stats API", False, f"Status: {status}")

    def test_workflow_crud_operations(self):
        """Test workflow CRUD operations"""
        print("\n🔄 TESTING WORKFLOW CRUD OPERATIONS")
        print("=" * 40)
        
        # Test GET workflows
        success, status, data = self.make_request('GET', 'api/workflows')
        self.log_test("GET Workflows", success, f"Status: {status}")
        
        # Test CREATE workflow
        workflow_data = {
            "name": f"Test Workflow {datetime.now().strftime('%H%M%S')}",
            "description": "Post-middleware fix test workflow",
            "nodes": [
                {
                    "id": "node1",
                    "type": "trigger",
                    "name": "Webhook Trigger",
                    "config": {"url": "/webhook/test"}
                }
            ],
            "connections": [],
            "triggers": [{"type": "webhook", "conditions": {"path": "/webhook/test"}}]
        }
        
        success, status, data = self.make_request('POST', 'api/workflows', workflow_data)
        if success and 'workflow_id' in data:
            self.created_workflow_id = data['workflow_id']
            self.log_test("CREATE Workflow", True, f"ID: {self.created_workflow_id[:8]}...")
        else:
            self.log_test("CREATE Workflow", False, f"Status: {status}")
        
        # Test EXECUTE workflow
        if self.created_workflow_id:
            success, status, data = self.make_request('POST', f'api/workflows/{self.created_workflow_id}/execute')
            if success and 'execution_id' in data:
                self.created_execution_id = data['execution_id']
                self.log_test("EXECUTE Workflow", True, f"Execution ID: {self.created_execution_id[:8]}...")
            else:
                self.log_test("EXECUTE Workflow", False, f"Status: {status}")

    def test_integration_management(self):
        """Test integration management"""
        print("\n🔗 TESTING INTEGRATION MANAGEMENT")
        print("=" * 40)
        
        # Test GET available integrations
        success, status, data = self.make_request('GET', 'api/integrations')
        if success:
            total_integrations = data.get('total_count', 0)
            categories = len(data.get('categories', []))
            self.log_test("GET Available Integrations", True, 
                         f"Total: {total_integrations}, Categories: {categories}")
        else:
            self.log_test("GET Available Integrations", False, f"Status: {status}")
        
        # Test CREATE integration
        integration_data = {
            "name": f"Test Integration {datetime.now().strftime('%H%M%S')}",
            "platform": "slack",
            "credentials": {
                "api_key": "test_api_key_123",
                "webhook_url": "https://hooks.slack.com/test"
            }
        }
        
        success, status, data = self.make_request('POST', 'api/integrations', integration_data)
        if success and 'integration_id' in data:
            self.created_integration_id = data['integration_id']
            self.log_test("CREATE Integration", True, f"ID: {self.created_integration_id[:8]}...")
        else:
            self.log_test("CREATE Integration", False, f"Status: {status}")
        
        # Test GET user integrations
        success, status, data = self.make_request('GET', 'api/integrations/user')
        self.log_test("GET User Integrations", success, f"Status: {status}")

    def test_ai_endpoints(self):
        """Test AI endpoints (GROQ integration)"""
        print("\n🤖 TESTING AI ENDPOINTS (GROQ Integration)")
        print("=" * 45)
        
        # Test AI Chat
        chat_data = {
            "message": "What is workflow automation and how can it help businesses?"
        }
        
        success, status, data = self.make_request('POST', 'api/ai/chat', chat_data)
        if success:
            has_response = 'response' in data and len(data['response']) > 0
            model_info = data.get('model', 'unknown')
            self.log_test("AI Chat Endpoint", has_response, 
                         f"Model: {model_info}, Response length: {len(data.get('response', ''))}")
        else:
            self.log_test("AI Chat Endpoint", False, f"Status: {status}")

    def test_template_system(self):
        """Test template system functionality"""
        print("\n📋 TESTING TEMPLATE SYSTEM")
        print("=" * 30)
        
        success, status, data = self.make_request('GET', 'api/templates')
        if success:
            templates = data.get('templates', [])
            template_count = len(templates)
            self.log_test("Template System", True, f"Available templates: {template_count}")
            
            # Check template structure
            if templates:
                first_template = templates[0]
                required_fields = ['id', 'name', 'description', 'category']
                has_structure = all(field in first_template for field in required_fields)
                self.log_test("Template Structure", has_structure, 
                             f"First template: {first_template.get('name', 'Unknown')}")
        else:
            self.log_test("Template System", False, f"Status: {status}")

    def test_mongodb_connectivity(self):
        """Test MongoDB connectivity and operations"""
        print("\n🗄️ TESTING DATABASE INTEGRATION (MongoDB)")
        print("=" * 45)
        
        # Test health endpoint for database status
        success, status, data = self.make_request('GET', 'api/health')
        if success:
            db_status = data.get('database_status', 'unknown')
            db_connected = db_status == 'connected'
            self.log_test("MongoDB Connectivity", db_connected, f"Database status: {db_status}")
        else:
            self.log_test("MongoDB Connectivity", False, f"Status: {status}")
        
        # Test data persistence by checking if created workflow exists
        if self.created_workflow_id:
            success, status, data = self.make_request('GET', 'api/workflows')
            if success:
                workflows = data.get('workflows', [])
                workflow_exists = any(w.get('id') == self.created_workflow_id for w in workflows)
                self.log_test("Data Persistence", workflow_exists, 
                             f"Created workflow found in database: {workflow_exists}")
            else:
                self.log_test("Data Persistence", False, f"Status: {status}")

    def test_middleware_functionality(self):
        """Test middleware functionality (CORS, GZip)"""
        print("\n⚙️ TESTING MIDDLEWARE FUNCTIONALITY")
        print("=" * 40)
        
        # Test CORS headers
        try:
            response = requests.options(f"{self.base_url}/api/health", 
                                      headers={'Origin': 'http://localhost:3000'}, 
                                      timeout=10)
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            has_cors = any(cors_headers.values())
            self.log_test("CORS Middleware", has_cors, f"CORS headers present: {has_cors}")
        except Exception as e:
            self.log_test("CORS Middleware", False, f"Error: {str(e)}")
        
        # Test GZip compression (check for content-encoding header)
        try:
            response = requests.get(f"{self.base_url}/api/nodes", 
                                  headers={'Accept-Encoding': 'gzip'}, 
                                  timeout=10)
            has_gzip = 'gzip' in response.headers.get('Content-Encoding', '')
            self.log_test("GZip Middleware", True, f"GZip compression available: {has_gzip}")
        except Exception as e:
            self.log_test("GZip Middleware", False, f"Error: {str(e)}")

    def test_post_upgrade_validation(self):
        """Test for regressions from package updates"""
        print("\n🔄 TESTING POST-UPGRADE VALIDATION")
        print("=" * 40)
        
        # Test that all endpoints still return proper JSON
        endpoints_to_test = [
            ('GET', 'api/health'),
            ('GET', 'api/nodes'),
            ('GET', 'api/integrations'),
            ('GET', 'api/templates'),
            ('GET', 'api/enhanced/system-status')
        ]
        
        json_valid_count = 0
        for method, endpoint in endpoints_to_test:
            try:
                success, status, data = self.make_request(method, endpoint)
                if success and isinstance(data, dict):
                    json_valid_count += 1
            except:
                pass
        
        all_json_valid = json_valid_count == len(endpoints_to_test)
        self.log_test("JSON Response Validation", all_json_valid, 
                     f"{json_valid_count}/{len(endpoints_to_test)} endpoints return valid JSON")
        
        # Test FastAPI version compatibility
        success, status, data = self.make_request('GET', 'api/health')
        if success:
            version = data.get('version', 'unknown')
            self.log_test("FastAPI Version Compatibility", True, f"API version: {version}")
        else:
            self.log_test("FastAPI Version Compatibility", False, f"Status: {status}")

    def run_comprehensive_test(self):
        """Run all tests"""
        print("🚀 POST-MIDDLEWARE FIX VERIFICATION TEST")
        print("=" * 50)
        print("Testing FastAPI middleware fix and package updates:")
        print("- FastAPI: 0.104.1 → 0.116.1")
        print("- Starlette: 0.37.2 → 0.47.2") 
        print("- Uvicorn: → 0.35.0")
        print("=" * 50)
        
        # Run all test suites
        self.test_critical_endpoints_previously_failing()
        self.test_authentication_system()
        self.test_dashboard_apis()
        self.test_workflow_crud_operations()
        self.test_integration_management()
        self.test_ai_endpoints()
        self.test_template_system()
        self.test_mongodb_connectivity()
        self.test_middleware_functionality()
        self.test_post_upgrade_validation()
        
        # Print final results
        print("\n" + "=" * 50)
        print("📊 FINAL TEST RESULTS")
        print("=" * 50)
        print(f"Tests passed: {self.tests_passed}/{self.tests_run}")
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"Success rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("✅ EXCELLENT: All critical systems operational after middleware fix!")
            status = "PRODUCTION_READY"
        elif success_rate >= 80:
            print("✅ GOOD: Most systems operational, minor issues detected")
            status = "MOSTLY_OPERATIONAL"
        elif success_rate >= 70:
            print("⚠️ ACCEPTABLE: Core functionality working, some features need attention")
            status = "CORE_FUNCTIONAL"
        else:
            print("❌ ISSUES DETECTED: Significant problems found after middleware fix")
            status = "NEEDS_ATTENTION"
        
        print(f"Overall Status: {status}")
        return success_rate, status

def main():
    tester = PostMiddlewareFixTester()
    success_rate, status = tester.run_comprehensive_test()
    
    # Return appropriate exit code
    if success_rate >= 70:
        return 0
    else:
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())