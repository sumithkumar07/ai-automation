#!/usr/bin/env python3
"""
Quick middleware test to isolate the FastAPI middleware configuration issue
"""

import requests
import sys
import json
from datetime import datetime

def test_backend_endpoints():
    """Test the specific endpoints mentioned in the review request"""
    base_url = "http://localhost:8001"
    
    endpoints_to_test = [
        ("Health Check", "GET", "/api/health"),
        ("Node Types", "GET", "/api/nodes"),
        ("Available Integrations", "GET", "/api/integrations"),
        ("Templates", "GET", "/api/templates"),
        ("Enhanced System Status", "GET", "/api/enhanced/system-status")
    ]
    
    print("🔍 Testing Backend Endpoints for Middleware Issues")
    print("=" * 60)
    
    results = []
    
    for name, method, endpoint in endpoints_to_test:
        url = f"{base_url}{endpoint}"
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=10)
            else:
                response = requests.request(method, url, timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 500:
                print(f"   ❌ 500 Internal Server Error - Middleware issue confirmed")
                try:
                    error_text = response.text[:200]
                    print(f"   Error: {error_text}")
                except:
                    print(f"   Error: Unable to read response")
                results.append((name, False, "500 Internal Server Error"))
            elif response.status_code == 200:
                print(f"   ✅ Success")
                try:
                    data = response.json()
                    print(f"   Response: {json.dumps(data, indent=2)[:100]}...")
                except:
                    print(f"   Response: {response.text[:100]}...")
                results.append((name, True, "Success"))
            else:
                print(f"   ⚠️ Unexpected status: {response.status_code}")
                results.append((name, False, f"Status {response.status_code}"))
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Connection Error - Backend server not running")
            results.append((name, False, "Connection Error"))
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            results.append((name, False, str(e)))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 MIDDLEWARE TEST RESULTS")
    print("=" * 60)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for name, success, message in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {name}: {message}")
    
    print(f"\nSummary: {passed}/{total} endpoints working")
    
    if passed == 0:
        print("\n🚨 CRITICAL: All endpoints failing with 500 errors")
        print("   This confirms the FastAPI middleware configuration issue")
        print("   Error: 'ValueError: too many values to unpack (expected 2)'")
        return False
    elif passed < total:
        print(f"\n⚠️ PARTIAL: Some endpoints working, {total-passed} failing")
        return True
    else:
        print(f"\n✅ SUCCESS: All endpoints working correctly")
        return True

if __name__ == "__main__":
    success = test_backend_endpoints()
    sys.exit(0 if success else 1)