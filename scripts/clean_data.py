"""
Data Cleaning Script - TPA Match Demo

This script processes messy raw vendor data and produces clean, normalized output.

Purpose:
- Demonstrate handling of real-world messy data
- Standardize vendor names, states, claim types, dates
- Detect duplicates and conflicts
- Flag data quality issues
- Prepare data for database import

Input: data/raw/vendor_profiles_raw.csv
Output: data/clean/vendors_cleaned.csv
"""

import pandas as pd
import re
from datetime import datetime
from pathlib import Path
from difflib import SequenceMatcher
import json

# ============================================================================
# CONFIGURATION
# ============================================================================

RAW_DATA_PATH = Path("data/raw/vendor_profiles_raw.csv")
CLEAN_DATA_PATH = Path("data/clean/vendors_cleaned.csv")
ISSUES_LOG_PATH = Path("data/clean/data_quality_issues.json")

# Ensure output directory exists
CLEAN_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

# ============================================================================
# NORMALIZATION MAPPINGS
# ============================================================================

# State name to 2-letter code mapping
STATE_MAPPINGS = {
    # Full names
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
    "california": "CA", "colorado": "CO", "connecticut": "CT", "delaware": "DE",
    "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID",
    "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS",
    "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
    "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS",
    "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV",
    "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM", "new york": "NY",
    "north carolina": "NC", "north dakota": "ND", "ohio": "OH", "oklahoma": "OK",
    "oregon": "OR", "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC",
    "south dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT",
    "vermont": "VT", "virginia": "VA", "washington": "WA", "west virginia": "WV",
    "wisconsin": "WI", "wyoming": "WY", "district of columbia": "DC",
    
    # Common abbreviations
    "minn": "MN", "wisc": "WI", "penn": "PA", "calif": "CA", "colo": "CO",
    "conn": "CT", "mass": "MA", "miss": "MS", "okla": "OK", "tenn": "TN",
    "wash": "WA", "mfg": "manufacturing",
    
    # Special cases
    "dc": "DC", "d.c.": "DC"
}

# Claim type normalization
CLAIM_TYPE_MAPPINGS = {
    # Workers Compensation variations
    "wc": "workers_comp",
    "workers comp": "workers_comp",
    "workers' compensation": "workers_comp",
    "workers compensation": "workers_comp",
    "work comp": "workers_comp",
    "worker's comp": "workers_comp",
    
    # General Liability
    "gl": "general_liability",
    "general liability": "general_liability",
    "gen liability": "general_liability",
    "gen liab": "general_liability",
    
    # Auto Liability
    "al": "auto_liability",
    "auto": "auto_liability",
    "auto liability": "auto_liability",
    "auto liab": "auto_liability",
    
    # Property
    "property": "property",
    "prop": "property",
    
    # Professional Liability
    "professional liability": "professional_liability",
    "prof liability": "professional_liability",
    "prof liab": "professional_liability",
    "e&o": "professional_liability",
    
    # Occupational Accident
    "occupational accident": "occupational_accident",
    "occ accident": "occupational_accident",
    "occ acc": "occupational_accident",
}

