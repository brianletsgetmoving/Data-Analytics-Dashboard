#!/usr/bin/env python3
"""
Link BadLead records to LeadStatus based on matching criteria.
Since BadLead doesn't have quote_number, we'll match on email, phone, or name+location.
"""

import sys
from pathlib import Path
import psycopg2
from datetime import datetime
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.testing.database_connection import get_db_connection

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def link_badlead_to_leadstatus(conn, dry_run: bool = True):
    """Link BadLead records to LeadStatus."""
    cursor = conn.cursor()
    
    # Strategy: Match BadLead to LeadStatus via BookedOpportunity -> Customer
    # Then find LeadStatus records for the same customer
    
    # First, match via email
    cursor.execute("""
        UPDATE bad_leads bl
        SET lead_status_id = (
            SELECT ls.id
            FROM lead_status ls
            JOIN booked_opportunities bo ON ls.booked_opportunity_id = bo.id
            JOIN customers c ON bo.customer_id = c.id
            WHERE c.email = bl.customer_email
              AND c.email IS NOT NULL
              AND bl.customer_email IS NOT NULL
            ORDER BY ls.created_at ASC
            LIMIT 1
        ),
        updated_at = NOW()
        WHERE bl.lead_status_id IS NULL
          AND bl.customer_email IS NOT NULL
          AND EXISTS (
              SELECT 1
              FROM lead_status ls
              JOIN booked_opportunities bo ON ls.booked_opportunity_id = bo.id
              JOIN customers c ON bo.customer_id = c.id
              WHERE c.email = bl.customer_email
          )
    """)
    
    email_matches = cursor.rowcount
    
    # Match via phone
    cursor.execute("""
        UPDATE bad_leads bl
        SET lead_status_id = (
            SELECT ls.id
            FROM lead_status ls
            JOIN booked_opportunities bo ON ls.booked_opportunity_id = bo.id
            JOIN customers c ON bo.customer_id = c.id
            WHERE c.phone = bl.customer_phone
              AND c.phone IS NOT NULL
              AND bl.customer_phone IS NOT NULL
            ORDER BY ls.created_at ASC
            LIMIT 1
        ),
        updated_at = NOW()
        WHERE bl.lead_status_id IS NULL
          AND bl.customer_phone IS NOT NULL
          AND EXISTS (
              SELECT 1
              FROM lead_status ls
              JOIN booked_opportunities bo ON ls.booked_opportunity_id = bo.id
              JOIN customers c ON bo.customer_id = c.id
              WHERE c.phone = bl.customer_phone
          )
    """)
    
    phone_matches = cursor.rowcount
    
    # Match via customer_id (if BadLead already has customer_id)
    cursor.execute("""
        UPDATE bad_leads bl
        SET lead_status_id = (
            SELECT ls.id
            FROM lead_status ls
            JOIN booked_opportunities bo ON ls.booked_opportunity_id = bo.id
            WHERE bo.customer_id = bl.customer_id
              AND bl.customer_id IS NOT NULL
            ORDER BY ls.created_at ASC
            LIMIT 1
        ),
        updated_at = NOW()
        WHERE bl.lead_status_id IS NULL
          AND bl.customer_id IS NOT NULL
          AND EXISTS (
              SELECT 1
              FROM lead_status ls
              JOIN booked_opportunities bo ON ls.booked_opportunity_id = bo.id
              WHERE bo.customer_id = bl.customer_id
          )
    """)
    
    customer_id_matches = cursor.rowcount
    
    total_matches = email_matches + phone_matches + customer_id_matches
    
    if not dry_run:
        conn.commit()
        logger.info(f"Linked BadLead records: {email_matches} via email, {phone_matches} via phone, {customer_id_matches} via customer_id")
    else:
        logger.info(f"[DRY RUN] Would link BadLead records: {email_matches} via email, {phone_matches} via phone, {customer_id_matches} via customer_id")
    
    cursor.close()
    return total_matches


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Link BadLead to LeadStatus')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Run in dry-run mode (default: True)')
    parser.add_argument('--execute', action='store_true',
                       help='Execute the updates (overrides dry-run)')
    
    args = parser.parse_args()
    dry_run = not args.execute
    
    if dry_run:
        logger.info("Running in DRY RUN mode. Use --execute to apply changes.")
    else:
        logger.info("EXECUTING updates to database.")
    
    conn = get_db_connection()
    try:
        logger.info("Linking BadLead to LeadStatus...")
        total_matches = link_badlead_to_leadstatus(conn, dry_run=dry_run)
        
        print("\n" + "="*80)
        print("BADLEAD TO LEADSTATUS LINKAGE SUMMARY")
        print("="*80)
        print(f"Total BadLead records linked: {total_matches}")
        print("="*80 + "\n")
        
        if dry_run:
            logger.info("Dry run complete. Review the output and run with --execute to apply changes.")
        else:
            logger.info("Linkage complete!")
        
        return 0
        
    except Exception as e:
        logger.error(f"Linkage failed: {e}")
        logger.exception(e)
        conn.rollback()
        return 1
    finally:
        conn.close()


if __name__ == '__main__':
    sys.exit(main())

