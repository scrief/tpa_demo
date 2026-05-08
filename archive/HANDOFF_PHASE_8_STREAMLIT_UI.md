# Handoff Document: Phase 8 - Streamlit UI

**Date:** 2026-05-07  
**Current Status:** Phase 7 Complete - Validation Framework Built and Tested  
**Next Phase:** Phase 8 - Streamlit UI Development  
**Agent Task:** Build interactive web interface for TPA vendor matching

---

## Executive Summary

The TPA Match Demo matching engine is **fully functional and validated**. Your task is to build a clean, accessible Streamlit web interface that allows users to:
1. Submit buyer requests (natural language + structured fields)
2. View ranked vendor matches with score breakdowns
3. See reason codes and warning flags
4. Provide feedback on recommendations

**All backend logic is complete and tested at 100% pass rate.** You just need to build the frontend.

---

## What's Already Complete ✅

### Phase 0-7: Full Backend Implementation

| Phase | Status | Key Deliverables |
|-------|--------|------------------|
| 0-1 | ✅ | 8 documentation files in `tpa-match-demo-docs/` |
| 2 | ✅ | Normalized database schema (SQLite) |
| 3 | ✅ | Data cleaning script (`scripts/clean_data.py`) |
| 4 | ✅ | Database creation script (`scripts/create_database.py`) |
| 5 | ✅ | Sample data: 24 vendors, 15 buyer scenarios |
| 6 | ✅ | Matching engine (`scripts/match_vendors.py`) |
| 7 | ✅ | Validation framework (100% pass rate) |

### Matching Engine Capabilities

**File:** `scripts/match_vendors.py` (900+ lines)

**Features:**
- Hard filters (excluded vendors, required states/claim types, cost sensitivity)
- Priority-based weight adjustment (1-5 scale)
- 8 scoring categories (geography, claims, industry, services, reporting, performance, technology, data quality)
- Structured reason codes (40+ codes)
- Human review flags (low scores, stale data, missing requirements)
- Database persistence

**Usage:**
```bash
python scripts/match_vendors.py <buyer_id>  # Match single buyer
python scripts/match_vendors.py --all        # Match all buyers
```

### Database Status

**Location:** `database/tpa_match_demo.db`

**Current Data:**
- 24 active vendors with full profiles
- 15 buyer scenarios (diverse industries, geographies, claim types)
- 77 match results (pre-generated for all buyers)
- 103 validation results (historical test runs)

**Key Tables:**
- `vendors` - TPA vendor master data
- `vendor_states`, `vendor_claim_types`, `vendor_industries`, `vendor_services` - Relationship tables
- `buyer_requests` - Buyer scenarios
- `buyer_required_states`, `buyer_required_services` - Buyer requirements
- `match_results` - Vendor rankings with scores and reason codes

### Validation Status

**100% Pass Rate:**
- 25/25 validation scenarios passing
- 5/5 priority sensitivity tests passing
- All edge cases documented
- Comprehensive testing guide available

**Validation Framework:**
- `scripts/validate_matches.py` - Main validation script
- `scripts/test_priority_sensitivity.py` - Priority testing
- `data/validation_scenarios.json` - 25 test scenarios
- `VALIDATION_TESTING_GUIDE.md` - Complete documentation

---

## Phase 8 Objectives

Build a Streamlit web application that provides an intuitive interface for the TPA matching system.

### Core User Flow

```
1. User arrives at home page
   ↓
2. User fills out buyer request form
   - Natural language description (optional)
   - Structured fields (industry, states, claim type, etc.)
   - Priority sliders (1-5 scale)
   - Required services (multi-select)
   - Excluded vendors (optional)
   ↓
3. User clicks "Find Matches"
   ↓
4. App runs matching engine
   ↓
5. App displays ranked vendor results
   - Top 3-5 vendors
   - Score breakdown by category
   - Reason codes in plain English
   - Warning/risk flags prominently displayed
   - Human review indicators
   ↓
6. User can:
   - View detailed vendor profiles
   - See score visualizations
   - Provide feedback
   - Save results
```

