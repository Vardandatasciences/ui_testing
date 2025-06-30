#!/usr/bin/env python
"""
RBAC Endpoint Testing Script

This script automatically tests all policy module endpoints with different user permissions
to validate the RBAC implementation.

Usage:
    python test_rbac_endpoints.py
"""

import requests
import json
import sys
import time
from datetime import datetime
from pathlib import Path

class RBACEndpointTester:
    """Comprehensive RBAC endpoint testing class"""
    
    def __init__(self, base_url='http://localhost:8000'):
        self.base_url = base_url
        self.sessions = {}
        self.results = {}
        self.load_sessions()
        
    def load_sessions(self):
        """Load test sessions from file"""
        session_file = Path(__file__).parent / 'rbac_test_sessions.json'
        
        if not session_file.exists():
            print("❌ Session file not found. Please run create_rbac_test_sessions.py first")
            sys.exit(1)
        
        with open(session_file, 'r') as f:
            data = json.load(f)
            self.sessions = data.get('sessions', {})
        
        if not self.sessions:
            print("❌ No sessions found. Please run create_rbac_test_sessions.py first")
            sys.exit(1)
        
        print(f"✅ Loaded {len(self.sessions)} test sessions")
    
    def make_request(self, session_key, endpoint, method='GET', data=None):
        """Make HTTP request with session cookie"""
        cookies = {'grc_sessionid': session_key}
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, cookies=cookies, timeout=10)
            elif method == 'POST':
                response = requests.post(url, cookies=cookies, json=data, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, cookies=cookies, json=data, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, cookies=cookies, timeout=10)
            else:
                return None, "Unsupported method"
            
            return response.status_code, response.text[:200] if response.text else ""
        
        except requests.exceptions.ConnectionError:
            return None, "Connection refused - is the Django server running?"
        except requests.exceptions.Timeout:
            return None, "Request timeout"
        except Exception as e:
            return None, str(e)
    
    def define_test_cases(self):
        """Define comprehensive test cases"""
        return [
            # Framework endpoints
            {
                'name': 'Framework List (GET)',
                'endpoint': '/api/frameworks/',
                'method': 'GET',
                'expected_access': {
                    'policy_admin': 200,
                    'policy_manager': 200,
                    'policy_creator': 200,
                    'policy_reviewer': 200,
                    'policy_viewer': 200,
                    'framework_manager': 200,
                    'analytics_user': 200,
                    'dept_limited': 200,
                    'entity_limited': 200,
                    'no_permissions': 403,
                    'mixed_permissions': 200
                }
            },
            {
                'name': 'Framework Create (POST)',
                'endpoint': '/api/frameworks/',
                'method': 'POST',
                'data': {'FrameworkName': 'Test Framework', 'FrameworkDescription': 'Test'},
                'expected_access': {
                    'policy_admin': 201,
                    'policy_manager': 201,
                    'policy_creator': 201,
                    'policy_reviewer': 403,
                    'policy_viewer': 403,
                    'framework_manager': 201,
                    'analytics_user': 403,
                    'dept_limited': 201,
                    'entity_limited': 403,
                    'no_permissions': 403,
                    'mixed_permissions': 201
                }
            },
            
            # Policy endpoints
            {
                'name': 'Policy List (GET)',
                'endpoint': '/api/policies/',
                'method': 'GET',
                'expected_access': {
                    'policy_admin': 200,
                    'policy_manager': 200,
                    'policy_creator': 200,
                    'policy_reviewer': 200,
                    'policy_viewer': 200,
                    'framework_manager': 200,
                    'analytics_user': 200,
                    'dept_limited': 200,
                    'entity_limited': 200,
                    'no_permissions': 403,
                    'mixed_permissions': 200
                }
            },
            
            # Analytics endpoints
            {
                'name': 'Policy Analytics (GET)',
                'endpoint': '/api/policy-analytics/',
                'method': 'GET',
                'expected_access': {
                    'policy_admin': 200,
                    'policy_manager': 200,
                    'policy_creator': 200,
                    'policy_reviewer': 200,
                    'policy_viewer': 403,  # Viewer cannot access analytics
                    'framework_manager': 200,
                    'analytics_user': 200,
                    'dept_limited': 200,
                    'entity_limited': 200,
                    'no_permissions': 403,
                    'mixed_permissions': 200
                }
            },
            {
                'name': 'Policy KPIs (GET)',
                'endpoint': '/api/policy-kpis/',
                'method': 'GET',
                'expected_access': {
                    'policy_admin': 200,
                    'policy_manager': 200,
                    'policy_creator': 200,
                    'policy_reviewer': 200,
                    'policy_viewer': 403,  # Viewer cannot access KPIs
                    'framework_manager': 200,
                    'analytics_user': 200,
                    'dept_limited': 200,
                    'entity_limited': 200,
                    'no_permissions': 403,
                    'mixed_permissions': 200
                }
            },
            {
                'name': 'Policy Dashboard (GET)',
                'endpoint': '/api/policy-dashboard/',
                'method': 'GET',
                'expected_access': {
                    'policy_admin': 200,
                    'policy_manager': 200,
                    'policy_creator': 200,
                    'policy_reviewer': 200,
                    'policy_viewer': 200,  # Viewer can access dashboard
                    'framework_manager': 200,
                    'analytics_user': 200,
                    'dept_limited': 200,
                    'entity_limited': 200,
                    'no_permissions': 403,
                    'mixed_permissions': 200
                }
            },
            
            # Approval workflow endpoints
            {
                'name': 'Policy Approvals for Reviewer (GET)',
                'endpoint': '/api/policy-approvals/reviewer/',
                'method': 'GET',
                'expected_access': {
                    'policy_admin': 200,
                    'policy_manager': 200,
                    'policy_creator': 403,  # Creator cannot access approval workflow
                    'policy_reviewer': 200,
                    'policy_viewer': 403,
                    'framework_manager': 200,
                    'analytics_user': 403,
                    'dept_limited': 403,
                    'entity_limited': 403,
                    'no_permissions': 403,
                    'mixed_permissions': 200
                }
            },
            
            # User and utility endpoints
            {
                'name': 'Users List (GET)',
                'endpoint': '/api/users/',
                'method': 'GET',
                'expected_access': {
                    'policy_admin': 200,
                    'policy_manager': 200,
                    'policy_creator': 200,
                    'policy_reviewer': 200,
                    'policy_viewer': 200,
                    'framework_manager': 200,
                    'analytics_user': 200,
                    'dept_limited': 200,
                    'entity_limited': 200,
                    'no_permissions': 403,
                    'mixed_permissions': 200
                }
            },
            
            # Framework explorer
            {
                'name': 'Framework Explorer (GET)',
                'endpoint': '/api/framework-explorer/',
                'method': 'GET',
                'expected_access': {
                    'policy_admin': 200,
                    'policy_manager': 200,
                    'policy_creator': 200,
                    'policy_reviewer': 200,
                    'policy_viewer': 200,
                    'framework_manager': 200,
                    'analytics_user': 200,
                    'dept_limited': 200,
                    'entity_limited': 200,
                    'no_permissions': 403,
                    'mixed_permissions': 200
                }
            }
        ]
    
    def run_tests(self):
        """Run all test cases"""
        test_cases = self.define_test_cases()
        total_tests = len(test_cases) * len(self.sessions)
        current_test = 0
        
        print(f"\n🧪 Running RBAC Endpoint Tests")
        print(f"Total test cases: {len(test_cases)}")
        print(f"Total users: {len(self.sessions)}")
        print(f"Total tests: {total_tests}")
        print("=" * 80)
        
        for test_case in test_cases:
            print(f"\n🔍 Testing: {test_case['name']}")
            print(f"   Endpoint: {test_case['method']} {test_case['endpoint']}")
            
            test_results = {}
            
            for user_type, session_key in self.sessions.items():
                current_test += 1
                
                # Make request
                status_code, response = self.make_request(
                    session_key,
                    test_case['endpoint'],
                    test_case['method'],
                    test_case.get('data')
                )
                
                # Check expected result
                expected = test_case['expected_access'].get(user_type, 'UNKNOWN')
                
                if status_code is None:
                    result = f"❌ ERROR: {response}"
                elif status_code == expected:
                    result = f"✅ PASS ({status_code})"
                else:
                    result = f"❌ FAIL (got {status_code}, expected {expected})"
                
                test_results[user_type] = {
                    'actual': status_code,
                    'expected': expected,
                    'status': 'PASS' if status_code == expected else 'FAIL',
                    'response': response[:100] if response else ""
                }
                
                print(f"   {user_type:<20} {result}")
                
                # Small delay to avoid overwhelming the server
                time.sleep(0.1)
            
            # Store results
            self.results[test_case['name']] = test_results
        
        print(f"\n✨ Completed {current_test} tests")
    
    def generate_report(self):
        """Generate detailed test report"""
        
        # Calculate summary statistics
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for test_name, test_results in self.results.items():
            for user_type, result in test_results.items():
                total_tests += 1
                if result['status'] == 'PASS':
                    passed_tests += 1
                else:
                    failed_tests += 1
        
        # Generate report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = Path(__file__).parent / f'rbac_test_report_{timestamp}.json'
        
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'success_rate': f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%"
            },
            'test_results': self.results,
            'users_tested': list(self.sessions.keys()),
            'base_url': self.base_url
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📊 Test Summary")
        print("=" * 50)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {report_data['summary']['success_rate']}")
        print(f"Report saved to: {report_file}")
        
        # Show failed tests
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for test_name, test_results in self.results.items():
                for user_type, result in test_results.items():
                    if result['status'] == 'FAIL':
                        print(f"   {test_name} - {user_type}: got {result['actual']}, expected {result['expected']}")
        
        return report_data
    
    def print_permission_matrix(self):
        """Print a permission matrix for easy viewing"""
        
        print(f"\n📋 Permission Matrix")
        print("=" * 120)
        
        # Header
        users = list(self.sessions.keys())
        header = f"{'Test Case':<40}"
        for user in users:
            header += f"{user:<12}"
        print(header)
        print("-" * 120)
        
        # Rows
        for test_name, test_results in self.results.items():
            row = f"{test_name:<40}"
            for user in users:
                result = test_results.get(user, {})
                status = result.get('actual', 'N/A')
                if result.get('status') == 'PASS':
                    symbol = f"✅{status}"
                elif result.get('status') == 'FAIL':
                    symbol = f"❌{status}"
                else:
                    symbol = f"❓{status}"
                row += f"{symbol:<12}"
            print(row)

def main():
    """Main function"""
    
    print("🎯 RBAC Endpoint Testing Script")
    print("This script tests all policy module endpoints with different user permissions")
    print("=" * 80)
    
    # Check if Django server is running
    try:
        response = requests.get('http://localhost:8000', timeout=5)
        print("✅ Django server is running")
    except requests.exceptions.ConnectionError:
        print("❌ Django server is not running. Please start it with:")
        print("   cd backend && python manage.py runserver")
        sys.exit(1)
    except Exception as e:
        print(f"⚠️  Cannot verify Django server status: {e}")
    
    # Initialize tester
    tester = RBACEndpointTester()
    
    # Run tests
    try:
        tester.run_tests()
        report = tester.generate_report()
        tester.print_permission_matrix()
        
        print(f"\n🎉 Testing Complete!")
        print(f"Success Rate: {report['summary']['success_rate']}")
        
        if report['summary']['failed'] == 0:
            print("🎊 All tests passed! RBAC implementation is working correctly.")
        else:
            print(f"⚠️  {report['summary']['failed']} tests failed. Please review the results.")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
