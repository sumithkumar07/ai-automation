import requests
import sys
import json
import time
import uuid
from datetime import datetime

class AetherAutomationAPITester:
    def __init__(self, base_url="https://subscription-model.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_workflow_id = None
        self.created_integration_id = None
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

    def test_signup(self):
        """Test user signup"""
        test_user_data = {
            "email": f"test_{datetime.now().strftime('%H%M%S')}@example.com",
            "password": "password123",
            "first_name": f"Test",
            "last_name": f"User {datetime.now().strftime('%H%M%S')}"
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
            print(f"   Token obtained: {self.token[:20]}...")
            return True
        return False

    def test_login(self):
        """Test user login with existing test user"""
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        success, response = self.run_test(
            "User Login",
            "POST",
            "api/auth/login",
            200,
            data=login_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user']['id']
            print(f"   Token obtained: {self.token[:20]}...")
            return True
        return False

    def test_dashboard_stats(self):
        """Test dashboard stats endpoint"""
        success, response = self.run_test(
            "Dashboard Stats",
            "GET",
            "api/dashboard/stats",
            200
        )
        return success

    def test_get_workflows(self):
        """Test get workflows endpoint"""
        success, response = self.run_test(
            "Get Workflows",
            "GET",
            "api/workflows",
            200
        )
        return success

    def test_create_workflow(self):
        """Test create workflow endpoint"""
        workflow_data = {
            "name": f"Test Workflow {datetime.now().strftime('%H%M%S')}",
            "description": "A test workflow created by automated testing",
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
        
        success, response = self.run_test(
            "Create Workflow",
            "POST",
            "api/workflows",
            200,
            data=workflow_data
        )
        
        if success and 'id' in response:
            self.created_workflow_id = response['id']
            print(f"   Created workflow ID: {self.created_workflow_id}")
            return True
        return False

    def test_get_workflow(self):
        """Test get single workflow endpoint"""
        if not self.created_workflow_id:
            print("❌ Skipping - No workflow ID available")
            return False
            
        success, response = self.run_test(
            "Get Single Workflow",
            "GET",
            f"api/workflows/{self.created_workflow_id}",
            200
        )
        return success

    def test_update_workflow(self):
        """Test update workflow endpoint"""
        if not self.created_workflow_id:
            print("❌ Skipping - No workflow ID available")
            return False
            
        updated_data = {
            "name": f"Updated Test Workflow {datetime.now().strftime('%H%M%S')}",
            "description": "Updated test workflow description",
            "nodes": [
                {
                    "id": "node1",
                    "type": "trigger",
                    "name": "Updated Webhook Trigger",
                    "config": {"url": "/webhook/updated"}
                }
            ],
            "connections": [],
            "triggers": [
                {
                    "type": "webhook",
                    "conditions": {"path": "/webhook/updated"}
                }
            ]
        }
        
        success, response = self.run_test(
            "Update Workflow",
            "PUT",
            f"api/workflows/{self.created_workflow_id}",
            200,
            data=updated_data
        )
        return success

    def test_execute_workflow(self):
        """Test workflow execution endpoint"""
        if not self.created_workflow_id:
            print("❌ Skipping - No workflow ID available")
            return False
            
        success, response = self.run_test(
            "Execute Workflow",
            "POST",
            f"api/workflows/{self.created_workflow_id}/execute",
            200
        )
        return success

    def test_get_templates(self):
        """Test get templates endpoint"""
        success, response = self.run_test(
            "Get Templates",
            "GET",
            "api/templates",
            200
        )
        return success

    def test_get_integrations(self):
        """Test get user integrations endpoint"""
        success, response = self.run_test(
            "Get User Integrations",
            "GET",
            "api/integrations",
            200
        )
        return success

    def test_get_available_integrations(self):
        """Test get available integrations endpoint"""
        success, response = self.run_test(
            "Get Available Integrations",
            "GET",
            "api/integrations",
            200
        )
        
        if success:
            # Verify we have 15+ integrations
            if isinstance(response, list):
                integration_count = len(response)
                print(f"   ✅ Found {integration_count} integrations")
                
                if integration_count >= 15:
                    print(f"   ✅ Integration count meets requirements (15+)")
                    
                    # Check for specific integrations mentioned in review
                    integration_names = [integration.get('name', '').lower() for integration in response]
                    required_integrations = ['slack', 'gmail', 'github', 'groq', 'stripe']
                    found_integrations = [name for name in required_integrations if any(name in int_name for int_name in integration_names)]
                    
                    print(f"   ✅ Found required integrations: {', '.join(found_integrations)}")
                    
                    if len(found_integrations) >= 4:
                        print(f"   ✅ Key integrations present")
                    else:
                        print(f"   ⚠️ Some key integrations missing")
                else:
                    print(f"   ⚠️ Integration count below requirements: {integration_count}")
            else:
                print(f"   ⚠️ Integrations response not a list")
        
        return success

    def test_create_integration(self):
        """Test create integration endpoint"""
        integration_data = {
            "name": f"Test Integration {datetime.now().strftime('%H%M%S')}",
            "platform": "slack",
            "credentials": {
                "api_key": "test_api_key_123",
                "webhook_url": "https://hooks.slack.com/test"
            }
        }
        
        success, response = self.run_test(
            "Create Integration",
            "POST",
            "api/integrations",
            200,
            data=integration_data
        )
        return success

    def test_get_node_types(self):
        """Test get node types endpoint"""
        success, response = self.run_test(
            "Get Node Types",
            "GET",
            "api/workflows/node-types",
            200
        )
        
        if success:
            # Verify we have the expected 25 nodes across 4 categories
            if 'categories' in response and 'stats' in response:
                stats = response['stats']
                total_nodes = stats.get('total_nodes', 0)
                categories = stats.get('categories', 0)
                print(f"   ✅ Found {total_nodes} nodes across {categories} categories")
                
                if total_nodes >= 25 and categories >= 4:
                    print(f"   ✅ Node types meet requirements (25+ nodes, 4+ categories)")
                else:
                    print(f"   ⚠️ Node types below requirements: {total_nodes} nodes, {categories} categories")
            else:
                print(f"   ⚠️ Node types response missing expected structure")
        
        return success

    def test_ai_generate_workflow(self):
        """Test AI workflow generation endpoint"""
        prompt_data = {
            "description": "Create a workflow that sends a Slack notification when a new email arrives"
        }
        
        success, response = self.run_test(
            "AI Generate Workflow",
            "POST",
            "api/ai/generate-workflow",
            200,
            data=prompt_data
        )
        
        if success:
            # Verify GROQ AI integration is working
            if 'workflow' in response and 'confidence' in response:
                confidence = response.get('confidence', 0)
                print(f"   ✅ AI workflow generated with confidence: {confidence}")
                
                workflow = response['workflow']
                if 'nodes' in workflow and 'connections' in workflow:
                    node_count = len(workflow['nodes'])
                    connection_count = len(workflow['connections'])
                    print(f"   ✅ Generated workflow has {node_count} nodes and {connection_count} connections")
                    
                    # Check if GROQ AI is actually working (not just mock)
                    if confidence > 0.8:
                        print(f"   ✅ GROQ AI appears to be working (high confidence)")
                    else:
                        print(f"   ⚠️ GROQ AI may be using fallback (low confidence)")
                else:
                    print(f"   ⚠️ Generated workflow missing nodes or connections")
            else:
                print(f"   ⚠️ AI response missing expected fields")
        
        return success

    def test_ai_chat(self):
        """Test AI chat endpoint"""
        success, response = self.run_test(
            "AI Chat",
            "POST",
            "api/ai/chat",
            200,
            params={"message": "How do I create a workflow that processes CSV files?"}
        )
        return success

    def test_delete_workflow(self):
        """Test delete workflow endpoint"""
        if not self.created_workflow_id:
            print("❌ Skipping - No workflow ID available")
            return False
            
        success, response = self.run_test(
            "Delete Workflow",
            "DELETE",
            f"api/workflows/{self.created_workflow_id}",
            200
        )
        return success

    # NEW ENHANCED FEATURE TESTS
    
    def test_health_endpoint(self):
        """Test health endpoint for database connectivity"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "api/health",
            200
        )
        
        if success:
            # Verify health response structure
            if 'status' in response and 'database' in response:
                print(f"   ✅ Health check structure valid")
                if response['database']['status'] == 'ok':
                    print(f"   ✅ Database connectivity: OK")
                else:
                    print(f"   ⚠️ Database status: {response['database']['status']}")
            else:
                print(f"   ⚠️ Health response missing expected fields")
        
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
            # Verify checklist structure
            expected_fields = ['has_any_workflow', 'has_any_integration', 'has_any_execution', 'completion_percentage']
            if all(field in response for field in expected_fields):
                print(f"   ✅ Checklist structure valid")
                print(f"   Completion: {response.get('completion_percentage', 0)}%")
            else:
                print(f"   ⚠️ Checklist response missing expected fields")
        
        return success

    def test_workflows_pagination(self):
        """Test workflows endpoint with pagination"""
        # Test with pagination parameters
        success1, response1 = self.run_test(
            "Workflows with Pagination",
            "GET",
            "api/workflows",
            200,
            params={"page": 1, "limit": 5}
        )
        
        if success1:
            if 'pagination' in response1:
                print(f"   ✅ Pagination metadata present")
                pagination = response1['pagination']
                if all(key in pagination for key in ['page', 'limit', 'total', 'pages']):
                    print(f"   ✅ Pagination structure valid")
                else:
                    print(f"   ⚠️ Pagination missing some fields")
            else:
                print(f"   ⚠️ Pagination metadata missing")
        
        return success1

    def test_integrations_pagination(self):
        """Test integrations endpoint with pagination"""
        success, response = self.run_test(
            "Integrations with Pagination",
            "GET",
            "api/integrations",
            200,
            params={"page": 1, "limit": 10}
        )
        
        if success:
            if 'pagination' in response:
                print(f"   ✅ Integration pagination metadata present")
            else:
                print(f"   ⚠️ Integration pagination metadata missing")
        
        return success

    def test_integration_test_connection(self):
        """Test integration connection testing"""
        # Test Slack connection (will fail but should return proper error)
        slack_test_data = {
            "name": "Test Slack Integration",
            "platform": "slack",
            "credentials": {
                "token": "invalid_test_token"
            }
        }
        
        success1, response1 = self.run_test(
            "Test Slack Connection",
            "POST",
            "api/integrations/test-connection",
            200,
            data=slack_test_data
        )
        
        if success1:
            if 'status' in response1:
                print(f"   Connection test status: {response1['status']}")
                print(f"   Detail: {response1.get('detail', 'No detail')}")
            else:
                print(f"   ⚠️ Connection test response missing status")
        
        # Test GitHub connection
        github_test_data = {
            "name": "Test GitHub Integration",
            "platform": "github",
            "credentials": {
                "token": "invalid_test_token"
            }
        }
        
        success2, response2 = self.run_test(
            "Test GitHub Connection",
            "POST",
            "api/integrations/test-connection",
            200,
            data=github_test_data
        )
        
        # Test unknown platform
        unknown_test_data = {
            "name": "Test Unknown Integration",
            "platform": "unknown_platform",
            "credentials": {
                "api_key": "test_key"
            }
        }
        
        success3, response3 = self.run_test(
            "Test Unknown Platform Connection",
            "POST",
            "api/integrations/test-connection",
            200,
            data=unknown_test_data
        )
        
        return success1 and success2 and success3

    def test_workflow_autosave(self):
        """Test workflow autosave functionality"""
        if not self.created_workflow_id:
            print("❌ Skipping - No workflow ID available")
            return False
        
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
        
        success, response = self.run_test(
            "Workflow Autosave",
            "POST",
            f"api/workflows/{self.created_workflow_id}/autosave",
            200,
            data=autosave_data
        )
        
        if success:
            if 'saved' in response and response['saved']:
                print(f"   ✅ Autosave successful")
                if 'timestamp' in response:
                    print(f"   Timestamp: {response['timestamp']}")
            else:
                print(f"   ⚠️ Autosave response unexpected")
        
        return success

    def test_template_search(self):
        """Test template search with query parameters"""
        # Test search with query
        success1, response1 = self.run_test(
            "Template Search with Query",
            "GET",
            "api/templates/search",
            200,
            params={"query": "automation", "category": "productivity"}
        )
        
        if success1:
            if 'templates' in response1 and 'filters' in response1:
                print(f"   ✅ Search response structure valid")
                print(f"   Found {len(response1['templates'])} templates")
                filters = response1['filters']
                if filters.get('query') == 'automation' and filters.get('category') == 'productivity':
                    print(f"   ✅ Search filters applied correctly")
                else:
                    print(f"   ⚠️ Search filters not applied correctly")
            else:
                print(f"   ⚠️ Search response missing expected fields")
        
        # Test search with difficulty filter
        success2, response2 = self.run_test(
            "Template Search with Difficulty",
            "GET",
            "api/templates/search",
            200,
            params={"difficulty": "beginner"}
        )
        
        return success1 and success2

    def test_enhanced_ai_structured_output(self):
        """Test AI workflow generation with structured output"""
        structured_request = {
            "prompt": "Create a simple workflow that sends an email notification",
            "structured": True
        }
        
        success, response = self.run_test(
            "AI Structured Workflow Generation",
            "POST",
            "api/ai/generate-workflow",
            200,
            data=structured_request
        )
        
        if success:
            if 'type' in response:
                print(f"   Response type: {response['type']}")
                if response['type'] == 'workflow' and 'data' in response:
                    workflow_data = response['data']
                    required_fields = ['name', 'description', 'nodes', 'connections', 'triggers']
                    if all(field in workflow_data for field in required_fields):
                        print(f"   ✅ Structured workflow data valid")
                    else:
                        print(f"   ⚠️ Structured workflow missing some fields")
                elif response['type'] == 'suggestion':
                    print(f"   ✅ Fallback to suggestion mode")
            else:
                print(f"   ⚠️ AI response missing type field")
        
        return success

    def test_ai_suggest_integrations(self):
        """Test AI integration suggestions endpoint"""
        success, response = self.run_test(
            "AI Suggest Integrations",
            "POST",
            "api/ai/suggest-integrations",
            200,
            params={"description": "I want to send notifications when someone submits a form"}
        )
        
        if success:
            if 'suggestions' in response:
                suggestions = response['suggestions']
                print(f"   ✅ AI suggested {len(suggestions)} integrations")
                
                # Check if GROQ AI is working
                ai_powered = response.get('ai_powered', False)
                if ai_powered:
                    print(f"   ✅ GROQ AI integration suggestions working")
                else:
                    print(f"   ⚠️ Using fallback integration suggestions")
            else:
                print(f"   ⚠️ Suggestions response missing expected fields")
        
        return success
        """Test AI chat with session memory"""
        # First message in session
        success1, response1 = self.run_test(
            "AI Chat with Session - Message 1",
            "POST",
            "api/ai/chat",
            200,
            params={"message": "What is workflow automation?", "session_id": self.session_id}
        )
        
        if success1:
            if 'session_id' in response1 and response1['session_id'] == self.session_id:
                print(f"   ✅ Session ID maintained")
            else:
                print(f"   ⚠️ Session ID not maintained")
        
        # Second message in same session
        success2, response2 = self.run_test(
            "AI Chat with Session - Message 2",
            "POST",
            "api/ai/chat",
            200,
            params={"message": "Can you give me an example?", "session_id": self.session_id}
        )
        
        return success1 and success2

    def test_etag_support(self):
        """Test ETag support for caching"""
        # Test /api/nodes with ETag
        success1, response1 = self.run_test(
            "Node Types with ETag",
            "GET",
            "api/nodes",
            200
        )
        
        if success1:
            # Make second request with If-None-Match header
            etag_headers = {"If-None-Match": '"node-types-v2"'}
            success2, response2 = self.run_test(
                "Node Types with If-None-Match",
                "GET",
                "api/nodes",
                304,  # Expect 304 Not Modified
                headers=etag_headers
            )
            
            if success2:
                print(f"   ✅ ETag caching working for /api/nodes")
            else:
                print(f"   ⚠️ ETag caching not working for /api/nodes")
        
        # Test /api/integrations/available with ETag
        success3, response3 = self.run_test(
            "Available Integrations with ETag",
            "GET",
            "api/integrations/available",
            200
        )
        
        if success3:
            etag_headers = {"If-None-Match": '"available-integrations-v2"'}
            success4, response4 = self.run_test(
                "Available Integrations with If-None-Match",
                "GET",
                "api/integrations/available",
                304,
                headers=etag_headers
            )
            
            if success4:
                print(f"   ✅ ETag caching working for /api/integrations/available")
            else:
                print(f"   ⚠️ ETag caching not working for /api/integrations/available")
        
        return success1 and success3

    def test_enhanced_workflow_execution(self):
        """Test enhanced workflow execution with idempotency"""
        if not self.created_workflow_id:
            print("❌ Skipping - No workflow ID available")
            return False
        
        # Test execution with idempotency key
        idempotency_key = str(uuid.uuid4())
        idempotency_headers = {"idempotency-key": idempotency_key}
        
        success1, response1 = self.run_test(
            "Workflow Execution with Idempotency Key",
            "POST",
            f"api/workflows/{self.created_workflow_id}/execute",
            200,
            headers=idempotency_headers
        )
        
        if success1:
            execution_id = response1.get('execution_id')
            if execution_id:
                print(f"   Execution ID: {execution_id}")
                
                # Test duplicate execution with same idempotency key
                success2, response2 = self.run_test(
                    "Duplicate Execution with Same Idempotency Key",
                    "POST",
                    f"api/workflows/{self.created_workflow_id}/execute",
                    200,
                    headers=idempotency_headers
                )
                
                if success2:
                    if response2.get('execution_id') == execution_id:
                        print(f"   ✅ Idempotency working - same execution ID returned")
                    else:
                        print(f"   ⚠️ Idempotency not working - different execution ID")
                
                # Test getting execution status
                success3, response3 = self.run_test(
                    "Get Execution Status",
                    "GET",
                    f"api/executions/{execution_id}",
                    200
                )
                
                if success3:
                    if 'logs' in response3 and 'status' in response3:
                        print(f"   ✅ Execution details include logs and status")
                        print(f"   Status: {response3['status']}")
                    else:
                        print(f"   ⚠️ Execution details missing logs or status")
                
                return success1 and success2 and success3
        
        return success1

    def test_rate_limiting(self):
        """Test rate limiting middleware"""
        print(f"\n🔍 Testing Rate Limiting...")
        print(f"   Making multiple rapid requests to test rate limiting...")
        
        # Make multiple rapid requests to trigger rate limiting
        rate_limit_triggered = False
        
        for i in range(5):  # Make 5 rapid requests
            try:
                url = f"{self.base_url}/api/workflows"
                headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}
                
                workflow_data = {
                    "name": f"Rate Limit Test {i}",
                    "description": "Testing rate limiting",
                    "nodes": [],
                    "connections": [],
                    "triggers": []
                }
                
                response = requests.post(url, json=workflow_data, headers=headers, timeout=5)
                
                if response.status_code == 429:
                    print(f"   ✅ Rate limiting triggered on request {i+1}")
                    rate_limit_triggered = True
                    
                    # Check for proper rate limit headers
                    if 'Retry-After' in response.headers:
                        print(f"   ✅ Retry-After header present: {response.headers['Retry-After']}")
                    else:
                        print(f"   ⚠️ Retry-After header missing")
                    
                    break
                else:
                    print(f"   Request {i+1}: {response.status_code}")
                    
                time.sleep(0.1)  # Small delay between requests
                
            except Exception as e:
                print(f"   Error in rate limit test: {e}")
                break
        
        if rate_limit_triggered:
            self.tests_passed += 1
            print(f"✅ Rate limiting test passed")
        else:
            print(f"⚠️ Rate limiting not triggered (may need more requests)")
        
        self.tests_run += 1
        return rate_limit_triggered

    def test_error_standardization(self):
        """Test that all endpoints return StandardError format"""
        # Test invalid endpoint
        success1, response1 = self.run_test(
            "Invalid Endpoint Error Format",
            "GET",
            "api/invalid-endpoint",
            404
        )
        
        # Test unauthorized access
        temp_token = self.token
        self.token = None  # Remove token temporarily
        
        success2, response2 = self.run_test(
            "Unauthorized Error Format",
            "GET",
            "api/dashboard/stats",
            401
        )
        
        self.token = temp_token  # Restore token
        
        # Test invalid workflow ID
        success3, response3 = self.run_test(
            "Not Found Error Format",
            "GET",
            "api/workflows/invalid-id",
            404
        )
        
        # Check error format consistency
        error_format_valid = True
        for i, (success, response) in enumerate([(success1, response1), (success2, response2), (success3, response3)], 1):
            if success and isinstance(response, dict):
                if 'error_code' in response and 'detail' in response:
                    print(f"   ✅ Error {i} has StandardError format")
                else:
                    print(f"   ⚠️ Error {i} missing StandardError format")
                    error_format_valid = False
        
        return error_format_valid

def main():
    print("🚀 Starting Aether Automation API Tests - Enhanced Features")
    print("=" * 60)
    
    # Initialize tester
    tester = AetherAutomationAPITester("https://subscription-model.preview.emergentagent.com")
    
    # Run authentication tests
    print("\n📝 AUTHENTICATION TESTS")
    print("-" * 30)
    
    # Try signup first, if it fails try login
    if not tester.test_signup():
        print("Signup failed, trying login with test user...")
        if not tester.test_login():
            print("❌ Both signup and login failed, stopping tests")
            return 1
    
    # NEW ENHANCED FEATURE TESTS
    print("\n🏥 HEALTH & SYSTEM TESTS")
    print("-" * 30)
    tester.test_health_endpoint()
    tester.test_user_checklist()
    tester.test_error_standardization()
    
    print("\n📊 DASHBOARD & WORKFLOW TESTS")
    print("-" * 30)
    tester.test_dashboard_stats()
    tester.test_workflows_pagination()
    tester.test_create_workflow()
    tester.test_get_workflow()
    tester.test_update_workflow()
    tester.test_workflow_autosave()
    tester.test_enhanced_workflow_execution()
    
    print("\n🔗 INTEGRATION TESTS")
    print("-" * 30)
    tester.test_integrations_pagination()
    tester.test_get_available_integrations()
    tester.test_create_integration()
    tester.test_integration_test_connection()
    
    print("\n📋 TEMPLATE & NODE TESTS")
    print("-" * 30)
    tester.test_get_templates()
    tester.test_template_search()
    tester.test_get_node_types()
    
    print("\n🤖 AI TESTS")
    print("-" * 30)
    tester.test_ai_generate_workflow()
    tester.test_enhanced_ai_structured_output()
    tester.test_ai_chat()
    tester.test_ai_chat_with_session()
    
    print("\n⚡ PERFORMANCE & CACHING TESTS")
    print("-" * 30)
    tester.test_etag_support()
    tester.test_rate_limiting()
    
    print("\n🗑️ CLEANUP TESTS")
    print("-" * 30)
    tester.test_delete_workflow()
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 FINAL RESULTS - ENHANCED FEATURES TEST")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    success_rate = (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")
    
    if success_rate >= 85:
        print("✅ Enhanced backend features tests highly successful!")
        return 0
    elif success_rate >= 70:
        print("✅ Enhanced backend features tests mostly successful!")
        return 0
    elif success_rate >= 50:
        print("⚠️ Enhanced backend features tests partially successful - some issues found")
        return 0
    else:
        print("❌ Enhanced backend features tests failed - major issues found")
        return 1

if __name__ == "__main__":
    sys.exit(main())