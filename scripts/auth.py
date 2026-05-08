"""
Authentication module for TPA Match Demo.
Handles user login, logout, and session management.
"""

import sqlite3
import hashlib
import streamlit as st
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

DB_PATH = Path("database/tpa_match_demo.db")


def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    return hash_password(password) == password_hash


def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """
    Authenticate a user with username and password.
    
    Returns:
        User dict if authentication successful, None otherwise
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT user_id, username, email, password_hash, full_name, role, is_active
        FROM users
        WHERE username = ? AND is_active = 1
    """, (username,))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return None
    
    user_id, username, email, password_hash, full_name, role, is_active = result
    
    if verify_password(password, password_hash):
        # Update last login
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users SET last_login = ? WHERE user_id = ?
        """, (datetime.now().isoformat(), user_id))
        conn.commit()
        conn.close()
        
        return {
            'user_id': user_id,
            'username': username,
            'email': email,
            'full_name': full_name,
            'role': role
        }
    
    return None


def is_logged_in() -> bool:
    """Check if a user is currently logged in."""
    return 'user' in st.session_state and st.session_state.user is not None


def get_current_user() -> Optional[Dict]:
    """Get the currently logged in user."""
    if is_logged_in():
        return st.session_state.user
    return None


def is_admin() -> bool:
    """Check if the current user is an admin."""
    user = get_current_user()
    return user is not None and user.get('role') == 'admin'


def login_user(user: Dict):
    """Log in a user by storing their info in session state."""
    st.session_state.user = user
    st.session_state.logged_in = True


def logout_user():
    """Log out the current user."""
    if 'user' in st.session_state:
        del st.session_state.user
    if 'logged_in' in st.session_state:
        del st.session_state.logged_in


def require_login():
    """
    Decorator/function to require login for a page.
    Call this at the start of protected pages.
    """
    if not is_logged_in():
        st.warning("⚠️ Please log in to access this page.")
        st.stop()


def create_user(username: str, email: str, password: str, full_name: str = None, role: str = 'user') -> bool:
    """
    Create a new user account.
    
    Returns:
        True if user created successfully, False otherwise
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, full_name, role, created_at, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            username,
            email,
            hash_password(password),
            full_name,
            role,
            datetime.now().isoformat(),
            1
        ))
        
        conn.commit()
        conn.close()
        return True
        
    except sqlite3.IntegrityError:
        return False
