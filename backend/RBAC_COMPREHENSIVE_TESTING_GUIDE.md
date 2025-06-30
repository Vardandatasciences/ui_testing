# Comprehensive RBAC Testing Guide for GRC Policy Module

## Overview

This guide provides step-by-step instructions for testing the comprehensive Role-Based Access Control (RBAC) system implemented for the GRC Policy Module. The RBAC system controls access to all policy-related endpoints based on user permissions.

## Table of Contents

1. [Setup and Prerequisites](#setup-and-prerequisites)
2. [Test User Profiles](#test-user-profiles)
3. [Database Changes Required](#database-changes-required)
4. [Testing Methodology](#testing-methodology)
5. [Endpoint Testing Matrix](#endpoint-testing-matrix)
6. [Session-Based Testing](#session-based-testing)
7. [Expected Results by User Type](#expected-results-by-user-type)
8. [Troubleshooting](#troubleshooting)

## Setup and Prerequisites

### 1. Database Setup

First, ensure the RBAC table exists and load test data:

```bash
# Navigate to backend directory
cd backend

# Apply the test data
mysql -u root -p grc < test_rbac_comprehensive_data.sql
```

### 2. Verify Django Settings

Ensure these settings are configured in your Django settings:

```python
# In backend/backend/settings.py
INSTALLED_APPS = [
    # ... other apps
    'grc.rbac',
]

MIDDLEWARE = [
    # ... other middleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    # ... other middleware
]

# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_NAME = 'grc_sessionid'
SESSION_COOKIE_AGE = 86400  # 24 hours
```

### 3. Run Migrations

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

## Test User Profiles

Our test data includes 11 different user profiles with varying permission levels:

| User ID | Username | Role | Policy Permissions | Department Access | Entity Access |
|---------|----------|------|-------------------|-------------------|---------------|
| 100 | policy_admin | Administrator | All (CVEAD+) | All | All |
| 101 | policy_manager | Manager | CVEA+ (no Delete) | GRC, Policy, Compliance, Audit | Corporate, Test, Internal |
| 102 | policy_creator | Creator | CVE (no Approve/Delete) | Policy, Compliance | Corporate, Test |
| 103 | policy_reviewer | Reviewer | VA (View + Approve only) | All except General | Corporate, Test, Internal, External |
| 104 | policy_viewer | Viewer | V (View only) | Policy, General | Corporate |
| 105 | framework_manager | Framework Manager | CVEA+ (Framework focus) | GRC, Policy, Compliance | All |
| 106 | analytics_user | Analytics Specialist | V (View + Analytics) | All except General | All |
| 107 | dept_limited | Department User | CVE | Policy only | Corporate |
| 108 | entity_limited | Regional User | V | Policy, Compliance | Europe only |
| 109 | no_permissions | Guest | None | General | Test |
| 110 | mixed_permissions | Mixed Role | Complex mix | Mixed | Mixed |

**Permission Legend:**
- C = Create, V = View, E = Edit, A = Approve, D = Delete, + = Assign

## Database Changes Required

### New RBAC Table Structure

The RBAC system uses a single comprehensive table with the following key fields:

```sql
-- Core user information
user_id, email, role, department, entity

-- Policy module permissions
policy_create, policy_view, policy_edit, policy_approve, policy_delete, policy_assign

-- Other module permissions (for future expansion)
compliance_*, audit_*, risk_*, incident_*

-- Department access controls
dept_grc, dept_policy, dept_compliance, dept_audit, dept_risk, dept_incident, dept_management, dept_general

-- Entity access controls
entity_corporate, entity_test, entity_internal, entity_external, entity_north_america, entity_europe, entity_asia_pacific

-- Additional permissions
can_view_all_departments, can_view_all_entities, can_export_data, can_import_data, 
can_manage_users, can_view_reports, can_create_reports, can_approve_workflows

-- Status and audit fields
is_active, created_at, updated_at
```

### Migration Script

Run this if the RBAC table doesn't exist:

```sql
-- Run this in your MySQL client
USE grc;

CREATE TABLE IF NOT EXISTS rbac (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    email VARCHAR(255) NOT NULL,
    role VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    entity VARCHAR(100),
    
    -- Policy permissions
    policy_create BOOLEAN DEFAULT FALSE,
    policy_view BOOLEAN DEFAULT FALSE,
    policy_edit BOOLEAN DEFAULT FALSE,
    policy_approve BOOLEAN DEFAULT FALSE,
    policy_delete BOOLEAN DEFAULT FALSE,
    policy_assign BOOLEAN DEFAULT FALSE,
    
    -- Compliance permissions
    compliance_create BOOLEAN DEFAULT FALSE,
    compliance_view BOOLEAN DEFAULT FALSE,
    compliance_edit BOOLEAN DEFAULT FALSE,
    compliance_approve BOOLEAN DEFAULT FALSE,
    compliance_delete BOOLEAN DEFAULT FALSE,
    compliance_assign BOOLEAN DEFAULT FALSE,
    
    -- Audit permissions
    audit_create BOOLEAN DEFAULT FALSE,
    audit_view BOOLEAN DEFAULT FALSE,
    audit_edit BOOLEAN DEFAULT FALSE,
    audit_approve BOOLEAN DEFAULT FALSE,
    audit_delete BOOLEAN DEFAULT FALSE,
    audit_assign BOOLEAN DEFAULT FALSE,
    
    -- Risk permissions
    risk_create BOOLEAN DEFAULT FALSE,
    risk_view BOOLEAN DEFAULT FALSE,
    risk_edit BOOLEAN DEFAULT FALSE,
    risk_approve BOOLEAN DEFAULT FALSE,
    risk_delete BOOLEAN DEFAULT FALSE,
    risk_assign BOOLEAN DEFAULT FALSE,
    
    -- Incident permissions
    incident_create BOOLEAN DEFAULT FALSE,
    incident_view BOOLEAN DEFAULT FALSE,
    incident_edit BOOLEAN DEFAULT FALSE,
    incident_approve BOOLEAN DEFAULT FALSE,
    incident_delete BOOLEAN DEFAULT FALSE,
    incident_assign BOOLEAN DEFAULT FALSE,
    
    -- Department access
    dept_grc BOOLEAN DEFAULT FALSE,
    dept_policy BOOLEAN DEFAULT FALSE,
    dept_compliance BOOLEAN DEFAULT FALSE,
    dept_audit BOOLEAN DEFAULT FALSE,
    dept_risk BOOLEAN DEFAULT FALSE,
    dept_incident BOOLEAN DEFAULT FALSE,
    dept_management BOOLEAN DEFAULT FALSE,
    dept_general BOOLEAN DEFAULT FALSE,
    
    -- Entity access
    entity_corporate BOOLEAN DEFAULT FALSE,
    entity_test BOOLEAN DEFAULT FALSE,
    entity_internal BOOLEAN DEFAULT FALSE,
    entity_external BOOLEAN DEFAULT FALSE,
    entity_north_america BOOLEAN DEFAULT FALSE,
    entity_europe BOOLEAN DEFAULT FALSE,
    entity_asia_pacific BOOLEAN DEFAULT FALSE,
    
    -- Additional permissions
    can_view_all_departments BOOLEAN DEFAULT FALSE,
    can_view_all_entities BOOLEAN DEFAULT FALSE,
    can_export_data BOOLEAN DEFAULT FALSE,
    can_import_data BOOLEAN DEFAULT FALSE,
    can_manage_users BOOLEAN DEFAULT FALSE,
    can_view_reports BOOLEAN DEFAULT FALSE,
    can_create_reports BOOLEAN DEFAULT FALSE,
    can_approve_workflows BOOLEAN DEFAULT FALSE,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_user_id (user_id),
    INDEX idx_email (email),
    INDEX idx_role (role),
    INDEX idx_department (department),
    INDEX idx_entity (entity),
    INDEX idx_active (is_active),
    INDEX idx_user_active (user_id, is_active),
    
    -- Constraints
    UNIQUE KEY unique_user (user_id)
);
```

## Testing Methodology

### 1. Session-Based Testing Approach

We use Django sessions to simulate different users without complex authentication:

```python
# Create test session for a user
python manage.py shell

# In the shell:
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore

# Create session for user 100 (admin)
session = SessionStore()
session['user_id'] = 100
session.save()
print(f"Admin session key: {session.session_key}")

# Create session for user 104 (viewer)
session = SessionStore()
session['user_id'] = 104
session.save()
print(f"Viewer session key: {session.session_key}")
```

### 2. Browser Testing Setup

Use browser developer tools to set session cookies:

1. Open browser developer tools (F12)
2. Go to Application/Storage tab
3. Find Cookies section
4. Add cookie: `grc_sessionid` = `your_session_key`
5. Set Domain to your application domain
6. Test endpoints

### 3. API Testing with cURL

```bash
# Test with admin user (user 100)
curl -H "Cookie: grc_sessionid=your_admin_session_key" \
     http://localhost:8000/api/frameworks/

# Test with viewer user (user 104) - should have limited access
curl -H "Cookie: grc_sessionid=your_viewer_session_key" \
     http://localhost:8000/api/frameworks/

# Test creating a framework (should fail for viewer)
curl -X POST \
     -H "Cookie: grc_sessionid=your_viewer_session_key" \
     -H "Content-Type: application/json" \
     -d '{"FrameworkName": "Test Framework"}' \
     http://localhost:8000/api/frameworks/
```

## Endpoint Testing Matrix

### Framework Endpoints

| Endpoint | Method | Admin (100) | Manager (101) | Creator (102) | Reviewer (103) | Viewer (104) | No-Perm (109) |
|----------|--------|-------------|---------------|---------------|----------------|--------------|---------------|
| `/api/frameworks/` | GET | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `/api/frameworks/` | POST | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `/api/frameworks/{id}/` | GET | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `/api/frameworks/{id}/` | PUT | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `/api/frameworks/{id}/` | DELETE | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |

### Policy Endpoints

| Endpoint | Method | Admin (100) | Manager (101) | Creator (102) | Reviewer (103) | Viewer (104) | No-Perm (109) |
|----------|--------|-------------|---------------|---------------|----------------|--------------|---------------|
| `/api/policies/` | GET | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `/api/policies/` | POST | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `/api/policies/{id}/` | GET | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `/api/policies/{id}/` | PUT | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `/api/policies/{id}/` | DELETE | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |

### Approval Workflow Endpoints

| Endpoint | Method | Admin (100) | Manager (101) | Creator (102) | Reviewer (103) | Viewer (104) | No-Perm (109) |
|----------|--------|-------------|---------------|---------------|----------------|--------------|---------------|
| `/api/policy-approvals/{id}/` | PUT | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ |
| `/api/policy-approvals/reviewer/` | GET | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ |
| `/api/frameworks/{id}/submit-review/` | POST | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ |

### Analytics Endpoints

| Endpoint | Method | Admin (100) | Manager (101) | Creator (102) | Reviewer (103) | Viewer (104) | Analytics (106) | No-Perm (109) |
|----------|--------|-------------|---------------|---------------|----------------|--------------|-----------------|---------------|
| `/api/policy-analytics/` | GET | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ |
| `/api/policy-kpis/` | GET | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ |
| `/api/policy-dashboard/` | GET | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |

### Versioning Endpoints

| Endpoint | Method | Admin (100) | Manager (101) | Creator (102) | Reviewer (103) | Viewer (104) | No-Perm (109) |
|----------|--------|-------------|---------------|---------------|----------------|--------------|---------------|
| `/api/policies/{id}/create-version/` | POST | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `/api/frameworks/{id}/create-version/` | POST | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `/api/policies/{id}/versions/` | GET | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |

## Session-Based Testing

### Step 1: Create Test Sessions

Use this Python script to create sessions for all test users:

```python
# backend/create_test_sessions.py
from django.contrib.sessions.backends.db import SessionStore
import json

test_users = {
    100: 'admin',
    101: 'manager', 
    102: 'creator',
    103: 'reviewer',
    104: 'viewer',
    105: 'framework',
    106: 'analytics',
    107: 'dept_limited',
    108: 'entity_limited',
    109: 'no_permissions',
    110: 'mixed'
}

sessions = {}

for user_id, role in test_users.items():
    session = SessionStore()
    session['user_id'] = user_id
    session.save()
    sessions[role] = session.session_key
    print(f"{role} (user {user_id}): {session.session_key}")

# Save to file for reference
with open('test_sessions.json', 'w') as f:
    json.dump(sessions, f, indent=2)

print("\nSessions saved to test_sessions.json")
print("Use these session keys in your browser cookies as 'grc_sessionid'")
```

### Step 2: Browser Testing

1. Open your browser's developer tools
2. Set the cookie `grc_sessionid` to one of the session keys
3. Navigate to your GRC application
4. Test various endpoints and verify access control

### Step 3: Automated Testing Script

```python
# backend/test_rbac_endpoints.py
import requests
import json
from datetime import datetime

# Load session keys
with open('test_sessions.json', 'r') as f:
    sessions = json.load(f)

BASE_URL = 'http://localhost:8000'

def test_endpoint(session_key, endpoint, method='GET', data=None):
    """Test an endpoint with a specific session"""
    cookies = {'grc_sessionid': session_key}
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == 'GET':
            response = requests.get(url, cookies=cookies)
        elif method == 'POST':
            response = requests.post(url, cookies=cookies, json=data)
        elif method == 'PUT':
            response = requests.put(url, cookies=cookies, json=data)
        elif method == 'DELETE':
            response = requests.delete(url, cookies=cookies)
        
        return response.status_code, response.text[:100]
    except Exception as e:
        return None, str(e)

# Test matrix
test_cases = [
    ('/api/frameworks/', 'GET'),
    ('/api/frameworks/', 'POST', {'FrameworkName': 'Test Framework'}),
    ('/api/policies/', 'GET'),
    ('/api/policy-analytics/', 'GET'),
    ('/api/policy-kpis/', 'GET'),
]

# Run tests for each user
results = {}
for role, session_key in sessions.items():
    results[role] = {}
    print(f"\nTesting {role}:")
    
    for test_case in test_cases:
        endpoint = test_case[0]
        method = test_case[1]
        data = test_case[2] if len(test_case) > 2 else None
        
        status_code, response = test_endpoint(session_key, endpoint, method, data)
        results[role][f"{method} {endpoint}"] = status_code
        
        print(f"  {method} {endpoint}: {status_code}")

# Save results
with open(f'rbac_test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
    json.dump(results, f, indent=2)
```

## Expected Results by User Type

### Administrator (User 100)
- **Expected**: Full access to all endpoints
- **Should succeed**: All CRUD operations, analytics, exports, approvals
- **Should fail**: Nothing (has all permissions)

### Manager (User 101)
- **Expected**: Most operations except delete
- **Should succeed**: Create, read, update, approve policies/frameworks
- **Should fail**: Delete operations, some restricted analytics

### Creator (User 102)
- **Expected**: Create and edit access only
- **Should succeed**: Create, read, update policies/frameworks
- **Should fail**: Approval operations, delete operations, analytics

### Reviewer (User 103)
- **Expected**: View and approve access only
- **Should succeed**: Read operations, approval operations
- **Should fail**: Create, update, delete operations

### Viewer (User 104)
- **Expected**: Read-only access
- **Should succeed**: View policies, frameworks, basic reports
- **Should fail**: All write operations, analytics, approvals

### No Permissions (User 109)
- **Expected**: No policy access
- **Should succeed**: Nothing in policy module
- **Should fail**: All policy-related endpoints

## Troubleshooting

### Common Issues

1. **Permission Denied Errors**
   ```
   Status: 403 Forbidden
   Response: {"detail": "You do not have permission to perform this action."}
   ```
   - Check user's RBAC record exists and is active
   - Verify correct session cookie is set
   - Confirm endpoint requires correct permission

2. **Session Not Found**
   ```
   Status: 403 Forbidden  
   Response: "No user_id found in session"
   ```
   - Check session middleware is enabled
   - Verify session cookie name matches `grc_sessionid`
   - Ensure session hasn't expired

3. **User Not Found in RBAC**
   ```
   Status: 403 Forbidden
   Response: "No RBAC record found for user"
   ```
   - Run the test data SQL script
   - Check user exists in both `users` and `rbac` tables
   - Verify `is_active` field is TRUE

### Debug Queries

```sql
-- Check if user exists in RBAC
SELECT * FROM rbac WHERE user_id = 100;

-- Check user permissions summary
SELECT 
    user_id, email, role, 
    policy_create, policy_view, policy_edit, policy_approve,
    is_active
FROM rbac 
WHERE user_id BETWEEN 100 AND 110;

-- Check active sessions
SELECT session_key, session_data, expire_date 
FROM django_session 
WHERE expire_date > NOW();
```

### Debug Logging

Enable verbose RBAC logging in Django settings:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'grc.rbac': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

### Testing Checklist

- [ ] RBAC table created and populated with test data
- [ ] All 11 test users created with correct permissions
- [ ] Session middleware enabled
- [ ] Test sessions created and verified
- [ ] Framework endpoints tested with different user types
- [ ] Policy endpoints tested with different user types
- [ ] Approval workflow tested with appropriate users
- [ ] Analytics endpoints tested with analytics user
- [ ] Version control endpoints tested
- [ ] Permission denials working correctly
- [ ] Department/entity restrictions working
- [ ] Logging and debugging working

## Conclusion

This comprehensive RBAC system provides fine-grained access control across all policy module functionalities. The test suite validates that users can only access endpoints and perform operations that match their assigned permissions, ensuring security and proper workflow enforcement.

Use this guide to systematically test all aspects of the RBAC implementation and verify that the system meets your security requirements. 