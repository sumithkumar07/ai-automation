#!/usr/bin/env python3
"""
Extended Authentication Testing - Token Validation
"""

import requests
import json

# Get backend URL from environment
BACKEND_URL = "https://subscription-model.preview.emergentagent.com/api"

# Test data
TEST_USER_DATA = {
    "email": "token.test@example.com",
    "password": "testpass123",
    "first_name": "Token",
    "last_name": "Test",
    "company": "Test Corp"
}

def test_token_authentication():
    """Test token-based authentication flow"""
    print("🔑 TOKEN AUTHENTICATION TESTING")
    print("=" * 50)
    
    # Step 1: Register a new user
    print("1. Registering new user...")
    response = requests.post(f"{BACKEND_URL}/auth/signup", json=TEST_USER_DATA)
    
    if response.status_code == 200:
        data = response.json()
        token = data["access_token"]
        print(f"✅ User registered successfully. Token: {token[:20]}...")
    elif response.status_code == 400:
        # User already exists, try to login
        print("User already exists, attempting login...")
        login_data = {
            "email": TEST_USER_DATA["email"],
            "password": TEST_USER_DATA["password"]
        }
        response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data["access_token"]
            print(f"✅ Login successful. Token: {token[:20]}...")
        else:
            print(f"❌ Login failed: {response.status_code}")
            return
    else:
        print(f"❌ Registration failed: {response.status_code}")
        return
    
    # Step 2: Test /me endpoint with token
    print("\n2. Testing /api/auth/me endpoint with token...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BACKEND_URL}/auth/me", headers=headers)
    
    if response.status_code == 200:
        user_data = response.json()
        print(f"✅ /me endpoint working. User: {user_data.get('email', 'N/A')}")
        print(f"   User ID: {user_data.get('id', 'N/A')}")
        print(f"   Name: {user_data.get('first_name', '')} {user_data.get('last_name', '')}")
        print(f"   Company: {user_data.get('company', 'N/A')}")
    else:
        print(f"❌ /me endpoint failed: {response.status_code}")
        print(f"   Response: {response.text}")
    
    # Step 3: Test with invalid token
    print("\n3. Testing with invalid token...")
    invalid_headers = {"Authorization": "Bearer invalid_token_here"}
    response = requests.get(f"{BACKEND_URL}/auth/me", headers=invalid_headers)
    
    if response.status_code == 401:
        print("✅ Invalid token properly rejected with 401")
    else:
        print(f"❌ Unexpected response to invalid token: {response.status_code}")
    
    # Step 4: Test without token
    print("\n4. Testing without token...")
    response = requests.get(f"{BACKEND_URL}/auth/me")
    
    if response.status_code == 401:
        print("✅ Missing token properly rejected with 401")
    else:
        print(f"❌ Unexpected response to missing token: {response.status_code}")
    
    print("\n🏁 TOKEN AUTHENTICATION TESTING COMPLETED")
    print("=" * 50)

if __name__ == "__main__":
    test_token_authentication()