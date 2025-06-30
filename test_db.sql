-- Check that all tables exist
SHOW TABLES LIKE 'rbac%';

-- Verify sample data
SELECT COUNT(*) FROM users;        -- Should be 18
SELECT COUNT(*) FROM rbac;         -- Should be 18
SELECT COUNT(*) FROM rbac_role_permission_matrix; -- Should be 94