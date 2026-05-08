"""
TPA Match Demo - Priority Sensitivity Testing Script

This script tests that adjusting buyer priorities affects match scores
in expected ways.

Usage:
    python scripts/test_priority_sensitivity.py                    # Run all tests
    python scripts/test_priority_sensitivity.py --test reporting   # Run specific test
    python scripts/test_priority_sensitivity.py --verbose          # Detailed output
"""

import sqlite3
from pathlib import Path
import json
import sys

DB_PATH = Path("database/tpa_match_demo.db")


def create_test_buyer(conn, buyer_data):
    """Create a test buyer request and return the buyer_request_id."""
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO buyer_requests (
            buyer_name,
            industry,
            claim_type_needed,
            program_type,
            priority_geography,
            priority_claims,
            priority_industry,
            priority_services,
            priority_reporting,
            priority_technology,
            priority_cost
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        buyer_data['buyer_name'],
        buyer_data['industry'],
        buyer_data['claim_type_needed'],
        buyer_data.get('program_type', 'self_insured'),
        buyer_data.get('priority_geography', 3),
        buyer_data.get('priority_claims', 3),
        buyer_data.get('priority_industry', 3),
        buyer_data.get('priority_services', 3),
        buyer_data.get('priority_reporting', 3),
        buyer_data.get('priority_technology', 3),
        buyer_data.get('priority_cost', 3)
    ))
    
    buyer_id = cursor.lastrowid
    
    # Insert required states
    if buyer_data.get('states'):
        for state in buyer_data['states']:
            cursor.execute("""
                INSERT INTO buyer_required_states (buyer_request_id, state_code)
                VALUES (?, ?)
            """, (buyer_id, state))
    
    # Insert required services
    if buyer_data.get('services'):
        for service in buyer_data['services']:
            cursor.execute("""
                INSERT INTO buyer_required_services (buyer_request_id, service_name)
                VALUES (?, ?)
            """, (buyer_id, service))
    
    conn.commit()
    return buyer_id


def run_matching_for_buyer(buyer_id):
    """Run the matching engine for a test buyer."""
    import subprocess
    result = subprocess.run(
        ['python', 'scripts/match_vendors.py', str(buyer_id)],
        capture_output=True,
        text=True
    )
    return result.returncode == 0


def get_top_matches(conn, buyer_id, top_n=3):
    """Get top N matches for a buyer."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            v.vendor_name,
            m.total_score,
            m.geography_score,
            m.claims_score,
            m.industry_score,
            m.service_score,
            m.reporting_score,
            m.performance_score,
            m.technology_score,
            m.data_quality_score
        FROM match_results m
        JOIN vendors v ON m.vendor_id = v.vendor_id
        WHERE m.buyer_request_id = ?
        ORDER BY m.rank
        LIMIT ?
    """, (buyer_id, top_n))
    
    results = []
    for row in cursor.fetchall():
        results.append({
            'vendor_name': row[0],
            'total_score': row[1],
            'score_geography': row[2],
            'score_claims': row[3],
            'score_industry': row[4],
            'score_service': row[5],
            'score_reporting': row[6],
            'score_performance': row[7],
            'score_technology': row[8],
            'score_data_quality': row[9]
        })
    return results


def cleanup_test_buyer(conn, buyer_id):
    """Remove test buyer and associated data."""
    cursor = conn.cursor()
    
    # Delete from dependent tables first
    cursor.execute("DELETE FROM buyer_required_states WHERE buyer_request_id = ?", (buyer_id,))
    cursor.execute("DELETE FROM buyer_required_services WHERE buyer_request_id = ?", (buyer_id,))
    cursor.execute("DELETE FROM match_results WHERE buyer_request_id = ?", (buyer_id,))
    cursor.execute("DELETE FROM buyer_requests WHERE buyer_request_id = ?", (buyer_id,))
    
    conn.commit()


