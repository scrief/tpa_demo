"""
Create demo user accounts for testing authentication.
"""

import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime

DB_PATH = Path("database/tpa_match_demo.db")


def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def create_demo_users():
    """Create demo user accounts."""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if users table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='users'
    """)
    
    if not cursor.fetchone():
        print("Users table does not exist. Run scripts/create_users_table.py first.")
        conn.close()
        return
    
    demo_users = [
        {
            'username': 'demo',
            'email': 'demo@commonpoint.com',
            'password': 'demo123',
            'full_name': 'Demo User',
            'role': 'user'
        },
        {
            'username': 'admin',
            'email': 'admin@commonpoint.com',
            'password': 'admin123',
            'full_name': 'Admin User',
            'role': 'admin'
        }
    ]
    
    created_count = 0
    
    for user in demo_users:
        try:
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, full_name, role, created_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user['username'],
                user['email'],
                hash_password(user['password']),
                user['full_name'],
                user['role'],
                datetime.now().isoformat(),
                1
            ))
            created_count += 1
            print(f"Created user: {user['username']} ({user['role']})")
        except sqlite3.IntegrityError:
            print(f"User already exists: {user['username']}")
    
    conn.commit()
    conn.close()
    
    if created_count > 0:
        print(f"\nCreated {created_count} demo user(s)")
        print("\nDemo Credentials:")
        print("=" * 50)
        print("Regular User:")
        print("  Username: demo")
        print("  Password: demo123")
        print("\nAdmin User:")
        print("  Username: admin")
        print("  Password: admin123")
        print("=" * 50)
    else:
        print("\nAll demo users already exist")


if __name__ == "__main__":
    create_demo_users()
