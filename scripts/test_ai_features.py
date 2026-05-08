"""
Phase 9 - AI Features Test Suite
Comprehensive tests for all AI features: parsing, explanations, hallucinations, follow-ups.
"""

import sys
import json
from pathlib import Path
import sqlite3

# Add scripts to path
sys.path.append(str(Path(__file__).parent))

from parse_narrative_request import parse_narrative_request
from generate_explanation import generate_explanation
from detect_hallucinations import detect_hallucinations
from generate_followup_questions import generate_followup_from_buyer_id

DB_PATH = Path("database/tpa_match_demo.db")
TEST_DATA_PATH = Path("data/ai_test_cases.json")


class AIFeaturesTester:
    """Test suite for Phase 9 AI features."""
    
    def __init__(self):
        """Initialize tester."""
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []
    
    def run_all_tests(self, test_type=None):
        """Run all tests or specific test type."""
        print("=" * 60)
        print("Phase 9 AI Features Test Suite")
        print("=" * 60)
        print()
        
        # Load test data
        if not TEST_DATA_PATH.exists():
            print(f"[ERROR] Test data file not found: {TEST_DATA_PATH}")
            return False
        
        with open(TEST_DATA_PATH, 'r') as f:
            test_data = json.load(f)
        
        # Run tests based on type
        if test_type is None or test_type == 'parsing':
            self.test_narrative_parsing(test_data.get('parsing_tests', []))
        
        if test_type is None or test_type == 'explanations':
            self.test_explanation_generation(test_data.get('explanation_tests', []))
        
        if test_type is None or test_type == 'hallucinations':
            self.test_hallucination_detection(test_data.get('hallucination_tests', []))
        
        if test_type is None or test_type == 'followups':
            self.test_followup_questions()
        
        # Print summary
        self.print_summary()
        
        return self.tests_failed == 0
    
    def test_narrative_parsing(self, test_cases):
        """Test natural language parsing."""
        print("\n" + "=" * 60)
        print("Test 1: Natural Language Parsing")
        print("=" * 60)
        
        if not test_cases:
            print("[SKIP] No test cases provided")
            return
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n[Test {i}] {test.get('description', 'No description')}")
            print(f"Input: {test['input'][:80]}...")
            
            try:
                result = parse_narrative_request(test['input'])
                
                if 'error' in result:
                    self._record_failure(f"Parsing test {i}", f"Error: {result['error']}")
                    continue
                
                # Check expected fields
                expected = test.get('expected', {})
                passed = True
                
                for field, expected_value in expected.items():
                    actual_value = result.get(field)
                    
                    # Special handling for lists and sets
                    if isinstance(expected_value, list):
                        if set(actual_value or []) != set(expected_value):
                            print(f"  [FAIL] {field}: expected {expected_value}, got {actual_value}")
                            passed = False
                        else:
                            print(f"  [PASS] {field}: {actual_value}")
                    else:
                        if actual_value != expected_value:
                            print(f"  [FAIL] {field}: expected {expected_value}, got {actual_value}")
                            passed = False
                        else:
                            print(f"  [PASS] {field}: {actual_value}")
                
                # Check confidence threshold
                confidence = result.get('confidence_score', 0)
                min_confidence = test.get('min_confidence', 0.7)
                
                if confidence < min_confidence:
                    print(f"  [WARN] Confidence {confidence:.2f} below threshold {min_confidence}")
                    passed = False
                else:
                    print(f"  [PASS] Confidence: {confidence:.2f}")
                
                if passed:
                    self._record_success(f"Parsing test {i}")
                else:
                    self._record_failure(f"Parsing test {i}", "Field mismatch or low confidence")
                    
            except Exception as e:
                self._record_failure(f"Parsing test {i}", str(e))
    
    def test_explanation_generation(self, test_cases):
        """Test AI explanation generation."""
        print("\n" + "=" * 60)
        print("Test 2: Explanation Generation")
        print("=" * 60)
        
        if not test_cases:
            # Use default test with buyer 1, top vendor
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT vendor_id FROM match_results 
                WHERE buyer_request_id = 1 
                ORDER BY rank 
                LIMIT 1
            """)
            result = cursor.fetchone()
            conn.close()
            
            if result:
                test_cases = [{'buyer_id': 1, 'vendor_id': result[0]}]
            else:
                print("[SKIP] No match results found in database")
                return
        
        for i, test in enumerate(test_cases, 1):
            buyer_id = test['buyer_id']
            vendor_id = test['vendor_id']
            
            print(f"\n[Test {i}] Buyer {buyer_id}, Vendor {vendor_id}")
            
            try:
                result = generate_explanation(vendor_id, buyer_id)
                
                if 'error' in result:
                    self._record_failure(f"Explanation test {i}", f"Error: {result['error']}")
                    continue
                
                explanation = result['explanation']
                
                # Check explanation length
                if len(explanation) < 100:
                    print(f"  [FAIL] Explanation too short ({len(explanation)} chars)")
                    self._record_failure(f"Explanation test {i}", "Explanation too short")
                    continue
                
                print(f"  [PASS] Generated {len(explanation)} character explanation")
                
                # Check for hallucinations
                hallucinations = detect_hallucinations(explanation, vendor_id, buyer_id)
                high_severity = [h for h in hallucinations if h['severity'] == 'high']
                
                if high_severity:
                    print(f"  [FAIL] {len(high_severity)} high-severity hallucinations detected")
                    for h in high_severity:
                        print(f"    - {h['claim']}: {h['issue']}")
                    self._record_failure(f"Explanation test {i}", "High-severity hallucinations")
                else:
                    print(f"  [PASS] No high-severity hallucinations")
                    self._record_success(f"Explanation test {i}")
                    
            except Exception as e:
                self._record_failure(f"Explanation test {i}", str(e))
    
    def test_hallucination_detection(self, test_cases):
        """Test hallucination detection."""
        print("\n" + "=" * 60)
        print("Test 3: Hallucination Detection")
        print("=" * 60)
        
        if not test_cases:
            print("[SKIP] No test cases provided")
            return
        
        for i, test in enumerate(test_cases, 1):
            text = test['text']
            vendor_id = test['vendor_id']
            expected_count = test.get('expected_hallucinations', 0)
            
            print(f"\n[Test {i}] Text: '{text[:60]}...'")
            print(f"  Expected: {expected_count} hallucination(s)")
            
            try:
                hallucinations = detect_hallucinations(text, vendor_id)
                actual_count = len(hallucinations)
                
                print(f"  Detected: {actual_count} hallucination(s)")
                
                if actual_count >= expected_count:
                    print(f"  [PASS] Detection working")
                    for h in hallucinations:
                        print(f"    - [{h['severity']}] {h['claim']}: {h['issue']}")
                    self._record_success(f"Hallucination test {i}")
                else:
                    print(f"  [FAIL] Expected at least {expected_count}, found {actual_count}")
                    self._record_failure(f"Hallucination test {i}", "Under-detected")
                    
            except Exception as e:
                self._record_failure(f"Hallucination test {i}", str(e))
    
    def test_followup_questions(self):
        """Test follow-up question generation."""
        print("\n" + "=" * 60)
        print("Test 4: Follow-up Question Generation")
        print("=" * 60)
        
        # Test with buyer requests
        test_buyer_ids = [1, 2, 3]
        
        for buyer_id in test_buyer_ids:
            print(f"\n[Test] Buyer Request {buyer_id}")
            
            try:
                questions = generate_followup_from_buyer_id(buyer_id)
                
                if not questions:
                    print(f"  [INFO] No questions generated (request may be complete)")
                    self._record_success(f"Follow-up test (buyer {buyer_id})")
                else:
                    print(f"  [PASS] Generated {len(questions)} question(s)")
                    for j, q in enumerate(questions, 1):
                        print(f"    {j}. {q[:80]}...")
                    self._record_success(f"Follow-up test (buyer {buyer_id})")
                    
            except Exception as e:
                self._record_failure(f"Follow-up test (buyer {buyer_id})", str(e))
    
    def _record_success(self, test_name):
        """Record a passing test."""
        self.tests_passed += 1
        self.test_results.append({'test': test_name, 'status': 'PASS'})
    
    def _record_failure(self, test_name, reason):
        """Record a failing test."""
        self.tests_failed += 1
        self.test_results.append({'test': test_name, 'status': 'FAIL', 'reason': reason})
        print(f"  [FAIL] {reason}")
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        
        total = self.tests_passed + self.tests_failed
        pass_rate = (self.tests_passed / total * 100) if total > 0 else 0
        
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_failed}")
        print(f"Pass Rate: {pass_rate:.1f}%")
        
        if self.tests_failed > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    reason = result.get('reason', 'Unknown')
                    print(f"  - {result['test']}: {reason}")
        
        print("\n" + "=" * 60)
        
        if self.tests_failed == 0:
            print("[SUCCESS] All tests passed!")
        else:
            print(f"[WARNING] {self.tests_failed} test(s) failed")
        
        print("=" * 60)


def main():
    """Run the test suite."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Phase 9 AI features')
    parser.add_argument(
        '--test',
        choices=['parsing', 'explanations', 'hallucinations', 'followups', 'all'],
        default='all',
        help='Which tests to run'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Run all tests (same as --test all)'
    )
    
    args = parser.parse_args()
    
    test_type = None if args.all or args.test == 'all' else args.test
    
    tester = AIFeaturesTester()
    success = tester.run_all_tests(test_type)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
