# Data Cleaning Architecture - Human-in-the-Loop Workflow

## Overview

This system is designed for ongoing, incremental data intake from multiple sources. It includes persistent mapping tables, human review workflows, and learning from corrections.

## Core Components

### 1. Persistent Mapping Tables (in database)

Store learned mappings to avoid re-cleaning the same data:

```sql
-- State name to standard code mappings
CREATE TABLE state_mappings (
    mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_value TEXT NOT NULL UNIQUE,
    canonical_value TEXT NOT NULL,
    confidence TEXT DEFAULT 'high',
    verified_by_human INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Claim type mappings
CREATE TABLE claim_type_mappings (
    mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_value TEXT NOT NULL UNIQUE,
    canonical_value TEXT NOT NULL,
    confidence TEXT DEFAULT 'high',
    verified_by_human INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Industry mappings
CREATE TABLE industry_mappings (
    mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_value TEXT NOT NULL UNIQUE,
    canonical_value TEXT NOT NULL,
    confidence TEXT DEFAULT 'high',
    verified_by_human INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Vendor name deduplication mappings
CREATE TABLE vendor_name_mappings (
    mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_name TEXT NOT NULL UNIQUE,
    canonical_name TEXT NOT NULL,
    canonical_vendor_id INTEGER,
    confidence TEXT DEFAULT 'high',
    verified_by_human INTEGER DEFAULT 0,
    merge_with_vendor_id INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (canonical_vendor_id) REFERENCES vendors(vendor_id)
);
```

### 2. Data Quality Review Queue

Track incoming data that needs human review:

```sql
CREATE TABLE data_quality_queue (
    queue_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file TEXT,
    source_row INTEGER,
    raw_data TEXT,  -- JSON blob of raw row data
    issue_type TEXT,  -- 'unknown_state', 'unknown_claim_type', 'duplicate_vendor', 'conflicting_data', 'missing_required'
    issue_description TEXT,
    status TEXT DEFAULT 'pending',  -- 'pending', 'reviewed', 'resolved', 'skipped'
    resolution TEXT,  -- JSON blob of human decision
    reviewed_by TEXT,
    reviewed_at TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### 3. Vendor Master Data with Source Tracking

Track which sources contributed to each vendor's data:

```sql
CREATE TABLE vendor_source_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_id INTEGER NOT NULL,
    source_name TEXT NOT NULL,
    source_file TEXT,
    source_row INTEGER,
    field_name TEXT,
    old_value TEXT,
    new_value TEXT,
    confidence TEXT,
    imported_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
);
```

## Cleaning Workflow

### Phase 1: Initial Auto-Cleaning

```python
def auto_clean_row(raw_row, mapping_tables):
    """
    Attempt automatic cleaning using learned mappings.
    Returns (cleaned_row, issues_for_review)
    """
    issues = []
    cleaned = {}
    
    # 1. Vendor name standardization
    vendor_name = standardize_vendor_name(raw_row['Vendor Name'])
    mapping = lookup_vendor_mapping(vendor_name, mapping_tables)
    if mapping:
        cleaned['vendor_name'] = mapping.canonical_name
        cleaned['canonical_vendor_id'] = mapping.canonical_vendor_id
    else:
        # Check for fuzzy match
        fuzzy_match = find_similar_vendor(vendor_name, threshold=0.85)
        if fuzzy_match:
            issues.append({
                'type': 'possible_duplicate',
                'field': 'vendor_name',
                'raw_value': vendor_name,
                'suggestion': fuzzy_match.canonical_name,
                'confidence': fuzzy_match.similarity_score
            })
        cleaned['vendor_name'] = vendor_name
    
    # 2. State normalization
    states = parse_state_list(raw_row['State Coverage'])
    cleaned_states = []
    for state in states:
        mapping = lookup_state_mapping(state, mapping_tables)
        if mapping:
            cleaned_states.append(mapping.canonical_value)
        else:
            # Try fuzzy match against state names/codes
            suggestion = fuzzy_match_state(state)
            if suggestion and suggestion.confidence > 0.8:
                cleaned_states.append(suggestion.canonical_value)
            else:
                issues.append({
                    'type': 'unknown_state',
                    'field': 'states',
                    'raw_value': state,
                    'suggestion': suggestion.canonical_value if suggestion else None
                })
    
    # 3. Claim type normalization
    # Similar logic...
    
    # 4. Date parsing
    # Try multiple date formats, flag if unparseable
    
    # 5. Missing value handling
    # Flag required fields that are missing
    
    return cleaned, issues
