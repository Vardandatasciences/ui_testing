# 🧪 RBAC Testing Steps - Policy KPIs Page

## ✅ **What's Fixed:**

1. **Unicode encoding errors** - Removed emoji characters from logs
2. **Session cookie configuration** - Added `withCredentials: true` to all axios requests
3. **Login process** - Properly stores `user_id` in Django session
4. **Permission debugging** - Enhanced logging for troubleshooting

## 🎯 **Testing Process:**

### **Step 1: Start the Application**

1. **Backend:** Django server should be running on `http://localhost:8000`
2. **Frontend:** Start Vue.js dev server on `http://localhost:8080`

### **Step 2: Login with a Valid User**

1. Go to: `http://localhost:8080/login`
2. Use any of these test credentials:
   - **Username:** `admin.grc` | **Password:** `password123` (Admin user)
   - **Username:** `policy.manager` | **Password:** `password123` (Policy Manager)
   - **Username:** `policy.viewer` | **Password:** `password123` (Policy Viewer)

### **Step 3: Test the Policy KPIs Page**

1. After login, navigate to: `http://localhost:8080/performance`
2. **Expected Behavior:**
   - ✅ **With Permission:** Policy KPIs data loads successfully
   - ❌ **Without Permission:** "Access Denied" message with permission details

### **Step 4: Check Debug Logs**

Watch the Django console for detailed RBAC logs:

```
[RBAC DEBUG] ===== REQUEST DEBUG =====
[RBAC DEBUG] Request path: /policy-kpis/
[RBAC DEBUG] Has session: True
[RBAC DEBUG] Session keys: ['user_id', 'grc_user_id', 'grc_username']
[RBAC DEBUG] Session data: {'user_id': 3, 'grc_user_id': 3, 'grc_username': 'policy.viewer'}
[RBAC] Got user_id from session: 3
[RBAC POLICY KPI] User ID: 3
[RBAC POLICY KPI] User Email: policy.viewer@test.com
[RBAC POLICY KPI] User Role: Policy Viewer
[RBAC POLICY KPI] Policy View Permission: True
[RBAC POLICY KPI] FINAL RESULT: ALLOWED
```

## 🔧 **If Still Having Issues:**

### **Issue 1: No Session Cookie**
```
[RBAC DEBUG] Session keys: []
[RBAC DEBUG] Cookies: {}
```
**Solution:** 
- Clear browser cookies
- Login again
- Check browser Dev Tools > Application > Cookies for `grc_sessionid`

### **Issue 2: User Not Found in RBAC**
```
[RBAC POLICY KPI] No RBAC record found for user 1053
```
**Solution:**
```bash
# Update your current user's permissions
mysql -u root -p -e "UPDATE grc.rbac SET policy_view = 1 WHERE user_id = 1053;"
```

### **Issue 3: Permission Denied**
```
[RBAC POLICY KPI] Policy View Permission: False
[RBAC POLICY KPI] FINAL RESULT: DENIED
```
**Solution:**
- Use test user with `policy_view = 1` permission
- Or update current user: `UPDATE rbac SET policy_view = 1 WHERE user_id = YOUR_USER_ID`

## 🎯 **Manual Session Testing (If Needed):**

If login isn't working properly, create a manual test session:

```bash
cd backend
python debug_session.py
# Copy the session key: zzoba2svykrpg92ajbkf2rlf87yeww03
```

Then in browser:
1. Open Dev Tools (F12)
2. Go to Application > Cookies
3. Set: `grc_sessionid = zzoba2svykrpg92ajbkf2rlf87yeww03`
4. Visit: `http://localhost:8080/performance`

## 📊 **Expected Results:**

### **✅ Success Scenario:**
- User logs in successfully
- Session cookie is set
- Policy KPI page loads data
- Console shows: `FINAL RESULT: ALLOWED`

### **❌ Access Denied Scenario:**
- User logs in but lacks permission
- Policy KPI page shows "Access Denied" card
- Console shows: `FINAL RESULT: DENIED`
- Message: "Required permission: policy_view"

## 🚀 **Next Steps:**

Once this is working:
1. Apply same RBAC pattern to other policy endpoints
2. Extend to other modules (audit, risk, compliance)
3. Add more granular permission levels
4. Implement role-based UI components

---

**🔍 Debug Commands:**
- Check sessions: `python debug_session.py`
- Check RBAC data: `SELECT * FROM rbac WHERE user_id = YOUR_ID;`
- Test API directly: `curl -X GET http://localhost:8000/policy-kpis/ --cookie "grc_sessionid=YOUR_SESSION_KEY"` 