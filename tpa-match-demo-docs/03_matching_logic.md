# Matching Logic

## Core principle

Use deterministic, inspectable logic for ranking. AI can help parse the request and explain the results, but the scoring engine should be rules-based for the MVP.

## Matching flow

1. Intake buyer request.
2. Convert request into structured buyer criteria.
3. Normalize all criteria to controlled values.
4. Apply hard filters.
5. Score eligible vendors.
6. Generate structured reason codes.
7. Generate warnings and human-review flags.
8. Optionally generate a plain-English explanation from reason codes.
9. Save results and feedback for validation.

## Step 1: Intake buyer request

User can provide:

- natural language text
- optional structured fields
- both

Example:

> We need a WC TPA for a self-insured manufacturing client in MN, WI, and IA. RTW and reporting are major issues.

## Step 2: Convert to structured buyer profile

Example normalized output:

```json
{
  "industry": "manufacturing",
  "states_needed": ["MN", "WI", "IA"],
  "claim_type_needed": "workers_comp",
  "required_services": ["return_to_work"],
  "preferred_services": ["nurse_case_management"],
  "reporting_needs": ["monthly_claim_reviews", "dashboard_reporting"],
  "program_type": "self_insured",
  "priority_reporting": "high",
  "priority_service_quality": "high"
}
```

## Step 3: Hard filters

Hard filters are deal-breakers. The app should return disqualification reasons when vendors fail these filters.

### Default hard filters

| Filter | Rule | Example disqualification reason |
|---|---|---|
| Required states | Vendor must serve all required states unless partial matches are explicitly allowed | Missing required state: IA |
| Required claim type | Vendor must support requested claim type | Does not handle workers_comp |
| Excluded vendors | Vendor cannot be in buyer's excluded vendor list | Buyer excluded this vendor |
| Active status | Vendor must be active | Vendor status is inactive |
| Minimum security | If required, vendor must meet required security fields | Missing required SOC2 evidence |
| Minimum satisfaction | If buyer sets minimum, vendor must meet it | Satisfaction score below 80 |

### Optional softer behavior

Instead of removing all partial matches, the app can separate results into:

- eligible vendors
- partial matches
- disqualified vendors

This is useful for demos because it shows transparency.

## Step 4: Weighted scoring model

Default MVP scoring totals 100 points.

| Category | Weight |
|---|---:|
| Geographic fit | 20 |
| Claims capability fit | 20 |
| Industry/client profile fit | 15 |
| Service capability fit | 15 |
| Reporting/analytics fit | 10 |
| Performance fit | 10 |
| Technology/integration fit | 5 |
| Data quality/confidence | 5 |

## Category logic

### Geographic fit - 20 points

- 20: serves all required states and has strong regional/local capability
- 15: serves all required states but local strength is unknown or partial
- 10: serves most required states
- 0: missing a required state if not already disqualified

Reason codes:

- serves_all_required_states
- serves_some_required_states
- missing_required_state
- strong_local_presence
- limited_local_presence

### Claims capability fit - 20 points

- 20: requested claim type is primary focus or strong capability
- 15: requested claim type is supported with moderate capability
- 5: claim type is weak/limited
- 0: claim type not supported

Reason codes:

- handles_required_claim_type
- claim_type_is_primary_focus
- limited_claim_type_capability
- missing_claim_type_data

### Industry/client profile fit - 15 points

- 15: strong experience with buyer's industry and company profile
- 10: documented industry experience but not strongest industry
- 5: adjacent industry experience
- 0: no evidence of industry fit

Reason codes:

- strong_industry_match
- moderate_industry_match
- adjacent_industry_match
- no_industry_evidence
- similar_client_size_match

### Service capability fit - 15 points

Score required services first, then preferred services.

- 15: all required services and multiple preferred services present
- 10: all required services present
- 5: some required services present
- 0: required services missing

Reason codes:

- has_required_service_return_to_work
- has_required_service_nurse_case_management
- missing_required_service
- has_preferred_service

### Reporting/analytics fit - 10 points

- 10: strong reporting, dashboard, export, and claim review support
- 7: good standard reporting
- 4: limited reporting
- 0: reporting unknown or weak

Reason codes:

- strong_reporting
- dashboard_available
- data_export_available
- limited_reporting
- missing_reporting_data

### Performance fit - 10 points

Suggested scoring:

- satisfaction score 90+ = strong
- satisfaction score 80-89 = moderate
- satisfaction score below 80 = weak
- fast response time improves score
- high complaint/escalation risk reduces score

Reason codes:

- high_satisfaction_score
- moderate_satisfaction_score
- low_satisfaction_score
- fast_response_time
- slow_response_time
- performance_data_missing

### Technology/integration fit - 5 points

- 5: required/preferred integration supported and export/API available
- 3: basic portal/export available
- 1: limited technology capability
- 0: missing required integration if not already disqualified

Reason codes:

- origami_integration_experience
- api_available
- sftp_available
- client_portal_available
- missing_integration_data

### Data quality/confidence - 5 points

- 5: verified, current, complete data
- 3: mostly complete but not verified or slightly stale
- 1: significant missing/stale/conflicting data
- 0: low confidence data

Reason codes:

- verified_vendor_data
- current_vendor_data
- stale_vendor_data
- missing_key_fields
- conflicting_source_data
- low_source_confidence

## Priority weighting

Buyer priorities can adjust category weights.

Example:

If priority_reporting = high:

- increase Reporting/analytics from 10 to 15
- reduce less important categories proportionally

If priority_cost = high:

- increase pricing/commercial fit in future version

If priority_local_presence = high:

- increase geographic fit or local adjuster component

## Reason code format

Each result should include structured reason codes:

```json
{
  "vendor_id": "V001",
  "score": 88,
  "reason_codes": [
    "serves_all_required_states",
    "handles_required_claim_type",
    "strong_industry_match",
    "has_required_service_return_to_work",
    "strong_reporting",
    "current_vendor_data"
  ],
  "warning_codes": [
    "missing_api_information"
  ]
}
```

## Human-review flags

Flag for human review when:

- total score is below 60
- top match has missing required-field evidence
- vendor data is stale
- conflicting source data exists
- AI extraction confidence is low
- required service is only partially supported
- buyer request is ambiguous

## Recommended next questions

The app should suggest follow-up questions when useful.

Examples:

- Confirm whether dedicated adjusters are included in pricing.
- Confirm whether the vendor has current Origami integration experience.
- Confirm state-specific coverage in IA.
- Request current performance metrics because vendor data is more than 12 months old.
- Confirm whether return-to-work support is in-house or partner-provided.
