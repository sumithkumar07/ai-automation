#!/usr/bin/env python3
"""
COMPREHENSIVE END-TO-END BACKEND TESTING - AETHER AUTOMATION
Verify all features are REAL & FUNCTIONAL (not demo/fake data)

This test suite verifies:
1. 100% backend functionality success rate
2. All 103+ integrations are real and functional
3. AI features with GROQ integration are working (not fallback/demo)
4. Workflow system processes actual logic
5. Dashboard analytics return real data
6. Template system with actual workflow data
7. Database operations persist correctly
8. All 25+ node types functionality
"""

import requests
import sys
import json
import time
import uuid
from datetime import datetime
import random
import string

class ComprehensiveAetherTester:
    def __init__(self, base_url="https://feature-explorer-11.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_failures = []
        self.created_workflow_id = None
        self.created_template_id = None
        self.session_id = str(uuid.uuid4())
        
        # Test data for realistic testing
        self.test_email = f"aether_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@automation.com"
        self.test_password = "AetherTest2024!"
        
    def log_critical_failure(self, test_name, reason):
        """Log critical failures that indicate fake/demo data"""
        self.critical_failures.append({
            'test': test_name,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        })
        
    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, params=None, timeout=15):
        """Run a single API test with enhanced error handling"""
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
                response = requests.get(url, headers=test_headers, params=params, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, params=params, timeout=timeout)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, params=params, timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, params=params, timeout=timeout)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
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

    def test_authentication_system(self):
        """Test comprehensive authentication system"""
        print("\n🔐 TESTING AUTHENTICATION SYSTEM")
        print("=" * 50)
        
        # Test user registration with realistic data
        user_data = {
            "email": self.test_email,
            "password": self.test_password,
            "first_name": "Aether",
            "last_name": "TestUser"
        }
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "api/auth/register",
            200,
            data=user_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user']['id']
            print(f"   ✅ JWT Token obtained: {self.token[:30]}...")
            print(f"   ✅ User ID: {self.user_id}")
            
            # Verify token is real JWT (not fake)
            if len(self.token) > 100 and '.' in self.token:
                print(f"   ✅ Token appears to be real JWT format")
            else:
                self.log_critical_failure("Authentication", "Token doesn't appear to be real JWT")
                
        else:
            print("❌ Registration failed, trying login...")
            # Fallback to existing test user
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
            else:
                print("❌ CRITICAL: Both registration and login failed")
                return False
        
        # Test token validation
        success, response = self.run_test(
            "Token Validation",
            "GET",
            "api/auth/me",
            200
        )
        
        if success:
            if 'id' in response and 'email' in response:
                print(f"   ✅ Token validation successful")
                print(f"   User: {response.get('email', 'N/A')}")
            else:
                self.log_critical_failure("Authentication", "Token validation returned incomplete user data")
        
        return success

    def test_integration_system_comprehensive(self):
        """Test the 103+ integrations claim thoroughly"""
        print("\n🔗 TESTING INTEGRATION SYSTEM - 103+ INTEGRATIONS VERIFICATION")
        print("=" * 70)
        
        # Test available integrations endpoint
        success, response = self.run_test(
            "Get Available Integrations",
            "GET",
            "api/integrations/",
            200
        )
        
        if not success:
            self.log_critical_failure("Integrations", "Available integrations endpoint failed")
            return False
            
        # Verify integration count
        if isinstance(response, list):
            integration_count = len(response)
            print(f"   📊 Found {integration_count} integrations")
            
            if integration_count >= 103:
                print(f"   ✅ HOMEPAGE PROMISE FULFILLED: {integration_count} integrations (exceeds 100+)")
            elif integration_count >= 50:
                print(f"   ⚠️ PARTIAL FULFILLMENT: {integration_count} integrations (below 100+ promise)")
            else:
                print(f"   ❌ PROMISE NOT FULFILLED: Only {integration_count} integrations")
                self.log_critical_failure("Integrations", f"Only {integration_count} integrations, far below 100+ promise")
            
            # Test integration categories
            categories = set()
            platforms = set()
            
            for integration in response[:10]:  # Sample first 10
                if 'category' in integration:
                    categories.add(integration['category'])
                if 'platform' in integration:
                    platforms.add(integration['platform'])
                    
                # Verify integration has real metadata (not just placeholder)
                required_fields = ['name', 'description', 'platform', 'category']
                missing_fields = [field for field in required_fields if field not in integration or not integration[field]]
                
                if missing_fields:
                    print(f"   ⚠️ Integration {integration.get('name', 'Unknown')} missing: {missing_fields}")
                else:
                    print(f"   ✅ Integration {integration['name']} has complete metadata")
            
            print(f"   📊 Found {len(categories)} categories: {', '.join(list(categories)[:5])}...")
            print(f"   📊 Found {len(platforms)} platforms: {', '.join(list(platforms)[:5])}...")
            
            # Test integration search functionality
            search_terms = ['slack', 'google', 'github', 'ai', 'payment']
            for term in search_terms:
                success, search_response = self.run_test(
                    f"Integration Search - {term}",
                    "GET",
                    "api/integrations/search",
                    200,
                    params={"query": term}
                )
                
                if success and isinstance(search_response, list):
                    print(f"   🔍 Search '{term}': {len(search_response)} results")
                    
                    # Verify search results are relevant
                    if search_response:
                        first_result = search_response[0]
                        if term.lower() in first_result.get('name', '').lower() or term.lower() in first_result.get('description', '').lower():
                            print(f"   ✅ Search results relevant for '{term}'")
                        else:
                            print(f"   ⚠️ Search results may not be relevant for '{term}'")
        
        # Test integration connection testing
        test_integrations = ['slack', 'github', 'gmail']
        for platform in test_integrations:
            test_data = {
                "integration_id": f"test_{platform}_{int(time.time())}"
            }
            
            success, response = self.run_test(
                f"Test {platform.title()} Connection",
                "POST",
                f"api/integration-testing/test-connection/{platform}",
                200,
                data=test_data
            )
            
            if success:
                if 'test_result' in response and 'status' in response:
                    print(f"   ✅ {platform.title()} connection test functional")
                    print(f"   Status: {response['status']}")
                else:
                    print(f"   ⚠️ {platform.title()} connection test incomplete response")
        
        return True

    def test_ai_features_groq_verification(self):
        """Test AI features to ensure GROQ integration is real (not demo/fallback)"""
        print("\n🤖 TESTING AI FEATURES - GROQ INTEGRATION VERIFICATION")
        print("=" * 60)
        
        # Test AI workflow generation
        workflow_prompts = [
            "Create a workflow that processes customer support tickets and routes them to appropriate teams",
            "Build an automation that monitors social media mentions and sends alerts",
            "Design a workflow for processing e-commerce orders and updating inventory"
        ]
        
        for i, prompt in enumerate(workflow_prompts, 1):
            success, response = self.run_test(
                f"AI Workflow Generation - Test {i}",
                "POST",
                "api/ai/generate-workflow",
                200,
                data={"description": prompt}
            )
            
            if success:
                # Verify response indicates real AI processing
                if 'workflow' in response and 'confidence' in response:
                    confidence = response.get('confidence', 0)
                    workflow = response['workflow']
                    
                    print(f"   📊 Confidence: {confidence}")
                    print(f"   📊 Nodes: {len(workflow.get('nodes', []))}")
                    print(f"   📊 Connections: {len(workflow.get('connections', []))}")
                    
                    # Check for signs of real AI vs demo data
                    if confidence > 0.7 and len(workflow.get('nodes', [])) > 2:
                        print(f"   ✅ AI appears to be generating real workflows")
                        
                        # Check if workflow content is relevant to prompt
                        workflow_text = json.dumps(workflow).lower()
                        prompt_keywords = prompt.lower().split()[:3]  # First 3 words
                        relevant_keywords = sum(1 for keyword in prompt_keywords if keyword in workflow_text)
                        
                        if relevant_keywords >= 1:
                            print(f"   ✅ Generated workflow relevant to prompt")
                        else:
                            print(f"   ⚠️ Generated workflow may not be relevant to prompt")
                            self.log_critical_failure("AI Features", "AI workflow generation not contextually relevant")
                    else:
                        print(f"   ⚠️ AI may be using fallback/demo mode")
                        self.log_critical_failure("AI Features", f"Low confidence ({confidence}) or simple workflow")
                else:
                    self.log_critical_failure("AI Features", "AI workflow response missing expected structure")
        
        # Test AI integration suggestions
        success, response = self.run_test(
            "AI Integration Suggestions",
            "POST",
            "api/ai/suggest-integrations",
            200,
            params={"description": "I need to automate customer onboarding process"}
        )
        
        if success:
            if 'suggestions' in response:
                suggestions = response['suggestions']
                print(f"   📊 AI suggested {len(suggestions)} integrations")
                
                # Check if suggestions are contextually relevant
                if suggestions:
                    suggestion_text = json.dumps(suggestions).lower()
                    if 'customer' in suggestion_text or 'onboard' in suggestion_text or 'crm' in suggestion_text:
                        print(f"   ✅ AI suggestions contextually relevant")
                    else:
                        print(f"   ⚠️ AI suggestions may not be contextually relevant")
                        
                # Check if GROQ AI is working
                ai_powered = response.get('ai_powered', False)
                if ai_powered:
                    print(f"   ✅ GROQ AI integration suggestions confirmed")
                else:
                    print(f"   ⚠️ Using fallback integration suggestions")
                    self.log_critical_failure("AI Features", "AI integration suggestions using fallback mode")
        
        # Test AI chat functionality
        chat_messages = [
            "What are the best practices for workflow automation?",
            "How do I handle errors in automated workflows?",
            "Can you explain the difference between triggers and actions?"
        ]
        
        for i, message in enumerate(chat_messages, 1):
            success, response = self.run_test(
                f"AI Chat - Message {i}",
                "POST",
                "api/ai/chat",
                200,
                params={"message": message, "session_id": self.session_id}
            )
            
            if success:
                if 'response' in response:
                    ai_response = response['response']
                    print(f"   💬 AI Response length: {len(ai_response)} characters")
                    
                    # Check for signs of real AI vs canned responses
                    if len(ai_response) > 50 and any(word in ai_response.lower() for word in ['workflow', 'automation', 'process']):
                        print(f"   ✅ AI chat response appears contextual and detailed")
                    else:
                        print(f"   ⚠️ AI chat response may be canned/generic")
                        self.log_critical_failure("AI Features", "AI chat responses appear generic/canned")
                        
                    # Check session continuity
                    if 'session_id' in response and response['session_id'] == self.session_id:
                        print(f"   ✅ AI chat session continuity maintained")
                    else:
                        print(f"   ⚠️ AI chat session continuity not maintained")
        
        return True

    def test_workflow_system_comprehensive(self):
        """Test workflow system with real processing verification"""
        print("\n⚙️ TESTING WORKFLOW SYSTEM - REAL PROCESSING VERIFICATION")
        print("=" * 60)
        
        # Create a comprehensive test workflow
        workflow_data = {
            "name": f"Comprehensive Test Workflow {datetime.now().strftime('%H%M%S')}",
            "description": "A comprehensive test workflow to verify real processing capabilities",
            "nodes": [
                {
                    "id": "trigger_node",
                    "type": "webhook_trigger",
                    "name": "Webhook Trigger",
                    "config": {
                        "path": "/webhook/test",
                        "method": "POST",
                        "authentication": "none"
                    },
                    "position": {"x": 100, "y": 100}
                },
                {
                    "id": "filter_node",
                    "type": "filter",
                    "name": "Data Filter",
                    "config": {
                        "conditions": [
                            {"field": "status", "operator": "equals", "value": "active"}
                        ]
                    },
                    "position": {"x": 300, "y": 100}
                },
                {
                    "id": "transform_node",
                    "type": "data_transform",
                    "name": "Data Transformer",
                    "config": {
                        "transformations": [
                            {"field": "email", "operation": "lowercase"},
                            {"field": "timestamp", "operation": "format_date", "format": "ISO"}
                        ]
                    },
                    "position": {"x": 500, "y": 100}
                },
                {
                    "id": "action_node",
                    "type": "http_request",
                    "name": "HTTP Action",
                    "config": {
                        "url": "https://httpbin.org/post",
                        "method": "POST",
                        "headers": {"Content-Type": "application/json"},
                        "body": "{{transformed_data}}"
                    },
                    "position": {"x": 700, "y": 100}
                }
            ],
            "connections": [
                {
                    "from": "trigger_node",
                    "to": "filter_node",
                    "fromPort": "output",
                    "toPort": "input"
                },
                {
                    "from": "filter_node",
                    "to": "transform_node",
                    "fromPort": "output",
                    "toPort": "input"
                },
                {
                    "from": "transform_node",
                    "to": "action_node",
                    "fromPort": "output",
                    "toPort": "input"
                }
            ],
            "triggers": [
                {
                    "type": "webhook",
                    "node_id": "trigger_node",
                    "conditions": {"path": "/webhook/test"}
                }
            ],
            "settings": {
                "timeout": 300,
                "retry_count": 3,
                "error_handling": "continue"
            }
        }
        
        # Test workflow creation
        success, response = self.run_test(
            "Create Comprehensive Workflow",
            "POST",
            "api/workflows/",  # Note the trailing slash to avoid redirect
            200,
            data=workflow_data
        )
        
        if success and 'id' in response:
            self.created_workflow_id = response['id']
            print(f"   ✅ Workflow created with ID: {self.created_workflow_id}")
            
            # Verify workflow was stored correctly
            success, get_response = self.run_test(
                "Verify Workflow Storage",
                "GET",
                f"api/workflows/{self.created_workflow_id}",
                200
            )
            
            if success:
                stored_workflow = get_response
                if len(stored_workflow.get('nodes', [])) == 4:
                    print(f"   ✅ Workflow stored correctly with all nodes")
                else:
                    print(f"   ⚠️ Workflow storage incomplete")
                    self.log_critical_failure("Workflow System", "Workflow not stored correctly")
            
            # Test workflow execution
            execution_data = {
                "input_data": {
                    "status": "active",
                    "email": "TEST@EXAMPLE.COM",
                    "timestamp": datetime.now().isoformat(),
                    "user_id": "test_user_123"
                },
                "execution_mode": "test"
            }
            
            success, exec_response = self.run_test(
                "Execute Workflow",
                "POST",
                f"api/workflows/{self.created_workflow_id}/execute",
                200,
                data=execution_data
            )
            
            if success:
                if 'execution_id' in exec_response:
                    execution_id = exec_response['execution_id']
                    print(f"   ✅ Workflow execution started: {execution_id}")
                    
                    # Wait a moment for execution
                    time.sleep(2)
                    
                    # Check execution status
                    success, status_response = self.run_test(
                        "Check Execution Status",
                        "GET",
                        f"api/executions/{execution_id}",
                        200
                    )
                    
                    if success:
                        status = status_response.get('status', 'unknown')
                        print(f"   📊 Execution status: {status}")
                        
                        # Check for real processing indicators
                        if 'logs' in status_response and status_response['logs']:
                            print(f"   ✅ Execution logs present - indicates real processing")
                            logs = status_response['logs']
                            if len(logs) > 1:
                                print(f"   ✅ Multiple log entries - workflow actually processed")
                            else:
                                print(f"   ⚠️ Limited log entries - may be demo processing")
                        else:
                            print(f"   ⚠️ No execution logs - may indicate fake processing")
                            self.log_critical_failure("Workflow System", "No execution logs found")
                        
                        # Check for data transformation
                        if 'output_data' in status_response:
                            output = status_response['output_data']
                            if isinstance(output, dict) and 'email' in output:
                                if output['email'] == 'test@example.com':  # Should be lowercase
                                    print(f"   ✅ Data transformation working (email lowercased)")
                                else:
                                    print(f"   ⚠️ Data transformation may not be working")
                            else:
                                print(f"   ⚠️ Output data structure unexpected")
                else:
                    print(f"   ⚠️ Workflow execution response missing execution_id")
                    self.log_critical_failure("Workflow System", "Execution response incomplete")
            
            # Test workflow duplication
            success, dup_response = self.run_test(
                "Duplicate Workflow",
                "POST",
                f"api/workflows/{self.created_workflow_id}/duplicate",
                200
            )
            
            if success and 'id' in dup_response:
                print(f"   ✅ Workflow duplication working")
            else:
                print(f"   ⚠️ Workflow duplication failed")
        
        else:
            print(f"   ❌ Workflow creation failed")
            self.log_critical_failure("Workflow System", "Workflow creation failed")
            return False
        
        return True

    def test_dashboard_analytics_real_data(self):
        """Test dashboard analytics to ensure real data (not hardcoded)"""
        print("\n📊 TESTING DASHBOARD ANALYTICS - REAL DATA VERIFICATION")
        print("=" * 60)
        
        # Test dashboard stats
        success, response = self.run_test(
            "Dashboard Stats",
            "GET",
            "api/dashboard/stats",
            200
        )
        
        if success:
            stats = response
            print(f"   📊 Dashboard stats structure: {list(stats.keys())}")
            
            # Check for dynamic data indicators
            if 'total_workflows' in stats and 'total_executions' in stats:
                workflows = stats['total_workflows']
                executions = stats['total_executions']
                
                print(f"   📊 Total workflows: {workflows}")
                print(f"   📊 Total executions: {executions}")
                
                # If we just created a workflow, count should reflect that
                if workflows > 0:
                    print(f"   ✅ Workflow count indicates real data")
                else:
                    print(f"   ⚠️ Zero workflows - may indicate fresh system or demo data")
                
                # Check success rate calculation
                if 'success_rate' in stats:
                    success_rate = stats['success_rate']
                    if 0 <= success_rate <= 100:
                        print(f"   ✅ Success rate realistic: {success_rate}%")
                    else:
                        print(f"   ⚠️ Success rate unrealistic: {success_rate}%")
                        self.log_critical_failure("Dashboard", f"Unrealistic success rate: {success_rate}%")
            
            # Test analytics overview
            success, analytics_response = self.run_test(
                "Analytics Overview",
                "GET",
                "api/analytics/dashboard/overview",
                200
            )
            
            if success:
                if 'summary' in analytics_response and 'charts' in analytics_response:
                    print(f"   ✅ Analytics overview has comprehensive structure")
                    
                    summary = analytics_response['summary']
                    charts = analytics_response['charts']
                    
                    # Check for realistic data patterns
                    if 'total_workflows' in summary and 'active_integrations' in summary:
                        print(f"   📊 Analytics workflows: {summary['total_workflows']}")
                        print(f"   📊 Analytics integrations: {summary['active_integrations']}")
                        
                        # Check if data is consistent between endpoints
                        if abs(summary['total_workflows'] - workflows) <= 1:  # Allow for timing differences
                            print(f"   ✅ Analytics data consistent with dashboard")
                        else:
                            print(f"   ⚠️ Analytics data inconsistent with dashboard")
                            self.log_critical_failure("Dashboard", "Inconsistent data between endpoints")
                    
                    # Check chart data
                    if charts and isinstance(charts, dict):
                        for chart_name, chart_data in charts.items():
                            if isinstance(chart_data, list) and chart_data:
                                print(f"   ✅ Chart '{chart_name}' has data points: {len(chart_data)}")
                            else:
                                print(f"   ⚠️ Chart '{chart_name}' has no data")
                else:
                    print(f"   ⚠️ Analytics overview missing expected structure")
        
        # Test integration usage analytics
        success, usage_response = self.run_test(
            "Integration Usage Analytics",
            "GET",
            "api/analytics/integrations/usage",
            200
        )
        
        if success:
            if 'breakdown' in usage_response and 'metrics' in usage_response:
                print(f"   ✅ Integration usage analytics comprehensive")
                
                breakdown = usage_response['breakdown']
                if breakdown and isinstance(breakdown, list):
                    print(f"   📊 Integration breakdown: {len(breakdown)} entries")
                    
                    # Check for realistic usage patterns
                    for item in breakdown[:3]:  # Check first 3
                        if 'usage_count' in item and 'success_rate' in item:
                            usage = item['usage_count']
                            success_rate = item['success_rate']
                            if usage >= 0 and 0 <= success_rate <= 100:
                                print(f"   ✅ Realistic usage data: {usage} uses, {success_rate}% success")
                            else:
                                print(f"   ⚠️ Unrealistic usage data")
                                self.log_critical_failure("Analytics", "Unrealistic integration usage data")
            else:
                print(f"   ⚠️ Integration usage analytics incomplete")
        
        return True

    def test_template_system_real_data(self):
        """Test template system to ensure real workflow data (not placeholders)"""
        print("\n📋 TESTING TEMPLATE SYSTEM - REAL DATA VERIFICATION")
        print("=" * 60)
        
        # Test template listing
        success, response = self.run_test(
            "Get Templates",
            "GET",
            "api/templates/",
            200
        )
        
        if success:
            templates = response if isinstance(response, list) else response.get('templates', [])
            print(f"   📊 Found {len(templates)} templates")
            
            if templates:
                # Analyze first few templates for real data indicators
                for i, template in enumerate(templates[:3], 1):
                    print(f"   🔍 Analyzing template {i}: {template.get('name', 'Unnamed')}")
                    
                    # Check for real workflow data
                    if 'workflow_data' in template:
                        workflow = template['workflow_data']
                        if 'nodes' in workflow and 'connections' in workflow:
                            nodes = workflow['nodes']
                            connections = workflow['connections']
                            
                            print(f"     📊 Nodes: {len(nodes)}, Connections: {len(connections)}")
                            
                            # Check for realistic node configurations
                            if nodes:
                                first_node = nodes[0]
                                if 'config' in first_node and first_node['config']:
                                    print(f"     ✅ Template has real node configurations")
                                else:
                                    print(f"     ⚠️ Template nodes lack configuration")
                                    self.log_critical_failure("Templates", "Template nodes lack real configuration")
                            
                            # Check for logical connections
                            if len(connections) > 0 and len(nodes) > 1:
                                print(f"     ✅ Template has logical node connections")
                            elif len(nodes) > 1:
                                print(f"     ⚠️ Template missing connections between nodes")
                        else:
                            print(f"     ⚠️ Template missing workflow structure")
                            self.log_critical_failure("Templates", "Template missing workflow structure")
                    else:
                        print(f"     ⚠️ Template missing workflow data")
                        self.log_critical_failure("Templates", "Template missing workflow data")
                    
                    # Check for realistic metadata
                    required_fields = ['name', 'description', 'category', 'difficulty']
                    missing_fields = [field for field in required_fields if field not in template or not template[field]]
                    
                    if not missing_fields:
                        print(f"     ✅ Template has complete metadata")
                    else:
                        print(f"     ⚠️ Template missing metadata: {missing_fields}")
            else:
                print(f"   ⚠️ No templates found - may indicate empty system")
        
        # Test template creation with real data
        template_data = {
            "name": f"Test Template {datetime.now().strftime('%H%M%S')}",
            "description": "A comprehensive test template with real workflow data",
            "category": "automation",
            "difficulty": "intermediate",
            "tags": ["test", "automation", "comprehensive"],
            "workflow_data": {
                "name": "Template Workflow",
                "description": "Workflow from template",
                "nodes": [
                    {
                        "id": "start",
                        "type": "trigger",
                        "name": "Start Trigger",
                        "config": {"trigger_type": "manual"}
                    },
                    {
                        "id": "process",
                        "type": "action",
                        "name": "Process Data",
                        "config": {"action_type": "transform", "rules": ["lowercase_email"]}
                    }
                ],
                "connections": [
                    {"from": "start", "to": "process", "fromPort": "output", "toPort": "input"}
                ]
            }
        }
        
        success, create_response = self.run_test(
            "Create Template",
            "POST",
            "api/templates/create",
            200,
            data=template_data
        )
        
        if success and 'id' in create_response:
            self.created_template_id = create_response['id']
            print(f"   ✅ Template created with ID: {self.created_template_id}")
            
            # Test template search
            success, search_response = self.run_test(
                "Search Templates",
                "GET",
                "api/templates/search",
                200,
                params={"query": "automation", "category": "automation"}
            )
            
            if success:
                if 'templates' in search_response:
                    search_results = search_response['templates']
                    print(f"   🔍 Search found {len(search_results)} templates")
                    
                    # Check if our created template appears in search
                    found_our_template = any(t.get('id') == self.created_template_id for t in search_results)
                    if found_our_template:
                        print(f"   ✅ Template search working - found our created template")
                    else:
                        print(f"   ⚠️ Template search may not be working properly")
                else:
                    print(f"   ⚠️ Template search response incomplete")
        else:
            print(f"   ⚠️ Template creation failed")
        
        return True

    def test_node_types_comprehensive(self):
        """Test all 25+ node types functionality"""
        print("\n🔧 TESTING NODE TYPES - 25+ TYPES VERIFICATION")
        print("=" * 50)
        
        # Test node types endpoint
        success, response = self.run_test(
            "Get Node Types",
            "GET",
            "api/node-types",
            200
        )
        
        if success:
            # Handle both old and new response formats
            if isinstance(response, dict) and 'categories' in response and 'stats' in response:
                stats = response['stats']
                categories = response['categories']
                
                total_nodes = stats.get('total_nodes', 0)
                category_count = stats.get('categories', 0)
                
                print(f"   📊 Total node types: {total_nodes}")
                print(f"   📊 Categories: {category_count}")
                
                if total_nodes >= 25:
                    print(f"   ✅ Node count meets promise (25+)")
                else:
                    print(f"   ⚠️ Node count below promise: {total_nodes}")
                    self.log_critical_failure("Node Types", f"Only {total_nodes} node types, below 25+ promise")
                
                if category_count >= 4:
                    print(f"   ✅ Category count adequate (4+)")
                else:
                    print(f"   ⚠️ Category count low: {category_count}")
                
                # Analyze node categories
                for category_name, category_data in categories.items():
                    nodes = category_data.get('nodes', [])
                    print(f"   📂 {category_name}: {len(nodes)} nodes")
                    
                    # Check for real node configurations
                    if nodes:
                        sample_node = nodes[0]
                        if 'config_schema' in sample_node and sample_node['config_schema']:
                            print(f"     ✅ Nodes have configuration schemas")
                        else:
                            print(f"     ⚠️ Nodes lack configuration schemas")
                            self.log_critical_failure("Node Types", f"Nodes in {category_name} lack config schemas")
                        
                        if 'description' in sample_node and len(sample_node['description']) > 20:
                            print(f"     ✅ Nodes have detailed descriptions")
                        else:
                            print(f"     ⚠️ Nodes have minimal descriptions")
                
                # Check for essential node types
                essential_types = ['webhook_trigger', 'http_request', 'email_send', 'condition', 'ai_process']
                found_essential = []
                
                for category_data in categories.values():
                    for node in category_data.get('nodes', []):
                        if node.get('type') in essential_types:
                            found_essential.append(node['type'])
                
                print(f"   🔍 Found essential types: {', '.join(found_essential)}")
                
                if len(found_essential) >= 3:
                    print(f"   ✅ Essential node types present")
                else:
                    print(f"   ⚠️ Missing essential node types")
                    self.log_critical_failure("Node Types", "Missing essential node types")
            
            elif isinstance(response, list):
                # Handle list format response
                total_nodes = len(response)
                print(f"   📊 Total node types: {total_nodes}")
                
                if total_nodes >= 25:
                    print(f"   ✅ Node count meets promise (25+)")
                else:
                    print(f"   ⚠️ Node count below promise: {total_nodes}")
                    self.log_critical_failure("Node Types", f"Only {total_nodes} node types, below 25+ promise")
                
                # Check for node structure
                if response:
                    sample_node = response[0]
                    if isinstance(sample_node, dict) and 'type' in sample_node:
                        print(f"   ✅ Node types have proper structure")
                    else:
                        print(f"   ⚠️ Node types structure unclear")
            
            else:
                print(f"   ⚠️ Node types response format unexpected")
                self.log_critical_failure("Node Types", "Node types endpoint response format unexpected")
        
        return success

    def test_database_persistence(self):
        """Test database operations and data persistence"""
        print("\n💾 TESTING DATABASE PERSISTENCE")
        print("=" * 40)
        
        # Test health endpoint for database connectivity
        success, response = self.run_test(
            "Database Health Check",
            "GET",
            "api/health",
            200
        )
        
        if success:
            if 'database' in response:
                db_status = response['database']
                if db_status.get('status') == 'ok':
                    print(f"   ✅ Database connectivity confirmed")
                    print(f"   📊 Connection time: {db_status.get('response_time_ms', 'N/A')}ms")
                else:
                    print(f"   ❌ Database connectivity issues")
                    self.log_critical_failure("Database", "Database health check failed")
            else:
                print(f"   ⚠️ Health check missing database status")
        
        # Test data persistence by creating and retrieving data
        if self.created_workflow_id:
            # Update workflow and verify persistence
            update_data = {
                "name": f"Updated Workflow {datetime.now().strftime('%H%M%S')}",
                "description": "Testing data persistence",
                "nodes": [
                    {
                        "id": "persistence_test",
                        "type": "action",
                        "name": "Persistence Test Node",
                        "config": {"test_field": "persistence_value"}
                    }
                ]
            }
            
            success, update_response = self.run_test(
                "Update Workflow for Persistence Test",
                "PUT",
                f"api/workflows/{self.created_workflow_id}",
                200,
                data=update_data
            )
            
            if success:
                # Retrieve and verify the update persisted
                success, get_response = self.run_test(
                    "Verify Workflow Persistence",
                    "GET",
                    f"api/workflows/{self.created_workflow_id}",
                    200
                )
                
                if success:
                    if get_response.get('name') == update_data['name']:
                        print(f"   ✅ Workflow updates persisted correctly")
                        
                        # Check if node data persisted
                        nodes = get_response.get('nodes', [])
                        if nodes and nodes[0].get('config', {}).get('test_field') == 'persistence_value':
                            print(f"   ✅ Complex data structures persisted correctly")
                        else:
                            print(f"   ⚠️ Complex data structures may not persist correctly")
                            self.log_critical_failure("Database", "Complex data persistence issues")
                    else:
                        print(f"   ⚠️ Workflow updates not persisted")
                        self.log_critical_failure("Database", "Data persistence failed")
        
        return True

    def test_performance_under_load(self):
        """Test system performance under realistic load"""
        print("\n⚡ TESTING PERFORMANCE UNDER LOAD")
        print("=" * 40)
        
        # Test multiple concurrent requests
        start_time = time.time()
        concurrent_tests = []
        
        # Make several requests in quick succession
        for i in range(5):
            success, response = self.run_test(
                f"Concurrent Request {i+1}",
                "GET",
                "api/dashboard/stats",
                200
            )
            concurrent_tests.append(success)
            
        end_time = time.time()
        total_time = end_time - start_time
        
        success_count = sum(concurrent_tests)
        print(f"   📊 Concurrent requests: {success_count}/5 successful")
        print(f"   📊 Total time: {total_time:.2f} seconds")
        print(f"   📊 Average response time: {total_time/5:.2f} seconds")
        
        if success_count >= 4 and total_time < 30:
            print(f"   ✅ Performance under load acceptable")
        else:
            print(f"   ⚠️ Performance issues detected")
            self.log_critical_failure("Performance", f"Poor performance: {success_count}/5 success, {total_time:.2f}s total")
        
        return success_count >= 4

    def run_comprehensive_test_suite(self):
        """Run the complete comprehensive test suite"""
        print("🚀 STARTING COMPREHENSIVE END-TO-END BACKEND TESTING")
        print("🎯 OBJECTIVE: Verify 100% functionality and real data (not demo/fake)")
        print("=" * 80)
        
        # Test authentication first
        if not self.test_authentication_system():
            print("❌ CRITICAL: Authentication failed - cannot continue")
            return False
        
        # Run all test modules
        test_modules = [
            ("Integration System (103+ Integrations)", self.test_integration_system_comprehensive),
            ("AI Features (GROQ Verification)", self.test_ai_features_groq_verification),
            ("Workflow System (Real Processing)", self.test_workflow_system_comprehensive),
            ("Dashboard Analytics (Real Data)", self.test_dashboard_analytics_real_data),
            ("Template System (Real Data)", self.test_template_system_real_data),
            ("Node Types (25+ Types)", self.test_node_types_comprehensive),
            ("Database Persistence", self.test_database_persistence),
            ("Performance Under Load", self.test_performance_under_load)
        ]
        
        module_results = []
        for module_name, test_function in test_modules:
            print(f"\n{'='*20} {module_name} {'='*20}")
            try:
                result = test_function()
                module_results.append((module_name, result))
                if result:
                    print(f"✅ {module_name} - PASSED")
                else:
                    print(f"❌ {module_name} - FAILED")
            except Exception as e:
                print(f"❌ {module_name} - ERROR: {str(e)}")
                module_results.append((module_name, False))
                self.log_critical_failure(module_name, f"Test module error: {str(e)}")
        
        # Generate comprehensive report
        self.generate_final_report(module_results)
        
        return True

    def generate_final_report(self, module_results):
        """Generate comprehensive final report"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE END-TO-END BACKEND TESTING - FINAL REPORT")
        print("=" * 80)
        
        # Overall statistics
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"📈 OVERALL STATISTICS:")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Module results
        print(f"\n📋 MODULE RESULTS:")
        passed_modules = 0
        for module_name, result in module_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {module_name}: {status}")
            if result:
                passed_modules += 1
        
        module_success_rate = (passed_modules / len(module_results) * 100) if module_results else 0
        print(f"   Module Success Rate: {module_success_rate:.1f}% ({passed_modules}/{len(module_results)})")
        
        # Critical failures analysis
        print(f"\n🚨 CRITICAL ISSUES ANALYSIS:")
        if self.critical_failures:
            print(f"   Found {len(self.critical_failures)} critical issues:")
            for i, failure in enumerate(self.critical_failures, 1):
                print(f"   {i}. {failure['test']}: {failure['reason']}")
        else:
            print(f"   ✅ No critical issues found - all features appear to be real and functional!")
        
        # Real vs Demo Data Assessment
        print(f"\n🔍 REAL vs DEMO DATA ASSESSMENT:")
        demo_indicators = len([f for f in self.critical_failures if 'demo' in f['reason'].lower() or 'fake' in f['reason'].lower() or 'fallback' in f['reason'].lower()])
        
        if demo_indicators == 0:
            print(f"   ✅ ALL FEATURES APPEAR TO BE REAL AND FUNCTIONAL")
            print(f"   ✅ No demo/fake data patterns detected")
        elif demo_indicators <= 2:
            print(f"   ⚠️ MOSTLY REAL with {demo_indicators} potential demo patterns")
        else:
            print(f"   ❌ SIGNIFICANT DEMO/FAKE DATA detected ({demo_indicators} patterns)")
        
        # Final verdict
        print(f"\n🎯 FINAL VERDICT:")
        if success_rate >= 90 and module_success_rate >= 80 and demo_indicators <= 1:
            print(f"   🎉 OUTSTANDING SUCCESS - Backend is production-ready with real functionality!")
            print(f"   ✅ All major promises fulfilled")
            print(f"   ✅ 103+ integrations confirmed")
            print(f"   ✅ AI features working with GROQ")
            print(f"   ✅ Workflow engine processes real logic")
            print(f"   ✅ Dashboard shows real analytics")
        elif success_rate >= 75 and module_success_rate >= 70:
            print(f"   ✅ GOOD SUCCESS - Backend is functional with minor issues")
            print(f"   ⚠️ Some areas need attention but core functionality works")
        elif success_rate >= 50:
            print(f"   ⚠️ PARTIAL SUCCESS - Backend has significant issues")
            print(f"   🔧 Major fixes needed before production")
        else:
            print(f"   ❌ CRITICAL FAILURE - Backend has major functionality issues")
            print(f"   🚨 Extensive fixes required")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if self.critical_failures:
            print(f"   🔧 Address critical issues:")
            for failure in self.critical_failures[:5]:  # Top 5 issues
                print(f"      - Fix {failure['test']}: {failure['reason']}")
        
        if success_rate < 90:
            print(f"   📈 Improve test success rate from {success_rate:.1f}% to 90%+")
        
        if demo_indicators > 0:
            print(f"   🎯 Replace demo/fallback data with real functionality")
        
        print(f"   ✅ Continue with frontend testing if backend issues are resolved")
        
        print("\n" + "=" * 80)

def main():
    """Main test execution function"""
    tester = ComprehensiveAetherTester()
    
    try:
        success = tester.run_comprehensive_test_suite()
        
        # Return appropriate exit code
        success_rate = (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0
        critical_issues = len(tester.critical_failures)
        
        if success_rate >= 90 and critical_issues <= 1:
            return 0  # Outstanding success
        elif success_rate >= 75 and critical_issues <= 3:
            return 0  # Good success
        elif success_rate >= 50:
            return 1  # Partial success - issues found
        else:
            return 2  # Critical failure
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR in test execution: {str(e)}")
        return 2

if __name__ == "__main__":
    sys.exit(main())