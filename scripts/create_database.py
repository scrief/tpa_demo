import sqlite3
from pathlib import Path

DB_PATH = Path("database/tpa_match_demo.db")

def create_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.executescript("""
    DROP TABLE IF EXISTS validation_results;
    DROP TABLE IF EXISTS match_results;
    DROP TABLE IF EXISTS buyer_required_services;
    DROP TABLE IF EXISTS buyer_required_states;
    DROP TABLE IF EXISTS buyer_requests;
    DROP TABLE IF EXISTS vendor_services;
    DROP TABLE IF EXISTS vendor_industries;
    DROP TABLE IF EXISTS vendor_claim_types;
    DROP TABLE IF EXISTS vendor_states;
    DROP TABLE IF EXISTS vendors;

    CREATE TABLE vendors (
        vendor_id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendor_name TEXT NOT NULL UNIQUE,
        vendor_type TEXT DEFAULT 'TPA',
        headquarters_state TEXT,
        company_size TEXT,
        years_in_business INTEGER,
        website TEXT,
        active_status TEXT DEFAULT 'active',

        ideal_client_size TEXT,
        program_type_fit TEXT,
        pricing_level TEXT,

        satisfaction_score REAL,
        avg_response_time_days REAL,
        reporting_score REAL,
        data_quality_score REAL,

        source TEXT,
        source_confidence TEXT,
        last_updated TEXT,
        verified_by_human INTEGER DEFAULT 0,

        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE vendor_states (
        vendor_state_id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendor_id INTEGER NOT NULL,
        state_code TEXT NOT NULL,
        coverage_strength TEXT DEFAULT 'unknown',
        local_adjuster_network INTEGER DEFAULT 0,
        FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id) ON DELETE CASCADE,
        UNIQUE(vendor_id, state_code)
    );

    CREATE TABLE vendor_claim_types (
        vendor_claim_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendor_id INTEGER NOT NULL,
        claim_type TEXT NOT NULL,
        capability_level TEXT DEFAULT 'unknown',
        primary_focus INTEGER DEFAULT 0,
        FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id) ON DELETE CASCADE,
        UNIQUE(vendor_id, claim_type)
    );

    CREATE TABLE vendor_industries (
        vendor_industry_id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendor_id INTEGER NOT NULL,
        industry TEXT NOT NULL,
        experience_level TEXT DEFAULT 'unknown',
        FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id) ON DELETE CASCADE,
        UNIQUE(vendor_id, industry)
    );

    CREATE TABLE vendor_services (
        vendor_service_id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendor_id INTEGER NOT NULL,
        service_name TEXT NOT NULL,
        service_level TEXT DEFAULT 'unknown',
        provided_in_house INTEGER DEFAULT 1,
        notes TEXT,
        FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id) ON DELETE CASCADE,
        UNIQUE(vendor_id, service_name)
    );

    CREATE TABLE buyer_requests (
        buyer_request_id INTEGER PRIMARY KEY AUTOINCREMENT,
        buyer_name TEXT,
        industry TEXT,
        sub_industry TEXT,
        employee_count INTEGER,
        program_type TEXT,
        claim_type_needed TEXT,
        annual_claim_volume INTEGER,
        implementation_timeline_days INTEGER,

        priority_geography INTEGER DEFAULT 3,
        priority_claims INTEGER DEFAULT 3,
        priority_industry INTEGER DEFAULT 3,
        priority_services INTEGER DEFAULT 3,
        priority_reporting INTEGER DEFAULT 3,
        priority_technology INTEGER DEFAULT 3,
        priority_cost INTEGER DEFAULT 3,

        narrative_request TEXT,
        pain_points TEXT,
        excluded_vendors TEXT,

        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE buyer_required_states (
        buyer_required_state_id INTEGER PRIMARY KEY AUTOINCREMENT,
        buyer_request_id INTEGER NOT NULL,
        state_code TEXT NOT NULL,
        required INTEGER DEFAULT 1,
        FOREIGN KEY (buyer_request_id) REFERENCES buyer_requests(buyer_request_id) ON DELETE CASCADE,
        UNIQUE(buyer_request_id, state_code)
    );

    CREATE TABLE buyer_required_services (
        buyer_required_service_id INTEGER PRIMARY KEY AUTOINCREMENT,
        buyer_request_id INTEGER NOT NULL,
        service_name TEXT NOT NULL,
        required INTEGER DEFAULT 1,
        priority_level TEXT DEFAULT 'required',
        FOREIGN KEY (buyer_request_id) REFERENCES buyer_requests(buyer_request_id) ON DELETE CASCADE,
        UNIQUE(buyer_request_id, service_name)
    );

    CREATE TABLE match_results (
        match_result_id INTEGER PRIMARY KEY AUTOINCREMENT,
        buyer_request_id INTEGER NOT NULL,
        vendor_id INTEGER NOT NULL,
        total_score REAL NOT NULL,
        rank INTEGER,

        geography_score REAL DEFAULT 0,
        claims_score REAL DEFAULT 0,
        industry_score REAL DEFAULT 0,
        service_score REAL DEFAULT 0,
        reporting_score REAL DEFAULT 0,
        performance_score REAL DEFAULT 0,
        technology_score REAL DEFAULT 0,
        data_quality_score REAL DEFAULT 0,

        reason_codes TEXT,
        risk_flags TEXT,
        explanation TEXT,
        human_review_required INTEGER DEFAULT 0,

        created_at TEXT DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (buyer_request_id) REFERENCES buyer_requests(buyer_request_id) ON DELETE CASCADE,
        FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id) ON DELETE CASCADE
    );

    CREATE TABLE validation_results (
        validation_result_id INTEGER PRIMARY KEY AUTOINCREMENT,
        scenario_name TEXT NOT NULL,
        buyer_request_id INTEGER,
        expected_good_vendors TEXT,
        expected_bad_vendors TEXT,
        actual_top_vendors TEXT,
        top_match_pass INTEGER,
        explanation_pass INTEGER,
        hallucination_detected INTEGER DEFAULT 0,
        missing_data_flag_correct INTEGER,
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (buyer_request_id) REFERENCES buyer_requests(buyer_request_id) ON DELETE SET NULL
    );

    CREATE INDEX idx_vendor_states_state ON vendor_states(state_code);
    CREATE INDEX idx_vendor_claim_types_claim ON vendor_claim_types(claim_type);
    CREATE INDEX idx_vendor_industries_industry ON vendor_industries(industry);
    CREATE INDEX idx_vendor_services_service ON vendor_services(service_name);
    CREATE INDEX idx_match_results_buyer ON match_results(buyer_request_id);

    -- ========================================================================
    -- MAPPING TABLES FOR DATA CLEANING (Persistent Learning)
    -- ========================================================================

    CREATE TABLE state_mappings (
        mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
        raw_value TEXT NOT NULL UNIQUE,
        canonical_value TEXT NOT NULL,
        confidence TEXT DEFAULT 'high',
        verified_by_human INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE claim_type_mappings (
        mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
        raw_value TEXT NOT NULL UNIQUE,
        canonical_value TEXT NOT NULL,
        confidence TEXT DEFAULT 'high',
        verified_by_human INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE industry_mappings (
        mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
        raw_value TEXT NOT NULL UNIQUE,
        canonical_value TEXT NOT NULL,
        confidence TEXT DEFAULT 'high',
        verified_by_human INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE vendor_name_mappings (
        mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
        raw_name TEXT NOT NULL UNIQUE,
        canonical_name TEXT NOT NULL,
        canonical_vendor_id INTEGER,
        confidence TEXT DEFAULT 'high',
        verified_by_human INTEGER DEFAULT 0,
        merge_with_vendor_id INTEGER,
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (canonical_vendor_id) REFERENCES vendors(vendor_id) ON DELETE SET NULL,
        FOREIGN KEY (merge_with_vendor_id) REFERENCES vendors(vendor_id) ON DELETE SET NULL
    );

    -- ========================================================================
    -- DATA QUALITY REVIEW QUEUE
    -- ========================================================================

    CREATE TABLE data_quality_queue (
        queue_id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_file TEXT,
        source_row INTEGER,
        raw_data TEXT,
        issue_type TEXT,
        issue_description TEXT,
        suggested_resolution TEXT,
        status TEXT DEFAULT 'pending',
        resolution TEXT,
        reviewed_by TEXT,
        reviewed_at TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX idx_dq_queue_status ON data_quality_queue(status);
    CREATE INDEX idx_dq_queue_issue_type ON data_quality_queue(issue_type);

    -- ========================================================================
    -- VENDOR SOURCE HISTORY (Data Provenance Tracking)
    -- ========================================================================

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
        FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id) ON DELETE CASCADE
    );

    CREATE INDEX idx_vendor_source_vendor ON vendor_source_history(vendor_id);
    CREATE INDEX idx_vendor_source_file ON vendor_source_history(source_file);

    """)

    conn.commit()
    conn.close()

    print(f"Database created successfully at: {DB_PATH}")

if __name__ == "__main__":
    create_database()