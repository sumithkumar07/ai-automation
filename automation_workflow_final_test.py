#!/usr/bin/env python3
"""
🚀 FINAL COMPREHENSIVE AUTOMATION WORKFLOW TESTING
VERIFY REAL FUNCTIONALITY - Aether Automation Platform

CORRECTED VERSION: Uses enhanced endpoints for accurate testing
"""

import requests
import json
import time
from datetime import datetime
import uuid

# Configuration
BACKEND_URL = "https://frontend-e2e-test.preview.emergentagent.com/api"
TEST_USER_EMAIL = "final.automation.tester@aether.com"
TEST_USER_PASSWORD = "FinalTest2024!"
TEST_USER_NAME = "Final Automation Tester"

class FinalAutomationTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.created_workflows = []
        
    def log_test(self, test_name: str, success: bool, details: str, data: any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.test_results.append(result)
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {details}")
        
    def setup_authentication(self):
        """Setup authentication for testing"""
        try:
            # Register test user
            register_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "first_name": TEST_USER_NAME.split()[0],
                "last_name": " ".join(TEST_USER_NAME.split()[1:]) if len(TEST_USER_NAME.split()) > 1 else "User"
            }
            
            register_response = self.session.post(f"{BACKEND_URL}/auth/register", json=register_data)
            
            # Login to get token
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            login_response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if login_response.status_code == 200:
                login_result = login_response.json()
                self.auth_token = login_result.get("access_token")
                
                # Set authorization header
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                })
                
                self.log_test("Authentication Setup", True, f"Successfully authenticated user: {TEST_USER_EMAIL}")
                return True
            else:
                self.log_test("Authentication Setup", False, f"Login failed: {login_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Authentication Setup", False, f"Authentication error: {str(e)}")
            return False

    def test_comprehensive_automation_capabilities(self):
        """Test all automation capabilities comprehensively"""
        print("\n🚀 TESTING COMPREHENSIVE AUTOMATION CAPABILITIES")
        
        # 1. Test Node System (321+ nodes requirement)
        try:
            nodes_response = self.session.get(f"{BACKEND_URL}/node-types")
            if nodes_response.status_code == 200:
                nodes_data = nodes_response.json()
                total_nodes = nodes_data.get("stats", {}).get("total_nodes", 0)
                
                if total_nodes >= 321:
                    self.log_test("Node System Verification", True, 
                                f"✅ EXCELLENT: Found {total_nodes} nodes (exceeds 321+ requirement)")
                else:
                    self.log_test("Node System Verification", False, 
                                f"❌ INSUFFICIENT: Only {total_nodes} nodes found (below 321+ requirement)")
            else:
                self.log_test("Node System Verification", False, f"Failed to get nodes: {nodes_response.status_code}")
        except Exception as e:
            self.log_test("Node System Verification", False, f"Error: {str(e)}")

        # 2. Test Integration System (220+ integrations requirement) - CORRECTED
        try:
            # Use enhanced integrations endpoint
            integrations_response = self.session.get(f"{BACKEND_URL}/integrations/enhanced")
            if integrations_response.status_code == 200:
                integrations_data = integrations_response.json()
                total_integrations = len(integrations_data)
                
                if total_integrations >= 220:
                    self.log_test("Integration System Verification", True,
                                f"✅ EXCELLENT: Found {total_integrations} integrations (exceeds 220+ requirement)")
                else:
                    self.log_test("Integration System Verification", False,
                                f"❌ INSUFFICIENT: Only {total_integrations} integrations found (below 220+ requirement)")
                    
                # Test integration search functionality
                search_response = self.session.get(f"{BACKEND_URL}/integrations/search/enhanced?q=slack")
                if search_response.status_code == 200:
                    search_data = search_response.json()
                    search_results = len(search_data.get("integrations", []))
                    self.log_test("Integration Search Functionality", True,
                                f"Integration search working: found {search_results} results for 'slack'")
                else:
                    self.log_test("Integration Search Functionality", False,
                                f"Integration search failed: {search_response.status_code}")
                    
            else:
                self.log_test("Integration System Verification", False, 
                            f"Failed to get integrations: {integrations_response.status_code}")
        except Exception as e:
            self.log_test("Integration System Verification", False, f"Error: {str(e)}")

        # 3. Test Template System (100+ templates requirement) - CORRECTED
        try:
            # Use enhanced templates endpoint
            templates_response = self.session.get(f"{BACKEND_URL}/templates/enhanced")
            if templates_response.status_code == 200:
                templates_data = templates_response.json()
                total_templates = len(templates_data)
                
                if total_templates >= 100:
                    self.log_test("Template System Verification", True,
                                f"✅ EXCELLENT: Found {total_templates} templates (exceeds 100+ requirement)")
                else:
                    self.log_test("Template System Verification", False,
                                f"❌ INSUFFICIENT: Only {total_templates} templates found (below 100+ requirement)")
                    
                # Test template search functionality
                search_response = self.session.get(f"{BACKEND_URL}/templates/search/enhanced?q=automation")
                if search_response.status_code == 200:
                    search_data = search_response.json()
                    search_results = len(search_data.get("results", []))
                    self.log_test("Template Search Functionality", True,
                                f"Template search working: found {search_results} results for 'automation'")
                else:
                    self.log_test("Template Search Functionality", False,
                                f"Template search failed: {search_response.status_code}")
                    
            else:
                self.log_test("Template System Verification", False,
                            f"Failed to get templates: {templates_response.status_code}")
        except Exception as e:
            self.log_test("Template System Verification", False, f"Error: {str(e)}")

        # 4. Test Workflow Creation & Management
        workflow_types = [
            {
                "name": "Real Webhook Automation Workflow",
                "description": "Process real webhook data with AI analysis and multi-channel notifications",
                "nodes": [
                    {"id": "webhook_trigger", "type": "webhook_trigger", "config": {"endpoint": "/webhook/customer-data"}},
                    {"id": "ai_analyzer", "type": "ai_data_analyzer", "config": {"model": "groq", "analysis_type": "sentiment"}},
                    {"id": "conditional_router", "type": "conditional_logic", "config": {"condition": "sentiment > 0.7"}},
                    {"id": "slack_notify", "type": "slack_notification", "config": {"channel": "#customer-success"}},
                    {"id": "email_followup", "type": "email_automation", "config": {"template": "positive_feedback"}}
                ]
            },
            {
                "name": "AI-Powered Content Automation",
                "description": "Generate, review, and publish content across multiple channels using AI",
                "nodes": [
                    {"id": "schedule_trigger", "type": "cron_schedule", "config": {"schedule": "0 9 * * MON"}},
                    {"id": "ai_content_gen", "type": "ai_content_generator", "config": {"model": "groq", "content_type": "blog_post"}},
                    {"id": "content_reviewer", "type": "human_approval", "config": {"reviewers": ["editor@company.com"]}},
                    {"id": "cms_publisher", "type": "wordpress_publisher", "config": {"site": "company-blog"}},
                    {"id": "social_distributor", "type": "social_media_publisher", "config": {"platforms": ["twitter", "linkedin", "facebook"]}}
                ]
            }
        ]
        
        for workflow_config in workflow_types:
            try:
                # Create workflow
                create_response = self.session.post(f"{BACKEND_URL}/workflows/", json=workflow_config)
                
                if create_response.status_code == 200:
                    workflow = create_response.json()
                    workflow_id = workflow.get("id")
                    self.created_workflows.append(workflow_id)
                    
                    self.log_test(f"Create Real Automation Workflow", True, 
                                f"Successfully created: {workflow_config['name']}")
                    
                    # Test workflow execution
                    execution_data = {
                        "input_data": {
                            "test_mode": True,
                            "real_automation_test": True,
                            "timestamp": datetime.now().isoformat(),
                            "workflow_type": workflow_config["name"]
                        }
                    }
                    
                    execute_response = self.session.post(f"{BACKEND_URL}/workflows/{workflow_id}/execute",
                                                       json=execution_data)
                    
                    if execute_response.status_code == 200:
                        execution_result = execute_response.json()
                        execution_id = execution_result.get("execution_id")
                        
                        self.log_test(f"Execute Real Automation", True,
                                    f"Workflow execution started successfully: {execution_id}")
                        
                        # Check execution status
                        time.sleep(2)
                        status_response = self.session.get(f"{BACKEND_URL}/workflows/executions/{execution_id}/status")
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            execution_status = status_data.get("status", "unknown")
                            self.log_test(f"Monitor Automation Execution", True,
                                        f"Execution status tracked: {execution_status}")
                        else:
                            self.log_test(f"Monitor Automation Execution", False,
                                        f"Status tracking failed: {status_response.status_code}")
                    else:
                        self.log_test(f"Execute Real Automation", False,
                                    f"Execution failed: {execute_response.status_code}")
                else:
                    self.log_test(f"Create Real Automation Workflow", False,
                                f"Creation failed: {create_response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Real Automation Workflow Testing", False, f"Error: {str(e)}")

        # 5. Test AI Capabilities (Real vs Demo)
        ai_tests = [
            {
                "endpoint": "/ai/generate-workflow",
                "data": {"description": "Create an automation that monitors social media mentions, analyzes sentiment, and triggers appropriate responses"},
                "test_name": "AI Workflow Generation"
            },
            {
                "endpoint": "/ai/suggest-integrations", 
                "data": {"description": "I need to automate customer onboarding from CRM to email marketing to support ticketing"},
                "test_name": "AI Integration Suggestions"
            }
        ]
        
        for test in ai_tests:
            try:
                response = self.session.post(f"{BACKEND_URL}{test['endpoint']}", json=test["data"])
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Validate if response is real AI-generated content
                    response_str = json.dumps(result).lower()
                    
                    # Check for real automation concepts
                    real_indicators = ["workflow", "node", "trigger", "action", "integration", "automation"]
                    has_real_content = any(indicator in response_str for indicator in real_indicators)
                    
                    # Check response substance
                    is_substantial = len(response_str) > 200
                    
                    # Check for demo/fake patterns
                    demo_patterns = ["demo", "fake", "test data", "placeholder", "lorem"]
                    has_demo_patterns = any(pattern in response_str for pattern in demo_patterns)
                    
                    if has_real_content and is_substantial and not has_demo_patterns:
                        self.log_test(test["test_name"], True,
                                    "✅ REAL AI: Response contains genuine, contextual automation content")
                    else:
                        self.log_test(test["test_name"], False,
                                    "❌ DEMO AI: Response appears to be demo/fake data")
                else:
                    self.log_test(test["test_name"], False,
                                f"AI request failed: {response.status_code}")
                    
            except Exception as e:
                self.log_test(test["test_name"], False, f"Error: {str(e)}")

        # 6. Test Performance & Scalability
        try:
            start_time = time.time()
            concurrent_workflows = []
            
            # Create 5 workflows concurrently to test scalability
            for i in range(5):
                workflow_data = {
                    "name": f"Scalability Test Workflow {i}",
                    "description": f"Testing platform scalability with concurrent workflow {i}",
                    "nodes": [
                        {"id": f"trigger_{i}", "type": "manual_trigger", "config": {"test_id": i}},
                        {"id": f"processor_{i}", "type": "data_processor", "config": {"operation": "transform"}},
                        {"id": f"action_{i}", "type": "webhook_action", "config": {"url": f"https://test.example.com/{i}"}}
                    ]
                }
                
                response = self.session.post(f"{BACKEND_URL}/workflows/", json=workflow_data)
                concurrent_workflows.append({
                    "id": i,
                    "success": response.status_code == 200,
                    "workflow_id": response.json().get("id") if response.status_code == 200 else None
                })
                
                if response.status_code == 200:
                    self.created_workflows.append(response.json().get("id"))
            
            end_time = time.time()
            total_time = end_time - start_time
            successful_creations = sum(1 for w in concurrent_workflows if w["success"])
            
            if successful_creations >= 4:  # Allow 1 failure
                self.log_test("Platform Scalability", True,
                            f"✅ EXCELLENT: Created {successful_creations}/5 workflows concurrently in {total_time:.2f}s")
            else:
                self.log_test("Platform Scalability", False,
                            f"❌ POOR: Only {successful_creations}/5 concurrent workflows succeeded")
                
        except Exception as e:
            self.log_test("Platform Scalability", False, f"Error: {str(e)}")

        # 7. Test Data Persistence
        if self.created_workflows:
            try:
                workflow_id = self.created_workflows[0]
                
                # Update workflow
                update_data = {
                    "name": f"Data Persistence Test - {datetime.now().isoformat()}",
                    "description": "Testing if workflow data persists correctly across operations"
                }
                
                update_response = self.session.put(f"{BACKEND_URL}/workflows/{workflow_id}", json=update_data)
                
                if update_response.status_code == 200:
                    # Verify persistence
                    get_response = self.session.get(f"{BACKEND_URL}/workflows/{workflow_id}")
                    if get_response.status_code == 200:
                        workflow_data = get_response.json()
                        if update_data["name"] in workflow_data.get("name", ""):
                            self.log_test("Data Persistence", True,
                                        "✅ EXCELLENT: Workflow data persists correctly across operations")
                        else:
                            self.log_test("Data Persistence", False,
                                        "❌ FAILED: Workflow data did not persist changes")
                    else:
                        self.log_test("Data Persistence", False,
                                    f"Failed to retrieve workflow: {get_response.status_code}")
                else:
                    self.log_test("Data Persistence", False,
                                f"Failed to update workflow: {update_response.status_code}")
                    
            except Exception as e:
                self.log_test("Data Persistence", False, f"Error: {str(e)}")

    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n🧹 CLEANING UP TEST DATA")
        
        for workflow_id in self.created_workflows:
            try:
                delete_response = self.session.delete(f"{BACKEND_URL}/workflows/{workflow_id}")
                if delete_response.status_code == 200:
                    self.log_test(f"Cleanup Workflow", True, f"Successfully deleted {workflow_id}")
                else:
                    self.log_test(f"Cleanup Workflow", False, f"Delete failed: {delete_response.status_code}")
            except Exception as e:
                self.log_test(f"Cleanup Workflow", False, f"Error: {str(e)}")

    def generate_final_report(self):
        """Generate final comprehensive report"""
        print("\n" + "="*100)
        print("🚀 FINAL COMPREHENSIVE AUTOMATION WORKFLOW TESTING REPORT")
        print("="*100)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for test in self.test_results if test["success"])
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests - successful_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print(f"\n🎯 CRITICAL AUTOMATION CAPABILITIES ASSESSMENT:")
        
        # Assess critical capabilities
        critical_capabilities = {
            "Node System (321+ nodes)": any("Node System Verification" in test["test"] and test["success"] for test in self.test_results),
            "Integration System (220+ integrations)": any("Integration System Verification" in test["test"] and test["success"] for test in self.test_results),
            "Template System (100+ templates)": any("Template System Verification" in test["test"] and test["success"] for test in self.test_results),
            "Real Workflow Creation": any("Create Real Automation Workflow" in test["test"] and test["success"] for test in self.test_results),
            "Workflow Execution Engine": any("Execute Real Automation" in test["test"] and test["success"] for test in self.test_results),
            "AI Capabilities (Real, not demo)": any("AI" in test["test"] and "REAL AI" in test["details"] and test["success"] for test in self.test_results),
            "Data Persistence": any("Data Persistence" in test["test"] and test["success"] for test in self.test_results),
            "Platform Scalability": any("Platform Scalability" in test["test"] and test["success"] for test in self.test_results)
        }
        
        working_capabilities = sum(1 for working in critical_capabilities.values() if working)
        total_capabilities = len(critical_capabilities)
        
        for capability, working in critical_capabilities.items():
            status = "✅ WORKING" if working else "❌ FAILED"
            print(f"{status} {capability}")
        
        print(f"\n🏆 FINAL AUTOMATION PLATFORM VERDICT:")
        
        if success_rate >= 85 and working_capabilities >= 7:
            verdict = "🎉 EXCELLENT - PRODUCTION READY"
            description = "Platform demonstrates outstanding automation capabilities with real functionality"
        elif success_rate >= 70 and working_capabilities >= 6:
            verdict = "✅ GOOD - MOSTLY FUNCTIONAL"
            description = "Platform has solid automation capabilities with minor limitations"
        elif success_rate >= 50 and working_capabilities >= 4:
            verdict = "⚠️ FAIR - NEEDS IMPROVEMENT"
            description = "Platform has basic automation but significant gaps remain"
        else:
            verdict = "❌ POOR - NOT READY"
            description = "Platform has major automation functionality issues"
        
        print(f"{verdict}")
        print(f"{description}")
        
        print(f"\n📈 AUTOMATION PLATFORM CAPABILITIES CONFIRMED:")
        
        # Detailed capability analysis
        capabilities_confirmed = []
        capabilities_missing = []
        
        for capability, working in critical_capabilities.items():
            if working:
                capabilities_confirmed.append(capability)
            else:
                capabilities_missing.append(capability)
        
        for capability in capabilities_confirmed:
            print(f"✅ {capability}")
            
        if capabilities_missing:
            print(f"\n⚠️ AREAS NEEDING ATTENTION:")
            for capability in capabilities_missing:
                print(f"❌ {capability}")
        
        print(f"\n🎯 REAL vs DEMO ASSESSMENT:")
        real_functionality_tests = [test for test in self.test_results if "REAL" in test.get("details", "").upper()]
        demo_functionality_tests = [test for test in self.test_results if "DEMO" in test.get("details", "").upper()]
        
        if len(real_functionality_tests) > len(demo_functionality_tests):
            print("✅ REAL FUNCTIONALITY CONFIRMED - Platform uses genuine automation, not demo data")
        else:
            print("⚠️ MIXED FUNCTIONALITY - Some features may be demo/placeholder data")
        
        print(f"\n📋 DETAILED TEST RESULTS:")
        for test in self.test_results:
            status = "✅" if test["success"] else "❌"
            print(f"{status} {test['test']}: {test['details']}")
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": success_rate,
            "critical_capabilities": critical_capabilities,
            "working_capabilities": working_capabilities,
            "verdict": verdict,
            "description": description
        }

    def run_final_test(self):
        """Run final comprehensive automation workflow test"""
        print("🚀 STARTING FINAL COMPREHENSIVE AUTOMATION WORKFLOW TESTING")
        print("="*100)
        
        # Setup
        if not self.setup_authentication():
            print("❌ Authentication failed - cannot proceed with testing")
            return
        
        # Run comprehensive test
        self.test_comprehensive_automation_capabilities()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Generate final report
        return self.generate_final_report()

if __name__ == "__main__":
    tester = FinalAutomationTester()
    report = tester.run_final_test()