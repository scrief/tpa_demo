# Data Cleaning Process - Quick Start Guide

## What We Built

### 1. Messy Raw Data
**File:** `data/raw/vendor_profiles_raw.csv`

Contains 28 vendor records with realistic data quality issues:
- Duplicate vendor names (different spellings)
- Inconsistent state formats ("Minnesota", "MN", "MN, WI, IA")
- Multiple claim type formats ("WC", "Workers Comp", "Workers' Compensation")
- Various date formats ("2/1/2026", "Feb 1 2026", "11-18-2025")
- Different delimiters (commas, semicolons, pipes, slashes)
- Missing values
- Case inconsistencies

### 2. Cleaning Script
**File:** `scripts/clean_data.py`

Processes messy data and produces clean, normalized output:
- Standardizes vendor names
- Normalizes states to 2-letter codes
- Normalizes claim types to standard taxonomy
- Parses various date formats to YYYY-MM-DD
- Handles missing values
- Detects potential duplicates (using string similarity)
- Flags data quality issues
- Logs all issues to JSON file

### 3. Mapping Tables in Database
**Added to:** `scripts/create_database.py`

New tables for persistent learning architecture:
- `state_mappings` - Learn state name variations
- `claim_type_mappings` - Learn claim type variations
- `industry_mappings` - Learn industry variations
- `vendor_name_mappings` - Track vendor deduplication decisions
- `data_quality_queue` - Human review queue for ambiguous data
- `vendor_source_history` - Track data provenance and changes

## How to Use

### Step 1: Run the Cleaning Script

```bash
# From project root
python scripts/clean_data.py
```

**Output:**
```
======================================================================
TPA Match Demo - Data Cleaning Script
======================================================================

Loading raw data from: data/raw/vendor_profiles_raw.csv
✓ Loaded 28 rows

Detecting potential duplicates...
⚠ Found 3 potential duplicate(s):
  - Row 0: 'NorthStar Claims' <-> Row 1: 'North Star Claims' (similarity: 92%)
  - Row 2: 'Midwest TPA Group' <-> Row 3: 'MIDWEST TPA GROUP' (similarity: 100%)
  - Row 7: 'Great Lakes Claims' <-> Row 8: 'Great Lakes Claims' (similarity: 92%)

Saving cleaned data to: data/clean/vendors_cleaned.csv
✓ Saved 28 cleaned records
Saving data quality issues to: data/clean/data_quality_issues.json
✓ Logged 15 data quality issue(s)

======================================================================
CLEANING SUMMARY
======================================================================
Total records processed: 28
Records with data quality flags: 8
Records missing states: 0
Records missing claim types: 0
Records missing satisfaction score: 3
Potential duplicates found: 3

✓ Data cleaning complete!
```

### Step 2: Review Cleaned Output

**File:** `data/clean/vendors_cleaned.csv`

Contains normalized data with these fields:
- `vendor_name` - Standardized name
- `headquarters_state` - 2-letter code
- `states_served` - Comma-separated 2-letter codes
- `claim_types` - Comma-separated normalized types
- `industries` - Comma-separated normalized industries
- `years_in_business` - Integer
- `satisfaction_score` - Float (0-100)
- `avg_response_time_days` - Float
- `last_updated` - YYYY-MM-DD format
- `source` - Data source name
- `contact_email` - Email address
- `data_quality_flags` - Comma-separated flags for issues

### Step 3: Review Issues Log

**File:** `data/clean/data_quality_issues.json`

JSON log of all data quality issues found:
```json
[
  {
    "row": 8,
    "vendor_name_raw": "Great Lakes Claims LLC",
    "issues": [
      {
        "field": "states",
        "issue": "unknown_states",
        "raw_value": "OH; MI; IN; KY",
        "unknown": []
      }
    ]
  },
  {
    "issue_type": "potential_duplicate",
    "row1": 0,
    "row2": 1,
    "vendor1": "NorthStar Claims",
    "vendor2": "North Star Claims",
    "similarity": 0.92
  }
]
```

## What Gets Cleaned

### State Normalization
```
"Minnesota" → "MN"
"Wisc" → "WI"
"MN, WI, IA" → "MN,WI,IA"
"MN; WI; IA" → "MN,WI,IA"
```

### Claim Type Normalization
```
"WC" → "workers_comp"
"Workers Comp" → "workers_comp"
"Workers' Compensation" → "workers_comp"
"GL" → "general_liability"
"Auto Liability" → "auto_liability"
```

### Industry Normalization
```
"Mfg" → "manufacturing"
"Health Care" → "healthcare"
"Prof Services" → "professional_services"
"Tech" → "technology"
```

### Date Normalization
```
"2/1/2026" → "2026-02-01"
"Feb 1 2026" → "2026-02-01"
"11-18-2025" → "2025-11-18"
"Nov 2025" → "2025-11-01"
```

### Vendor Name Standardization
```
"NorthStar Claims LLC" → "NorthStar Claims"
"MIDWEST TPA GROUP" → "Midwest TPA Group"
"Great Lakes Claims LLC" → "Great Lakes Claims"
```

## Data Quality Flags

The cleaning script adds flags for these issues:

| Flag | Meaning |
|------|---------|
| `unknown_headquarters_state` | Headquarters state couldn't be parsed |
| `unknown_states` | One or more states in coverage couldn't be parsed |
| `unknown_claim_types` | One or more claim types couldn't be parsed |
| `unparseable_date` | Date couldn't be parsed to standard format |
| `missing_vendor_name` | No vendor name provided |
| `missing_states` | No state coverage provided |
| `missing_claim_types` | No claim types provided |

## Next Steps

### For MVP:
1. ✅ Run `clean_data.py` to process messy data
2. Review `vendors_cleaned.csv` and `data_quality_issues.json`
3. Manually resolve duplicates and ambiguous cases
4. Update `seed_sample_data.py` to load from cleaned CSV (or keep current structure)

### For Future Production:
1. Create review queue UI using `data_quality_queue` table
2. Build mapping management interface
3. Implement incremental import workflow
4. Add fuzzy matching with confidence scores
5. Enable learning from human corrections
6. Build data lineage tracking dashboard

## Design Principles Demonstrated

✅ **Real-world messiness** - Multiple formats, delimiters, missing data  
✅ **Systematic normalization** - Controlled vocabularies, consistent formats  
✅ **Duplicate detection** - String similarity algorithms  
✅ **Data quality tracking** - Flag issues for review  
✅ **Auditability** - Log all issues for human review  
✅ **Extensibility** - Mapping tables support future learning  

## Interview Story

> "I built a data cleaning pipeline that handles real-world messy vendor data from multiple sources. The system normalizes states, claim types, and dates using controlled vocabularies, detects duplicates using string similarity, and flags data quality issues for human review. I designed persistent mapping tables so the system can learn from human corrections and become more automated over time. This demonstrates understanding of operational data workflows where ongoing data intake requires both automation and human oversight."
