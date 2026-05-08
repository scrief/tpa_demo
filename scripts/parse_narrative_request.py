"""
Phase 9 - Natural Language Parser
Converts narrative buyer requests into structured criteria.
Supports OpenAI GPT and Google Gemini models.
"""

import json
import os
import re
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
AI_PROVIDER = os.getenv('AI_PROVIDER', 'openai').lower()
AI_ENABLED = os.getenv('AI_FEATURES_ENABLED', 'true').lower() == 'true'

# OpenAI configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_PARSING_MODEL = os.getenv('OPENAI_PARSING_MODEL', 'gpt-4o')

# Gemini configuration
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GEMINI_PARSING_MODEL = os.getenv('GEMINI_PARSING_MODEL', 'gemini-1.5-pro')

# Import appropriate client
if AI_PROVIDER == 'gemini':
    try:
        import google.generativeai as genai
        if GOOGLE_API_KEY:
            genai.configure(api_key=GOOGLE_API_KEY)
    except ImportError:
        print("Warning: google-generativeai not installed. Run: pip install google-generativeai")
        AI_ENABLED = False
else:
    try:
        import openai
    except ImportError:
        print("Warning: openai not installed. Run: pip install openai")
        AI_ENABLED = False


class NarrativeParser:
    """Parse natural language buyer requests into structured data."""
    
    # Valid options for each field
    VALID_INDUSTRIES = [
        "manufacturing", "construction", "healthcare", "retail", 
        "hospitality", "transportation", "technology", 
        "professional_services", "education", "government"
    ]
    
    VALID_CLAIM_TYPES = [
        "workers_comp", "general_liability", "auto_liability", 
        "property", "multi_line"
    ]
    
    VALID_PROGRAM_TYPES = [
        "self_insured", "fully_insured", "large_deductible"
    ]
    
    VALID_SERVICES = [
        "return_to_work", "nurse_case_management", "medical_bill_review",
        "fraud_investigation", "subrogation", "legal_support"
    ]
    
    # US State codes
    STATE_CODES = [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
    ]
    
    # State name to code mapping (for parsing state names)
    STATE_NAME_TO_CODE = {
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
        "wisconsin": "WI", "wyoming": "WY"
    }
    
    def __init__(self):
        """Initialize the parser."""
        self.provider = AI_PROVIDER
        self.enabled = AI_ENABLED
        
        if AI_PROVIDER == 'gemini':
            if not GOOGLE_API_KEY or GOOGLE_API_KEY == 'your_api_key_here':
                self.client = None
                self.enabled = False
            else:
                self.client = 'gemini'  # Flag to use Gemini
                self.model_name = GEMINI_PARSING_MODEL
        else:  # OpenAI
            if not OPENAI_API_KEY or OPENAI_API_KEY == 'your_api_key_here':
                self.client = None
                self.enabled = False
            else:
                self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
                self.model_name = OPENAI_PARSING_MODEL
    
    def parse_narrative_request(self, narrative_text: str) -> Dict[str, Any]:
        """
        Parse natural language buyer request into structured criteria.
        
        Args:
            narrative_text: User's natural language description
            
        Returns:
            dict with extracted fields:
                - industry (str or None)
                - claim_type_needed (str or None)
                - program_type (str or None)
                - required_states (list)
                - required_services (list)
                - priority_geography (int 1-5)
                - priority_claims (int 1-5)
                - priority_industry (int 1-5)
                - priority_services (int 1-5)
                - priority_reporting (int 1-5)
                - priority_technology (int 1-5)
                - priority_cost (int 1-5)
                - confidence_score (float 0-1)
                - extraction_notes (list of issues)
        """
        if not self.enabled or not self.client:
            return {
                'error': 'AI parsing not available. Please configure OPENAI_API_KEY in .env file.',
                'confidence_score': 0.0
            }
        
        try:
            # Build the prompt
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(narrative_text)
            
            # Call AI provider
            if self.provider == 'gemini':
                response_text = self._call_gemini(system_prompt, user_prompt)
            else:
                response_text = self._call_openai(system_prompt, user_prompt)
            
            # Parse response
            result = json.loads(response_text)
            
            # Validate and clean the result
            validated_result = self._validate_extraction(result)
            
            return validated_result
            
        except Exception as e:
            return {
                'error': f'Parsing failed: {str(e)}',
                'confidence_score': 0.0,
                'extraction_notes': [f'Error during parsing: {str(e)}']
            }
    
    def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        """Call OpenAI API."""
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    
    def _call_gemini(self, system_prompt: str, user_prompt: str) -> str:
        """Call Google Gemini API."""
        model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={
                "temperature": 0.2,
                "response_mime_type": "application/json"
            }
        )
        
        # Combine system and user prompts for Gemini
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        response = model.generate_content(full_prompt)
        return response.text
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for parsing."""
        return f"""You are a TPA (Third Party Administrator) matching assistant. Extract structured information from buyer requests.

