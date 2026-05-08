"""
Phase 9 - AI Explanation Generator
Converts structured reason codes into plain-English narratives.
Supports OpenAI GPT and Google Gemini models.
"""

import json
import os
import sqlite3
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
AI_PROVIDER = os.getenv('AI_PROVIDER', 'openai').lower()
AI_ENABLED = os.getenv('AI_FEATURES_ENABLED', 'true').lower() == 'true'
DB_PATH = Path("database/tpa_match_demo.db")

# OpenAI configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_EXPLANATION_MODEL = os.getenv('OPENAI_EXPLANATION_MODEL', 'gpt-4o-mini')

# Gemini configuration
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GEMINI_EXPLANATION_MODEL = os.getenv('GEMINI_EXPLANATION_MODEL', 'gemini-1.5-flash')

# Import appropriate client
if AI_PROVIDER == 'gemini':
    try:
        import google.generativeai as genai
        if GOOGLE_API_KEY:
            genai.configure(api_key=GOOGLE_API_KEY)
    except ImportError:
        print("Warning: google-generativeai not installed")
        AI_ENABLED = False
else:
    try:
        import openai
    except ImportError:
        print("Warning: openai not installed")
        AI_ENABLED = False


class ExplanationGenerator:
    """Generate plain-English explanations for vendor matches."""
    
    def __init__(self):
        """Initialize the generator."""
        self.provider = AI_PROVIDER
        self.enabled = AI_ENABLED
        
        if AI_PROVIDER == 'gemini':
            if not GOOGLE_API_KEY or GOOGLE_API_KEY == 'your_api_key_here':
                self.client = None
                self.enabled = False
            else:
                self.client = 'gemini'
                self.model_name = GEMINI_EXPLANATION_MODEL
        else:  # OpenAI
            if not OPENAI_API_KEY or OPENAI_API_KEY == 'your_api_key_here':
                self.client = None
                self.enabled = False
            else:
                self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
                self.model_name = OPENAI_EXPLANATION_MODEL
    
    def generate_explanation(
        self,
        vendor_id: int,
        buyer_request_id: int,
        match_result_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate plain-English explanation for vendor match.
        
        Args:
            vendor_id: ID of the vendor
            buyer_request_id: ID of the buyer request
            match_result_id: Optional ID of match result (if None, queries from DB)
            
        Returns:
            dict with:
                - explanation (str): The narrative explanation
                - vendor_name (str): Vendor name
                - error (str): Error message if generation failed
        """
        if not self.enabled or not self.client:
            return {
                'error': 'AI explanation not available. Please configure OPENAI_API_KEY in .env file.'
            }
        
        try:
            # Gather data from database
            vendor_data = self._get_vendor_data(vendor_id)
            buyer_data = self._get_buyer_data(buyer_request_id)
            match_data = self._get_match_data(vendor_id, buyer_request_id)
            
            if not vendor_data or not buyer_data or not match_data:
                return {
                    'error': 'Could not retrieve required data from database.'
                }
            
            # Build the prompt
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(vendor_data, buyer_data, match_data)
            
            # Call AI provider
            if self.provider == 'gemini':
                explanation = self._call_gemini(system_prompt, user_prompt)
            else:
                explanation = self._call_openai(system_prompt, user_prompt)
            
            return {
                'explanation': explanation,
                'vendor_name': vendor_data['vendor_name'],
                'total_score': match_data['total_score']
            }
            
        except Exception as e:
            return {
                'error': f'Explanation generation failed: {str(e)}'
            }
    
    def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        """Call OpenAI API."""
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )
        return response.choices[0].message.content.strip()
    
    def _call_gemini(self, system_prompt: str, user_prompt: str) -> str:
        """Call Google Gemini API."""
        model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 800
            }
        )
        
        # Combine prompts for Gemini
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        response = model.generate_content(full_prompt)
        return response.text.strip()
    
    def _get_vendor_data(self, vendor_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve vendor data from database."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Get vendor profile
            cursor.execute("""
                SELECT 
                    vendor_name, headquarters_state, company_size, pricing_level,
                    satisfaction_score, reporting_score, response_time_days
                FROM vendors
                WHERE vendor_id = ?
            """, (vendor_id,))
            
            row = cursor.fetchone()
            if not row:
                conn.close()
                return None
            
            vendor_data = {
                'vendor_name': row[0],
                'headquarters_state': row[1],
                'company_size': row[2],
                'pricing_level': row[3],
                'satisfaction_score': row[4],
                'reporting_score': row[5],
                'response_time_days': row[6]
            }
            
            # Get states served
            cursor.execute("""
                SELECT state_code FROM vendor_states
                WHERE vendor_id = ?
                ORDER BY state_code
            """, (vendor_id,))
            vendor_data['states_served'] = [row[0] for row in cursor.fetchall()]
            
            # Get claim types
            cursor.execute("""
                SELECT claim_type, is_primary_focus FROM vendor_claim_types
                WHERE vendor_id = ?
                ORDER BY is_primary_focus DESC, claim_type
            """, (vendor_id,))
            claim_types = []
            for row in cursor.fetchall():
                claim_types.append({
                    'claim_type': row[0],
                    'is_primary_focus': bool(row[1])
                })
            vendor_data['claim_types'] = claim_types
            
            # Get industries served
            cursor.execute("""
                SELECT industry FROM vendor_industries
                WHERE vendor_id = ?
                ORDER BY industry
            """, (vendor_id,))
            vendor_data['industries'] = [row[0] for row in cursor.fetchall()]
            
            # Get services offered
            cursor.execute("""
                SELECT service_name FROM vendor_services
                WHERE vendor_id = ?
                ORDER BY service_name
            """, (vendor_id,))
            vendor_data['services'] = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            return vendor_data
            
        except Exception as e:
            print(f"Error retrieving vendor data: {e}")
            return None
    
    def _get_buyer_data(self, buyer_request_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve buyer request data from database."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Get buyer request
            cursor.execute("""
                SELECT 
                    buyer_name, industry, claim_type_needed, program_type,
                    employee_count, priority_geography, priority_claims,
                    priority_industry, priority_services, priority_reporting,
                    priority_technology
                FROM buyer_requests
                WHERE buyer_request_id = ?
            """, (buyer_request_id,))
            
            row = cursor.fetchone()
            if not row:
                conn.close()
                return None
            
            buyer_data = {
                'buyer_name': row[0],
                'industry': row[1],
                'claim_type_needed': row[2],
                'program_type': row[3],
                'employee_count': row[4],
                'priority_geography': row[5],
                'priority_claims': row[6],
                'priority_industry': row[7],
                'priority_services': row[8],
                'priority_reporting': row[9],
                'priority_technology': row[10]
            }
            
            # Get required states
            cursor.execute("""
                SELECT state_code FROM buyer_required_states
                WHERE buyer_request_id = ?
                ORDER BY state_code
            """, (buyer_request_id,))
            buyer_data['required_states'] = [row[0] for row in cursor.fetchall()]
            
            # Get required services
            cursor.execute("""
                SELECT service_name FROM buyer_required_services
                WHERE buyer_request_id = ?
                ORDER BY service_name
            """, (buyer_request_id,))
            buyer_data['required_services'] = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            return buyer_data
            
        except Exception as e:
            print(f"Error retrieving buyer data: {e}")
            return None
    
    def _get_match_data(self, vendor_id: int, buyer_request_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve match result data from database."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    rank, total_score, geography_score, claims_score,
                    industry_score, service_score, reporting_score,
                    performance_score, technology_score, data_quality_score,
                    reason_codes, risk_flags, human_review_required
                FROM match_results
                WHERE vendor_id = ? AND buyer_request_id = ?
            """, (vendor_id, buyer_request_id))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
            
            return {
                'rank': row[0],
                'total_score': row[1],
                'geography_score': row[2],
                'claims_score': row[3],
                'industry_score': row[4],
                'service_score': row[5],
                'reporting_score': row[6],
                'performance_score': row[7],
                'technology_score': row[8],
                'data_quality_score': row[9],
                'reason_codes': json.loads(row[10]) if row[10] else [],
                'risk_flags': json.loads(row[11]) if row[11] else [],
                'human_review_required': bool(row[12])
            }
            
        except Exception as e:
            print(f"Error retrieving match data: {e}")
            return None
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for explanation generation."""
        return """You are a TPA (Third Party Administrator) matching expert explaining vendor recommendations to insurance buyers.

