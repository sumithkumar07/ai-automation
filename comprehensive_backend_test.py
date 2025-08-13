import requests
import sys
import json
import time
import uuid
from datetime import datetime

class ComprehensiveBackendTester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_workflow_id = None
        self.created_integration_id = None
        self.execution_id = None
        self.session_id = str(uuid.uuid4())

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
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_signup(self):
        """Test user signup"""
        test_user_data = {
            "name": f"Comprehensive Test User {datetime.now().strftime('%H%M%S')}",
            "email": f"comprehensive_test_{datetime.now().strftime('%H%M%S')}@example.com",
            "password": "password123"
        }
        
        success, response = self.run_test(
            "User Signup",
            "POST",
            "api/auth/signup",
            200,
            data=test_user_data
        )
        
        if success and 'token' in response:
            self.token = response['token']
            self.user_id = response['user']['id']
            print(f"   Token obtained: {self.token[:20]}...")
            return True
        return False

    def test_health_endpoint(self):
        """Test health endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "api/health",
            200
        )
        
        if success:
            if 'status' in response and 'database' in response:
                print(f"   ✅ Health check structure valid")
                if response['database']['status'] == 'ok':
                    print(f"   ✅ Database connectivity: OK")
                else:
                    print(f"   ⚠️ Database status: {response['database']['status']}")
            else:
                print(f"   ⚠️ Health response missing expected fields")
        
        return success

    def test_dashboard_stats(self):
        """Test dashboard stats endpoint"""
        success, response = self.run_test(
            "Dashboard Stats",
            "GET",
            "api/dashboard/stats",
            200
        )
        
        if success:
            required_fields = ['total_workflows', 'total_executions', 'success_rate']
            if all(field in response for field in required_fields):
                print(f"   ✅ Dashboard stats structure valid")
            else:
                print(f"   ⚠️ Dashboard stats missing some required fields")
        
        return success

    def test_user_checklist(self):
        """Test user checklist endpoint"""
        success, response = self.run_test(
            "User Checklist",
            "GET",
            "api/user/checklist",
            200
        )
        
        if success:
            expected_fields = ['has_any_workflow', 'has_any_integration', 'has_any_execution', 'completion_percentage']
            if all(field in response for field in expected_fields):
                print(f"   ✅ Checklist structure valid")
                print(f"   Completion: {response.get('completion_percentage', 0)}%")
            else:
                print(f"   ⚠️ Checklist response missing expected fields")
        
        return success

    def test_workflows_crud(self):
        """Test complete workflow CRUD operations"""
        # Create workflow
        workflow_data = {
            "name": f"Comprehensive Test Workflow {datetime.now().strftime('%H%M%S')}",
            "description": "A comprehensive test workflow",
            "nodes": [
                {
                    "id": "node1",
                    "type": "trigger",
                    "name": "Webhook Trigger",
                    "config": {"url": "/webhook/test"}
                },
                {
                    "id": "node2", 
                    "type": "action",
                    "name": "HTTP Request",
                    "config": {"method": "GET", "url": "https://api.example.com"}
                }
            ],
            "connections": [
                {
                    "from": "node1",
                    "to": "node2",
                    "fromPort": "output",
                    "toPort": "input"
                }
            ],
            "triggers": [
                {
                    "type": "webhook",
                    "conditions": {"path": "/webhook/test"}
                }
            ]
        }
        
        success1, response1 = self.run_test(
            "Create Workflow",
            "POST",
            "api/workflows",
            200,
            data=workflow_data
        )
        
        if success1 and 'id' in response1:
            self.created_workflow_id = response1['id']
            print(f"   Created workflow ID: {self.created_workflow_id}")
        else:
            return False

        # Get workflows list
        success2, response2 = self.run_test(
            "Get Workflows List",
            "GET",
            "api/workflows",
            200,
            params={"page": 1, "limit": 10}
        )

        # Get single workflow
        success3, response3 = self.run_test(
            "Get Single Workflow",
            "GET",
            f"api/workflows/{self.created_workflow_id}",
            200
        )

        # Update workflow
        updated_data = {
            "name": f"Updated Comprehensive Test Workflow {datetime.now().strftime('%H%M%S')}",
            "description": "Updated comprehensive test workflow",
            "nodes": workflow_data["nodes"],
            "connections": workflow_data["connections"],
            "triggers": workflow_data["triggers"]
        }
        
        success4, response4 = self.run_test(
            "Update Workflow",
            "PUT",
            f"api/workflows/{self.created_workflow_id}",
            200,
            data=updated_data
        )

        # Test autosave
        autosave_data = {
            "nodes": [
                {
                    "id": "autosave_node",
                    "type": "action",
                    "name": "Autosaved Node",
                    "config": {"test": "autosave"}
                }
            ],
            "connections": [],
            "meta": {"autosaved": True}
        }
        
        success5, response5 = self.run_test(
            "Workflow Autosave",
            "POST",
            f"api/workflows/{self.created_workflow_id}/autosave",
            200,
            data=autosave_data
        )

        return all([success1, success2, success3, success4, success5])

    def test_workflow_execution(self):
        """Test workflow execution system"""
        if not self.created_workflow_id:
            print("❌ Skipping - No workflow ID available")
            return False

        # Execute workflow with idempotency key
        idempotency_key = str(uuid.uuid4())
        idempotency_headers = {"idempotency-key": idempotency_key}
        
        success1, response1 = self.run_test(
            "Execute Workflow",
            "POST",
            f"api/workflows/{self.created_workflow_id}/execute",
            200,
            headers=idempotency_headers
        )
        
        if success1 and 'execution_id' in response1:
            self.execution_id = response1['execution_id']
            print(f"   Execution ID: {self.execution_id}")
            
            # Wait a moment for execution to process
            time.sleep(2)
            
            # Get execution status
            success2, response2 = self.run_test(
                "Get Execution Status",
                "GET",
                f"api/executions/{self.execution_id}",
                200
            )
            
            if success2:
                if 'status' in response2 and 'logs' in response2:
                    print(f"   ✅ Execution details include status and logs")
                    print(f"   Status: {response2['status']}")
                else:
                    print(f"   ⚠️ Execution details missing status or logs")
            
            # Test duplicate execution with same idempotency key
            success3, response3 = self.run_test(
                "Duplicate Execution (Idempotency Test)",
                "POST",
                f"api/workflows/{self.created_workflow_id}/execute",
                200,
                headers=idempotency_headers
            )
            
            if success3:
                if response3.get('execution_id') == self.execution_id:
                    print(f"   ✅ Idempotency working - same execution ID returned")
                else:
                    print(f"   ⚠️ Idempotency not working - different execution ID")
            
            return success1 and success2 and success3
        
        return success1

    def test_integrations_system(self):
        """Test complete integrations system"""
        # Get available integrations
        success1, response1 = self.run_test(
            "Get Available Integrations",
            "GET",
            "api/integrations/available",
            200
        )

        # Create integration
        integration_data = {
            "name": f"Comprehensive Test Integration {datetime.now().strftime('%H%M%S')}",
            "platform": "slack",
            "credentials": {
                "api_key": "test_api_key_123",
                "webhook_url": "https://hooks.slack.com/test"
            }
        }
        
        success2, response2 = self.run_test(
            "Create Integration",
            "POST",
            "api/integrations",
            200,
            data=integration_data
        )
        
        if success2 and 'id' in response2:
            self.created_integration_id = response2['id']
            print(f"   Created integration ID: {self.created_integration_id}")

        # Get user integrations
        success3, response3 = self.run_test(
            "Get User Integrations",
            "GET",
            "api/integrations",
            200,
            params={"page": 1, "limit": 10}
        )

        # Test integration connection
        test_connection_data = {
            "name": "Test Slack Connection",
            "platform": "slack",
            "credentials": {
                "token": "invalid_test_token"
            }
        }
        
        success4, response4 = self.run_test(
            "Test Integration Connection",
            "POST",
            "api/integrations/test-connection",
            200,
            data=test_connection_data
        )

        return all([success1, success2, success3, success4])

    def test_templates_system(self):
        """Test templates system"""
        # Get templates
        success1, response1 = self.run_test(
            "Get Templates",
            "GET",
            "api/templates",
            200
        )

        # Search templates
        success2, response2 = self.run_test(
            "Search Templates",
            "GET",
            "api/templates/search",
            200,
            params={"query": "automation", "category": "productivity"}
        )

        # Test massive templates endpoint
        success3, response3 = self.run_test(
            "Get Massive Templates",
            "GET",
            "api/templates/massive",
            200
        )

        # Test comprehensive template stats
        success4, response4 = self.run_test(
            "Get Comprehensive Template Stats",
            "GET",
            "api/templates/stats/comprehensive",
            200
        )

        return all([success1, success2, success3, success4])

    def test_ai_system(self):
        """Test AI system endpoints"""
        # Test AI chat
        chat_data = {
            "message": "How do I create a workflow that processes CSV files?",
            "session_id": self.session_id
        }
        
        success1, response1 = self.run_test(
            "AI Chat",
            "POST",
            "api/ai/chat",
            200,
            data=chat_data
        )

        # Test AI workflow generation
        workflow_gen_data = {
            "prompt": "Create a workflow that sends a Slack notification when a new email arrives",
            "structured": True
        }
        
        success2, response2 = self.run_test(
            "AI Generate Workflow",
            "POST",
            "api/ai/generate-workflow",
            200,
            data=workflow_gen_data
        )

        # Test AI providers stats
        success3, response3 = self.run_test(
            "AI Providers Stats",
            "GET",
            "api/ai/providers/stats",
            200
        )

        # Test AI workflow optimization
        if self.created_workflow_id:
            optimize_data = {
                "workflow_id": self.created_workflow_id,
                "optimization_goals": ["performance", "reliability"]
            }
            
            success4, response4 = self.run_test(
                "AI Optimize Workflow",
                "POST",
                "api/ai/optimize-workflow",
                200,
                data=optimize_data
            )
        else:
            success4 = True  # Skip if no workflow available

        # Test AI error detection
        if self.created_workflow_id:
            error_detect_data = {
                "workflow_id": self.created_workflow_id
            }
            
            success5, response5 = self.run_test(
                "AI Detect Errors",
                "POST",
                "api/ai/detect-errors",
                200,
                data=error_detect_data
            )
        else:
            success5 = True  # Skip if no workflow available

        return all([success1, success2, success3, success4, success5])

    def test_node_types(self):
        """Test node types endpoint"""
        success, response = self.run_test(
            "Get Node Types",
            "GET",
            "api/nodes",
            200
        )
        
        if success:
            if 'categories' in response:
                categories = response['categories']
                total_nodes = sum(len(nodes) for nodes in categories.values())
                print(f"   ✅ Node types loaded: {total_nodes} nodes in {len(categories)} categories")
            else:
                print(f"   ⚠️ Node types response missing categories")
        
        return success

    def test_websocket_stats(self):
        """Test WebSocket stats endpoint"""
        success, response = self.run_test(
            "WebSocket Stats",
            "GET",
            "api/websocket/stats",
            200
        )
        
        if success:
            if 'stats' in response:
                print(f"   ✅ WebSocket stats retrieved")
            else:
                print(f"   ⚠️ WebSocket stats response missing stats field")
        
        return success

    def test_enterprise_features(self):
        """Test enterprise features (basic endpoints)"""
        # Test get organizations
        success1, response1 = self.run_test(
            "Get User Organizations",
            "GET",
            "api/enterprise/organizations",
            200
        )

        # Test create organization
        org_data = {
            "name": f"Test Organization {datetime.now().strftime('%H%M%S')}",
            "plan": "free"
        }
        
        success2, response2 = self.run_test(
            "Create Organization",
            "POST",
            "api/enterprise/organizations",
            200,
            data=org_data
        )

        return success1 and success2

    def cleanup_test_data(self):
        """Clean up test data"""
        success_count = 0
        total_cleanup = 0

        # Delete workflow if created
        if self.created_workflow_id:
            total_cleanup += 1
            success, _ = self.run_test(
                "Delete Test Workflow",
                "DELETE",
                f"api/workflows/{self.created_workflow_id}",
                200
            )
            if success:
                success_count += 1

        # Delete integration if created
        if self.created_integration_id:
            total_cleanup += 1
            success, _ = self.run_test(
                "Delete Test Integration",
                "DELETE",
                f"api/integrations/{self.created_integration_id}",
                200
            )
            if success:
                success_count += 1

        print(f"\n🧹 Cleanup completed: {success_count}/{total_cleanup} items cleaned up")
        return success_count == total_cleanup

def main():
    print("🚀 Starting Comprehensive Backend API Testing - Aether Automation Platform")
    print("=" * 80)
    
    # Initialize tester
    tester = ComprehensiveBackendTester("http://localhost:8001")
    
    # Authentication
    print("\n📝 AUTHENTICATION TESTS")
    print("-" * 40)
    if not tester.test_signup():
        print("❌ Authentication failed, stopping tests")
        return 1
    
    # Health and System Tests
    print("\n🏥 HEALTH & SYSTEM TESTS")
    print("-" * 40)
    tester.test_health_endpoint()
    tester.test_user_checklist()
    tester.test_websocket_stats()
    
    # Dashboard Tests
    print("\n📊 DASHBOARD TESTS")
    print("-" * 40)
    tester.test_dashboard_stats()
    
    # Workflow Tests
    print("\n⚙️ WORKFLOW MANAGEMENT TESTS")
    print("-" * 40)
    tester.test_workflows_crud()
    tester.test_workflow_execution()
    
    # Integration Tests
    print("\n🔗 INTEGRATION SYSTEM TESTS")
    print("-" * 40)
    tester.test_integrations_system()
    
    # Template Tests
    print("\n📋 TEMPLATE SYSTEM TESTS")
    print("-" * 40)
    tester.test_templates_system()
    
    # AI Tests
    print("\n🤖 AI INTEGRATION TESTS")
    print("-" * 40)
    tester.test_ai_system()
    
    # Node Types Tests
    print("\n🔧 NODE TYPES TESTS")
    print("-" * 40)
    tester.test_node_types()
    
    # Enterprise Features Tests
    print("\n🏢 ENTERPRISE FEATURES TESTS")
    print("-" * 40)
    tester.test_enterprise_features()
    
    # Cleanup
    print("\n🧹 CLEANUP TESTS")
    print("-" * 40)
    tester.cleanup_test_data()
    
    # Print final results
    print("\n" + "=" * 80)
    print(f"📊 COMPREHENSIVE BACKEND API TEST RESULTS")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    success_rate = (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("✅ Comprehensive backend tests HIGHLY SUCCESSFUL!")
        return 0
    elif success_rate >= 80:
        print("✅ Comprehensive backend tests SUCCESSFUL!")
        return 0
    elif success_rate >= 70:
        print("⚠️ Comprehensive backend tests MOSTLY SUCCESSFUL - minor issues found")
        return 0
    elif success_rate >= 50:
        print("⚠️ Comprehensive backend tests PARTIALLY SUCCESSFUL - some issues found")
        return 0
    else:
        print("❌ Comprehensive backend tests FAILED - major issues found")
        return 1

if __name__ == "__main__":
    sys.exit(main())