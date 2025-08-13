#!/usr/bin/env python3

import requests
import json
import sys
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')

def test_backend_basic():
    """Test basic backend connectivity"""
    print(f"🔍 Testing backend connectivity at {BACKEND_URL}")
    
    try:
        # Test health endpoint
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=10)
        print(f"Health endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is healthy: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to backend at {BACKEND_URL}")
        return False
    except Exception as e:
        print(f"❌ Backend test error: {e}")
        return False

def test_auth_endpoints():
    """Test authentication endpoints"""
    print(f"\n🔍 Testing authentication endpoints")
    
    # Test signup
    signup_data = {
        "name": f"Test User {datetime.now().strftime('%H%M%S')}",
        "email": f"test_{datetime.now().strftime('%H%M%S')}@example.com", 
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/signup", json=signup_data, timeout=10)
        print(f"Signup status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'token' in data:
                print(f"✅ Signup successful, token received")
                return data['token'], data['user']['id']
            else:
                print(f"❌ Signup response missing token")
                return None, None
        else:
            print(f"❌ Signup failed: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ Signup test error: {e}")
        return None, None

def test_protected_endpoint(token):
    """Test a protected endpoint"""
    print(f"\n🔍 Testing protected endpoint")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/dashboard/stats", headers=headers, timeout=10)
        print(f"Dashboard stats status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard stats retrieved successfully")
            print(f"Stats: {json.dumps(data, indent=2)[:200]}...")
            return True
        else:
            print(f"❌ Dashboard stats failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Protected endpoint test error: {e}")
        return False

def main():
    print("🚀 Simple Backend Connectivity Test")
    print("=" * 50)
    
    # Test basic connectivity
    if not test_backend_basic():
        print("\n❌ Backend is not accessible, stopping tests")
        return 1
    
    # Test authentication
    token, user_id = test_auth_endpoints()
    if not token:
        print("\n❌ Authentication failed, stopping tests")
        return 1
    
    # Test protected endpoint
    if not test_protected_endpoint(token):
        print("\n❌ Protected endpoint test failed")
        return 1
    
    print("\n✅ All basic backend tests passed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())