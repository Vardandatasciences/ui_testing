#!/usr/bin/env python3

import requests
import json

# Test the debug endpoint
policy_id = 1283  # The policy ID from the error logs
base_url = "http://localhost:8000"

print("Testing Policy Status Debug Endpoint...")
print(f"Policy ID: {policy_id}")

# Test 1: Debug endpoint
debug_url = f"{base_url}/api/policies/{policy_id}/test-debug/"
debug_data = {
    "reason": "test reason",
    "ReviewerId": 2,
    "cascadeSubpolicies": True
}

print(f"\n1. Testing debug endpoint: {debug_url}")
try:
    response = requests.post(debug_url, json=debug_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Debug endpoint error: {str(e)}")

# Test 2: Actual toggle endpoint  
toggle_url = f"{base_url}/api/policies/{policy_id}/toggle-status/"
print(f"\n2. Testing actual toggle endpoint: {toggle_url}")
try:
    response = requests.post(toggle_url, json=debug_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Toggle endpoint error: {str(e)}")

print("\n=== Test completed ===")
print("Check the Django console for detailed debug logs!") 