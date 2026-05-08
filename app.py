"""
TPA Match Demo - Streamlit Web Interface
Commonpoint Brand Identity Applied
"""

import streamlit as st
import sqlite3
import json
import subprocess
from pathlib import Path
from datetime import datetime
import sys
import plotly.graph_objects as go
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="TPA Match Demo | Commonpoint",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Commonpoint brand styling
def load_custom_css():
    """Apply Commonpoint brand identity styling."""
    st.markdown("""
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Open+Sans:wght@400;600&family=JetBrains+Mono:wght@400&display=swap');
        
        /* CSS Variables - Commonpoint Brand */
        :root {
            --color-primary: #001F3F;
            --color-secondary: #3A506B;
            --color-bg: #FFFFFF;
            --color-text: #4A4A4A;
            --color-divider: #E2E8F0;
            --color-success: #10B981;
            --radius-md: 8px;
            --font-main: 'Inter', sans-serif;
            --font-body: 'Open Sans', sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
        }
        
        /* Global Typography */
        html, body, [class*="css"] {
            font-family: var(--font-body);
            color: var(--color-text);
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-family: var(--font-main);
            font-weight: 700;
            color: var(--color-primary);
        }
        
        /* Main title styling */
        .main-title {
            font-family: var(--font-main);
            font-weight: 700;
            color: var(--color-primary);
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        
        .subtitle {
            font-family: var(--font-body);
            color: var(--color-secondary);
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }
        
        /* Buttons */
        .stButton>button {
            background-color: var(--color-primary);
            color: white;
            border-radius: var(--radius-md);
            border: none;
            padding: 12px 24px;
            font-family: var(--font-main);
            font-weight: 600;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            background-color: var(--color-secondary);
            box-shadow: 0 6px 8px -1px rgba(0, 0, 0, 0.15), 0 4px 6px -1px rgba(0, 0, 0, 0.08);
        }
        
        /* Input fields */
        .stTextInput>div>div>input,
        .stTextArea>div>div>textarea,
        .stSelectbox>div>div>select,
        .stMultiSelect>div>div>div {
            border-radius: var(--radius-md);
            border: 1px solid var(--color-divider);
            font-family: var(--font-body);
        }
        
        /* Cards and containers */
        .vendor-card {
            background: white;
            border-radius: var(--radius-md);
            padding: 24px;
            margin: 16px 0;
            border: 1px solid var(--color-divider);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
        
        /* Dividers */
        hr {
            border: none;
            border-top: 1px solid var(--color-divider);
            margin: 24px 0;
        }
        
        /* Success/Warning/Error boxes */
        .stSuccess {
            background-color: rgba(16, 185, 129, 0.1);
            border-left: 4px solid var(--color-success);
            border-radius: var(--radius-md);
        }
        
        .stWarning {
            background-color: rgba(251, 191, 36, 0.1);
            border-left: 4px solid #FBB024;
            border-radius: var(--radius-md);
        }
        
        .stError {
            background-color: rgba(239, 68, 68, 0.1);
            border-left: 4px solid #EF4444;
            border-radius: var(--radius-md);
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #F8FAFC;
            border-right: 1px solid var(--color-divider);
        }
        
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3 {
            color: var(--color-primary);
            font-family: var(--font-main);
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            font-family: var(--font-main);
            font-weight: 600;
            color: var(--color-primary);
            background-color: #F8FAFC;
            border-radius: var(--radius-md);
        }
        
        /* Progress bars */
        .stProgress > div > div > div {
            background-color: var(--color-primary);
            border-radius: var(--radius-md);
        }
        
        /* Score badges */
        .score-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 16px;
            font-family: var(--font-main);
            font-weight: 600;
            font-size: 0.9rem;
        }
        
        .score-high {
            background-color: rgba(16, 185, 129, 0.15);
            color: #059669;
        }
        
        .score-medium {
            background-color: rgba(251, 191, 36, 0.15);
            color: #D97706;
        }
        
        .score-low {
            background-color: rgba(239, 68, 68, 0.15);
            color: #DC2626;
        }
        
        /* Monospace for data */
        .data-value {
            font-family: var(--font-mono);
            font-size: 0.95rem;
            color: var(--color-secondary);
        }
        
        /* Radio and checkbox labels */
        .stRadio label, .stCheckbox label {
            font-family: var(--font-body);
            color: var(--color-text);
        }
        
        /* Slider labels */
        .stSlider label {
            font-family: var(--font-main);
            font-weight: 600;
            color: var(--color-primary);
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            font-family: var(--font-main);
            font-weight: 600;
            border-radius: var(--radius-md) var(--radius-md) 0 0;
            padding: 12px 24px;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: var(--color-primary);
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)

# Database path
DB_PATH = Path("database/tpa_match_demo.db")

# Helper functions
def get_db_connection():
    """Create database connection."""
    return sqlite3.connect(DB_PATH)

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

def get_score_badge_class(score, max_score=100):
    """Determine badge class based on score."""
    percentage = (score / max_score) * 100
    if percentage >= 75:
        return "score-high"
    elif percentage >= 50:
        return "score-medium"
    else:
        return "score-low"

# Page functions
def show_home():
    """Display home page."""
    st.markdown('<h1 class="main-title">TPA Match Demo</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Find the perfect TPA vendor for your needs</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🎯 Smart Matching")
        st.write("Our deterministic scoring engine evaluates vendors across 8 key categories to find your best matches.")
    
    with col2:
        st.markdown("### 📊 Transparent Scoring")
        st.write("Every recommendation includes detailed score breakdowns and clear reason codes explaining the ranking.")
    
    with col3:
        st.markdown("### ✅ Quality Assured")
        st.write("100% validated matching engine with comprehensive testing across diverse scenarios.")
    
    st.markdown("---")
    
    # Quick stats
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM vendors WHERE active_status = 'active'")
    vendor_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM buyer_requests")
    buyer_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM match_results")
    match_count = cursor.fetchone()[0]
    
    conn.close()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Active Vendors", vendor_count)
    
    with col2:
        st.metric("Buyer Scenarios", buyer_count)
    
    with col3:
        st.metric("Match Results", match_count)
    
    st.markdown("---")
    
    st.info("👈 Use the sidebar navigation to get started with a new match request or browse existing results.")

def create_buyer_request(form_data):
    """Create a new buyer request in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Insert buyer request
    cursor.execute("""
        INSERT INTO buyer_requests (
            buyer_name, industry, claim_type_needed, program_type,
            employee_count, priority_geography, priority_claims,
            priority_industry, priority_services, priority_reporting,
            priority_technology, priority_cost, narrative_request,
            pain_points, excluded_vendors, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        form_data['buyer_name'],
        form_data['industry'],
        form_data['claim_type_needed'],
        form_data['program_type'],
        form_data.get('employee_count'),
        form_data['priority_geography'],
        form_data['priority_claims'],
        form_data['priority_industry'],
        form_data['priority_services'],
        form_data['priority_reporting'],
        form_data['priority_technology'],
        form_data['priority_cost'],
        form_data.get('narrative_request', ''),
        form_data.get('pain_points', ''),
        form_data.get('excluded_vendors', ''),
        datetime.now().isoformat()
    ))
    
    buyer_id = cursor.lastrowid
    
    # Insert required states
    if form_data.get('required_states'):
        for state in form_data['required_states']:
            cursor.execute(
                "INSERT INTO buyer_required_states (buyer_request_id, state_code) VALUES (?, ?)",
                (buyer_id, state)
            )
    
    # Insert required services
    if form_data.get('required_services'):
        for service in form_data['required_services']:
            cursor.execute(
                "INSERT INTO buyer_required_services (buyer_request_id, service_name) VALUES (?, ?)",
                (buyer_id, service)
            )
    
    conn.commit()
    conn.close()
    
    return buyer_id

def show_match_form():
    """Display buyer request form."""
    st.markdown('<h1 class="main-title">New Match Request</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Tell us about your requirements and we\'ll find the best TPA vendors for you.</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    with st.form("match_request_form"):
        # Section 1: Basic Information
        st.markdown("### 📋 Basic Information")
        col1, col2 = st.columns(2)
        
        with col1:
            buyer_name = st.text_input(
                "Company Name *",
                placeholder="e.g., ABC Manufacturing",
                help="Enter your company name"
            )
            
            industry = st.selectbox(
                "Industry *",
                [
                    "manufacturing",
                    "construction",
                    "healthcare",
                    "retail",
                    "hospitality",
                    "transportation",
                    "technology",
                    "professional_services",
                    "education",
                    "government"
                ],
                format_func=lambda x: x.replace('_', ' ').title()
            )
            
            employee_count = st.number_input(
                "Employee Count",
                min_value=0,
                max_value=100000,
                value=0,
                step=1,
                help="Approximate number of employees"
            )
        
        with col2:
            claim_type_needed = st.selectbox(
                "Claim Type Needed *",
                [
                    "workers_comp",
                    "general_liability",
                    "auto_liability",
                    "property",
                    "multi_line"
                ],
                format_func=lambda x: x.replace('_', ' ').title()
            )
            
            program_type = st.selectbox(
                "Program Type",
                [
                    "self_insured",
                    "fully_insured",
                    "large_deductible"
                ],
                format_func=lambda x: x.replace('_', ' ').title()
            )
        
        st.markdown("---")
        
        # Section 2: Geographic Requirements
        st.markdown("### 🗺️ Geographic Requirements")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT state_code FROM vendor_states ORDER BY state_code")
        all_states = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        st.write("**Select Required States:** Check all states where you need TPA coverage")
        
        # Create grid of checkboxes (6 columns)
        cols_per_row = 6
        rows = [all_states[i:i + cols_per_row] for i in range(0, len(all_states), cols_per_row)]
        
        required_states = []
        for row in rows:
            cols = st.columns(cols_per_row)
            for idx, state in enumerate(row):
                with cols[idx]:
                    if st.checkbox(state, key=f"state_{state}"):
                        required_states.append(state)
        
        # Show selected count
        if required_states:
            st.success(f"✅ {len(required_states)} state(s) selected: {', '.join(sorted(required_states))}")
        else:
            st.warning("⚠️ Please select at least one state")
        
        priority_geography = st.slider(
            "Priority: Geographic Coverage",
            min_value=1,
            max_value=5,
            value=3,
            help="1 = Very Low, 3 = Moderate, 5 = Critical"
        )
        
        st.caption(f"**Priority Level:** {get_priority_label(priority_geography)}")
        
        st.markdown("---")
        
        # Section 3: Service Requirements
        st.markdown("### 🛠️ Service Requirements")
        
        service_options = [
            "return_to_work",
            "nurse_case_management",
            "medical_bill_review",
            "fraud_investigation",
            "subrogation",
            "legal_support"
        ]
        
        required_services = st.multiselect(
            "Required Services",
            service_options,
            format_func=lambda x: x.replace('_', ' ').title(),
            help="Select all services you require from your TPA"
        )
        
        priority_services = st.slider(
            "Priority: Service Capability",
            min_value=1,
            max_value=5,
            value=3,
            help="How important are these specific services?"
        )
        
        st.caption(f"**Priority Level:** {get_priority_label(priority_services)}")
        
        st.markdown("---")
        
        # Section 4: Other Priorities
        st.markdown("### 📊 Other Priorities")
        
        col1, col2 = st.columns(2)
        
        with col1:
            priority_claims = st.slider(
                "Claims Capability",
                min_value=1,
                max_value=5,
                value=3,
                help="How important is expertise in your specific claim type?"
            )
            st.caption(f"**{get_priority_label(priority_claims)}**")
            
            priority_industry = st.slider(
                "Industry Experience",
                min_value=1,
                max_value=5,
                value=3,
                help="How important is experience in your industry?"
            )
            st.caption(f"**{get_priority_label(priority_industry)}**")
            
            priority_reporting = st.slider(
                "Reporting & Analytics",
                min_value=1,
                max_value=5,
                value=3,
                help="How important are reporting capabilities?"
            )
            st.caption(f"**{get_priority_label(priority_reporting)}**")
        
        with col2:
            priority_technology = st.slider(
                "Technology Integration",
                min_value=1,
                max_value=5,
                value=3,
                help="How important is API/system integration?"
            )
            st.caption(f"**{get_priority_label(priority_technology)}**")
            
            priority_cost = st.slider(
                "Cost Sensitivity",
                min_value=1,
                max_value=5,
                value=3,
                help="How cost-sensitive is this selection? (5 = very cost-sensitive)"
            )
            st.caption(f"**{get_priority_label(priority_cost)}**")
        
        st.markdown("---")
        
        # Section 5: Optional Fields
        st.markdown("### 💬 Additional Information (Optional)")
        
        narrative_request = st.text_area(
            "Describe Your Needs",
            placeholder="e.g., We need a WC TPA for a self-insured manufacturing client with locations in MN, WI, and IA. RTW and reporting are major priorities.",
            help="Natural language description of your requirements"
        )
        
        excluded_vendors = st.text_input(
            "Excluded Vendors",
            placeholder="e.g., Vendor A, Vendor B (comma-separated)",
            help="Any vendors you want to exclude from consideration"
        )
        
        pain_points = st.text_area(
            "Current Pain Points",
            placeholder="e.g., Current TPA has slow response times and limited reporting",
            help="What issues are you experiencing with your current TPA?"
        )
        
        st.markdown("---")
        
        # Submit button
        submitted = st.form_submit_button("🎯 Find Matches", type="primary", use_container_width=True)
        
        if submitted:
            # Validate required fields
            if not buyer_name:
                st.error("❌ Please enter a company name")
            elif not required_states:
                st.error("❌ Please select at least one required state")
            else:
                # Prepare form data
                form_data = {
                    'buyer_name': buyer_name,
                    'industry': industry,
                    'claim_type_needed': claim_type_needed,
                    'program_type': program_type,
                    'employee_count': employee_count if employee_count > 0 else None,
                    'priority_geography': priority_geography,
                    'priority_claims': priority_claims,
                    'priority_industry': priority_industry,
                    'priority_services': priority_services,
                    'priority_reporting': priority_reporting,
                    'priority_technology': priority_technology,
                    'priority_cost': priority_cost,
                    'required_states': required_states,
                    'required_services': required_services,
                    'narrative_request': narrative_request,
                    'excluded_vendors': excluded_vendors,
                    'pain_points': pain_points
                }
                
                # Store in session state to process outside form
                st.session_state['pending_match_request'] = form_data
                st.session_state['form_submitted'] = True
    
    # Process form submission outside the form context
    if st.session_state.get('form_submitted', False):
        form_data = st.session_state.get('pending_match_request')
        
        if form_data:
            # Create buyer request
            with st.spinner("Processing your request..."):
                buyer_id = create_buyer_request(form_data)
            
            # Run matching engine
            with st.spinner("Finding the best TPA matches for you..."):
                result = subprocess.run(
                    ['python', 'scripts/match_vendors.py', str(buyer_id)],
                    capture_output=True,
                    text=True,
                    cwd=Path.cwd()
                )
            
            if result.returncode == 0:
                st.success("✅ Matching complete! View results below.")
                st.markdown("---")
                show_match_results(buyer_id)
            else:
                st.error(f"❌ Matching failed: {result.stderr}")
                st.code(result.stdout)
            
            # Clear session state
            st.session_state['form_submitted'] = False
            st.session_state['pending_match_request'] = None

def get_priority_label(priority_value):
    """Get human-readable label for priority value."""
    labels = {
        1: "Very Low - Not important",
        2: "Low - Minimal importance",
        3: "Moderate - Standard importance",
        4: "High - Very important",
        5: "Critical - Must be excellent"
    }
    return labels.get(priority_value, "Unknown")

def show_past_results():
    """Display past match results."""
    st.markdown('<h1 class="main-title">Past Match Results</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Review previous TPA vendor matches</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    conn = get_db_connection()
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
    """)
    
    results = cursor.fetchall()
    
    if not results:
        st.warning("No match results found. Run the matching engine first.")
        conn.close()
        return
    
    # Create a selection box instead of expanders
    buyer_options = [
        f"{name} - {industry.replace('_', ' ').title()} - {claim_type.replace('_', ' ').title()}" 
        for _, name, industry, claim_type, _ in results
    ]
    buyer_ids = [buyer_id for buyer_id, _, _, _, _ in results]
    
    selected_index = st.selectbox(
        "Select a buyer request to view results:",
        range(len(buyer_options)),
        format_func=lambda i: buyer_options[i]
    )
    
    conn.close()
    
    if selected_index is not None:
        st.markdown("---")
        show_match_results(buyer_ids[selected_index])

def save_feedback(buyer_id, usefulness, accuracy, comments):
    """Save user feedback to database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO feedback (
            buyer_request_id,
            usefulness,
            accuracy,
            comments,
            created_at
        ) VALUES (?, ?, ?, ?, ?)
    """, (buyer_id, usefulness, accuracy, comments, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

def create_radar_chart(matches):
    """Create a radar chart comparing top vendors."""
    if not matches or len(matches) == 0:
        return None
    
    # Take top 3 vendors
    top_vendors = matches[:3]
    
    fig = go.Figure()
    
    categories = ['Geography', 'Claims', 'Industry', 'Services', 'Reporting', 'Performance', 'Technology', 'Quality']
    
    for match in top_vendors:
        (rank, vendor_name, _, _, _, _, geo_score, claims_score, industry_score, 
         service_score, reporting_score, performance_score, tech_score, 
         quality_score, _, _, _) = match
        
        # Normalize scores to percentage of max for each category
        scores = [
            (geo_score / 20) * 100,
            (claims_score / 20) * 100,
            (industry_score / 15) * 100,
            (service_score / 15) * 100,
            (reporting_score / 10) * 100,
            (performance_score / 10) * 100,
            (tech_score / 5) * 100,
            (quality_score / 5) * 100
        ]
        
        fig.add_trace(go.Scatterpolar(
            r=scores,
            theta=categories,
            fill='toself',
            name=f"#{rank}. {vendor_name}"
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                ticksuffix='%'
            )
        ),
        showlegend=True,
        title="Vendor Comparison Across Categories",
        font=dict(family="Inter, sans-serif"),
        height=500
    )
    
    return fig

def create_score_bar_chart(score_categories):
    """Create a horizontal bar chart for score breakdown."""
    categories = [cat[0] for cat in score_categories]
    scores = [cat[1] for cat in score_categories]
    max_scores = [cat[2] for cat in score_categories]
    percentages = [(score/max_score)*100 if max_score > 0 else 0 
                   for score, max_score in zip(scores, max_scores)]
    
    # Assign colors based on percentage for better visibility
    colors = []
    for pct in percentages:
        if pct >= 75:
            colors.append('#10B981')  # Success Green
        elif pct >= 50:
            colors.append('#3A506B')  # Secondary Blue
        elif pct >= 25:
            colors.append('#FBB024')  # Warning Yellow
        else:
            colors.append('#94A3B8')  # Light Gray
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=categories,
        x=percentages,
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='#E2E8F0', width=1)
        ),
        text=[f"{score:.1f}/{max_score}" for score, max_score in zip(scores, max_scores)],
        textposition='inside',
        textfont=dict(color='white', size=12, family='Inter, sans-serif', weight='bold'),
        hovertemplate='<b>%{y}</b><br>Score: %{text}<br>Percentage: %{x:.1f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title="Score Breakdown by Category",
        xaxis_title="Percentage of Maximum Score",
        yaxis_title="",
        font=dict(family="Inter, sans-serif"),
        height=400,
        xaxis=dict(range=[0, 100], ticksuffix='%', gridcolor='#E2E8F0'),
        yaxis=dict(gridcolor='#E2E8F0'),
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

