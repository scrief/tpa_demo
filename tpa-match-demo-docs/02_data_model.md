# Data Model

## Core data model concept

The app compares two things:

1. Vendor reality: what a TPA/vendor can actually do.
2. Buyer need: what the client is looking for.

The app then uses hard filters, scoring, reason codes, and validation rules to produce a recommendation.

## Canonicalization principle

Raw source data may contain inconsistent values such as:

- Minnesota, Minn., MN
- Workers Comp, WC, Workers' Compensation
- Return to Work, RTW, transitional duty

The cleaned/canonical dataset should standardize these into controlled values:

- MN
- workers_comp
- return_to_work

## Vendor fields

### Vendor identity

| Field | Type | Example | Notes |
|---|---|---|---|
| vendor_id | string | V001 | Stable unique ID |
| vendor_name | string | NorthStar Claims | Display name |
| normalized_vendor_name | string | northstar_claims | Used for matching/deduplication |
| vendor_type | enum | TPA | TPA, managed care, bill review, etc. |
| parent_company | string | NorthStar Holdings | Optional |
| headquarters_state | enum | MN | Two-letter state |
| years_in_business | integer | 18 | Optional |
| company_size | enum | mid_market | small, mid_market, enterprise |
| website | string | https://example.com | Optional |
| active_status | enum | active | active, inactive, unknown |

### Geographic coverage

| Field | Type | Example | Notes |
|---|---|---|---|
| states_served | list | MN, WI, IA | Required for matching |
| regions_served | list | Midwest | Optional derived field |
| nationwide_capability | boolean | false | Do not assume quality in every state |
| licensed_states | list | MN, WI, IA | Optional |
| excluded_states | list | CA, NY | Useful hard filter |
| local_adjuster_network | enum | strong | none, limited, partial, strong |
| field_adjuster_availability | enum | partial | none, partial, strong |
| catastrophe_response_states | list | MN, WI, IA | Optional |

### Claims handled

| Field | Type | Example | Notes |
|---|---|---|---|
| claim_types | list | workers_comp, general_liability | Required |
| primary_claim_focus | enum | workers_comp | Main specialty |
| workers_comp_capability | enum | strong | none, limited, moderate, strong |
| general_liability_capability | enum | moderate | none, limited, moderate, strong |
| auto_liability_capability | enum | limited | none, limited, moderate, strong |
| property_claims_capability | enum | none | none, limited, moderate, strong |
| professional_liability_capability | enum | none | none, limited, moderate, strong |
| medical_only_claims | boolean | true | WC detail |
| lost_time_claims | boolean | true | WC detail |
| litigated_claims | boolean | true | Important complexity signal |
| catastrophic_claims | enum | partial | none, partial, strong |

### Industry experience

| Field | Type | Example | Notes |
|---|---|---|---|
| industries_served | list | manufacturing, construction | Required for industry fit |
| strongest_industries | list | manufacturing | Optional |
| limited_industries | list | public_entity | Optional |
| industry_case_studies_available | boolean | true | Evidence signal |
| similar_client_experience | list | mid_market_manufacturing | Optional |

### Employer/client profile fit

| Field | Type | Example | Notes |
|---|---|---|---|
| ideal_client_size | enum | 250-2500_employees | Optional |
| small_business_fit | enum | moderate | limited, moderate, strong |
| middle_market_fit | enum | strong | limited, moderate, strong |
| enterprise_fit | enum | moderate | limited, moderate, strong |
| self_insured_fit | enum | strong | none, limited, moderate, strong |
| guaranteed_cost_fit | enum | moderate | none, limited, moderate, strong |
| high_deductible_fit | enum | strong | none, limited, moderate, strong |
| captive_fit | enum | partial | none, partial, strong |
| multi_state_fit | enum | strong | none, limited, moderate, strong |
| union_workforce_experience | enum | partial | unknown, none, partial, strong |

### Service capabilities

| Field | Type | Example | Notes |
|---|---|---|---|
| return_to_work | enum | strong | none, limited, moderate, strong |
| nurse_case_management | boolean | true | Service offering |
| medical_bill_review | boolean | true | Service offering |
| utilization_review | boolean | true | Service offering |
| pharmacy_benefit_management | enum | partner | none, partner, in_house |
| subrogation | boolean | true | Service offering |
| fraud_investigation | boolean | true | Service offering |
| litigation_management | enum | strong | none, limited, moderate, strong |
| settlement_authority_support | boolean | true | Optional |
| loss_control_coordination | enum | partial | none, partial, strong |
| claim_reporting_24_7 | boolean | true | Intake support |
| dedicated_account_manager | boolean | true | Service model |
| dedicated_adjuster_team | boolean | false | Service model |

