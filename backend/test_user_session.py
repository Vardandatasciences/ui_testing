#!/usr/bin/env python
"""
Test script to verify user details and session functionality
"""

import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"

def test_user_details():
    """Test getting user details by ID"""
    print("=" * 60)
    print("TESTING USER DETAILS RETRIEVAL")
    print("=" * 60)
    
    # Test with different user IDs
    user_ids = [1, 1053, 1061, 1062]  # admin, admin.grc, auditor, manager
    
    for user_id in user_ids:
        print(f"\n🔍 Testing User ID: {user_id}")
        try:
            response = requests.get(f"{BASE_URL}/api/test-user-details/{user_id}/")
            
            if response.status_code == 200:
                data = response.json()
                user = data.get('user', {})
                print(f"✅ SUCCESS: {user.get('username')} ({user.get('email')})")
                print(f"   RBAC Role: {user.get('rbac_info', {}).get('role', 'No RBAC')}")
                print(f"   Department: {user.get('rbac_info', {}).get('department', 'No Department')}")
            else:
                print(f"❌ FAILED: Status {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")

def test_session_creation():
    """Test creating user session"""
    print("\n" + "=" * 60)
    print("TESTING SESSION CREATION")
    print("=" * 60)
    
    # Test creating sessions for different users
    user_ids = [1, 1053, 1061]  # admin, admin.grc, auditor
    
    for user_id in user_ids:
        print(f"\n🔧 Creating session for User ID: {user_id}")
        try:
            response = requests.post(f"{BASE_URL}/api/save-user-session/", 
                                   json={"user_id": user_id})
            
            if response.status_code == 200:
                data = response.json()
                user = data.get('user', {})
                session_data = data.get('session_data', {})
                print(f"✅ SESSION CREATED: {user.get('username')}")
                print(f"   Session Key: {user.get('session_key')}")
                print(f"   GRC User ID: {session_data.get('grc_user_id')}")
                print(f"   Session Data: {session_data}")
            else:
                print(f"❌ FAILED: Status {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")

def test_debug_auth_status():
    """Test debug auth status endpoint"""
    print("\n" + "=" * 60)
    print("TESTING DEBUG AUTH STATUS")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/debug-auth-status/")
        
        if response.status_code == 200:
            data = response.json()
            auth_status = data.get('auth_status', {})
            session_info = data.get('session_info', {})
            
            print(f"🔍 Authentication Status:")
            print(f"   Authenticated: {auth_status.get('user_is_authenticated')}")
            print(f"   User Type: {auth_status.get('user_type')}")
            print(f"   Django User ID: {auth_status.get('user_id_django')}")
            print(f"   Username: {auth_status.get('username')}")
            print(f"   RBAC User ID: {auth_status.get('rbac_user_id')}")
            
            print(f"\n🍪 Session Info:")
            print(f"   Has Session: {session_info.get('has_session')}")
            print(f"   Session Key: {session_info.get('session_key')}")
            print(f"   Session Data: {session_info.get('session_data')}")
            
        else:
            print(f"❌ FAILED: Status {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_login_and_session():
    """Test the full login flow"""
    print("\n" + "=" * 60)
    print("TESTING FULL LOGIN FLOW")
    print("=" * 60)
    
    # Test login
    login_data = {
        "username": "admin.grc",
        "password": "admin123"  # Correct password from database
    }
    
    print(f"🔑 Attempting login with: {login_data['username']}")
    
    try:
        # Create a session to maintain cookies
        session = requests.Session()
        
        # Login
        response = session.post(f"{BASE_URL}/api/login/", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ LOGIN SUCCESS: {data.get('message')}")
            user = data.get('user', {})
            print(f"   User ID: {user.get('id')}")
            print(f"   Username: {user.get('username')}")
            print(f"   Session Key: {user.get('session_key')}")
            
            # Now test protected endpoint with same session
            print(f"\n🔒 Testing protected endpoint with session...")
            protected_response = session.get(f"{BASE_URL}/api/debug-auth-status/")
            
            if protected_response.status_code == 200:
                auth_data = protected_response.json()
                auth_status = auth_data.get('auth_status', {})
                print(f"✅ PROTECTED ENDPOINT ACCESS:")
                print(f"   Authenticated: {auth_status.get('user_is_authenticated')}")
                print(f"   RBAC User ID: {auth_status.get('rbac_user_id')}")
                
                if auth_status.get('rbac_info'):
                    rbac_info = auth_status['rbac_info']
                    print(f"   Role: {rbac_info.get('role')}")
                    print(f"   Department: {rbac_info.get('department')}")
            else:
                print(f"❌ PROTECTED ENDPOINT FAILED: Status {protected_response.status_code}")
                
        else:
            print(f"❌ LOGIN FAILED: Status {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    print("🚀 Starting GRC User Session Tests")
    print("Make sure Django server is running on http://localhost:8000")
    
    test_user_details()
    test_session_creation() 
    test_debug_auth_status()
    test_login_and_session()
    
    print("\n" + "=" * 60)
    print("✅ Tests completed!")
    print("=" * 60) 