def show_match_results(buyer_id):
    """Display match results for a specific buyer."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get buyer details
    cursor.execute("SELECT * FROM buyer_requests WHERE buyer_request_id = ?", (buyer_id,))
    buyer_row = cursor.fetchone()
    
    if not buyer_row:
        st.error(f"Buyer request {buyer_id} not found.")
        conn.close()
        return
    
    # Get column names
    buyer_columns = [description[0] for description in cursor.description]
    buyer = dict(zip(buyer_columns, buyer_row))
    
    # Display buyer requirements
    st.markdown("#### Buyer Requirements")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write(f"**Industry:** {buyer['industry'].replace('_', ' ').title()}")
        st.write(f"**Claim Type:** {buyer['claim_type_needed'].replace('_', ' ').title()}")
    
    with col2:
        st.write(f"**Program Type:** {buyer.get('program_type', 'N/A').replace('_', ' ').title()}")
        employee_count = buyer.get('employee_count')
        if employee_count:
            st.write(f"**Employee Count:** {employee_count:,}")
        else:
            st.write(f"**Employee Count:** N/A")
    
    with col3:
        # Get required states
        cursor.execute("SELECT state_code FROM buyer_required_states WHERE buyer_request_id = ?", (buyer_id,))
        states = [row[0] for row in cursor.fetchall()]
        st.write(f"**Required States:** {', '.join(states) if states else 'N/A'}")
    
    st.markdown("---")
    
    # Get match results
    cursor.execute("""
        SELECT 
            m.rank,
            v.vendor_name,
            v.headquarters_state,
            v.company_size,
            v.pricing_level,
            m.total_score,
            m.geography_score,
            m.claims_score,
            m.industry_score,
            m.service_score,
            m.reporting_score,
            m.performance_score,
            m.technology_score,
            m.data_quality_score,
            m.reason_codes,
            m.risk_flags,
            m.human_review_required
        FROM match_results m
        JOIN vendors v ON m.vendor_id = v.vendor_id
        WHERE m.buyer_request_id = ?
        ORDER BY m.rank
        LIMIT 5
    """, (buyer_id,))
    
    matches = cursor.fetchall()
    
    if not matches:
        st.warning("No matches found for this buyer request.")
        conn.close()
        return
    
    st.markdown(f"### Top {len(matches)} Matches")
    
    # Check if any require human review
    if any(match[16] for match in matches):
        st.warning("⚠️ Some matches require human review - see flags below")
    
    # Show radar chart comparing top vendors
    if len(matches) >= 2:
        st.markdown("#### Vendor Comparison")
        radar_chart = create_radar_chart(matches)
        if radar_chart:
            st.plotly_chart(radar_chart, use_container_width=True)
        st.markdown("---")
    
    # Display each match
    for match in matches:
        (rank, vendor_name, hq_state, company_size, pricing_level, 
         total_score, geo_score, claims_score, industry_score, service_score,
         reporting_score, performance_score, tech_score, quality_score,
         reason_codes_json, risk_flags_json, human_review) = match
        
        # Score badge
        badge_class = get_score_badge_class(total_score)
        
        with st.expander(
            f"#{rank}. {vendor_name} - {total_score:.1f}/100",
            expanded=(rank == 1)
        ):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Vendor details
                st.markdown("#### Vendor Profile")
                st.write(f"**Headquarters:** {hq_state or 'Not specified'}")
                st.write(f"**Company Size:** {company_size.replace('_', ' ').title() if company_size else 'Not specified'}")
                st.write(f"**Pricing Level:** {pricing_level.replace('_', ' ').title() if pricing_level else 'Not specified'}")
                
                st.markdown("---")
                
                # Score breakdown with chart
                st.markdown("#### Score Breakdown")
                
                score_categories = [
                    ("Geography", geo_score, 20),
                    ("Claims Capability", claims_score, 20),
                    ("Industry Fit", industry_score, 15),
                    ("Service Capability", service_score, 15),
                    ("Reporting", reporting_score, 10),
                    ("Performance", performance_score, 10),
                    ("Technology", tech_score, 5),
                    ("Data Quality", quality_score, 5)
                ]
                
                # Show bar chart
                bar_chart = create_score_bar_chart(score_categories)
                st.plotly_chart(bar_chart, use_container_width=True)
            
            with col2:
                # Human review flag
                if human_review:
                    st.error("⚠️ **Human Review Required**")
                else:
                    st.success("✅ **Meets Quality Standards**")
                
                st.markdown("---")
                
                # Reason codes
                st.markdown("#### Why This Vendor?")
                if reason_codes_json:
                    reason_codes = json.loads(reason_codes_json)
                    for code in reason_codes[:5]:  # Show top 5
                        st.write(f"• {format_reason_code(code)}")
                else:
                    st.write("No reason codes available")
                
                # Risk flags
                if risk_flags_json:
                    risk_flags = json.loads(risk_flags_json)
                    if risk_flags:
                        st.markdown("---")
                        st.markdown("#### ⚠️ Considerations")
                        for flag in risk_flags:
                            st.warning(format_risk_flag(flag))
    
    # Feedback section (no nested form - use session state instead)
    st.markdown("---")
    st.markdown("### 💬 How did we do?")
    st.write("Your feedback helps us improve our matching recommendations.")
    
    # Initialize session state for feedback if not exists
    if f"feedback_submitted_{buyer_id}" not in st.session_state:
        st.session_state[f"feedback_submitted_{buyer_id}"] = False
    
    if not st.session_state[f"feedback_submitted_{buyer_id}"]:
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
            placeholder="What could we improve? Were any results surprising?",
            key=f"comments_{buyer_id}"
        )
        
        if st.button("Submit Feedback", key=f"submit_feedback_{buyer_id}", type="secondary"):
            save_feedback(buyer_id, usefulness, accuracy, comments)
            st.session_state[f"feedback_submitted_{buyer_id}"] = True
            st.success("✅ Thank you for your feedback!")
            st.rerun()
    else:
        st.success("✅ Thank you for your feedback!")
        if st.button("Submit New Feedback", key=f"reset_feedback_{buyer_id}", type="secondary"):
            st.session_state[f"feedback_submitted_{buyer_id}"] = False
            st.rerun()
    
    conn.close()

def show_vendor_directory():
    """Display vendor directory browser."""
    st.markdown('<h1 class="main-title">Vendor Directory</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Browse all TPA vendors in our database</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # State filter
        cursor.execute("SELECT DISTINCT state_code FROM vendor_states ORDER BY state_code")
        all_states = [row[0] for row in cursor.fetchall()]
        state_filter = st.multiselect("Filter by State", all_states)
    
    with col2:
        # Claim type filter
        cursor.execute("SELECT DISTINCT claim_type FROM vendor_claim_types ORDER BY claim_type")
        all_claim_types = ["All"] + [row[0] for row in cursor.fetchall()]
        claim_type_filter = st.selectbox("Filter by Claim Type", all_claim_types)
    
    with col3:
        # Search
        search = st.text_input("Search vendor name")
    
    # Build query
    query = "SELECT vendor_id, vendor_name, headquarters_state, company_size, pricing_level, satisfaction_score FROM vendors WHERE active_status = 'active'"
    params = []
    
    if state_filter:
        query += " AND vendor_id IN (SELECT vendor_id FROM vendor_states WHERE state_code IN ({seq}))".format(
            seq=','.join(['?']*len(state_filter))
        )
        params.extend(state_filter)
    
    if claim_type_filter != "All":
        query += " AND vendor_id IN (SELECT vendor_id FROM vendor_claim_types WHERE claim_type = ?)"
        params.append(claim_type_filter)
    
    if search:
        query += " AND vendor_name LIKE ?"
        params.append(f"%{search}%")
    
    query += " ORDER BY vendor_name"
    
    cursor.execute(query, params)
    vendors = cursor.fetchall()
    
    if not vendors:
        st.warning("No vendors found matching your filters.")
        conn.close()
        return
    
    st.write(f"Found **{len(vendors)}** vendors")
    
    # Display vendors
    for vendor_id, name, hq, size, pricing, satisfaction in vendors:
        with st.expander(f"**{name}** - {hq or 'HQ Not Specified'}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Company Size:** {size.replace('_', ' ').title() if size else 'Not specified'}")
                st.write(f"**Pricing Level:** {pricing.replace('_', ' ').title() if pricing else 'Not specified'}")
                st.write(f"**Satisfaction Score:** {satisfaction if satisfaction else 'Not available'}")
            
            with col2:
                # Get states
                cursor.execute("SELECT state_code FROM vendor_states WHERE vendor_id = ? ORDER BY state_code", (vendor_id,))
                states = [row[0] for row in cursor.fetchall()]
                st.write(f"**States Served:** {', '.join(states) if states else 'Not specified'}")
                
                # Get claim types
                cursor.execute("SELECT claim_type FROM vendor_claim_types WHERE vendor_id = ? ORDER BY claim_type", (vendor_id,))
                claim_types = [row[0].replace('_', ' ').title() for row in cursor.fetchall()]
                st.write(f"**Claim Types:** {', '.join(claim_types) if claim_types else 'Not specified'}")
    
    conn.close()

# Main app
def main():
    """Main application entry point."""
    # Load custom CSS
    load_custom_css()
    
    # Sidebar navigation
    st.sidebar.markdown("## Navigation")
    page = st.sidebar.radio(
        "Select a page:",
        ["🏠 Home", "🎯 New Match Request", "📊 View Results", "📁 Browse Vendors"],
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.info(
        "**TPA Match Demo** uses a validated matching engine to rank vendors "
        "across 8 scoring categories with complete transparency."
    )
    
    st.sidebar.markdown("---")
    st.sidebar.caption("Powered by Commonpoint")
    
    # Route to appropriate page
    if page == "🏠 Home":
        show_home()
    elif page == "🎯 New Match Request":
        show_match_form()
    elif page == "📊 View Results":
        show_past_results()
    elif page == "📁 Browse Vendors":
        show_vendor_directory()

if __name__ == "__main__":
    main()
