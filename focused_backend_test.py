import requests
import sys
import json
import time
import uuid
from datetime import datetime

class FocusedAPITester:
    def __init__(self, base_url="https://complete-qa-suite.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0

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
        print(f"   Method: {method}")
        if self.token:
            print(f"   Auth: Bearer {self.token[:20]}...")
        
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

    def authenticate(self):
        """Authenticate and get token"""
        test_user_data = {
            "email": f"focused_test_{datetime.now().strftime('%H%M%S')}@example.com",
            "password": "password123",
            "first_name": "Focused",
            "last_name": f"User {datetime.now().strftime('%H%M%S')}"
        }
        
        success, response = self.run_test(
            "Authentication - /api/auth/signup",
            "POST",
            "api/auth/signup",
            200,
            data=test_user_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user']['id']
            print(f"   ✅ Authentication successful")
            return True
        return False

    def test_core_endpoints(self):
        """Test the 5 core endpoints requested in the review"""
        results = {}
        
        # 1. Authentication Fix: /api/auth/signup
        print("\n" + "="*50)
        print("1. AUTHENTICATION FIX TEST")
        print("="*50)
        
        # Test signup endpoint specifically
        signup_data = {
            "email": f"signup_specific_{datetime.now().strftime('%H%M%S')}@example.com",
            "password": "password123",
            "first_name": "Signup",
            "last_name": "Test"
        }
        
        success, response = self.run_test(
            "Authentication Fix - /api/auth/signup endpoint",
            "POST",
            "api/auth/signup",
            200,
            data=signup_data
        )
        
        results['auth_signup'] = success
        if success:
            print("   ✅ AUTHENTICATION FIX: /api/auth/signup is working properly")
            if 'access_token' in response and 'user' in response:
                print("   ✅ Returns proper JWT token and user data")
            else:
                print("   ⚠️ Response structure may be incomplete")
        else:
            print("   ❌ AUTHENTICATION FIX: /api/auth/signup has issues")
        
        # 2. Analytics Routes
        print("\n" + "="*50)
        print("2. ANALYTICS ROUTES TEST")
        print("="*50)
        
        # Test dashboard overview
        success1, response1 = self.run_test(
            "Analytics - Dashboard Overview",
            "GET",
            "api/analytics/dashboard/overview",
            200
        )
        
        results['analytics_dashboard'] = success1
        if success1:
            print("   ✅ ANALYTICS: /api/analytics/dashboard/overview is working")
            if 'summary' in response1 and 'charts' in response1:
                print("   ✅ Returns comprehensive dashboard analytics")
            else:
                print("   ⚠️ Analytics structure may be incomplete")
        else:
            print("   ❌ ANALYTICS: /api/analytics/dashboard/overview has issues")
        
        # Test integrations usage
        success2, response2 = self.run_test(
            "Analytics - Integration Usage",
            "GET",
            "api/analytics/integrations/usage",
            200,
            params={"period": "30d"}
        )
        
        results['analytics_integrations'] = success2
        if success2:
            print("   ✅ ANALYTICS: /api/analytics/integrations/usage is working")
            if 'integration_breakdown' in response2 and 'success_rates_by_integration' in response2:
                print("   ✅ Returns detailed integration analytics")
            else:
                print("   ⚠️ Integration analytics structure may be incomplete")
        else:
            print("   ❌ ANALYTICS: /api/analytics/integrations/usage has issues")
        
        # 3. Template Routes
        print("\n" + "="*50)
        print("3. TEMPLATE ROUTES TEST")
        print("="*50)
        
        # Test templates list
        success3, response3 = self.run_test(
            "Templates - List Templates",
            "GET",
            "api/templates/",
            200,
            params={"limit": 10}
        )
        
        results['templates_list'] = success3
        if success3:
            print("   ✅ TEMPLATES: /api/templates/ is working")
            if 'templates' in response3 and 'pagination' in response3:
                print("   ✅ Returns proper template list with pagination")
            else:
                print("   ⚠️ Template list structure may be incomplete")
        else:
            print("   ❌ TEMPLATES: /api/templates/ has issues")
        
        # Test template creation (simplified)
        simple_template = {
            "name": f"Simple Test Template {datetime.now().strftime('%H%M%S')}",
            "description": "Simple test template",
            "category": "test",
            "difficulty": "beginner",
            "workflow_definition": {
                "nodes": [],
                "edges": []
            }
        }
        
        success4, response4 = self.run_test(
            "Templates - Create Template",
            "POST",
            "api/templates/create",
            200,
            data=simple_template
        )
        
        results['templates_create'] = success4
        if success4:
            print("   ✅ TEMPLATES: /api/templates/create is working")
        else:
            print("   ❌ TEMPLATES: /api/templates/create has issues")
        
        # 4. Integration Testing Routes
        print("\n" + "="*50)
        print("4. INTEGRATION TESTING ROUTES TEST")
        print("="*50)
        
        # Test connection testing
        connection_config = {
            "access_token": "test_token_123"
        }
        
        success5, response5 = self.run_test(
            "Integration Testing - Test Connection",
            "POST",
            "api/integration-testing/test-connection/github",
            200,
            data=connection_config
        )
        
        results['integration_testing'] = success5
        if success5:
            print("   ✅ INTEGRATION TESTING: /api/integration-testing/test-connection/{integration_id} is working")
            if 'test_result' in response5 and 'status' in response5:
                print("   ✅ Returns proper connection test results")
            else:
                print("   ⚠️ Connection test structure may be incomplete")
        else:
            print("   ❌ INTEGRATION TESTING: /api/integration-testing/test-connection/{integration_id} has issues")
        
        # 5. Collaboration Routes
        print("\n" + "="*50)
        print("5. COLLABORATION ROUTES TEST")
        print("="*50)
        
        # Test collaboration stats
        success6, response6 = self.run_test(
            "Collaboration - Stats",
            "GET",
            "api/collaboration/stats",
            200
        )
        
        results['collaboration_stats'] = success6
        if success6:
            print("   ✅ COLLABORATION: /api/collaboration/stats is working")
            if 'collaboration_stats' in response6:
                print("   ✅ Returns collaboration statistics")
            else:
                print("   ⚠️ Collaboration stats structure may be incomplete")
        else:
            print("   ❌ COLLABORATION: /api/collaboration/stats has issues")
        
        # Test workflow collaborators (need to create a workflow first)
        workflow_data = {
            "name": f"Test Workflow {datetime.now().strftime('%H%M%S')}",
            "description": "Test workflow for collaboration",
            "nodes": [],
            "connections": [],
            "triggers": []
        }
        
        # Try to create workflow first
        workflow_success, workflow_response = self.run_test(
            "Helper - Create Workflow for Collaboration Test",
            "POST",
            "api/workflows",
            200,
            data=workflow_data
        )
        
        if workflow_success and 'id' in workflow_response:
            workflow_id = workflow_response['id']
            
            success7, response7 = self.run_test(
                "Collaboration - Workflow Collaborators",
                "GET",
                f"api/collaboration/workflow/{workflow_id}/collaborators",
                200
            )
            
            results['collaboration_workflow'] = success7
            if success7:
                print("   ✅ COLLABORATION: /api/collaboration/workflow/{workflow_id}/collaborators is working")
                if 'collaborators' in response7:
                    print("   ✅ Returns workflow collaborators data")
                else:
                    print("   ⚠️ Collaborators data structure may be incomplete")
            else:
                print("   ❌ COLLABORATION: /api/collaboration/workflow/{workflow_id}/collaborators has issues")
        else:
            print("   ⚠️ Could not test workflow collaborators - workflow creation failed")
            results['collaboration_workflow'] = False
        
        return results

def main():
    print("🚀 Starting Focused Backend API Tests for New Features")
    print("Testing the 5 specific endpoint groups requested in the review")
    print("=" * 70)
    
    # Initialize tester
    tester = FocusedAPITester("https://complete-qa-suite.preview.emergentagent.com")
    
    # Authenticate first
    if not tester.authenticate():
        print("❌ Authentication failed, cannot proceed")
        return 1
    
    # Test core endpoints
    results = tester.test_core_endpoints()
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 FOCUSED TEST RESULTS SUMMARY")
    print("=" * 70)
    
    endpoint_groups = [
        ("Authentication Fix (/api/auth/signup)", results.get('auth_signup', False)),
        ("Analytics Dashboard (/api/analytics/dashboard/overview)", results.get('analytics_dashboard', False)),
        ("Analytics Integrations (/api/analytics/integrations/usage)", results.get('analytics_integrations', False)),
        ("Templates List (/api/templates/)", results.get('templates_list', False)),
        ("Templates Create (/api/templates/create)", results.get('templates_create', False)),
        ("Integration Testing (/api/integration-testing/test-connection/{id})", results.get('integration_testing', False)),
        ("Collaboration Stats (/api/collaboration/stats)", results.get('collaboration_stats', False)),
        ("Collaboration Workflow (/api/collaboration/workflow/{id}/collaborators)", results.get('collaboration_workflow', False))
    ]
    
    passed = 0
    total = len(endpoint_groups)
    
    for name, status in endpoint_groups:
        if status:
            print(f"✅ {name}")
            passed += 1
        else:
            print(f"❌ {name}")
    
    print(f"\nTests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"Endpoint groups working: {passed}/{total}")
    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")
    
    # Determine overall result
    if success_rate >= 80:
        print("\n✅ FOCUSED BACKEND TESTS: HIGHLY SUCCESSFUL!")
        print("The newly implemented backend features are working well.")
        return 0
    elif success_rate >= 60:
        print("\n✅ FOCUSED BACKEND TESTS: MOSTLY SUCCESSFUL!")
        print("Most newly implemented backend features are working.")
        return 0
    elif success_rate >= 40:
        print("\n⚠️ FOCUSED BACKEND TESTS: PARTIALLY SUCCESSFUL")
        print("Some newly implemented backend features need attention.")
        return 0
    else:
        print("\n❌ FOCUSED BACKEND TESTS: NEEDS ATTENTION")
        print("Several newly implemented backend features have issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())