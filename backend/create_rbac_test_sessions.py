#!/usr/bin/env python
"""
RBAC Test Session Creator

This script creates Django sessions for all RBAC test users to facilitate testing
without requiring complex authentication setup.

Usage:
    python create_rbac_test_sessions.py
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.sessions.backends.db import SessionStore
from grc.models import Users, RBAC
import json
from datetime import datetime

def create_test_sessions():
    """Create test sessions for all RBAC test users"""
    
    # Test user definitions
    test_users = {
        100: {'name': 'policy_admin', 'role': 'Administrator'},
        101: {'name': 'policy_manager', 'role': 'Manager'},
        102: {'name': 'policy_creator', 'role': 'Creator'},
        103: {'name': 'policy_reviewer', 'role': 'Reviewer'},
        104: {'name': 'policy_viewer', 'role': 'Viewer'},
        105: {'name': 'framework_manager', 'role': 'Framework Manager'},
        106: {'name': 'analytics_user', 'role': 'Analytics Specialist'},
        107: {'name': 'dept_limited', 'role': 'Department User'},
        108: {'name': 'entity_limited', 'role': 'Regional User'},
        109: {'name': 'no_permissions', 'role': 'Guest'},
        110: {'name': 'mixed_permissions', 'role': 'Mixed Role'}
    }
    
    sessions = {}
    created_sessions = []
    
    print("🔧 Creating RBAC Test Sessions")
    print("=" * 50)
    
    for user_id, user_info in test_users.items():
        try:
            # Check if user exists in database
            user_exists = Users.objects.filter(UserId=user_id).exists()
            rbac_exists = RBAC.objects.filter(user_id=user_id, is_active=True).exists()
            
            if not user_exists:
                print(f"⚠️  User {user_id} ({user_info['name']}) not found in database")
                continue
                
            if not rbac_exists:
                print(f"⚠️  RBAC record for user {user_id} ({user_info['name']}) not found or inactive")
                continue
            
            # Create session
            session = SessionStore()
            session['user_id'] = user_id
            session.save()
            
            session_key = session.session_key
            sessions[user_info['name']] = session_key
            
            created_sessions.append({
                'user_id': user_id,
                'username': user_info['name'],
                'role': user_info['role'],
                'session_key': session_key
            })
            
            print(f"✅ {user_info['name']} (ID: {user_id}): {session_key}")
            
        except Exception as e:
            print(f"❌ Error creating session for user {user_id}: {str(e)}")
    
    # Save sessions to file for reference
    session_file = project_root / 'rbac_test_sessions.json'
    with open(session_file, 'w') as f:
        json.dump({
            'created_at': datetime.now().isoformat(),
            'sessions': sessions,
            'detailed_sessions': created_sessions
        }, f, indent=2)
    
    print("\n" + "=" * 50)
    print(f"📁 Sessions saved to: {session_file}")
    print(f"✨ Successfully created {len(created_sessions)} test sessions")
    
    return sessions, created_sessions

def print_usage_instructions(sessions, created_sessions):
    """Print detailed usage instructions"""
    
    print("\n🚀 How to Use These Sessions")
    print("=" * 50)
    
    print("\n1. Browser Testing:")
    print("   - Open browser Developer Tools (F12)")
    print("   - Go to Application/Storage → Cookies")
    print("   - Add/Edit cookie: name='grc_sessionid', value='<session_key>'")
    print("   - Set domain to your application domain")
    print("   - Navigate to your GRC application")
    
    print("\n2. cURL Testing:")
    for session in created_sessions[:3]:  # Show first 3 examples
        print(f"   # Test as {session['role']} ({session['username']})")
        print(f"   curl -H \"Cookie: grc_sessionid={session['session_key']}\" \\")
        print(f"        http://localhost:8000/api/frameworks/")
        print()
    
    print("\n3. Quick Test Commands:")
    print("   # Test basic access")
    if 'policy_admin' in sessions:
        print(f"   export ADMIN_SESSION='{sessions['policy_admin']}'")
    if 'policy_viewer' in sessions:
        print(f"   export VIEWER_SESSION='{sessions['policy_viewer']}'")
    if 'no_permissions' in sessions:
        print(f"   export NO_PERM_SESSION='{sessions['no_permissions']}'")
    
    print("\n   # Test with different users")
    print("   curl -H \"Cookie: grc_sessionid=$ADMIN_SESSION\" http://localhost:8000/api/frameworks/")
    print("   curl -H \"Cookie: grc_sessionid=$VIEWER_SESSION\" http://localhost:8000/api/frameworks/")
    print("   curl -H \"Cookie: grc_sessionid=$NO_PERM_SESSION\" http://localhost:8000/api/frameworks/")

def verify_rbac_data():
    """Verify RBAC test data exists"""
    
    print("\n🔍 Verifying RBAC Test Data")
    print("=" * 50)
    
    # Check users
    test_user_count = Users.objects.filter(UserId__gte=100, UserId__lte=110).count()
    print(f"Test users found: {test_user_count}/11")
    
    # Check RBAC records
    rbac_count = RBAC.objects.filter(user_id__gte=100, user_id__lte=110).count()
    print(f"RBAC records found: {rbac_count}/11")
    
    # Check active RBAC records
    active_rbac_count = RBAC.objects.filter(
        user_id__gte=100, 
        user_id__lte=110, 
        is_active=True
    ).count()
    print(f"Active RBAC records: {active_rbac_count}/11")
    
    if test_user_count < 11 or rbac_count < 11:
        print("\n⚠️  Missing test data! Please run:")
        print("   mysql -u root -p grc < test_rbac_comprehensive_data.sql")
        return False
    
    print("✅ RBAC test data verification passed")
    return True

def show_permission_summary():
    """Show summary of user permissions"""
    
    print("\n📊 User Permission Summary")
    print("=" * 80)
    print(f"{'User ID':<8} {'Username':<18} {'Role':<18} {'Policy Perms':<12} {'Active':<8}")
    print("-" * 80)
    
    rbac_records = RBAC.objects.filter(
        user_id__gte=100, 
        user_id__lte=110
    ).order_by('user_id')
    
    for rbac in rbac_records:
        # Build permission string
        perms = []
        if rbac.policy_create: perms.append('C')
        if rbac.policy_view: perms.append('V')
        if rbac.policy_edit: perms.append('E')
        if rbac.policy_approve: perms.append('A')
        if rbac.policy_delete: perms.append('D')
        if rbac.policy_assign: perms.append('+')
        
        perm_str = ''.join(perms) if perms else 'None'
        
        try:
            user = Users.objects.get(UserId=rbac.user_id)
            username = user.UserName
        except Users.DoesNotExist:
            username = 'NOT_FOUND'
        
        print(f"{rbac.user_id:<8} {username:<18} {rbac.role:<18} {perm_str:<12} {rbac.is_active}")

def main():
    """Main function"""
    
    print("🎯 RBAC Test Session Creator")
    print("This script creates Django sessions for testing RBAC permissions")
    print("=" * 60)
    
    # Verify test data exists
    if not verify_rbac_data():
        return
    
    # Show permission summary
    show_permission_summary()
    
    # Create sessions
    sessions, created_sessions = create_test_sessions()
    
    # Print usage instructions
    print_usage_instructions(sessions, created_sessions)
    
    # Print additional testing info
    print("\n📋 Testing Checklist")
    print("=" * 50)
    print("1. [ ] Framework CRUD operations")
    print("2. [ ] Policy CRUD operations")
    print("3. [ ] Approval workflow endpoints")
    print("4. [ ] Analytics and KPI endpoints")
    print("5. [ ] Department/entity restrictions")
    print("6. [ ] Permission denial responses")
    print("7. [ ] Version control operations")
    print("8. [ ] Export/import functionality")
    
    print("\n🔗 Useful URLs to Test:")
    print("- http://localhost:8000/api/frameworks/")
    print("- http://localhost:8000/api/policies/")
    print("- http://localhost:8000/api/policy-analytics/")
    print("- http://localhost:8000/api/policy-kpis/")
    print("- http://localhost:8000/api/policy-dashboard/")
    print("- http://localhost:8000/api/policy-approvals/reviewer/")

if __name__ == "__main__":
    main() 