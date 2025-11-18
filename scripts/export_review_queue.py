"""
Export manual review queues to CSV.
Exports medium-confidence matches and suspicious duplicates for manual review.
"""

import pandas as pd
import sys
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def export_manual_review_queue(predictions_file: str, output_file: str = "manual_review_queue.csv") -> None:
    """
    Export manual review queue from Splink predictions.
    
    Args:
        predictions_file: Path to Splink predictions file
        output_file: Output CSV file path
    """
    try:
        predictions = pd.read_parquet(predictions_file) if predictions_file.endswith('.parquet') else pd.read_csv(predictions_file)
        
        # Filter for manual review (75-95% confidence)
        manual_review = predictions[
            (predictions['match_probability'] >= 0.75) &
            (predictions['match_probability'] < 0.95)
        ].copy()
        
        if len(manual_review) > 0:
            manual_review.to_csv(output_file, index=False)
            logger.info(f"Exported {len(manual_review)} pairs to {output_file}")
        else:
            logger.info("No pairs in manual review queue")
    except Exception as e:
        logger.error(f"Failed to export manual review queue: {e}")


def export_suspicious_duplicates(jobs_file: str, output_file: str = "suspicious_duplicates.csv") -> None:
    """
    Export suspicious duplicate jobs.
    
    Args:
        jobs_file: Path to jobs file
        output_file: Output CSV file path
    """
    try:
        from src.analytics.job_duplicate_detection import detect_all_duplicates
        
        jobs = pd.read_parquet(jobs_file) if jobs_file.endswith('.parquet') else pd.read_csv(jobs_file)
        jobs = detect_all_duplicates(jobs)
        
        # Get suspicious duplicates (Level 3)
        suspicious = jobs[jobs['is_duplicate_level_3'] == True].copy()
        
        if len(suspicious) > 0:
            suspicious.to_csv(output_file, index=False)
            logger.info(f"Exported {len(suspicious)} suspicious duplicates to {output_file}")
        else:
            logger.info("No suspicious duplicates found")
    except Exception as e:
        logger.error(f"Failed to export suspicious duplicates: {e}")


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python export_review_queue.py <predictions_file> [jobs_file]")
        sys.exit(1)
    
    predictions_file = sys.argv[1]
    jobs_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Export manual review queue
    export_manual_review_queue(predictions_file)
    
    # Export suspicious duplicates if jobs file provided
    if jobs_file:
        export_suspicious_duplicates(jobs_file)


if __name__ == '__main__':
    main()

