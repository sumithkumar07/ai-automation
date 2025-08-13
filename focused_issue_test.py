#!/usr/bin/env python3
"""
Focused Issue Testing for Aether Automation Platform
Targeting specific issues found in comprehensive testing
"""

import requests
import sys
import json
import time
import uuid
from datetime import datetime

class FocusedIssueTester:
    def __init__(self, base_url="https://integration-verify-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.issues_found = []
        self.session_id = str(uuid.uuid4())

    def authenticate(self):
        """Quick authentication"""
        test_user = {
            "email": f"focused_test_{self.session_id[:8]}@aether.com",
            "password": "SecurePass123!",
            "first_name": "Focused",
            "last_name": "Tester"
        }
        
        try:
            response = requests.post(f"{self.api_url}/auth/register", json=test_user, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access_token')
                self.user_id = data.get('user_id')
                print(f"✅ Authentication successful")
                return True
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
        return False

    def test_template_creation_issue(self):
        """Test the template creation 500 error"""
        print("\n🔍 TESTING TEMPLATE CREATION ISSUE")
        
        if not self.token:
            print("❌ No authentication token")
            return
            
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        # Simple template data
        template_data = {
            "name": f"Test Template {self.session_id[:8]}",
            "description": "Simple test template",
            "category": "automation",
            "workflow_definition": {
                "nodes": [
                    {"id": "node1", "type": "trigger", "name": "Start"}
                ],
                "edges": []
            }
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/templates/create", 
                json=template_data, 
                headers=headers, 
                timeout=15
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
            if response.status_code == 500:
                self.issues_found.append("Template creation returns 500 error")
                print("❌ Template creation still failing with 500 error")
            elif response.status_code == 200:
                print("✅ Template creation working")
            else:
                print(f"⚠️ Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            self.issues_found.append(f"Template creation request error: {e}")

    def test_template_detail_async_issue(self):
        """Test the template detail async issue"""
        print("\n🔍 TESTING TEMPLATE DETAIL ASYNC ISSUE")
        
        # Test with known template IDs
        template_ids = ["template_1", "template_2", "template_3"]
        
        for template_id in template_ids:
            try:
                response = requests.get(f"{self.api_url}/templates/{template_id}", timeout=15)
                print(f"Template {template_id}: Status {response.status_code}")
                
                if response.status_code == 500:
                    print(f"❌ Template {template_id} detail retrieval failing")
                    if "await" in response.text.lower():
                        self.issues_found.append(f"Template {template_id} has async/await issue")
                elif response.status_code == 200:
                    print(f"✅ Template {template_id} detail working")
                    
            except Exception as e:
                print(f"❌ Template {template_id} request failed: {e}")

    def test_ai_endpoints_404(self):
        """Test AI endpoints returning 404"""
        print("\n🔍 TESTING AI ENDPOINTS 404 ISSUE")
        
        ai_endpoints = [
            ("ai/integrations", "GET"),
            ("ai/integrations/suggestions", "GET"),
            ("ai/workflow/generate", "POST"),
        ]
        
        headers = {'Authorization': f'Bearer {self.token}'} if self.token else {}
        
        for endpoint, method in ai_endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{self.api_url}/{endpoint}", headers=headers, timeout=10)
                else:
                    test_data = {"description": "test workflow", "integrations": ["gmail"]}
                    response = requests.post(f"{self.api_url}/{endpoint}", json=test_data, headers=headers, timeout=10)
                
                print(f"{method} {endpoint}: Status {response.status_code}")
                
                if response.status_code == 404:
                    self.issues_found.append(f"AI endpoint {endpoint} returns 404")
                    print(f"❌ {endpoint} not found")
                elif response.status_code == 200:
                    print(f"✅ {endpoint} working")
                else:
                    print(f"⚠️ {endpoint} status: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {endpoint} request failed: {e}")

    def test_ai_chat_parameter_issue(self):
        """Test AI chat parameter issue"""
        print("\n🔍 TESTING AI CHAT PARAMETER ISSUE")
        
        if not self.token:
            print("❌ No authentication token")
            return
            
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        # Test different parameter formats
        test_cases = [
            {"message": "How do I create a workflow?"},  # Body parameter
            {"query": {"message": "How do I create a workflow?"}},  # Query parameter format
        ]
        
        for i, test_data in enumerate(test_cases):
            try:
                response = requests.post(
                    f"{self.api_url}/ai/chat", 
                    json=test_data, 
                    headers=headers, 
                    timeout=10
                )
                
                print(f"Test case {i+1}: Status {response.status_code}")
                
                if response.status_code == 422:
                    print(f"❌ Parameter validation error: {response.text[:200]}")
                elif response.status_code == 200:
                    print(f"✅ AI chat working with test case {i+1}")
                    break
                    
            except Exception as e:
                print(f"❌ AI chat test case {i+1} failed: {e}")

    def test_workflow_authentication_issue(self):
        """Test workflow authentication issue"""
        print("\n🔍 TESTING WORKFLOW AUTHENTICATION ISSUE")
        
        if not self.token:
            print("❌ No authentication token")
            return
            
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        # Test workflow creation
        workflow_data = {
            "name": f"Test Workflow {self.session_id[:8]}",
            "description": "Test workflow for authentication"
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/workflows", 
                json=workflow_data, 
                headers=headers, 
                timeout=10
            )
            
            print(f"Workflow creation: Status {response.status_code}")
            
            if response.status_code == 403:
                self.issues_found.append("Workflow creation returns 403 authentication error")
                print("❌ Workflow authentication still failing")
            elif response.status_code == 200:
                print("✅ Workflow creation working")
            else:
                print(f"⚠️ Unexpected workflow creation status: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Workflow creation failed: {e}")

    def test_integration_count_verification(self):
        """Quick integration count check"""
        print("\n🔍 TESTING INTEGRATION COUNT")
        
        try:
            response = requests.get(f"{self.api_url}/integrations", timeout=10)
            if response.status_code == 200:
                integrations = response.json()
                count = len(integrations)
                print(f"📊 Integration count: {count}")
                
                if count >= 100:
                    print("✅ Integration count meets homepage promise (100+)")
                elif count >= 62:
                    print(f"⚠️ Integration count ({count}) approaching promise but not yet 100+")
                else:
                    print(f"❌ Integration count ({count}) below promise")
                    self.issues_found.append(f"Only {count} integrations vs 100+ promised")
            else:
                print(f"❌ Failed to get integrations: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Integration count check failed: {e}")

    def run_focused_tests(self):
        """Run all focused tests"""
        print("🎯 FOCUSED ISSUE TESTING - AETHER AUTOMATION")
        print("=" * 50)
        print(f"Backend URL: {self.api_url}")
        print(f"Session ID: {self.session_id}")
        print("=" * 50)
        
        start_time = time.time()
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Cannot proceed without authentication")
            return
        
        # Run focused tests
        self.test_template_creation_issue()
        self.test_template_detail_async_issue()
        self.test_ai_endpoints_404()
        self.test_ai_chat_parameter_issue()
        self.test_workflow_authentication_issue()
        self.test_integration_count_verification()
        
        # Summary
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 50)
        print("🎯 FOCUSED ISSUE TEST RESULTS")
        print("=" * 50)
        print(f"Duration: {duration:.2f} seconds")
        
        if self.issues_found:
            print(f"\n❌ ISSUES FOUND ({len(self.issues_found)}):")
            for i, issue in enumerate(self.issues_found, 1):
                print(f"   {i}. {issue}")
        else:
            print("\n✅ NO CRITICAL ISSUES FOUND")
        
        print("=" * 50)
        
        return {
            "issues_found": self.issues_found,
            "duration": duration
        }

if __name__ == "__main__":
    tester = FocusedIssueTester()
    results = tester.run_focused_tests()
    
    # Exit with appropriate code
    if results["issues_found"]:
        sys.exit(1)
    else:
        sys.exit(0)