### Reporting and analytics

| Field | Type | Example | Notes |
|---|---|---|---|
| standard_dashboard | boolean | true | Reporting tech |
| custom_reporting | boolean | true | Higher flexibility |
| report_frequency | enum | monthly | weekly, monthly, quarterly, on_demand |
| bordereau_reporting | boolean | true | Insurance-specific reporting |
| claim_lag_reporting | boolean | true | Useful WC metric |
| loss_trend_reporting | boolean | true | Useful analytic capability |
| reserve_analysis | boolean | true | Claims management |
| litigation_reporting | boolean | true | Claims management |
| benchmarking | enum | partial | none, partial, strong |
| data_export_available | boolean | true | Important for RMIS |
| reporting_score | integer | 8 | 0-10 |

### Technology and integration

| Field | Type | Example | Notes |
|---|---|---|---|
| client_portal | boolean | true | Client-facing tech |
| mobile_app | boolean | false | Optional |
| api_access | enum | partial | none, partial, full |
| sftp_data_exchange | boolean | true | Common data exchange |
| single_sign_on | boolean | false | Optional |
| integration_experience | list | Origami, Riskonnect | Major fit signal |
| claim_intake_methods | list | portal, phone, email | Intake options |
| document_management | boolean | true | Optional |
| automated_workflows | enum | moderate | none, limited, moderate, strong |
| ai_capabilities | enum | limited | none, limited, moderate, strong |
| data_security_certification | list | SOC2 | Security evidence |

### Performance metrics

| Field | Type | Example | Notes |
|---|---|---|---|
| avg_response_time_days | decimal | 1.8 | Lower is better |
| avg_claim_setup_time_hours | decimal | 6 | Lower is better |
| avg_contact_time_hours | decimal | 24 | Lower is better |
| closure_rate | decimal | 0.82 | 0-1 |
| litigation_rate | decimal | 0.09 | Context dependent |
| avg_claim_duration_days | decimal | 42 | Context dependent |
| client_retention_rate | decimal | 0.91 | 0-1 |
| satisfaction_score | integer | 88 | 0-100 |
| complaint_rate | enum | low | low, moderate, high |
| escalation_rate | enum | moderate | low, moderate, high |
| data_quality_score | integer | 7 | 0-10 |

### Relationship and service model

| Field | Type | Example | Notes |
|---|---|---|---|
| service_model | enum | dedicated_team | call_center, pooled, dedicated_team |
| account_management_strength | enum | strong | limited, moderate, strong |
| adjuster_caseload | enum | moderate | low, moderate, high, unknown |
| adjuster_turnover_risk | enum | low | low, moderate, high, unknown |
| communication_style | enum | proactive | reactive, standard, proactive |
| review_meeting_frequency | enum | quarterly | monthly, quarterly, annual, on_demand |
| executive_sponsor_available | boolean | true | Optional |
| implementation_support | enum | strong | limited, moderate, strong |
| training_support | enum | moderate | limited, moderate, strong |

### Pricing and commercial fit

| Field | Type | Example | Notes |
|---|---|---|---|
| pricing_model | enum | per_claim | per_claim, flat_fee, hybrid, unknown |
| relative_cost | enum | medium | low, medium, high, unknown |
| minimum_account_size | string | 250 employees | Optional |
| implementation_fee | enum | yes | yes, no, unknown |
| contract_flexibility | enum | moderate | limited, moderate, high |
| typical_contract_length | string | 3 years | Optional |
| cost_transparency | enum | high | low, medium, high, unknown |

### Data quality and provenance

| Field | Type | Example | Notes |
|---|---|---|---|
| source | string | broker_uploaded_loss_run | Where data came from |
| source_type | enum | spreadsheet | spreadsheet, proposal, user_entry, public_site |
| source_confidence | enum | medium | low, medium, high |
| last_updated | date | 2026-02-01 | Freshness check |
| verified_by_human | boolean | true | Trust signal |
| verified_date | date | 2026-02-05 | Optional |
| missing_fields | list | api_available, pricing_model | Auto-generated |
| stale_data_flag | boolean | false | Auto-generated |
| conflicting_data_flag | boolean | true | Auto-generated |
| notes | text | State coverage differs by source. | Human-readable notes |

## Buyer request fields

### Buyer identity/profile

