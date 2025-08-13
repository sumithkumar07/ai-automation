#!/usr/bin/env python3
"""
Workflow Authentication Debug Test
Debug the specific 403 authentication issue with workflow endpoints
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "https://expansion-verify.preview.emergentagent.com/api"

def debug_workflow_auth():
    """Debug workflow authentication issues"""
    session = requests.Session()
    
    print("🔍 DEBUGGING WORKFLOW AUTHENTICATION ISSUE")
    print("=" * 60)
    
    # Step 1: Register a new user
    timestamp = int(time.time())
    test_email = f"workflow_debug_{timestamp}@example.com"
    test_password = "WorkflowDebug123!"
    
    print("1. Registering new user...")
    register_data = {
        "email": test_email,
        "password": test_password,
        "first_name": "Workflow",
        "last_name": f"Debug{timestamp}"
    }
    
    try:
        response = session.post(f"{BASE_URL}/auth/register", json=register_data, timeout=15)
        print(f"   Registration Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            auth_token = data.get("access_token")
            user_id = data.get("user", {}).get("id")
            print(f"   ✅ User registered: {user_id}")
            print(f"   ✅ Token received: {auth_token[:20]}...")
            
            # Set authorization header
            session.headers.update({"Authorization": f"Bearer {auth_token}"})
            
        else:
            print(f"   ❌ Registration failed: {response.text}")
            return
            
    except Exception as e:
        print(f"   ❌ Registration error: {str(e)}")
        return
    
    # Step 2: Verify token works with /auth/me
    print("\n2. Verifying token with /auth/me...")
    try:
        response = session.get(f"{BASE_URL}/auth/me", timeout=10)
        print(f"   Auth/me Status: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"   ✅ Token valid for user: {user_data.get('email')}")
        else:
            print(f"   ❌ Token validation failed: {response.text}")
            return
            
    except Exception as e:
        print(f"   ❌ Token validation error: {str(e)}")
        return
    
    # Step 3: Test workflow endpoints with detailed debugging
    print("\n3. Testing workflow endpoints...")
    
    # Test GET /workflows
    print("\n   3a. Testing GET /workflows...")
    try:
        # Add detailed headers for debugging
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        response = requests.get(f"{BASE_URL}/workflows", headers=headers, timeout=15)
        print(f"      Status: {response.status_code}")
        print(f"      Headers sent: {dict(headers)}")
        print(f"      Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            workflows = response.json()
            print(f"      ✅ GET workflows successful: {len(workflows)} workflows")
        elif response.status_code == 403:
            print(f"      ❌ 403 Forbidden: {response.text}")
            print(f"      Response content: {response.content}")
        else:
            print(f"      ❌ Unexpected status: {response.text}")
            
    except Exception as e:
        print(f"      ❌ GET workflows error: {str(e)}")
    
    # Test POST /workflows
    print("\n   3b. Testing POST /workflows...")
    try:
        workflow_data = {
            "name": f"Debug Workflow {timestamp}",
            "description": "Test workflow for debugging authentication"
        }
        
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        response = requests.post(f"{BASE_URL}/workflows", 
                               json=workflow_data, 
                               headers=headers, 
                               timeout=20)
        print(f"      Status: {response.status_code}")
        print(f"      Headers sent: {dict(headers)}")
        print(f"      Request body: {json.dumps(workflow_data, indent=2)}")
        
        if response.status_code in [200, 201]:
            workflow_result = response.json()
            print(f"      ✅ POST workflow successful: {workflow_result.get('id', 'No ID')}")
        elif response.status_code == 403:
            print(f"      ❌ 403 Forbidden: {response.text}")
            print(f"      Response content: {response.content}")
        else:
            print(f"      ❌ Unexpected status: {response.text}")
            
    except Exception as e:
        print(f"      ❌ POST workflow error: {str(e)}")
    
    # Step 4: Test other protected endpoints for comparison
    print("\n4. Testing other protected endpoints for comparison...")
    
    # Test dashboard stats (should work)
    print("\n   4a. Testing GET /dashboard/stats...")
    try:
        response = session.get(f"{BASE_URL}/dashboard/stats", timeout=10)
        print(f"      Status: {response.status_code}")
        if response.status_code == 200:
            print(f"      ✅ Dashboard stats working")
        else:
            print(f"      ❌ Dashboard stats failed: {response.text}")
    except Exception as e:
        print(f"      ❌ Dashboard stats error: {str(e)}")
    
    # Test templates (might have issues)
    print("\n   4b. Testing GET /templates/...")
    try:
        response = session.get(f"{BASE_URL}/templates/", timeout=10)
        print(f"      Status: {response.status_code}")
        if response.status_code == 200:
            print(f"      ✅ Templates working")
        else:
            print(f"      ❌ Templates failed: {response.text}")
    except Exception as e:
        print(f"      ❌ Templates error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🔍 WORKFLOW AUTHENTICATION DEBUG COMPLETED")

if __name__ == "__main__":
    debug_workflow_auth()