---

## Your Tasks

### Task 1: Create Streamlit App Structure

**File to create:** `app.py`

**Basic Structure:**
```python
import streamlit as st
import sqlite3
import json
import subprocess
from pathlib import Path

# Page config
st.set_page_config(
    page_title="TPA Match Demo",
    page_icon="🏢",
    layout="wide"
)

# Database connection
DB_PATH = Path("database/tpa_match_demo.db")

# Main app
def main():
    st.title("TPA Match Demo")
    st.subheader("Find the perfect TPA vendor for your needs")
    
    # Navigation
    page = st.sidebar.radio(
        "Navigation",
        ["Home", "New Match Request", "View Results", "Browse Vendors"]
    )
    
    if page == "Home":
        show_home()
    elif page == "New Match Request":
        show_match_form()
    elif page == "View Results":
        show_past_results()
    elif page == "Browse Vendors":
        show_vendor_directory()

if __name__ == "__main__":
    main()
```

### Task 2: Build Buyer Request Form

**Location:** `show_match_form()` function in `app.py`

**Required Form Fields:**

1. **Basic Information**
   - Buyer name (text input)
   - Industry (dropdown: manufacturing, construction, healthcare, etc.)
   - Claim type needed (dropdown: workers_comp, general_liability, auto_liability, etc.)
   - Program type (dropdown: self_insured, fully_insured, large_deductible)

2. **Geographic Requirements**
   - Required states (multi-select: MN, WI, IA, etc.)
   - Priority geography (slider: 1-5)

3. **Service Requirements**
   - Required services (multi-select: return_to_work, nurse_case_management, etc.)
   - Priority services (slider: 1-5)

4. **Other Priorities**
   - Priority claims capability (slider: 1-5)
   - Priority industry fit (slider: 1-5)
   - Priority reporting (slider: 1-5)
   - Priority technology (slider: 1-5)
   - Priority cost (slider: 1-5)

5. **Optional Fields**
   - Natural language request (text area)
   - Excluded vendors (text input, comma-separated)
   - Pain points (text area)

**Priority Slider Labels:**
```python
priority_labels = {
    1: "Very Low - Not important",
    2: "Low - Minimal importance",
    3: "Moderate - Standard importance",
    4: "High - Very important",
    5: "Critical - Must be excellent"
}
```

**Form Submit Logic:**
```python
if st.button("Find Matches", type="primary"):
    # 1. Save buyer request to database
    buyer_id = create_buyer_request(form_data)
    
    # 2. Run matching engine
    result = subprocess.run(
        ['python', 'scripts/match_vendors.py', str(buyer_id)],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        st.success("Match completed! View results below.")
        # 3. Display results
        show_match_results(buyer_id)
    else:
        st.error(f"Matching failed: {result.stderr}")
```

### Task 3: Display Match Results

**Location:** `show_match_results(buyer_id)` function in `app.py`

**What to Display:**

**A. Overall Match Summary**
```python
st.header("Match Results")
st.write(f"Found {match_count} matching vendors")

if any_human_review_required:
    st.warning("⚠️ Some matches require human review - see flags below")
```

**B. Top Vendors (Top 3-5)**

