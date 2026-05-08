"""
Add users table for authentication system.
Run this script to add user authentication to the database.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("database/tpa_match_demo.db")


def create_users_table():
    """Create users table for authentication."""
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found at {DB_PATH}. Run scripts/create_database.py first."
        )
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            role TEXT DEFAULT 'user' CHECK(role IN ('user', 'admin')),
            created_at TEXT NOT NULL,
            last_login TEXT,
            is_active INTEGER DEFAULT 1,
            UNIQUE(username),
            UNIQUE(email)
        )
    """)
    
    # Create index for faster lookups
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)
    """)
    
    conn.commit()
    conn.close()
    
    print("Users table created successfully!")
    print("\nNext steps:")
    print("1. Run: python scripts/create_demo_users.py (to create demo accounts)")
    print("2. Restart your Streamlit app")


if __name__ == "__main__":
    create_users_table()
