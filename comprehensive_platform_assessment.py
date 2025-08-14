#!/usr/bin/env python3
"""
Comprehensive Aether Automation Platform Assessment
Focus: Quantify current capabilities for expansion opportunities
"""

import requests
import sys
import json
import time
import uuid
from datetime import datetime

class AetherPlatformAssessment:
    def __init__(self, base_url="https://sub-plan-info.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.assessment_results = {
            "node_types": {},
            "integrations": {},
            "templates": {},
            "ai_capabilities": {},
            "workflow_engine": {},
            "features_utilization": {},
            "expansion_opportunities": []
        }
        self.session_id = str(uuid.uuid4())

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, params=None):
        """Run a single API test and return response data"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Assessing {name}...")
        
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
                print(f"✅ Success - Status: {response.status_code}")
                try:
                    return response.json()
                except:
                    return {"status": "success", "raw_response": response.text}
            else:
                print(f"❌ Failed - Expected: {expected_status}, Got: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return None

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None

    def authenticate(self):
        """Authenticate and get JWT token"""
        print("\n🔐 AUTHENTICATION SETUP")
        
        # Create unique test user
        test_email = f"assessment_{self.session_id[:8]}@example.com"
        test_password = "AssessmentTest123!"
        
        user_data = {
            "email": test_email,
            "password": test_password,
            "first_name": "Assessment",
            "last_name": "User"
        }
        
        # Register user
        response_data = self.run_test(
            "User Registration", 
            "POST", 
            "api/auth/register", 
            200, 
            user_data
        )
        
        if response_data and "access_token" in response_data:
            self.token = response_data["access_token"]
            self.user_id = response_data.get("user_id")
            print(f"✅ Authentication successful - User ID: {self.user_id}")
            return True
        else:
            print("❌ Authentication failed")
            return False

    def assess_node_types(self):
        """Assess current node types count and categories"""
        print("\n📊 NODE TYPES ASSESSMENT")
        
        # Test multiple node endpoints
        endpoints_to_test = [
            ("api/node-types", "Main Node Types Endpoint"),
            ("api/nodes", "Nodes Alias Endpoint"),
            ("api/nodes/enhanced", "Enhanced Nodes Endpoint"),
            ("api/enhanced/nodes/enhanced", "Enhanced API Nodes")
        ]
        
        node_data = None
        for endpoint, name in endpoints_to_test:
            data = self.run_test(name, "GET", endpoint, 200)
            if data and not node_data:
                node_data = data
        
        if node_data:
            # Extract node statistics
            if "stats" in node_data:
                stats = node_data["stats"]
                self.assessment_results["node_types"] = {
                    "total_nodes": stats.get("total_nodes", 0),
                    "categories": stats.get("categories", 0),
                    "triggers": stats.get("triggers", 0),
                    "actions": stats.get("actions", 0),
                    "logic": stats.get("logic", 0),
                    "ai": stats.get("ai", 0),
                    "breakdown": stats
                }
            elif "node_types" in node_data:
                # Count nodes by category
                categories = {}
                total = 0
                for category, nodes in node_data["node_types"].items():
                    count = len(nodes) if isinstance(nodes, list) else 0
                    categories[category] = count
                    total += count
                
                self.assessment_results["node_types"] = {
                    "total_nodes": total,
                    "categories": len(categories),
                    "breakdown": categories
                }
            
            print(f"📈 Node Types Summary:")
            for key, value in self.assessment_results["node_types"].items():
                print(f"   {key}: {value}")
        
        # Test node search functionality
        search_data = self.run_test("Node Search", "GET", "api/nodes/search", 200, params={"q": "ai"})
        if search_data:
            print(f"🔍 Node Search Results: {search_data.get('total_results', 0)} AI-related nodes")

    def assess_integrations(self):
        """Assess current integration count and verify 103+ claim"""
        print("\n🔗 INTEGRATIONS ASSESSMENT")
        
        # Get all integrations
        integration_data = self.run_test("All Integrations", "GET", "api/integrations", 200)
        
        if integration_data:
            # Handle both list and dict responses
            if isinstance(integration_data, list):
                integrations = integration_data
                categories = []
            else:
                integrations = integration_data.get("integrations", [])
                categories = integration_data.get("categories", [])
            
            self.assessment_results["integrations"] = {
                "total_count": len(integrations),
                "categories_count": len(categories),
                "categories": categories,
                "meets_100_plus_promise": len(integrations) >= 100,
                "sample_integrations": [i.get("name", "Unknown") for i in integrations[:10]]
            }
            
            print(f"📈 Integration Summary:")
            print(f"   Total Integrations: {len(integrations)}")
            print(f"   Categories: {len(categories)}")
            print(f"   Meets 100+ Promise: {'✅ YES' if len(integrations) >= 100 else '❌ NO'}")
            print(f"   Sample: {', '.join(self.assessment_results['integrations']['sample_integrations'])}")
        
        # Test integration search
        search_tests = [
            ("slack", "Slack Integration Search"),
            ("google", "Google Integration Search"),
            ("ai", "AI Integration Search")
        ]
        
        for term, name in search_tests:
            search_data = self.run_test(name, "GET", "api/integrations/search", 200, params={"q": term})
            if search_data:
                results = search_data.get("results", [])
                print(f"🔍 {term.title()} Search: {len(results)} results")

    def assess_templates(self):
        """Assess current template system count and functionality"""
        print("\n📋 TEMPLATE SYSTEM ASSESSMENT")
        
        # Test multiple template endpoints
        template_endpoints = [
            ("api/templates", "Main Templates Endpoint"),
            ("api/templates/enhanced", "Enhanced Templates"),
            ("api/templates/stats", "Template Statistics"),
            ("api/templates/trending", "Trending Templates")
        ]
        
        template_data = None
        for endpoint, name in template_endpoints:
            data = self.run_test(name, "GET", endpoint, 200)
            if data and "templates" in data:
                template_data = data
                break
        
        # Get template statistics
        stats_data = self.run_test("Template Stats", "GET", "api/templates/stats", 200)
        
        if template_data or stats_data:
            templates = template_data.get("templates", []) if template_data else []
            stats = stats_data if stats_data else {}
            
            self.assessment_results["templates"] = {
                "total_templates": len(templates) or stats.get("total_templates", 0),
                "categories": stats.get("categories", 0),
                "average_rating": stats.get("average_rating", 0),
                "total_deployments": stats.get("total_deployments", 0),
                "sample_templates": [t.get("name", "Unknown") for t in templates[:5]]
            }
            
            print(f"📈 Template Summary:")
            for key, value in self.assessment_results["templates"].items():
                print(f"   {key}: {value}")
        
        # Test template creation
        test_template = {
            "name": f"Assessment Template {self.session_id[:8]}",
            "description": "Test template for platform assessment",
            "category": "automation",
            "nodes": [
                {"id": "trigger_1", "type": "webhook", "name": "Webhook Trigger"},
                {"id": "action_1", "type": "email", "name": "Send Email"}
            ]
        }
        
        create_data = self.run_test("Template Creation", "POST", "api/templates/create", 200, test_template)
        if create_data:
            print("✅ Template creation functionality working")

    def assess_ai_capabilities(self):
        """Assess AI features and GROQ integration"""
        print("\n🤖 AI CAPABILITIES ASSESSMENT")
        
        # Test AI endpoints
        ai_endpoints = [
            ("api/ai/system-status", "AI System Status"),
            ("api/enhanced/ai/providers", "AI Providers"),
            ("api/ai/dashboard-insights", "AI Dashboard Insights")
        ]
        
        ai_working = 0
        total_ai_tests = len(ai_endpoints)
        
        for endpoint, name in ai_endpoints:
            data = self.run_test(name, "GET", endpoint, 200)
            if data:
                ai_working += 1
        
        # Test AI workflow generation
        workflow_prompt = {
            "description": "Create a workflow that sends a Slack notification when a new email arrives",
            "requirements": ["email trigger", "slack integration", "notification"]
        }
        
        generation_data = self.run_test(
            "AI Workflow Generation", 
            "POST", 
            "api/ai/generate-workflow", 
            200, 
            workflow_prompt
        )
        
        if generation_data:
            ai_working += 1
            total_ai_tests += 1
        
        # Test AI integration suggestions
        suggestion_data = self.run_test(
            "AI Integration Suggestions",
            "POST",
            "api/ai/suggest-integrations",
            200,
            {"description": "I need to automate customer support"}
        )
        
        if suggestion_data:
            ai_working += 1
            total_ai_tests += 1
        
        self.assessment_results["ai_capabilities"] = {
            "total_ai_features": total_ai_tests,
            "working_features": ai_working,
            "success_rate": f"{(ai_working/total_ai_tests)*100:.1f}%",
            "groq_integration": "operational" if ai_working > 0 else "unknown",
            "workflow_generation": "working" if generation_data else "not working",
            "integration_suggestions": "working" if suggestion_data else "not working"
        }
        
        print(f"📈 AI Capabilities Summary:")
        for key, value in self.assessment_results["ai_capabilities"].items():
            print(f"   {key}: {value}")

    def assess_workflow_engine(self):
        """Test end-to-end workflow creation and execution"""
        print("\n⚙️ WORKFLOW ENGINE ASSESSMENT")
        
        if not self.token:
            print("❌ Cannot test workflow engine - authentication required")
            return
        
        # Test workflow CRUD operations
        test_workflow = {
            "name": f"Assessment Workflow {self.session_id[:8]}",
            "description": "Test workflow for platform assessment",
            "nodes": [
                {
                    "id": "trigger_1",
                    "type": "webhook",
                    "name": "Webhook Trigger",
                    "config": {"url": "https://example.com/webhook"}
                },
                {
                    "id": "action_1", 
                    "type": "email",
                    "name": "Send Email",
                    "config": {"to": "test@example.com", "subject": "Test"}
                }
            ],
            "connections": [
                {"from": "trigger_1", "to": "action_1"}
            ]
        }
        
        # Create workflow
        create_data = self.run_test("Workflow Creation", "POST", "api/workflows/", 200, test_workflow)
        workflow_id = None
        
        if create_data and "id" in create_data:
            workflow_id = create_data["id"]
            print(f"✅ Workflow created with ID: {workflow_id}")
        
        # List workflows
        list_data = self.run_test("List Workflows", "GET", "api/workflows/", 200)
        if isinstance(list_data, list):
            workflow_count = len(list_data)
        else:
            workflow_count = len(list_data.get("workflows", [])) if list_data else 0
        
        # Test workflow execution if we have a workflow
        execution_data = None
        if workflow_id:
            execution_data = self.run_test(
                "Workflow Execution",
                "POST", 
                f"api/workflows/{workflow_id}/execute",
                200,
                {"input_data": {"test": "assessment"}}
            )
        
        self.assessment_results["workflow_engine"] = {
            "workflow_creation": "working" if workflow_id else "not working",
            "workflow_listing": "working" if list_data else "not working", 
            "workflow_execution": "working" if execution_data else "not working",
            "total_workflows": workflow_count,
            "crud_operations": "functional" if workflow_id and list_data else "limited"
        }
        
        print(f"📈 Workflow Engine Summary:")
        for key, value in self.assessment_results["workflow_engine"].items():
            print(f"   {key}: {value}")

    def assess_features_utilization(self):
        """Assess overall feature utilization and system health"""
        print("\n📊 FEATURES UTILIZATION ASSESSMENT")
        
        # Test system status endpoints
        status_endpoints = [
            ("api/enhanced/status", "Enhanced System Status"),
            ("api/dashboard/stats", "Dashboard Statistics"),
            ("api/analytics/dashboard/overview", "Analytics Overview")
        ]
        
        system_health = 0
        total_status_tests = len(status_endpoints)
        
        for endpoint, name in status_endpoints:
            data = self.run_test(name, "GET", endpoint, 200)
            if data:
                system_health += 1
        
        # Calculate overall platform utilization
        total_features = (
            self.assessment_results.get("node_types", {}).get("total_nodes", 0) +
            self.assessment_results.get("integrations", {}).get("total_count", 0) +
            self.assessment_results.get("templates", {}).get("total_templates", 0)
        )
        
        self.assessment_results["features_utilization"] = {
            "system_health_score": f"{(system_health/total_status_tests)*100:.1f}%",
            "total_platform_features": total_features,
            "operational_endpoints": self.tests_passed,
            "total_endpoints_tested": self.tests_run,
            "overall_success_rate": f"{(self.tests_passed/self.tests_run)*100:.1f}%"
        }
        
        print(f"📈 Features Utilization Summary:")
        for key, value in self.assessment_results["features_utilization"].items():
            print(f"   {key}: {value}")

    def identify_expansion_opportunities(self):
        """Identify areas for expansion based on assessment"""
        print("\n🚀 EXPANSION OPPORTUNITIES ANALYSIS")
        
        opportunities = []
        
        # Node types expansion
        node_count = self.assessment_results.get("node_types", {}).get("total_nodes", 0)
        if node_count < 50:
            opportunities.append(f"Node Types: Current {node_count}, recommend expanding to 100+ nodes")
        
        # Integration expansion
        integration_count = self.assessment_results.get("integrations", {}).get("total_count", 0)
        if integration_count < 150:
            opportunities.append(f"Integrations: Current {integration_count}, recommend expanding to 200+ integrations")
        
        # Template expansion
        template_count = self.assessment_results.get("templates", {}).get("total_templates", 0)
        if template_count < 100:
            opportunities.append(f"Templates: Current {template_count}, recommend expanding to 100+ templates")
        
        # AI capabilities expansion
        ai_success = self.assessment_results.get("ai_capabilities", {}).get("working_features", 0)
        if ai_success < 5:
            opportunities.append("AI Capabilities: Expand multi-provider support and advanced AI features")
        
        self.assessment_results["expansion_opportunities"] = opportunities
        
        print("📋 Identified Expansion Opportunities:")
        for i, opportunity in enumerate(opportunities, 1):
            print(f"   {i}. {opportunity}")

    def generate_comprehensive_report(self):
        """Generate final comprehensive assessment report"""
        print("\n" + "="*80)
        print("🎯 COMPREHENSIVE AETHER AUTOMATION PLATFORM ASSESSMENT REPORT")
        print("="*80)
        
        print(f"\n📊 EXECUTIVE SUMMARY:")
        print(f"   • Tests Run: {self.tests_run}")
        print(f"   • Tests Passed: {self.tests_passed}")
        print(f"   • Overall Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        print(f"\n🔢 CURRENT PLATFORM CAPABILITIES:")
        
        # Node Types
        node_data = self.assessment_results.get("node_types", {})
        print(f"   📦 Node Types: {node_data.get('total_nodes', 'Unknown')} nodes across {node_data.get('categories', 'Unknown')} categories")
        
        # Integrations
        integration_data = self.assessment_results.get("integrations", {})
        integration_count = integration_data.get("total_count", 0)
        meets_promise = "✅ EXCEEDS" if integration_count >= 100 else "❌ BELOW"
        print(f"   🔗 Integrations: {integration_count} integrations ({meets_promise} 100+ promise)")
        
        # Templates
        template_data = self.assessment_results.get("templates", {})
        print(f"   📋 Templates: {template_data.get('total_templates', 'Unknown')} templates available")
        
        # AI Capabilities
        ai_data = self.assessment_results.get("ai_capabilities", {})
        print(f"   🤖 AI Features: {ai_data.get('working_features', 0)}/{ai_data.get('total_ai_features', 0)} working ({ai_data.get('success_rate', '0%')})")
        
        # Workflow Engine
        workflow_data = self.assessment_results.get("workflow_engine", {})
        print(f"   ⚙️ Workflow Engine: {workflow_data.get('crud_operations', 'Unknown')} status")
        
        print(f"\n🚀 EXPANSION READINESS:")
        opportunities = self.assessment_results.get("expansion_opportunities", [])
        if opportunities:
            for opportunity in opportunities:
                print(f"   • {opportunity}")
        else:
            print("   ✅ Platform ready for advanced expansion")
        
        print(f"\n🎯 FINAL VERDICT:")
        success_rate = (self.tests_passed/self.tests_run)*100
        if success_rate >= 90:
            verdict = "🎉 EXCELLENT - Production ready with expansion opportunities"
        elif success_rate >= 75:
            verdict = "✅ GOOD - Solid foundation, ready for targeted expansion"
        elif success_rate >= 60:
            verdict = "⚠️ FAIR - Needs improvements before major expansion"
        else:
            verdict = "❌ POOR - Requires significant fixes before expansion"
        
        print(f"   {verdict}")
        print("="*80)

    def run_comprehensive_assessment(self):
        """Run the complete platform assessment"""
        print("🚀 STARTING COMPREHENSIVE AETHER AUTOMATION PLATFORM ASSESSMENT")
        print("="*80)
        
        # Authentication
        if not self.authenticate():
            print("❌ Assessment failed - could not authenticate")
            return False
        
        # Run all assessments
        self.assess_node_types()
        self.assess_integrations()
        self.assess_templates()
        self.assess_ai_capabilities()
        self.assess_workflow_engine()
        self.assess_features_utilization()
        self.identify_expansion_opportunities()
        
        # Generate final report
        self.generate_comprehensive_report()
        
        return True

if __name__ == "__main__":
    print("🎯 Aether Automation Platform Comprehensive Assessment")
    print("Focus: Quantifying current capabilities for expansion planning")
    print("-" * 60)
    
    assessor = AetherPlatformAssessment()
    success = assessor.run_comprehensive_assessment()
    
    if success:
        print("\n✅ Comprehensive assessment completed successfully!")
    else:
        print("\n❌ Assessment completed with issues")
    
    sys.exit(0 if success else 1)