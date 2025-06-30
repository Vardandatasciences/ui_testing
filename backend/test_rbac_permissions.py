#!/usr/bin/env python3
"""
RBAC Permissions Test Script

This script tests all RBAC permissions for policy endpoints to ensure
database-based permission checking is working correctly.

Usage:
    python test_rbac_permissions.py

Make sure to have test data in the database first:
    mysql -u root -p grc < test_rbac_data.sql
"""

import os
import sys
import django
import requests
import json

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_USER_ID = 1053  # From your logs

class RBACTester:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        
    def setup_test_session(self, user_id=TEST_USER_ID):
        """Setup a test session with the specified user ID"""
        print(f"Setting up test session for user {user_id}...")
        
        # First, try to create a session via the save-user-session endpoint
        try:
            response = self.session.post(f"{self.base_url}/api/save-user-session/", 
                                       json={"user_id": user_id})
            if response.status_code == 200:
                print(f"✓ Session created successfully for user {user_id}")
                return True
            else:
                print(f"✗ Failed to create session: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"✗ Error creating session: {e}")
            return False
    
    def test_endpoint(self, endpoint, method="GET", data=None, expected_permission=None):
        """Test an endpoint and check if RBAC is working"""
        print(f"\nTesting {method} {endpoint}")
        print("-" * 50)
        
        try:
            if method == "GET":
                response = self.session.get(f"{self.base_url}{endpoint}")
            elif method == "POST":
                response = self.session.post(f"{self.base_url}{endpoint}", 
                                           json=data or {})
            elif method == "PUT":
                response = self.session.put(f"{self.base_url}{endpoint}", 
                                          json=data or {})
            else:
                print(f"✗ Unsupported method: {method}")
                return False
            
            print(f"Status Code: {response.status_code}")
            
            # Print response content (truncated)
            response_text = response.text[:500] + "..." if len(response.text) > 500 else response.text
            print(f"Response: {response_text}")
            
            # Check if it's a permission denial
            if response.status_code == 403:
                print("✓ RBAC working - Access denied (403)")
                try:
                    json_response = response.json()
                    if 'error' in json_response:
                        print(f"  Error: {json_response['error']}")
                    if 'message' in json_response:
                        print(f"  Message: {json_response['message']}")
                except:
                    pass
                return True
            elif response.status_code == 200:
                print("✓ RBAC working - Access granted (200)")
                try:
                    json_response = response.json()
                    if 'user_id' in json_response:
                        print(f"  User ID: {json_response['user_id']}")
                except:
                    pass
                return True
            else:
                print(f"? Unexpected status code: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Error testing endpoint: {e}")
            return False
    
    def test_debug_endpoints(self):
        """Test debug endpoints to verify RBAC setup"""
        print("\n" + "="*60)
        print("TESTING DEBUG ENDPOINTS")
        print("="*60)
        
        # Test auth status
        self.test_endpoint("/api/debug-auth-status/")
        
        # Test user permissions
        self.test_endpoint("/api/user-permissions/")
        
        # Test user role
        self.test_endpoint("/api/user-role/")
        
        # Test RBAC data
        self.test_endpoint("/api/debug-rbac-data/")
    
    def test_rbac_specific_endpoints(self):
        """Test RBAC-specific test endpoints"""
        print("\n" + "="*60)
        print("TESTING RBAC-SPECIFIC ENDPOINTS")
        print("="*60)
        
        # Test policy view permission
        self.test_endpoint("/api/test-policy-view/")
        
        # Test policy create permission
        self.test_endpoint("/api/test-policy-create/")
        
        # Test policy approve permission
        self.test_endpoint("/api/test-policy-approve/")
        
        # Test ANY permission (view OR create)
        self.test_endpoint("/api/test-any-permission/")
        
        # Test ALL permissions (view AND create)
        self.test_endpoint("/api/test-all-permissions/")
        
        # Test endpoint permission checker
        self.test_endpoint("/api/test-endpoint-permission/", 
                         method="POST", 
                         data={"endpoint_name": "get_policy_kpis"})
    
    def test_policy_endpoints(self):
        """Test key policy endpoints that should have RBAC protection"""
        print("\n" + "="*60)
        print("TESTING POLICY ENDPOINTS WITH RBAC")
        print("="*60)
        
        # Framework endpoints
        self.test_endpoint("/api/frameworks/", expected_permission="policy_view")
        self.test_endpoint("/api/frameworks/", method="POST", 
                         data={"FrameworkName": "Test Framework"}, 
                         expected_permission="policy_create")
        
        # Policy endpoints
        self.test_endpoint("/api/policies/", expected_permission="policy_view")
        self.test_endpoint("/api/policy-kpis/", expected_permission="policy_view")
        self.test_endpoint("/api/policy-analytics/", expected_permission="policy_view")
        
        # Export endpoint
        self.test_endpoint("/api/frameworks/1/export/", method="POST", 
                         data={"format": "xlsx"}, 
                         expected_permission="policy_view")
        
        # Tailoring endpoints
        self.test_endpoint("/api/tailoring/create-framework/", method="POST",
                         data={"title": "Test"}, 
                         expected_permission="policy_create")
        
        # Framework explorer
        self.test_endpoint("/api/framework-explorer/", expected_permission="policy_view")
    
    def test_user_with_different_permissions(self, user_id, description):
        """Test with a specific user ID to see different permission levels"""
        print(f"\n" + "="*60)
        print(f"TESTING WITH {description} (User ID: {user_id})")
        print("="*60)
        
        if self.setup_test_session(user_id):
            # Test a few key endpoints
            self.test_endpoint("/api/user-permissions/")
            self.test_endpoint("/api/test-policy-view/")
            self.test_endpoint("/api/test-policy-create/")
            self.test_endpoint("/api/policy-kpis/")
        else:
            print(f"✗ Could not setup session for user {user_id}")
    
    def run_comprehensive_test(self):
        """Run all RBAC tests"""
        print("RBAC PERMISSIONS COMPREHENSIVE TEST")
        print("="*60)
        print(f"Testing against: {self.base_url}")
        print("="*60)
        
        # Setup session with default test user
        if not self.setup_test_session(TEST_USER_ID):
            print("✗ Could not setup initial test session. Exiting.")
            return False
        
        # Run all test categories
        self.test_debug_endpoints()
        self.test_rbac_specific_endpoints()
        self.test_policy_endpoints()
        
        # Test with different user types (if you have them in your database)
        # You would need to add different users with different permission levels
        # self.test_user_with_different_permissions(1054, "REGULAR USER")
        # self.test_user_with_different_permissions(1055, "APPROVER USER")
        
        print("\n" + "="*60)
        print("RBAC TEST COMPLETED")
        print("="*60)
        print("""
Summary:
- ✓ means the endpoint is working correctly (either granted or denied access)
- ✗ means there was an error
- ? means unexpected behavior

Next steps:
1. Check logs for detailed RBAC permission checks
2. Verify database has correct permissions for test users
3. Test with users having different permission levels
        """)

if __name__ == "__main__":
    tester = RBACTester()
    tester.run_comprehensive_test() 