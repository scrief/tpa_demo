"""
TPA Match Demo - Validation Testing Script

This script validates the matching engine against expected results.

Usage:
    python scripts/validate_matches.py                    # Run all validations
    python scripts/validate_matches.py --scenario VAL-001 # Run specific scenario
    python scripts/validate_matches.py --report           # Generate detailed report
    python scripts/validate_matches.py --verbose          # Verbose output
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
import sys

DB_PATH = Path("database/tpa_match_demo.db")
SCENARIOS_PATH = Path("data/validation_scenarios.json")


def load_validation_scenarios():
    """Load validation scenarios from JSON file."""
    if not SCENARIOS_PATH.exists():
        print(f"[ERROR] Validation scenarios not found at {SCENARIOS_PATH}")
        print("Create this file first with expected test scenarios.")
        sys.exit(1)
    
    with open(SCENARIOS_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)['scenarios']


def get_match_results(conn, buyer_request_id, top_n=10):
    """Fetch match results for a buyer request."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            m.rank,
            v.vendor_name,
            m.total_score,
            m.reason_codes,
            m.risk_flags,
            m.human_review_required
        FROM match_results m
        JOIN vendors v ON m.vendor_id = v.vendor_id
        WHERE m.buyer_request_id = ?
        ORDER BY m.rank
        LIMIT ?
    """, (buyer_request_id, top_n))
    
    results = []
    for row in cursor.fetchall():
        results.append({
            'rank': row[0],
            'vendor_name': row[1],
            'total_score': row[2],
            'reason_codes': json.loads(row[3]) if row[3] else [],
            'risk_flags': json.loads(row[4]) if row[4] else [],
            'human_review_required': bool(row[5])
        })
    return results


def validate_top_vendor(scenario, actual_results):
    """Check if expected top vendor matches actual top vendor."""
    expected = scenario.get('expected_top_vendor')
    if not expected:
        return True, "No expected top vendor specified", None
    
    if not actual_results:
        return False, "No results returned", None
    
    actual_top = actual_results[0]['vendor_name']
    passed = (actual_top == expected)
    
    if passed:
        return True, f"[PASS] Top vendor correct: {actual_top}", None
    else:
        return False, f"[FAIL] Expected: {expected}, Got: {actual_top}", {
            'expected': expected,
            'actual': actual_top
        }


def validate_top_3(scenario, actual_results):
    """Check if expected vendors appear in top 3."""
    expected_vendors = scenario.get('expected_in_top_3', [])
    if not expected_vendors:
        return True, "No expected top 3 specified", None
    
    if not actual_results:
        return False, "No results to validate", None
    
    actual_top_3 = [r['vendor_name'] for r in actual_results[:3]]
    
    found = [v for v in expected_vendors if v in actual_top_3]
    missing = [v for v in expected_vendors if v not in actual_top_3]
    
    if not missing:
        return True, f"[PASS] All expected vendors in top 3: {', '.join(found)}", None
    else:
        return False, f"[FAIL] Missing from top 3: {', '.join(missing)}", {
            'expected': expected_vendors,
            'actual': actual_top_3,
            'missing': missing
        }


def validate_ranking_order(scenario, actual_results):
    """Check if top vendors appear in expected order."""
    expected_order = scenario.get('expected_ranking_order', [])
    if not expected_order:
        return True, "No expected ranking order specified", None
    
    if not actual_results:
        return False, "No results to validate", None
    
    actual_order = [r['vendor_name'] for r in actual_results[:len(expected_order)]]
    
    if actual_order == expected_order:
        return True, f"[PASS] Ranking order correct: {' > '.join(actual_order)}", None
    else:
        return False, f"[FAIL] Expected order: {' > '.join(expected_order)}, Got: {' > '.join(actual_order)}", {
            'expected': expected_order,
            'actual': actual_order
        }


def validate_reason_codes(scenario, actual_results):
    """Check if expected reason codes are present."""
    expected_codes = scenario.get('expected_reason_codes', [])
    min_codes = scenario.get('min_reason_codes', 0)
    
    if not expected_codes and min_codes == 0:
        return True, "No expected reason codes specified", None
    
    if not actual_results:
        return False, "No results to validate", None
    
    actual_codes = actual_results[0]['reason_codes']
    
    # Check minimum number of reason codes
    if min_codes > 0 and len(actual_codes) < min_codes:
        return False, f"[FAIL] Expected at least {min_codes} reason codes, got {len(actual_codes)}", {
            'expected_min': min_codes,
            'actual_count': len(actual_codes)
        }
    
    # Check specific expected codes
    if expected_codes:
        found = [c for c in expected_codes if c in actual_codes]
        missing = [c for c in expected_codes if c not in actual_codes]
        
        if not missing:
            return True, f"[PASS] All expected reason codes present: {', '.join(found)}", None
        else:
            return False, f"[FAIL] Missing reason codes: {', '.join(missing)}", {
                'expected': expected_codes,
                'actual': actual_codes,
                'missing': missing
            }
    
    return True, f"[PASS] Has {len(actual_codes)} reason codes (min: {min_codes})", None


def validate_warning_codes(scenario, actual_results):
    """Check if expected warning/risk flags are present."""
    expected_warnings = scenario.get('expected_warning_codes', [])
    if not expected_warnings:
        return True, "No expected warning codes specified", None
    
    if not actual_results:
        return False, "No results to validate", None
    
    # Check top result for warnings
    actual_warnings = actual_results[0]['risk_flags']
    
    found = [w for w in expected_warnings if w in actual_warnings]
    missing = [w for w in expected_warnings if w not in actual_warnings]
    
    if not missing:
        return True, f"[PASS] All expected warnings present: {', '.join(found)}", None
    else:
        return False, f"[FAIL] Missing warnings: {', '.join(missing)}", {
            'expected': expected_warnings,
            'actual': actual_warnings,
            'missing': missing
        }


def validate_human_review_flag(scenario, actual_results):
    """Check if human review flag matches expectation."""
    expected_review = scenario.get('should_require_human_review')
    if expected_review is None:
        return True, "No human review expectation specified", None
    
    if not actual_results:
        return False, "No results to validate", None
    
    actual_review = actual_results[0]['human_review_required']
    
    if actual_review == expected_review:
        status = "required" if actual_review else "not required"
        return True, f"[PASS] Human review correctly {status}", None
    else:
        expected_status = "required" if expected_review else "not required"
        actual_status = "required" if actual_review else "not required"
        return False, f"[FAIL] Expected human review {expected_status}, got {actual_status}", {
            'expected': expected_review,
            'actual': actual_review
        }


def validate_score_range(scenario, actual_results):
    """Check if score is within expected range."""
    score_range = scenario.get('expected_score_range')
    if not score_range:
        return True, "No expected score range specified", None
    
    if not actual_results:
        return False, "No results to validate", None
    
    actual_score = actual_results[0]['total_score']
    min_score = score_range.get('min', 0)
    max_score = score_range.get('max', 100)
    
    if min_score <= actual_score <= max_score:
        return True, f"[PASS] Score {actual_score:.1f} in expected range [{min_score:.1f}, {max_score:.1f}]", None
    else:
        return False, f"[FAIL] Score {actual_score:.1f} outside expected range [{min_score:.1f}, {max_score:.1f}]", {
            'expected_range': score_range,
            'actual_score': actual_score
        }


def validate_vendor_exclusion(scenario, actual_results):
    """Check that excluded vendor does not appear in results."""
    excluded_vendor = scenario.get('vendor_must_not_appear')
    if not excluded_vendor:
        return True, "No vendor exclusion specified", None
    
    if not actual_results:
        return True, "No results (vendor correctly not present)", None
    
    vendor_names = [r['vendor_name'] for r in actual_results]
    
    if excluded_vendor in vendor_names:
        return False, f"[FAIL] Excluded vendor '{excluded_vendor}' appears in results", {
            'excluded_vendor': excluded_vendor,
            'appeared_at_rank': vendor_names.index(excluded_vendor) + 1
        }
    else:
        return True, f"[PASS] Excluded vendor '{excluded_vendor}' correctly not in results", None


def validate_aggregate_human_review_flags(conn):
    """Validate that all low-scoring matches have human review flags."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            COUNT(*) as total_low_scores,
            SUM(CASE WHEN human_review_required = 1 THEN 1 ELSE 0 END) as flagged
        FROM match_results
        WHERE total_score < 70 AND rank = 1
    """)
    
    total, flagged = cursor.fetchone()
    
    if total == 0:
        return True, "No low-scoring matches to validate", None
    
    if total == flagged:
        return True, f"[PASS] All {total} low-scoring matches (<70) have human review flags", None
    else:
        return False, f"[FAIL] {total - flagged} of {total} low-scoring matches missing human review flag", {
            'total_low_scores': total,
            'flagged': flagged,
            'missing_flags': total - flagged
        }


def validate_all_buyers_have_results(conn):
    """Validate that all buyers have at least one match result."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(DISTINCT buyer_request_id) FROM buyer_requests
    """)
    total_buyers = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(DISTINCT buyer_request_id) FROM match_results
    """)
    buyers_with_results = cursor.fetchone()[0]
    
    if total_buyers == buyers_with_results:
        return True, f"[PASS] All {total_buyers} buyers have match results", None
    else:
        return False, f"[FAIL] {total_buyers - buyers_with_results} of {total_buyers} buyers have no match results", {
            'total_buyers': total_buyers,
            'buyers_with_results': buyers_with_results
        }


