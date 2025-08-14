#!/usr/bin/env python3
"""
MASSIVE EXPANSION VERIFICATION TEST SUITE
=========================================

Testing the massive expansion of Aether Automation platform:
- Templates: 5 → 100+ professional templates across 20 categories
- Integrations: 103 → 200+ real integrations across 25 categories
- Enhanced system with new massive engines

Priority Areas:
1. Template System Expansion (HIGH)
2. Integration System Expansion (HIGH) 
3. Enhanced System Status (HIGH)
4. Backward Compatibility (MEDIUM)
5. Data Quality & Realism (HIGH)
6. Performance Testing (MEDIUM)
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, List, Any

# Configuration
BACKEND_URL = "https://feature-explorer-11.preview.emergentagent.com/api"
TEST_USER_EMAIL = "expansion.tester@aether.com"
TEST_USER_PASSWORD = "ExpansionTest2024!"
TEST_USER_NAME = "Expansion Tester"

class MassiveExpansionTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = []
        self.start_time = time.time()
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"Content-Type": "application/json"}
        )
        
    async def cleanup_session(self):
        """Clean up HTTP session"""
        if self.session:
            await self.session.close()
            
    async def authenticate(self):
        """Authenticate and get JWT token"""
        try:
            # Try to register user first
            register_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "first_name": TEST_USER_NAME.split()[0],
                "last_name": TEST_USER_NAME.split()[1] if len(TEST_USER_NAME.split()) > 1 else "User"
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/register", json=register_data) as response:
                if response.status in [200, 201]:
                    result = await response.json()
                    self.auth_token = result.get("access_token")
                    return True
                    
        except Exception as e:
            pass  # User might already exist
            
        # Try to login
        try:
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/login", json=login_data) as response:
                if response.status == 200:
                    result = await response.json()
                    self.auth_token = result.get("access_token")
                    return True
                    
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False
            
        return False
        
    def get_auth_headers(self):
        """Get authorization headers"""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}
        
    async def test_template_system_expansion(self):
        """Test Template System Expansion - Priority: HIGH"""
        print("\n🎯 TESTING TEMPLATE SYSTEM EXPANSION (Priority: HIGH)")
        print("=" * 60)
        
        tests = [
            ("Enhanced Templates Endpoint", "GET", "/templates/enhanced", None),
            ("Template Search Enhanced", "GET", "/templates/search/enhanced?q=automation", None),
            ("Template Categories Enhanced", "GET", "/templates/categories/enhanced", None),
            ("Trending Templates", "GET", "/templates/trending", None),
            ("Template Statistics", "GET", "/templates/stats", None),
        ]
        
        template_count = 0
        category_count = 0
        
        for test_name, method, endpoint, data in tests:
            try:
                headers = {**self.get_auth_headers(), "Content-Type": "application/json"}
                
                async with self.session.request(method, f"{BACKEND_URL}{endpoint}", 
                                              json=data, headers=headers) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        # Analyze template expansion
                        if endpoint == "/templates/enhanced":
                            if isinstance(result, list):
                                template_count = len(result)
                            elif isinstance(result, dict) and "templates" in result:
                                template_count = len(result["templates"])
                            elif isinstance(result, dict) and "results" in result:
                                template_count = len(result["results"])
                                
                        elif endpoint == "/templates/categories/enhanced":
                            if isinstance(result, list):
                                category_count = len(result)
                            elif isinstance(result, dict) and "categories" in result:
                                category_count = len(result["categories"])
                                
                        elif endpoint == "/templates/stats":
                            if isinstance(result, dict):
                                template_count = result.get("total_templates", 0)
                                category_count = result.get("categories", 0)
                        
                        self.test_results.append({
                            "test": f"Template System - {test_name}",
                            "status": "✅ PASS",
                            "details": f"Status: {response.status}, Response received"
                        })
                        print(f"✅ {test_name}: PASS (Status: {response.status})")
                        
                    else:
                        self.test_results.append({
                            "test": f"Template System - {test_name}",
                            "status": "❌ FAIL",
                            "details": f"Status: {response.status}"
                        })
                        print(f"❌ {test_name}: FAIL (Status: {response.status})")
                        
            except Exception as e:
                self.test_results.append({
                    "test": f"Template System - {test_name}",
                    "status": "❌ ERROR",
                    "details": str(e)
                })
                print(f"❌ {test_name}: ERROR - {e}")
        
        # Verify expansion goals
        print(f"\n📊 TEMPLATE EXPANSION ANALYSIS:")
        print(f"   Template Count: {template_count}")
        print(f"   Category Count: {category_count}")
        
        if template_count >= 100:
            print(f"🎉 TEMPLATE EXPANSION SUCCESS: {template_count} templates (exceeds 100+ goal)")
            expansion_success = True
        else:
            print(f"⚠️ TEMPLATE EXPANSION INCOMPLETE: {template_count} templates (goal: 100+)")
            expansion_success = False
            
        if category_count >= 20:
            print(f"🎉 CATEGORY EXPANSION SUCCESS: {category_count} categories (meets 20+ goal)")
        else:
            print(f"⚠️ CATEGORY EXPANSION INCOMPLETE: {category_count} categories (goal: 20+)")
            
        return expansion_success, template_count, category_count
        
    async def test_integration_system_expansion(self):
        """Test Integration System Expansion - Priority: HIGH"""
        print("\n🎯 TESTING INTEGRATION SYSTEM EXPANSION (Priority: HIGH)")
        print("=" * 60)
        
        tests = [
            ("Enhanced Integrations Endpoint", "GET", "/integrations/enhanced", None),
            ("Integration Search Enhanced", "GET", "/integrations/search/enhanced?q=slack", None),
            ("Integration Categories Enhanced", "GET", "/integrations/categories/enhanced", None),
            ("Integration Stats Enhanced", "GET", "/integrations/stats/enhanced", None),
        ]
        
        integration_count = 0
        category_count = 0
        
        for test_name, method, endpoint, data in tests:
            try:
                headers = {**self.get_auth_headers(), "Content-Type": "application/json"}
                
                async with self.session.request(method, f"{BACKEND_URL}{endpoint}", 
                                              json=data, headers=headers) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        # Analyze integration expansion
                        if endpoint == "/integrations/enhanced":
                            if isinstance(result, list):
                                integration_count = len(result)
                            elif isinstance(result, dict) and "integrations" in result:
                                integration_count = len(result["integrations"])
                                
                        elif endpoint == "/integrations/categories/enhanced":
                            if isinstance(result, list):
                                category_count = len(result)
                            elif isinstance(result, dict) and "categories" in result:
                                category_count = len(result["categories"])
                                
                        elif endpoint == "/integrations/stats/enhanced":
                            if isinstance(result, dict):
                                integration_count = result.get("total_integrations", 0)
                                category_count = result.get("total_categories", 0)
                        
                        self.test_results.append({
                            "test": f"Integration System - {test_name}",
                            "status": "✅ PASS",
                            "details": f"Status: {response.status}, Response received"
                        })
                        print(f"✅ {test_name}: PASS (Status: {response.status})")
                        
                    else:
                        self.test_results.append({
                            "test": f"Integration System - {test_name}",
                            "status": "❌ FAIL",
                            "details": f"Status: {response.status}"
                        })
                        print(f"❌ {test_name}: FAIL (Status: {response.status})")
                        
            except Exception as e:
                self.test_results.append({
                    "test": f"Integration System - {test_name}",
                    "status": "❌ ERROR",
                    "details": str(e)
                })
                print(f"❌ {test_name}: ERROR - {e}")
        
        # Verify expansion goals
        print(f"\n📊 INTEGRATION EXPANSION ANALYSIS:")
        print(f"   Integration Count: {integration_count}")
        print(f"   Category Count: {category_count}")
        
        if integration_count >= 200:
            print(f"🎉 INTEGRATION EXPANSION SUCCESS: {integration_count} integrations (exceeds 200+ goal)")
            expansion_success = True
        else:
            print(f"⚠️ INTEGRATION EXPANSION INCOMPLETE: {integration_count} integrations (goal: 200+)")
            expansion_success = False
            
        if category_count >= 25:
            print(f"🎉 CATEGORY EXPANSION SUCCESS: {category_count} categories (meets 25+ goal)")
        else:
            print(f"⚠️ CATEGORY EXPANSION INCOMPLETE: {category_count} categories (goal: 25+)")
            
        return expansion_success, integration_count, category_count
        
    async def test_enhanced_system_status(self):
        """Test Enhanced System Status - Priority: HIGH"""
        print("\n🎯 TESTING ENHANCED SYSTEM STATUS (Priority: HIGH)")
        print("=" * 60)
        
        try:
            headers = {**self.get_auth_headers(), "Content-Type": "application/json"}
            
            async with self.session.get(f"{BACKEND_URL}/enhanced/status", headers=headers) as response:
                
                if response.status == 200:
                    result = await response.json()
                    
                    # Analyze system status
                    template_count = result.get("features", {}).get("templates", {}).get("total", 0)
                    integration_count = result.get("features", {}).get("integrations", {}).get("total", 0)
                    node_count = result.get("features", {}).get("nodes", {}).get("total", 0)
                    
                    print(f"📊 ENHANCED SYSTEM STATUS:")
                    print(f"   Status: {result.get('status', 'unknown')}")
                    print(f"   Version: {result.get('version', 'unknown')}")
                    print(f"   Enhancement Level: {result.get('enhancement_level', 'unknown')}")
                    print(f"   System Health: {result.get('system_health', 'unknown')}")
                    print(f"   Feature Utilization: {result.get('feature_utilization', 'unknown')}")
                    print(f"   Templates: {template_count}")
                    print(f"   Integrations: {integration_count}")
                    print(f"   Nodes: {node_count}")
                    
                    # Verify massive expansion stats
                    expansion_verified = (
                        template_count >= 100 and 
                        integration_count >= 200 and
                        result.get("enhancement_level") == "massive"
                    )
                    
                    if expansion_verified:
                        print(f"🎉 MASSIVE EXPANSION VERIFIED: All expansion goals met!")
                        status = "✅ PASS"
                    else:
                        print(f"⚠️ EXPANSION INCOMPLETE: Some goals not met")
                        status = "⚠️ PARTIAL"
                    
                    self.test_results.append({
                        "test": "Enhanced System Status",
                        "status": status,
                        "details": f"Templates: {template_count}, Integrations: {integration_count}, Nodes: {node_count}"
                    })
                    
                    return expansion_verified, template_count, integration_count, node_count
                    
                else:
                    self.test_results.append({
                        "test": "Enhanced System Status",
                        "status": "❌ FAIL",
                        "details": f"Status: {response.status}"
                    })
                    print(f"❌ Enhanced System Status: FAIL (Status: {response.status})")
                    return False, 0, 0, 0
                    
        except Exception as e:
            self.test_results.append({
                "test": "Enhanced System Status",
                "status": "❌ ERROR",
                "details": str(e)
            })
            print(f"❌ Enhanced System Status: ERROR - {e}")
            return False, 0, 0, 0
            
    async def test_backward_compatibility(self):
        """Test Backward Compatibility - Priority: MEDIUM"""
        print("\n🎯 TESTING BACKWARD COMPATIBILITY (Priority: MEDIUM)")
        print("=" * 60)
        
        legacy_endpoints = [
            ("Legacy Templates", "GET", "/templates/", None),
            ("Legacy Integrations", "GET", "/integrations/", None),
            ("Legacy Node Types", "GET", "/node-types", None),
        ]
        
        compatibility_success = True
        
        for test_name, method, endpoint, data in legacy_endpoints:
            try:
                headers = {**self.get_auth_headers(), "Content-Type": "application/json"}
                
                async with self.session.request(method, f"{BACKEND_URL}{endpoint}", 
                                              json=data, headers=headers) as response:
                    
                    if response.status == 200:
                        self.test_results.append({
                            "test": f"Backward Compatibility - {test_name}",
                            "status": "✅ PASS",
                            "details": f"Status: {response.status}, Legacy endpoint working"
                        })
                        print(f"✅ {test_name}: PASS (Status: {response.status})")
                        
                    else:
                        compatibility_success = False
                        self.test_results.append({
                            "test": f"Backward Compatibility - {test_name}",
                            "status": "❌ FAIL",
                            "details": f"Status: {response.status}"
                        })
                        print(f"❌ {test_name}: FAIL (Status: {response.status})")
                        
            except Exception as e:
                compatibility_success = False
                self.test_results.append({
                    "test": f"Backward Compatibility - {test_name}",
                    "status": "❌ ERROR",
                    "details": str(e)
                })
                print(f"❌ {test_name}: ERROR - {e}")
        
        return compatibility_success
        
    async def test_data_quality_realism(self):
        """Test Data Quality & Realism - Priority: HIGH"""
        print("\n🎯 TESTING DATA QUALITY & REALISM (Priority: HIGH)")
        print("=" * 60)
        
        quality_tests = [
            ("Template Data Quality", "GET", "/templates/enhanced", None),
            ("Integration Data Quality", "GET", "/integrations/enhanced", None),
        ]
        
        quality_score = 0
        total_tests = len(quality_tests)
        
        for test_name, method, endpoint, data in quality_tests:
            try:
                headers = {**self.get_auth_headers(), "Content-Type": "application/json"}
                
                async with self.session.request(method, f"{BACKEND_URL}{endpoint}", 
                                              json=data, headers=headers) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        # Analyze data quality
                        realistic_data = True
                        demo_patterns = 0
                        
                        if isinstance(result, list) and len(result) > 0:
                            sample_item = result[0]
                            
                            # Check for demo/fake patterns
                            item_str = json.dumps(sample_item).lower()
                            demo_keywords = ["test", "demo", "fake", "sample", "example", "placeholder"]
                            
                            for keyword in demo_keywords:
                                if keyword in item_str:
                                    demo_patterns += 1
                                    
                            if demo_patterns > 2:
                                realistic_data = False
                        
                        if realistic_data:
                            quality_score += 1
                            self.test_results.append({
                                "test": f"Data Quality - {test_name}",
                                "status": "✅ PASS",
                                "details": f"Realistic data detected, demo patterns: {demo_patterns}"
                            })
                            print(f"✅ {test_name}: PASS (Realistic data, demo patterns: {demo_patterns})")
                        else:
                            self.test_results.append({
                                "test": f"Data Quality - {test_name}",
                                "status": "⚠️ PARTIAL",
                                "details": f"Some demo patterns detected: {demo_patterns}"
                            })
                            print(f"⚠️ {test_name}: PARTIAL (Demo patterns detected: {demo_patterns})")
                            
                    else:
                        self.test_results.append({
                            "test": f"Data Quality - {test_name}",
                            "status": "❌ FAIL",
                            "details": f"Status: {response.status}"
                        })
                        print(f"❌ {test_name}: FAIL (Status: {response.status})")
                        
            except Exception as e:
                self.test_results.append({
                    "test": f"Data Quality - {test_name}",
                    "status": "❌ ERROR",
                    "details": str(e)
                })
                print(f"❌ {test_name}: ERROR - {e}")
        
        quality_percentage = (quality_score / total_tests) * 100 if total_tests > 0 else 0
        print(f"\n📊 DATA QUALITY SCORE: {quality_percentage:.1f}% ({quality_score}/{total_tests})")
        
        return quality_percentage >= 80
        
    async def test_performance_with_large_datasets(self):
        """Test Performance with Large Datasets - Priority: MEDIUM"""
        print("\n🎯 TESTING PERFORMANCE WITH LARGE DATASETS (Priority: MEDIUM)")
        print("=" * 60)
        
        performance_tests = [
            ("Large Template Search", "GET", "/templates/search/enhanced?q=automation", None),
            ("Large Integration Search", "GET", "/integrations/search/enhanced?q=api", None),
            ("Enhanced Status Load", "GET", "/enhanced/status", None),
        ]
        
        performance_results = []
        
        for test_name, method, endpoint, data in performance_tests:
            try:
                headers = {**self.get_auth_headers(), "Content-Type": "application/json"}
                
                start_time = time.time()
                async with self.session.request(method, f"{BACKEND_URL}{endpoint}", 
                                              json=data, headers=headers) as response:
                    
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        # Analyze response size
                        response_size = len(json.dumps(result))
                        
                        performance_results.append({
                            "test": test_name,
                            "response_time": response_time,
                            "response_size": response_size,
                            "status": "✅ PASS"
                        })
                        
                        self.test_results.append({
                            "test": f"Performance - {test_name}",
                            "status": "✅ PASS",
                            "details": f"Response time: {response_time:.2f}ms, Size: {response_size} bytes"
                        })
                        print(f"✅ {test_name}: PASS ({response_time:.2f}ms, {response_size} bytes)")
                        
                    else:
                        self.test_results.append({
                            "test": f"Performance - {test_name}",
                            "status": "❌ FAIL",
                            "details": f"Status: {response.status}"
                        })
                        print(f"❌ {test_name}: FAIL (Status: {response.status})")
                        
            except Exception as e:
                self.test_results.append({
                    "test": f"Performance - {test_name}",
                    "status": "❌ ERROR",
                    "details": str(e)
                })
                print(f"❌ {test_name}: ERROR - {e}")
        
        # Calculate average performance
        if performance_results:
            avg_response_time = sum(r["response_time"] for r in performance_results) / len(performance_results)
            print(f"\n📊 AVERAGE RESPONSE TIME: {avg_response_time:.2f}ms")
            
            performance_acceptable = avg_response_time < 5000  # 5 seconds threshold
            return performance_acceptable
        
        return False
        
    async def run_comprehensive_test(self):
        """Run comprehensive massive expansion verification"""
        print("🚀 MASSIVE EXPANSION VERIFICATION TEST SUITE")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        await self.setup_session()
        
        try:
            # Authenticate
            print("\n🔐 AUTHENTICATION")
            auth_success = await self.authenticate()
            if not auth_success:
                print("❌ Authentication failed - continuing with public endpoints only")
            else:
                print("✅ Authentication successful")
            
            # Run all test categories
            template_success, template_count, template_categories = await self.test_template_system_expansion()
            integration_success, integration_count, integration_categories = await self.test_integration_system_expansion()
            status_success, status_templates, status_integrations, status_nodes = await self.test_enhanced_system_status()
            compatibility_success = await self.test_backward_compatibility()
            quality_success = await self.test_data_quality_realism()
            performance_success = await self.test_performance_with_large_datasets()
            
            # Calculate overall results
            total_tests = len(self.test_results)
            passed_tests = len([r for r in self.test_results if r["status"] == "✅ PASS"])
            success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
            
            # Generate comprehensive report
            print("\n" + "=" * 80)
            print("🎯 MASSIVE EXPANSION VERIFICATION RESULTS")
            print("=" * 80)
            
            print(f"\n📊 OVERALL SUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
            
            print(f"\n🎯 EXPANSION GOALS VERIFICATION:")
            print(f"   ✅ Template Expansion: {template_count} templates (Goal: 100+) - {'SUCCESS' if template_count >= 100 else 'INCOMPLETE'}")
            print(f"   ✅ Integration Expansion: {integration_count} integrations (Goal: 200+) - {'SUCCESS' if integration_count >= 200 else 'INCOMPLETE'}")
            print(f"   ✅ Template Categories: {template_categories} categories (Goal: 20+) - {'SUCCESS' if template_categories >= 20 else 'INCOMPLETE'}")
            print(f"   ✅ Integration Categories: {integration_categories} categories (Goal: 25+) - {'SUCCESS' if integration_categories >= 25 else 'INCOMPLETE'}")
            
            print(f"\n🔍 SYSTEM VERIFICATION:")
            print(f"   Enhanced System Status: {'✅ PASS' if status_success else '❌ FAIL'}")
            print(f"   Backward Compatibility: {'✅ PASS' if compatibility_success else '❌ FAIL'}")
            print(f"   Data Quality & Realism: {'✅ PASS' if quality_success else '❌ FAIL'}")
            print(f"   Performance Testing: {'✅ PASS' if performance_success else '❌ FAIL'}")
            
            # Determine overall verdict
            expansion_complete = (
                template_count >= 100 and 
                integration_count >= 200 and
                template_categories >= 20 and
                integration_categories >= 25
            )
            
            if expansion_complete and success_rate >= 90:
                verdict = "🎉 MASSIVE EXPANSION SUCCESSFULLY VERIFIED"
            elif expansion_complete and success_rate >= 75:
                verdict = "✅ MASSIVE EXPANSION VERIFIED WITH MINOR ISSUES"
            elif template_count >= 100 or integration_count >= 200:
                verdict = "⚠️ PARTIAL EXPANSION ACHIEVED"
            else:
                verdict = "❌ EXPANSION GOALS NOT MET"
            
            print(f"\n🏆 FINAL VERDICT: {verdict}")
            
            # Detailed test results
            print(f"\n📋 DETAILED TEST RESULTS:")
            for result in self.test_results:
                print(f"   {result['status']} {result['test']}")
                if result['status'] != "✅ PASS":
                    print(f"      Details: {result['details']}")
            
            execution_time = time.time() - self.start_time
            print(f"\n⏱️ Total Execution Time: {execution_time:.2f} seconds")
            print("=" * 80)
            
            return {
                "success_rate": success_rate,
                "expansion_complete": expansion_complete,
                "template_count": template_count,
                "integration_count": integration_count,
                "verdict": verdict,
                "detailed_results": self.test_results
            }
            
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution"""
    tester = MassiveExpansionTester()
    results = await tester.run_comprehensive_test()
    return results

if __name__ == "__main__":
    asyncio.run(main())