Available industries: {', '.join(self.VALID_INDUSTRIES)}
Available claim types: {', '.join(self.VALID_CLAIM_TYPES)}
Available program types: {', '.join(self.VALID_PROGRAM_TYPES)}
Available services: {', '.join(self.VALID_SERVICES)}
Available states: Use two-letter US state codes (e.g., MN, WI, IA, CA, TX)

Priority scale (1-5):
- 5 (Critical): "critical", "must have", "essential", "major priority", "top priority"
- 4 (High): "important", "very important", "prefer", "strong preference"
- 3 (Moderate): Default - mentioned but no strong emphasis
- 2 (Low): "nice to have", "optional", "if available", "not critical"
- 1 (Very Low): "not important", "least important"

Special inference rules:
- Negative signals (e.g., "current TPA has service issues") → increase priority_performance to 4-5
- Negative signals (e.g., "poor reporting") → increase priority_reporting to 4-5
- Cost concerns (e.g., "budget-conscious", "cost-effective") → increase priority_cost to 4-5
- Technology mentions (e.g., "API", "integration", "portal") → increase priority_technology to 4-5

Extract only information explicitly stated or strongly implied. If uncertain, return null for that field.
Return valid JSON only."""
    
    def _build_user_prompt(self, narrative_text: str) -> str:
        """Build the user prompt for parsing."""
        return f"""Extract structured data from this buyer request:

"{narrative_text}"

