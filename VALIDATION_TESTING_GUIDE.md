# Validation Testing Guide

## Overview

This guide explains how to validate the TPA Match Demo matching engine to ensure it produces accurate, consistent, and reliable vendor recommendations.

**Purpose:** Verify that the matching engine correctly ranks vendors based on buyer criteria, generates appropriate reason codes and warning flags, and maintains quality standards across diverse scenarios.

---

## Quick Start

### Running All Validation Tests

```bash
# Run all 25 validation scenarios
python scripts/validate_matches.py

# Generate summary report from database
python scripts/validate_matches.py --report
```

### Running Specific Tests

```bash
# Run a single validation scenario
python scripts/validate_matches.py --scenario VAL-001

# Run priority sensitivity tests
python scripts/test_priority_sensitivity.py

# Run specific priority test
python scripts/test_priority_sensitivity.py --test reporting
```

---

## Validation Framework Components

### 1. Validation Scenarios (`data/validation_scenarios.json`)

**Contains:** 25+ test scenarios covering:
- Perfect matches (high scores, all criteria met)
- Partial matches (missing states, services)
- Data quality issues (stale data, low confidence)
- Edge cases (single vendor, tie scores)
- Priority sensitivity (testing weight adjustments)
- Negative tests (vendor exclusion, filtering)

**Format:**
```json
{
  "scenario_id": "VAL-001",
  "category": "perfect_match",
  "scenario_name": "Perfect match - ABC Manufacturing WC Midwest",
  "buyer_request_id": 1,
  "expected_top_vendor": "Platinum Claims Group",
  "expected_in_top_3": ["Platinum Claims Group", "NorthStar Claims", "Horizon Claims Services"],
  "expected_reason_codes": [
    "serves_all_required_states",
    "handles_required_claim_type",
    "strong_industry_match"
  ],
  "should_require_human_review": false,
  "notes": "ABC Manufacturing scenario - perfect Midwest WC match with high score"
}
```

### 2. Validation Script (`scripts/validate_matches.py`)

**Features:**
- Compares actual vs. expected results
- Validates top vendor, top 3 vendors, ranking order
- Checks reason codes and warning flags
- Verifies human review flags
- Validates score ranges
- Tests vendor exclusion logic
- Saves results to `validation_results` table

**Validation Checks:**
1. **Top Vendor Check:** Is the expected vendor ranked #1?
2. **Top 3 Check:** Do expected vendors appear in top 3?
3. **Ranking Order Check:** Are vendors in expected order?
4. **Reason Codes Check:** Are expected reason codes present?
5. **Warning Codes Check:** Are expected warnings present?
6. **Human Review Flag Check:** Is human review flag set correctly?
7. **Score Range Check:** Is score within expected range?
8. **Vendor Exclusion Check:** Are excluded vendors absent?
9. **Hallucination Check:** No invented capabilities (for Phase 9 AI testing)

### 3. Edge Case Scenarios (`data/edge_case_scenarios.json`)

**Documents:** 15+ edge cases including:
- Single vendor matches
- Very low scores
- Perfect tie scores
- All vendors with stale data
- Missing required data
- Invalid buyer IDs
- Rare claim types
- Extreme priority values
- Empty results

**Purpose:** Ensure the matching engine handles unusual and boundary conditions gracefully without crashes or data corruption.

### 4. Priority Sensitivity Tests (`scripts/test_priority_sensitivity.py`)

**Tests:**
- **Reporting Priority:** High reporting priority boosts reporting-strong vendors
- **Cost Priority:** High cost priority excludes expensive vendors
- **Geography Priority:** Critical geography priority penalizes partial state coverage
- **All Priorities High:** System handles all priorities = 5 correctly
- **All Priorities Low:** System handles all priorities = 1 correctly

**How It Works:**
1. Creates test buyers with different priority settings
2. Runs matching engine
3. Compares results between priority variations
4. Validates that priorities affect rankings as expected
5. Cleans up test data automatically

---

## Understanding Test Results

### Pass Rate Interpretation

| Pass Rate | Status | Action |
|-----------|--------|--------|
| 90-100% | Excellent | Matching engine is highly reliable |
| 80-89% | Good | Minor issues to investigate |
| 70-79% | Acceptable | Review failed scenarios, adjust expectations or logic |
| <70% | Needs Work | Significant issues with matching logic or test expectations |