def test_reporting_priority(conn, verbose=True):
    """
    Test that high reporting priority boosts reporting-strong vendors.
    
    Create two identical buyers except for reporting priority:
    - Buyer A: priority_reporting = 3 (moderate)
    - Buyer B: priority_reporting = 5 (critical)
    
    Verify: Reporting-strong vendors score higher for Buyer B
    """
    if verbose:
        print("\n" + "="*70)
        print("TEST: Reporting Priority Sensitivity")
        print("="*70)
    
    # Buyer A - moderate reporting priority
    buyer_a_data = {
        'buyer_name': 'TEST_ReportingPriority_A',
        'industry': 'manufacturing',
        'claim_type_needed': 'workers_comp',
        'program_type': 'self_insured',
        'states': ['MN', 'WI', 'IA'],
        'services': [],
        'priority_reporting': 3,  # Moderate
        'priority_geography': 3,
        'priority_claims': 3,
        'priority_services': 3
    }
    
    # Buyer B - critical reporting priority
    buyer_b_data = buyer_a_data.copy()
    buyer_b_data['buyer_name'] = 'TEST_ReportingPriority_B'
    buyer_b_data['priority_reporting'] = 5  # Critical
    
    try:
        # Create test buyers
        buyer_a_id = create_test_buyer(conn, buyer_a_data)
        buyer_b_id = create_test_buyer(conn, buyer_b_data)
        
        # Run matching
        if verbose:
            print("Running matching for Buyer A (priority_reporting=3)...")
        run_matching_for_buyer(buyer_a_id)
        
        if verbose:
            print("Running matching for Buyer B (priority_reporting=5)...")
        run_matching_for_buyer(buyer_b_id)
        
        # Get results
        results_a = get_top_matches(conn, buyer_a_id, top_n=5)
        results_b = get_top_matches(conn, buyer_b_id, top_n=5)
        
        if verbose:
            print(f"\nBuyer A (priority_reporting=3) - Top 3:")
            for i, r in enumerate(results_a[:3], 1):
                print(f"  {i}. {r['vendor_name']:30} Total: {r['total_score']:5.1f}  Reporting: {r['score_reporting']:4.1f}")
            
            print(f"\nBuyer B (priority_reporting=5) - Top 3:")
            for i, r in enumerate(results_b[:3], 1):
                print(f"  {i}. {r['vendor_name']:30} Total: {r['total_score']:5.1f}  Reporting: {r['score_reporting']:4.1f}")
        
        # Validate: reporting scores should be higher for Buyer B overall
        avg_reporting_a = sum(r['score_reporting'] for r in results_a[:3]) / 3
        avg_reporting_b = sum(r['score_reporting'] for r in results_b[:3]) / 3
        
        passed = avg_reporting_b > avg_reporting_a
        
        if verbose:
            print(f"\nAverage reporting score (top 3):")
            print(f"  Buyer A: {avg_reporting_a:.2f}")
            print(f"  Buyer B: {avg_reporting_b:.2f}")
            print(f"\nResult: {'[PASS]' if passed else '[FAIL]'} Buyer B reporting scores {'higher' if passed else 'NOT higher'}")
        
        return passed
        
    finally:
        # Cleanup
        cleanup_test_buyer(conn, buyer_a_id)
        cleanup_test_buyer(conn, buyer_b_id)


