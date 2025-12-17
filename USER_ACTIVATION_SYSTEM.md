# User Activation System Documentation

## Overview
The Investment Dashboard now implements a user activation system where newly registered users cannot access investment management features until an administrator approves and activates their account.

## System Architecture

### 1. **User Registration Flow**
When a new user registers:
- Account is created in the database with `is_active = FALSE`
- User receives a confirmation message that their account is pending admin approval
- User cannot login or access investment features until activated

**User sees:**
```
✅ Registration successful!
⏳ Account Pending Activation

Your account has been created but needs admin approval before you can access the investment pages.
An administrator will review your account and activate it shortly.
```

### 2. **User Login Flow**
When a user tries to login:
1. System checks if user exists
2. System verifies password
3. **NEW:** System checks if user is active (`is_active = TRUE`)

**Three possible outcomes:**
- ❌ **Invalid credentials** → "Invalid username or password!"
- 🔒 **Inactive account** → "Your account is awaiting admin approval!"
- ✅ **Active account** → Login successful

### 3. **Active vs Inactive User Dashboard**

#### **Inactive User Permissions:**
- ✅ Can view and edit their profile
- ✅ Can change password
- ✅ Can logout
- ❌ Cannot access Dashboard
- ❌ Cannot create investments
- ❌ Cannot view investments
- ❌ Cannot update investments
- ❌ Cannot delete investments
- ❌ Cannot access Admin Panel (if admin)

**Menu items shown to inactive users:**
- 👤 Profile
- 🚪 Logout

**Additional warning displayed:**
```
🔒 Account Pending Activation

Your account is awaiting admin approval. You can only access your profile settings 
until your account is activated.
```

#### **Active User Permissions:**
- ✅ Full access to all investment features
- ✅ Dashboard with analytics
- ✅ Create investments
- ✅ View all investments
- ✅ Update investments
- ✅ Delete investments
- ✅ Access Profile settings
- ✅ Access Admin Panel (if admin role)

**Menu items shown to active users:**
- 📊 Dashboard
- ➕ Create
- 👁️ View All
- ✏️ Update
- 🗑️ Delete
- 👨‍💼 Admin Panel (admin only)
- 👤 Profile
- 🚪 Logout

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    user_id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) NOT NULL DEFAULT 'user',  -- 'user' or 'admin'
    is_active BOOLEAN DEFAULT FALSE,            -- NEW: Must be TRUE to access features
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT '0000-00-00 00:00:00',
    KEY idx_username (username),
    KEY idx_email (email),
    KEY idx_role (role)
);
```

## Admin Panel Features

### User Management
The Admin Panel now has these capabilities:

1. **View All Users**
   - Shows username, email, full name, role, and status
   - Status column shows: 🟢 Active or 🔴 Inactive

2. **Toggle User Status**
   - Click "🔓 Toggle Status" to activate/deactivate users
   - Activated users can immediately login
   - Deactivated users cannot login on next attempt

3. **Modify User Role**
   - Change users between 'user' and 'admin' roles

4. **Delete User**
   - Remove user accounts (cannot delete self)

5. **Statistics**
   - Total users
   - Active users
   - Admin count
   - Inactive users awaiting approval

## Implementation Details

### Key Functions

#### In `mysql_service.py`:

**`register_user()`**
- Creates new user with `is_active=FALSE`
- Returns user data for registration confirmation

**`authenticate_user()`**
- Checks username and password
- **NEW:** Only returns user if `is_active=TRUE`
- Returns None if user is inactive

**`check_user_status()`**
- Used during login for feedback
- Returns: `exists`, `password_correct`, `is_active`
- Allows showing specific error messages

**`toggle_user_status()`**
- Flips user's active status (admin only)
- Used to approve/disapprove accounts

#### In `app.py`:

**`is_user_active()`**
- Returns value of `st.session_state.is_active`
- Used to control access to investment pages

**`show_inactive_user_message()`**
- Displays warning message to inactive users
- Explains what features are locked

#### In `auth_pages.py`:

**`show_login_page()`**
- Uses `check_user_status()` for detailed feedback
- Shows appropriate error for inactive accounts
- Sets `st.session_state.is_active` after successful login

**`show_admin_page()`**
- Displays user management interface
- Toggle buttons for user activation/deactivation
- Statistics dashboard

**`show_profile_page()`**
- Shows user's current status (Active/Inactive)
- Users can change password

## User Journey Examples

### Example 1: New User Registration and Activation

1. **New User Registration**
   ```
   Username: john_doe
   Email: john@example.com
   Password: MyPassword123
   ```
   Result: Account created with `is_active=FALSE`

2. **User Attempts Login**
   ```
   Username: john_doe
   Password: MyPassword123
   ```
   Result: ❌ "Your account is awaiting admin approval!"

3. **Admin Activates User**
   - Goes to Admin Panel
   - Selects john_doe
   - Clicks "🔓 Toggle Status"
   - User is now active

4. **User Attempts Login Again**
   ```
   Username: john_doe
   Password: MyPassword123
   ```
   Result: ✅ Login successful! Full access to dashboard

### Example 2: Admin Deactivating an Active User

1. **Admin Panel**
   - Goes to Admin Panel
   - Selects target user
   - Clicks "🔓 Toggle Status"
   - User is now inactive

2. **User Attempts Login**
   ```
   Username: [previously active user]
   Password: [correct password]
   ```
   Result: ❌ "Your account is awaiting admin approval!"

## Session State Variables

All user activation state is stored in `st.session_state`:

```python
st.session_state.authenticated   # True if user is logged in
st.session_state.user_id         # User's ID from database
st.session_state.username        # User's username
st.session_state.email           # User's email
st.session_state.full_name       # User's full name
st.session_state.role            # 'user' or 'admin'
st.session_state.is_active       # NEW: True if user is activated by admin
st.session_state.refresh_key     # Counter for forcing page refreshes
```

## Access Control Logic

### Protecting Investment Pages
```python
if not is_user_active():
    show_inactive_user_message()
