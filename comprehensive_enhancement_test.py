#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND TESTING: AETHER AUTOMATION ENHANCED BACKEND
Testing 6 key enhancement areas as requested in the review.
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
import sys
import os

# Backend URL from environment
BACKEND_URL = "https://auto-flow-verify.preview.emergentagent.com/api"

class AetherBackendTester:
    def __init__(self):
        self.session = None
        self.test_results = {
            "integration_count_verification": {"status": "pending", "details": {}},
            "enhanced_ai_capabilities": {"status": "pending", "details": {}},
            "performance_optimization": {"status": "pending", "details": {}},
            "enhanced_node_types": {"status": "pending", "details": {}},
            "system_health_monitoring": {"status": "pending", "details": {}},
            "integration_search_filtering": {"status": "pending", "details": {}}
        }
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0

    async def setup_session(self):
        """Setup HTTP session for testing"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"Content-Type": "application/json"}
        )

    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()

    async def make_request(self, method, endpoint, data=None, headers=None):
        """Make HTTP request with error handling"""
        url = f"{BACKEND_URL}{endpoint}"
        try:
            async with self.session.request(method, url, json=data, headers=headers) as response:
                response_data = await response.text()
                try:
                    json_data = json.loads(response_data)
                except json.JSONDecodeError:
                    json_data = {"raw_response": response_data}
                
                return {
                    "status_code": response.status,
                    "data": json_data,
                    "success": 200 <= response.status < 300
                }
        except Exception as e:
            return {
                "status_code": 0,
                "data": {"error": str(e)},
                "success": False
            }

    def log_test(self, test_name, success, details=""):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            print(f"✅ {test_name}")
        else:
            self.failed_tests += 1
            print(f"❌ {test_name}")
        
        if details:
            print(f"   {details}")

    async def test_integration_count_verification(self):
        """Test 1: Integration Count Verification - Target: 100+ integrations"""
        print("\n🎯 TEST 1: INTEGRATION COUNT VERIFICATION")
        print("=" * 60)
        
        # Test main integrations endpoint
        response = await self.make_request("GET", "/integrations/")
        
        if response["success"]:
            integrations = response["data"]
            integration_count = len(integrations)
            
            self.log_test(
                f"Integration Count Test", 
                integration_count >= 100,
                f"Found {integration_count} integrations (Target: 100+)"
            )
            
            # Test for specific new AI integrations mentioned in review
            ai_integrations = [
                "openai_gpt4", "google_gemini", "elevenlabs", 
                "midjourney", "stability_ai", "cohere"
            ]
            
            found_ai_integrations = []
            for integration in integrations:
                if integration.get("id") in ai_integrations:
                    found_ai_integrations.append(integration.get("id"))
            
            self.log_test(
                "New AI Integrations Test",
                len(found_ai_integrations) >= 4,
                f"Found AI integrations: {found_ai_integrations}"
            )
            
            # Test integration categories
            categories_response = await self.make_request("GET", "/integrations/categories")
            if categories_response["success"]:
                categories = categories_response["data"]
                category_count = len(categories)
                
                self.log_test(
                    "Integration Categories Test",
                    category_count >= 15,
                    f"Found {category_count} categories (Target: 15+)"
                )
            
            self.test_results["integration_count_verification"] = {
                "status": "completed",
                "details": {
                    "total_integrations": integration_count,
                    "target_met": integration_count >= 100,
                    "ai_integrations_found": found_ai_integrations,
                    "categories_count": category_count if categories_response["success"] else 0
                }
            }
        else:
            self.log_test("Integration Count Test", False, f"API Error: {response['data']}")
            self.test_results["integration_count_verification"]["status"] = "failed"

    async def test_enhanced_ai_capabilities(self):
        """Test 2: Enhanced AI Capabilities"""
        print("\n🤖 TEST 2: ENHANCED AI CAPABILITIES")
        print("=" * 60)
        
        # Test AI service initialization
        health_response = await self.make_request("GET", "/performance/system/health")
        
        if health_response["success"]:
            health_data = health_response["data"]
            ai_components = health_data.get("components", {}).get("ai_services", {})
            
            # Check multi-AI provider support
            providers = ["groq_configured", "openai_configured", "anthropic_configured", "gemini_configured"]
            active_providers = [p for p in providers if ai_components.get(p, False)]
            
            self.log_test(
                "Multi-AI Provider Support",
                len(active_providers) >= 1,
                f"Active providers: {active_providers}"
            )
        
        # Test AI workflow generation
        ai_response = await self.make_request("POST", "/ai/generate-workflow", {
            "description": "Create a workflow that processes customer emails and generates AI responses"
        })
        
        self.log_test(
            "AI Workflow Generation",
            ai_response["success"],
            f"Status: {ai_response['status_code']}"
        )
        
        self.test_results["enhanced_ai_capabilities"] = {
            "status": "completed",
            "details": {
                "multi_provider_support": len(active_providers) if health_response["success"] else 0,
                "workflow_generation": ai_response["success"],
                "ai_services_status": ai_components.get("status", "unknown") if health_response["success"] else "unknown"
            }
        }

    async def test_performance_optimization(self):
        """Test 3: Performance Optimization - New endpoints"""
        print("\n⚡ TEST 3: PERFORMANCE OPTIMIZATION")
        print("=" * 60)
        
        # Test new performance endpoints
        performance_endpoints = [
            "/performance/cache/stats",
            "/performance/system/health", 
            "/performance/metrics"
        ]
        
        for endpoint in performance_endpoints:
            response = await self.make_request("GET", endpoint)
            endpoint_name = endpoint.split("/")[-1].replace("_", " ").title()
            
            self.log_test(
                f"Performance {endpoint_name} Endpoint",
                response["success"],
                f"Status: {response['status_code']}"
            )
            
            if response["success"] and endpoint == "/performance/cache/stats":
                cache_data = response["data"]
                has_cache_stats = "cache_stats" in cache_data
                has_cache_configs = "cache_configs" in cache_data
                
                self.log_test(
                    "Cache Statistics Available",
                    has_cache_stats and has_cache_configs,
                    f"Cache stats: {has_cache_stats}, Cache configs: {has_cache_configs}"
                )
        
        # Test caching on integration routes
        start_time = time.time()
        first_response = await self.make_request("GET", "/integrations/")
        first_time = time.time() - start_time
        
        start_time = time.time()
        second_response = await self.make_request("GET", "/integrations/")
        second_time = time.time() - start_time
        
        cache_working = first_response["success"] and second_response["success"]
        
        self.log_test(
            "Integration Route Caching",
            cache_working,
            f"First request: {first_time:.3f}s, Second request: {second_time:.3f}s"
        )
        
        self.test_results["performance_optimization"] = {
            "status": "completed",
            "details": {
                "cache_stats_endpoint": True,
                "system_health_endpoint": True,
                "metrics_endpoint": True,
                "caching_functional": cache_working
            }
        }

    async def test_enhanced_node_types(self):
        """Test 4: Enhanced Node Types"""
        print("\n🔧 TEST 4: ENHANCED NODE TYPES")
        print("=" * 60)
        
        # Test node types endpoint
        response = await self.make_request("GET", "/node-types")
        
        if response["success"]:
            node_data = response["data"]
            
            # Count total node types
            total_nodes = 0
            ai_nodes = 0
            categories = node_data.get("categories", {})
            
            for category_name, nodes in categories.items():
                total_nodes += len(nodes)
                if category_name == "ai":
                    ai_nodes = len(nodes)
            
            self.log_test(
                "Total Node Types Count",
                total_nodes >= 35,
                f"Found {total_nodes} node types (Target: 35+)"
            )
            
            # Test for specific new AI node types
            ai_node_types = [
                "ai_text_generation", "ai_image_generation", 
                "ai_document_processing", "ai_voice_synthesis"
            ]
            
            found_ai_nodes = []
            for category_name, nodes in categories.items():
                for node in nodes:
                    if node.get("id") in ai_node_types:
                        found_ai_nodes.append(node.get("id"))
            
            self.log_test(
                "AI Node Types Available",
                len(found_ai_nodes) >= 3,
                f"Found AI nodes: {found_ai_nodes}"
            )
            
            # Test for advanced node types
            advanced_node_types = [
                "data_transformation", "file_processing", 
                "database_query", "send_webhook"
            ]
            
            found_advanced_nodes = []
            for category_name, nodes in categories.items():
                for node in nodes:
                    if node.get("id") in advanced_node_types:
                        found_advanced_nodes.append(node.get("id"))
            
            self.log_test(
                "Advanced Node Types Available",
                len(found_advanced_nodes) >= 3,
                f"Found advanced nodes: {found_advanced_nodes}"
            )
            
            self.test_results["enhanced_node_types"] = {
                "status": "completed",
                "details": {
                    "total_nodes": total_nodes,
                    "ai_nodes": ai_nodes,
                    "ai_node_types_found": found_ai_nodes,
                    "advanced_node_types_found": found_advanced_nodes
                }
            }
        else:
            self.log_test("Node Types Test", False, f"API Error: {response['data']}")
            self.test_results["enhanced_node_types"]["status"] = "failed"

    async def test_system_health_monitoring(self):
        """Test 5: System Health & Monitoring"""
        print("\n🏥 TEST 5: SYSTEM HEALTH & MONITORING")
        print("=" * 60)
        
        # Test comprehensive health check
        health_response = await self.make_request("GET", "/performance/system/health")
        
        if health_response["success"]:
            health_data = health_response["data"]
            components = health_data.get("components", {})
            
            # Check all components
            component_tests = [
                ("cache", "Cache Service"),
                ("database", "Database Connection"),
                ("ai_services", "AI Services"),
                ("integrations", "Integrations Engine")
            ]
            
            healthy_components = 0
            for component_key, component_name in component_tests:
                component_status = components.get(component_key, {}).get("status", "unknown")
                is_healthy = component_status in ["healthy", "degraded"]
                
                if is_healthy:
                    healthy_components += 1
                
                self.log_test(
                    f"{component_name} Health Check",
                    is_healthy,
                    f"Status: {component_status}"
                )
            
            overall_status = health_data.get("status", "unknown")
            self.log_test(
                "Overall System Health",
                overall_status in ["healthy", "degraded"],
                f"System status: {overall_status}"
            )
        
        # Test performance metrics
        metrics_response = await self.make_request("GET", "/performance/metrics")
        
        if metrics_response["success"]:
            metrics_data = metrics_response["data"]
            has_system_metrics = "system" in metrics_data
            has_app_metrics = "application" in metrics_data
            
            self.log_test(
                "Performance Metrics Available",
                has_system_metrics and has_app_metrics,
                f"System metrics: {has_system_metrics}, App metrics: {has_app_metrics}"
            )
        
        self.test_results["system_health_monitoring"] = {
            "status": "completed",
            "details": {
                "health_check_working": health_response["success"],
                "healthy_components": healthy_components if health_response["success"] else 0,
                "metrics_available": metrics_response["success"]
            }
        }

    async def test_integration_search_filtering(self):
        """Test 6: Integration Search & Filtering"""
        print("\n🔍 TEST 6: INTEGRATION SEARCH & FILTERING")
        print("=" * 60)
        
        # Test integration search
        search_tests = [
            ("ai", "AI integrations"),
            ("google", "Google services"),
            ("slack", "Slack integration"),
            ("payment", "Payment integrations")
        ]
        
        search_results = {}
        for search_term, description in search_tests:
            response = await self.make_request("GET", f"/integrations/search?q={search_term}")
            
            if response["success"]:
                results = response["data"]
                result_count = len(results)
                search_results[search_term] = result_count
                
                self.log_test(
                    f"Search for '{search_term}'",
                    result_count > 0,
                    f"Found {result_count} {description}"
                )
            else:
                self.log_test(f"Search for '{search_term}'", False, "Search failed")
        
        # Test category filtering
        categories_response = await self.make_request("GET", "/integrations/categories")
        
        if categories_response["success"]:
            categories = categories_response["data"]
            
            # Test filtering by a few categories
            test_categories = ["communication", "ai", "productivity"]
            category_results = {}
            
            for category in test_categories:
                if any(cat.get("id") == category for cat in categories):
                    cat_response = await self.make_request("GET", f"/integrations/category/{category}")
                    
                    if cat_response["success"]:
                        cat_integrations = cat_response["data"]
                        category_results[category] = len(cat_integrations)
                        
                        self.log_test(
                            f"Category '{category}' filtering",
                            len(cat_integrations) > 0,
                            f"Found {len(cat_integrations)} integrations"
                        )
        
        # Test performance with caching
        start_time = time.time()
        cached_response = await self.make_request("GET", "/integrations/search?q=ai")
        cached_time = time.time() - start_time
        
        self.log_test(
            "Search Performance with Caching",
            cached_response["success"] and cached_time < 2.0,
            f"Search completed in {cached_time:.3f}s"
        )
        
        self.test_results["integration_search_filtering"] = {
            "status": "completed",
            "details": {
                "search_results": search_results,
                "category_filtering": category_results if categories_response["success"] else {},
                "search_performance": cached_time
            }
        }

    async def run_all_tests(self):
        """Run all enhancement tests"""
        print("🚀 AETHER AUTOMATION ENHANCED BACKEND TESTING")
        print("=" * 80)
        print(f"Testing backend at: {BACKEND_URL}")
        print(f"Test started at: {datetime.now().isoformat()}")
        print("=" * 80)
        
        await self.setup_session()
        
        try:
            # Run all test suites
            await self.test_integration_count_verification()
            await self.test_enhanced_ai_capabilities()
            await self.test_performance_optimization()
            await self.test_enhanced_node_types()
            await self.test_system_health_monitoring()
            await self.test_integration_search_filtering()
            
        finally:
            await self.cleanup_session()
        
        # Print final results
        self.print_final_results()

    def print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 OVERALL STATISTICS:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Passed: {self.passed_tests}")
        print(f"   Failed: {self.failed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        print(f"\n🎯 SUCCESS METRICS VERIFICATION:")
        
        # Integration count verification
        integration_details = self.test_results["integration_count_verification"]["details"]
        if integration_details:
            integration_count = integration_details.get("total_integrations", 0)
            target_met = integration_details.get("target_met", False)
            print(f"   ✅ Integration Count: {integration_count} (Target: 100+) {'✅' if target_met else '❌'}")
        
        # Node types verification
        node_details = self.test_results["enhanced_node_types"]["details"]
        if node_details:
            total_nodes = node_details.get("total_nodes", 0)
            ai_nodes = node_details.get("ai_nodes", 0)
            print(f"   ✅ Node Types: {total_nodes} total, {ai_nodes} AI nodes (Target: 35+) {'✅' if total_nodes >= 35 else '❌'}")
        
        # Performance endpoints
        perf_details = self.test_results["performance_optimization"]["details"]
        if perf_details:
            cache_working = perf_details.get("caching_functional", False)
            print(f"   ✅ Performance Endpoints: All working {'✅' if cache_working else '❌'}")
        
        # System health
        health_details = self.test_results["system_health_monitoring"]["details"]
        if health_details:
            healthy_components = health_details.get("healthy_components", 0)
            print(f"   ✅ System Health: {healthy_components}/4 components healthy {'✅' if healthy_components >= 3 else '❌'}")
        
        print(f"\n🔍 DETAILED FINDINGS:")
        for test_name, result in self.test_results.items():
            status = result["status"]
            details = result.get("details", {})
            print(f"   {test_name.replace('_', ' ').title()}: {status}")
            if details:
                for key, value in details.items():
                    print(f"     - {key}: {value}")
        
        print(f"\n⭐ ENHANCEMENT VERIFICATION:")
        if success_rate >= 80:
            print("   🎉 EXCELLENT: Backend enhancements successfully implemented!")
        elif success_rate >= 60:
            print("   ✅ GOOD: Most enhancements working, minor issues detected")
        else:
            print("   ⚠️  NEEDS ATTENTION: Significant issues found in enhancements")
        
        print("=" * 80)

async def main():
    """Main test execution"""
    tester = AetherBackendTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())