```

### Phase 2: Human Review UI

For each flagged issue, present a review interface:

**UI Elements:**

1. **Unknown State Review:**
   ```
   ⚠️ Unknown State Value
   
   Raw Value: "Wisc"
   Source: vendor_profiles_raw.csv, Row 5
   
   Suggested Mapping: Wisconsin (WI)
   Confidence: 95%
   
   Actions:
   [✓ Accept Suggestion]  [Manual Entry: ___]  [Skip]
   
   ☑ Remember this mapping for future imports
   ```

2. **Possible Duplicate Vendor:**
   ```
   ⚠️ Possible Duplicate Vendor
   
   New Entry: "North Star Claims"
   Existing: "NorthStar Claims" (ID: V001)
   Similarity: 92%
   
   Compare Data:
   ┌─────────────────┬──────────────────┬─────────────────┐
   │ Field           │ New Entry        │ Existing        │
   ├─────────────────┼──────────────────┼─────────────────┤
   │ Headquarters    │ MN               │ Minnesota       │
   │ States          │ MN WI IA IL      │ MN, WI, IA      │
   │ Satisfaction    │ 91               │ 91              │
   │ Last Updated    │ Feb 1 2026       │ 2/1/2026        │
   └─────────────────┴──────────────────┴─────────────────┘
   
   Actions:
   [Merge with Existing]  [Create New Vendor]  [Need More Info]
   
   If Merge:
   Field-by-field resolution:
   States: ☑ Add IL to existing  ☐ Keep existing only
   ```

3. **Conflicting Data:**
   ```
   ⚠️ Conflicting Data
   
   Vendor: Great Lakes Claims
   Field: Satisfaction Score
   
   Source A (Broker Database, 12/10/25): 87
   Source B (Proposal, Dec 2025): 85
   
   Resolution:
   ( ) Use Source A
   ( ) Use Source B  
   ( ) Use Average (86)
   ( ) Flag for investigation
   
   Confidence level: [High ▼] [Medium] [Low]
   
   Notes: ________________________________
   ```

### Phase 3: Learning from Review

After each human decision:

```python
def learn_from_review(review_decision):
    """
    Store human decisions as mappings for future imports.
    """
    if review_decision.type == 'unknown_state':
        # Store mapping
        db.insert_mapping(
            table='state_mappings',
            raw_value=review_decision.raw_value,
            canonical_value=review_decision.selected_value,
            verified_by_human=1,
            confidence='high'
        )
    
    elif review_decision.type == 'duplicate_vendor':
        if review_decision.action == 'merge':
            # Store vendor name mapping
            db.insert_mapping(
                table='vendor_name_mappings',
                raw_name=review_decision.new_vendor_name,
                canonical_name=review_decision.existing_vendor_name,
                canonical_vendor_id=review_decision.existing_vendor_id,
                verified_by_human=1
            )
            
            # Merge field-level data
            merge_vendor_data(
                source_vendor=review_decision.new_data,
                target_vendor_id=review_decision.existing_vendor_id,
                field_resolutions=review_decision.field_decisions
            )
```

### Phase 4: Incremental Import

When new data arrives:

```python
def import_new_data(csv_file):
    """
    Import new data using learned mappings and human review.
    """
    # 1. Load existing mappings from database
    mappings = load_all_mappings()
    
    # 2. Read raw CSV
    raw_data = pd.read_csv(csv_file)
    
    # 3. Auto-clean each row
    cleaned_rows = []
    review_queue = []
    
    for idx, row in raw_data.iterrows():
        cleaned, issues = auto_clean_row(row, mappings)
        
        if issues:
            # Add to review queue
            review_queue.append({
                'source_file': csv_file,
                'source_row': idx,
                'raw_data': row.to_json(),
                'issues': issues
            })
        else:
            # Fully auto-cleaned, ready to import
            cleaned_rows.append(cleaned)
    
    # 4. Import clean rows immediately
    import_clean_vendors(cleaned_rows)
    
    # 5. Save review queue to database
    save_review_queue(review_queue)
    
    # 6. Return summary
    return {
        'auto_imported': len(cleaned_rows),
        'needs_review': len(review_queue),
        'review_url': '/admin/data-quality-queue'
    }
```

## Ongoing Operations

### Daily Workflow:

1. **New data arrives** (email, SFTP, web form, etc.)
2. **Auto-import** runs, uses learned mappings
3. **Review queue** is populated with unknowns/conflicts
4. **Human reviewer** processes queue in web UI
5. **Mappings updated** from human decisions
6. **Next import** is more automatic

### Quality Metrics Dashboard:

```
📊 Data Quality Metrics (Last 30 Days)

Auto-Import Rate: 87%  ↑ 5%
├─ Fully Automated: 78%
├─ Low-Confidence Auto: 9%
└─ Required Review: 13%

Review Queue Status: 12 items pending
├─ Unknown States: 2
├─ Duplicate Vendors: 5
├─ Conflicting Data: 3
└─ Missing Required Fields: 2

Mapping Library Growth:
├─ State Mappings: 47 (23 human-verified)
├─ Claim Type Mappings: 31 (18 human-verified)
├─ Vendor Name Mappings: 15 (15 human-verified)

Data Confidence by Source:
├─ Broker Database: High (92% verified)
├─ Proposals: Medium (67% verified)
├─ Self Reported: Low (34% verified)
```

## MVP vs Future

### For MVP (Portfolio Demo):

- Basic auto-cleaning script with hardcoded rules
- Show examples of mapping tables
- Demo the messy → clean transformation once
- Document the human review workflow (but don't build full UI)

### For Production (Future):

- Full web UI for review queue
- API endpoints for data submission
- Automated email alerts for review queue
- Machine learning for fuzzy matching
- Audit trail for all decisions
- Rollback capability

## Benefits of This Architecture:

✅ **Scalable** - Handles ongoing data intake
✅ **Learning** - Gets smarter with each review
✅ **Auditable** - Tracks all decisions
✅ **Flexible** - Adapts to new data sources
✅ **Efficient** - Reduces manual work over time
✅ **Trustworthy** - Human oversight on ambiguous cases

