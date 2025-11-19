#!/usr/bin/env python3
"""
Complete linkage between LeadStatus and BookedOpportunities, 
and LostLead and BookedOpportunities via quote_number.
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
    
    args = parser.parse_args()
    dry_run = not args.execute
    
    if dry_run:
        logger.info("Running in DRY RUN mode. Use --execute to apply changes.")
    else:
        logger.info("EXECUTING updates to database.")
    
    conn = get_db_connection()
    try:
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

