# Validation Rules and Evals

## Purpose

Validation is what makes this project credible. The app should not simply produce recommendations. It should prove that recommendations are grounded, testable, and reviewable.

## Data validation rules

These checks apply to vendor and buyer data before matching.

| Rule | Description | Severity |
|---|---|---|
| vendor_name_required | Vendor name cannot be blank | error |
| vendor_id_required | Vendor ID must be present and unique | error |
| valid_state_codes | States must be two-letter US state abbreviations | error |
| valid_claim_type_taxonomy | Claim types must map to controlled values | error |
| valid_industry_taxonomy | Industry names must map to controlled values | warning |
| valid_score_ranges | Satisfaction/reporting/data quality scores must be within allowed range | error |
| valid_dates | last_updated and verified_date must be valid dates | error |
| stale_data_check | Data older than configured threshold should be flagged | warning |
| duplicate_vendor_check | Similar vendor names should be flagged for review | warning |
| missing_required_fields | Key matching fields should be present | warning/error depending on field |
| conflicting_source_check | Conflicting values from different sources should be flagged | warning |

## Controlled value examples

### States

Use two-letter state codes such as MN, WI, IA.

### Claim types

- workers_comp
- general_liability
- auto_liability
- property
- professional_liability
- occupational_accident

### Industries

- manufacturing
- construction
- healthcare
- transportation
- public_entity
- retail
- hospitality
- education
- professional_services

### Service capabilities

- return_to_work
- nurse_case_management
- medical_bill_review
- utilization_review
- pharmacy_benefit_management
- subrogation
- fraud_investigation
- litigation_management
- loss_control_coordination
- dedicated_account_manager

## Matching validation rules

| Rule | Description |
|---|---|
| no_top_rank_missing_required_state | Vendor should not be top-ranked if missing a required state |
| no_top_rank_missing_required_claim_type | Vendor should not be top-ranked if it does not handle required claim type |
| required_service_penalty | Missing required services should cause major penalty or disqualification |
| excluded_vendor_rule | Excluded vendors cannot appear in recommendations |
| low_confidence_review | Low source confidence should trigger human review |
| stale_data_penalty | Stale vendor data should reduce score and show warning |
| conflicting_data_review | Conflicting data should trigger human review |
| ambiguous_request_review | Ambiguous buyer requests should trigger clarification or assumptions display |

## AI parsing validation rules

If AI is used to convert natural language into JSON, validate the parsed output.

| Rule | Description |
|---|---|
| valid_json_required | AI extraction must return valid JSON |
| schema_required | Extracted JSON must match expected buyer request schema |
| no_unknown_states | State values must normalize to valid state codes |
| no_unknown_claim_types | Claim types must normalize to controlled taxonomy |
| confidence_required | Extraction should include confidence or assumptions |
| ambiguity_flag_required | Ambiguous requests should be flagged, not silently guessed |

## AI explanation validation rules

AI-generated explanations must be grounded in structured data and reason codes.

| Rule | Description |
|---|---|
| no_unsupported_claims | AI cannot mention vendor capabilities not present in data or reason codes |
| disclose_missing_data | Missing important data must be disclosed when relevant |
| disclose_stale_data | Stale data must be mentioned when it affects confidence |
| no_overconfidence | Use cautious language when confidence is low |
| source_grounded | Explanation must be based on vendor fields, score components, and reason codes |
| no_hidden_decisioning | Explanation should not imply the AI made the ranking decision |
| human_review_when_uncertain | Low confidence or incomplete data should trigger human review note |

## Evaluation test set

Create at least 20 buyer scenarios. Each scenario should define expected good matches and expected bad matches.

### Scenario fields

- scenario_id
- buyer_request_text
- industry
- states_needed
- claim_type_needed
- program_type
- required_services
- preferred_services
- reporting_needs
- technology_needs
- excluded_vendors
- expected_good_matches
- expected_bad_matches
- expected_reason_codes
- expected_warning_codes

## Example eval scenario

```json
{
  "scenario_id": "S001",
  "buyer_request_text": "Need a WC TPA for a self-insured manufacturing client in MN, WI, and IA with RTW support and strong reporting.",
  "industry": "manufacturing",
  "states_needed": ["MN", "WI", "IA"],
  "claim_type_needed": "workers_comp",
  "program_type": "self_insured",
  "required_services": ["return_to_work"],
  "preferred_services": ["nurse_case_management"],
  "reporting_needs": ["dashboard_reporting", "monthly_claim_reviews"],
  "expected_good_matches": ["NorthStar Claims", "Midwest TPA Group"],
  "expected_bad_matches": ["Coastal GL Administrators"],
  "expected_reason_codes": ["serves_all_required_states", "handles_required_claim_type", "has_required_service_return_to_work"],
  "expected_warning_codes": []
}
```

## Eval result fields

- scenario_id
- expected_top_matches
- actual_top_matches
- top_3_contains_good_match
- top_match_is_good_match
- bad_match_in_top_3
- explanation_pass
- hallucination_detected
- missing_data_flag_correct
- human_review_flag_correct
- notes
- fix_needed

## MVP quality metrics

Track these metrics:

- top 3 success rate
- top 1 success rate
- bad match leakage rate
- explanation pass rate
- hallucination rate
- missing data flag accuracy
- human review flag accuracy

## Example validation summary

> Out of 20 test scenarios, the prototype returned an acceptable top-3 match in 17 cases. The most common failure was overweighting state coverage compared with claim specialty. I adjusted the scoring model to correct this.

## Regression testing principle

When scoring logic changes, rerun all scenarios and compare results. Do not improve one scenario while silently breaking five others.
