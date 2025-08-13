import requests
import sys
import json
import time
import uuid
import asyncio
import websockets
from datetime import datetime

class EnhancedFeaturesAPITester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.ws_url = base_url.replace("http://", "ws://").replace("https://", "wss://")
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.organization_id = None
        self.workspace_id = None

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
                    if isinstance(response_data, dict) and len(str(response_data)) < 500:
                        print(f"   Response: {response_data}")
                    return True, response_data
                except:
                    return True, response.text
            else:
                print(f"❌ Failed - Expected: {expected_status}, Got: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, None

        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return False, None

    def setup_authentication(self):
        """Setup authentication for testing"""
        print("🔐 Setting up authentication...")
        
        # Create test user
        signup_data = {
            "email": f"testuser_{int(time.time())}@example.com",
            "password": "testpassword123",
            "name": "Enhanced Features Test User"
        }
        
        success, response = self.run_test(
            "User Signup",
            "POST",
            "api/auth/signup",
            200,
            data=signup_data
        )
        
        if success and response:
            self.token = response.get('token')
            self.user_id = response.get('user', {}).get('id')
            print(f"✅ Authentication setup complete - User ID: {self.user_id}")
            return True
        
        print("❌ Authentication setup failed")
        return False

    # =======================================
    # WEBSOCKET REAL-TIME FEATURES TESTS
    # =======================================

    def test_websocket_stats(self):
        """Test WebSocket connection statistics endpoint"""
        success, response = self.run_test(
            "WebSocket Stats",
            "GET",
            "api/websocket/stats",
            200
        )
        
        if success and response:
            expected_fields = ['status', 'stats', 'timestamp']
            for field in expected_fields:
                if field not in response:
                    print(f"❌ Missing field: {field}")
                    return False
            
            stats = response.get('stats', {})
            print(f"   WebSocket Stats: {stats}")
            return True
        
        return False

    async def test_websocket_connection(self):
        """Test WebSocket real-time connection"""
        if not self.user_id:
            print("❌ Skipping WebSocket test - No user ID available")
            return False
        
        print(f"\n🔍 Testing WebSocket Connection...")
        print(f"   WebSocket URL: {self.ws_url}/ws/{self.user_id}")
        
        try:
            # Test WebSocket connection
            uri = f"{self.ws_url}/ws/{self.user_id}"
            
            async with websockets.connect(uri) as websocket:
                print("✅ WebSocket connection established")
                
                # Wait for welcome message
                welcome_message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                welcome_data = json.loads(welcome_message)
                
                if welcome_data.get('type') == 'welcome':
                    print("✅ Welcome message received")
                    
                    # Test ping-pong
                    ping_message = json.dumps({"type": "ping"})
                    await websocket.send(ping_message)
                    
                    pong_response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    pong_data = json.loads(pong_response)
                    
                    if pong_data.get('type') == 'pong':
                        print("✅ Ping-pong test successful")
                        self.tests_passed += 1
                        return True
                    else:
                        print(f"❌ Expected pong, got: {pong_data}")
                        return False
                else:
                    print(f"❌ Expected welcome message, got: {welcome_data}")
                    return False
                    
        except asyncio.TimeoutError:
            print("❌ WebSocket connection timeout")
            return False
        except Exception as e:
            print(f"❌ WebSocket connection error: {e}")
            return False
        finally:
            self.tests_run += 1

    # =======================================
    # ENTERPRISE FEATURES TESTS
    # =======================================

    def test_create_organization(self):
        """Test organization creation"""
        org_data = {
            "name": f"Test Organization {int(time.time())}",
            "plan": "enterprise"
        }
        
        success, response = self.run_test(
            "Create Organization",
            "POST",
            "api/enterprise/organizations",
            200,
            data=org_data
        )
        
        if success and response:
            organization = response.get('organization', {})
            self.organization_id = organization.get('id')
            print(f"   Created Organization ID: {self.organization_id}")
            return True
        
        return False

    def test_get_user_organizations(self):
        """Test get user organizations"""
        success, response = self.run_test(
            "Get User Organizations",
            "GET",
            "api/enterprise/organizations",
            200
        )
        
        if success and response:
            organizations = response.get('organizations', [])
            count = response.get('count', 0)
            print(f"   Found {count} organizations")
            return True
        
        return False

    def test_assign_user_role(self):
        """Test user role assignment"""
        if not self.organization_id:
            print("❌ Skipping - No organization ID available")
            return False
        
        role_data = {
            "user_id": self.user_id,
            "role": "member"
        }
        
        success, response = self.run_test(
            "Assign User Role",
            "POST",
            f"api/enterprise/organizations/{self.organization_id}/members",
            200,
            data=role_data
        )
        
        return success

    def test_get_audit_logs(self):
        """Test organization audit logs"""
        if not self.organization_id:
            print("❌ Skipping - No organization ID available")
            return False
        
        success, response = self.run_test(
            "Get Audit Logs",
            "GET",
            f"api/enterprise/organizations/{self.organization_id}/audit-logs",
            200,
            params={"limit": 10}
        )
        
        if success and response:
            logs = response.get('logs', [])
            total = response.get('total', 0)
            print(f"   Found {total} audit log entries")
            return True
        
        return False

    def test_get_organization_analytics(self):
        """Test organization analytics"""
        if not self.organization_id:
            print("❌ Skipping - No organization ID available")
            return False
        
        success, response = self.run_test(
            "Get Organization Analytics",
            "GET",
            f"api/enterprise/organizations/{self.organization_id}/analytics",
            200
        )
        
        if success and response:
            analytics = response.get('analytics', {})
            generated_at = response.get('generated_at')
            print(f"   Analytics generated at: {generated_at}")
            return True
        
        return False

    def test_create_team_workspace(self):
        """Test team workspace creation"""
        if not self.organization_id:
            print("❌ Skipping - No organization ID available")
            return False
        
        workspace_data = {
            "name": f"Test Workspace {int(time.time())}",
            "description": "Test workspace for enhanced features",
            "members": [self.user_id]
        }
        
        success, response = self.run_test(
            "Create Team Workspace",
            "POST",
            f"api/enterprise/organizations/{self.organization_id}/workspaces",
            200,
            data=workspace_data
        )
        
        if success and response:
            workspace = response.get('workspace', {})
            self.workspace_id = workspace.get('id')
            print(f"   Created Workspace ID: {self.workspace_id}")
            return True
        
        return False

    def test_get_user_workspaces(self):
        """Test get user workspaces"""
        if not self.organization_id:
            print("❌ Skipping - No organization ID available")
            return False
        
        success, response = self.run_test(
            "Get User Workspaces",
            "GET",
            f"api/enterprise/organizations/{self.organization_id}/workspaces",
            200
        )
        
        if success and response:
            workspaces = response.get('workspaces', [])
            count = response.get('count', 0)
            print(f"   Found {count} workspaces")
            return True
        
        return False

    # =======================================
    # ENHANCED AI FEATURES TESTS
    # =======================================

    def test_enhanced_ai_generate_workflow(self):
        """Test enhanced AI workflow generation with provider info"""
        ai_data = {
            "prompt": "Create a workflow for processing customer feedback from multiple channels",
            "structured": True
        }
        
        success, response = self.run_test(
            "Enhanced AI Generate Workflow",
            "POST",
            "api/ai/generate-workflow",
            200,
            data=ai_data
        )
        
        if success and response:
            # Check for enhanced features
            if 'provider_used' in response or 'ai_provider' in response:
                print("✅ Provider information included")
            
            workflow_data = response.get('workflow', response)
            if 'nodes' in workflow_data and 'connections' in workflow_data:
                print("✅ Complete workflow structure generated")
                return True
        
        return False

    def test_enhanced_ai_chat(self):
        """Test enhanced AI chat with provider and context info"""
        ai_data = {
            "message": "Help me optimize my automation workflows for better performance",
            "session_id": str(uuid.uuid4())
        }
        
        success, response = self.run_test(
            "Enhanced AI Chat",
            "POST",
            "api/ai/chat",
            200,
            data=ai_data
        )
        
        if success and response:
            # Check for enhanced features
            if 'provider_used' in response or 'ai_provider' in response:
                print("✅ Provider information included")
            
            if 'context' in response or 'session_context' in response:
                print("✅ Context information included")
            
            if 'response' in response or 'message' in response:
                print("✅ AI response generated")
                return True
        
        return False

    def test_ai_provider_stats(self):
        """Test AI provider statistics"""
        success, response = self.run_test(
            "AI Provider Stats",
            "GET",
            "api/ai/providers/stats",
            200
        )
        
        if success and response:
            # Check for provider stats
            expected_fields = ['providers', 'usage_stats', 'performance_metrics']
            found_fields = 0
            
            for field in expected_fields:
                if field in response:
                    found_fields += 1
                    print(f"✅ Found {field}")
            
            if found_fields > 0:
                return True
        
        return False

    def test_ai_workflow_optimization(self):
        """Test AI workflow optimization"""
        # First create a simple workflow to optimize
        workflow_data = {
            "workflow_id": str(uuid.uuid4()),
            "optimization_goals": ["performance", "cost", "reliability"]
        }
        
        success, response = self.run_test(
            "AI Workflow Optimization",
            "POST",
            "api/ai/optimize-workflow",
            200,
            data=workflow_data
        )
        
        if success and response:
            if 'optimizations' in response or 'suggestions' in response:
                print("✅ Optimization suggestions provided")
                return True
        
        return False

    # =======================================
    # MASSIVE TEMPLATES LIBRARY TESTS
    # =======================================

    def test_massive_templates_all(self):
        """Test massive templates library (all templates)"""
        success, response = self.run_test(
            "Get Massive Templates (All)",
            "GET",
            "api/templates/massive",
            200
        )
        
        if success and response:
            templates = response.get('templates', [])
            total = response.get('total', 0)
            stats = response.get('stats', {})
            
            print(f"   Total templates: {total}")
            print(f"   Template stats: {stats}")
            
            if total >= 100:  # Should have 100+ templates
                print("✅ Massive template library confirmed (100+ templates)")
                return True
            else:
                print(f"❌ Expected 100+ templates, got {total}")
        
        return False

    def test_massive_templates_by_category(self):
        """Test massive templates by category"""
        categories = ["business_automation", "marketing", "ecommerce", "finance", "healthcare", "ai_powered"]
        
        for category in categories:
            success, response = self.run_test(
                f"Get Massive Templates ({category})",
                "GET",
                "api/templates/massive",
                200,
                params={"category": category}
            )
            
            if success and response:
                templates = response.get('templates', [])
                category_name = response.get('category')
                print(f"   {category}: {len(templates)} templates")
            else:
                print(f"❌ Failed to get {category} templates")
                return False
        
        return True

    def test_comprehensive_template_stats(self):
        """Test comprehensive template statistics"""
        success, response = self.run_test(
            "Get Comprehensive Template Stats",
            "GET",
            "api/templates/stats/comprehensive",
            200
        )
        
        if success and response:
            massive_stats = response.get('massive_library', {})
            original_stats = response.get('original_library', {})
            combined_total = response.get('combined_total', 0)
            coverage_analysis = response.get('coverage_analysis', {})
            
            print(f"   Combined total templates: {combined_total}")
            print(f"   Industries covered: {coverage_analysis.get('industries_covered', 0)}")
            print(f"   Use cases covered: {coverage_analysis.get('use_cases_covered', 0)}")
            
            if combined_total >= 100:
                print("✅ Comprehensive template system confirmed")
                return True
        
        return False

    # =======================================
    # ENHANCED WORKFLOW EXECUTION TESTS
    # =======================================

    def test_enhanced_workflow_execution_with_websocket(self):
        """Test enhanced workflow execution with real-time WebSocket updates"""
        # First create a test workflow
        workflow_data = {
            "name": f"Enhanced Test Workflow {int(time.time())}",
            "description": "Test workflow for enhanced execution with WebSocket updates",
            "nodes": [
                {
                    "id": "node1",
                    "type": "trigger",
                    "name": "Start Trigger",
                    "config": {"trigger_type": "manual"},
                    "x": 100,
                    "y": 100
                },
                {
                    "id": "node2", 
                    "type": "action",
                    "name": "Process Data",
                    "config": {"action_type": "data_processing"},
                    "x": 300,
                    "y": 100
                },
                {
                    "id": "node3",
                    "type": "ai-text-advanced",
                    "name": "AI Analysis",
                    "config": {"model": "gpt-3.5-turbo", "prompt": "Analyze the data"},
                    "x": 500,
                    "y": 100
                }
            ],
            "connections": [
                {
                    "id": "conn1",
                    "from": "node1",
                    "to": "node2",
                    "fromPort": "output",
                    "toPort": "input"
                },
                {
                    "id": "conn2", 
                    "from": "node2",
                    "to": "node3",
                    "fromPort": "output",
                    "toPort": "input"
                }
            ],
            "triggers": [
                {
                    "type": "manual",
                    "conditions": {}
                }
            ]
        }
        
        # Create workflow
        success, workflow_response = self.run_test(
            "Create Enhanced Test Workflow",
            "POST",
            "api/workflows",
            200,
            data=workflow_data
        )
        
        if not success:
            return False
        
        workflow_id = workflow_response.get('id')
        if not workflow_id:
            print("❌ No workflow ID returned")
            return False
        
        # Execute workflow with enhanced features
        execution_headers = {
            "idempotency-key": str(uuid.uuid4()),
            "x-request-id": str(uuid.uuid4())
        }
        
        success, execution_response = self.run_test(
            "Enhanced Workflow Execution",
            "POST",
            f"api/workflows/{workflow_id}/execute",
            200,
            headers=execution_headers
        )
        
        if success and execution_response:
            execution_id = execution_response.get('execution_id')
            status = execution_response.get('status')
            estimated_completion = execution_response.get('estimated_completion')
            resource_estimation = execution_response.get('resource_estimation', {})
            
            print(f"   Execution ID: {execution_id}")
            print(f"   Status: {status}")
            print(f"   Estimated completion: {estimated_completion}")
            print(f"   Resource estimation: {resource_estimation}")
            
            if execution_id and status == 'running':
                print("✅ Enhanced workflow execution started successfully")
                
                # Wait a bit for execution to complete
                time.sleep(3)
                
                # Check execution status
                success, status_response = self.run_test(
                    "Get Execution Status",
                    "GET",
                    f"api/executions/{execution_id}",
                    200
                )
                
                if success and status_response:
                    final_status = status_response.get('status')
                    performance_metrics = status_response.get('performance_metrics', {})
                    node_execution_details = status_response.get('node_execution_details', [])
                    
                    print(f"   Final status: {final_status}")
                    print(f"   Performance metrics: {performance_metrics}")
                    print(f"   Node execution details: {len(node_execution_details)} nodes")
                    
                    if final_status in ['success', 'completed']:
                        print("✅ Enhanced workflow execution completed successfully")
                        return True
        
        return False

    def run_all_enhanced_tests(self):
        """Run all enhanced feature tests"""
        print("🚀 Starting Enhanced Features API Testing...")
        print("=" * 60)
        
        # Setup authentication
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Aborting tests.")
            return 0, 1
        
        # WebSocket Real-time Features Tests
        print("\n" + "=" * 60)
        print("🔌 WEBSOCKET REAL-TIME FEATURES TESTS")
        print("=" * 60)
        
        self.test_websocket_stats()
        
        # Run WebSocket connection test
        try:
            asyncio.run(self.test_websocket_connection())
        except Exception as e:
            print(f"❌ WebSocket test failed: {e}")
            self.tests_run += 1
        
        # Enterprise Features Tests
        print("\n" + "=" * 60)
        print("🏢 ENTERPRISE FEATURES TESTS")
        print("=" * 60)
        
        self.test_create_organization()
        self.test_get_user_organizations()
        self.test_assign_user_role()
        self.test_get_audit_logs()
        self.test_get_organization_analytics()
        self.test_create_team_workspace()
        self.test_get_user_workspaces()
        
        # Enhanced AI Features Tests
        print("\n" + "=" * 60)
        print("🤖 ENHANCED AI FEATURES TESTS")
        print("=" * 60)
        
        self.test_enhanced_ai_generate_workflow()
        self.test_enhanced_ai_chat()
        self.test_ai_provider_stats()
        self.test_ai_workflow_optimization()
        
        # Massive Templates Library Tests
        print("\n" + "=" * 60)
        print("📚 MASSIVE TEMPLATES LIBRARY TESTS")
        print("=" * 60)
        
        self.test_massive_templates_all()
        self.test_massive_templates_by_category()
        self.test_comprehensive_template_stats()
        
        # Enhanced Workflow Execution Tests
        print("\n" + "=" * 60)
        print("⚡ ENHANCED WORKFLOW EXECUTION TESTS")
        print("=" * 60)
        
        self.test_enhanced_workflow_execution_with_websocket()
        
        # Print final results
        print("\n" + "=" * 60)
        print("📊 ENHANCED FEATURES TEST RESULTS")
        print("=" * 60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL ENHANCED FEATURES TESTS PASSED!")
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
        
        return self.tests_passed, self.tests_run

if __name__ == "__main__":
    # Get backend URL from environment or use default
    import os
    backend_url = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
    
    tester = EnhancedFeaturesAPITester(backend_url)
    passed, total = tester.run_all_enhanced_tests()
    
    # Exit with appropriate code
    sys.exit(0 if passed == total else 1)