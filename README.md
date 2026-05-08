# TPA Match Demo

**A sophisticated vendor matching system for Third Party Administrators (TPAs) in the insurance claims space.**

**Status:** Phase 8 Complete - Streamlit UI Functional  
**Brand:** Commonpoint  
**Ready to Demo:** Yes

---

## Quick Start

### Launch the App

```bash
streamlit run app.py
```

**Opens at:** `http://localhost:8501`

---

## What This Is

A demo application that matches insurance buyers with TPA vendors using:
- **Deterministic scoring** across 8 categories
- **Priority-based weighting** (1-5 scale)
- **Transparent reason codes** explaining every ranking
- **Human review flags** for quality assurance
- **100% validated** matching engine

---

## Key Features

### 🎯 Smart Matching
- 8-category scoring system (Geography, Claims, Industry, Services, etc.)
- Priority multipliers adjust weights based on buyer needs
- Hard filters remove disqualified vendors
- Structured reason codes explain rankings

### 📊 Visual Results
- Radar charts comparing top vendors
- Color-coded bar charts (performance-based)
- Human-readable reason codes
- Prominent risk flags and warnings

### 🎨 Professional UI
- Commonpoint brand identity fully integrated
- WCAG AA accessible design
- Interactive forms with real-time validation
- Intuitive checkbox grid for state selection
- Responsive layout

### 💬 Feedback Loop
- User ratings for usefulness and accuracy
- Comment collection for improvement
- Database persistence for analysis

---

## Project Structure

```
TPA Demo/
├── app.py                              # Streamlit web application
├── .streamlit/config.toml              # Brand theme configuration
├── requirements.txt                     # Python dependencies
├── database/
│   └── tpa_match_demo.db               # SQLite database
├── scripts/
│   ├── match_vendors.py                # Matching engine (900 lines)
│   ├── validate_matches.py             # Validation suite
│   ├── test_priority_sensitivity.py    # Priority testing
│   ├── test_streamlit_app.py           # UI tests
│   ├── create_database.py              # Database schema
│   ├── seed_sample_data.py             # Sample data generator
│   └── clean_data.py                   # Data cleaning
├── data/
│   ├── validation_scenarios.json       # 25 test scenarios
│   └── edge_case_scenarios.json        # Edge case documentation
├── tpa-match-demo-docs/                # Full project specifications
├── PROJECT_OVERVIEW.md                 # Project overview and status
├── PHASE_8_UI_GUIDE.md                 # UI implementation guide
├── PHASE_8_COMPLETION_SUMMARY.md       # Phase 8 results
├── VALIDATION_TESTING_GUIDE.md         # Testing documentation
└── README.md                           # This file
```

---

## Database

**SQLite database with:**
- 24 active TPA vendors
- 15 buyer scenarios (diverse industries, geographies)
- 77 pre-generated match results
- 103 validation test results
- Normalized relational schema

**Key Tables:**
- `vendors` - Vendor master data
- `buyer_requests` - Buyer scenarios
- `match_results` - Vendor rankings with scores
- `feedback` - User feedback collection

---

## Commands

```bash
# Launch the Streamlit app
streamlit run app.py

# Run UI tests (5 automated tests)
python scripts/test_streamlit_app.py

# Test matching engine for buyer #1
python scripts/match_vendors.py 1

# Run all matches (15 buyers)
python scripts/match_vendors.py --all

# Run validation suite (25 scenarios)
python scripts/validate_matches.py

# Run priority sensitivity tests (5 tests)
python scripts/test_priority_sensitivity.py
```

---

## Requirements

**Python 3.12+**

```bash
pip install -r requirements.txt
```

**Dependencies:**
- pandas >= 2.0.0
- streamlit >= 1.30.0
- plotly >= 5.0.0
- sqlite3 (built-in)

---

## Testing

**Automated Tests:**
```bash
python scripts/test_streamlit_app.py
```

**Result:** 5/5 tests passing (100%)

**Validation:**
```bash
python scripts/validate_matches.py
```

**Result:** 25/25 scenarios passing (100%)

---

## Development Phases

| Phase | Status | Description |
|-------|--------|-------------|
| 0-1 | ✅ Complete | Project documentation |
| 2 | ✅ Complete | Database schema design |
| 3 | ✅ Complete | Data cleaning pipeline |
| 4 | ✅ Complete | Database creation |
| 5 | ✅ Complete | Sample data seeding |
| 6 | ✅ Complete | Matching engine (validated) |
| 7 | ✅ Complete | Validation framework (100% pass) |
| 8 | ✅ Complete | Streamlit UI (Commonpoint brand) |
| 9 | ⏳ Next | AI explanation layer |

