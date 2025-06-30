#!/usr/bin/env python3
"""
RBAC Testing Script for Policy Module
This script helps test different user sessions and RBAC permissions.

Usage:
1. First run the SQL script: mysql -u root -p grc < test_rbac_data.sql
2. Then run this script: python test_rbac_sessions.py
3. Follow the prompts to test different users
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
from grc.models import RBAC, Users
from grc.rbac.utils import RBACUtils
from datetime import datetime, timedelta
import json


class RBACTester:
    def __init__(self):
        self.test_users = [
            {
                'user_id': 1,
                'email': 'admin@test.com',
                'role': 'Administrator',
                'description': 'Full admin access - CAN access Policy KPIs',
                'expected_access': True
            },
            {
                'user_id': 2,
                'email': 'policy.manager@test.com',
                'role': 'Policy Manager',
                'description': 'Policy manager with view permissions - CAN access Policy KPIs',
                'expected_access': True
            },
            {
                'user_id': 3,
                'email': 'policy.viewer@test.com',
                'role': 'Policy Viewer',
                'description': 'Read-only policy access - CAN access Policy KPIs',
                'expected_access': True
            },
            {
                'user_id': 4,
                'email': 'restricted.user@test.com',
                'role': 'Basic User',
                'description': 'No policy permissions - CANNOT access Policy KPIs',
                'expected_access': False
            },
            {
                'user_id': 5,
                'email': 'inactive.user@test.com',
                'role': 'Inactive Manager',
                'description': 'Inactive user - CANNOT access Policy KPIs',
                'expected_access': False
            }
        ]

    def show_test_users(self):
        """Display all test users and their expected access levels"""
        print("\n" + "="*80)
        print("RBAC TEST USERS FOR POLICY MODULE")
        print("="*80)
        
        for i, user in enumerate(self.test_users, 1):
            access_status = "✅ CAN ACCESS" if user['expected_access'] else "❌ CANNOT ACCESS"
            print(f"\n{i}. {user['role']} (ID: {user['user_id']})")
            print(f"   Email: {user['email']}")
            print(f"   Description: {user['description']}")
            print(f"   Expected Access: {access_status}")

    def check_rbac_record(self, user_id):
        """Check RBAC permissions for a user"""
        try:
            rbac_record = RBAC.objects.get(user_id=user_id, is_active=True)
            
            print(f"\n📋 RBAC Record for User {user_id}:")
            print(f"   Email: {rbac_record.email}")
            print(f"   Role: {rbac_record.role}")
            print(f"   Department: {rbac_record.department}")
            print(f"   Entity: {rbac_record.entity}")
            print(f"   Is Active: {rbac_record.is_active}")
            
            print(f"\n🔐 Policy Permissions:")
            print(f"   policy_create: {rbac_record.policy_create}")
            print(f"   policy_view: {rbac_record.policy_view}")
            print(f"   policy_edit: {rbac_record.policy_edit}")
            print(f"   policy_approve: {rbac_record.policy_approve}")
            print(f"   policy_delete: {rbac_record.policy_delete}")
            print(f"   policy_assign: {rbac_record.policy_assign}")
            
            print(f"\n📊 Additional Permissions:")
            print(f"   can_view_reports: {rbac_record.can_view_reports}")
            print(f"   can_export_data: {rbac_record.can_export_data}")
            
            # Check if user can access Policy KPIs
            can_access_kpis = rbac_record.policy_view and rbac_record.is_active
            status = "✅ ALLOWED" if can_access_kpis else "❌ DENIED"
            print(f"\n🎯 Policy KPI Access: {status}")
            
            return rbac_record
        except RBAC.DoesNotExist:
            print(f"❌ No RBAC record found for user {user_id}")
            return None

    def create_test_session(self, user_id):
        """Create a test session for a specific user"""
        try:
            # Clear existing sessions for this user (optional)
            Session.objects.filter(session_data__contains=str(user_id)).delete()
            
            # Create new session
            session = Session()
            session.session_key = f"test_session_{user_id}_{int(datetime.now().timestamp())}"
            session.session_data = session.encode({
                'user_id': user_id,
                'is_authenticated': True,
                'test_session': True,
                'created_at': datetime.now().isoformat()
            })
            session.expire_date = datetime.now() + timedelta(hours=24)
            session.save()
            
            print(f"\n✅ Created test session for User {user_id}")
            print(f"   Session Key: {session.session_key}")
            print(f"   Expires: {session.expire_date}")
            
            return session.session_key
        except Exception as e:
            print(f"❌ Error creating session: {e}")
            return None

    def test_user_access(self, user_id):
        """Test RBAC access for a specific user"""
        print(f"\n{'='*60}")
        print(f"TESTING USER ACCESS - ID: {user_id}")
        print(f"{'='*60}")
        
        # Find user in test data
        user_info = next((u for u in self.test_users if u['user_id'] == user_id), None)
        if user_info:
            print(f"User: {user_info['role']} ({user_info['email']})")
            print(f"Expected: {'CAN access' if user_info['expected_access'] else 'CANNOT access'} Policy KPIs")
        
        # Check RBAC record
        rbac_record = self.check_rbac_record(user_id)
        
        if rbac_record:
            # Create test session
            session_key = self.create_test_session(user_id)
            
            # Test permission check
            has_permission = RBACUtils.has_policy_permission(user_id, 'view')
            print(f"\n🧪 RBACUtils.has_policy_permission({user_id}, 'view'): {has_permission}")
            
            # Simulate PolicyKPIPermission check
            can_access = rbac_record.policy_view and rbac_record.is_active
            print(f"🎯 Final Access Decision: {'ALLOWED' if can_access else 'DENIED'}")
            
            return session_key
        else:
            print("❌ Cannot test - no RBAC record found")
            return None

    def run_interactive_test(self):
        """Run interactive RBAC testing"""
        print("\n🚀 RBAC Policy Module Tester")
        print("This tool helps you test RBAC permissions for the Policy KPI page")
        
        while True:
            self.show_test_users()
            
            print(f"\n{'='*80}")
            print("OPTIONS:")
            print("1-5: Test specific user (enter user number)")
            print("A: Test all users automatically")
            print("S: Show current RBAC data")
            print("Q: Quit")
            print("="*80)
            
            choice = input("\nEnter your choice: ").strip().upper()
            
            if choice == 'Q':
                print("👋 Goodbye!")
                break
            elif choice == 'A':
                self.test_all_users()
            elif choice == 'S':
                self.show_rbac_data()
            elif choice.isdigit() and 1 <= int(choice) <= 5:
                user_index = int(choice) - 1
                user_id = self.test_users[user_index]['user_id']
                session_key = self.test_user_access(user_id)
                
                if session_key:
                    print(f"\n💡 TO TEST IN BROWSER:")
                    print(f"   1. Open browser developer tools")
                    print(f"   2. Go to Application > Cookies")
                    print(f"   3. Set cookie: grc_sessionid = {session_key}")
                    print(f"   4. Visit: http://localhost:8080/performance")
                    print(f"   5. Check browser console for RBAC debug messages")
                
                input("\nPress Enter to continue...")
            else:
                print("❌ Invalid choice. Please try again.")

    def test_all_users(self):
        """Test all users automatically"""
        print(f"\n{'='*60}")
        print("TESTING ALL USERS")
        print(f"{'='*60}")
        
        for user in self.test_users:
            print(f"\n--- Testing {user['role']} (ID: {user['user_id']}) ---")
            rbac_record = self.check_rbac_record(user['user_id'])
            
            if rbac_record:
                actual_access = rbac_record.policy_view and rbac_record.is_active
                expected_access = user['expected_access']
                
                if actual_access == expected_access:
                    print("✅ PASS - Access matches expectation")
                else:
                    print("❌ FAIL - Access does not match expectation")
                    print(f"   Expected: {expected_access}")
                    print(f"   Actual: {actual_access}")
            else:
                print("❌ FAIL - No RBAC record found")

    def show_rbac_data(self):
        """Show current RBAC data for all test users"""
        print(f"\n{'='*80}")
        print("CURRENT RBAC DATA")
        print(f"{'='*80}")
        
        rbac_records = RBAC.objects.filter(email__contains='test').order_by('user_id')
        
        if not rbac_records:
            print("❌ No test RBAC data found.")
            print("💡 Run the test_rbac_data.sql script first!")
            return
        
        for rbac in rbac_records:
            status = "✅ ACTIVE" if rbac.is_active else "❌ INACTIVE"
            kpi_access = "✅ CAN ACCESS" if (rbac.policy_view and rbac.is_active) else "❌ CANNOT ACCESS"
            
            print(f"\nUser ID: {rbac.user_id}")
            print(f"Email: {rbac.email}")
            print(f"Role: {rbac.role}")
            print(f"Status: {status}")
            print(f"Policy View: {rbac.policy_view}")
            print(f"KPI Access: {kpi_access}")


def main():
    """Main function to run the RBAC tester"""
    print("🔧 RBAC Policy Module Integration Tester")
    print("=========================================")
    
    # Check if RBAC table has test data
    test_count = RBAC.objects.filter(email__contains='test').count()
    if test_count == 0:
        print("❌ No test data found in RBAC table!")
        print("💡 Please run the test_rbac_data.sql script first:")
        print("   mysql -u root -p grc < test_rbac_data.sql")
        return
    else:
        print(f"✅ Found {test_count} test users in RBAC table")
    
    # Start interactive testing
    tester = RBACTester()
    tester.run_interactive_test()


if __name__ == "__main__":
    main() 