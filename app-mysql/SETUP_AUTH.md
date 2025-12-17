# Quick Setup Guide - Authentication System

## ⚡ Quick Start

### For Local Development

1. **Update secrets file** (if needed):
   ```bash
   cd app-mysql
   # Edit .streamlit/secrets.toml with your database credentials
   ```

2. **Start the app**:
   ```bash
   streamlit run app.py
   ```

3. **First-time setup**:
   - Register a new account
   - Promote first account to admin via SQL:
     ```sql
     UPDATE users SET role = 'admin' WHERE username = 'your_username';
     ```

### For Streamlit Cloud

1. **Push to GitHub** (secrets.toml is already in .gitignore)
   
2. **Deploy via Streamlit Cloud**:
   - Connect your GitHub repo
   - In app settings → Secrets, add:
     ```toml
     [mysql]
     host = "your_host"
     port = 3306
     user = "your_user"
     password = "your_password"
     database = "your_db"
     ```

3. **First user becomes admin** (optional):
   - Register first account
   - Use remote database tool to promote to admin

## 📋 Default Accounts

No default accounts are created. Users must register through the app.

## 🔐 Test Credentials (if created for testing)

After first registration, you can create test accounts:

- **Admin Account**: username: `admin`, password: `admin123` (then promote via SQL)
- **Regular User**: username: `user1`, password: `user123`

## 🛠️ New Features Added

### 1. Login & Registration
- Secure password hashing
- Email validation
- Username uniqueness check

### 2. Admin Panel
- User management interface
- Role assignment
- User activation/deactivation
- System statistics dashboard

### 3. User Profile
- Profile information display
- Password change functionality
- Account status information

### 4. Database Tables
- `users` table with secure schema
- Support for role-based access

## 📦 New Dependencies

No new external dependencies needed. Uses:
- `streamlit` (existing)
- `mysql-connector-python` (existing)
- `hashlib` (Python built-in)
- `uuid` (Python built-in)

## 🎯 Usage

### First Admin Setup

```sql
-- After registering first user, promote to admin:
UPDATE users SET role = 'admin' WHERE username = 'your_first_username';
```

### Create Additional Admins

Use Admin Panel → User Management → Modify User Role

### Test the System

1. Register as normal user
2. Logout and login
3. Try accessing Admin Panel (should fail)
4. Admin logs in and promotes user to admin
5. User logs back in and now has access to Admin Panel

## 🚨 Important Files

- `app.py` - Main application with authentication flow
- `auth_pages.py` - All authentication UI pages
- `mysql_service.py` - Database operations including AuthenticationService
- `.streamlit/secrets.toml` - Credentials (local dev only)
- `AUTHENTICATION.md` - Full documentation

## ⚠️ Security Notes

- Never commit `secrets.toml` to Git (already in .gitignore)
- Don't share passwords in code or issues
- Use strong passwords (recommend 10+ characters)
- Regularly audit user accounts
- Deactivate unused accounts

## 🐛 Common Issues

**"Module not found: auth_pages"**
- Make sure auth_pages.py is in the same directory as app.py

**"MySQL connection failed"**
- Check credentials in .streamlit/secrets.toml
- Verify database server is accessible

**"Can't login"**
- Verify username and password are correct
- Check that user account is active (admin can check)

**"Can't access Admin Panel"**
- Your role must be 'admin'
- Ask another admin to promote you

## 📞 Support

Refer to [AUTHENTICATION.md](AUTHENTICATION.md) for comprehensive documentation.

---

**Happy secure investing! 🚀**