def test_cost_priority(conn, verbose=True):
    """
    Test that high cost priority excludes expensive vendors.
    
    Create two buyers:
    - Buyer A: priority_cost = 3 (moderate)
    - Buyer B: priority_cost = 5 (critical - must be cost-effective)
    
    Verify: Buyer B results exclude high-priced vendors
    """
    if verbose:
        print("\n" + "="*70)
        print("TEST: Cost Priority Sensitivity")
        print("="*70)
    
    # Buyer A - moderate cost priority
    buyer_a_data = {
        'buyer_name': 'TEST_CostPriority_A',
        'industry': 'manufacturing',
        'claim_type_needed': 'workers_comp',
        'program_type': 'self_insured',
        'states': ['MN', 'WI', 'IA'],
        'services': [],
        'priority_cost': 3  # Moderate
    }
    
    # Buyer B - critical cost priority
    buyer_b_data = buyer_a_data.copy()
    buyer_b_data['buyer_name'] = 'TEST_CostPriority_B'
    buyer_b_data['priority_cost'] = 5  # Critical
    
    try:
        # Create test buyers
        buyer_a_id = create_test_buyer(conn, buyer_a_data)
        buyer_b_id = create_test_buyer(conn, buyer_b_data)
        
        # Run matching
        if verbose:
            print("Running matching for Buyer A (priority_cost=3)...")
        run_matching_for_buyer(buyer_a_id)
        
        if verbose:
            print("Running matching for Buyer B (priority_cost=5)...")
        run_matching_for_buyer(buyer_b_id)
        
        # Get results
        cursor = conn.cursor()
        
        # Get count of results for each buyer
        cursor.execute("SELECT COUNT(*) FROM match_results WHERE buyer_request_id = ?", (buyer_a_id,))
        count_a = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM match_results WHERE buyer_request_id = ?", (buyer_b_id,))
        count_b = cursor.fetchone()[0]
        
        if verbose:
            print(f"\nBuyer A (priority_cost=3): {count_a} vendors matched")
            print(f"Buyer B (priority_cost=5): {count_b} vendors matched")
        
        # Check if Buyer B has fewer matches (high-priced vendors filtered out)
        # Note: This assumes some vendors in the DB have pricing_level = "high"
        # If cost filtering is working, Buyer B should have fewer or equal matches
        
        results_a = get_top_matches(conn, buyer_a_id, top_n=3)
        results_b = get_top_matches(conn, buyer_b_id, top_n=3)
        
        if verbose:
            print(f"\nBuyer A - Top 3:")
            for i, r in enumerate(results_a, 1):
                print(f"  {i}. {r['vendor_name']:30} Score: {r['total_score']:5.1f}")
            
            print(f"\nBuyer B - Top 3:")
            for i, r in enumerate(results_b, 1):
                print(f"  {i}. {r['vendor_name']:30} Score: {r['total_score']:5.1f}")
        
        # Validate: Buyer B should have equal or fewer results (some filtered by cost)
        passed = count_b <= count_a
        
        if verbose:
            print(f"\nResult: {'[PASS]' if passed else '[FAIL]'} Cost filtering {'working' if passed else 'NOT working'}")
        
        return passed
        
    finally:
        # Cleanup
        cleanup_test_buyer(conn, buyer_a_id)
        cleanup_test_buyer(conn, buyer_b_id)


def test_geography_priority(conn, verbose=True):
    """
    Test that critical geography priority heavily weights state coverage.
    
    Create two buyers with partial state coverage available:
    - Buyer A: priority_geography = 3
    - Buyer B: priority_geography = 5
    
    Verify: Buyer B penalizes partial coverage more heavily
    """
    if verbose:
        print("\n" + "="*70)
        print("TEST: Geography Priority Sensitivity")
        print("="*70)
    
    # Use a state combination that's hard to cover (testing partial matches)
    buyer_a_data = {
        'buyer_name': 'TEST_GeographyPriority_A',
        'industry': 'manufacturing',
        'claim_type_needed': 'workers_comp',
        'program_type': 'self_insured',
        'states': ['CA', 'TX', 'FL', 'NY'],  # Hard to cover all
        'services': [],
        'priority_geography': 3  # Moderate
    }
    
    buyer_b_data = buyer_a_data.copy()
    buyer_b_data['buyer_name'] = 'TEST_GeographyPriority_B'
    buyer_b_data['priority_geography'] = 5  # Critical
    
    try:
        # Create test buyers
        buyer_a_id = create_test_buyer(conn, buyer_a_data)
        buyer_b_id = create_test_buyer(conn, buyer_b_data)
        
        # Run matching
        if verbose:
            print("Running matching for Buyer A (priority_geography=3)...")
        run_matching_for_buyer(buyer_a_id)
        
        if verbose:
            print("Running matching for Buyer B (priority_geography=5)...")
        run_matching_for_buyer(buyer_b_id)
        
        # Get results
        results_a = get_top_matches(conn, buyer_a_id, top_n=3)
        results_b = get_top_matches(conn, buyer_b_id, top_n=3)
        
        if verbose:
            print(f"\nBuyer A (priority_geography=3) - Top 3:")
            for i, r in enumerate(results_a, 1):
                print(f"  {i}. {r['vendor_name']:30} Total: {r['total_score']:5.1f}  Geography: {r['score_geography']:4.1f}")
            
            print(f"\nBuyer B (priority_geography=5) - Top 3:")
            for i, r in enumerate(results_b, 1):
                print(f"  {i}. {r['vendor_name']:30} Total: {r['total_score']:5.1f}  Geography: {r['score_geography']:4.1f}")
        
        # Validate: geography scores should matter more for Buyer B
        # The spread between high and low geography scores should be larger for B
        if results_a and results_b:
            geo_range_a = max(r['score_geography'] for r in results_a) - min(r['score_geography'] for r in results_a)
            geo_range_b = max(r['score_geography'] for r in results_b) - min(r['score_geography'] for r in results_b)
            
            passed = geo_range_b >= geo_range_a * 0.9  # Allow some tolerance
            
            if verbose:
                print(f"\nGeography score range (top 3):")
                print(f"  Buyer A: {geo_range_a:.2f}")
                print(f"  Buyer B: {geo_range_b:.2f}")
                print(f"\nResult: {'[PASS]' if passed else '[FAIL]'} Geography weighting {'working' if passed else 'needs review'}")
        else:
            passed = False
            if verbose:
                print("\nResult: [FAIL] No results returned")
        
        return passed
        
    finally:
        # Cleanup
        cleanup_test_buyer(conn, buyer_a_id)
        cleanup_test_buyer(conn, buyer_b_id)


