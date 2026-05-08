"""
Phase 9 - Hallucination Detector
Detects factual errors in AI-generated explanations.
"""

import re
import json
import sqlite3
from typing import List, Dict, Any, Set, Optional
from pathlib import Path

DB_PATH = Path("database/tpa_match_demo.db")


class HallucinationDetector:
    """Detect factual errors in AI-generated text."""
    
    # US State codes and names for detection
    STATE_CODES = [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
    ]
    
    STATE_NAMES = {
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
    
    # Service keywords for detection
    SERVICE_KEYWORDS = {
        'return_to_work': ['return to work', 'return-to-work', 'rtw'],
        'nurse_case_management': ['nurse case management', 'case management', 'ncm'],
        'medical_bill_review': ['medical bill review', 'bill review', 'mbr'],
        'fraud_investigation': ['fraud investigation', 'fraud', 'siu'],
        'subrogation': ['subrogation', 'recovery'],
        'legal_support': ['legal support', 'legal services', 'litigation']
    }
    
    def __init__(self):
        """Initialize the detector."""
        pass
    
    def detect_hallucinations(
        self,
        ai_explanation: str,
        vendor_id: int,
        buyer_request_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect factual errors in AI-generated explanation.
        
        Args:
            ai_explanation: AI-generated text to verify
            vendor_id: Vendor being explained
            buyer_request_id: Optional buyer request ID
            
        Returns:
            list of hallucinations:
                [{
                    "claim": "Description of what AI claimed",
                    "issue": "Why it's wrong",
                    "severity": "high|medium|low",
                    "category": "state|service|score|capability"
                }]
        """
        hallucinations = []
        
        # Get actual vendor data
        vendor_data = self._get_vendor_data(vendor_id)
        if not vendor_data:
            return [{
                "claim": "Unable to verify",
                "issue": "Could not retrieve vendor data from database",
                "severity": "high",
                "category": "system"
            }]
        
        # Check state claims
        hallucinations.extend(self._check_state_claims(ai_explanation, vendor_data))
        
        # Check service claims
        hallucinations.extend(self._check_service_claims(ai_explanation, vendor_data))
        
        # Check score claims
        hallucinations.extend(self._check_score_claims(ai_explanation, vendor_data))
        
        # Check claim type capabilities
        hallucinations.extend(self._check_claim_type_claims(ai_explanation, vendor_data))
        
        # Check industry claims
        hallucinations.extend(self._check_industry_claims(ai_explanation, vendor_data))
        
        return hallucinations
    
    def _get_vendor_data(self, vendor_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve vendor data from database."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Get vendor profile
            cursor.execute("""
                SELECT 
                    vendor_name, satisfaction_score, reporting_score,
                    response_time_days
                FROM vendors
                WHERE vendor_id = ?
            """, (vendor_id,))
            
            row = cursor.fetchone()
            if not row:
                conn.close()
                return None
            
            vendor_data = {
                'vendor_id': vendor_id,
                'vendor_name': row[0],
                'satisfaction_score': row[1],
                'reporting_score': row[2],
                'response_time_days': row[3]
            }
            
            # Get states served
            cursor.execute("""
                SELECT state_code FROM vendor_states
                WHERE vendor_id = ?
            """, (vendor_id,))
            vendor_data['states_served'] = set(row[0] for row in cursor.fetchall())
            
            # Get services offered
            cursor.execute("""
                SELECT service_name FROM vendor_services
                WHERE vendor_id = ?
            """, (vendor_id,))
            vendor_data['services'] = set(row[0] for row in cursor.fetchall())
            
            # Get claim types
            cursor.execute("""
                SELECT claim_type FROM vendor_claim_types
                WHERE vendor_id = ?
            """, (vendor_id,))
            vendor_data['claim_types'] = set(row[0] for row in cursor.fetchall())
            
            # Get industries
            cursor.execute("""
                SELECT industry FROM vendor_industries
                WHERE vendor_id = ?
            """, (vendor_id,))
            vendor_data['industries'] = set(row[0] for row in cursor.fetchall())
            
            conn.close()
            return vendor_data
            
        except Exception as e:
            print(f"Error retrieving vendor data: {e}")
            return None
    
    def _extract_states_from_text(self, text: str) -> Set[str]:
        """Extract state mentions from text."""
        text_lower = text.lower()
        states_found = set()
        
        # Look for state codes (e.g., "MN", "WI", "CA")
        state_code_pattern = r'\b(' + '|'.join(self.STATE_CODES) + r')\b'
        matches = re.finditer(state_code_pattern, text, re.IGNORECASE)
        for match in matches:
            states_found.add(match.group(1).upper())
        
        # Look for state names
        for state_name, state_code in self.STATE_NAMES.items():
            if state_name in text_lower:
                states_found.add(state_code)
        
        return states_found
    
    def _check_state_claims(
        self,
        text: str,
        vendor_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check if AI claimed states the vendor doesn't serve."""
        hallucinations = []
        
        mentioned_states = self._extract_states_from_text(text)
        actual_states = vendor_data['states_served']
        
        # Find states mentioned but not served
        false_states = mentioned_states - actual_states
        
        for state in false_states:
            # Check context to avoid false positives (e.g., "not in CA")
            if not self._is_negative_context(text, state):
                hallucinations.append({
                    "claim": f"Vendor serves {state}",
                    "issue": f"Vendor does not serve {state} according to database",
                    "severity": "high",
                    "category": "state"
                })
        
        return hallucinations
    
    def _check_service_claims(
        self,
        text: str,
        vendor_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check if AI claimed services the vendor doesn't offer."""
        hallucinations = []
        text_lower = text.lower()
        
        actual_services = vendor_data['services']
        
        # Check for each service type
        for service_key, keywords in self.SERVICE_KEYWORDS.items():
            service_mentioned = any(keyword in text_lower for keyword in keywords)
            service_offered = service_key in actual_services
            
            if service_mentioned and not service_offered:
                # Check if it's in a negative context
                if not self._is_negative_context_for_service(text, keywords):
                    hallucinations.append({
                        "claim": f"Offers {service_key.replace('_', ' ')}",
                        "issue": f"Service not listed in vendor profile",
                        "severity": "medium",
                        "category": "service"
                    })
        
        return hallucinations
    
    def _check_score_claims(
        self,
        text: str,
        vendor_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check if AI mentioned scores that don't match database."""
        hallucinations = []
        
        # Extract numeric claims (e.g., "92/100", "85%", "score of 90")
        score_patterns = [
            r'(\d+)/100',
            r'(\d+)%',
            r'score of (\d+)',
            r'rating of (\d+)',
            r'satisfaction.*?(\d+)'
        ]
        
        mentioned_scores = set()
        for pattern in score_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                score = int(match.group(1))
                mentioned_scores.add(score)
        
        # Get actual scores
        actual_scores = []
        if vendor_data.get('satisfaction_score'):
            actual_scores.append(vendor_data['satisfaction_score'])
        if vendor_data.get('reporting_score'):
            actual_scores.append(vendor_data['reporting_score'])
        
        # Check if mentioned scores are within ±5% of actual scores
        for mentioned in mentioned_scores:
            if not any(abs(mentioned - actual) <= 5 for actual in actual_scores if actual):
                hallucinations.append({
                    "claim": f"Score of {mentioned}",
                    "issue": f"Score doesn't match database values: {actual_scores}",
                    "severity": "medium",
                    "category": "score"
                })
        
        return hallucinations
    
    def _check_claim_type_claims(
        self,
        text: str,
        vendor_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check if AI claimed claim types the vendor doesn't handle."""
        hallucinations = []
        text_lower = text.lower()
        
        actual_claim_types = vendor_data['claim_types']
        
        # Claim type keywords
        claim_type_keywords = {
            'workers_comp': ['workers comp', "workers' comp", 'wc', 'workers compensation'],
            'general_liability': ['general liability', 'gl'],
            'auto_liability': ['auto liability', 'auto', 'vehicle'],
            'property': ['property', 'property damage'],
            'multi_line': ['multi-line', 'multiline', 'multiple lines']
        }
        
        for claim_type, keywords in claim_type_keywords.items():
            mentioned = any(keyword in text_lower for keyword in keywords)
            supported = claim_type in actual_claim_types
            
            if mentioned and not supported:
                if not self._is_negative_context_generic(text, keywords[0]):
                    hallucinations.append({
                        "claim": f"Handles {claim_type.replace('_', ' ')}",
                        "issue": f"Claim type not in vendor profile",
                        "severity": "high",
                        "category": "capability"
                    })
        
        return hallucinations
    
    def _check_industry_claims(
        self,
        text: str,
        vendor_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check if AI claimed industries the vendor doesn't serve."""
        hallucinations = []
        text_lower = text.lower()
        
        actual_industries = vendor_data['industries']
        
        # Industry keywords
        industry_keywords = [
            'manufacturing', 'construction', 'healthcare', 'retail',
            'hospitality', 'transportation', 'technology', 'education',
            'government', 'professional services'
        ]
        
        for industry in industry_keywords:
            if industry in text_lower:
                industry_db = industry.replace(' ', '_')
                if industry_db not in actual_industries:
                    # Only flag if it's claiming expertise, not just mentioning
                    expertise_phrases = [
                        f'experience in {industry}',
                        f'expertise in {industry}',
                        f'{industry} industry',
                        f'serves {industry}',
                        f'{industry} clients'
                    ]
                    
                    if any(phrase in text_lower for phrase in expertise_phrases):
                        hallucinations.append({
                            "claim": f"Experience in {industry}",
                            "issue": f"Industry not listed in vendor profile",
                            "severity": "low",
                            "category": "capability"
                        })
        
        return hallucinations
    
    def _is_negative_context(self, text: str, state: str) -> bool:
        """Check if state mention is in a negative context (e.g., 'does not serve CA')."""
        # Look for negation words near the state mention
        negation_words = [
            'not', 'no', 'doesn\'t', 'does not', 'cannot', 'can\'t',
            'except', 'excluding', 'without', 'outside'
        ]
        
        # Find state mention
        pattern = rf'\b{state}\b'
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            return False
        
        # Check 50 characters before and after
        start = max(0, match.start() - 50)
        end = min(len(text), match.end() + 50)
        context = text[start:end].lower()
        
        return any(neg in context for neg in negation_words)
    
    def _is_negative_context_for_service(self, text: str, keywords: List[str]) -> bool:
        """Check if service mention is in a negative context."""
        text_lower = text.lower()
        
        for keyword in keywords:
            if keyword in text_lower:
                # Find position
                pos = text_lower.find(keyword)
                start = max(0, pos - 50)
                end = min(len(text), pos + len(keyword) + 50)
                context = text[start:end].lower()
                
                negation_words = ['not', 'no', 'doesn\'t', 'does not', 'without', 'lacking']
                if any(neg in context for neg in negation_words):
                    return True
        
        return False
    
    def _is_negative_context_generic(self, text: str, phrase: str) -> bool:
        """Check if phrase is in a negative context."""
        text_lower = text.lower()
        
        if phrase.lower() not in text_lower:
            return False
        
        pos = text_lower.find(phrase.lower())
        start = max(0, pos - 50)
        end = min(len(text), pos + len(phrase) + 50)
        context = text[start:end].lower()
        
        negation_words = ['not', 'no', 'doesn\'t', 'does not', 'cannot', 'without']
        return any(neg in context for neg in negation_words)


def detect_hallucinations(
    ai_explanation: str,
    vendor_id: int,
    buyer_request_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Convenience function for detecting hallucinations.
    
    Args:
        ai_explanation: AI-generated text
        vendor_id: Vendor being explained
        buyer_request_id: Optional buyer request ID
        
    Returns:
        List of detected hallucinations
    """
    detector = HallucinationDetector()
    return detector.detect_hallucinations(ai_explanation, vendor_id, buyer_request_id)


# Command-line interface for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python detect_hallucinations.py <vendor_id> '<explanation_text>'")
        print("\nExample:")
        print('  python detect_hallucinations.py 1 "This vendor serves California and offers AI-powered claims routing."')
        sys.exit(1)
    
    vendor_id = int(sys.argv[1])
    explanation_text = ' '.join(sys.argv[2:])
    
    print(f"Checking explanation for Vendor {vendor_id}\n")
    print(f"Text: {explanation_text}\n")
    
    hallucinations = detect_hallucinations(explanation_text, vendor_id)
    
    if hallucinations:
        print(f"⚠️ Found {len(hallucinations)} potential hallucination(s):\n")
        for h in hallucinations:
            print(f"[{h['severity'].upper()}] {h['category']}")
            print(f"  Claim: {h['claim']}")
            print(f"  Issue: {h['issue']}")
            print()
    else:
        print("✅ No hallucinations detected. All claims appear grounded in database.")