CRITICAL RULES:
1. Base EVERY claim on the provided data (vendor_data, buyer_requirements, match_result)
2. NEVER invent facts, statistics, or capabilities not in the data
3. Reference specific reason codes from match_result
4. Mention actual scores when available (e.g., "satisfaction score of 92/100")
5. Include risk flags naturally in the narrative if present
6. Be concise (2-4 paragraphs maximum)
7. Professional, confident tone matching Commonpoint brand
8. Focus on "why" this vendor fits the buyer's needs
9. If data is missing for a claim, say "information not available" - NEVER make it up

FORMAT:
- Paragraph 1: Overall fit summary and key strengths
- Paragraph 2: Geographic coverage and local presence details
- Paragraph 3: Capability match (claims, industry, services)
- Paragraph 4 (optional): Performance metrics and any considerations/risk flags

Use natural, conversational language while remaining professional. Avoid bullet points."""
    
    def _build_user_prompt(
        self,
        vendor_data: Dict[str, Any],
        buyer_data: Dict[str, Any],
        match_data: Dict[str, Any]
    ) -> str:
        """Build the user prompt for explanation generation."""
        
        # Format reason codes for readability
        reason_codes_formatted = "\n".join(f"  - {code}" for code in match_data['reason_codes'])
        risk_flags_formatted = "\n".join(f"  - {flag}" for flag in match_data['risk_flags']) if match_data['risk_flags'] else "  None"
        
        return f"""Explain why this vendor is a good match for the buyer:

