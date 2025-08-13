#!/usr/bin/env python3
"""
Test the workflow redirect issue
"""

import requests
import time

BASE_URL = "https://expansion-verify.preview.emergentagent.com/api"

def test_workflow_redirect():
    """Test workflow redirect issue"""
    session = requests.Session()
    
    print("🔍 TESTING WORKFLOW REDIRECT ISSUE")
    print("=" * 50)
    
    # Register user and get token
    timestamp = int(time.time())
    test_email = f"redirect_test_{timestamp}@example.com"
    
    register_data = {
        "email": test_email,
        "password": "RedirectTest123!",
        "first_name": "Redirect",
        "last_name": f"Test{timestamp}"
    }
    
    response = session.post(f"{BASE_URL}/auth/register", json=register_data, timeout=15)
    if response.status_code != 200:
        print(f"❌ Registration failed: {response.text}")
        return
    
    data = response.json()
    auth_token = data.get("access_token")
    print(f"✅ Token received: {auth_token[:20]}...")
    
    # Test different URL patterns
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    print("\n1. Testing /api/workflows (without trailing slash):")
    response = requests.get(f"{BASE_URL}/workflows", headers=headers, timeout=10, allow_redirects=False)
    print(f"   Status: {response.status_code}")
    if response.status_code == 307:
        print(f"   ✅ Redirect detected: {response.headers.get('location')}")
        
        # Follow redirect manually with headers
        redirect_url = response.headers.get('location')
        if redirect_url:
            print(f"\n2. Following redirect manually to: {redirect_url}")
            response2 = requests.get(redirect_url, headers=headers, timeout=10)
            print(f"   Status: {response2.status_code}")
            if response2.status_code == 200:
                print(f"   ✅ Manual redirect successful!")
            else:
                print(f"   ❌ Manual redirect failed: {response2.text}")
    
    print("\n3. Testing /api/workflows/ (with trailing slash):")
    response = requests.get(f"{BASE_URL}/workflows/", headers=headers, timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        workflows = response.json()
        print(f"   ✅ Direct call successful: {len(workflows)} workflows")
    else:
        print(f"   ❌ Direct call failed: {response.text}")
    
    print("\n4. Testing POST /api/workflows/ (with trailing slash):")
    workflow_data = {
        "name": f"Redirect Test Workflow {timestamp}",
        "description": "Test workflow for redirect issue"
    }
    response = requests.post(f"{BASE_URL}/workflows/", json=workflow_data, headers=headers, timeout=15)
    print(f"   Status: {response.status_code}")
    if response.status_code in [200, 201]:
        result = response.json()
        print(f"   ✅ POST successful: {result.get('id', 'No ID')}")
    else:
        print(f"   ❌ POST failed: {response.text}")

if __name__ == "__main__":
    test_workflow_redirect()