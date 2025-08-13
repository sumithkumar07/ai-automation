import requests
import sys
import json
import time
import uuid
from datetime import datetime

class EnhancedEndpointsTester:
    def __init__(self, base_url="http://localhost:8001"):
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
            "name": f"Enhanced Test User {datetime.now().strftime('%H%M%S')}",
            "email": f"enhanced_test_{datetime.now().strftime('%H%M%S')}@example.com",
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

    def test_comprehensive_health_check(self):
        """Test comprehensive health check endpoint"""
        success, response = self.run_test(
            "Comprehensive Health Check",
            "GET",
            "api/health/comprehensive",
            200
        )
        
        if success:
            if 'services' in response and 'system_metrics' in response:
                print(f"   ✅ Comprehensive health check structure valid")
                services = response['services']
                if 'database' in services and 'ai_provider' in services:
                    print(f"   ✅ All services monitored")
                else:
                    print(f"   ⚠️ Some services missing from health check")
            else:
                print(f"   ⚠️ Comprehensive health response missing expected fields")
        
        return success

    def test_multi_agent_ai_endpoints(self):
        """Test multi-agent AI system endpoints"""
        # Test multi-agent conversation
        conversation_data = {
            "message": "Help me create an automation workflow for processing customer emails",
            "session_id": str(uuid.uuid4())
        }
        
        success1, response1 = self.run_test(
            "Multi-Agent AI Conversation",
            "POST",
            "api/ai/multi-agent/conversation",
            200,
            data=conversation_data
        )

        # Test conversation enhancement
        enhancement_data = {
            "conversation_history": [
                {"role": "user", "content": "I need help with automation"},
                {"role": "assistant", "content": "I can help you with that"}
            ],
            "user_context": {"user_id": self.user_id}
        }
        
        success2, response2 = self.run_test(
            "Enhance Conversation Quality",
            "POST",
            "api/ai/enhance-conversation",
            200,
            data=enhancement_data
        )

        # Test multi-agent performance metrics
        success3, response3 = self.run_test(
            "Multi-Agent Performance Metrics",
            "GET",
            "api/ai/multi-agent/performance",
            200
        )

        return success1 and success2 and success3

    def test_enhanced_integration_library(self):
        """Test enhanced integration library endpoints"""
        # Test get all enhanced integrations
        success1, response1 = self.run_test(
            "Get Enhanced Integrations (200+)",
            "GET",
            "api/integrations/enhanced/all",
            200
        )

        # Test get integrations by category
        success2, response2 = self.run_test(
            "Get Integrations by Category",
            "GET",
            "api/integrations/enhanced/category/communication",
            200
        )

        # Test search enhanced integrations
        success3, response3 = self.run_test(
            "Search Enhanced Integrations",
            "GET",
            "api/integrations/enhanced/search",
            200,
            params={"query": "slack"}
        )

        # Test enhanced integration statistics
        success4, response4 = self.run_test(
            "Enhanced Integration Statistics",
            "GET",
            "api/integrations/enhanced/statistics",
            200
        )

        return success1 and success2 and success3 and success4

    def test_performance_monitoring_endpoints(self):
        """Test performance monitoring and Web Vitals endpoints"""
        # Test record Web Vitals
        web_vitals_data = {
            "lcp": 1200,
            "fid": 50,
            "cls": 0.1,
            "fcp": 800,
            "ttfb": 200,
            "page": "/dashboard",
            "user_agent": "Mozilla/5.0 Test Browser"
        }
        
        success1, response1 = self.run_test(
            "Record Web Vitals",
            "POST",
            "api/performance/web-vitals/record",
            200,
            data=web_vitals_data
        )

        # Test enhanced performance report
        success2, response2 = self.run_test(
            "Enhanced Performance Report",
            "GET",
            "api/performance/enhanced-report",
            200
        )

        # Test auto-optimization
        success3, response3 = self.run_test(
            "Auto Performance Optimization",
            "POST",
            "api/performance/optimize/auto",
            200
        )

        return success1 and success2 and success3

    def test_accessibility_compliance_endpoints(self):
        """Test accessibility compliance endpoints"""
        # Test compliance analysis
        success1, response1 = self.run_test(
            "Accessibility Compliance Analysis",
            "GET",
            "api/accessibility/compliance-analysis",
            200
        )

        # Test accessibility preferences
        preferences_data = {
            "high_contrast": True,
            "reduced_motion": False,
            "large_text": True,
            "screen_reader_optimized": True
        }
        
        success2, response2 = self.run_test(
            "Set Accessibility Preferences",
            "POST",
            "api/accessibility/preferences",
            200,
            data=preferences_data
        )

        # Test quick accessibility fixes
        success3, response3 = self.run_test(
            "Get Quick Accessibility Fixes",
            "GET",
            "api/accessibility/quick-fixes",
            200
        )

        # Test accessibility guidelines
        success4, response4 = self.run_test(
            "Get Accessibility Guidelines",
            "GET",
            "api/accessibility/guidelines",
            200
        )

        return success1 and success2 and success3 and success4

    def test_enhanced_system_status(self):
        """Test enhanced system status endpoint"""
        success, response = self.run_test(
            "Enhanced System Status",
            "GET",
            "api/enhanced/system-status",
            200
        )
        
        if success:
            if 'system_components' in response and 'enhancement_levels' in response:
                print(f"   ✅ Enhanced system status structure valid")
                components = response['system_components']
                if 'multi_agent_ai' in components and 'integration_library' in components:
                    print(f"   ✅ All enhanced components monitored")
                else:
                    print(f"   ⚠️ Some enhanced components missing")
            else:
                print(f"   ⚠️ Enhanced system status missing expected fields")
        
        return success

    def test_groq_ai_intelligence_endpoints(self):
        """Test GROQ AI intelligence endpoints"""
        # Test AI dashboard insights
        success1, response1 = self.run_test(
            "AI Dashboard Insights (GROQ)",
            "GET",
            "api/ai/dashboard-insights",
            200
        )

        # Test smart workflow suggestions
        success2, response2 = self.run_test(
            "Smart Workflow Suggestions (GROQ)",
            "POST",
            "api/ai/smart-suggestions",
            200
        )

        # Test predictive insights
        success3, response3 = self.run_test(
            "Predictive AI Insights",
            "POST",
            "api/ai/predictive-insights",
            200
        )

        # Test natural language workflow generation
        natural_workflow_data = {
            "message": "Create a workflow that automatically backs up files to cloud storage every day"
        }
        
        success4, response4 = self.run_test(
            "Natural Language Workflow Generation (GROQ)",
            "POST",
            "api/ai/generate-natural-workflow",
            200,
            data=natural_workflow_data
        )

        return success1 and success2 and success3 and success4

