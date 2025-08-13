#!/usr/bin/env python3
"""
DETAILED ERROR ANALYSIS TEST
Get exact error messages and validation details for failing endpoints
"""

import requests
import json

def test_specific_endpoints():
    base_url = "https://frontend-e2e-test.preview.emergentagent.com"
    
    # First authenticate
    auth_data = {
        "email": f"test_error_analysis@example.com",
        "password": "TestPass123!",
        "first_name": "Test",
        "last_name": "User"
    }
    
    auth_response = requests.post(f"{base_url}/api/auth/register", json=auth_data)
    if auth_response.status_code == 200:
        token = auth_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    else:
        print("❌ Authentication failed")
        return
    
    print("🔍 DETAILED ERROR ANALYSIS")
    print("=" * 50)
    
    # Test 1: Template creation error
    print("\n1. TEMPLATE CREATION ERROR ANALYSIS:")
    template_data = {
        "name": "Test Template",
        "description": "Test template for error analysis",
        "category": "automation",
        "nodes": [{"id": "node1", "type": "trigger", "name": "Test"}],
        "connections": []
    }
    
    response = requests.post(f"{base_url}/api/templates/create", json=template_data, headers=headers)
    print(f"   Status: {response.status_code}")
    try:
        error_detail = response.json()
        print(f"   Error: {json.dumps(error_detail, indent=2)}")
    except:
        print(f"   Raw response: {response.text}")
    
    # Test 2: Integration search parameter validation
    print("\n2. INTEGRATION SEARCH PARAMETER VALIDATION:")
    search_params = [
        {"query": "slack"},
        {"q": "slack"},
        {"search": "slack"}
    ]
    
    for params in search_params:
        response = requests.get(f"{base_url}/api/integrations/search", params=params, headers=headers)
        print(f"   Params {params}: Status {response.status_code}")
        if response.status_code != 200:
            try:
                error_detail = response.json()
                print(f"      Error: {error_detail}")
            except:
                print(f"      Raw: {response.text}")
    
    # Test 3: AI integration suggestions validation
    print("\n3. AI INTEGRATION SUGGESTIONS VALIDATION:")
    ai_data_variants = [
        {"description": "Test workflow"},
        {"workflow_description": "Test workflow"},
        {"prompt": "Test workflow"}
    ]
    
    for data in ai_data_variants:
        response = requests.post(f"{base_url}/api/ai/suggest-integrations", json=data, headers=headers)
        print(f"   Data {data}: Status {response.status_code}")
        if response.status_code != 200:
            try:
                error_detail = response.json()
                print(f"      Error: {error_detail}")
            except:
                print(f"      Raw: {response.text}")
    
    # Test 4: Node types response format
    print("\n4. NODE TYPES RESPONSE FORMAT:")
    response = requests.get(f"{base_url}/api/node-types", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"   Response type: {type(data)}")
            if isinstance(data, dict):
                print(f"   Keys: {list(data.keys())}")
            elif isinstance(data, list):
                print(f"   List length: {len(data)}")
                if data:
                    print(f"   First item: {data[0]}")
        except:
            print(f"   Raw: {response.text}")

if __name__ == "__main__":
    test_specific_endpoints()