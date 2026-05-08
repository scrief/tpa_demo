# Design Decisions and Open Questions

This document captures design decisions that need to be made during implementation and serves as a reference for choices made along the way.

## Status: 🔴 Open questions to resolve as we build

---

## 1. Scoring Thresholds and Exact Formulas

### Stale data threshold

**Question:** How old is "stale" data?

**Decision:** 180 days (6 months), calculated dynamically

**Date:** 2026-05-07

**Rationale:** Vendor capabilities and performance don't change daily. 180 days balances the need for current information with the reality that vendor data updates are infrequent in this industry.

**Implementation:**
```python
from datetime import datetime, timedelta

def is_stale(last_updated_str, threshold_days=180):
    """
    Check if vendor data is stale based on last_updated date.
    
    Args:
        last_updated_str: Date string in "YYYY-MM-DD" format
        threshold_days: Number of days before data is considered stale
    
    Returns:
        Boolean indicating if data is stale
    """
    last_updated = datetime.strptime(last_updated_str, "%Y-%m-%d")
    age_days = (datetime.now() - last_updated).days
    return age_days > threshold_days
```

**Date format:** Dates stored as strings in "YYYY-MM-DD" format (e.g., "2026-02-01")

**Impact:** 
- Affects data quality scoring in matching engine
- Triggers human review flags for recommendations with stale data
- Used in validation to test data quality warnings
- Implemented in Phase 3 (data cleaning) and Phase 6 (matching engine)

**Note:** Do NOT add a `stale_data_flag` boolean column to database. Calculate staleness dynamically based on `last_updated` field to avoid stale flags becoming stale themselves.

---

### Priority weight adjustments

**Question:** When `priority_reporting = high`, how exactly do category weights shift?

**Decision:** Use multiplier approach with normalization

**Date:** 2026-05-07

**Priority Scale:** 1-5 where:
- **5 = Critical** - Must-have, heavily influences recommendation
- **4 = High** - Very important, significant weight
- **3 = Moderate** - Standard importance (default)
- **2 = Low** - Nice to have, minimal weight
- **1 = Very Low** - Not a priority for this placement

**Calculation Approach:**
```python
# Base scoring weights (sum to 100)
base_weights = {
    "geography": 20,
    "claims": 20,
    "industry": 15,
    "services": 15,
    "reporting": 10,
    "performance": 10,
    "technology": 5,
    "data_quality": 5
}

# Priority multipliers (1-5 scale)
multipliers = {
    5: 1.3,   # +30% boost for critical priority
    4: 1.15,  # +15% boost for high priority
    3: 1.0,   # No change for moderate/default
    2: 0.7,   # -30% penalty for low priority
    1: 0.5    # -50% penalty for very low priority
}

# Steps:
# 1. Apply multiplier to base weight for each category with a priority
# 2. Keep base weights for performance and data_quality (no priority fields)
# 3. Normalize all adjusted weights to sum to 100
```

**Priority categories in database:**
- `priority_geography` (1-5) → affects geographic fit weight
- `priority_claims` (1-5) → affects claims capability weight
- `priority_industry` (1-5) → affects industry fit weight
- `priority_services` (1-5) → affects service capability weight
- `priority_reporting` (1-5) → affects reporting/analytics weight
- `priority_technology` (1-5) → affects technology fit weight
- `priority_cost` (1-5) → affects hard filtering and vendor selection (not direct scoring weight)

**Note:** `performance` and `data_quality` scoring categories don't have corresponding priority fields. They always use base weights.

**Special handling for `priority_cost`:**
Cost priority doesn't map to a scoring category. Instead:
- If `priority_cost >= 4`: Exclude or penalize vendors with `pricing_level = "high"`
- If `priority_cost == 5`: Strongly favor vendors with `pricing_level = "low"` or `"medium_low"`
- Can be incorporated into performance scoring as a cost-consciousness factor

**Impact:** Affects scoring engine logic and buyer scenario modeling.

---

### Human review threshold

**Question:** What triggers the human review flag?