def validate_no_duplicate_ranks(conn):
    """Validate that each buyer has unique rank values."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            buyer_request_id,
            COUNT(*) as total_results,
            COUNT(DISTINCT rank) as unique_ranks
        FROM match_results
        GROUP BY buyer_request_id
        HAVING total_results != unique_ranks
    """)
    
    duplicates = cursor.fetchall()
    
    if not duplicates:
        return True, "[PASS] All buyers have unique rank values (no duplicates)", None
    else:
        buyer_ids = [d[0] for d in duplicates]
        return False, f"[FAIL] Buyers {buyer_ids} have duplicate rank values", {
            'buyers_with_duplicates': buyer_ids
        }


def check_for_hallucination(actual_results):
    """
    Check for potential hallucinated capabilities.
    
    This is a placeholder for future AI explanation validation.
    For now, just verify reason codes reference actual data.
    """
    # For Phase 7, just return pass
    # This will be important for Phase 9 when AI generates explanations
    return True, "No hallucination detection (deterministic engine)", None


def save_validation_result(conn, scenario, validation_results, overall_pass):
    """Save validation result to database."""
    cursor = conn.cursor()
    
    scenario_id = scenario.get('scenario_id', 'UNKNOWN')
    scenario_name = scenario['scenario_name']
    buyer_request_id = scenario.get('buyer_request_id')
    
    # Get actual top vendors if buyer_request_id exists
    actual_top_vendors = []
    if buyer_request_id:
        cursor.execute("""
            SELECT v.vendor_name
            FROM match_results m
            JOIN vendors v ON m.vendor_id = v.vendor_id
            WHERE m.buyer_request_id = ?
            ORDER BY m.rank
            LIMIT 3
        """, (buyer_request_id,))
        actual_top_vendors = [row[0] for row in cursor.fetchall()]
    
    # Prepare expected vendors
    expected_good = scenario.get('expected_in_top_3', [])
    expected_top = scenario.get('expected_top_vendor')
    if expected_top and not expected_good:
        expected_good = [expected_top]
    
    # Save to validation_results table
    cursor.execute("""
        INSERT INTO validation_results (
            scenario_name,
            buyer_request_id,
            expected_good_vendors,
            actual_top_vendors,
            top_match_pass,
            explanation_pass,
            hallucination_detected,
            notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        f"{scenario_id}: {scenario_name}",
        buyer_request_id,
        json.dumps(expected_good) if expected_good else None,
        json.dumps(actual_top_vendors) if actual_top_vendors else None,
        1 if overall_pass else 0,
        1,  # explanation_pass (not tested in Phase 7)
        0,  # hallucination_detected (deterministic engine)
        json.dumps(validation_results)
    ))
    
    conn.commit()


def run_validation(scenario, conn, verbose=True):
    """Run validation for a single scenario."""
    scenario_id = scenario['scenario_id']
    scenario_name = scenario['scenario_name']
    category = scenario.get('category', 'general')
    test_type = scenario.get('test_type', 'standard')
    
    if verbose:
        print(f"\n{'='*80}")
        print(f"Validating: {scenario_id} - {scenario_name}")
        print(f"Category: {category}")
        print(f"{'='*80}")
    
    # Handle aggregate tests
    if test_type == 'aggregate':
        checks = []
        
        if category == 'human_review':
            passed, msg, details = validate_aggregate_human_review_flags(conn)
            checks.append({'check': 'aggregate_human_review', 'passed': passed, 'message': msg, 'details': details})
            if verbose:
                print(f"  {msg}")
        
        elif category == 'data_completeness':
            if 'All buyers have match results' in scenario_name:
                passed, msg, details = validate_all_buyers_have_results(conn)
                checks.append({'check': 'all_buyers_have_results', 'passed': passed, 'message': msg, 'details': details})
                if verbose:
                    print(f"  {msg}")
            
            elif 'No duplicate ranks' in scenario_name:
                passed, msg, details = validate_no_duplicate_ranks(conn)
                checks.append({'check': 'no_duplicate_ranks', 'passed': passed, 'message': msg, 'details': details})
                if verbose:
                    print(f"  {msg}")
        
        overall_pass = all(check['passed'] for check in checks)
        
        if verbose:
            print(f"\n  Overall: {'[PASS] PASS' if overall_pass else '[FAIL] FAIL'}")
        
        save_validation_result(conn, scenario, checks, overall_pass)
        return overall_pass, checks
    
    # Standard scenario validation
    buyer_request_id = scenario.get('buyer_request_id')
    if not buyer_request_id:
        print(f"[ERROR] No buyer_request_id specified for scenario {scenario_id}")
        return False, []
    
    # Get actual match results
    actual_results = get_match_results(conn, buyer_request_id)
    
    if not actual_results:
        print(f"[ERROR] No match results found for buyer_request_id {buyer_request_id}")
        print(f"        Run: python scripts/match_vendors.py {buyer_request_id}")
        return False, []
    
    # Run all validation checks
    checks = []
    
    # 1. Top vendor check
    passed, msg, details = validate_top_vendor(scenario, actual_results)
    checks.append({'check': 'top_vendor', 'passed': passed, 'message': msg, 'details': details})
    if verbose:
        print(f"  {msg}")
    
    # 2. Top 3 vendors check
    passed, msg, details = validate_top_3(scenario, actual_results)
    checks.append({'check': 'top_3', 'passed': passed, 'message': msg, 'details': details})
    if verbose:
        print(f"  {msg}")
    
    # 3. Ranking order check
    passed, msg, details = validate_ranking_order(scenario, actual_results)
    checks.append({'check': 'ranking_order', 'passed': passed, 'message': msg, 'details': details})
    if verbose:
        print(f"  {msg}")
    
    # 4. Reason codes check
    passed, msg, details = validate_reason_codes(scenario, actual_results)
    checks.append({'check': 'reason_codes', 'passed': passed, 'message': msg, 'details': details})
    if verbose:
        print(f"  {msg}")
    
    # 5. Warning codes check
    passed, msg, details = validate_warning_codes(scenario, actual_results)
    checks.append({'check': 'warning_codes', 'passed': passed, 'message': msg, 'details': details})
    if verbose:
        print(f"  {msg}")
    
    # 6. Human review flag check
    passed, msg, details = validate_human_review_flag(scenario, actual_results)
    checks.append({'check': 'human_review', 'passed': passed, 'message': msg, 'details': details})
    if verbose:
        print(f"  {msg}")
    
    # 7. Score range check
    passed, msg, details = validate_score_range(scenario, actual_results)
    checks.append({'check': 'score_range', 'passed': passed, 'message': msg, 'details': details})
    if verbose:
        print(f"  {msg}")
    
    # 8. Vendor exclusion check
    passed, msg, details = validate_vendor_exclusion(scenario, actual_results)
    checks.append({'check': 'vendor_exclusion', 'passed': passed, 'message': msg, 'details': details})
    if verbose:
        print(f"  {msg}")
    
    # 9. Hallucination check
    passed, msg, details = check_for_hallucination(actual_results)
    checks.append({'check': 'hallucination', 'passed': passed, 'message': msg, 'details': details})
    if verbose:
        print(f"  {msg}")
    
    # Determine overall pass/fail
    # Only count checks that were actually tested (not skipped)
    tested_checks = [c for c in checks if "No expected" not in c['message'] and "not specified" not in c['message']]
    if tested_checks:
        overall_pass = all(check['passed'] for check in tested_checks)
    else:
        overall_pass = True  # If nothing was tested, consider it a pass
    
    if verbose:
        print(f"\n  Overall: {'[PASS] PASS' if overall_pass else '[FAIL] FAIL'}")
        print(f"  Actual score: {actual_results[0]['total_score']:.1f}")
    
    # Save result to database
    save_validation_result(conn, scenario, checks, overall_pass)
    
    return overall_pass, checks


def generate_validation_report(conn):
    """Generate summary validation report."""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(top_match_pass) as passed,
            SUM(CASE WHEN top_match_pass = 0 THEN 1 ELSE 0 END) as failed
        FROM validation_results
    """)
    
    row = cursor.fetchone()
    if not row or row[0] == 0:
        print("\n[WARNING] No validation results found in database.")
        print("          Run validation scenarios first.")
        return
    
    total, passed, failed = row
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    print("\n" + "="*80)
    print("VALIDATION SUMMARY REPORT")
    print("="*80)
    print(f"Total scenarios tested: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Pass rate: {pass_rate:.1f}%")
    print()
    
    # Get failed scenarios
    cursor.execute("""
        SELECT scenario_name, notes
        FROM validation_results
        WHERE top_match_pass = 0
        ORDER BY created_at DESC
    """)
    
    failed_scenarios = cursor.fetchall()
    
    if failed_scenarios:
        print("Failed scenarios:")
        for name, notes in failed_scenarios:
            print(f"  - {name}")
            if notes:
                try:
                    checks = json.loads(notes)
                    failed_checks = [c for c in checks if not c.get('passed', True)]
                    for check in failed_checks:
                        print(f"    {check.get('message', 'Unknown failure')}")
                except:
                    pass
        print()
    else:
        print("[PASS] All scenarios passed!")
        print()
    
    # Category breakdown
    cursor.execute("""
        SELECT 
            SUBSTR(scenario_name, 1, INSTR(scenario_name, ':') - 1) as category,
            COUNT(*) as total,
            SUM(top_match_pass) as passed
        FROM validation_results
        GROUP BY SUBSTR(scenario_name, 1, INSTR(scenario_name, ':') - 1)
        ORDER BY category
    """)
    
    print("Results by category:")
    for category, cat_total, cat_passed in cursor.fetchall():
        cat_pass_rate = (cat_passed / cat_total * 100) if cat_total > 0 else 0
        print(f"  {category:20} {cat_passed:2}/{cat_total:2} ({cat_pass_rate:5.1f}%)")
    
    print("\n" + "="*80)