| Field | Type | Example | Notes |
|---|---|---|---|
| buyer_name | string | ABC Manufacturing | Optional in MVP |
| industry | enum | manufacturing | Important fit signal |
| sub_industry | string | metal_fabrication | Optional |
| employee_count | integer | 850 | Client size fit |
| annual_payroll | decimal | 62000000 | Optional |
| locations_count | integer | 7 | Complexity signal |
| states_needed | list | MN, WI, IA | Required |
| union_workforce | boolean | true | Optional complexity signal |
| risk_complexity | enum | moderate_high | low, moderate, moderate_high, high |

### Insurance/program structure

| Field | Type | Example | Notes |
|---|---|---|---|
| program_type | enum | self_insured | self_insured, high_deductible, guaranteed_cost, captive |
| claim_type_needed | enum | workers_comp | Required |
| deductible_structure | enum | high_deductible | Optional |
| captive_program | boolean | false | Optional |
| current_tpa | string | Legacy Claims Co. | Optional |
| reason_for_search | enum | service_issues | service_issues, new_program, cost, reporting, renewal |
| implementation_timeline | enum | 90_days | urgent, 90_days, 6_months, flexible |

### Claims profile

| Field | Type | Example | Notes |
|---|---|---|---|
| annual_claim_volume | integer | 220 | Scale signal |
| medical_only_percentage | decimal | 0.65 | Optional |
| lost_time_percentage | decimal | 0.35 | Optional |
| litigated_claim_percentage | decimal | 0.12 | Optional |
| high_severity_claims | enum | moderate | low, moderate, high |
| common_injury_types | list | strains, lacerations, slips | Optional |
| claim_lag_issue | boolean | true | Pain point |
| return_to_work_challenge | boolean | true | Pain point |
| open_claim_backlog | enum | high | low, moderate, high |

### Required capabilities

Must-have items that can disqualify a vendor.

| Field | Type | Example |
|---|---|---|
| required_states | list | MN, WI, IA |
| required_claim_types | list | workers_comp |
| required_industry_experience | list | manufacturing |
| required_services | list | return_to_work, nurse_case_management |
| required_reporting | list | monthly_claim_reviews |
| required_integrations | list | Origami |
| required_security | list | SOC2 |
| required_language_support | list | English, Spanish |

### Preferred capabilities

Nice-to-have items that should increase score but not automatically disqualify.

| Field | Type | Example |
|---|---|---|
| preferred_services | list | pharmacy_review, subrogation |
| preferred_reporting | list | dashboard_reporting |
| preferred_technology | list | api_access |
| preferred_service_model | enum | dedicated_team |
| preferred_geography | string | Midwest presence |
| preferred_cost_level | enum | medium |

### Buyer priorities

Priority fields change scoring weights.

| Field | Type | Example |
|---|---|---|
| priority_speed | enum | high |
| priority_cost | enum | medium |
| priority_claim_outcomes | enum | high |
| priority_reporting | enum | high |
| priority_service_quality | enum | high |
| priority_technology | enum | medium |
| priority_local_presence | enum | high |
| priority_industry_expertise | enum | high |
| priority_implementation_speed | enum | medium |

### Constraints

| Field | Type | Example |
|---|---|---|
| excluded_vendors | list | Legacy Claims Co. |
| max_cost_level | enum | high |
| must_have_states | list | MN, WI, IA |
| must_have_security | list | SOC2 |
| cannot_use_outsourced_adjusting | boolean | true |
| implementation_deadline | date | 2026-09-01 |
| minimum_satisfaction_score | integer | 80 |

### Buyer context notes

| Field | Type | Example |
|---|---|---|
| narrative_request | text | Need better WC handling and RTW support. |
| pain_points | list | slow response, poor reporting, high claim lag |
| broker_notes | text | Client wants a more proactive TPA. |
| decision_makers | list | CFO, HR, Risk Manager |
| sensitivity_notes | text | Cost matters, but service is the bigger issue. |

## MVP field set

For version 1, implement these first:

### Vendor MVP fields

- vendor_id
- vendor_name
- states_served
- claim_types
- industries_served
- client_size_fit
- program_type_fit
- services
- reporting_capabilities
- technology_capabilities
- satisfaction_score
- avg_response_time_days
- pricing_level
- source
- last_updated
- missing_data_flags

### Buyer MVP fields

- industry
- states_needed
- claim_type_needed
- program_type
- employee_count
- required_services
- preferred_services
- reporting_needs
- technology_needs
- priority_weights
- excluded_vendors