VENDOR PROFILE:
Name: {vendor_data['vendor_name']}
Headquarters: {vendor_data.get('headquarters_state', 'Not specified')}
Company Size: {vendor_data.get('company_size', 'Not specified')}
Pricing Level: {vendor_data.get('pricing_level', 'Not specified')}
Satisfaction Score: {vendor_data.get('satisfaction_score', 'Not available')}
Reporting Score: {vendor_data.get('reporting_score', 'Not available')}
Response Time: {vendor_data.get('response_time_days', 'Not available')} days
States Served: {', '.join(vendor_data['states_served'])}
Claim Types: {', '.join([f"{ct['claim_type']}{' (primary focus)' if ct['is_primary_focus'] else ''}" for ct in vendor_data['claim_types']])}
Industries: {', '.join(vendor_data['industries'])}
Services: {', '.join(vendor_data['services'])}

BUYER REQUIREMENTS:
Buyer: {buyer_data['buyer_name']}
Industry: {buyer_data['industry']}
Claim Type Needed: {buyer_data['claim_type_needed']}
Program Type: {buyer_data.get('program_type', 'Not specified')}
Required States: {', '.join(buyer_data['required_states'])}
Required Services: {', '.join(buyer_data['required_services']) if buyer_data['required_services'] else 'None specified'}
Top Priorities:
  - Geography: Priority {buyer_data['priority_geography']}/5
  - Claims Capability: Priority {buyer_data['priority_claims']}/5
  - Industry Experience: Priority {buyer_data['priority_industry']}/5
  - Services: Priority {buyer_data['priority_services']}/5
  - Reporting: Priority {buyer_data['priority_reporting']}/5
  - Technology: Priority {buyer_data['priority_technology']}/5

MATCH RESULT:
Rank: #{match_data['rank']}
Total Score: {match_data['total_score']:.1f}/100
Score Breakdown:
  - Geography: {match_data['geography_score']:.1f}/20
  - Claims: {match_data['claims_score']:.1f}/20
  - Industry: {match_data['industry_score']:.1f}/15
  - Services: {match_data['service_score']:.1f}/15
  - Reporting: {match_data['reporting_score']:.1f}/10
  - Performance: {match_data['performance_score']:.1f}/10
  - Technology: {match_data['technology_score']:.1f}/5
  - Data Quality: {match_data['data_quality_score']:.1f}/5

Reason Codes (explain these):
{reason_codes_formatted}

Risk Flags (mention if present):
{risk_flags_formatted}

Human Review Required: {'Yes' if match_data['human_review_required'] else 'No'}

Write a 2-4 paragraph explanation that:
1. Summarizes why this vendor is a strong match
2. Explains geographic fit and coverage
3. Details capability match (claims, industry, services)
4. Mentions performance metrics and any considerations
5. References specific data points and scores from above

Remember: Only use facts provided above. Never invent capabilities, scores, or coverage areas."""
    


def generate_explanation(
    vendor_id: int,
    buyer_request_id: int,
    match_result_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Convenience function for generating explanations.
    
    Args:
        vendor_id: ID of the vendor
        buyer_request_id: ID of the buyer request
        match_result_id: Optional ID of match result
        
    Returns:
        Explanation result dict
    """
    generator = ExplanationGenerator()
    return generator.generate_explanation(vendor_id, buyer_request_id, match_result_id)


# Command-line interface for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python generate_explanation.py <vendor_id> <buyer_request_id>")
        print("\nExample:")
        print("  python generate_explanation.py 1 1")
        sys.exit(1)
    
    vendor_id = int(sys.argv[1])
    buyer_request_id = int(sys.argv[2])
    
    print(f"Generating explanation for Vendor {vendor_id}, Buyer Request {buyer_request_id}\n")
    
    result = generate_explanation(vendor_id, buyer_request_id)
    
    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Vendor: {result['vendor_name']}")
        print(f"Score: {result['total_score']:.1f}/100")
        print(f"\nExplanation:\n{result['explanation']}")
