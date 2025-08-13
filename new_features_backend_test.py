import requests
import sys
import json
import time
import uuid
from datetime import datetime

class NewFeaturesAPITester:
    def __init__(self, base_url="https://thorough-testing.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_workflow_id = None
        self.created_template_id = None

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
                    print(f"   Response: {json.dumps(response_data, indent=2)[:300]}...")
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

    def test_signup_endpoint(self):
        """Test the /api/auth/signup endpoint specifically"""
        test_user_data = {
            "email": f"signup_test_{datetime.now().strftime('%H%M%S')}@example.com",
            "password": "password123",
            "first_name": "Signup",
            "last_name": f"User {datetime.now().strftime('%H%M%S')}"
        }
        
        success, response = self.run_test(
            "Authentication Fix - /api/auth/signup",
            "POST",
            "api/auth/signup",
            200,
            data=test_user_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user']['id']
            print(f"   ✅ Signup successful, token obtained: {self.token[:20]}...")
            return True
        return False

    def test_analytics_dashboard_overview(self):
        """Test /api/analytics/dashboard/overview endpoint"""
        success, response = self.run_test(
            "Analytics Routes - Dashboard Overview",
            "GET",
            "api/analytics/dashboard/overview",
            200
        )
        
        if success:
            # Verify response structure
            expected_fields = ['user_id', 'summary', 'charts', 'insights']
            if all(field in response for field in expected_fields):
                print(f"   ✅ Dashboard overview structure valid")
                
                # Check summary fields
                summary = response.get('summary', {})
                summary_fields = ['total_workflows', 'total_executions', 'success_rate', 'workflow_efficiency_score']
                if all(field in summary for field in summary_fields):
                    print(f"   ✅ Summary metrics present")
                else:
                    print(f"   ⚠️ Some summary metrics missing")
                
                # Check charts structure
                charts = response.get('charts', {})
                chart_fields = ['executions_over_time', 'success_rate_trend', 'workflow_performance']
                if all(field in charts for field in chart_fields):
                    print(f"   ✅ Chart data structure valid")
                else:
                    print(f"   ⚠️ Some chart data missing")
                    
            else:
                print(f"   ⚠️ Dashboard overview missing expected fields")
        
        return success

    def test_analytics_integrations_usage(self):
        """Test /api/analytics/integrations/usage endpoint"""
        success, response = self.run_test(
            "Analytics Routes - Integration Usage",
            "GET",
            "api/analytics/integrations/usage",
            200,
            params={"period": "30d"}
        )
        
        if success:
            # Verify response structure
            expected_fields = ['period', 'total_integration_calls', 'unique_integrations_used', 'integration_breakdown']
            if all(field in response for field in expected_fields):
                print(f"   ✅ Integration usage structure valid")
                
                # Check additional analytics fields
                analytics_fields = ['success_rates_by_integration', 'performance_by_integration', 'cost_analysis', 'trends']
                if all(field in response for field in analytics_fields):
                    print(f"   ✅ Advanced analytics fields present")
                else:
                    print(f"   ⚠️ Some advanced analytics missing")
                    
                # Check recommendations
                if 'recommendations' in response:
                    print(f"   ✅ Recommendations system working")
                else:
                    print(f"   ⚠️ Recommendations missing")
                    
            else:
                print(f"   ⚠️ Integration usage missing expected fields")
        
        return success

    def test_templates_list(self):
        """Test /api/templates/ endpoint"""
        success, response = self.run_test(
            "Template Routes - List Templates",
            "GET",
            "api/templates/",
            200,
            params={"sort_by": "popular", "limit": 10}
        )
        
        if success:
            # Verify response structure
            expected_fields = ['templates', 'pagination', 'filters']
            if all(field in response for field in expected_fields):
                print(f"   ✅ Templates list structure valid")
                
                # Check pagination
                pagination = response.get('pagination', {})
                pagination_fields = ['total', 'limit', 'offset', 'has_more']
                if all(field in pagination for field in pagination_fields):
                    print(f"   ✅ Pagination structure valid")
                else:
                    print(f"   ⚠️ Pagination structure incomplete")
                
                # Check filters
                filters = response.get('filters', {})
                filter_fields = ['available_categories', 'available_difficulties', 'popular_tags']
                if all(field in filters for field in filter_fields):
                    print(f"   ✅ Filter options available")
                else:
                    print(f"   ⚠️ Some filter options missing")
                    
                # Check templates structure
                templates = response.get('templates', [])
                if templates and isinstance(templates, list):
                    template = templates[0]
                    template_fields = ['id', 'name', 'description', 'category', 'difficulty']
                    if all(field in template for field in template_fields):
                        print(f"   ✅ Template structure valid")
                    else:
                        print(f"   ⚠️ Template structure incomplete")
                        
            else:
                print(f"   ⚠️ Templates list missing expected fields")
        
        return success

    def test_templates_create(self):
        """Test /api/templates/create endpoint"""
        template_data = {
            "name": f"Test Template {datetime.now().strftime('%H%M%S')}",
            "description": "A test template created by automated testing",
            "category": "automation",
            "difficulty": "beginner",
            "tags": ["test", "automation", "api"],
            "workflow_definition": {
                "nodes": [
                    {
                        "id": "node1",
                        "type": "trigger",
                        "name": "HTTP Trigger",
                        "config": {"method": "POST", "path": "/webhook"}
                    },
                    {
                        "id": "node2",
                        "type": "action",
                        "name": "Send Email",
                        "config": {"to": "user@example.com", "subject": "Test"}
                    }
                ],
                "edges": [
                    {
                        "id": "edge1",
                        "source": "node1",
                        "target": "node2"
                    }
                ]
            },
            "is_public": False,
            "requirements": ["email_integration"]
        }
        
        success, response = self.run_test(
            "Template Routes - Create Template",
            "POST",
            "api/templates/create",
            200,
            data=template_data
        )
        
        if success:
            # Verify response structure
            if 'template_id' in response or 'id' in response:
                self.created_template_id = response.get('template_id') or response.get('id')
                print(f"   ✅ Template created successfully: {self.created_template_id}")
                
                # Check if template has proper structure
                if 'name' in response and 'category' in response:
                    print(f"   ✅ Template response includes metadata")
                else:
                    print(f"   ⚠️ Template response missing some metadata")
                    
            else:
                print(f"   ⚠️ Template creation response missing ID")
        
        return success

    def test_integration_testing_connection(self):
        """Test /api/integration-testing/test-connection/{integration_id} endpoint"""
        # Test with Slack integration
        integration_id = "slack"
        connection_config = {
            "name": "Test Slack Connection",
            "api_key": "test_api_key_123",
            "webhook_url": "https://hooks.slack.com/test"
        }
        
        success, response = self.run_test(
            "Integration Testing Routes - Test Connection",
            "POST",
            f"api/integration-testing/test-connection/{integration_id}",
            200,
            data=connection_config
        )
        
        if success:
            # Verify response structure
            expected_fields = ['test_result', 'status', 'integration_id', 'tested_at']
            if all(field in response for field in expected_fields):
                print(f"   ✅ Connection test structure valid")
                
                test_result = response.get('test_result')
                status = response.get('status')
                
                if test_result in ['success', 'failed']:
                    print(f"   ✅ Test result valid: {test_result}")
                else:
                    print(f"   ⚠️ Unexpected test result: {test_result}")
                
                if 'response_time_ms' in response:
                    print(f"   ✅ Performance metrics included")
                else:
                    print(f"   ⚠️ Performance metrics missing")
                    
            else:
                print(f"   ⚠️ Connection test missing expected fields")
        
        return success

    def test_collaboration_stats(self):
        """Test /api/collaboration/stats endpoint"""
        success, response = self.run_test(
            "Collaboration Routes - Stats",
            "GET",
            "api/collaboration/stats",
            200
        )
        
        if success:
            # Verify response structure
            expected_fields = ['collaboration_stats', 'timestamp']
            if all(field in response for field in expected_fields):
                print(f"   ✅ Collaboration stats structure valid")
                
                stats = response.get('collaboration_stats', {})
                if isinstance(stats, dict):
                    print(f"   ✅ Stats data is properly formatted")
                    
                    # Check for common stats fields
                    if any(key in stats for key in ['active_connections', 'total_rooms', 'messages_sent']):
                        print(f"   ✅ Stats contain meaningful data")
                    else:
                        print(f"   ⚠️ Stats may be empty or incomplete")
                else:
                    print(f"   ⚠️ Stats data not properly formatted")
                    
            else:
                print(f"   ⚠️ Collaboration stats missing expected fields")
        
        return success

    def test_collaboration_workflow_collaborators(self):
        """Test /api/collaboration/workflow/{workflow_id}/collaborators endpoint"""
        # First create a workflow to test with
        if not self.created_workflow_id:
            self.create_test_workflow()
        
        if not self.created_workflow_id:
            print("   ❌ Skipping - No workflow ID available")
            return False
            
        success, response = self.run_test(
            "Collaboration Routes - Workflow Collaborators",
            "GET",
            f"api/collaboration/workflow/{self.created_workflow_id}/collaborators",
            200
        )
        
        if success:
            # Verify response structure
            expected_fields = ['workflow_id', 'collaborators', 'total']
            if all(field in response for field in expected_fields):
                print(f"   ✅ Collaborators response structure valid")
                
                workflow_id = response.get('workflow_id')
                collaborators = response.get('collaborators', [])
                total = response.get('total', 0)
                
                if workflow_id == self.created_workflow_id:
                    print(f"   ✅ Workflow ID matches request")
                else:
                    print(f"   ⚠️ Workflow ID mismatch")
                
                if isinstance(collaborators, list) and len(collaborators) == total:
                    print(f"   ✅ Collaborators data consistent")
                else:
                    print(f"   ⚠️ Collaborators data inconsistent")
                    
            else:
                print(f"   ⚠️ Collaborators response missing expected fields")
        
        return success

    def create_test_workflow(self):
        """Helper method to create a test workflow"""
        workflow_data = {
            "name": f"Test Workflow for Collaboration {datetime.now().strftime('%H%M%S')}",
            "description": "A test workflow for collaboration testing",
            "nodes": [
                {
                    "id": "node1",
                    "type": "trigger",
                    "name": "Webhook Trigger",
                    "config": {"url": "/webhook/test"}
                }
            ],
            "connections": [],
            "triggers": [
                {
                    "type": "webhook",
                    "conditions": {"path": "/webhook/test"}
                }
            ]
        }
        
        success, response = self.run_test(
            "Helper - Create Test Workflow",
            "POST",
            "api/workflows",
            200,
            data=workflow_data
        )
        
        if success and 'id' in response:
            self.created_workflow_id = response['id']
            print(f"   ✅ Test workflow created: {self.created_workflow_id}")
            return True
        return False

    def test_additional_analytics_endpoints(self):
        """Test additional analytics endpoints for comprehensive coverage"""
        # Test workflow performance analytics
        if self.created_workflow_id:
            success1, response1 = self.run_test(
                "Analytics - Workflow Performance",
                "GET",
                f"api/analytics/workflow/{self.created_workflow_id}/performance",
                200,
                params={"period": "7d"}
            )
            
            if success1:
                expected_fields = ['workflow_id', 'period', 'summary', 'timeline', 'performance_trends']
                if all(field in response1 for field in expected_fields):
                    print(f"   ✅ Workflow performance analytics structure valid")
                else:
                    print(f"   ⚠️ Workflow performance analytics incomplete")
        else:
            success1 = False
            print("   ❌ Skipping workflow performance test - no workflow available")
        
        # Test workflow comparison analytics
        if self.created_workflow_id:
            success2, response2 = self.run_test(
                "Analytics - Workflow Comparison",
                "GET",
                "api/analytics/workflows/comparison",
                200,
                params={"workflow_ids": [self.created_workflow_id]}
            )
            
            if success2:
                expected_fields = ['workflow_comparison', 'summary']
                if all(field in response2 for field in expected_fields):
                    print(f"   ✅ Workflow comparison analytics structure valid")
                else:
                    print(f"   ⚠️ Workflow comparison analytics incomplete")
        else:
            success2 = False
            print("   ❌ Skipping workflow comparison test - no workflow available")
        
        return success1 or success2

    def test_template_advanced_features(self):
        """Test advanced template features"""
        # Test template search
        success1, response1 = self.run_test(
            "Templates - Advanced Search",
            "GET",
            "api/templates/search",
            200,
            params={"query": "automation", "category": "productivity", "difficulty": "beginner"}
        )
        
        if success1:
            expected_fields = ['templates', 'filters']
            if all(field in response1 for field in expected_fields):
                print(f"   ✅ Template search structure valid")
            else:
                print(f"   ⚠️ Template search structure incomplete")
        
        # Test template deployment if we have a template
        success2 = False
        if self.created_template_id:
            deployment_config = {
                "name": "Deployed Test Template",
                "description": "Deployed from template for testing",
                "variables": {
                    "email": "test@example.com",
                    "webhook_url": "https://example.com/webhook"
                }
            }
            
            success2, response2 = self.run_test(
                "Templates - Deploy Template",
                "POST",
                f"api/templates/{self.created_template_id}/deploy",
                200,
                data=deployment_config
            )
            
            if success2:
                if 'workflow_id' in response2:
                    print(f"   ✅ Template deployment successful")
                else:
                    print(f"   ⚠️ Template deployment response incomplete")
        
        return success1 or success2

    def test_integration_testing_advanced(self):
        """Test advanced integration testing features"""
        # Test integration test suite
        integration_id = "github"
        
        success1, response1 = self.run_test(
            "Integration Testing - Get Test Suite",
            "GET",
            f"api/integration-testing/test-suite/{integration_id}",
            200
        )
        
        if success1:
            expected_fields = ['integration_id', 'integration_name', 'test_suite', 'total_tests']
            if all(field in response1 for field in expected_fields):
                print(f"   ✅ Test suite structure valid")
                
                test_suite = response1.get('test_suite', [])
                if test_suite and isinstance(test_suite, list):
                    print(f"   ✅ Test suite contains {len(test_suite)} tests")
                else:
                    print(f"   ⚠️ Test suite empty or invalid")
            else:
                print(f"   ⚠️ Test suite response incomplete")
        
        # Test comprehensive test suite execution
        connection_config = {
            "access_token": "test_token_123",
            "repository": "test/repo"
        }
        
        success2, response2 = self.run_test(
            "Integration Testing - Run Test Suite",
            "POST",
            f"api/integration-testing/run-test-suite/{integration_id}",
            200,
            data=connection_config
        )
        
        if success2:
            expected_fields = ['integration_id', 'overall_success', 'statistics', 'test_results']
            if all(field in response2 for field in expected_fields):
                print(f"   ✅ Test suite execution structure valid")
                
                statistics = response2.get('statistics', {})
                if 'total_tests' in statistics and 'success_rate' in statistics:
                    print(f"   ✅ Test execution statistics complete")
                else:
                    print(f"   ⚠️ Test execution statistics incomplete")
            else:
                print(f"   ⚠️ Test suite execution response incomplete")
        
        return success1 or success2

def main():
    print("🚀 Starting New Features Backend API Tests")
    print("=" * 60)
    
    # Initialize tester
    tester = NewFeaturesAPITester("https://thorough-testing.preview.emergentagent.com")
    
    # Run authentication test first
    print("\n📝 AUTHENTICATION TESTS")
    print("-" * 30)
    
    if not tester.test_signup_endpoint():
        print("❌ Signup failed, cannot proceed with authenticated tests")
        return 1
    
    # Test Analytics Routes
    print("\n📊 ANALYTICS ROUTES TESTS")
    print("-" * 30)
    tester.test_analytics_dashboard_overview()
    tester.test_analytics_integrations_usage()
    tester.test_additional_analytics_endpoints()
    
    # Test Template Routes
    print("\n📋 TEMPLATE ROUTES TESTS")
    print("-" * 30)
    tester.test_templates_list()
    tester.test_templates_create()
    tester.test_template_advanced_features()
    
    # Test Integration Testing Routes
    print("\n🔗 INTEGRATION TESTING ROUTES TESTS")
    print("-" * 30)
    tester.test_integration_testing_connection()
    tester.test_integration_testing_advanced()
    
    # Test Collaboration Routes
    print("\n👥 COLLABORATION ROUTES TESTS")
    print("-" * 30)
    tester.test_collaboration_stats()
    tester.test_collaboration_workflow_collaborators()
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 FINAL RESULTS - NEW FEATURES TEST")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    success_rate = (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")
    
    if success_rate >= 85:
        print("✅ New backend features tests highly successful!")
        return 0
    elif success_rate >= 70:
        print("✅ New backend features tests mostly successful!")
        return 0
    elif success_rate >= 50:
        print("⚠️ New backend features tests partially successful - some issues found")
        return 0
    else:
        print("❌ New backend features tests failed - major issues found")
        return 1

if __name__ == "__main__":
    sys.exit(main())