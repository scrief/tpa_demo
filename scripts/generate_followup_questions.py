"""
Phase 9 - Follow-up Question Generator
Generates clarifying questions to improve match quality.
"""

import sqlite3
from typing import List, Dict, Any, Optional
from pathlib import Path

DB_PATH = Path("database/tpa_match_demo.db")


class FollowUpQuestionGenerator:
    """Generate clarifying questions to improve match quality."""
    
    def __init__(self):
        """Initialize the generator."""
        pass
    
    def generate_followup_questions(
        self,
        buyer_request: Dict[str, Any],
        match_results: Optional[List[Dict[str, Any]]] = None,
        extraction_confidence: float = 1.0
    ) -> List[str]:
        """
        Generate clarifying questions to improve match quality.
        
        Args:
            buyer_request: Dict with buyer requirements
            match_results: List of top vendor matches (optional)
            extraction_confidence: 0-1 confidence from NLP parsing
            
        Returns:
            list of questions (max 5)
        """
        questions = []
        
        # Check for missing required fields
        questions.extend(self._check_missing_fields(buyer_request))
        
        # Check for low confidence extractions
        if extraction_confidence < 0.7:
            questions.extend(self._suggest_clarification(buyer_request, extraction_confidence))
        
        # Check for ambiguous priorities
        questions.extend(self._check_ambiguous_priorities(buyer_request))
        
        # Check match results for close scores
        if match_results:
            questions.extend(self._check_close_matches(match_results))
        
        # Check for data quality issues
        if match_results:
            questions.extend(self._check_data_quality_flags(match_results))
        
        # Return max 5 most important questions
        return questions[:5]
    
    def _check_missing_fields(self, buyer_request: Dict[str, Any]) -> List[str]:
        """Generate questions for missing required fields."""
        questions = []
        
        # Check for missing states
        if not buyer_request.get('required_states'):
            questions.append(
                "Which states do you need TPA coverage in? This is critical for finding qualified vendors."
            )
        
        # Check for missing claim type
        if not buyer_request.get('claim_type_needed'):
            questions.append(
                "What type of claims will this TPA primarily handle? (Workers' Comp, General Liability, Auto, Property, or Multi-line)"
            )
        
        # Check for missing industry
        if not buyer_request.get('industry'):
            questions.append(
                "What industry are you in? Industry-specific experience can significantly impact service quality."
            )
        
        # Check for missing services
        if not buyer_request.get('required_services'):
            questions.append(
                "Are there specific services you require, such as return-to-work programs, nurse case management, or fraud investigation?"
            )
        
        # Check for missing employee count
        if not buyer_request.get('employee_count') or buyer_request.get('employee_count') == 0:
            questions.append(
                "Approximately how many employees do you have? This helps us match you with appropriately-sized TPAs."
            )
        
        return questions
    
    def _suggest_clarification(
        self,
        buyer_request: Dict[str, Any],
        confidence: float
    ) -> List[str]:
        """Suggest clarification when AI confidence is low."""
        questions = []
        
        if confidence < 0.5:
            questions.append(
                "Could you provide more details about your requirements? We want to ensure we understand your needs correctly."
            )
        elif confidence < 0.7:
            # Check which fields are ambiguous
            if buyer_request.get('industry') and not buyer_request.get('employee_count'):
                questions.append(
                    "Could you clarify your company size and annual claim volume? This helps us match you with the right-sized TPA."
                )
        
        return questions
    
    def _check_ambiguous_priorities(self, buyer_request: Dict[str, Any]) -> List[str]:
        """Generate questions for ambiguous priorities."""
        questions = []
        
        priority_fields = [
            'priority_geography', 'priority_claims', 'priority_industry',
            'priority_services', 'priority_reporting', 'priority_technology',
            'priority_cost'
        ]
        
        priorities = [buyer_request.get(field, 3) for field in priority_fields]
        
        # Check if all priorities are the same
        if len(set(priorities)) == 1:
            if priorities[0] == 5:
                questions.append(
                    "All factors are marked as critical. Which 2-3 factors are MOST important for your decision? This helps us fine-tune your recommendations."
                )
            elif priorities[0] == 3:
                questions.append(
                    "Which factors matter most to you? For example, is geographic coverage, reporting capabilities, or cost more important?"
                )
        
        # Check if cost priority is unclear
        cost_priority = buyer_request.get('priority_cost', 3)
        if cost_priority == 3:
            questions.append(
                "How price-sensitive is this decision? This helps us balance cost with other factors."
            )
        
        # Check for conflicting priorities
        if buyer_request.get('priority_cost', 3) >= 4 and buyer_request.get('priority_services', 3) >= 4:
            questions.append(
                "You've indicated both cost and comprehensive services are important. Would you prefer a budget-friendly TPA with core services, or are you willing to pay more for premium capabilities?"
            )
        
        return questions
    
    def _check_close_matches(self, match_results: List[Dict[str, Any]]) -> List[str]:
        """Generate questions when match scores are close."""
        questions = []
        
        if len(match_results) < 2:
            return questions
        
        # Get top 3 scores
        top_scores = [m.get('total_score', 0) for m in match_results[:3]]
        
        if len(top_scores) >= 2:
            score_diff = max(top_scores) - min(top_scores)
            
            if score_diff < 5:
                questions.append(
                    "Several vendors are very close in overall fit. Do you have a preference for local vs. national TPAs, or specific technology integrations?"
                )
            
            # Check if geographic scores are similar
            geo_scores = [m.get('geography_score', 0) for m in match_results[:3]]
            if len(geo_scores) >= 2 and max(geo_scores) - min(geo_scores) < 2:
                questions.append(
                    "Multiple vendors cover your states. Would you prefer a TPA with adjusters physically located in your area, or is remote handling acceptable?"
                )
        
        return questions
    
    def _check_data_quality_flags(self, match_results: List[Dict[str, Any]]) -> List[str]:
        """Generate questions when data quality flags are present."""
        questions = []
        
        # Check if any top matches require human review
        human_review_needed = any(
            m.get('human_review_required', False) 
            for m in match_results[:3]
        )
        
        if human_review_needed:
            questions.append(
                "Some recommended vendors have incomplete information. Would you like us to contact them for updated details before making your decision?"
            )
        
        # Check for risk flags in top matches
        risk_flags_present = any(
            m.get('risk_flags') and len(m['risk_flags']) > 0
            for m in match_results[:3]
        )
        
        if risk_flags_present:
            questions.append(
                "Some vendors have considerations noted (e.g., partial state coverage or missing data). Are these deal-breakers, or would you like to explore them further?"
            )
        
        return questions
    
    def generate_followup_from_buyer_id(
        self,
        buyer_request_id: int
    ) -> List[str]:
        """
        Generate follow-up questions from a buyer request ID.
        
        Args:
            buyer_request_id: ID of buyer request in database
            
        Returns:
            List of follow-up questions
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Get buyer request
            cursor.execute("""
                SELECT 
                    buyer_name, industry, claim_type_needed, program_type,
                    employee_count, priority_geography, priority_claims,
                    priority_industry, priority_services, priority_reporting,
                    priority_technology, priority_cost
                FROM buyer_requests
                WHERE buyer_request_id = ?
            """, (buyer_request_id,))
            
            row = cursor.fetchone()
            if not row:
                conn.close()
                return ["Could not retrieve buyer request from database."]
            
            buyer_request = {
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
                'priority_technology': row[10],
                'priority_cost': row[11]
            }
            
            # Get required states
            cursor.execute("""
                SELECT state_code FROM buyer_required_states
                WHERE buyer_request_id = ?
            """, (buyer_request_id,))
            buyer_request['required_states'] = [row[0] for row in cursor.fetchall()]
            
            # Get required services
            cursor.execute("""
                SELECT service_name FROM buyer_required_services
                WHERE buyer_request_id = ?
            """, (buyer_request_id,))
            buyer_request['required_services'] = [row[0] for row in cursor.fetchall()]
            
            # Get match results
            cursor.execute("""
                SELECT 
                    total_score, geography_score, human_review_required,
                    risk_flags
                FROM match_results
                WHERE buyer_request_id = ?
                ORDER BY rank
                LIMIT 5
            """, (buyer_request_id,))
            
            match_results = []
            for row in cursor.fetchall():
                import json
                match_results.append({
                    'total_score': row[0],
                    'geography_score': row[1],
                    'human_review_required': bool(row[2]),
                    'risk_flags': json.loads(row[3]) if row[3] else []
                })
            
            conn.close()
            
            # Generate questions
            return self.generate_followup_questions(
                buyer_request,
                match_results,
                extraction_confidence=1.0  # Assume high confidence for manual entry
            )
            
        except Exception as e:
            print(f"Error generating follow-up questions: {e}")
            return ["Error retrieving data. Please try again."]


def generate_followup_questions(
    buyer_request: Dict[str, Any],
    match_results: Optional[List[Dict[str, Any]]] = None,
    extraction_confidence: float = 1.0
) -> List[str]:
    """
    Convenience function for generating follow-up questions.
    
    Args:
        buyer_request: Dict with buyer requirements
        match_results: List of top vendor matches
        extraction_confidence: 0-1 confidence from NLP parsing
        
    Returns:
        List of questions
    """
    generator = FollowUpQuestionGenerator()
    return generator.generate_followup_questions(
        buyer_request, match_results, extraction_confidence
    )


def generate_followup_from_buyer_id(buyer_request_id: int) -> List[str]:
    """
    Convenience function for generating questions from buyer ID.
    
    Args:
        buyer_request_id: ID of buyer request
        
    Returns:
        List of questions
    """
    generator = FollowUpQuestionGenerator()
    return generator.generate_followup_from_buyer_id(buyer_request_id)


# Command-line interface for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python generate_followup_questions.py <buyer_request_id>")
        print("\nExample:")
        print("  python generate_followup_questions.py 1")
        sys.exit(1)
    
    buyer_request_id = int(sys.argv[1])
    
    print(f"Generating follow-up questions for Buyer Request {buyer_request_id}\n")
    
    questions = generate_followup_from_buyer_id(buyer_request_id)
    
    if questions:
        print(f"💡 We have {len(questions)} question(s) to improve your matches:\n")
        for i, question in enumerate(questions, 1):
            print(f"{i}. {question}\n")
    else:
        print("✅ No additional questions needed. Your request is complete!")
