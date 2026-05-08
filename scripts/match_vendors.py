"""
TPA Match Demo - Vendor Matching Engine

This script implements the deterministic scoring logic to match buyers with TPA vendors.

Core principle: Structured, explainable matching - NOT a black-box AI decision maker.

Usage:
    python scripts/match_vendors.py <buyer_request_id>
    python scripts/match_vendors.py --all  # Run for all buyer requests
"""

import sqlite3
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path("database/tpa_match_demo.db")

# Base scoring weights (sum to 100)
BASE_WEIGHTS = {
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
PRIORITY_MULTIPLIERS = {
    5: 1.3,   # Critical: +30% boost
    4: 1.15,  # High: +15% boost
    3: 1.0,   # Moderate: no change (default)
    2: 0.7,   # Low: -30% penalty
    1: 0.5    # Very Low: -50% penalty
}

STALE_DATA_THRESHOLD_DAYS = 180


def get_adjusted_weights(buyer_request):
    """
    Calculate adjusted scoring weights based on buyer priorities.
    
    Args:
        buyer_request: Dict containing buyer request data with priority fields
        
    Returns:
        Dict of adjusted weights that sum to 100
    """
    # Start with base weights
    adjusted = BASE_WEIGHTS.copy()
    
    # Apply multipliers based on priorities
    priority_mapping = {
        "geography": buyer_request.get("priority_geography", 3),
        "claims": buyer_request.get("priority_claims", 3),
        "industry": buyer_request.get("priority_industry", 3),
        "services": buyer_request.get("priority_services", 3),
        "reporting": buyer_request.get("priority_reporting", 3),
        "technology": buyer_request.get("priority_technology", 3),
    }
    
    # Apply multipliers
    for category, priority_level in priority_mapping.items():
        multiplier = PRIORITY_MULTIPLIERS.get(priority_level, 1.0)
        adjusted[category] *= multiplier
    
    # Normalize to sum to 100 (excluding performance and data_quality which don't have priority fields)
    # Keep performance and data_quality at their base weights
    adjustable_sum = sum([adjusted[k] for k in priority_mapping.keys()])
    adjustable_target = 100 - BASE_WEIGHTS["performance"] - BASE_WEIGHTS["data_quality"]
    
    scale_factor = adjustable_target / adjustable_sum if adjustable_sum > 0 else 1.0
    
    for category in priority_mapping.keys():
        adjusted[category] *= scale_factor
    
    return adjusted


def is_stale(last_updated_str, threshold_days=STALE_DATA_THRESHOLD_DAYS):
    """
    Check if vendor data is stale based on last_updated date.
    
    Args:
        last_updated_str: Date string in "YYYY-MM-DD" format
        threshold_days: Number of days before data is considered stale
        
    Returns:
        Boolean indicating if data is stale
    """
    if not last_updated_str:
        return True
    
    try:
        last_updated = datetime.strptime(last_updated_str, "%Y-%m-%d")
        age_days = (datetime.now() - last_updated).days
        return age_days > threshold_days
    except ValueError:
        return True


def get_buyer_request(conn, buyer_request_id):
    """Fetch buyer request data with related states and services."""
    cursor = conn.cursor()
    
    # Get buyer request
    cursor.execute("SELECT * FROM buyer_requests WHERE buyer_request_id = ?", (buyer_request_id,))
    columns = [desc[0] for desc in cursor.description]
    row = cursor.fetchone()
    
    if not row:
        return None
    
    buyer_request = dict(zip(columns, row))
    
    # Get required states
    cursor.execute("""
        SELECT state_code, required 
        FROM buyer_required_states 
        WHERE buyer_request_id = ?
    """, (buyer_request_id,))
    buyer_request["required_states"] = [
        {"state": row[0], "required": bool(row[1])} 
        for row in cursor.fetchall()
    ]
    
    # Get required services
    cursor.execute("""
        SELECT service_name, required, priority_level 
        FROM buyer_required_services 
        WHERE buyer_request_id = ?
    """, (buyer_request_id,))
    buyer_request["required_services"] = [
        {"service": row[0], "required": bool(row[1]), "priority": row[2]} 
        for row in cursor.fetchall()
    ]
    
    return buyer_request


def get_vendors(conn):
    """Fetch all active vendors with their related data."""
    cursor = conn.cursor()
    
    # Get all active vendors
    cursor.execute("SELECT * FROM vendors WHERE active_status = 'active'")
    columns = [desc[0] for desc in cursor.description]
    vendors = []
    
    for row in cursor.fetchall():
        vendor = dict(zip(columns, row))
        vendor_id = vendor["vendor_id"]
        
        # Get states
        cursor.execute("""
            SELECT state_code, coverage_strength, local_adjuster_network 
            FROM vendor_states 
            WHERE vendor_id = ?
        """, (vendor_id,))
        vendor["states"] = [
            {"state": row[0], "strength": row[1], "local_network": bool(row[2])} 
            for row in cursor.fetchall()
        ]
        
        # Get claim types
        cursor.execute("""
            SELECT claim_type, capability_level, primary_focus 
            FROM vendor_claim_types 
            WHERE vendor_id = ?
        """, (vendor_id,))
        vendor["claim_types"] = [
            {"type": row[0], "level": row[1], "primary": bool(row[2])} 
            for row in cursor.fetchall()
        ]
        
        # Get industries
        cursor.execute("""
            SELECT industry, experience_level 
            FROM vendor_industries 
            WHERE vendor_id = ?
        """, (vendor_id,))
        vendor["industries"] = [
            {"industry": row[0], "level": row[1]} 
            for row in cursor.fetchall()
        ]
        
        # Get services
        cursor.execute("""
            SELECT service_name, service_level, provided_in_house 
            FROM vendor_services 
            WHERE vendor_id = ?
        """, (vendor_id,))
        vendor["services"] = [
            {"service": row[0], "level": row[1], "in_house": bool(row[2])} 
            for row in cursor.fetchall()
        ]
        
        vendors.append(vendor)
    
    return vendors


def apply_hard_filters(vendors, buyer_request):
    """
    Apply hard filters to remove disqualified vendors.
    
    Returns:
        Tuple of (eligible_vendors, disqualified_vendors_with_reasons)
    """
    eligible = []
    disqualified = []
    
    excluded_vendors = []
    if buyer_request.get("excluded_vendors"):
        excluded_vendors = [v.strip().lower() for v in buyer_request["excluded_vendors"].split(",")]
    
    for vendor in vendors:
        reasons = []
        
        # Filter 1: Excluded vendors
        if vendor["vendor_name"].lower() in excluded_vendors:
            reasons.append("Buyer excluded this vendor")
        
        # Filter 2: Active status (already filtered in query, but double-check)
        if vendor.get("active_status") != "active":
            reasons.append("Vendor status is not active")
        
        # Filter 3: Required claim type
        claim_type_needed = buyer_request.get("claim_type_needed")
        if claim_type_needed:
            vendor_claim_types = [ct["type"] for ct in vendor.get("claim_types", [])]
            if claim_type_needed not in vendor_claim_types:
                reasons.append(f"Does not handle {claim_type_needed}")
        
        # Filter 4: Required states (strict mode)
        # For MVP, we'll use partial matching - vendors missing states get scored lower
        # but aren't automatically disqualified unless they serve NO required states
        required_states = [s["state"] for s in buyer_request.get("required_states", []) if s["required"]]
        if required_states:
            vendor_states = [s["state"] for s in vendor.get("states", [])]
            states_covered = [s for s in required_states if s in vendor_states]
            if not states_covered:
                reasons.append("Does not serve any required states")
        
        # Filter 5: Priority cost (if critical, exclude high-priced vendors)
        priority_cost = buyer_request.get("priority_cost", 3)
        if priority_cost >= 4 and vendor.get("pricing_level") == "high":
            reasons.append("Pricing level too high for buyer's cost sensitivity")
        
        # Filter 6: Minimum satisfaction score (if buyer has specific requirements)
        # This is optional - not implemented in MVP
        
        if reasons:
            disqualified.append({
                "vendor": vendor,
                "reasons": reasons
            })
        else:
            eligible.append(vendor)
    
    return eligible, disqualified


def score_geography(vendor, buyer_request, reason_codes):
    """
    Score geographic fit (0-20 points).
    
    Returns:
        Score (float) and updates reason_codes list
    """
    score = 0
    required_states = [s["state"] for s in buyer_request.get("required_states", []) if s["required"]]
    vendor_states = vendor.get("states", [])
    vendor_state_codes = [s["state"] for s in vendor_states]
    
    if not required_states:
        return 20  # If no specific states required, full points
    
    # Check coverage
    states_covered = [s for s in required_states if s in vendor_state_codes]
    coverage_pct = len(states_covered) / len(required_states) if required_states else 0
    
    # Check local strength
    strong_local = any(
        s["state"] in required_states and s["strength"] == "strong" and s["local_network"]
        for s in vendor_states
    )
    
    if coverage_pct == 1.0:
        reason_codes.append("serves_all_required_states")
        if strong_local:
            score = 20
            reason_codes.append("strong_local_presence")
        else:
            score = 15
            reason_codes.append("limited_local_presence")
    elif coverage_pct >= 0.5:
        score = 10
        reason_codes.append("serves_some_required_states")
        missing = [s for s in required_states if s not in vendor_state_codes]
        for state in missing[:2]:  # Report first 2 missing states
            reason_codes.append(f"missing_required_state_{state}")
    else:
        score = 5
        reason_codes.append("limited_state_coverage")
    
    return score


def score_claims_capability(vendor, buyer_request, reason_codes):
    """
    Score claims capability fit (0-20 points).
    
    Returns:
        Score (float) and updates reason_codes list
    """
    score = 0
    claim_type_needed = buyer_request.get("claim_type_needed")
    
    if not claim_type_needed:
        return 20  # If no specific claim type, full points
    
    vendor_claim_types = vendor.get("claim_types", [])
    matching_claim = None
    
    for ct in vendor_claim_types:
        if ct["type"] == claim_type_needed:
            matching_claim = ct
            break
    
    if not matching_claim:
        reason_codes.append("missing_claim_type")
        return 0
    
    reason_codes.append("handles_required_claim_type")
    
    # Score based on capability level and primary focus
    if matching_claim["primary"] and matching_claim["level"] == "strong":
        score = 20
        reason_codes.append("claim_type_is_primary_focus")
    elif matching_claim["level"] == "strong":
        score = 18
    elif matching_claim["level"] == "moderate":
        score = 15
    elif matching_claim["level"] == "limited":
        score = 5
        reason_codes.append("limited_claim_type_capability")
    else:
        score = 10
        reason_codes.append("missing_claim_type_data")
    
    return score


def score_industry_fit(vendor, buyer_request, reason_codes):
    """
    Score industry/client profile fit (0-15 points).
    
    Returns:
        Score (float) and updates reason_codes list
    """
    score = 0
    buyer_industry = buyer_request.get("industry")
    
    if not buyer_industry:
        return 15  # If no specific industry, full points
    
    vendor_industries = vendor.get("industries", [])
    matching_industry = None
    
    for ind in vendor_industries:
        if ind["industry"] == buyer_industry:
            matching_industry = ind
            break
    
    if not matching_industry:
        reason_codes.append("no_industry_evidence")
        return 0
    
    # Score based on experience level
    if matching_industry["level"] == "strong":
        score = 15
        reason_codes.append("strong_industry_match")
    elif matching_industry["level"] == "moderate":
        score = 10
        reason_codes.append("moderate_industry_match")
    elif matching_industry["level"] == "limited":
        score = 5
        reason_codes.append("adjacent_industry_match")
    else:
        score = 5
        reason_codes.append("limited_industry_evidence")
    
    # Check client size match
    ideal_client = vendor.get("ideal_client_size")
    buyer_employee_count = buyer_request.get("employee_count", 0)
    
    if ideal_client and buyer_employee_count:
        if ideal_client == "small" and buyer_employee_count < 100:
            reason_codes.append("similar_client_size_match")
        elif ideal_client == "mid_market" and 100 <= buyer_employee_count <= 1000:
            reason_codes.append("similar_client_size_match")
        elif ideal_client == "large" and buyer_employee_count > 1000:
            reason_codes.append("similar_client_size_match")
    
    return score


def score_service_capability(vendor, buyer_request, reason_codes):
    """
    Score service capability fit (0-15 points).
    
    Returns:
        Score (float) and updates reason_codes list
    """
    score = 0
    required_services = buyer_request.get("required_services", [])
    
    if not required_services:
        return 15  # If no specific services required, full points
    
    vendor_services = vendor.get("services", [])
    vendor_service_names = [s["service"] for s in vendor_services]
    
    required_service_names = [s["service"] for s in required_services if s["required"]]
    preferred_service_names = [s["service"] for s in required_services if not s["required"]]
    
    # Check required services
    required_met = 0
    for service in required_service_names:
        if service in vendor_service_names:
            required_met += 1
            # Find service details
            svc_detail = next((s for s in vendor_services if s["service"] == service), None)
            if svc_detail:
                reason_codes.append(f"has_required_service_{service}")
                if not svc_detail.get("in_house"):
                    reason_codes.append(f"service_{service}_via_partner")
        else:
            reason_codes.append(f"missing_required_service_{service}")
    
    # Check preferred services
    preferred_met = sum(1 for s in preferred_service_names if s in vendor_service_names)
    
    if required_service_names:
        required_pct = required_met / len(required_service_names)
    else:
        required_pct = 1.0
    
    # Score calculation
    if required_pct == 1.0:
        if preferred_met >= len(preferred_service_names) * 0.5:
            score = 15
            if preferred_met > 0:
                reason_codes.append("has_preferred_services")
        else:
            score = 10
    elif required_pct >= 0.5:
        score = 5
    else:
        score = 0
    
    return score


def score_reporting(vendor, buyer_request, reason_codes):
    """
    Score reporting/analytics fit (0-10 points).
    
    Returns:
        Score (float) and updates reason_codes list
    """
    reporting_score = vendor.get("reporting_score", 0)
    
    if reporting_score is None:
        reason_codes.append("missing_reporting_data")
        return 5  # Neutral score if data missing
    
    # Score based on reporting_score (0-10 scale)
    if reporting_score >= 9:
        reason_codes.append("strong_reporting")
        return 10
    elif reporting_score >= 7:
        reason_codes.append("good_reporting")
        return 7
    elif reporting_score >= 5:
        return 5
    else:
        reason_codes.append("limited_reporting")
        return 3


def score_performance(vendor, buyer_request, reason_codes):
    """
    Score performance fit (0-10 points).
    
    Returns:
        Score (float) and updates reason_codes list
    """
    score = 0
    satisfaction = vendor.get("satisfaction_score", 0)
    response_time = vendor.get("avg_response_time_days")
    
    # Satisfaction scoring (0-7 points)
    if satisfaction is None:
        reason_codes.append("performance_data_missing")
        satisfaction_points = 5  # Neutral
    elif satisfaction >= 90:
        reason_codes.append("high_satisfaction_score")
        satisfaction_points = 7
    elif satisfaction >= 80:
        reason_codes.append("moderate_satisfaction_score")
        satisfaction_points = 5
    else:
        reason_codes.append("low_satisfaction_score")
        satisfaction_points = 2
    
    # Response time scoring (0-3 points)
    if response_time is None:
        response_points = 2  # Neutral
    elif response_time <= 1.0:
        reason_codes.append("fast_response_time")
        response_points = 3
    elif response_time <= 3.0:
        response_points = 2
    else:
        reason_codes.append("slow_response_time")
        response_points = 1
    
    # Cost sensitivity adjustment
    priority_cost = buyer_request.get("priority_cost", 3)
    pricing_level = vendor.get("pricing_level")
    
    if priority_cost >= 4:
        # High cost sensitivity
        if pricing_level in ["low", "medium_low"]:
            reason_codes.append("cost_effective_pricing")
        elif pricing_level == "high":
            # Should already be filtered out, but just in case
            satisfaction_points *= 0.7
    
    score = satisfaction_points + response_points
    return min(score, 10)  # Cap at 10


def score_technology(vendor, buyer_request, reason_codes):
    """
    Score technology/integration fit (0-5 points).
    
    Returns:
        Score (float) and updates reason_codes list
    """
    score = 0
    vendor_services = vendor.get("services", [])
    vendor_service_names = [s["service"] for s in vendor_services]
    
    # Check for technology-related services
    tech_services = ["api_access", "sftp_export", "client_portal", "origami_integration"]
    available_tech = [s for s in tech_services if s in vendor_service_names]
    
    if "api_access" in available_tech:
        score += 2
        reason_codes.append("api_available")
    
    if "origami_integration" in available_tech:
        score += 1.5
        reason_codes.append("origami_integration_experience")
    
    if "sftp_export" in available_tech:
        score += 1
        reason_codes.append("sftp_available")
    
    if "client_portal" in available_tech:
        score += 0.5
        reason_codes.append("client_portal_available")
    
    if not available_tech:
        reason_codes.append("missing_integration_data")
        score = 2  # Neutral score
    
    return min(score, 5)  # Cap at 5


def score_data_quality(vendor, buyer_request, reason_codes):
    """
    Score data quality/confidence (0-5 points).
    
    Returns:
        Score (float) and updates reason_codes list
    """
    score = 5  # Start with full points
    
    # Check data quality score
    dq_score = vendor.get("data_quality_score", 0)
    if dq_score and dq_score < 6:
        score -= 2
        reason_codes.append("low_data_quality_score")
    
    # Check if data is stale
    if is_stale(vendor.get("last_updated")):
        score -= 2
        reason_codes.append("stale_vendor_data")
    else:
        reason_codes.append("current_vendor_data")
    
    # Check source confidence
    if vendor.get("source_confidence") == "low":
        score -= 1
        reason_codes.append("low_source_confidence")
    
    # Check if verified
    if vendor.get("verified_by_human"):
        reason_codes.append("verified_vendor_data")
    
    # Check for conflicts
    notes = vendor.get("notes", "")
    if "CONFLICT" in notes.upper():
        score -= 1
        reason_codes.append("conflicting_source_data")
    
    return max(score, 0)  # Don't go below 0


def check_human_review_flags(vendor, total_score, reason_codes, buyer_request):
    """
    Determine if this match requires human review.
    
    Returns:
        (requires_review: bool, review_reasons: list)
    """
    review_reasons = []
    
    # Low total score
    if total_score < 70:
        review_reasons.append("low_total_score")
    
    # Stale data
    if is_stale(vendor.get("last_updated")):
        review_reasons.append("stale_vendor_data")
    
    # Low source confidence
    if vendor.get("source_confidence") == "low":
        review_reasons.append("low_source_confidence")
    
    # Low data quality
    if vendor.get("data_quality_score", 10) < 6:
        review_reasons.append("low_data_quality_score")
    
    # Conflicting data
    if "CONFLICT" in vendor.get("notes", "").upper():
        review_reasons.append("conflicting_source_data")
    
    # Missing required services
    if any("missing_required_service" in rc for rc in reason_codes):
        review_reasons.append("missing_required_service")
    
    # Missing required states
    if any("missing_required_state" in rc for rc in reason_codes):
        review_reasons.append("missing_required_state")
    
    return len(review_reasons) > 0, review_reasons


def score_vendor(vendor, buyer_request, weights):
    """
    Score a single vendor against buyer requirements.
    
    Returns:
        Dict containing score breakdown, reason codes, and warnings
    """
    reason_codes = []
    
    # Score each category
    geography_score = score_geography(vendor, buyer_request, reason_codes)
    claims_score = score_claims_capability(vendor, buyer_request, reason_codes)
    industry_score = score_industry_fit(vendor, buyer_request, reason_codes)
    service_score = score_service_capability(vendor, buyer_request, reason_codes)
    reporting_score = score_reporting(vendor, buyer_request, reason_codes)
    performance_score = score_performance(vendor, buyer_request, reason_codes)
    technology_score = score_technology(vendor, buyer_request, reason_codes)
    data_quality_score = score_data_quality(vendor, buyer_request, reason_codes)
    
    # Apply weights to get final scores
    weighted_geography = (geography_score / 20) * weights["geography"]
    weighted_claims = (claims_score / 20) * weights["claims"]
    weighted_industry = (industry_score / 15) * weights["industry"]
    weighted_service = (service_score / 15) * weights["services"]
    weighted_reporting = (reporting_score / 10) * weights["reporting"]
    weighted_performance = (performance_score / 10) * weights["performance"]
    weighted_technology = (technology_score / 5) * weights["technology"]
    weighted_data_quality = (data_quality_score / 5) * weights["data_quality"]
    
    total_score = (
        weighted_geography +
        weighted_claims +
        weighted_industry +
        weighted_service +
        weighted_reporting +
        weighted_performance +
        weighted_technology +
        weighted_data_quality
    )
    
    # Check for human review flags
    requires_review, review_reasons = check_human_review_flags(
        vendor, total_score, reason_codes, buyer_request
    )
    
    return {
        "vendor_id": vendor["vendor_id"],
        "vendor_name": vendor["vendor_name"],
        "total_score": round(total_score, 2),
        "geography_score": round(weighted_geography, 2),
        "claims_score": round(weighted_claims, 2),
        "industry_score": round(weighted_industry, 2),
        "service_score": round(weighted_service, 2),
        "reporting_score": round(weighted_reporting, 2),
        "performance_score": round(weighted_performance, 2),
        "technology_score": round(weighted_technology, 2),
        "data_quality_score": round(weighted_data_quality, 2),
        "reason_codes": reason_codes,
        "risk_flags": review_reasons,
        "human_review_required": requires_review
    }


def save_match_results(conn, buyer_request_id, results):
    """Save match results to the database."""
    cursor = conn.cursor()
    
    # Delete existing results for this buyer request
    cursor.execute("DELETE FROM match_results WHERE buyer_request_id = ?", (buyer_request_id,))
    
    # Insert new results
    for rank, result in enumerate(results, 1):
        cursor.execute("""
            INSERT INTO match_results (
                buyer_request_id, vendor_id, total_score, rank,
                geography_score, claims_score, industry_score, service_score,
                reporting_score, performance_score, technology_score, data_quality_score,
                reason_codes, risk_flags, human_review_required
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            buyer_request_id,
            result["vendor_id"],
            result["total_score"],
            rank,
            result["geography_score"],
            result["claims_score"],
            result["industry_score"],
            result["service_score"],
            result["reporting_score"],
            result["performance_score"],
            result["technology_score"],
            result["data_quality_score"],
            json.dumps(result["reason_codes"]),
            json.dumps(result["risk_flags"]),
            1 if result["human_review_required"] else 0
        ))
    
    conn.commit()


def match_vendors(buyer_request_id, verbose=True):
    """
    Main matching function: Match vendors to a buyer request.
    
    Args:
        buyer_request_id: ID of the buyer request to match
        verbose: If True, print detailed output
        
    Returns:
        List of match results, sorted by score
    """
    if not DB_PATH.exists():
        print(f"[ERROR] Database not found at {DB_PATH}")
        print("Run: python scripts/create_database.py")
        return []
    
    conn = sqlite3.connect(DB_PATH)
    
    # Get buyer request
    buyer_request = get_buyer_request(conn, buyer_request_id)
    if not buyer_request:
        print(f"[ERROR] Buyer request {buyer_request_id} not found")
        conn.close()
        return []
    
    if verbose:
        print("=" * 70)
        print(f"Matching Vendors for Buyer Request #{buyer_request_id}")
        print("=" * 70)
        print(f"Buyer: {buyer_request.get('buyer_name', 'Unknown')}")
        print(f"Industry: {buyer_request.get('industry', 'Not specified')}")
        print(f"Claim Type: {buyer_request.get('claim_type_needed', 'Not specified')}")
        required_states = [s["state"] for s in buyer_request.get("required_states", [])]
        print(f"Required States: {', '.join(required_states) if required_states else 'Not specified'}")
        print()
    
    # Get all vendors
    vendors = get_vendors(conn)
    
    if verbose:
        print(f"Total active vendors: {len(vendors)}")
    
    # Apply hard filters
    eligible_vendors, disqualified = apply_hard_filters(vendors, buyer_request)
    
    if verbose:
        print(f"Eligible vendors after filters: {len(eligible_vendors)}")
        print(f"Disqualified vendors: {len(disqualified)}")
        print()
    
    if not eligible_vendors:
        print("[WARNING] No vendors passed hard filters!")
        print()
        print("Disqualified vendors:")
        for dq in disqualified[:5]:
            print(f"  - {dq['vendor']['vendor_name']}: {', '.join(dq['reasons'])}")
        conn.close()
        return []
    
    # Calculate adjusted weights
    weights = get_adjusted_weights(buyer_request)
    
    if verbose:
        print("Adjusted scoring weights:")
        for category, weight in weights.items():
            print(f"  {category:20} {weight:5.1f}")
        print()
    
    # Score all eligible vendors
    results = []
    for vendor in eligible_vendors:
        result = score_vendor(vendor, buyer_request, weights)
        results.append(result)
    
    # Sort by total score (descending)
    results.sort(key=lambda x: x["total_score"], reverse=True)
    
    # Save to database
    save_match_results(conn, buyer_request_id, results[:10])  # Save top 10
    
    if verbose:
        print("=" * 70)
        print("TOP MATCHES")
        print("=" * 70)
        print()
        
        for i, result in enumerate(results[:5], 1):
            print(f"{i}. {result['vendor_name']} - Score: {result['total_score']:.1f}/100")
            print(f"   Geography: {result['geography_score']:.1f} | Claims: {result['claims_score']:.1f} | Industry: {result['industry_score']:.1f}")
            print(f"   Services: {result['service_score']:.1f} | Reporting: {result['reporting_score']:.1f} | Performance: {result['performance_score']:.1f}")
            print(f"   Technology: {result['technology_score']:.1f} | Data Quality: {result['data_quality_score']:.1f}")
            
            # Show key reason codes (limit to most important)
            key_reasons = [r for r in result['reason_codes'] 
                          if not r.startswith('has_required_service_') 
                          and not r.startswith('missing_required_state_')][:6]
            if key_reasons:
                print(f"   Key reasons: {', '.join(key_reasons)}")
            
            if result['human_review_required']:
                print(f"   [!] HUMAN REVIEW REQUIRED: {', '.join(result['risk_flags'])}")
            
            print()
    
    conn.close()
    return results


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/match_vendors.py <buyer_request_id>")
        print("       python scripts/match_vendors.py --all")
        sys.exit(1)
    
    if sys.argv[1] == "--all":
        # Run for all buyer requests
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT buyer_request_id FROM buyer_requests")
        buyer_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        print(f"Running matching for {len(buyer_ids)} buyer requests...")
        print()
        
        for buyer_id in buyer_ids:
            match_vendors(buyer_id, verbose=True)
            print()
            print()
    else:
        buyer_request_id = int(sys.argv[1])
        match_vendors(buyer_request_id, verbose=True)


if __name__ == "__main__":
    main()
