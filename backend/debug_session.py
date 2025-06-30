#!/usr/bin/env python3
"""
Session Debug Script for RBAC
This script helps debug session issues with RBAC authentication.
"""

import os
import sys
import django

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.sessions.models import Session
from grc.models import RBAC
from datetime import datetime, timedelta


def check_sessions():
    """Check all active sessions"""
    print("🔍 CHECKING ALL ACTIVE SESSIONS")
    print("="*50)
    
    sessions = Session.objects.filter(expire_date__gt=datetime.now())
    print(f"Found {sessions.count()} active sessions")
    
    for session in sessions:
        print(f"\nSession: {session.session_key}")
        print(f"Expires: {session.expire_date}")
        
        try:
            session_data = session.get_decoded()
            print(f"Data: {session_data}")
            
            if 'user_id' in session_data:
                user_id = session_data['user_id']
                print(f"✅ Contains user_id: {user_id}")
                
                # Check if user has RBAC record
                rbac = RBAC.objects.filter(user_id=user_id, is_active=True).first()
                if rbac:
                    print(f"✅ RBAC record found: {rbac.email} ({rbac.role})")
                    print(f"   Policy view permission: {rbac.policy_view}")
                else:
                    print(f"❌ No RBAC record found for user {user_id}")
            else:
                print("❌ No user_id in session")
                
        except Exception as e:
            print(f"❌ Error decoding session: {e}")


def create_test_session(user_id=3):
    """Create a test session for debugging"""
    print(f"\n🛠 CREATING TEST SESSION FOR USER {user_id}")
    print("="*50)
    
    # Check if user exists in RBAC
    rbac = RBAC.objects.filter(user_id=user_id, is_active=True).first()
    if not rbac:
        print(f"❌ No RBAC record found for user {user_id}")
        print("Run: mysql -u root -p grc < test_rbac_data.sql")
        return None
    
    print(f"✅ User found: {rbac.email} ({rbac.role})")
    print(f"   Policy view permission: {rbac.policy_view}")
    
    # Create session
    from django.contrib.sessions.backends.db import SessionStore
    
    session_store = SessionStore()
    session_store['user_id'] = user_id
    session_store['is_authenticated'] = True
    session_store['debug_session'] = True
    session_store['created_at'] = datetime.now().isoformat()
    session_store['user_email'] = rbac.email
    session_store['user_role'] = rbac.role
    session_store.save()
    
    session_key = session_store.session_key
    
    print(f"✅ Created session: {session_key}")
    print(f"   Expires: in 24 hours")
    
    return session_key


def test_api_call():
    """Simulate API call with session"""
    print(f"\n🔗 TESTING API CALL SIMULATION")
    print("="*50)
    
    # This is just for demonstration
    print("To test the API call:")
    print("1. Open browser dev tools (F12)")
    print("2. Go to Application > Cookies")
    print("3. Set cookie: grc_sessionid = <session_key_from_above>")
    print("4. Visit: http://localhost:8080/performance")
    print("5. Check Django console for detailed debug logs")


def check_rbac_data():
    """Check RBAC test data"""
    print(f"\n📋 CHECKING RBAC TEST DATA")
    print("="*50)
    
    test_users = RBAC.objects.filter(email__contains='test').order_by('user_id')
    
    if not test_users.exists():
        print("❌ No test users found!")
        print("Run: mysql -u root -p grc < test_rbac_data.sql")
        return
    
    print(f"Found {test_users.count()} test users:")
    
    for rbac in test_users:
        status = "✅ ACTIVE" if rbac.is_active else "❌ INACTIVE"
        policy_access = "✅ CAN ACCESS" if rbac.policy_view else "❌ CANNOT ACCESS"
        
        print(f"\nUser {rbac.user_id}: {rbac.email}")
        print(f"  Role: {rbac.role}")
        print(f"  Status: {status}")
        print(f"  Policy KPIs: {policy_access}")


def main():
    """Main debugging function"""
    print("🐛 RBAC SESSION DEBUGGING TOOL")
    print("="*50)
    
    # Check RBAC data first
    check_rbac_data()
    
    # Check existing sessions
    check_sessions()
    
    # Create test session
    session_key = create_test_session(user_id=3)  # Policy viewer
    
    if session_key:
        print(f"\n🎯 NEXT STEPS:")
        print(f"1. Copy this session key: {session_key}")
        print(f"2. Open browser and set cookie: grc_sessionid = {session_key}")
        print(f"3. Visit: http://localhost:8080/performance")
        print(f"4. Check Django console logs for detailed RBAC debug output")
        print(f"5. You should see user_id extracted and permission granted")
    
    # Test with different users
    print(f"\n🔄 OTHER TEST USERS:")
    print(f"User 1: Admin (should have access)")
    print(f"User 2: Policy Manager (should have access)")
    print(f"User 3: Policy Viewer (should have access)")
    print(f"User 4: Restricted User (should be denied)")
    print(f"User 5: Inactive User (should be denied)")


if __name__ == "__main__":
    main() 