Return JSON with exactly these fields (use null for unknown values):
{{
  "industry": "<one of the valid industries or null>",
  "claim_type_needed": "<one of the valid claim types or null>",
  "program_type": "<one of the valid program types or null>",
  "required_states": ["<state codes as 2-letter uppercase>"],
  "required_services": ["<service names from valid list>"],
  "priority_geography": <integer 1-5>,
  "priority_claims": <integer 1-5>,
  "priority_industry": <integer 1-5>,
  "priority_services": <integer 1-5>,
  "priority_reporting": <integer 1-5>,
  "priority_technology": <integer 1-5>,
  "priority_cost": <integer 1-5>,
  "confidence": <float 0-1 representing overall confidence>,
  "notes": ["<list any ambiguities or assumptions made>"]
}}"""
    
    def _validate_extraction(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean extracted data."""
        validated = {
            'industry': None,
            'claim_type_needed': None,
            'program_type': None,
            'required_states': [],
            'required_services': [],
            'priority_geography': 3,
            'priority_claims': 3,
            'priority_industry': 3,
            'priority_services': 3,
            'priority_reporting': 3,
            'priority_technology': 3,
            'priority_cost': 3,
            'confidence_score': 0.5,
            'extraction_notes': []
        }
        
        # Validate industry
        if result.get('industry') in self.VALID_INDUSTRIES:
            validated['industry'] = result['industry']
        elif result.get('industry'):
            validated['extraction_notes'].append(
                f"Invalid industry '{result['industry']}' was removed"
            )
        
        # Validate claim type
        if result.get('claim_type_needed') in self.VALID_CLAIM_TYPES:
            validated['claim_type_needed'] = result['claim_type_needed']
        elif result.get('claim_type_needed'):
            validated['extraction_notes'].append(
                f"Invalid claim type '{result['claim_type_needed']}' was removed"
            )
        
        # Validate program type
        if result.get('program_type') in self.VALID_PROGRAM_TYPES:
            validated['program_type'] = result['program_type']
        elif result.get('program_type'):
            validated['extraction_notes'].append(
                f"Invalid program type '{result['program_type']}' was removed"
            )
        
        # Validate states
        states = result.get('required_states', [])
        valid_states = [s.upper() for s in states if s.upper() in self.STATE_CODES]
        invalid_states = [s for s in states if s.upper() not in self.STATE_CODES]
        
        if invalid_states:
            validated['extraction_notes'].append(
                f"Invalid state codes removed: {', '.join(invalid_states)}"
            )
        
        validated['required_states'] = valid_states
        
        # Validate services
        services = result.get('required_services', [])
        valid_services = [s for s in services if s in self.VALID_SERVICES]
        invalid_services = [s for s in services if s not in self.VALID_SERVICES]
        
        if invalid_services:
            validated['extraction_notes'].append(
                f"Invalid services removed: {', '.join(invalid_services)}"
            )
        
        validated['required_services'] = valid_services
        
        # Validate priorities (must be 1-5)
        priority_fields = [
            'priority_geography', 'priority_claims', 'priority_industry',
            'priority_services', 'priority_reporting', 'priority_technology',
            'priority_cost'
        ]
        
        for field in priority_fields:
            value = result.get(field, 3)
            if isinstance(value, int) and 1 <= value <= 5:
                validated[field] = value
            else:
                validated[field] = 3
                validated['extraction_notes'].append(
                    f"{field} had invalid value, defaulted to 3"
                )
        
        # Validate confidence
        confidence = result.get('confidence', 0.5)
        if isinstance(confidence, (int, float)) and 0 <= confidence <= 1:
            validated['confidence_score'] = float(confidence)
        else:
            validated['confidence_score'] = 0.5
        
        # Add any notes from AI
        ai_notes = result.get('notes', [])
        if ai_notes:
            validated['extraction_notes'].extend(ai_notes)
        
        # Calculate adjusted confidence based on completeness
        completeness_score = self._calculate_completeness(validated)
        validated['confidence_score'] = (validated['confidence_score'] + completeness_score) / 2
        
        return validated
    
    def _calculate_completeness(self, data: Dict[str, Any]) -> float:
        """Calculate completeness score based on how many fields were extracted."""
        total_fields = 10  # industry, claim_type, program_type, states, services, 5 priorities
        filled_fields = 0
        
        if data.get('industry'):
            filled_fields += 1
        if data.get('claim_type_needed'):
            filled_fields += 1
        if data.get('program_type'):
            filled_fields += 1
        if data.get('required_states'):
            filled_fields += 1
        if data.get('required_services'):
            filled_fields += 1
        
        # Count non-default priorities (not 3)
        priority_fields = [
            'priority_geography', 'priority_claims', 'priority_industry',
            'priority_services', 'priority_reporting'
        ]
        for field in priority_fields:
            if data.get(field, 3) != 3:
                filled_fields += 0.5
        
        return filled_fields / total_fields


def parse_narrative_request(narrative_text: str) -> Dict[str, Any]:
    """
    Convenience function for parsing narrative requests.
    
    Args:
        narrative_text: Natural language buyer request
        
    Returns:
        Parsed and validated structured data
    """
    parser = NarrativeParser()
    return parser.parse_narrative_request(narrative_text)


# Command-line interface for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python parse_narrative_request.py '<narrative text>'")
        print("\nExample:")
        print('  python parse_narrative_request.py "We need a WC TPA for manufacturing in MN, WI, IA"')
        sys.exit(1)
    
    narrative = ' '.join(sys.argv[1:])
    print(f"Parsing: {narrative}\n")
    
    result = parse_narrative_request(narrative)
    print(json.dumps(result, indent=2))