### Common Failure Modes

#### 1. Top Vendor Mismatch

**Symptom:** Expected vendor is not ranked #1

**Possible Causes:**
- Priority adjustments changed scoring
- Vendor has better data quality than expected
- Expected vendor has stale data penalty
- Scoring weights need adjustment

**Fix:** Review adjusted weights and reason codes to understand why ranking changed. Update expectations or adjust scoring logic.

#### 2. Missing Reason Codes

**Symptom:** Expected reason codes not present in results

**Possible Causes:**
- Scenario expectations too specific
- Vendor data doesn't support expected code
- Matching logic doesn't generate that code

**Fix:** Check vendor data in database. Verify matching engine generates codes correctly. Update expectations to match actual behavior.

#### 3. Incorrect Human Review Flag

**Symptom:** Human review flag doesn't match expectation

**Possible Causes:**
- Score threshold changed (default: <70)
- Data quality assessment different than expected
- Risk flag conditions not met

**Fix:** Review `check_human_review_flags()` function in `match_vendors.py`. Verify thresholds are appropriate. Check actual score and risk flags.

#### 4. Missing Warning Codes

**Symptom:** Expected warning/risk flags not present

**Possible Causes:**
- Data quality thresholds not met
- Stale data threshold changed (default: 180 days)
- Vendor data is better than expected

**Fix:** Query vendor's `last_updated` date, `source_confidence`, and `data_quality_score`. Verify matching engine generates appropriate warnings based on actual data.

---

## Validation Results Database Table

All validation results are saved to the `validation_results` table:

```sql
CREATE TABLE validation_results (
    validation_result_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_name TEXT NOT NULL,
    buyer_request_id INTEGER,
    expected_good_vendors TEXT,      -- JSON array
    expected_bad_vendors TEXT,        -- JSON array
    actual_top_vendors TEXT,          -- JSON array
    top_match_pass INTEGER,           -- 1 = pass, 0 = fail
    explanation_pass INTEGER,         -- For Phase 9 AI testing
    hallucination_detected INTEGER DEFAULT 0,
    missing_data_flag_correct INTEGER,
    notes TEXT,                       -- JSON with detailed check results
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (buyer_request_id) REFERENCES buyer_requests(buyer_request_id)
);
```

**Querying Results:**

```bash
# View recent validation results
python -c "import sqlite3; conn = sqlite3.connect('database/tpa_match_demo.db'); cursor = conn.cursor(); cursor.execute('SELECT scenario_name, top_match_pass, created_at FROM validation_results ORDER BY created_at DESC LIMIT 10'); [print(f'{'PASS' if r[1] else 'FAIL'} - {r[0]} ({r[2]})') for r in cursor.fetchall()]"

# Count pass/fail
python -c "import sqlite3; conn = sqlite3.connect('database/tpa_match_demo.db'); cursor = conn.cursor(); cursor.execute('SELECT SUM(top_match_pass) as passed, COUNT(*) - SUM(top_match_pass) as failed FROM validation_results'); row = cursor.fetchone(); print(f'Passed: {row[0]}, Failed: {row[1]}, Pass Rate: {row[0]/(row[0]+row[1])*100:.1f}%')"
```

---

## Adding New Validation Scenarios

### Step 1: Identify Test Case