For each vendor, show:
```python
with st.expander(f"#{rank}. {vendor_name} - Score: {total_score:.1f}/100", expanded=(rank==1)):
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Vendor details
        st.write(f"**Headquarters:** {headquarters_state}")
        st.write(f"**Company Size:** {company_size}")
        st.write(f"**Pricing Level:** {pricing_level}")
        
        # Score breakdown
        st.subheader("Score Breakdown")
        score_data = {
            "Geography": geography_score,
            "Claims Capability": claims_score,
            "Industry Fit": industry_score,
            "Service Capability": service_score,
            "Reporting": reporting_score,
            "Performance": performance_score,
            "Technology": technology_score,
            "Data Quality": data_quality_score
        }
        
        # Progress bars for each category
        for category, score in score_data.items():
            st.write(f"**{category}:** {score:.1f}")
            st.progress(score / 20.0)  # Assuming max 20 per category
    
    with col2:
        # Human review flag
        if human_review_required:
            st.error("⚠️ Human Review Required")
        else:
            st.success("✓ Meets Quality Standards")
        
        # Reason codes
        st.subheader("Why This Vendor?")
        reason_codes = json.loads(reason_codes_json)
        for code in reason_codes[:5]:  # Show top 5
            st.write(f"• {format_reason_code(code)}")
        
        # Risk flags
        if risk_flags:
            st.subheader("Considerations")
            risk_flags = json.loads(risk_flags_json)
            for flag in risk_flags:
                st.write(f"⚠️ {format_risk_flag(flag)}")
```

**C. Score Visualization**

```python
import plotly.graph_objects as go

# Create radar chart comparing top 3 vendors
fig = go.Figure()

for vendor in top_3_vendors:
    fig.add_trace(go.Scatterpolar(
        r=[vendor['geo_score'], vendor['claims_score'], 
           vendor['industry_score'], vendor['service_score'],
           vendor['reporting_score'], vendor['performance_score'],
           vendor['tech_score'], vendor['quality_score']],
        theta=['Geography', 'Claims', 'Industry', 'Services',
               'Reporting', 'Performance', 'Technology', 'Quality'],
        fill='toself',
        name=vendor['name']
    ))

fig.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 20])),
    showlegend=True
)

st.plotly_chart(fig)
```

### Task 4: Format Reason Codes & Risk Flags

**Helper Functions:**

```python
def format_reason_code(code):
    """Convert snake_case reason codes to human-readable text."""
    mappings = {
        "serves_all_required_states": "Serves all required states",
        "strong_local_presence": "Strong local presence in your area",
        "handles_required_claim_type": "Handles your required claim type",
        "claim_type_is_primary_focus": "This claim type is their primary focus",
        "strong_industry_match": "Strong experience in your industry",
        "has_required_service_return_to_work": "Offers return-to-work services",
        "has_required_service_nurse_case_management": "Offers nurse case management",
        "has_preferred_services": "Offers additional preferred services",
        "good_reporting": "Good reporting capabilities",
        "strong_reporting": "Excellent reporting capabilities",
        "high_satisfaction_score": "High client satisfaction scores",
        "moderate_satisfaction_score": "Good client satisfaction",
        "fast_response_time": "Fast claim response times",
        "api_available": "API integration available",
        "client_portal_available": "Client portal available",
        "current_vendor_data": "Data is current and up-to-date",
        "verified_vendor_data": "Vendor data has been verified"
    }
    return mappings.get(code, code.replace('_', ' ').title())

def format_risk_flag(flag):
    """Convert risk flags to user-friendly warnings."""
    mappings = {
        "missing_required_state": "Does not serve all required states",
        "missing_required_service": "Missing some required services",
        "stale_vendor_data": "Vendor data is more than 6 months old",
        "low_source_confidence": "Limited data confidence",
        "conflicting_source_data": "Conflicting information from sources",
        "missing_api_information": "API integration information unavailable"
    }
    return mappings.get(flag, flag.replace('_', ' ').title())
```

### Task 5: Add Feedback Collection

**Location:** Below match results in `show_match_results()`

```python
st.divider()
st.subheader("How did we do?")

col1, col2 = st.columns(2)

with col1:
    usefulness = st.radio(
        "Was this recommendation useful?",
        ["Very useful", "Somewhat useful", "Not useful"],
        key=f"usefulness_{buyer_id}"
    )

with col2:
    accuracy = st.radio(
        "Was the explanation accurate?",
        ["Very accurate", "Mostly accurate", "Not accurate"],
        key=f"accuracy_{buyer_id}"
    )

comments = st.text_area(
    "Additional feedback (optional)",
    key=f"comments_{buyer_id}"
)

if st.button("Submit Feedback"):
    save_feedback(buyer_id, usefulness, accuracy, comments)
    st.success("Thank you for your feedback!")
```

