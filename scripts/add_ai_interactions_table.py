"""
Phase 9 - Database Migration: Add AI Interactions Table
Tracks all AI interactions for logging, debugging, and improvement.
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("database/tpa_match_demo.db")


def add_ai_interactions_table():
    """Add ai_interactions table to track AI feature usage."""
    
    print("Adding ai_interactions table to database...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create ai_interactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_interactions (
                interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                buyer_request_id INTEGER,
                interaction_type TEXT NOT NULL,
                input_text TEXT,
                output_json TEXT,
                model_used TEXT,
                confidence_score REAL,
                hallucinations_detected INTEGER DEFAULT 0,
                hallucination_details TEXT,
                user_rating TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (buyer_request_id) REFERENCES buyer_requests(buyer_request_id)
            )
        """)
        
        print("[OK] Created ai_interactions table")
        
        # Create index for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ai_interactions_buyer 
            ON ai_interactions(buyer_request_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ai_interactions_type 
            ON ai_interactions(interaction_type)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ai_interactions_created 
            ON ai_interactions(created_at)
        """)
        
        print("[OK] Created indexes for ai_interactions")
        
        conn.commit()
        
        # Verify table was created
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='ai_interactions'
        """)
        
        if cursor.fetchone():
            print("[OK] Verification successful: ai_interactions table exists")
            
            # Show table schema
            cursor.execute("PRAGMA table_info(ai_interactions)")
            columns = cursor.fetchall()
            print("\nTable Schema:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        else:
            print("[ERROR] Verification failed: table was not created")
        
        conn.close()
        
        print("\n[OK] Database migration complete!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error during migration: {e}")
        return False


def log_ai_interaction(
    interaction_type: str,
    input_text: str,
    output_json: str,
    model_used: str,
    confidence_score: float = None,
    buyer_request_id: int = None,
    hallucinations_detected: int = 0,
    hallucination_details: str = None
):
    """
    Log an AI interaction to the database.
    
    Args:
        interaction_type: Type of interaction ('parse', 'explain', 'followup')
        input_text: Input provided to AI
        output_json: JSON output from AI
        model_used: Model name used (e.g., 'gpt-4o')
        confidence_score: Confidence score (0-1)
        buyer_request_id: Associated buyer request ID
        hallucinations_detected: Number of hallucinations found
        hallucination_details: JSON string of hallucination details
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO ai_interactions (
                buyer_request_id, interaction_type, input_text, output_json,
                model_used, confidence_score, hallucinations_detected,
                hallucination_details, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            buyer_request_id,
            interaction_type,
            input_text,
            output_json,
            model_used,
            confidence_score,
            hallucinations_detected,
            hallucination_details,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        interaction_id = cursor.lastrowid
        conn.close()
        
        return interaction_id
        
    except Exception as e:
        print(f"Error logging AI interaction: {e}")
        return None


def update_interaction_rating(interaction_id: int, user_rating: str):
    """
    Update the user rating for an AI interaction.
    
    Args:
        interaction_id: ID of the interaction
        user_rating: Rating ('helpful', 'somewhat_helpful', 'not_helpful')
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE ai_interactions
            SET user_rating = ?
            WHERE interaction_id = ?
        """, (user_rating, interaction_id))
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Error updating rating: {e}")
        return False


def get_ai_interaction_stats():
    """Get statistics on AI interactions."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Total interactions
        cursor.execute("SELECT COUNT(*) FROM ai_interactions")
        total = cursor.fetchone()[0]
        
        # By type
        cursor.execute("""
            SELECT interaction_type, COUNT(*) 
            FROM ai_interactions 
            GROUP BY interaction_type
        """)
        by_type = dict(cursor.fetchall())
        
        # Hallucination rate
        cursor.execute("""
            SELECT 
                COUNT(*) as total_explanations,
                SUM(CASE WHEN hallucinations_detected > 0 THEN 1 ELSE 0 END) as with_hallucinations,
                AVG(hallucinations_detected) as avg_hallucinations
            FROM ai_interactions
            WHERE interaction_type = 'explain'
        """)
        hallucination_stats = cursor.fetchone()
        
        # User ratings
        cursor.execute("""
            SELECT user_rating, COUNT(*)
            FROM ai_interactions
            WHERE user_rating IS NOT NULL
            GROUP BY user_rating
        """)
        ratings = dict(cursor.fetchall())
        
        # Average confidence
        cursor.execute("""
            SELECT AVG(confidence_score)
            FROM ai_interactions
            WHERE confidence_score IS NOT NULL
        """)
        avg_confidence = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_interactions': total,
            'by_type': by_type,
            'hallucination_stats': {
                'total_explanations': hallucination_stats[0] if hallucination_stats else 0,
                'with_hallucinations': hallucination_stats[1] if hallucination_stats else 0,
                'avg_per_explanation': hallucination_stats[2] if hallucination_stats else 0
            },
            'user_ratings': ratings,
            'avg_confidence': avg_confidence
        }
        
    except Exception as e:
        print(f"Error getting stats: {e}")
        return None


# Command-line interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'stats':
        print("AI Interaction Statistics:\n")
        stats = get_ai_interaction_stats()
        
        if stats:
            print(f"Total Interactions: {stats['total_interactions']}")
            print(f"\nBy Type:")
            for itype, count in stats['by_type'].items():
                print(f"  - {itype}: {count}")
            
            print(f"\nHallucination Stats:")
            hstats = stats['hallucination_stats']
            print(f"  - Total Explanations: {hstats['total_explanations']}")
            print(f"  - With Hallucinations: {hstats['with_hallucinations']}")
            if hstats['total_explanations'] > 0:
                rate = (hstats['with_hallucinations'] / hstats['total_explanations']) * 100
                print(f"  - Hallucination Rate: {rate:.1f}%")
            print(f"  - Avg per Explanation: {hstats['avg_per_explanation']:.2f}")
            
            if stats['user_ratings']:
                print(f"\nUser Ratings:")
                for rating, count in stats['user_ratings'].items():
                    print(f"  - {rating}: {count}")
            
            if stats['avg_confidence']:
                print(f"\nAverage Confidence: {stats['avg_confidence']:.2f}")
    else:
        add_ai_interactions_table()