**Decision:** Multiple conditions, any of which trigger human review flag

**Date:** 2026-05-07 (updated from initial review)

**Conditions that trigger human review:**

1. **Low total score:** Score < 70 (out of 100)
2. **Stale data:** Vendor `last_updated` > 180 days old
3. **Conflicting data:** Vendor has conflicting information from multiple sources (noted in `notes` field)
4. **Low source confidence:** Vendor `source_confidence = "low"`
5. **Missing required service:** Top-ranked vendor is missing a service marked as "required" by buyer
6. **Missing required state:** Top-ranked vendor doesn't serve all buyer's required states (partial match)
7. **Data quality score:** Vendor `data_quality_score < 6` (out of 10)
8. **Excluded vendor appeared:** A buyer-excluded vendor somehow passed filters (system check)

**Implementation:**
```python
def requires_human_review(vendor, match_score, buyer_request):
    """
    Determine if this match requires human review.
    Returns (boolean, list of reason codes)
    """
    review_needed = False
    reasons = []
    
    if match_score < 70:
        review_needed = True
        reasons.append("low_total_score")
    
    if is_stale(vendor.last_updated, threshold_days=180):
        review_needed = True
        reasons.append("stale_vendor_data")
    
    if "CONFLICT" in vendor.notes:
        review_needed = True
        reasons.append("conflicting_source_data")
    
    if vendor.source_confidence == "low":
        review_needed = True
        reasons.append("low_source_confidence")
    
    if vendor.data_quality_score < 6:
        review_needed = True
        reasons.append("low_data_quality_score")
    
    # Add checks for missing required services/states
    
    return review_needed, reasons
```

**Rationale:** Multiple safety checks ensure recommendations are flagged when confidence is low, data is questionable, or match quality is suboptimal. Supports project goal of human-in-the-loop review for trust.

**Impact:** Implemented in Phase 6 (matching engine) and displayed in Phase 8 (Streamlit results)

---

### Partial match scoring

**Question:** How do we score "serves 2 of 3 required states"?

**Options:**
1. Hard filter disqualification
2. Reduced geographic score (e.g., 10/20 instead of 20/20)
3. Include in "partial matches" section with warning

**Decision:** _TBD_

**Impact:** Affects hard filter logic vs scoring logic separation.

---

## 2. Database Schema Design

### Normalization level

**Question:** Should we normalize multi-value fields into junction tables?

**Decision:** Fully normalized approach with enhanced junction tables

**Date:** 2026-05-07

**Implemented Schema:**

Main `vendors` table keeps scalar fields (scores, dates, metadata).

Junction tables for multi-value fields with enhanced attributes:

1. **vendor_states** - Geographic coverage
   - Includes: `coverage_strength`, `local_adjuster_network`
   - Enables nuanced geographic scoring

2. **vendor_claim_types** - Claim types handled
   - Includes: `capability_level`, `primary_focus` flag
   - Enables claim specialty scoring

3. **vendor_industries** - Industry experience
   - Includes: `experience_level`
   - Enables industry fit scoring

4. **vendor_services** - Service capabilities
   - Includes: `service_level`, `provided_in_house` flag, `notes`
   - Enables service capability scoring with in-house vs partner distinction

Matching buyer structure:
- **buyer_required_states** - States needed
- **buyer_required_services** - Services needed with required/preferred distinction

**Rationale:** 
- Proper relational design for portfolio/learning purposes
- Easy to query specific relationships (e.g., "all vendors serving MN")
- Capability levels in junction tables support nuanced scoring
- No schema changes needed to add new states/services/industries
- Demonstrates understanding of database normalization

**Trade-offs:**
- More complex queries (requires JOINs)
- More tables to manage
- But: cleaner data model, more flexible, better for learning SQL

**Foreign Key Configuration:**
- `PRAGMA foreign_keys = ON` enabled
- `ON DELETE CASCADE` for cleanup
- `UNIQUE` constraints on composite keys (vendor_id, state_code), etc.
- Indexes on frequently queried columns