### Task 6: Create Vendor Directory Browser

**Location:** `show_vendor_directory()` function

**Features:**
- Display all 24 vendors in a sortable table
- Filter by state, claim type, industry
- Search by vendor name
- View detailed vendor profile on click

```python
def show_vendor_directory():
    st.header("Browse Vendor Directory")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        state_filter = st.multiselect("Filter by State", get_all_states())
    
    with col2:
        claim_type_filter = st.selectbox("Filter by Claim Type", ["All"] + get_claim_types())
    
    with col3:
        search = st.text_input("Search vendor name")
    
    # Get filtered vendors
    vendors = get_filtered_vendors(state_filter, claim_type_filter, search)
    
    # Display as table
    st.dataframe(vendors, use_container_width=True)
```

### Task 7: View Past Results

**Location:** `show_past_results()` function

```python
def show_past_results():
    st.header("Past Match Requests")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            buyer_request_id,
            buyer_name,
            industry,
            claim_type_needed,
            created_at
        FROM buyer_requests
        ORDER BY created_at DESC
        LIMIT 20
    """)
    
    results = cursor.fetchall()
    
    for buyer_id, name, industry, claim_type, created_at in results:
        with st.expander(f"{name} - {industry} - {claim_type} ({created_at})"):
            show_match_results(buyer_id)
    
    conn.close()
```

---

## Database Schema Reference

### Key Tables for UI

**buyer_requests:**
- `buyer_request_id` - Primary key
- `buyer_name` - Buyer company name
- `industry` - Industry type
- `claim_type_needed` - Required claim type
- `program_type` - Insurance program type
- `priority_geography`, `priority_claims`, `priority_industry`, `priority_services`, `priority_reporting`, `priority_technology`, `priority_cost` - Priority values (1-5)
- `narrative_request` - Natural language request
- `excluded_vendors` - Comma-separated vendor names

**buyer_required_states:**
- `buyer_request_id` - Foreign key to buyer_requests
- `state_code` - Two-letter state code (MN, WI, etc.)

**buyer_required_services:**
- `buyer_request_id` - Foreign key to buyer_requests
- `service_name` - Service identifier

**match_results:**
- `buyer_request_id` - Foreign key to buyer_requests
- `vendor_id` - Foreign key to vendors
- `total_score` - Overall score (0-100)
- `rank` - Vendor rank (1, 2, 3, etc.)
- `geography_score`, `claims_score`, `industry_score`, `service_score`, `reporting_score`, `performance_score`, `technology_score`, `data_quality_score` - Category scores
- `reason_codes` - JSON array of reason codes
- `risk_flags` - JSON array of risk flags
- `human_review_required` - Boolean (0 or 1)

**vendors:**
- `vendor_id` - Primary key
- `vendor_name` - Vendor company name
- `headquarters_state` - HQ location
- `company_size` - Size category
- `pricing_level` - Pricing tier
- `satisfaction_score` - Client satisfaction (0-100)
- `reporting_score` - Reporting capability (0-10)

---

## Design Requirements

### Accessibility (ADA/WCAG Compliance)

**Required:**
- ✅ Keyboard navigation for all controls
- ✅ Proper heading hierarchy (H1, H2, H3)
- ✅ Clear labels for all inputs
- ✅ WCAG AA color contrast (4.5:1 for text)
- ✅ Descriptive error messages
- ✅ Screen reader compatibility
- ✅ Visible focus indicators

**Streamlit Built-in Features:**
- Streamlit handles most accessibility by default
- Use semantic components (st.header, st.subheader)
- Add labels to all inputs
- Use st.warning, st.error for clear visual feedback

### Visual Design

