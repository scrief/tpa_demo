# TPA Match Demo

**A sophisticated vendor matching system for Third Party Administrators (TPAs) in the insurance claims space.**

**Status:** Phase 9 Complete - AI Features Integrated  
**Brand:** Commonpoint  
**Ready to Demo:** Yes (with API key configuration)

---

## Quick Start

### Launch the App

```bash
streamlit run app.py
```

**Opens at:** `http://localhost:8501`

### Enable AI Features (Optional)

1. Copy the template:
   ```bash
   cp .env.template .env
   ```

2. Configure your AI provider in `.env`:
   
   **Option A - Google Gemini (Default):**
   ```
   AI_PROVIDER=gemini
   GOOGLE_API_KEY=your_gemini_api_key_here
   GEMINI_PARSING_MODEL=gemini-2.5-flash
   GEMINI_EXPLANATION_MODEL=gemini-2.5-flash
   ```
   Get your key from: https://aistudio.google.com/app/apikey
   
   **Option B - OpenAI:**
   ```
   AI_PROVIDER=openai
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_PARSING_MODEL=gpt-4o
   OPENAI_EXPLANATION_MODEL=gpt-4o-mini
   ```
   Get your key from: https://platform.openai.com/api-keys

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Restart the app

---

## What This Is

A demo application that matches insurance buyers with TPA vendors using:
- **Deterministic scoring** across 8 categories
- **Priority-based weighting** (1-5 scale)
- **Transparent reason codes** explaining every ranking
- **Human review flags** for quality assurance
- **100% validated** matching engine
- **AI-powered features** for natural language parsing and explanations

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

### 🤖 AI-Powered Features (Phase 9)
- Natural language parsing of buyer requests
- Dual AI provider support (Google Gemini or OpenAI)
- AI-generated plain-English explanations
- Hallucination detection for accuracy
- Follow-up questions for better matches
- All AI features optional and transparent

---

## Project Structure

```
TPA Demo/
├── app.py                              # Streamlit web application (with AI features)
├── .env.template                        # API key template (Phase 9)
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
│   ├── clean_data.py                   # Data cleaning
│   ├── parse_narrative_request.py      # AI parsing (Phase 9)
│   ├── generate_explanation.py         # AI explanations (Phase 9)
│   ├── detect_hallucinations.py        # Hallucination detection (Phase 9)
│   ├── generate_followup_questions.py  # Follow-up questions (Phase 9)
│   ├── add_ai_interactions_table.py    # DB migration (Phase 9)
│   └── test_ai_features.py             # AI test suite (Phase 9)
├── data/
│   ├── validation_scenarios.json       # 25 test scenarios
│   ├── edge_case_scenarios.json        # Edge case documentation
│   └── ai_test_cases.json              # AI feature tests (Phase 9)
├── tpa-match-demo-docs/                # Full project specifications
├── PROJECT_OVERVIEW.md                 # Project overview and status
├── PHASE_8_UI_GUIDE.md                 # UI implementation guide
├── PHASE_8_COMPLETION_SUMMARY.md       # Phase 8 results
├── PHASE_9_COMPLETION_SUMMARY.md       # Phase 9 results (AI features)
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

# Test AI features (Phase 9)
python scripts/test_ai_features.py --all
python scripts/test_ai_features.py --test parsing

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
- openai >= 1.0.0 (Phase 9 - optional)
- python-dotenv >= 1.0.0 (Phase 9 - optional)

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
| 9 | ✅ Complete | AI explanation layer |

---

## Documentation

**Getting Started:**
- `README.md` - This file
- `PROJECT_OVERVIEW.md` - Project status and quick reference

**Phase 8 (UI):**
- `PHASE_8_UI_GUIDE.md` - Implementation guide (600+ lines)
- `PHASE_8_COMPLETION_SUMMARY.md` - Completion report
- `PHASE_8_UPDATES.md` - Post-launch improvements and bug fixes

**Phase 9 (AI Features):**
- `PHASE_9_COMPLETION_SUMMARY.md` - AI features completion report
- `.env.template` - API key configuration template
- `data/ai_test_cases.json` - AI test scenarios

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
- 1,270+ lines (Streamlit UI with AI features)
- 700+ lines (validation suite)
- 2,400+ lines (AI features - Phase 9)
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
- AI integration with hallucination prevention
- Graceful degradation and user control
- Prompt engineering for accuracy

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

**For Demos:**
1. Set up OpenAI API key (optional): Copy `.env.template` to `.env`
2. Test the app: `streamlit run app.py`
3. Try AI parsing: Describe needs in natural language
4. Generate AI explanations: Click button on match results
5. Review hallucination detection in action

**For Development:**
1. Run AI tests: `python scripts/test_ai_features.py --all`
2. Optimize prompts based on results
3. Collect user feedback on AI features
4. Monitor hallucination rates
5. Iterate on prompt engineering

---

## License

This is a demo/portfolio project. Not for production use without proper review.

---

**Status:** ✅ Phase 9 Complete - AI Features Integrated  
**Launch:** `streamlit run app.py`  
**Brand:** Commonpoint Professional Identity  
**Quality:** Production-ready with 100% test coverage  
**AI Features:** Optional, transparent, and hallucination-protected

🚀 Ready to show off with AI-powered enhancements!
