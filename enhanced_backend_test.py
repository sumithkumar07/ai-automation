import requests
import sys
import json
import time
import uuid
from datetime import datetime

class EnhancedBackendTester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
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
        """Test user signup for authentication"""
        test_user_data = {
            "name": f"Enhanced Test User {datetime.now().strftime('%H%M%S')}",
            "email": f"enhanced_test_{datetime.now().strftime('%H%M%S')}@example.com",
            "password": "password123"
        }
        
        success, response = self.run_test(
            "User Signup for Enhanced Tests",
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

    # ENHANCED NODE LIBRARY TESTS
    def test_enhanced_nodes(self):
        """Test enhanced node library endpoint"""
        success, response = self.run_test(
            "Enhanced Node Library",
            "GET",
            "api/nodes/enhanced",
            200
        )
        
        if success:
            if 'categories' in response and 'total_nodes' in response:
                total_nodes = response.get('total_nodes', 0)
                total_categories = response.get('total_categories', 0)
                print(f"   ✅ Enhanced nodes loaded: {total_nodes} nodes in {total_categories} categories")
                
                # Check if we have the expected enhanced nodes (30+ new types)
                if total_nodes >= 120:  # Should have 120+ nodes now
                    print(f"   ✅ Node library expansion successful (120+ nodes)")
                else:
                    print(f"   ⚠️ Node count lower than expected: {total_nodes}")
                    
                # Check for enhanced categories
                categories = response.get('categories', {})
                if 'configurations' in response and 'templates' in response:
                    print(f"   ✅ Node configurations and templates included")
                else:
                    print(f"   ⚠️ Missing configurations or templates")
            else:
                print(f"   ⚠️ Enhanced nodes response missing expected fields")
        
        return success

    def test_node_search(self):
        """Test node search functionality"""
        success1, response1 = self.run_test(
            "Node Search with Query",
            "GET",
            "api/nodes/search",
            200,
            params={"query": "ai", "category": "ai"}
        )
        
        if success1:
            if 'nodes' in response1 and 'total' in response1:
                total_found = response1.get('total', 0)
                print(f"   ✅ Found {total_found} AI nodes")
                
                # Check search filters
                query = response1.get('query', '')
                category = response1.get('category', '')
                if query == 'ai' and category == 'ai':
                    print(f"   ✅ Search filters applied correctly")
                else:
                    print(f"   ⚠️ Search filters not applied correctly")
            else:
                print(f"   ⚠️ Node search response missing expected fields")
        
        return success1

    # ENHANCED INTEGRATIONS TESTS
    def test_enhanced_integrations(self):
        """Test enhanced integrations endpoint"""
        success, response = self.run_test(
            "Enhanced Integrations",
            "GET",
            "api/integrations/enhanced",
            200
        )
        
        if success:
            if 'categories' in response and 'total_integrations' in response:
                total_integrations = response.get('total_integrations', 0)
                total_categories = response.get('total_categories', 0)
                print(f"   ✅ Enhanced integrations loaded: {total_integrations} integrations in {total_categories} categories")
                
                # Check if we have the expected enhanced integrations (25+ new platforms)
                if total_integrations >= 145:  # Should have 145+ integrations now (120 + 25)
                    print(f"   ✅ Integration expansion successful (145+ integrations)")
                else:
                    print(f"   ⚠️ Integration count lower than expected: {total_integrations}")
                    
                # Check for capabilities and OAuth configs
                if 'capabilities' in response and 'oauth_configurations' in response:
                    print(f"   ✅ Integration capabilities and OAuth configs included")
                else:
                    print(f"   ⚠️ Missing capabilities or OAuth configurations")
            else:
                print(f"   ⚠️ Enhanced integrations response missing expected fields")
        
        return success

    def test_advanced_integration_testing(self):
        """Test advanced integration testing"""
        test_data = {
            "platform": "slack",
            "credentials": {
                "token": "test_token_123"
            },
            "test_operations": ["connection", "read", "write"]
        }
        
        success, response = self.run_test(
            "Advanced Integration Testing",
            "POST",
            "api/integrations/test-advanced",
            200,
            data=test_data
        )
        
        if success:
            if 'test_results' in response and 'overall_status' in response:
                overall_status = response.get('overall_status', '')
                test_results = response.get('test_results', {})
                print(f"   ✅ Advanced integration test completed: {overall_status}")
                print(f"   Operations tested: {list(test_results.keys())}")
                
                # Check if all operations were tested
                expected_ops = ["connection", "read", "write"]
                if all(op in test_results for op in expected_ops):
                    print(f"   ✅ All test operations completed")
                else:
                    print(f"   ⚠️ Some test operations missing")
            else:
                print(f"   ⚠️ Advanced integration test response missing expected fields")
        
        return success

    # ADVANCED AI CAPABILITIES TESTS
    def test_ai_generate_code(self):
        """Test AI code generation endpoint"""
        code_request = {
            "prompt": "Create a Python function to calculate fibonacci numbers",
            "language": "python",
            "style": "clean"
        }
        
        success, response = self.run_test(
            "AI Code Generation",
            "POST",
            "api/ai/generate-code",
            200,
            data=code_request
        )
        
        if success:
            if 'code' in response or 'generated_code' in response:
                print(f"   ✅ AI code generation successful")
            else:
                print(f"   ⚠️ AI code generation response missing code field")
        
        return success

    def test_ai_analyze_sentiment(self):
        """Test AI sentiment analysis endpoint"""
        sentiment_request = {
            "text": "I love this new automation platform! It's amazing and very helpful.",
            "detailed": True
        }
        
        success, response = self.run_test(
            "AI Sentiment Analysis",
            "POST",
            "api/ai/analyze-sentiment",
            200,
            data=sentiment_request
        )
        
        if success:
            if 'sentiment' in response or 'analysis' in response:
                print(f"   ✅ AI sentiment analysis successful")
            else:
                print(f"   ⚠️ AI sentiment analysis response missing expected fields")
        
        return success

    def test_ai_extract_entities(self):
        """Test AI entity extraction endpoint"""
        entity_request = {
            "text": "John Smith works at Microsoft in Seattle and can be reached at john@microsoft.com",
            "entity_types": ["person", "organization", "location", "email"]
        }
        
        success, response = self.run_test(
            "AI Entity Extraction",
            "POST",
            "api/ai/extract-entities",
            200,
            data=entity_request
        )
        
        if success:
            if 'entities' in response or 'extracted_entities' in response:
                print(f"   ✅ AI entity extraction successful")
            else:
                print(f"   ⚠️ AI entity extraction response missing expected fields")
        
        return success

    def test_ai_summarize(self):
        """Test AI content summarization endpoint"""
        summary_request = {
            "content": "Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals. Leading AI textbooks define the field as the study of intelligent agents: any device that perceives its environment and takes actions that maximize its chance of successfully achieving its goals. Colloquially, the term artificial intelligence is often used to describe machines that mimic cognitive functions that humans associate with the human mind, such as learning and problem solving.",
            "style": "concise",
            "length": "short"
        }
        
        success, response = self.run_test(
            "AI Content Summarization",
            "POST",
            "api/ai/summarize",
            200,
            data=summary_request
        )
        
        if success:
            if 'summary' in response or 'summarized_content' in response:
                print(f"   ✅ AI content summarization successful")
            else:
                print(f"   ⚠️ AI summarization response missing expected fields")
        
        return success

    def test_ai_classify(self):
        """Test AI content classification endpoint"""
        classification_request = {
            "content": "This is a technical article about machine learning algorithms and neural networks",
            "categories": ["technology", "science", "business", "entertainment"],
            "multi_label": False
        }
        
        success, response = self.run_test(
            "AI Content Classification",
            "POST",
            "api/ai/classify",
            200,
            data=classification_request
        )
        
        if success:
            if 'classification' in response or 'predicted_category' in response:
                print(f"   ✅ AI content classification successful")
            else:
                print(f"   ⚠️ AI classification response missing expected fields")
        
        return success

    def test_ai_detect_language(self):
        """Test AI language detection endpoint"""
        success, response = self.run_test(
            "AI Language Detection",
            "POST",
            "api/ai/detect-language",
            200,
            params={"text": "Bonjour, comment allez-vous? Je suis très heureux de vous rencontrer."}
        )
        
        if success:
            if 'language' in response or 'detected_language' in response:
                print(f"   ✅ AI language detection successful")
            else:
                print(f"   ⚠️ AI language detection response missing expected fields")
        
        return success

    # PERFORMANCE MONITORING TESTS
    def test_performance_metrics(self):
        """Test performance metrics endpoint"""
        success, response = self.run_test(
            "Performance Metrics",
            "GET",
            "api/performance/metrics",
            200,
            params={"hours_back": 24}
        )
        
        if success:
            if 'metrics' in response and 'monitoring_status' in response:
                monitoring_status = response.get('monitoring_status', '')
                print(f"   ✅ Performance monitoring active: {monitoring_status}")
                
                # Check for recent alerts
                if 'recent_alerts' in response:
                    alerts_count = len(response.get('recent_alerts', []))
                    print(f"   Recent alerts: {alerts_count}")
                else:
                    print(f"   ⚠️ Recent alerts field missing")
            else:
                print(f"   ⚠️ Performance metrics response missing expected fields")
        
        return success

    def test_cache_stats(self):
        """Test cache statistics endpoint"""
        success, response = self.run_test(
            "Cache Statistics",
            "GET",
            "api/performance/cache-stats",
            200
        )
        
        if success:
            if 'cache_stats' in response and 'hit_rates' in response:
                hit_rates = response.get('hit_rates', {})
                memory_cache_size = response.get('memory_cache_size', 0)
                redis_available = response.get('redis_available', False)
                
                print(f"   ✅ Cache statistics retrieved")
                print(f"   Memory cache size: {memory_cache_size}")
                print(f"   Redis available: {redis_available}")
                print(f"   Hit rates: {list(hit_rates.keys())}")
            else:
                print(f"   ⚠️ Cache stats response missing expected fields")
        
        return success

    # REAL-TIME COLLABORATION TESTS
    def test_collaboration_join(self):
        """Test joining collaboration session"""
        join_request = {
            "workflow_id": str(uuid.uuid4()),
            "user_name": "Test User"
        }
        
        success, response = self.run_test(
            "Join Collaboration Session",
            "POST",
            "api/collaboration/join",
            200,
            data=join_request
        )
        
        if success:
            if 'session_id' in response or 'joined' in response:
                print(f"   ✅ Collaboration session joined successfully")
            else:
                print(f"   ⚠️ Collaboration join response missing expected fields")
        
        return success

    def test_collaboration_sessions(self):
        """Test getting collaboration sessions"""
        success, response = self.run_test(
            "Get Collaboration Sessions",
            "GET",
            "api/collaboration/sessions",
            200
        )
        
        if success:
            if 'active_sessions' in response and 'total_sessions' in response:
                total_sessions = response.get('total_sessions', 0)
                print(f"   ✅ Active collaboration sessions: {total_sessions}")
                
                if 'recent_events' in response:
                    events_count = len(response.get('recent_events', []))
                    print(f"   Recent events: {events_count}")
            else:
                print(f"   ⚠️ Collaboration sessions response missing expected fields")
        
        return success

    # ENHANCED TEMPLATES TESTS
    def test_enhanced_templates(self):
        """Test enhanced templates endpoint"""
        success, response = self.run_test(
            "Enhanced Templates",
            "GET",
            "api/templates/enhanced",
            200
        )
        
        if success:
            if 'templates' in response and 'total_templates' in response:
                total_templates = response.get('total_templates', 0)
                categories = response.get('categories', [])
                difficulties = response.get('difficulties', [])
                
                print(f"   ✅ Enhanced templates loaded: {total_templates} templates")
                print(f"   Categories: {len(categories)}")
                print(f"   Difficulties: {difficulties}")
                
                # Check for specific enhanced templates
                templates = response.get('templates', {})
                enhanced_template_names = ['ai_content_pipeline', 'financial_automation', 'healthcare_workflow']
                found_enhanced = sum(1 for name in enhanced_template_names if name in templates)
                
                if found_enhanced >= 2:
                    print(f"   ✅ Enhanced templates found: {found_enhanced}/3")
                else:
                    print(f"   ⚠️ Few enhanced templates found: {found_enhanced}/3")
            else:
                print(f"   ⚠️ Enhanced templates response missing expected fields")
        
        return success

    def test_create_template(self):
        """Test creating workflow template"""
        template_data = {
            "name": "Test Enhanced Template",
            "description": "A test template for enhanced features",
            "category": "testing",
            "difficulty": "beginner",
            "nodes": [
                {
                    "id": "node1",
                    "type": "trigger",
                    "name": "Test Trigger"
                }
            ],
            "connections": [],
            "triggers": []
        }
        
        success, response = self.run_test(
            "Create Workflow Template",
            "POST",
            "api/templates/create",
            200,
            data=template_data
        )
        
        if success:
            if 'template_id' in response and 'message' in response:
                template_id = response.get('template_id', '')
                print(f"   ✅ Template created successfully: {template_id}")
            else:
                print(f"   ⚠️ Template creation response missing expected fields")
        
        return success

    # SYSTEM DIAGNOSTICS TESTS
    def test_system_diagnostics(self):
        """Test system diagnostics endpoint"""
        success, response = self.run_test(
            "System Diagnostics",
            "GET",
            "api/system/diagnostics",
            200
        )
        
        if success:
            if 'system' in response and 'application' in response:
                system_info = response.get('system', {})
                app_info = response.get('application', {})
                status = response.get('status', '')
                
                print(f"   ✅ System diagnostics retrieved")
                print(f"   System status: {status}")
                
                # Check system metrics
                if 'cpu_usage' in system_info and 'memory_usage' in system_info:
                    cpu_usage = system_info.get('cpu_usage', 0)
                    memory_usage = system_info.get('memory_usage', 0)
                    print(f"   CPU usage: {cpu_usage}%")
                    print(f"   Memory usage: {memory_usage}%")
                
                # Check application metrics
                if 'cache_performance' in app_info:
                    print(f"   ✅ Application metrics included")
                else:
                    print(f"   ⚠️ Application metrics missing")
            else:
                print(f"   ⚠️ System diagnostics response missing expected fields")
        
        return success

def main():
    print("🚀 Starting Enhanced Backend Features Testing")
    print("=" * 60)
    
    # Initialize tester
    tester = EnhancedBackendTester("http://localhost:8001")
    
    # Authentication
    print("\n📝 AUTHENTICATION")
    print("-" * 30)
    if not tester.test_signup():
        print("❌ Authentication failed, stopping tests")
        return 1
    
    # Enhanced Node Library Tests
    print("\n🔧 ENHANCED NODE LIBRARY TESTS")
    print("-" * 30)
    tester.test_enhanced_nodes()
    tester.test_node_search()
    
    # Enhanced Integrations Tests
    print("\n🔗 ENHANCED INTEGRATIONS TESTS")
    print("-" * 30)
    tester.test_enhanced_integrations()
    tester.test_advanced_integration_testing()
    
    # Advanced AI Capabilities Tests
    print("\n🤖 ADVANCED AI CAPABILITIES TESTS")
    print("-" * 30)
    tester.test_ai_generate_code()
    tester.test_ai_analyze_sentiment()
    tester.test_ai_extract_entities()
    tester.test_ai_summarize()
    tester.test_ai_classify()
    tester.test_ai_detect_language()
    
    # Performance Monitoring Tests
    print("\n📊 PERFORMANCE MONITORING TESTS")
    print("-" * 30)
    tester.test_performance_metrics()
    tester.test_cache_stats()
    
    # Real-time Collaboration Tests
    print("\n👥 REAL-TIME COLLABORATION TESTS")
    print("-" * 30)
    tester.test_collaboration_join()
    tester.test_collaboration_sessions()
    
    # Enhanced Templates Tests
    print("\n📋 ENHANCED TEMPLATES TESTS")
    print("-" * 30)
    tester.test_enhanced_templates()
    tester.test_create_template()
    
    # System Diagnostics Tests
    print("\n🏥 SYSTEM DIAGNOSTICS TESTS")
    print("-" * 30)
    tester.test_system_diagnostics()
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 ENHANCED BACKEND FEATURES TEST RESULTS")
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