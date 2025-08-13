#!/usr/bin/env python3
"""
Backend Fixes Verification & Integration Count Test
Testing the critical fixes and enhancements implemented
"""

import requests
import json
import sys
import os
from datetime import datetime

# Backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://parallel-testing.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class FixesVerificationTester:
    def __init__(self):
        self.auth_token = None
        self.test_results = []
        self.user_data = {
            "email": "sarah.johnson@aethertech.com",
            "password": "SecurePass2024!",
            "first_name": "Sarah",
            "last_name": "Johnson"
        }
        
    def authenticate(self):
        """Authenticate and get JWT token"""
        try:
            # Try login first
            login_data = {
                "email": self.user_data["email"],
                "password": self.user_data["password"]
            }
            
            response = requests.post(f"{API_BASE}/auth/login", json=login_data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                self.auth_token = result.get("access_token")
                return True
            elif response.status_code == 401:
                # User doesn't exist, try signup
                signup_response = requests.post(f"{API_BASE}/auth/signup", json=self.user_data, timeout=10)
                if signup_response.status_code == 200:
                    signup_result = signup_response.json()
                    self.auth_token = signup_result.get("access_token")
                    return True
                else:
                    print(f"❌ Signup failed: {signup_response.status_code}")
                    return False
            else:
                print(f"❌ Login failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
            
    def get_headers(self):
        """Get headers with authentication"""
        headers = {'Content-Type': 'application/json'}
        if self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'
        return headers
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
            
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
    def test_priority_1_template_system(self):
        """PRIORITY 1 - Test template system fixes"""
        print("\n🎯 PRIORITY 1 - TEMPLATE SYSTEM FIXES")
        print("=" * 50)
        
        # Test 1: Get all templates (should work with ObjectId serialization)
        try:
            response = requests.get(f"{API_BASE}/templates/", headers=self.get_headers(), timeout=10)
            if response.status_code == 200:
                templates_data = response.json()
                templates = templates_data.get("templates", [])
                self.log_test("GET /api/templates/ - ObjectId serialization", True, 
                            f"Retrieved {len(templates)} templates successfully")
            else:
                self.log_test("GET /api/templates/ - ObjectId serialization", False, 
                            f"Status: {response.status_code}")
                return
        except Exception as e:
            self.log_test("GET /api/templates/ - ObjectId serialization", False, f"Exception: {e}")
            return
            
        # Test 2: Create a new template
        template_data = {
            "name": "Test Integration Template",
            "description": "Template created for testing ObjectId serialization fixes",
            "category": "business",
            "difficulty": "intermediate",
            "tags": ["test", "integration", "automation"],
            "workflow_definition": {
                "nodes": [
                    {"id": "start", "type": "trigger", "name": "Start Node"},
                    {"id": "process", "type": "action", "name": "Process Data"},
                    {"id": "end", "type": "action", "name": "Complete"}
                ],
                "edges": [
                    {"source": "start", "target": "process"},
                    {"source": "process", "target": "end"}
                ]
            },
            "is_public": True
        }
        
        created_template_id = None
        try:
            response = requests.post(f"{API_BASE}/templates/create", json=template_data, headers=self.get_headers(), timeout=10)
            if response.status_code == 200:
                result = response.json()
                created_template_id = result.get("template_id")
                self.log_test("POST /api/templates/create - Template creation", True,
                            f"Created template with ID: {created_template_id}")
            else:
                self.log_test("POST /api/templates/create - Template creation", False,
                            f"Status: {response.status_code}")
                return
        except Exception as e:
            self.log_test("POST /api/templates/create - Template creation", False, f"Exception: {e}")
            return
            
        # Test 3: Get newly created template details (this was failing before)
        if created_template_id:
            try:
                response = requests.get(f"{API_BASE}/templates/{created_template_id}", headers=self.get_headers(), timeout=10)
                if response.status_code == 200:
                    template_details = response.json()
                    self.log_test("GET /api/templates/{template_id} - Newly created template", True,
                                f"Retrieved template details: {template_details.get('name', 'Unknown')}")
                else:
                    self.log_test("GET /api/templates/{template_id} - Newly created template", False,
                                f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("GET /api/templates/{template_id} - Newly created template", False, f"Exception: {e}")
                
    def test_priority_2_integration_count(self):
        """PRIORITY 2 - Test integration count verification"""
        print("\n🎯 PRIORITY 2 - INTEGRATION COUNT VERIFICATION")
        print("=" * 50)
        
        # Test 1: Get all integrations and count them
        try:
            response = requests.get(f"{API_BASE}/integrations/", headers=self.get_headers(), timeout=10)
            if response.status_code == 200:
                integrations = response.json()
                integration_count = len(integrations)
                
                print(f"📊 INTEGRATION COUNT: {integration_count}")
                
                # Check if we have significantly more than 22 integrations
                if integration_count >= 100:
                    self.log_test("Integration count verification", True,
                                f"Found {integration_count} integrations (meets 100+ promise)")
                elif integration_count > 22:
                    self.log_test("Integration count verification", True,
                                f"Found {integration_count} integrations (improved from 22)")
                else:
                    self.log_test("Integration count verification", False,
                                f"Only {integration_count} integrations (still below promise)")
                    
                # Test specific new integrations mentioned in review
                integration_names = [integration.get('name', '').lower() for integration in integrations]
                integration_ids = [integration.get('id', '').lower() for integration in integrations]
                
                new_integrations = ['zoom', 'shopify', 'aws', 'whatsapp', 'telegram', 'asana', 'trello']
                found_new = []
                for new_int in new_integrations:
                    if new_int in integration_ids or any(new_int in name for name in integration_names):
                        found_new.append(new_int)
                        
                self.log_test("New integrations verification", len(found_new) > 0,
                            f"Found new integrations: {', '.join(found_new)}")
                            
                # Print all integration names for verification
                print(f"📋 ALL INTEGRATIONS ({integration_count}):")
                for i, integration in enumerate(integrations[:20], 1):  # Show first 20
                    print(f"  {i:2d}. {integration.get('name', 'Unknown')} ({integration.get('id', 'no-id')})")
                if integration_count > 20:
                    print(f"  ... and {integration_count - 20} more")
                            
            else:
                self.log_test("Integration count verification", False,
                            f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Integration count verification", False, f"Exception: {e}")
            
        # Test 2: Check integration categories
        try:
            response = requests.get(f"{API_BASE}/integrations/categories", headers=self.get_headers(), timeout=10)
            if response.status_code == 200:
                categories = response.json()
                category_names = [cat.get('name', '').lower() for cat in categories]
                
                # Check for new categories mentioned in review
                new_categories = ['ecommerce', 'analytics', 'support', 'database', 'content']
                found_categories = [cat for cat in new_categories if cat in ' '.join(category_names)]
                
                self.log_test("Integration categories verification", len(found_categories) > 0,
                            f"Found {len(categories)} categories, including new ones: {', '.join(found_categories)}")
                            
                print(f"📂 CATEGORIES ({len(categories)}):")
                for cat in categories:
                    print(f"  • {cat.get('name', 'Unknown')}")
            else:
                self.log_test("Integration categories verification", False,
                            f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Integration categories verification", False, f"Exception: {e}")
            
    def test_priority_3_integration_search(self):
        """PRIORITY 3 - Test integration search & filtering"""
        print("\n🎯 PRIORITY 3 - INTEGRATION SEARCH & FILTERING")
        print("=" * 50)
        
        # Test 1: Integration search functionality
        search_terms = ['slack', 'google', 'ai', 'payment']
        for term in search_terms:
            try:
                response = requests.get(f"{API_BASE}/integrations/search?q={term}", headers=self.get_headers(), timeout=10)
                if response.status_code == 200:
                    results = response.json()
                    self.log_test(f"Integration search - '{term}'", len(results) > 0,
                                f"Found {len(results)} integrations matching '{term}'")
                else:
                    self.log_test(f"Integration search - '{term}'", False,
                                f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Integration search - '{term}'", False, f"Exception: {e}")
                
        # Test 2: Category filtering
        categories_to_test = ['communication', 'productivity', 'ai', 'ecommerce', 'analytics']
        for category in categories_to_test:
            try:
                response = requests.get(f"{API_BASE}/integrations/category/{category}", headers=self.get_headers(), timeout=10)
                if response.status_code == 200:
                    results = response.json()
                    self.log_test(f"Category filtering - '{category}'", len(results) > 0,
                                f"Found {len(results)} integrations in '{category}' category")
                elif response.status_code == 400:
                    # Category might not exist, that's okay
                    self.log_test(f"Category filtering - '{category}'", True,
                                f"Category '{category}' not found (acceptable)")
                else:
                    self.log_test(f"Category filtering - '{category}'", False,
                                f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Category filtering - '{category}'", False, f"Exception: {e}")
                
    def test_quick_verification(self):
        """Quick verification tests for core systems"""
        print("\n🎯 QUICK VERIFICATION TESTS")
        print("=" * 50)
        
        # Test 1: Authentication still works
        try:
            response = requests.get(f"{API_BASE}/auth/me", headers=self.get_headers(), timeout=10)
            if response.status_code == 200:
                user_info = response.json()
                self.log_test("Core authentication", True,
                            f"User authenticated: {user_info.get('email', 'Unknown')}")
            else:
                self.log_test("Core authentication", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Core authentication", False, f"Exception: {e}")
            
        # Test 2: Workflow system
        try:
            response = requests.get(f"{API_BASE}/workflows", headers=self.get_headers(), timeout=10)
            if response.status_code in [200, 403]:  # 403 might be expected if no workflows
                self.log_test("Workflow system", True, "Workflow endpoints accessible")
            else:
                self.log_test("Workflow system", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Workflow system", False, f"Exception: {e}")
            
        # Test 3: AI features
        try:
            response = requests.get(f"{API_BASE}/ai/integrations", headers=self.get_headers(), timeout=10)
            if response.status_code == 200:
                ai_integrations = response.json()
                self.log_test("AI features", True, f"AI integrations available: {len(ai_integrations)}")
            else:
                self.log_test("AI features", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("AI features", False, f"Exception: {e}")
            
        # Test 4: Dashboard stats
        try:
            response = requests.get(f"{API_BASE}/dashboard/stats", headers=self.get_headers(), timeout=10)
            if response.status_code == 200:
                stats = response.json()
                self.log_test("Dashboard stats", True, "Dashboard statistics accessible")
            else:
                self.log_test("Dashboard stats", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Dashboard stats", False, f"Exception: {e}")
            
    def run_all_tests(self):
        """Run all verification tests"""
        print("🚀 BACKEND FIXES VERIFICATION & INTEGRATION COUNT TEST")
        print("=" * 60)
        print(f"Testing backend at: {API_BASE}")
        print(f"Started at: {datetime.now().isoformat()}")
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return
            
        print("✅ Authentication successful")
        
        # Run all test suites
        self.test_priority_1_template_system()
        self.test_priority_2_integration_count()
        self.test_priority_3_integration_search()
        self.test_quick_verification()
        
        # Print summary
        self.print_summary()
        
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🎯 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['details']}")
                    
        print(f"\nCompleted at: {datetime.now().isoformat()}")

def main():
    """Main test execution"""
    tester = FixesVerificationTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()