**Impact:** Implemented in Phase 4 (create_database.py) and Phase 5 (seed_sample_data.py)

---

## 3. Synthetic Data Generation

### Sample vendor naming patterns

**Question:** What naming patterns should fake vendors follow?

**Suggested patterns:**
- Geographic + Service Type: "NorthStar Claims", "Midwest TPA Group", "Coastal Claims Administrators"
- Service Focus: "Premier Workers Comp Services", "National Liability Claims"
- Corporate: "Horizon Risk Services", "Summit Claims Solutions"
- Regional: "Great Lakes TPA", "Pacific Northwest Claims"

**Decision:** _TBD_

**Count needed:** 25+ vendors

---

### Distribution targets

**Question:** How should the 25 vendors be distributed across quality/fit levels?

**Suggested distribution:**
- 5 strong matches for typical scenarios (Midwest, manufacturing, WC, strong services)
- 8 moderate matches (missing 1-2 key elements)
- 6 weak matches (wrong geography or claim type specialty)
- 3 wrong geography entirely (CA/NY only vendors)
- 3 wrong claim type specialty (GL/property focus, limited WC)

**Decision:** _TBD_

**Impact:** Affects validation test scenario design.

---

### Realistic conflict examples

**Question:** What types of conflicting data should we simulate?

**Suggested examples:**
1. **State coverage conflicts:**
   - Source A says "MN, WI, IA"
   - Source B says "MN, WI, IA, IL, IN"
   
2. **Capability rating conflicts:**
   - Source A rates return_to_work as "strong"
   - Source B rates return_to_work as "moderate"
   
3. **Date/status conflicts:**
   - Source A shows last_updated 2026-01-15
   - Source B shows last_updated 2024-08-20
   
4. **Service availability conflicts:**
   - Source A says api_access = "full"
   - Source B says api_access = "none"

**Decision:** Include 2-3 vendors with documented conflicts, store in `notes` field and set `conflicting_data_flag = true`

---

## 4. AI Prompt Templates

### Buyer request parser prompt

**Purpose:** Convert natural language buyer request into structured JSON matching buyer request schema.

**Key requirements:**
- Return valid JSON only
- Match expected schema exactly
- Include confidence indicators
- Flag ambiguous requests
- Never guess states or capabilities
- Return null/unknown for unclear fields

**Prompt template:** _TBD - to be created in `/prompts` folder_

**Status:** ⏳ Wait until Phase 9

---

### Recommendation explanation prompt

**Purpose:** Generate plain-English explanation from structured data and reason codes.

**Key requirements:**
- Only reference available vendor fields and reason codes
- Disclose missing data when relevant
- Use cautious language for low-confidence data
- Include human review recommendation when appropriate
- Never invent capabilities
- Ground every statement in structured data

**Prompt template:** _TBD - to be created in `/prompts` folder_

**Status:** ⏳ Wait until Phase 9

---

## 5. Error Handling Strategy

### Missing database file

**Question:** What happens if `database/tpa_match.db` doesn't exist?

**Options:**
1. Show error message with instructions to run `load_database.py`
2. Auto-create database from canonical CSV if available
3. Show helpful error in Streamlit app

**Decision:** _TBD_

---

### AI API unavailable

**Question:** What happens if OpenAI API is down or API key is invalid?

**Options:**
1. Graceful degradation: show structured reason codes without AI explanation
2. Show error message but allow app to function
3. Use template-based explanation as fallback

**Decision:** AI features are optional - app must work without AI using structured form fields and template-based explanations

---

### Invalid user input

**Question:** How do we handle blank or invalid form inputs?

**Strategy:**
- Validate required fields before matching
- Show specific error messages ("States needed is required. Use two-letter state codes such as MN, WI, IA.")
- Provide examples for expected formats
- Handle edge cases (empty strings, invalid state codes, etc.)

**Decision:** _TBD - implement during Phase 8_

---

### No vendors pass hard filters

**Question:** What happens if all vendors are disqualified?

**Options:**
1. Show "No matches found" with reasons
2. Show "partial matches" section even if none meet hard filters
3. Suggest relaxing requirements