def main():
    print("🚀 Starting Enhanced Endpoints Testing - Aether Automation Platform")
    print("Testing all enhanced features from the 5-phase enhancement system")
    print("=" * 80)
    
    # Initialize tester
    tester = EnhancedEndpointsTester("http://localhost:8001")
    
    # Authentication
    print("\n📝 AUTHENTICATION SETUP")
    print("-" * 40)
    if not tester.test_signup():
        print("❌ Authentication failed, stopping tests")
        return 1
    
    # Enhanced Health Monitoring
    print("\n🏥 ENHANCED HEALTH MONITORING")
    print("-" * 40)
    tester.test_comprehensive_health_check()
    tester.test_enhanced_system_status()
    
    # Multi-Agent AI System
    print("\n🤖 MULTI-AGENT AI SYSTEM (GROQ-POWERED)")
    print("-" * 40)
    tester.test_multi_agent_ai_endpoints()
    tester.test_groq_ai_intelligence_endpoints()
    
    # Enhanced Integration Library
    print("\n🔗 ENHANCED INTEGRATION LIBRARY (200+ INTEGRATIONS)")
    print("-" * 40)
    tester.test_enhanced_integration_library()
    
    # Performance Monitoring & Web Vitals
    print("\n⚡ PERFORMANCE MONITORING & WEB VITALS")
    print("-" * 40)
    tester.test_performance_monitoring_endpoints()
    
    # Accessibility Compliance
    print("\n🎨 ACCESSIBILITY COMPLIANCE (WCAG 2.2)")
    print("-" * 40)
    tester.test_accessibility_compliance_endpoints()
    
    # Print final results
    print("\n" + "=" * 80)
    print(f"📊 ENHANCED ENDPOINTS TEST RESULTS")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    success_rate = (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("✅ Enhanced endpoints tests HIGHLY SUCCESSFUL!")
        return 0
    elif success_rate >= 80:
        print("✅ Enhanced endpoints tests SUCCESSFUL!")
        return 0
    elif success_rate >= 70:
        print("⚠️ Enhanced endpoints tests MOSTLY SUCCESSFUL - minor issues found")
        return 0
    elif success_rate >= 50:
        print("⚠️ Enhanced endpoints tests PARTIALLY SUCCESSFUL - some issues found")
        return 0
    else:
        print("❌ Enhanced endpoints tests FAILED - major issues found")
        return 1

if __name__ == "__main__":
    sys.exit(main())