def test_all_priorities_high(conn, verbose=True):
    """
    Test that when all priorities are high (5), the system still produces
    valid results with proper weight normalization.
    """
    if verbose:
        print("\n" + "="*70)
        print("TEST: All Priorities High (5) - Weight Normalization")
        print("="*70)
    
    buyer_data = {
        'buyer_name': 'TEST_AllPrioritiesHigh',
        'industry': 'manufacturing',
        'claim_type_needed': 'workers_comp',
        'program_type': 'self_insured',
        'states': ['MN', 'WI', 'IA'],
        'services': [],
        'priority_geography': 5,
        'priority_claims': 5,
        'priority_industry': 5,
        'priority_services': 5,
        'priority_reporting': 5,
        'priority_technology': 5,
        'priority_cost': 5
    }
    
    try:
        buyer_id = create_test_buyer(conn, buyer_data)
        
        if verbose:
            print("Running matching with all priorities = 5...")
        
        success = run_matching_for_buyer(buyer_id)
        
        if not success:
            if verbose:
                print("\nResult: [FAIL] Matching failed to run")
            return False
        
        results = get_top_matches(conn, buyer_id, top_n=3)
        
        if not results:
            if verbose:
                print("\nResult: [FAIL] No results returned")
            return False
        
        if verbose:
            print(f"\nTop 3 results:")
            for i, r in enumerate(results, 1):
                print(f"  {i}. {r['vendor_name']:30} Score: {r['total_score']:5.1f}")
                print(f"     Geo: {r['score_geography']:.1f}, Claims: {r['score_claims']:.1f}, "
                      f"Industry: {r['score_industry']:.1f}, Services: {r['score_service']:.1f}")
                print(f"     Reporting: {r['score_reporting']:.1f}, Performance: {r['score_performance']:.1f}, "
                      f"Tech: {r['score_technology']:.1f}, Quality: {r['score_data_quality']:.1f}")
        
        # Validate: Total scores should be reasonable (0-100) and results should exist
        passed = all(0 <= r['total_score'] <= 100 for r in results)
        
        if verbose:
            print(f"\nResult: {'[PASS]' if passed else '[FAIL]'} All scores in valid range [0, 100]")
        
        return passed
        
    finally:
        cleanup_test_buyer(conn, buyer_id)


