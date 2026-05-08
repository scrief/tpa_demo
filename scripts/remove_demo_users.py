"""
Remove demo user accounts for production deployment.
Run this before deploying to production.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("database/tpa_match_demo.db")


def remove_demo_users():
    """Remove demo user accounts from the database."""
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if users table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='users'
    """)
    
    if not cursor.fetchone():
        print("Users table does not exist.")
        conn.close()
        return
    
    # Remove demo accounts
    demo_usernames = ['demo', 'admin']
    
    for username in demo_usernames:
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
    
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    if deleted_count > 0:
        print(f"Removed {deleted_count} demo account(s)")
        print("\nDemo accounts removed successfully!")
        print("Your app is now ready for production deployment.")
        print("\nIMPORTANT: Create a new admin account using the signup form.")
    else:
        print("No demo accounts found (already removed or never created)")


if __name__ == "__main__":
    print("WARNING: This will permanently delete demo accounts!")
    print("Demo accounts to be removed: demo, admin")
    response = input("\nContinue? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        remove_demo_users()
    else:
        print("Operation cancelled.")