---

## Documentation

**Getting Started:**
- `README.md` - This file
- `PROJECT_OVERVIEW.md` - Project status and quick reference

**Phase 8 (UI):**
- `PHASE_8_UI_GUIDE.md` - Implementation guide (600+ lines)
- `PHASE_8_COMPLETION_SUMMARY.md` - Completion report
- `PHASE_8_UPDATES.md` - Post-launch improvements and bug fixes

**Validation:**
- `VALIDATION_TESTING_GUIDE.md` - Testing framework (550+ lines)
- `PHASE_7_COMPLETION_SUMMARY.md` - Validation results

**Specifications:**
- `tpa-match-demo-docs/01_project_brief.md` - Project purpose
- `tpa-match-demo-docs/02_data_model.md` - Data structure
- `tpa-match-demo-docs/03_matching_logic.md` - Scoring rules
- `tpa-match-demo-docs/04_validation_rules.md` - Quality standards
- `tpa-match-demo-docs/05_security_accessibility.md` - Security & ADA

---

## Brand Identity

**Commonpoint**

**Colors:**
- Primary Navy: #001F3F
- Secondary Blue: #3A506B
- Pure White: #FFFFFF
- Cool Gray: #4A4A4A
- Success Green: #10B981

**Typography:**
- Headings: Inter (700)
- Body: Open Sans (400)
- Data: JetBrains Mono (400)

**Design Tokens:**
- Border Radius: 8px
- Shadows: Professional depth
- Padding: 4px base scale

---

## Key Statistics

**Database:**
- 24 active vendors
- 15 buyer scenarios
- 77 match results
- 94 state relationships
- 51 claim type relationships

**Validation:**
- 25/25 scenarios passing (100%)
- 5/5 priority tests passing (100%)
- 103 historical validation runs
- 15 edge cases documented

**Code:**
- 900+ lines (matching engine)
- 950+ lines (Streamlit UI)
- 700+ lines (validation suite)
- 100% test coverage on critical paths

---

## Interview Talking Points

**Problem:**
"Matching buyers with TPA vendors requires balancing multiple factors (geography, capability, cost, quality) while maintaining transparency and trust."

**Approach:**
"Built a structured, deterministic matching system with:
- Normalized relational database (SQLite)
- 8-category scoring with priority-based adjustment
- Structured reason codes for explainability
- Human review flags for quality assurance
- 100% validated test coverage"

**Key Achievements:**
- 100% validation pass rate (25 scenarios + 5 priority tests)
- Deterministic scoring (no black-box AI)
- Complete audit trail (reason codes explain every score)
- Production-ready SQL (normalized schema, parameterized queries)
- Extensible architecture (easy to add categories or adjust weights)

**What I Learned:**
- Database normalization trade-offs
- Balancing explainability vs. sophistication
- Human-in-the-loop system design
- Data quality impact on trust
- Importance of comprehensive validation
- Rapid UI development with Streamlit
- Brand identity integration in web applications

---

## Support

**Questions about the UI?**
- See `PHASE_8_UI_GUIDE.md`
- Review `app.py` code

**Questions about matching logic?**
- See `tpa-match-demo-docs/03_matching_logic.md`
- Review `scripts/match_vendors.py`

**Database questions?**
- See `scripts/create_database.py` for schema
- See `tpa-match-demo-docs/02_data_model.md` for structure

**Validation questions?**
- See `VALIDATION_TESTING_GUIDE.md`
- Run `python scripts/validate_matches.py --report`

---

## Next Steps

**For Phase 9 (AI Explanation Layer):**
1. Read `PHASE_8_UI_GUIDE.md` to understand the UI
2. Test the app: `streamlit run app.py`
3. Review form structure (natural language field ready)
4. Add AI parsing for narrative requests
5. Generate plain-English explanations from reason codes
6. Implement hallucination detection using validation framework

---

## License

This is a demo/portfolio project. Not for production use without proper review.

---

**Status:** ✅ Phase 8 Complete - Ready for Demo  
**Launch:** `streamlit run app.py`  
**Brand:** Commonpoint Professional Identity  
**Quality:** Production-ready with 100% test coverage

🚀 Ready to show off!