Determine what you want to test:
- A specific buyer-vendor match that should work
- An edge case or boundary condition
- A priority adjustment scenario
- A negative test (something that shouldn't match)

### Step 2: Run Matching Manually

```bash
# Run matching for existing buyer
python scripts/match_vendors.py <buyer_id>

# Or create new buyer scenario in seed_sample_data.py first
```

### Step 3: Inspect Results

```bash
# View top matches
python -c "import sqlite3, json; conn = sqlite3.connect('database/tpa_match_demo.db'); cursor = conn.cursor(); cursor.execute('SELECT v.vendor_name, m.total_score, m.reason_codes, m.risk_flags FROM match_results m JOIN vendors v ON m.vendor_id = v.vendor_id WHERE m.buyer_request_id = <buyer_id> AND m.rank <= 3 ORDER BY m.rank'); [print(f'{r[0]}: {r[1]:.1f}, Codes: {json.loads(r[2])}, Flags: {json.loads(r[3])}') for r in cursor.fetchall()]"
```

### Step 4: Add Scenario to JSON

Edit `data/validation_scenarios.json` and add:

```json
{
  "scenario_id": "VAL-026",
  "category": "your_category",
  "scenario_name": "Descriptive name",
  "buyer_request_id": <buyer_id>,
  "expected_top_vendor": "Vendor Name",
  "expected_in_top_3": ["Vendor 1", "Vendor 2", "Vendor 3"],
  "expected_reason_codes": ["code1", "code2"],
  "expected_warning_codes": ["warning1"],
  "should_require_human_review": true/false,
  "notes": "Explanation of what this tests"
}
```

### Step 5: Run Validation

```bash
python scripts/validate_matches.py --scenario VAL-026
```

### Step 6: Iterate

If the test fails:
- Check if expectations are correct based on actual data
- Verify matching logic is working as intended
- Update scenario or fix matching logic as needed

---

## Testing Priority Sensitivity

### Understanding Priority Weighting

The matching engine adjusts category weights based on buyer priorities:

| Priority | Multiplier | Effect |
|----------|------------|--------|
| 5 (Critical) | 1.3x | +30% boost to that category |
| 4 (High) | 1.15x | +15% boost |
| 3 (Moderate) | 1.0x | Default weight (no change) |
| 2 (Low) | 0.7x | -30% penalty |
| 1 (Very Low) | 0.5x | -50% penalty |

**After adjustment, weights are normalized to sum to 100 points.**

### Example: Reporting Priority Test

```python
# Buyer A: priority_reporting = 3 (moderate)
# Buyer B: priority_reporting = 5 (critical)
# 
# Expected: Buyer B's top vendors have higher reporting scores
# because reporting category weight increased from 10 to 13 points
```

### Running Priority Tests

```bash
# Run all priority sensitivity tests
python scripts/test_priority_sensitivity.py

# Run specific test
python scripts/test_priority_sensitivity.py --test reporting
python scripts/test_priority_sensitivity.py --test cost
python scripts/test_priority_sensitivity.py --test geography
python scripts/test_priority_sensitivity.py --test all_high
python scripts/test_priority_sensitivity.py --test all_low
```

---

## Validation Best Practices

### 1. Run After Every Change

Run validation tests after any changes to:
- Matching logic or scoring weights
- Hard filter rules
- Reason code generation
- Human review flag conditions
- Priority adjustment calculations

### 2. Update Scenarios with Codebase

When you change matching logic:
- Update expected results in validation scenarios
- Add new scenarios to cover new features
- Remove or update obsolete scenarios

### 3. Document Failures

When a test fails:
- Document why it failed (logic bug vs. expectation mismatch)
- Record decision: fix logic or update expectation
- Add notes to scenario explaining edge cases

### 4. Test Regression

Keep historical validation results:
- Compare pass rates over time
- Ensure improvements don't break existing scenarios
- Track which scenarios become problematic

### 5. Balance Expectations

Don't make expectations too specific:
- Test for presence of key reason codes, not exhaustive lists
- Allow reasonable score ranges, not exact values
- Focus on critical behaviors, not every detail

---

## Common Validation Queries

### Find All Failed Scenarios

```bash
python -c "import sqlite3; conn = sqlite3.connect('database/tpa_match_demo.db'); cursor = conn.cursor(); cursor.execute('SELECT scenario_name, notes FROM validation_results WHERE top_match_pass = 0 ORDER BY created_at DESC LIMIT 10'); print('Failed Scenarios:'); [print(f'- {r[0]}') for r in cursor.fetchall()]"
```

### Check Specific Buyer Results

```bash
python -c "import sqlite3; conn = sqlite3.connect('database/tpa_match_demo.db'); cursor = conn.cursor(); cursor.execute('SELECT v.vendor_name, m.total_score, m.rank, m.human_review_required FROM match_results m JOIN vendors v ON m.vendor_id = v.vendor_id WHERE m.buyer_request_id = <buyer_id> ORDER BY m.rank LIMIT 5'); print('Top 5 matches:'); [print(f'{r[2]}. {r[0]} ({r[1]:.1f}) HR: {r[3]}') for r in cursor.fetchall()]"
```

### View Reason Codes for Top Match

```bash
python -c "import sqlite3, json; conn = sqlite3.connect('database/tpa_match_demo.db'); cursor = conn.cursor(); cursor.execute('SELECT v.vendor_name, m.reason_codes, m.risk_flags FROM match_results m JOIN vendors v ON m.vendor_id = v.vendor_id WHERE m.buyer_request_id = <buyer_id> AND m.rank = 1'); row = cursor.fetchone(); print(f'Top Match: {row[0]}'); print(f'Reason Codes: {json.loads(row[1])}'); print(f'Risk Flags: {json.loads(row[2])}')"
```

---

## Validation Workflow

```
1. Make changes to matching logic
   ↓
2. Run matching engine on test buyers
   python scripts/match_vendors.py --all
   ↓
3. Run validation tests
   python scripts/validate_matches.py
   ↓
4. Review failures
   python scripts/validate_matches.py --report
   ↓
5. Investigate failures
   - Check actual vs. expected
   - Review matching logic
   - Verify data quality
   ↓
6. Fix issues
   - Update matching logic, OR
   - Update validation expectations
   ↓
7. Re-run validation
   python scripts/validate_matches.py
   ↓
8. Achieve 90%+ pass rate
   ↓
9. Document changes and reasoning
```

---

## Success Criteria

### Phase 7 Completion Requirements

- ✅ 25+ validation scenarios defined
- ✅ Validation script running successfully
- ✅ 90%+ pass rate on all scenarios
- ✅ Edge cases documented
- ✅ Priority sensitivity tests passing
- ✅ Validation results saved to database
- ✅ Clear documentation of validation process

### Ongoing Quality Standards

- Maintain 90%+ pass rate
- All new features have validation scenarios
- Failed scenarios investigated within 1 session
- Validation suite runs in <30 seconds
- Clear reason for any expected failures documented

---

## Troubleshooting

### Validation Script Won't Run

**Error:** `Database not found`
```bash
# Solution: Create database first
python scripts/create_database.py
python scripts/seed_sample_data.py
python scripts/match_vendors.py --all
```

**Error:** `Validation scenarios not found`
```bash
# Solution: Ensure file exists
ls data/validation_scenarios.json
```

### All Tests Failing

**Likely Cause:** Match results are stale or missing
```bash
# Solution: Re-run matching engine
python scripts/match_vendors.py --all
```

### Specific Scenario Failing

```bash
# 1. Run scenario in verbose mode
python scripts/validate_matches.py --scenario VAL-XXX

# 2. Check actual match results
python -c "import sqlite3, json; conn = sqlite3.connect('database/tpa_match_demo.db'); cursor = conn.cursor(); cursor.execute('SELECT v.vendor_name, m.total_score, m.reason_codes, m.risk_flags FROM match_results m JOIN vendors v ON m.vendor_id = v.vendor_id WHERE m.buyer_request_id = <buyer_id> AND m.rank = 1'); row = cursor.fetchone(); print(f'Vendor: {row[0]}, Score: {row[1]}, Codes: {json.loads(row[2])}, Flags: {json.loads(row[3])}')"

# 3. Compare with expectations in validation_scenarios.json

# 4. Either fix matching logic or update expectations
```

---

## Next Steps

After Phase 7 validation is complete:

**Phase 8: Streamlit UI**
- Use validation framework to test UI interactions
- Ensure UI displays correct reason codes and warnings
- Validate user feedback collection

**Phase 9: AI Explanation Layer**
- Use validation to detect hallucinations
- Verify AI explanations match reason codes
- Test AI request parsing accuracy

---

## Questions or Issues?

- **Matching logic unclear?** See `tpa-match-demo-docs/03_matching_logic.md`
- **Database schema questions?** See `scripts/create_database.py`
- **Need to re-run matches?** Run `python scripts/match_vendors.py --all`
- **Sample data questions?** See `scripts/seed_sample_data.py`

---

## Summary

The validation framework ensures the TPA Match Demo matching engine:
- Produces accurate vendor rankings
- Generates appropriate reason codes and warnings
- Handles edge cases gracefully
- Responds correctly to priority adjustments
- Maintains quality standards over time

**Key Command:**
```bash
python scripts/validate_matches.py && python scripts/test_priority_sensitivity.py
```

**Success Indicator:** 90%+ pass rate on all tests with clear documentation of expected failures.
