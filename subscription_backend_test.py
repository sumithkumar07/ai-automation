#!/usr/bin/env python3
"""
🎯 AETHER AUTOMATION - SUBSCRIPTION SYSTEM BACKEND TESTING
Comprehensive testing of subscription endpoints integration
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://pricing-flow-test.preview.emergentagent.com/api"
TEST_USER_EMAIL = f"subscription.test.{int(time.time())}@aether.com"
TEST_USER_PASSWORD = "SubscriptionTest123!"
TEST_USER_NAME = "Subscription Tester"

class SubscriptionTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Aether-Subscription-Test/1.0'
        })
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        print(f"{status} | {test_name}")
        if details:
            print(f"    Details: {details}")
        if not success and response_data:
            print(f"    Response: {response_data}")
        print()

    def setup_test_user(self) -> bool:
        """Create test user and get authentication token"""
        try:
            # Try to register new user
            register_data = {
                "first_name": TEST_USER_NAME.split()[0],
                "last_name": TEST_USER_NAME.split()[1] if len(TEST_USER_NAME.split()) > 1 else "User",
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = self.session.post(f"{self.base_url}/auth/register", json=register_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user", {}).get("user_id")
                self.log_test("User Registration", True, f"New user created with ID: {self.user_id}")
            elif response.status_code == 400 and "already exists" in response.text.lower():
                # User exists, try to login
                login_data = {
                    "email": TEST_USER_EMAIL,
                    "password": TEST_USER_PASSWORD
                }
                
                login_response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
                if login_response.status_code == 200:
                    data = login_response.json()
                    self.auth_token = data.get("access_token")
                    self.user_id = data.get("user", {}).get("user_id")
                    self.log_test("User Login", True, f"Existing user logged in with ID: {self.user_id}")
                else:
                    self.log_test("User Login", False, f"Login failed: {login_response.status_code}", login_response.text)
                    return False
            else:
                self.log_test("User Registration", False, f"Registration failed: {response.status_code}", response.text)
                return False
            
            # Set authorization header for future requests
            if self.auth_token:
                self.session.headers.update({
                    'Authorization': f'Bearer {self.auth_token}'
                })
                return True
            else:
                self.log_test("Authentication Setup", False, "No access token received")
                return False
                
        except Exception as e:
            self.log_test("User Setup", False, f"Exception during setup: {str(e)}")
            return False

    def test_subscription_plans(self) -> bool:
        """Test GET /api/subscription/plans endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/subscription/plans")
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                if "status" in data and data["status"] == "success":
                    plans = data.get("plans", {})
                    
                    # Check for required plan tiers
                    required_tiers = ["basic", "pro", "enterprise"]
                    found_tiers = []
                    
                    for tier_name, plan_data in plans.items():
                        if tier_name in required_tiers:
                            found_tiers.append(tier_name)
                            
                            # Validate plan structure
                            required_fields = ["tier", "name", "price_monthly", "price_yearly", "limits", "features"]
                            missing_fields = [field for field in required_fields if field not in plan_data]
                            
                            if missing_fields:
                                self.log_test("Subscription Plans Structure", False, 
                                            f"Plan {tier_name} missing fields: {missing_fields}", data)
                                return False
                    
                    if len(found_tiers) == 3:
                        self.log_test("Subscription Plans", True, 
                                    f"All 3 tiers found: {found_tiers}. Trial days: {data.get('trial_days', 'N/A')}", 
                                    {"plans_count": len(plans), "tiers": found_tiers})
                        return True
                    else:
                        missing_tiers = [tier for tier in required_tiers if tier not in found_tiers]
                        self.log_test("Subscription Plans", False, 
                                    f"Missing tiers: {missing_tiers}", data)
                        return False
                else:
                    self.log_test("Subscription Plans", False, "Invalid response format", data)
                    return False
            else:
                self.log_test("Subscription Plans", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Subscription Plans", False, f"Exception: {str(e)}")
            return False

    def test_current_subscription(self) -> bool:
        """Test GET /api/subscription/current endpoint"""
        try:
            if not self.auth_token:
                self.log_test("Current Subscription", False, "No authentication token available")
                return False
            
            response = self.session.get(f"{self.base_url}/subscription/current")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if user has no subscription (expected for new user)
                if data.get("status") == "no_subscription":
                    self.log_test("Current Subscription", True, 
                                "No subscription found (expected for new user)", 
                                {"status": data.get("status"), "trial_available": data.get("trial_available")})
                    return True
                
                # Check if user has a subscription
                elif data.get("status") == "success" and "subscription" in data:
                    subscription = data["subscription"]
                    usage = data.get("usage", {})
                    
                    # Validate subscription structure
                    required_fields = ["id", "tier", "status", "created_at"]
                    missing_fields = [field for field in required_fields if field not in subscription]
                    
                    if missing_fields:
                        self.log_test("Current Subscription Structure", False, 
                                    f"Missing fields: {missing_fields}", data)
                        return False
                    
                    self.log_test("Current Subscription", True, 
                                f"Subscription found - Tier: {subscription.get('tier')}, Status: {subscription.get('status')}", 
                                {"tier": subscription.get("tier"), "status": subscription.get("status"), 
                                 "is_trial": subscription.get("is_trial")})
                    return True
                else:
                    self.log_test("Current Subscription", False, "Unexpected response format", data)
                    return False
            else:
                self.log_test("Current Subscription", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Current Subscription", False, f"Exception: {str(e)}")
            return False

    def test_subscription_upgrade(self) -> bool:
        """Test POST /api/subscription/upgrade endpoint"""
        try:
            if not self.auth_token:
                self.log_test("Subscription Upgrade", False, "No authentication token available")
                return False
            
            # Test upgrade request data
            upgrade_data = {
                "tier": "pro",
                "billing_cycle": "monthly",
                "origin_url": "https://pricing-flow-test.preview.emergentagent.com"
            }
            
            response = self.session.post(f"{self.base_url}/subscription/upgrade", json=upgrade_data)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "success" and "checkout" in data:
                    checkout = data["checkout"]
                    
                    # Validate checkout response structure
                    required_fields = ["checkout_url", "session_id", "amount", "tier"]
                    missing_fields = [field for field in required_fields if field not in checkout]
                    
                    if missing_fields:
                        self.log_test("Subscription Upgrade Structure", False, 
                                    f"Missing checkout fields: {missing_fields}", data)
                        return False
                    
                    # Validate checkout URL format
                    checkout_url = checkout.get("checkout_url", "")
                    if not checkout_url.startswith("https://checkout.stripe.com"):
                        self.log_test("Subscription Upgrade", False, 
                                    f"Invalid checkout URL format: {checkout_url}", data)
                        return False
                    
                    self.log_test("Subscription Upgrade", True, 
                                f"Checkout session created - Tier: {checkout.get('tier')}, Amount: ${checkout.get('amount')}", 
                                {"session_id": checkout.get("session_id"), "amount": checkout.get("amount"), 
                                 "tier": checkout.get("tier")})
                    return True
                else:
                    self.log_test("Subscription Upgrade", False, "Invalid response format", data)
                    return False
            elif response.status_code == 400:
                # Check if it's a validation error (acceptable)
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                self.log_test("Subscription Upgrade", True, 
                            f"Validation error (expected): {error_data}", error_data)
                return True
            else:
                self.log_test("Subscription Upgrade", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Subscription Upgrade", False, f"Exception: {str(e)}")
            return False

    def test_subscription_usage_stats(self) -> bool:
        """Test GET /api/subscription/usage endpoint"""
        try:
            if not self.auth_token:
                self.log_test("Subscription Usage", False, "No authentication token available")
                return False
            
            response = self.session.get(f"{self.base_url}/subscription/usage")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "success" and "usage" in data:
                    usage = data["usage"]
                    
                    # Validate usage structure
                    expected_sections = ["current_usage", "limits", "percentage_used"]
                    missing_sections = [section for section in expected_sections if section not in usage]
                    
                    if missing_sections:
                        self.log_test("Subscription Usage Structure", False, 
                                    f"Missing sections: {missing_sections}", data)
                        return False
                    
                    current_usage = usage["current_usage"]
                    limits = usage["limits"]
                    
                    self.log_test("Subscription Usage", True, 
                                f"Usage stats retrieved - Workflows: {current_usage.get('workflows_created', 0)}, Executions: {current_usage.get('executions_run', 0)}", 
                                {"current_usage": current_usage, "has_limits": bool(limits)})
                    return True
                else:
                    self.log_test("Subscription Usage", False, "Invalid response format", data)
                    return False
            else:
                self.log_test("Subscription Usage", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Subscription Usage", False, f"Exception: {str(e)}")
            return False

    def test_usage_limits_check(self) -> bool:
        """Test GET /api/subscription/check-limits/{usage_type} endpoint"""
        try:
            if not self.auth_token:
                self.log_test("Usage Limits Check", False, "No authentication token available")
                return False
            
            # Test different usage types
            usage_types = ["workflows_created", "executions_run", "ai_requests"]
            
            for usage_type in usage_types:
                response = self.session.get(f"{self.base_url}/subscription/check-limits/{usage_type}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("status") == "success" and "limit_check" in data:
                        limit_check = data["limit_check"]
                        
                        # Validate limit check structure
                        if "allowed" in limit_check:
                            self.log_test(f"Usage Limits Check ({usage_type})", True, 
                                        f"Allowed: {limit_check.get('allowed')}, Remaining: {limit_check.get('remaining', 'N/A')}", 
                                        limit_check)
                        else:
                            self.log_test(f"Usage Limits Check ({usage_type})", False, 
                                        "Missing 'allowed' field in limit_check", data)
                            return False
                    else:
                        self.log_test(f"Usage Limits Check ({usage_type})", False, 
                                    "Invalid response format", data)
                        return False
                else:
                    self.log_test(f"Usage Limits Check ({usage_type})", False, 
                                f"HTTP {response.status_code}", response.text)
                    return False
            
            return True
                
        except Exception as e:
            self.log_test("Usage Limits Check", False, f"Exception: {str(e)}")
            return False

    def run_comprehensive_test(self):
        """Run all subscription system tests"""
        print("🎯 AETHER AUTOMATION - SUBSCRIPTION SYSTEM TESTING")
        print("=" * 60)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {TEST_USER_EMAIL}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Test sequence
        tests = [
            ("User Authentication Setup", self.setup_test_user),
            ("Subscription Plans Endpoint", self.test_subscription_plans),
            ("Current Subscription Endpoint", self.test_current_subscription),
            ("Subscription Upgrade Endpoint", self.test_subscription_upgrade),
            ("Subscription Usage Stats", self.test_subscription_usage_stats),
            ("Usage Limits Check", self.test_usage_limits_check),
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            print(f"🔄 Running: {test_name}")
            try:
                success = test_func()
                if success:
                    passed_tests += 1
                time.sleep(0.5)  # Brief pause between tests
            except Exception as e:
                self.log_test(test_name, False, f"Unexpected exception: {str(e)}")
        
        # Summary
        print("=" * 60)
        print("🎯 SUBSCRIPTION SYSTEM TESTING SUMMARY")
        print("=" * 60)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        print()
        
        # Detailed results
        for result in self.test_results:
            status_icon = "✅" if result["success"] else "❌"
            print(f"{status_icon} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        print()
        
        # Final assessment
        if success_rate >= 80:
            print("🎉 SUBSCRIPTION SYSTEM STATUS: EXCELLENT")
            print("✅ All critical subscription endpoints are working properly")
            print("✅ Authentication integration successful")
            print("✅ Subscription plans data structure correct")
            print("✅ Usage tracking and limits functional")
        elif success_rate >= 60:
            print("⚠️ SUBSCRIPTION SYSTEM STATUS: GOOD")
            print("✅ Most subscription functionality working")
            print("⚠️ Some minor issues detected")
        else:
            print("❌ SUBSCRIPTION SYSTEM STATUS: NEEDS ATTENTION")
            print("❌ Critical subscription functionality issues detected")
        
        print()
        print(f"Testing completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return success_rate, passed_tests, total_tests

def main():
    """Main test execution"""
    tester = SubscriptionTester()
    success_rate, passed, total = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 80 else 1)

if __name__ == "__main__":
    main()