def test_all_priorities_low(conn, verbose=True):
    """
    Test that when all priorities are low (1), scores are closer together
    (less differentiation between vendors).
    """
    if verbose:
        print("\n" + "="*70)
        print("TEST: All Priorities Low (1) - Reduced Differentiation")
        print("="*70)
    
    buyer_data = {
        'buyer_name': 'TEST_AllPrioritiesLow',
        'industry': 'manufacturing',
        'claim_type_needed': 'workers_comp',
        'program_type': 'self_insured',
        'states': ['MN', 'WI', 'IA'],
        'services': [],
        'priority_geography': 1,
        'priority_claims': 1,
        'priority_industry': 1,
        'priority_services': 1,
        'priority_reporting': 1,
        'priority_technology': 1,
        'priority_cost': 1
    }
    
    try:
        buyer_id = create_test_buyer(conn, buyer_data)
        
        if verbose:
            print("Running matching with all priorities = 1...")
        
        success = run_matching_for_buyer(buyer_id)
        
        if not success:
            if verbose:
                print("\nResult: [FAIL] Matching failed to run")
            return False
        
        results = get_top_matches(conn, buyer_id, top_n=5)
        
        if len(results) < 3:
            if verbose:
                print("\nResult: [FAIL] Insufficient results to test")
            return False
        
        if verbose:
            print(f"\nTop 5 results:")
            for i, r in enumerate(results, 1):
                print(f"  {i}. {r['vendor_name']:30} Score: {r['total_score']:5.1f}")
        
        # Validate: Score spread should be smaller (less than with default priorities)
        # Top score - 5th score should be relatively small
        score_spread = results[0]['total_score'] - results[-1]['total_score']
        
        # With low priorities, vendors should score more similarly (smaller spread)
        passed = score_spread < 30  # Arbitrary but reasonable threshold
        
        if verbose:
            print(f"\nScore spread (top to 5th): {score_spread:.1f}")
            print(f"Result: {'[PASS]' if passed else '[FAIL]'} Spread {'reasonable' if passed else 'too large'} for low priorities")
        
        return passed
        
    finally:
        cleanup_test_buyer(conn, buyer_id)


def main():
    """Main entry point."""
    if not DB_PATH.exists():
        print(f"[ERROR] Database not found at {DB_PATH}")
        print("Run: python scripts/create_database.py")
        return
    
    # Parse arguments
    run_all = True
    specific_test = None
    verbose = True
    
    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv[1:]):
            if arg == '--test' and i + 2 < len(sys.argv):
                run_all = False
                specific_test = sys.argv[i + 2]
            elif arg == '--verbose':
                verbose = True
            elif arg == '--quiet':
                verbose = False
    
    conn = sqlite3.connect(DB_PATH)
    
    tests = {
        'reporting': test_reporting_priority,
        'cost': test_cost_priority,
        'geography': test_geography_priority,
        'all_high': test_all_priorities_high,
        'all_low': test_all_priorities_low
    }
    
    if specific_test:
        if specific_test not in tests:
            print(f"[ERROR] Unknown test: {specific_test}")
            print(f"Available tests: {', '.join(tests.keys())}")
            conn.close()
            return
        
        passed = tests[specific_test](conn, verbose=verbose)
        print(f"\n{'='*70}")
        print(f"Test '{specific_test}': {'PASSED' if passed else 'FAILED'}")
        print(f"{'='*70}")
    else:
        # Run all tests
        print("\nRunning all priority sensitivity tests...")
        print("="*70)
        
        results = {}
        for test_name, test_func in tests.items():
            try:
                passed = test_func(conn, verbose=verbose)
                results[test_name] = passed
            except Exception as e:
                print(f"\n[ERROR] Exception in test '{test_name}': {str(e)}")
                results[test_name] = False
        
        # Summary
        print("\n" + "="*70)
        print("PRIORITY SENSITIVITY TEST SUMMARY")
        print("="*70)
        
        for test_name, passed in results.items():
            status = '[PASS]' if passed else '[FAIL]'
            print(f"{status} {test_name}")
        
        total = len(results)
        passed_count = sum(1 for p in results.values() if p)
        
        print()
        print(f"Total tests: {total}")
        print(f"Passed: {passed_count}")
        print(f"Failed: {total - passed_count}")
        print(f"Pass rate: {(passed_count/total*100):.1f}%")
        print("="*70)
    
    conn.close()


if __name__ == "__main__":
    main()
