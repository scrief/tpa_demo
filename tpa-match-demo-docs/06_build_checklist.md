# Working Build Checklist

Use this as the project task list in Cursor/Carly. Check off items as they are completed.

## Phase 0: Project setup

- [ ] Create project folder `tpa-match-demo`
- [ ] Create folders: `data/raw`, `data/clean`, `scripts`, `app`, `docs`, `prompts`, `database`, `tests`
- [ ] Create `README.md`
- [ ] Create `requirements.txt`
- [ ] Create `.gitignore`
- [ ] Create `.env.example`
- [ ] Confirm `.env` is ignored by Git
- [ ] Add this source-of-truth documentation to `/docs`

## Phase 1: Synthetic messy data

- [ ] Create `data/raw/vendor_profiles_raw.csv`
- [ ] Create `data/raw/vendor_performance_raw.csv`
- [ ] Create `data/raw/vendor_contacts_raw.csv`
- [ ] Include at least 25 fake vendors
- [ ] Include messy state values such as Minnesota, Minn., MN
- [ ] Include messy claim type values such as WC, Workers Comp, Workers' Compensation
- [ ] Include duplicate or near-duplicate vendor names
- [ ] Include missing values
- [ ] Include stale `last_updated` values
- [ ] Include conflicting source data for at least 2 vendors

## Phase 2: Data inspection

- [ ] Create `scripts/inspect_data.py`
- [ ] Load all raw CSV files
- [ ] Print row counts
- [ ] Print column names
- [ ] Show missing values by column
- [ ] Show duplicate vendor names
- [ ] Show unique raw state values
- [ ] Show unique raw claim type values

## Phase 3: Data cleaning and canonicalization

- [ ] Create `scripts/clean_data.py`
- [ ] Standardize vendor names into `normalized_vendor_name`
- [ ] Standardize states into two-letter codes
- [ ] Standardize claim types into controlled values
- [ ] Standardize industries into controlled values
- [ ] Standardize service capabilities into controlled values
- [ ] Merge raw files into one canonical vendor dataset
- [ ] Generate unique `vendor_id` values
- [ ] Add `missing_data_flags`
- [ ] Add `stale_data_flag`
- [ ] Add `conflicting_data_flag`
- [ ] Export `data/clean/canonical_vendors.csv`

## Phase 4: SQLite database

- [ ] Create `scripts/load_database.py`
- [ ] Create SQLite database at `database/tpa_match.db`
- [ ] Load canonical vendors into database
- [ ] Create basic vendor table
- [ ] Create optional related tables if helpful: vendor_services, vendor_states, vendor_industries
- [ ] Create `queries.sql`
- [ ] Add query: vendors serving MN
- [ ] Add query: vendors serving MN/WI/IA
- [ ] Add query: vendors handling workers comp
- [ ] Add query: vendors with manufacturing experience
- [ ] Add query: vendors with missing data
- [ ] Add query: vendors with stale data
- [ ] Add query: top vendors by satisfaction

## Phase 5: Buyer scenario model

- [ ] Create `data/clean/buyer_scenarios.csv`
- [ ] Add at least 20 test scenarios
- [ ] Include expected good matches
- [ ] Include expected bad matches
- [ ] Include expected reason codes
- [ ] Include expected warning codes
- [ ] Include at least 3 ambiguous scenarios
- [ ] Include at least 3 scenarios requiring human review

## Phase 6: Matching engine

- [ ] Create `scripts/score_matches.py`
- [ ] Implement hard filters
- [ ] Implement geographic scoring
- [ ] Implement claims capability scoring
- [ ] Implement industry/client profile scoring
- [ ] Implement service capability scoring
- [ ] Implement reporting/analytics scoring
- [ ] Implement performance scoring
- [ ] Implement technology/integration scoring
- [ ] Implement data quality/confidence scoring
- [ ] Generate total score out of 100
- [ ] Generate category score breakdown
- [ ] Generate reason codes
- [ ] Generate warning codes
- [ ] Generate human-review flag
- [ ] Return top 3 vendors
- [ ] Return disqualified vendors and reasons

## Phase 7: Validation and evals

- [ ] Create `scripts/run_evals.py`
- [ ] Run all buyer scenarios through matching engine
- [ ] Check whether expected good match appears in top 3
- [ ] Check whether expected bad match appears in top 3
- [ ] Check reason codes
- [ ] Check warning codes
- [ ] Check human-review flags
- [ ] Export `data/clean/validation_results.csv`
- [ ] Create validation summary metrics
- [ ] Document at least one scoring adjustment based on eval results

## Phase 8: Streamlit app

- [ ] Create `app/streamlit_app.py`
- [ ] Add buyer request text box
- [ ] Add optional structured fields for states, industry, claim type, and required services
- [ ] Add submit button
- [ ] Display ranked vendor results
- [ ] Display score breakdown
- [ ] Display reason codes in plain language
- [ ] Display warning codes
- [ ] Display human-review flag
- [ ] Display disqualified vendors in expandable section
- [ ] Add feedback form
- [ ] Save feedback to `data/clean/feedback_log.csv`

## Phase 9: AI parsing and explanation layer

- [ ] Create `prompts/buyer_request_parser_prompt.md`
- [ ] Create `prompts/recommendation_explanation_prompt.md`
- [ ] Create `scripts/generate_explanation.py`
- [ ] Add AI request parsing to convert natural language to structured criteria
- [ ] Validate AI parser returns valid JSON matching buyer request schema
- [ ] Add AI explanation generation from reason codes and match results
- [ ] Ensure AI explanation uses ONLY structured fields and reason codes (no hallucination)
- [ ] Add explicit missing data disclosure in AI explanations
- [ ] Test AI explanation against validation scenarios for hallucination detection
- [ ] Add fallback template-based explanation if API unavailable
- [ ] Confirm no API key is hardcoded (use .env only)
- [ ] Add error handling for API failures (rate limits, timeouts, etc.)
- [ ] Update Streamlit app to display AI explanations
- [ ] Validate AI explanations are grounded in actual vendor data

## Phase 10: Security checks

- [ ] Confirm all data is synthetic
- [ ] Confirm `.env` is not committed
- [ ] Confirm API key is loaded from environment variable only
- [ ] Confirm app handles blank/invalid inputs gracefully
- [ ] Confirm SQL queries do not concatenate raw user input unsafely
- [ ] Confirm minimal data is sent to AI API
- [ ] Add basic error handling around AI calls
- [ ] Add audit output for each recommendation

## Phase 11: Accessibility checks

- [ ] Use clear page title and headings
- [ ] Ensure all form inputs have labels
- [ ] Avoid placeholder-only instructions
- [ ] Do not rely only on color for warnings
- [ ] Use clear table headers
- [ ] Use plain-language error messages
- [ ] Make score details expandable to reduce clutter
- [ ] Test keyboard navigation manually
- [ ] Confirm warning/human-review messages are text-based

## Phase 12: Documentation and interview prep

- [ ] Update project `README.md`
- [ ] Document data model
- [ ] Document matching logic
- [ ] Document validation approach
- [ ] Document security/accessibility considerations
- [ ] Add screenshots of app
- [ ] Write short project summary
- [ ] Write lessons learned
- [ ] Prepare 2-minute interview explanation
- [ ] Prepare answer: where AI was used
- [ ] Prepare answer: how validation works
- [ ] Prepare answer: what would be improved next