**Decision:** _TBD_

**Suggested approach:** Show disqualified vendors section with clear reasons, suggest which filters are too strict.

---

## 6. Streamlit UI Specifics

### Buyer intake form fields

**Question:** What exact form fields appear in the buyer request section?

**Decision:** Use sliders for priority input with visual feedback

**Date:** 2026-05-07

**Priority Input UI Approach:**

Use Streamlit sliders (1-5 scale) for each priority category with:
- User-friendly labels (not technical field names)
- Icons for visual clarity
- Help text explaining what each priority means
- Optional expandable section showing how priorities adjust scoring weights
- Live bar chart showing adjusted weight distribution

**Priority slider labels:**

| Technical Field | User-Facing Label | Icon | Help Text |
|----------------|-------------------|------|-----------|
| priority_geography | Geographic Coverage & Local Presence | 📍 | How important is it that the TPA has adjusters and expertise in your specific states? |
| priority_claims | Claim Type Specialty | 🏥 | How critical is deep experience with your specific claim type? |
| priority_industry | Industry Experience | 🏭 | How important is experience with clients like yours? |
| priority_services | Service Capabilities | ⚙️ | How critical are specific services like RTW, case management, etc.? |
| priority_reporting | Reporting & Analytics | 📊 | How important are dashboards, custom reports, and data transparency? |
| priority_technology | Technology & Integration | 💻 | How important is modern tech, API access, or RMIS integration? |
| priority_cost | Cost Sensitivity | 💰 | How budget-conscious is this placement? (5 = critical, 1 = cost not a concern) |

**Scale explanation to display:**
```
Priority Scale:
- 5 - Critical: Must-have, will heavily influence recommendation
- 4 - High: Very important, significant weight
- 3 - Moderate: Standard importance (default)
- 2 - Low: Nice to have, minimal weight
- 1 - Very Low: Not a priority for this placement
```

**Additional form fields (MVP):**

1. **Narrative request** (text area)
   - Label: "Describe your TPA needs"
   - Placeholder: Example request text
   
2. **Industry** (dropdown)
   - Options: manufacturing, construction, healthcare, transportation, retail, hospitality, education, public_entity, professional_services, energy, real_estate, other
   
3. **States needed** (multiselect or text input)
   - Help text: "Enter two-letter state codes, separated by commas"
   
4. **Claim type needed** (dropdown)
   - Options: workers_comp, general_liability, auto_liability, property, professional_liability, occupational_accident
   
5. **Program type** (dropdown)
   - Options: self_insured, high_deductible, guaranteed_cost, captive
   
6. **Employee count** (number input)
   
7. **Required services** (multiselect)
   - Options: return_to_work, nurse_case_management, medical_bill_review, utilization_review, litigation_management, dashboard_reporting, api_access, etc.
   
8. **Excluded vendors** (text input - optional)
   - Help text: "Enter vendor names to exclude from recommendations, separated by commas"

**Rationale:** Sliders provide intuitive, visual priority setting while maintaining transparency about how priorities affect scoring. This supports the project's core principle of explainability over black-box recommendations.

**Impact:** Implemented in Phase 8 (Streamlit app)

---

### Score breakdown display

**Question:** How should we display the score breakdown?

**Options:**
1. **Expandable sections** (Streamlit expander)
   ```
   ▶ Score breakdown (88/100)
   ```
   
2. **Side-by-side columns**
   ```
   | Category | Score | Max |
   |----------|-------|-----|
   | Geographic fit | 20 | 20 |
   | Claims capability | 18 | 20 |
   ```
   
3. **Progress bars with labels**

**Decision:** _TBD - implement in Phase 8_

---

### Feedback form design

**Question:** What does the feedback form look like?

**Suggested fields:**
1. Was this recommendation useful? (Yes/No/Somewhat)
2. Was the explanation accurate? (Yes/No/Uncertain)
3. What information was missing or unclear? (text box)
4. Should a different vendor have ranked higher? (text box)
5. Additional comments (text box)