**Style Guidelines:**
- Clean, professional appearance
- Use Streamlit's default theme (can customize later)
- Clear visual hierarchy
- Consistent spacing
- Color-coded feedback (green = good, yellow = warning, red = review needed)

**Recommended Layout:**
- Wide layout (`layout="wide"`)
- Two-column design for match results
- Expandable sections for vendor details
- Progress bars for score visualization

---

## Success Criteria

By the end of Phase 8, you should have:

- ✅ Working Streamlit app (`app.py`)
- ✅ Buyer request form with all required fields
- ✅ Integration with matching engine
- ✅ Match results display with:
  - Top 3-5 vendors
  - Score breakdowns
  - Reason codes (formatted)
  - Warning flags (formatted)
  - Human review indicators
- ✅ Score visualizations (charts/progress bars)
- ✅ Feedback collection form
- ✅ Vendor directory browser
- ✅ Past results viewer
- ✅ Accessible design (keyboard navigation, labels, contrast)
- ✅ No crashes on edge cases (invalid input, no results, etc.)

---

## Key Commands

### Running the App

```bash
# Install Streamlit first (if not installed)
pip install streamlit plotly

# Run the app
streamlit run app.py

# Open in browser at http://localhost:8501
```

### Testing the App

```bash
# Run matching engine manually
python scripts/match_vendors.py 1

# Run validation suite
python scripts/validate_matches.py

# Check database
python -c "import sqlite3; conn = sqlite3.connect('database/tpa_match_demo.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM buyer_requests'); print(f'Buyer requests: {cursor.fetchone()[0]}')"
```

### Useful Database Queries

```python
# Get all buyer requests
cursor.execute("SELECT * FROM buyer_requests ORDER BY created_at DESC")

# Get match results for a buyer
cursor.execute("""
    SELECT v.vendor_name, m.total_score, m.rank
    FROM match_results m
    JOIN vendors v ON m.vendor_id = v.vendor_id
    WHERE m.buyer_request_id = ?
    ORDER BY m.rank
""", (buyer_id,))

# Get all states a vendor serves
cursor.execute("""
    SELECT state_code 
    FROM vendor_states 
    WHERE vendor_id = ?
""", (vendor_id,))
```

---

## Important Files

### Documentation
- `tpa-match-demo-docs/01_project_brief.md` - Project overview
- `tpa-match-demo-docs/02_data_model.md` - Data structure
- `tpa-match-demo-docs/03_matching_logic.md` - Scoring rules
- `tpa-match-demo-docs/04_validation_rules.md` - Quality rules
- `tpa-match-demo-docs/05_security_accessibility.md` - Security & ADA requirements

### Backend Scripts
- `scripts/match_vendors.py` - Matching engine (900 lines)
- `scripts/create_database.py` - Database schema
- `scripts/seed_sample_data.py` - Sample data generation

### Validation
- `VALIDATION_TESTING_GUIDE.md` - Testing documentation
- `scripts/validate_matches.py` - Validation suite
- `data/validation_scenarios.json` - Test scenarios

### Database
- `database/tpa_match_demo.db` - SQLite database (24 vendors, 15 buyers, 77 match results)

---

## Common Pitfalls to Avoid

### 1. Don't Modify the Matching Engine
**The matching logic is complete and validated.** Just call it as a subprocess:
```python
subprocess.run(['python', 'scripts/match_vendors.py', str(buyer_id)])
```

### 2. Handle Missing Data Gracefully
Some vendors have NULL values for optional fields. Always check before displaying:
```python
headquarters = vendor.get('headquarters_state') or "Not specified"
```

### 3. Parse JSON Fields
Reason codes and risk flags are stored as JSON strings:
```python
reason_codes = json.loads(reason_codes_json)
```

### 4. Use Parameterized Queries
Prevent SQL injection:
```python
cursor.execute("SELECT * FROM vendors WHERE vendor_id = ?", (vendor_id,))
```

