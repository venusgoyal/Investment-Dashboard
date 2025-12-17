# Investment Dashboard - Authentication & Security Guide

## Overview

The Investment Dashboard now includes a complete authentication system with role-based access control and admin panel for user management.

## Features

### 🔐 Authentication System
- **Secure Login/Register**: User registration with password hashing (SHA-256)
- **Session Management**: Streamlit session-based authentication
- **Role-Based Access Control**: Admin and User roles
- **Password Security**: Passwords are hashed and never stored in plain text

### 👥 User Management (Admin Only)
- View all users in the system
- Assign/change user roles (Admin/User)
- Activate/deactivate users
- Delete users
- View user statistics and analytics

### 👤 User Profile
- View personal profile information
- Change password with current password verification
- View account creation date and status

### 📊 Admin Dashboard
- System statistics (Total users, Active users, Admin count)
- User role distribution chart
- User management interface

## Default Admin Account

**To create the first admin account:**

1. Start the app for the first time
2. Click **Register** tab
3. Fill in the details with your preferred username and email
4. After registration, contact database admin to set role to 'admin' OR
5. Use this SQL command to promote first user to admin:

```sql
UPDATE users SET role = 'admin' WHERE username = 'your_username';
```

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    user_id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT '0000-00-00 00:00:00',
    KEY idx_username (username),
    KEY idx_email (email),
    KEY idx_role (role)
)
```

## User Roles

### 👤 User
- Can create, view, update, and delete their own investments
- Can manage their profile and change password
- No access to admin panel or user management

### 👑 Admin
- All User permissions
- Access to Admin Panel
- Can view all users in the system
- Can change user roles (promote/demote users)
- Can activate/deactivate user accounts
- Can delete user accounts
- View system statistics and analytics

## Architecture

### File Structure

```
app-mysql/
├── app.py                 # Main Streamlit application
├── auth_pages.py          # Authentication pages (login, register, profile, admin)
├── mysql_service.py       # Database service with AuthenticationService
├── .streamlit/
│   └── secrets.toml       # Secure credentials (Git ignored)
└── .gitignore             # Includes .streamlit/secrets.toml
```

### Components

1. **AuthenticationService** (mysql_service.py)
   - User registration
   - User authentication
   - User management (CRUD operations)
   - Password management
   - Role management

2. **Auth Pages** (auth_pages.py)
   - Login/Register page
   - Admin panel with user management
   - User profile and password change
   - System statistics

3. **Main App** (app.py)
   - Authentication check on startup
   - Role-based navigation menu
   - Investment management (Dashboard, Create, View, Update, Delete)
   - Admin and Profile pages

## Security Features

### ✅ Implemented
- Password hashing using SHA-256
- Session-based authentication
- Role-based access control (RBAC)
- Protected admin pages (admin-only access)
- Secure credential management via Streamlit Secrets
- User status management (active/inactive)
- Password change functionality with verification

### 🔒 Best Practices
- Never store passwords in plain text
- Use environment variables for sensitive data
- Validate all user inputs
- Check authentication on every page load
- Implement proper error handling

## Streamlit Cloud Deployment

### Step 1: Create .streamlit/secrets.toml Locally

```toml
[mysql]
host = "your_mysql_host"
port = 3306
user = "your_mysql_user"
password = "your_mysql_password"
database = "your_database_name"
```

### Step 2: Deploy to Streamlit Cloud

1. Push code to GitHub (secrets.toml is in .gitignore)
2. Go to [Streamlit Cloud](https://share.streamlit.io)
3. Create new app from your repository
4. In app settings, go to "Secrets"
5. Copy-paste the TOML content with your credentials
6. Deploy!

## Usage Guide

### For Users

1. **Registration**
   - Click Register tab
   - Fill in username, email, full name, and password
   - Click Register
   - Login with your credentials

2. **Managing Investments**
   - Use Dashboard to view overview
   - Use Create to add new investments
   - Use View All to see all investments
   - Use Update to modify existing investments
   - Use Delete to remove investments

3. **Profile Management**
   - Click Profile in sidebar
   - View your account information
   - Change your password

### For Admins

1. **User Management**
   - Click Admin Panel in sidebar
   - View all users in the system
   - Change user roles
   - Activate/deactivate users
   - Delete users if needed

2. **System Statistics**
   - Click Statistics tab
   - View user count breakdown
   - View admin vs user distribution

## API Reference

### AuthenticationService Methods

```python
# Registration
register_user(username, email, password, full_name="", role="user")

# Authentication
authenticate_user(username, password)

# User Retrieval
get_user_by_id(user_id)
get_user_by_username(username)
get_all_users()

# User Management
update_user_role(user_id, role)
toggle_user_status(user_id)
delete_user(user_id)

# Password Management
change_password(user_id, old_password, new_password)

# Password Hashing
hash_password(password)  # Static method
```

## Troubleshooting

### Can't login
- Verify username is correct (case-sensitive)
- Check password matches registration
- Ensure account is active (admin can check)

### Forgot password
- Currently, users cannot self-reset passwords
- Admin must delete the account and user can register again
- OR manually update database: `UPDATE users SET password_hash = '...' WHERE user_id = '...';`

### Can't access Admin Panel
- Verify your account role is 'admin'
- Ask another admin to promote your account
- Or use SQL: `UPDATE users SET role = 'admin' WHERE username = 'your_username';`

### Database connection errors
- Check credentials in secrets.toml
- Verify database server is running
- Check firewall/network connectivity
- Verify database and tables exist

## Security Checklist

- [ ] Change default admin password if any
- [ ] Use strong passwords (8+ characters recommended)
- [ ] Regularly audit user accounts
- [ ] Deactivate unused accounts
- [ ] Monitor admin activity
- [ ] Keep database credentials secure
- [ ] Regular backups of database
- [ ] Use HTTPS in production (Streamlit Cloud provides this)

## Future Enhancements

- [ ] Email verification for registration
- [ ] Password reset via email
- [ ] Two-factor authentication (2FA)
- [ ] Activity logging and audit trail
- [ ] OAuth integration (Google, GitHub)
- [ ] User permission levels (read-only, editor, etc.)
- [ ] Session timeout management
- [ ] Login attempt tracking and rate limiting

## Support

For issues or questions about authentication:
1. Check this documentation
2. Review code comments in auth_pages.py
3. Check mysql_service.py for AuthenticationService implementation
4. Review app.py for authentication flow

---

**Version**: 1.0  
**Last Updated**: December 2025  
**Built with**: Streamlit + MySQL + Python
