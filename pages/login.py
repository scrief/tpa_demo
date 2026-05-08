"""
Login page for TPA Match Demo.
"""

import streamlit as st
import sys
from pathlib import Path

# Add scripts to path
sys.path.append(str(Path(__file__).parent.parent / "scripts"))
from auth import authenticate_user, login_user, create_user


def show_login_page():
    """Display the login page."""
    st.markdown('<h1 class="main-title">Welcome to TPA Match Demo</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Log in to find the perfect TPA vendor for your needs</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Create tabs for Login and Sign Up
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
    
    with tab1:
        show_login_form()
    
    with tab2:
        show_signup_form()


def show_login_form():
    """Display the login form."""
    st.markdown("### Login to Your Account")
    
    with st.form("login_form"):
        username = st.text_input(
            "Username",
            placeholder="Enter your username",
            key="login_username"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password"
        )
        
        col1, col2 = st.columns([1, 3])
        with col1:
            submit = st.form_submit_button("🔐 Login", type="primary", use_container_width=True)
        
        if submit:
            if not username or not password:
                st.error("❌ Please enter both username and password")
            else:
                user = authenticate_user(username, password)
                
                if user:
                    login_user(user)
                    st.success(f"✅ Welcome back, {user['full_name'] or user['username']}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
    
    # Demo credentials info
    st.info("""
        **Demo Credentials:**
        
        Regular User: `demo` / `demo123`
        
        Admin User: `admin` / `admin123`
    """)


def show_signup_form():
    """Display the signup form."""
    st.markdown("### Create New Account")
    
    with st.form("signup_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_username = st.text_input(
                "Username *",
                placeholder="Choose a username",
                key="signup_username"
            )
            
            new_email = st.text_input(
                "Email *",
                placeholder="your.email@example.com",
                key="signup_email"
            )
        
        with col2:
            new_full_name = st.text_input(
                "Full Name",
                placeholder="Your full name (optional)",
                key="signup_fullname"
            )
            
            new_password = st.text_input(
                "Password *",
                type="password",
                placeholder="Choose a strong password",
                key="signup_password"
            )
        
        confirm_password = st.text_input(
            "Confirm Password *",
            type="password",
            placeholder="Re-enter your password",
            key="signup_confirm"
        )
        
        submit = st.form_submit_button("📝 Sign Up", type="primary", use_container_width=True)
        
        if submit:
            # Validation
            if not new_username or not new_email or not new_password:
                st.error("❌ Please fill in all required fields")
            elif new_password != confirm_password:
                st.error("❌ Passwords do not match")
            elif len(new_password) < 6:
                st.error("❌ Password must be at least 6 characters long")
            elif "@" not in new_email or "." not in new_email:
                st.error("❌ Please enter a valid email address")
            else:
                # Create user
                success = create_user(
                    username=new_username,
                    email=new_email,
                    password=new_password,
                    full_name=new_full_name if new_full_name else None,
                    role='user'
                )
                
                if success:
                    st.success(f"✅ Account created successfully! Please log in with your credentials.")
                    st.info(f"Username: `{new_username}`")
                else:
                    st.error("❌ Username or email already exists. Please choose different ones.")