# Industry normalization
INDUSTRY_MAPPINGS = {
    "mfg": "manufacturing",
    "manuf": "manufacturing",
    "manufacturing": "manufacturing",
    "construction": "construction",
    "const": "construction",
    "healthcare": "healthcare",
    "health care": "healthcare",
    "transportation": "transportation",
    "transport": "transportation",
    "retail": "retail",
    "hospitality": "hospitality",
    "education": "education",
    "edu": "education",
    "public entity": "public_entity",
    "public": "public_entity",
    "professional services": "professional_services",
    "prof services": "professional_services",
    "technology": "technology",
    "tech": "technology",
    "energy": "energy",
    "real estate": "real_estate",
    "realestate": "real_estate",
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def standardize_vendor_name(name):
    """
    Standardize vendor name for consistent comparison.
    - Remove extra whitespace
    - Standardize case
    - Remove common suffixes
    """
    if pd.isna(name):
        return None
    
    name = str(name).strip()
    
    # Remove common business suffixes for comparison
    suffixes = [" LLC", " Inc", " Inc.", " Corporation", " Corp", " Corp.", " Ltd", " Ltd."]
    for suffix in suffixes:
        if name.endswith(suffix):
            name = name[:-len(suffix)].strip()
    
    return name

def normalize_state(state_str):
    """
    Convert state name/abbreviation to standard 2-letter code.
    Returns uppercase 2-letter code or None if not recognized.
    """
    if pd.isna(state_str):
        return None
    
    state_str = str(state_str).strip().lower()
    
    # If already 2 letters and uppercase, return as-is
    if len(state_str) == 2 and state_str.upper() in [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC"
    ]:
        return state_str.upper()
    
    # Look up in mapping
    return STATE_MAPPINGS.get(state_str, None)

def parse_state_list(state_str):
    """
    Parse a messy state list into clean 2-letter codes.
    Handles various delimiters: commas, semicolons, pipes, spaces.
    """
    if pd.isna(state_str):
        return []
    
    # Replace various delimiters with comma
    state_str = str(state_str)
    state_str = re.sub(r'[;|/]', ',', state_str)
    
    # Split by comma or multiple spaces
    states = re.split(r'[,\s]{2,}|\s*,\s*', state_str)
    
    # Normalize each state
    normalized = []
    unknown = []
    
    for state in states:
        state = state.strip()
        if not state:
            continue
        
        normalized_state = normalize_state(state)
        if normalized_state:
            if normalized_state not in normalized:  # Avoid duplicates
                normalized.append(normalized_state)
        else:
            unknown.append(state)
    
    return normalized, unknown

def normalize_claim_type(claim_str):
    """
    Normalize claim type to standard taxonomy.
    """
    if pd.isna(claim_str):
        return None
    
    claim_str = str(claim_str).strip().lower()
    
    # Remove parenthetical notes like "(primary)"
    claim_str = re.sub(r'\s*\([^)]*\)', '', claim_str)
    
    return CLAIM_TYPE_MAPPINGS.get(claim_str, None)

def parse_claim_type_list(claim_str):
    """
    Parse messy claim type list into normalized types.
    """
    if pd.isna(claim_str):
        return []
    
    # Replace various delimiters with comma
    claim_str = str(claim_str)
    claim_str = re.sub(r'[;|/&]', ',', claim_str)
    
    # Split
    claims = re.split(r'\s*,\s*', claim_str)
    
    # Normalize each
    normalized = []
    unknown = []
    
    for claim in claims:
        claim = claim.strip()
        if not claim:
            continue
        
        normalized_claim = normalize_claim_type(claim)
        if normalized_claim:
            if normalized_claim not in normalized:
                normalized.append(normalized_claim)
        else:
            unknown.append(claim)
    
    return normalized, unknown

def normalize_industry(industry_str):
    """
    Normalize industry to standard taxonomy.
    """
    if pd.isna(industry_str):
        return None
    
    industry_str = str(industry_str).strip().lower()
    return INDUSTRY_MAPPINGS.get(industry_str, industry_str)

def parse_industry_list(industry_str):
    """
    Parse messy industry list into normalized industries.
    """
    if pd.isna(industry_str):
        return []
    
    # Replace various delimiters
    industry_str = str(industry_str)
    industry_str = re.sub(r'[;|/]', ',', industry_str)
    
    # Split
    industries = re.split(r'\s*,\s*', industry_str)
    
    # Normalize each
    normalized = []
    
    for industry in industries:
        industry = industry.strip()
        if not industry:
            continue
        
        normalized_industry = normalize_industry(industry)
        if normalized_industry and normalized_industry not in normalized:
            normalized.append(normalized_industry)
    
    return normalized

def parse_date(date_str):
    """
    Parse various date formats into standard YYYY-MM-DD format.
    """
    if pd.isna(date_str) or date_str == "":
        return None
    
    date_str = str(date_str).strip()
    
    # Try various date formats
    formats = [
        "%m/%d/%Y",      # 2/1/2026
        "%m-%d-%Y",      # 2-1-2026
        "%Y-%m-%d",      # 2026-02-01
        "%m/%d/%y",      # 2/1/26
        "%d/%m/%Y",      # 01/02/2026
        "%B %d %Y",      # February 1 2026
        "%b %d %Y",      # Feb 1 2026
        "%B %Y",         # February 2026
        "%b %Y",         # Feb 2026
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    # If no format matches, return None
    return None

def similarity(a, b):
    """
    Calculate string similarity ratio (0-1).
    """
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def find_duplicates(names, threshold=0.85):
    """
    Find potential duplicate vendor names based on string similarity.
    Returns list of (index1, index2, similarity_score) tuples.
    """
    duplicates = []
    
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            sim = similarity(names[i], names[j])
            if sim >= threshold:
                duplicates.append((i, j, sim))
    
    return duplicates

# ============================================================================
# MAIN CLEANING FUNCTION
# ============================================================================

def clean_vendor_data():
    """
    Main function to clean raw vendor data.
    """
    print("=" * 70)
    print("TPA Match Demo - Data Cleaning Script")
    print("=" * 70)
    print()
    
    # Load raw data
    print(f"Loading raw data from: {RAW_DATA_PATH}")
    try:
        df = pd.read_csv(RAW_DATA_PATH)
        print(f"[OK] Loaded {len(df)} rows")
    except FileNotFoundError:
        print(f"[ERROR] File not found at {RAW_DATA_PATH}")
        return
    
    print()
    
    # Track issues for logging
    all_issues = []
    
    # Clean each row
    cleaned_data = []
    
    for idx, row in df.iterrows():
        issues = {
            "row": idx,
            "vendor_name_raw": row.get("Vendor Name"),
            "issues": []
        }
        
        cleaned_row = {
            "vendor_name": None,
            "headquarters_state": None,
            "states_served": None,
            "claim_types": None,
            "industries": None,
            "years_in_business": None,
            "satisfaction_score": None,
            "avg_response_time_days": None,
            "last_updated": None,
            "source": None,
            "contact_email": None,
            "data_quality_flags": []
        }
        
        # 1. Clean vendor name
        vendor_name = standardize_vendor_name(row.get("Vendor Name"))
        cleaned_row["vendor_name"] = vendor_name
        
        # 2. Clean headquarters state
        hq_state = normalize_state(row.get("Headquarters"))
        if hq_state:
            cleaned_row["headquarters_state"] = hq_state
        elif pd.notna(row.get("Headquarters")):
            issues["issues"].append({
                "field": "headquarters",
                "issue": "unknown_state",
                "raw_value": row.get("Headquarters")
            })
            cleaned_row["data_quality_flags"].append("unknown_headquarters_state")
        
        # 3. Parse state coverage
        states, unknown_states = parse_state_list(row.get("State Coverage"))
        cleaned_row["states_served"] = ",".join(states) if states else None
        
        if unknown_states:
            issues["issues"].append({
                "field": "states",
                "issue": "unknown_states",
                "raw_value": row.get("State Coverage"),
                "unknown": unknown_states
            })
            cleaned_row["data_quality_flags"].append("unknown_states")
        
        # 4. Parse claim types
        claims, unknown_claims = parse_claim_type_list(row.get("Claim Types"))
        cleaned_row["claim_types"] = ",".join(claims) if claims else None
        
        if unknown_claims:
            issues["issues"].append({
                "field": "claim_types",
                "issue": "unknown_claim_types",
                "raw_value": row.get("Claim Types"),
                "unknown": unknown_claims
            })
            cleaned_row["data_quality_flags"].append("unknown_claim_types")
        
        # 5. Parse industries
        industries = parse_industry_list(row.get("Industries Served"))
        cleaned_row["industries"] = ",".join(industries) if industries else None
        
        # 6. Clean numeric fields
        try:
            years = row.get("Years in Business")
            cleaned_row["years_in_business"] = int(years) if pd.notna(years) else None
        except:
            cleaned_row["years_in_business"] = None
        
        try:
            sat = row.get("Satisfaction Score")
            cleaned_row["satisfaction_score"] = float(sat) if pd.notna(sat) and str(sat).strip() != "" else None
        except:
            cleaned_row["satisfaction_score"] = None
        
        try:
            resp = row.get("Avg Response Days")
            cleaned_row["avg_response_time_days"] = float(resp) if pd.notna(resp) and str(resp).strip() != "" else None
        except:
            cleaned_row["avg_response_time_days"] = None
        
        # 7. Parse date
        date_parsed = parse_date(row.get("Last Updated"))
        cleaned_row["last_updated"] = date_parsed
        
        if pd.notna(row.get("Last Updated")) and not date_parsed:
            issues["issues"].append({
                "field": "last_updated",
                "issue": "unparseable_date",
                "raw_value": row.get("Last Updated")
            })
            cleaned_row["data_quality_flags"].append("unparseable_date")
        
        # 8. Source and contact
        cleaned_row["source"] = row.get("Source") if pd.notna(row.get("Source")) else None
        cleaned_row["contact_email"] = row.get("Contact Email") if pd.notna(row.get("Contact Email")) else None
        
        # 9. Check for missing critical fields
        if not cleaned_row["vendor_name"]:
            cleaned_row["data_quality_flags"].append("missing_vendor_name")
        if not cleaned_row["states_served"]:
            cleaned_row["data_quality_flags"].append("missing_states")
        if not cleaned_row["claim_types"]:
            cleaned_row["data_quality_flags"].append("missing_claim_types")
        
        # Convert flags list to comma-separated string
        cleaned_row["data_quality_flags"] = ",".join(cleaned_row["data_quality_flags"]) if cleaned_row["data_quality_flags"] else None
        
        cleaned_data.append(cleaned_row)
        
        if issues["issues"]:
            all_issues.append(issues)
    
    # Convert to DataFrame
    df_cleaned = pd.DataFrame(cleaned_data)
    
    # Detect duplicates
    print("Detecting potential duplicates...")
    vendor_names = df_cleaned["vendor_name"].tolist()
    duplicates = find_duplicates(vendor_names, threshold=0.85)
    
    if duplicates:
        print(f"[WARNING] Found {len(duplicates)} potential duplicate(s):")
        for i, j, sim in duplicates:
            print(f"  - Row {i}: '{vendor_names[i]}' <-> Row {j}: '{vendor_names[j]}' (similarity: {sim:.2%})")
            all_issues.append({
                "issue_type": "potential_duplicate",
                "row1": i,
                "row2": j,
                "vendor1": vendor_names[i],
                "vendor2": vendor_names[j],
                "similarity": sim
            })
    else:
        print("[OK] No duplicates detected")
    
    print()
    
    # Save cleaned data
    print(f"Saving cleaned data to: {CLEAN_DATA_PATH}")
    df_cleaned.to_csv(CLEAN_DATA_PATH, index=False)
    print(f"[OK] Saved {len(df_cleaned)} cleaned records")
    
    # Save issues log
    if all_issues:
        print(f"Saving data quality issues to: {ISSUES_LOG_PATH}")
        with open(ISSUES_LOG_PATH, 'w') as f:
            json.dump(all_issues, f, indent=2)
        print(f"[OK] Logged {len(all_issues)} data quality issue(s)")
    
    # Summary statistics
    print()
    print("=" * 70)
    print("CLEANING SUMMARY")
    print("=" * 70)
    print(f"Total records processed: {len(df_cleaned)}")
    print(f"Records with data quality flags: {df_cleaned['data_quality_flags'].notna().sum()}")
    print(f"Records missing states: {df_cleaned['states_served'].isna().sum()}")
    print(f"Records missing claim types: {df_cleaned['claim_types'].isna().sum()}")
    print(f"Records missing satisfaction score: {df_cleaned['satisfaction_score'].isna().sum()}")
    print(f"Potential duplicates found: {len(duplicates)}")
    print()
    print("[SUCCESS] Data cleaning complete!")
    print()

# ============================================================================
# RUN SCRIPT
# ============================================================================

if __name__ == "__main__":
    clean_vendor_data()
