#!/usr/bin/env python3
"""
Complete linkage between LeadStatus and BookedOpportunities, 
and LostLead and BookedOpportunities via quote_number.

NOTE: This script is now largely replaced by database triggers.
The triggers will automatically link records on insert/update.
This script is kept for backfilling existing NULL relationships.
"""

import sys
from pathlib import Path
import psycopg2
from datetime import datetime
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.utils.database import get_db_connection
from scripts.utils.script_execution import check_and_log_execution

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SCRIPT_NAME = "complete_quote_linkage"


def link_lead_status_to_booked_opportunities(conn, dry_run: bool = True):
    """Link LeadStatus records to BookedOpportunities via quote_number."""
    cursor = conn.cursor()
    
    # Find LeadStatus records without booked_opportunity_id but with matching quote_number
    cursor.execute("""
        UPDATE lead_status ls
        SET booked_opportunity_id = bo.id,
            updated_at = NOW()
        FROM booked_opportunities bo
        WHERE ls.quote_number = bo.quote_number
          AND ls.booked_opportunity_id IS NULL
    """)
    
    updated_count = cursor.rowcount
    
    if not dry_run:
        conn.commit()
        logger.info(f"Linked {updated_count} LeadStatus records to BookedOpportunities")
    else:
        logger.info(f"[DRY RUN] Would link {updated_count} LeadStatus records to BookedOpportunities")
    
    cursor.close()
    return updated_count


def link_lost_leads_to_booked_opportunities(conn, dry_run: bool = True):
    """Link LostLead records to BookedOpportunities via quote_number."""
    cursor = conn.cursor()
    
    # Find LostLead records without booked_opportunity_id but with matching quote_number
    cursor.execute("""
        UPDATE lost_leads ll
        SET booked_opportunity_id = bo.id,
            updated_at = NOW()
        FROM booked_opportunities bo
        WHERE ll.quote_number = bo.quote_number
          AND ll.booked_opportunity_id IS NULL
    """)
    
    updated_count = cursor.rowcount
    
    if not dry_run:
        conn.commit()
        logger.info(f"Linked {updated_count} LostLead records to BookedOpportunities")
    else:
        logger.info(f"[DRY RUN] Would link {updated_count} LostLead records to BookedOpportunities")
    
    cursor.close()
    return updated_count


def main():
    """Main linking function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Complete quote_number linkage')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Run in dry-run mode (default: True)')
    parser.add_argument('--execute', action='store_true',
                       help='Execute the updates (overrides dry-run)')
    parser.add_argument('--force', action='store_true',
                       help='Force execution even if already run')
    
    args = parser.parse_args()
    dry_run = not args.execute
    
    if dry_run:
        logger.info("Running in DRY RUN mode. Use --execute to apply changes.")
    else:
        logger.info("EXECUTING updates to database.")
    
    conn = get_db_connection()
    try:
        # Check if script should run (idempotency check)
        if not dry_run and not check_and_log_execution(conn, SCRIPT_NAME, force=args.force, 
                                                      notes="Backfill existing NULL relationships"):
            return 0
        
        # Check if there's any work to do
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                (SELECT COUNT(*) FROM lead_status WHERE booked_opportunity_id IS NULL AND quote_number IS NOT NULL) as ls_unlinked,
                (SELECT COUNT(*) FROM lost_leads WHERE booked_opportunity_id IS NULL AND quote_number IS NOT NULL) as ll_unlinked
        """)
        result = cursor.fetchone()
        cursor.close()
        
        ls_unlinked = result[0] if result else 0
        ll_unlinked = result[1] if result else 0
        
        if ls_unlinked == 0 and ll_unlinked == 0:
            logger.info("No unlinked records found. All relationships are already established.")
            logger.info("NOTE: Database triggers will automatically link new records going forward.")
            return 0
        
        logger.info(f"Found {ls_unlinked} unlinked LeadStatus records and {ll_unlinked} unlinked LostLead records")
        
        logger.info("Linking LeadStatus to BookedOpportunities...")
        ls_count = link_lead_status_to_booked_opportunities(conn, dry_run=dry_run)
        
        logger.info("Linking LostLead to BookedOpportunities...")
        ll_count = link_lost_leads_to_booked_opportunities(conn, dry_run=dry_run)
        
        print("\n" + "="*80)
        print("QUOTE NUMBER LINKAGE SUMMARY")
        print("="*80)
        print(f"LeadStatus records linked: {ls_count}")
        print(f"LostLead records linked: {ll_count}")
        print(f"Total records linked: {ls_count + ll_count}")
        print("="*80 + "\n")
        
        if not dry_run:
            logger.info("NOTE: Database triggers will automatically link new records going forward.")
        
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