### 5. Test with All 15 Buyer Scenarios
The database has 15 pre-existing buyers. Test your UI displays all of them correctly.

---

## Optional Enhancements

**If you have extra time:**

1. **Export Results** - Add PDF/CSV export of match results
2. **Match Comparison** - Compare 2-3 vendors side-by-side
3. **Saved Searches** - Allow users to save buyer profiles
4. **Admin Panel** - Add/edit vendors through UI
5. **Real-time Updates** - Show matching progress bar
6. **Email Results** - Send match results via email
7. **Custom Themes** - Add company branding options

**Don't build these unless Phase 8 core requirements are done first.**

---

## Testing Checklist

Before considering Phase 8 complete, test:

- [ ] Can submit a new buyer request with all fields
- [ ] Match results display correctly for all 15 existing buyers
- [ ] Score breakdowns add up to ~100 points
- [ ] Reason codes are formatted and readable
- [ ] Risk flags display prominently
- [ ] Human review warnings are visible
- [ ] Can provide feedback on results
- [ ] Can browse vendor directory
- [ ] Can filter/search vendors
- [ ] Can view past results
- [ ] Keyboard navigation works
- [ ] No crashes on invalid input
- [ ] No crashes when no vendors match
- [ ] App loads quickly (<3 seconds)

---

## Phase 9 Preview (Not Your Task)

After you complete Phase 8, the next agent will add AI explanation features:
- Natural language request parsing (convert text to structured fields)
- AI-generated explanations from reason codes
- Hallucination detection using validation framework

**You don't need to worry about this** - just build a solid UI that displays the structured data.

---

## Questions or Issues?

### Documentation References
- **Matching logic:** `tpa-match-demo-docs/03_matching_logic.md`
- **Data model:** `tpa-match-demo-docs/02_data_model.md`
- **Database schema:** `scripts/create_database.py`
- **Security/accessibility:** `tpa-match-demo-docs/05_security_accessibility.md`

### Validation Testing
If you need to verify your UI displays correct data:
```bash
python scripts/validate_matches.py
```

### Re-generate Match Results
If you need fresh match results:
```bash
python scripts/match_vendors.py --all
```

### Database Inspection
```bash
# View all tables
python -c "import sqlite3; conn = sqlite3.connect('database/tpa_match_demo.db'); cursor = conn.cursor(); cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\"'); [print(r[0]) for r in cursor.fetchall()]"

# Count records
python -c "import sqlite3; conn = sqlite3.connect('database/tpa_match_demo.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM match_results'); print(f'Match results: {cursor.fetchone()[0]}')"
```

---

## Project Status

| Phase | Status | Pass Rate |
|-------|--------|-----------|
| 0-1: Documentation | ✅ Complete | N/A |
| 2: Database Schema | ✅ Complete | N/A |
| 3: Data Cleaning | ✅ Complete | N/A |
| 4: Database Creation | ✅ Complete | N/A |
| 5: Sample Data | ✅ Complete | N/A |
| 6: Matching Engine | ✅ Complete | 100% |
| 7: Validation | ✅ Complete | 100% |
| **8: Streamlit UI** | **← YOU ARE HERE** | **TBD** |
| 9: AI Explanation | ⏳ Pending | TBD |

---

## Summary

**You are building the frontend for a fully-functional backend.**

- Matching engine: ✅ Complete and validated
- Database: ✅ Populated with 24 vendors and 15 buyer scenarios
- Match results: ✅ 77 pre-generated results ready to display
- Validation: ✅ 100% pass rate on all tests

**Your focus:** Create a clean, accessible Streamlit UI that:
1. Collects buyer requirements
2. Calls the matching engine
3. Displays results beautifully
4. Collects user feedback

**Time estimate:** 8-12 hours for core functionality

**Success metric:** User can submit a request and see ranked, explained vendor matches with clear visual feedback.

Good luck! The backend is rock-solid - focus on making the user experience excellent. 🚀
