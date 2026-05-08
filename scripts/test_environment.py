"""
Environment Test Script - TPA Match Demo

Run this to verify your Python environment is ready.
"""

import sys

print("=" * 70)
print("Environment Check")
print("=" * 70)
print()

# Check Python version
print(f"[OK] Python version: {sys.version}")
print(f"     Location: {sys.executable}")
print()

# Check required modules
required_modules = [
    ("sqlite3", "Built-in SQLite support"),
    ("pandas", "Data manipulation"),
    ("pathlib", "File path handling"),
    ("json", "JSON handling"),
    ("datetime", "Date/time handling"),
    ("re", "Regular expressions"),
    ("difflib", "String similarity")
]

print("Checking required modules:")
all_good = True

for module_name, description in required_modules:
    try:
        __import__(module_name)
        print(f"  [OK] {module_name:15} - {description}")
    except ImportError:
        print(f"  [MISSING] {module_name:15} - MISSING (needs installation)")
        all_good = False

print()

if not all_good:
    print("[WARNING] Some modules are missing. Install with:")
    print("  pip install pandas")
    print()
else:
    print("[SUCCESS] All required modules are available!")
    print()
    
    # Test SQLite connection
    print("Testing SQLite connection...")
    try:
        import sqlite3
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()
        cursor.execute("SELECT sqlite_version();")
        version = cursor.fetchone()[0]
        conn.close()
        print(f"  [OK] SQLite version: {version}")
        print()
        print("[SUCCESS] Your environment is ready to go!")
    except Exception as e:
        print(f"  [ERROR] SQLite test failed: {e}")

print()
print("=" * 70)
print("Next steps:")
print("=" * 70)
print("1. If pandas is missing: pip install pandas")
print("2. Run: python scripts/create_database.py")
print("3. Run: python scripts/seed_sample_data.py")
print("4. Run: python scripts/clean_data.py (optional)")
print()
