# Comprehensive RBAC Testing Guide for GRC Policy Module

## Overview

This guide provides step-by-step instructions for testing the comprehensive Role-Based Access Control (RBAC) system implemented for the GRC Policy Module.

## Setup Instructions

### 1. Load Test Data

```bash
# Navigate to backend directory
cd backend

# Load comprehensive test data
mysql -u root -p grc < test_rbac_comprehensive_data.sql
```

### 2. Verify Test Users Created

```sql
-- Check test users
SELECT UserId, UserName, email FROM users WHERE UserId BETWEEN 100 AND 110;

-- Check RBAC permissions
SELECT user_id, email, role, 
       policy_create, policy_view, policy_edit, policy_approve, policy_delete
FROM rbac WHERE user_id BETWEEN 100 AND 110;
```

## Test User Profiles

| User ID | Username | Role | Policy Permissions | Use Case |
|---------|----------|------|-------------------|----------|
| 100 | policy_admin | Administrator | All (CVEAD+) | Full access testing |
| 101 | policy_manager | Manager | CVEA+ (no Delete) | Manager workflow |
| 102 | policy_creator | Creator | CVE (no Approve/Delete) | Content creation |
| 103 | policy_reviewer | Reviewer | VA (View + Approve) | Approval workflow |
| 104 | policy_viewer | Viewer | V (View only) | Read-only access |
| 105 | framework_manager | Framework Manager | Framework operations | Framework testing |
| 106 | analytics_user | Analytics | View + Analytics | Dashboard/KPI testing |
| 107 | dept_limited | Department User | Limited dept access | Department restrictions |
| 108 | entity_limited | Regional User | Limited entity access | Entity restrictions |
| 109 | no_permissions | Guest | No policy permissions | Access denial testing |
| 110 | mixed_permissions | Mixed Role | Complex permissions | Edge case testing |

## Testing Methodology

### Session-Based Testing

Create test sessions for different users:

```python
# Python script to create test sessions
from django.contrib.sessions.backends.db import SessionStore

def create_test_session(user_id):
    session = SessionStore()
    session['user_id'] = user_id
    session.save()
    return session.session_key

# Create sessions for key test users
admin_session = create_test_session(100)  # Admin
viewer_session = create_test_session(104)  # Viewer
no_perm_session = create_test_session(109)  # No permissions

print(f"Admin session: {admin_session}")
print(f"Viewer session: {viewer_session}")
print(f"No permissions session: {no_perm_session}")
```

### Browser Testing

1. Open browser developer tools (F12)
2. Go to Application/Storage → Cookies
3. Set cookie: `grc_sessionid` = `your_session_key`
4. Test endpoints in the application

### API Testing with cURL

```bash
# Test with admin user
curl -H "Cookie: grc_sessionid=your_admin_session" \
     http://localhost:8000/api/frameworks/

# Test with no-permissions user (should fail)
curl -H "Cookie: grc_sessionid=your_no_perm_session" \
     http://localhost:8000/api/frameworks/
```

## Testing Matrix

### Framework Endpoints

| Endpoint | Admin (100) | Manager (101) | Creator (102) | Reviewer (103) | Viewer (104) | No-Perm (109) |
|----------|-------------|---------------|---------------|----------------|--------------|---------------|
| GET /api/frameworks/ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| POST /api/frameworks/ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| PUT /api/frameworks/{id}/ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| DELETE /api/frameworks/{id}/ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |

### Policy Endpoints

| Endpoint | Admin (100) | Manager (101) | Creator (102) | Reviewer (103) | Viewer (104) | No-Perm (109) |
|----------|-------------|---------------|---------------|----------------|--------------|---------------|
| GET /api/policies/ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| POST /api/policies/ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| PUT /api/policies/{id}/ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |

### Approval Workflow

| Endpoint | Admin (100) | Manager (101) | Creator (102) | Reviewer (103) | Viewer (104) |
|----------|-------------|---------------|---------------|----------------|--------------|
| PUT /api/policy-approvals/{id}/ | ✅ | ✅ | ❌ | ✅ | ❌ |
| GET /api/policy-approvals/reviewer/ | ✅ | ✅ | ❌ | ✅ | ❌ |
| POST /api/frameworks/{id}/submit-review/ | ✅ | ✅ | ❌ | ✅ | ❌ |

### Analytics & KPIs

| Endpoint | Admin (100) | Analytics (106) | Viewer (104) | No-Perm (109) |
|----------|-------------|-----------------|--------------|---------------|
| GET /api/policy-analytics/ | ✅ | ✅ | ❌ | ❌ |
| GET /api/policy-kpis/ | ✅ | ✅ | ❌ | ❌ |
| GET /api/policy-dashboard/ | ✅ | ✅ | ✅ | ❌ |

## Step-by-Step Testing Process

### Test 1: Basic Framework Operations

