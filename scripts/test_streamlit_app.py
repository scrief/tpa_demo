"""Quick test to verify Streamlit app components."""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

DB_PATH = Path("database/tpa_match_demo.db")

def test_database_connectivity():
    """Test database connection and tables."""
    print("Testing database connectivity...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check required tables exist
        required_tables = [
            'vendors', 'buyer_requests', 'match_results', 
            'vendor_states', 'buyer_required_states', 'feedback'
        ]
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        for table in required_tables:
            if table in existing_tables:
                print(f"  [OK] Table '{table}' exists")
            else:
                print(f"  [ERROR] Table '{table}' missing!")
                return False
        
        conn.close()
        return True
    except Exception as e:
        print(f"  [ERROR] Database connectivity failed: {e}")
        return False

def test_data_exists():
    """Test that required data exists."""
    print("\nTesting data availability...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check vendors
        cursor.execute("SELECT COUNT(*) FROM vendors WHERE active_status = 'active'")
        vendor_count = cursor.fetchone()[0]
        print(f"  [OK] {vendor_count} active vendors found")
        
        # Check buyer requests
        cursor.execute("SELECT COUNT(*) FROM buyer_requests")
        buyer_count = cursor.fetchone()[0]
        print(f"  [OK] {buyer_count} buyer requests found")
        
        # Check match results
        cursor.execute("SELECT COUNT(*) FROM match_results")
        match_count = cursor.fetchone()[0]
        print(f"  [OK] {match_count} match results found")
        
        conn.close()
        
        if vendor_count == 0 or buyer_count == 0:
            print("  [WARNING] Limited data available for testing")
            return False
        
        return True
    except Exception as e:
        print(f"  [ERROR] Data check failed: {e}")
        return False

def test_imports():
    """Test that all required modules can be imported."""
    print("\nTesting Python imports...")
    modules = [
        ('streamlit', 'streamlit'),
        ('plotly.graph_objects', 'plotly'),
        ('sqlite3', 'built-in'),
        ('json', 'built-in'),
        ('subprocess', 'built-in')
    ]
    
    all_ok = True
    for module, package in modules:
        try:
            __import__(module)
            print(f"  [OK] {module} ({package})")
        except ImportError:
            print(f"  [ERROR] {module} not found! Install with: pip install {package}")
            all_ok = False
    
    return all_ok

def test_matching_engine():
    """Test that matching engine script exists."""
    print("\nTesting matching engine...")
    match_script = Path("scripts/match_vendors.py")
    
    if match_script.exists():
        print(f"  [OK] Matching engine found at {match_script}")
        return True
    else:
        print(f"  [ERROR] Matching engine not found at {match_script}")
        return False

def test_app_file():
    """Test that app.py exists and is readable."""
    print("\nTesting Streamlit app file...")
    app_file = Path("app.py")
    
    if not app_file.exists():
        print(f"  [ERROR] app.py not found!")
        return False
    
    try:
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for key functions
        required_functions = [
            'show_home',
            'show_match_form',
            'show_match_results',
            'show_vendor_directory',
            'show_past_results'
        ]
        
        for func in required_functions:
            if func in content:
                print(f"  [OK] Function '{func}' found")
            else:
                print(f"  [ERROR] Function '{func}' missing!")
                return False
        
        return True
    except Exception as e:
        print(f"  [ERROR] Failed to read app.py: {e}")
        return False

def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("TPA Match Demo - Streamlit App Tests")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Database Connectivity", test_database_connectivity),
        ("Data Availability", test_data_exists),
        ("Matching Engine", test_matching_engine),
        ("App File", test_app_file)
    ]
    
    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed! Ready to launch:")
        print("  streamlit run app.py")
        return True
    else:
        print("\n[WARNING] Some tests failed. Review errors above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