def main():
    """Main entry point."""
    # Parse arguments
    run_all = True
    specific_scenario = None
    generate_report = False
    verbose = True
    
    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv[1:]):
            if arg == '--scenario' and i + 2 < len(sys.argv):
                run_all = False
                specific_scenario = sys.argv[i + 2]
            elif arg == '--report':
                generate_report = True
                run_all = False
            elif arg == '--verbose':
                verbose = True
            elif arg == '--quiet':
                verbose = False
    
    if not DB_PATH.exists():
        print(f"[ERROR] Database not found at {DB_PATH}")
        print("Run: python scripts/create_database.py")
        return
    
    conn = sqlite3.connect(DB_PATH)
    
    if generate_report:
        generate_validation_report(conn)
        conn.close()
        return
    
    # Load scenarios
    scenarios = load_validation_scenarios()
    
    if specific_scenario:
        scenarios = [s for s in scenarios if s['scenario_id'] == specific_scenario]
        if not scenarios:
            print(f"[ERROR] Scenario {specific_scenario} not found")
            conn.close()
            return
    
    print(f"\nRunning validation for {len(scenarios)} scenario(s)...")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    for scenario in scenarios:
        try:
            passed, checks = run_validation(scenario, conn, verbose=verbose)
            results.append({
                'scenario': scenario['scenario_id'],
                'passed': passed,
                'checks': checks
            })
        except Exception as e:
            print(f"\n[ERROR] Exception in scenario {scenario.get('scenario_id', 'UNKNOWN')}: {str(e)}")
            results.append({
                'scenario': scenario.get('scenario_id', 'UNKNOWN'),
                'passed': False,
                'checks': [{'check': 'exception', 'passed': False, 'message': str(e)}]
            })
    
    # Summary
    total = len(results)
    passed_count = sum(1 for r in results if r['passed'])
    failed_count = total - passed_count
    
    print("\n" + "="*80)
    print("VALIDATION COMPLETE")
    print("="*80)
    print(f"Total scenarios: {total}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {failed_count}")
    print(f"Pass rate: {(passed_count/total*100):.1f}%")
    print()
    
    if failed_count > 0:
        print("Failed scenarios:")
        for r in results:
            if not r['passed']:
                print(f"  - {r['scenario']}")
        print()
    
    # Pass rate assessment
    pass_rate = (passed_count / total * 100) if total > 0 else 0
    if pass_rate >= 90:
        print("[PASS] Excellent! Pass rate >= 90%")
    elif pass_rate >= 80:
        print("[PASS] Good! Pass rate >= 80%")
    else:
        print("[WARNING] Pass rate below 80% - review and adjust matching logic or expectations")
    
    print("\nResults saved to validation_results table")
    print("Run with --report flag to view detailed report")
    
    conn.close()


if __name__ == "__main__":
    main()