1. **Test Framework List (GET /api/frameworks/)**
   ```bash
   # Should succeed for users 100-108, fail for 109
   curl -H "Cookie: grc_sessionid=admin_session" http://localhost:8000/api/frameworks/
   curl -H "Cookie: grc_sessionid=viewer_session" http://localhost:8000/api/frameworks/
   curl -H "Cookie: grc_sessionid=no_perm_session" http://localhost:8000/api/frameworks/
   ```

2. **Test Framework Creation (POST /api/frameworks/)**
   ```bash
   # Should succeed for users 100-102, fail for others
   curl -X POST -H "Cookie: grc_sessionid=admin_session" \
        -H "Content-Type: application/json" \
        -d '{"FrameworkName": "Test Framework", "FrameworkDescription": "Test"}' \
        http://localhost:8000/api/frameworks/
   ```

### Test 2: Policy Operations

1. **Test Policy Viewing**
   - Verify users 100-108 can view policies
   - Verify user 109 gets 403 Forbidden

2. **Test Policy Creation**
   - Verify users 100-102 can create policies
   - Verify users 103-109 get 403 Forbidden

### Test 3: Approval Workflow

1. **Test Policy Approval**
   - Verify users 100, 101, 103 can approve policies
   - Verify users 102, 104-109 get 403 Forbidden

2. **Test Reviewer Dashboard**
   - Verify users 100, 101, 103 can access reviewer endpoints
   - Verify others get 403 Forbidden

### Test 4: Analytics & KPIs

1. **Test Analytics Access**
   - Verify users 100, 106 can access analytics
   - Verify others get 403 Forbidden

2. **Test KPI Dashboard**
   - Verify users 100, 106 can access KPIs
   - Verify user 104 (viewer) cannot access analytics

### Test 5: Department & Entity Restrictions

1. **Test Department Limitations (User 107)**
   - Should only access Policy department data
   - Should be denied access to other departments

2. **Test Entity Limitations (User 108)**
   - Should only access Europe entity data
   - Should be denied access to other entities

## Expected Results

### Success Cases (Status 200)

- **Admin (100)**: All endpoints should succeed
- **Manager (101)**: All except delete operations
- **Creator (102)**: Create, view, edit operations
- **Reviewer (103)**: View and approval operations
- **Viewer (104)**: Basic view operations only
- **Analytics (106)**: View and analytics operations

### Failure Cases (Status 403)

- **No Permissions (109)**: All policy endpoints should fail
- **Viewer (104)**: Create, edit, delete, approval operations should fail
- **Creator (102)**: Approval operations should fail

## Troubleshooting

### Common Issues

1. **"No user_id found in session"**
   - Check session middleware is enabled
   - Verify session cookie is set correctly

2. **"No RBAC record found for user"**
   - Run test data SQL script
   - Check user exists in rbac table

3. **Permission denied but should have access**
   - Check user's permission flags in rbac table
   - Verify is_active = 1

### Debug Queries

```sql
-- Check user permissions
SELECT user_id, email, role, policy_view, policy_create, policy_edit, policy_approve 
FROM rbac WHERE user_id = 104;

-- Check if user is active
SELECT user_id, email, is_active FROM rbac WHERE user_id = 104;
```

## Automated Testing Script

Create this Python script for automated testing:

```python
# test_rbac_automation.py
import requests
import json

# Session keys for test users
sessions = {
    'admin': 'your_admin_session_key',
    'viewer': 'your_viewer_session_key', 
    'no_perm': 'your_no_perm_session_key'
}

BASE_URL = 'http://localhost:8000'

def test_endpoint(user_type, endpoint, method='GET'):
    cookies = {'grc_sessionid': sessions[user_type]}
    url = f"{BASE_URL}{endpoint}"
    
    try:
        response = requests.get(url, cookies=cookies) if method == 'GET' else None
        return response.status_code
    except Exception as e:
        return f"Error: {e}"

# Test cases
test_cases = [
    ('/api/frameworks/', 'GET'),
    ('/api/policies/', 'GET'),
    ('/api/policy-analytics/', 'GET'),
]

# Run tests
for endpoint, method in test_cases:
    print(f"\nTesting {method} {endpoint}:")
    for user_type in sessions.keys():
        result = test_endpoint(user_type, endpoint, method)
        print(f"  {user_type}: {result}")
```

## Checklist

- [ ] Test data loaded successfully
- [ ] All 11 test users created with correct permissions
- [ ] Framework CRUD operations tested with different users
- [ ] Policy CRUD operations tested with different users
- [ ] Approval workflow tested with appropriate users
- [ ] Analytics endpoints tested with analytics user
- [ ] Permission denials working correctly
- [ ] Department/entity restrictions tested
- [ ] Session-based authentication working
- [ ] Error handling working properly

This comprehensive testing ensures your RBAC system properly controls access to all policy module functionalities based on user permissions. 