else:
    # Show investment page content
    # Dashboard, Create, View, Update, Delete pages
```

This pattern is used on:
- Dashboard (Line ~415)
- Create Investment (Line ~655)
- View All Investments (Line ~738)
- Update Investment (Line ~829)
- Delete Investment (Line ~964)

### Dynamic Menu Generation
```python
if st.session_state.is_active:
    # Show full menu with all investment features
    menu_options = ["📊 Dashboard", "➕ Create", "👁️ View All", ...]
else:
    # Show limited menu
    menu_options = ["👤 Profile", "🚪 Logout"]
    # Display warning message
```

## Testing the System

### Step-by-Step Test

1. **Test Registration**
   - Open app at login/register page
   - Register a new account
   - Verify registration success message shows account is pending

2. **Test Login Rejection**
   - Try logging in with new account
   - Verify error message: "Your account is awaiting admin approval!"

3. **Test Admin Activation**
   - Login as admin
   - Go to Admin Panel
   - Find the new user
   - Click "Toggle Status" to activate

4. **Test Login Success**
   - Logout from admin account
   - Try logging in with new (now active) user
   - Verify successful login and full dashboard access

5. **Test Feature Access**
   - Verify inactive users cannot:
     - See Dashboard menu item
     - Access Dashboard if URL is manipulated
   - Verify active users can:
     - See all menu items
     - Access all features

6. **Test Admin Deactivation**
   - While logged in as active user, note access to all features
   - Login as admin
   - Deactivate the active user
   - Logout
   - Try logging in as deactivated user
   - Verify access is denied

## Security Considerations

1. **Password Hashing**: All passwords are hashed using SHA-256 before storage
2. **SQL Injection Prevention**: Using parameterized queries
3. **Session Security**: User data stored in Streamlit session state
4. **Admin-Only Actions**: Only users with role='admin' can:
   - Access Admin Panel
   - Toggle user status
   - Modify user roles
   - Delete users
5. **Active Status**: Cannot be bypassed by URL manipulation due to server-side checks

## Future Enhancements

Possible improvements to the system:

1. **Email Verification**: Send verification email during registration
2. **Admin Notifications**: Email admins when new users register
3. **Expiring Tokens**: Add token-based authentication for better security
4. **Audit Logging**: Track who activated/deactivated users and when
5. **Bulk User Management**: Activate/deactivate multiple users at once
6. **User Invitations**: Admins can invite specific users
7. **Self-Service Password Reset**: Users can reset forgotten passwords via email
8. **Two-Factor Authentication**: Add 2FA for additional security
9. **Activity Logging**: Track user actions for compliance
10. **Scheduled Activation**: Auto-activate users after X days or on specific date

## Troubleshooting

### Issue: New user can still login
**Solution**: Check if user was created with `is_active=TRUE`. Admins must activate accounts manually.

### Issue: Admin cannot see new users in panel
**Solution**: Ensure admin is looking at "User Management" tab. Check database connection.

### Issue: Inactive user sees investment menu
**Solution**: Clear browser cache and restart the app to refresh session state.

### Issue: Cannot deactivate users
**Solution**: Verify logged-in user has admin role. Check database permissions.

## Code Changes Summary

### Files Modified:
1. **`mysql_service.py`**
   - `register_user()`: Now creates users with `is_active=FALSE`
   - `authenticate_user()`: Now checks `is_active` status
   - `check_user_status()`: Returns `is_active` in status dict
   - `toggle_user_status()`: Already implemented, flips status

2. **`auth_pages.py`**
   - `show_login_page()`: Shows status-specific error messages
   - `show_admin_page()`: Toggle Status button fully functional
   - `show_profile_page()`: Shows user's active status

3. **`app.py`**
   - Initialize `is_active` in session state
   - Dynamic menu generation based on `is_active`
   - Add warning message for inactive users
   - Access control on all investment pages (already in place)

### New Helper Functions:
- `is_user_active()`: Check if current user is active
- `show_inactive_user_message()`: Display restriction message

## Summary

The user activation system is now fully implemented:
- ✅ New users created as inactive
- ✅ Login blocked for inactive users with specific error
- ✅ Admin panel shows user status
- ✅ Admin can toggle user activation status
- ✅ Inactive users see limited menu
- ✅ Investment pages protected with access control
- ✅ User profile shows activation status