**Decision:** _TBD - implement in Phase 8_

---

## 7. Additional Open Questions

### Testing strategy

**Question:** Should we use pytest for automated tests, or just the eval script?

**Decision:** _TBD_

**Notes:** Eval script is higher priority. Pytest is optional polish.

---

### Data export features

**Question:** Should users be able to download results as CSV/PDF?

**Decision:** _TBD - nice to have, not MVP critical_

---

### Multi-scenario comparison

**Question:** Should users be able to run and compare multiple scenarios side-by-side?

**Decision:** _TBD - nice to have, not MVP critical_

---

## Decision Log

As decisions are made during implementation, document them here with date and rationale.

### 2026-05-07: Core Design Decisions

**Database Schema - Fully Normalized Approach**
- **Decision:** Use fully normalized schema with junction tables for states, claim types, industries, and services
- **Rationale:** Proper relational design for portfolio/learning purposes. Enhanced junction tables include capability levels (coverage_strength, capability_level, experience_level, service_level) that enable nuanced scoring.
- **Impact:** Implemented in create_database.py and seed_sample_data.py

**Stale Data Threshold - 180 Days**
- **Decision:** Data older than 180 days (6 months) is considered stale
- **Rationale:** Vendor capabilities don't change daily. 180 days balances freshness with reality of infrequent vendor data updates.
- **Implementation:** Calculate dynamically from `last_updated` field, don't store as boolean flag
- **Impact:** Affects data quality scoring and human review triggers

**Priority Scale - 1 to 5**
- **Decision:** User priorities use 1-5 scale where 5=critical, 3=moderate (default), 1=very low
- **Rationale:** Intuitive scale that maps well to slider UI and multiplier-based weight adjustments
- **Impact:** All buyer_requests use this scale for priority fields

**Priority Weight Adjustment - Multiplier with Normalization**
- **Decision:** Apply multipliers to base weights based on priority level, then normalize to 100
  - Priority 5 (Critical): 1.3x multiplier (+30% boost)
  - Priority 4 (High): 1.15x multiplier (+15% boost)
  - Priority 3 (Moderate): 1.0x multiplier (no change)
  - Priority 2 (Low): 0.7x multiplier (-30% penalty)
  - Priority 1 (Very Low): 0.5x multiplier (-50% penalty)
- **Rationale:** Transparent, explainable, and allows user control while maintaining 100-point scoring system
- **Impact:** Core logic for matching engine scoring calculations

**Priority Cost Handling**
- **Decision:** `priority_cost` affects filtering and vendor selection, not direct scoring weights
  - `priority_cost >= 4`: Exclude or penalize `pricing_level = "high"` vendors
  - `priority_cost == 5`: Strongly favor `pricing_level = "low"` or `"medium_low"` vendors
- **Rationale:** Cost is a constraint/preference, not a quality dimension like geography or services
- **Impact:** Implemented in hard filter logic and vendor selection

**Priority Input UI - Sliders**
- **Decision:** Use Streamlit sliders (1-5) for priority input with:
  - User-friendly labels with icons (not technical field names)
  - Help text explaining what each priority means
  - Optional expandable section showing adjusted weight distribution as bar chart
- **Rationale:** Visual, intuitive, maintains transparency about how priorities affect scoring
- **Impact:** Implemented in Phase 8 (Streamlit app)

**Seed Data - 25 Vendors, 15 Buyer Scenarios**
- **Decision:** 
  - 25 vendors with realistic diversity (geography, specialty, quality, data freshness)
  - 15 buyer scenarios covering various geographies, claim types, priorities, and edge cases
  - Include conflicting data examples (Great Lakes Claims, Midwest Claims Solutions)
  - Include very stale data examples (Legacy Claims Co., Regional Risk Administrators)
- **Rationale:** Comprehensive test coverage for validation phase, demonstrates various matching scenarios
- **Impact:** Implemented in seed_sample_data.py

---

## Open Questions Still To Resolve

The following questions remain open and will be addressed during implementation:



_This document should be updated throughout the build process._
