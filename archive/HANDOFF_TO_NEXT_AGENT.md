# Handoff Prompt for Next Agent Session

## Project Status Summary

I'm building a **TPA Match Demo** - a decision-support platform for matching employers with Third-Party Administrator (TPA) vendors. This is a portfolio/learning project demonstrating structured data matching, AI-assisted workflows, and validation practices.

**Core principle:** Build a structured, explainable matching system - NOT a black-box chatbot. AI assists with parsing/explanation, but deterministic scoring logic makes the actual recommendations.

## What's Complete ✅

### Phase 0-2: Project Setup & Data
- ✅ Project documentation in `tpa-match-demo-docs/` folder (8 files)
- ✅ Database schema designed with fully normalized structure (`scripts/create_database.py`)
  - Main vendor/buyer tables
  - Junction tables (vendor_states, vendor_claim_types, etc.)
  - Match results tables
  - **NEW:** Mapping tables for data cleaning (state_mappings, claim_type_mappings, etc.)
- ✅ **25 diverse vendors** created in `scripts/seed_sample_data.py`
- ✅ **15 buyer scenarios** created in `scripts/seed_sample_data.py`
- ✅ **Messy raw data** created: `data/raw/vendor_profiles_raw.csv`
- ✅ **Data cleaning script** complete: `scripts/clean_data.py`
- ✅ **Environment test script** created: `scripts/test_environment.py`
- ✅ **Requirements file** created: `requirements.txt`

### Key Design Decisions Documented:
- **Priority scale:** 1-5 (5=critical, 3=moderate default, 1=very low)
- **Priority weight calculation:** Multiplier approach then normalize to 100 points
- **Stale data threshold:** 180 days, calculated dynamically
- **Database schema:** Fully normalized with enhanced junction tables
- **Priority UI:** Sliders with user-friendly labels (for Phase 8)

All documented in: `tpa-match-demo-docs/08_design_decisions_open_questions.md`

## FIRST STEP: Environment Setup ⚙️

**SQLite is built into Python - no separate installation needed!**

### 1. Verify Your Environment

```bash
python scripts/test_environment.py
```

This will check:
- ✓ Python version
- ✓ SQLite availability (built-in)
- ✓ Required modules (pandas, etc.)

### 2. Install Dependencies (if needed)

```bash
pip install -r requirements.txt
```

Currently only needs: `pandas>=2.0.0`

### Expected Output:
```
======================================================================
Environment Check
======================================================================

✓ Python version: 3.x.x
  Location: C:\...

Checking required modules:
  ✓ sqlite3        - Built-in SQLite support
  ✓ pandas         - Data manipulation
  ✓ pathlib        - File path handling
  ...

Testing SQLite connection...
  ✓ SQLite version: 3.x.x

✅ Your environment is ready to go!
```

## Next Steps (Phase 3-6)

### **STEP 1: Test the Data Cleaning Pipeline**

```bash
python scripts/clean_data.py
```
- Should output cleaned CSV to `data/clean/vendors_cleaned.csv`
- Should create issues log at `data/clean/data_quality_issues.json`
- Review output to see normalization in action

### **STEP 2: Create the Database**

```bash
python scripts/create_database.py
```
- Creates SQLite DB at `database/tpa_match_demo.db`
- Includes all tables (vendors, buyers, mappings, etc.)
- You should see: "Database created successfully at: database/tpa_match_demo.db"

### **STEP 3: Seed the Database**

```bash
python scripts/seed_sample_data.py
```
- Loads 25 vendors and 15 buyer scenarios
- Uses clean, structured data
- You should see row counts for each table

### **STEP 4: Build Matching Engine (Phase 6)**

Create `scripts/match_vendors.py` to implement the scoring logic:

**Required functionality:**
1. Accept buyer_request_id as input
2. Apply hard filters (required states, excluded vendors, etc.)
3. Calculate adjusted scoring weights based on priorities
4. Score each vendor across 8 categories (100 points total):
   - Geographic fit (20 points default)
   - Claims capability fit (20 points)
   - Industry/client fit (15 points)
   - Service capability fit (15 points)
   - Reporting/analytics fit (10 points)
   - Performance fit (10 points)
   - Technology fit (5 points)
   - Data quality/confidence (5 points)
5. Generate reason codes (structured)
6. Generate warning codes
7. Set human review flags
8. Return top 3-5 ranked vendors
9. Save results to `match_results` table

**Key references for scoring logic:**
- `tpa-match-demo-docs/03_matching_logic.md` - Complete scoring rules
- `tpa-match-demo-docs/08_design_decisions_open_questions.md` - Priority weight calculations

**Database queries needed:**
- JOIN vendors with vendor_states, vendor_claim_types, etc.
- JOIN buyer_requests with buyer_required_states, buyer_required_services
- Calculate staleness: `(current_date - last_updated) > 180 days`

## Current Project Structure

```
TPA Demo/
├── tpa-match-demo-docs/          # Complete project documentation (8 files)
├── data/
│   ├── raw/
│   │   └── vendor_profiles_raw.csv    # Messy data
│   ├── clean/                          # Cleaned output goes here
│   └── DATA_CLEANING_README.md
├── docs/
│   └── data_cleaning_architecture.md
├── scripts/
│   ├── test_environment.py             # ✅ NEW - Check Python setup
│   ├── create_database.py              # DB schema
│   ├── seed_sample_data.py             # 25 vendors + 15 scenarios
│   └── clean_data.py                   # Data cleaning
├── requirements.txt                     # ✅ NEW - Dependencies
└── database/                            # Will contain .db file
```

## Important Context

**Tech Stack:**
- Python + pandas
- SQLite (built into Python - no installation needed!)
- Streamlit (for UI in Phase 8)
- OpenAI API optional (for AI explanation layer in Phase 9)

**Project Philosophy:**
- Structured data and deterministic logic are the foundation
- AI is an explanation layer, NOT the decision engine
- Human-in-the-loop for trust
- Validation/evaluation is a first-class feature
- Transparency over "AI magic"

## Quick Start Commands (In Order)

```bash
# 1. Check environment
python scripts/test_environment.py

# 2. Install dependencies (if needed)
pip install -r requirements.txt

# 3. Test data cleaning (optional but recommended)
python scripts/clean_data.py

# 4. Create database
python scripts/create_database.py

# 5. Seed database with vendors and buyers
python scripts/seed_sample_data.py

# 6. Build matching engine (next major task!)
# Create scripts/match_vendors.py
```

## Common Questions

**Q: Do I need to install SQLite?**
A: No! SQLite comes built into Python. Just verify with `test_environment.py`.

**Q: What if pandas is missing?**
A: Run `pip install pandas` or `pip install -r requirements.txt`

**Q: Should I use the cleaned CSV or the seed data?**
A: Use `seed_sample_data.py` for now - it has complete structured data.

**Q: What's the difference between `priority_cost` and other priorities?**
A: `priority_cost` affects filtering/vendor selection, not direct scoring weights.

## Files to Reference

**Most Important:**
1. `tpa-match-demo-docs/03_matching_logic.md` - Scoring rules and reason codes
2. `tpa-match-demo-docs/08_design_decisions_open_questions.md` - All design decisions
3. `scripts/seed_sample_data.py` - See vendor and buyer data structure
4. `scripts/create_database.py` - Database schema

## Success Criteria for Next Session

By end of next session, you should have:
- ✅ Environment verified (SQLite working)
- ✅ Database created and seeded
- ✅ Matching engine script that takes buyer_request_id and returns ranked vendors
- ✅ Scoring logic implemented with adjustable weights
- ✅ Reason codes and warnings generated
- ✅ Results saved to match_results table
- ✅ Tested against 2-3 buyer scenarios manually

**Start with environment setup, then build the matching engine!**
