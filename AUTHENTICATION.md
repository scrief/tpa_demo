# Authentication System

## Overview

The TPA Match Demo now includes a secure authentication system to protect access to the application.

## Features

- **Secure Login**: Password hashing using SHA-256
- **User Registration**: Sign up form for new users
- **Session Management**: Streamlit session state for persistent login
- **Role-Based Access**: Support for regular users and admin users
- **Protected Routes**: All app pages require login

## Quick Start

### Demo Credentials

The system comes with two pre-configured demo accounts:

**Regular User:**
- Username: `demo`
- Password: `demo123`

**Admin User:**
- Username: `admin`
- Password: `admin123`

### Setup

Authentication is automatically enabled when you run the app. The system will:
1. Check if you're logged in
2. Show login page if not authenticated
3. Allow access to all features once logged in

## User Management

### Database Schema

Users are stored in the `users` table with the following fields:
- `user_id`: Primary key
- `username`: Unique username
- `email`: Unique email address
- `password_hash`: SHA-256 hashed password
- `full_name`: Optional full name
- `role`: Either 'user' or 'admin'
- `created_at`: Account creation timestamp
- `last_login`: Last login timestamp
- `is_active`: Account status flag

### Creating New Users

**Option 1: Sign Up Form**
- Click the "Sign Up" tab on the login page
- Fill in required fields (username, email, password)
- Optional: Add full name
- Click "Sign Up"

**Option 2: Programmatically**
```python
from scripts.auth import create_user

create_user(
    username='newuser',
    email='user@example.com',
    password='password123',
    full_name='New User',
    role='user'  # or 'admin'
)
```

### Password Requirements

- Minimum 6 characters
- No special character requirements (can be customized)

## Security Features

1. **Password Hashing**: Passwords are hashed with SHA-256 before storage
2. **Session Management**: Secure session state tracking
3. **Active Status**: Users can be deactivated without deletion
4. **Last Login Tracking**: Audit trail of user logins

## File Structure

```
TPA Demo/
├── scripts/
│   ├── auth.py                    # Core authentication logic
│   ├── create_users_table.py      # Database setup script
│   └── create_demo_users.py       # Demo account creation
├── pages/
│   └── login.py                   # Login/signup UI
└── app.py                          # Updated with auth integration
```

## API Reference

### auth.py Functions

**`authenticate_user(username, password)`**
- Verifies credentials and returns user dict
- Updates last_login timestamp
- Returns None if authentication fails

**`is_logged_in()`**
- Returns True if user is currently logged in

**`get_current_user()`**
- Returns current user dict or None

**`is_admin()`**
- Returns True if current user has admin role

**`login_user(user)`**
- Stores user in session state

**`logout_user()`**
- Clears user from session state

**`create_user(username, email, password, full_name, role)`**
- Creates new user account
- Returns True if successful, False if username/email exists

## Customization

### Adding More Roles

Edit the role constraint in `create_users_table.py`:
```sql
role TEXT DEFAULT 'user' CHECK(role IN ('user', 'admin', 'manager', 'viewer'))
```

### Stronger Password Hashing

Consider upgrading to bcrypt or argon2 for production:
```python
# Install: pip install bcrypt
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())
```

### Adding Password Strength Requirements

In `pages/login.py`, add validation:
```python
import re

def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain uppercase letter"
    if not re.search(r"[0-9]", password):
        return False, "Password must contain a number"
    return True, ""
```

## Troubleshooting

**Can't log in after signup:**
- Verify username and password are correct
- Check that the user was created successfully in the database

**Session expires unexpectedly:**
- This is normal Streamlit behavior when the page is refreshed
- Users will need to log in again

**Want to reset demo accounts:**
```bash
# Delete existing users
sqlite3 database/tpa_match_demo.db "DELETE FROM users WHERE username IN ('demo', 'admin')"

# Recreate them
python scripts/create_demo_users.py
```

## Future Enhancements

Potential improvements for production use:
- [ ] Email verification
- [ ] Password reset functionality
- [ ] Two-factor authentication (2FA)
- [ ] OAuth integration (Google, Microsoft)
- [ ] Password strength meter
- [ ] Account lockout after failed attempts
- [ ] Password expiration policies
- [ ] Audit log for all authentication events
- [ ] Remember me functionality
- [ ] Profile management page

## Security Best Practices

1. **Never commit `.env` files** with real API keys
2. **Use HTTPS** in production
3. **Implement rate limiting** to prevent brute force
4. **Regular security audits** of authentication code
5. **Keep dependencies updated** for security patches
6. **Use environment variables** for sensitive configuration
7. **Implement proper logging** for security events
8. **Consider professional security review** before production deployment

---

**Note:** This authentication system is suitable for demos and internal tools. For production applications handling sensitive data, consider using established authentication services like Auth0, AWS Cognito, or Firebase Authentication.
