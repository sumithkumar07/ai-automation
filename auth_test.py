#!/usr/bin/env python3
"""
Authentication Endpoint Testing Script
Tests the authentication endpoints to verify the fixes work correctly.
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://feature-explorer-11.preview.emergentagent.com/api"

# Test data as specified in the review request
TEST_USER_DATA = {
    "email": "test@example.com",
    "password": "testpass123",
    "first_name": "Test",
    "last_name": "User",
    "company": "Test Corp"
}

def print_test_result(test_name, success, details=""):
    """Print formatted test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"   {details}")
    print()

def test_auth_endpoints():
    """Test all authentication endpoints"""
    print("🔐 AUTHENTICATION ENDPOINT TESTING")
    print("=" * 50)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test User: {TEST_USER_DATA['email']}")
    print()
    
    # Test 1: POST /api/auth/signup endpoint (newly added)
    print("1. Testing POST /api/auth/signup endpoint...")
    try:
        response = requests.post(f"{BACKEND_URL}/auth/signup", json=TEST_USER_DATA)
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data and "user" in data:
                signup_token = data["access_token"]
                user_info = data["user"]
                print_test_result("POST /api/auth/signup", True, 
                    f"User created successfully. Token received. User ID: {user_info.get('id', 'N/A')}")
            else:
                print_test_result("POST /api/auth/signup", False, 
                    f"Missing required fields in response: {data}")
        elif response.status_code == 400 and "already registered" in response.text:
            print_test_result("POST /api/auth/signup", True, 
                "User already exists (expected for repeated tests)")
            signup_token = None
        else:
            print_test_result("POST /api/auth/signup", False, 
                f"Status: {response.status_code}, Response: {response.text}")
            signup_token = None
    except Exception as e:
        print_test_result("POST /api/auth/signup", False, f"Exception: {str(e)}")
        signup_token = None

    # Test 2: POST /api/auth/register endpoint (existing)
    print("2. Testing POST /api/auth/register endpoint...")
    try:
        # Use slightly different email to avoid conflict
        register_data = TEST_USER_DATA.copy()
        register_data["email"] = "test.register@example.com"
        
        response = requests.post(f"{BACKEND_URL}/auth/register", json=register_data)
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data and "user" in data:
                register_token = data["access_token"]
                user_info = data["user"]
                print_test_result("POST /api/auth/register", True, 
                    f"User registered successfully. Token received. User ID: {user_info.get('id', 'N/A')}")
            else:
                print_test_result("POST /api/auth/register", False, 
                    f"Missing required fields in response: {data}")
        elif response.status_code == 400 and "already registered" in response.text:
            print_test_result("POST /api/auth/register", True, 
                "User already exists (expected for repeated tests)")
            register_token = None
        else:
            print_test_result("POST /api/auth/register", False, 
                f"Status: {response.status_code}, Response: {response.text}")
            register_token = None
    except Exception as e:
        print_test_result("POST /api/auth/register", False, f"Exception: {str(e)}")
        register_token = None

    # Test 3: POST /api/auth/login endpoint
    print("3. Testing POST /api/auth/login endpoint...")
    try:
        login_data = {
            "email": TEST_USER_DATA["email"],
            "password": TEST_USER_DATA["password"]
        }
        
        response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data and "user" in data:
                login_token = data["access_token"]
                user_info = data["user"]
                print_test_result("POST /api/auth/login", True, 
                    f"Login successful. Token received. User: {user_info.get('email', 'N/A')}")
            else:
                print_test_result("POST /api/auth/login", False, 
                    f"Missing required fields in response: {data}")
        else:
            print_test_result("POST /api/auth/login", False, 
                f"Status: {response.status_code}, Response: {response.text}")
            login_token = None
    except Exception as e:
        print_test_result("POST /api/auth/login", False, f"Exception: {str(e)}")
        login_token = None

    # Test 4: Verify both signup and register work with same functionality
    print("4. Testing functional equivalence of signup vs register...")
    try:
        # Test with new emails to ensure clean comparison
        signup_test_data = TEST_USER_DATA.copy()
        signup_test_data["email"] = "signup.test@example.com"
        
        register_test_data = TEST_USER_DATA.copy()
        register_test_data["email"] = "register.test@example.com"
        
        # Test signup
        signup_response = requests.post(f"{BACKEND_URL}/auth/signup", json=signup_test_data)
        register_response = requests.post(f"{BACKEND_URL}/auth/register", json=register_test_data)
        
        if signup_response.status_code == register_response.status_code == 200:
            signup_data = signup_response.json()
            register_data = register_response.json()
            
            # Check if both return same structure
            signup_keys = set(signup_data.keys())
            register_keys = set(register_data.keys())
            
            if signup_keys == register_keys:
                print_test_result("Functional equivalence test", True, 
                    "Both signup and register return identical response structure")
            else:
                print_test_result("Functional equivalence test", False, 
                    f"Different response structures. Signup: {signup_keys}, Register: {register_keys}")
        elif signup_response.status_code == register_response.status_code == 400:
            print_test_result("Functional equivalence test", True, 
                "Both endpoints handle existing users consistently")
        else:
            print_test_result("Functional equivalence test", False, 
                f"Different status codes. Signup: {signup_response.status_code}, Register: {register_response.status_code}")
    except Exception as e:
        print_test_result("Functional equivalence test", False, f"Exception: {str(e)}")

    # Test 5: Test with invalid data
    print("5. Testing error handling with invalid data...")
    try:
        invalid_data = {
            "email": "invalid-email",
            "password": "123",  # too short
            "first_name": "",
            "last_name": ""
        }
        
        response = requests.post(f"{BACKEND_URL}/auth/signup", json=invalid_data)
        
        if response.status_code in [400, 422]:  # Bad request or validation error
            print_test_result("Error handling test", True, 
                f"Properly rejected invalid data with status {response.status_code}")
        else:
            print_test_result("Error handling test", False, 
                f"Unexpected response to invalid data: {response.status_code}")
    except Exception as e:
        print_test_result("Error handling test", False, f"Exception: {str(e)}")

    print("🏁 AUTHENTICATION TESTING COMPLETED")
    print("=" * 50)

if __name__ == "__main__":
    test_auth_endpoints()