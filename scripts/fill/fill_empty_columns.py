#!/usr/bin/env python3
"""
Fill empty columns across all modules using raw data sources.
"""

import sys
from pathlib import Path
import psycopg2
import logging
from typing import Dict
import re

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.utils.database import get_db_connection
from scripts.utils.script_execution import check_and_log_execution

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SCRIPT_NAME = "fill_empty_columns"


def parse_name_to_first_last(name: str) -> tuple:
    """Parse name into first_name and last_name."""
    if not name or name.strip() == '':
        return (None, None)
    
    parts = name.strip().split()
    if len(parts) == 0:
        return (None, None)
    elif len(parts) == 1:
        return (parts[0], None)
    else:
        return (parts[0], ' '.join(parts[1:]))


def fill_customer_names(conn, dry_run: bool = True) -> int:
    """Fill first_name and last_name in customers from name field."""
    cursor = conn.cursor()
    updated = 0
    
    try:
        # Get customers with name but missing first_name or last_name
        cursor.execute("""
            SELECT id, name, first_name, last_name
            FROM customers
            WHERE name IS NOT NULL
            AND (first_name IS NULL OR last_name IS NULL)
        """)
        
        customers = cursor.fetchall()
        logger.info(f"Found {len(customers)} customers with missing first_name or last_name")
        
        if dry_run:
            logger.info("[DRY RUN] Would fill customer names")
            return len(customers)
        
        for customer_id, name, current_first, current_last in customers:
            first_name, last_name = parse_name_to_first_last(name)
            
            # Only update if we have new values
            new_first = first_name if not current_first else current_first
            new_last = last_name if not current_last else current_last
            
            if new_first != current_first or new_last != current_last:
                cursor.execute("""
                    UPDATE customers
                    SET first_name = %s, last_name = %s, updated_at = NOW()
                    WHERE id = %s
                """, (new_first, new_last, customer_id))
                updated += 1
        
        conn.commit()
        logger.info(f"Updated {updated} customer names")
        return updated
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error filling customer names: {e}")
        raise
    finally:
        cursor.close()


def fill_customer_addresses_from_jobs(conn, dry_run: bool = True) -> int:
    """Fill customer origin/destination addresses from Job data."""
    cursor = conn.cursor()
    updated = 0
    
    try:
        # Update origin addresses
        cursor.execute("""
            UPDATE customers c
            SET 
                origin_city = COALESCE(c.origin_city, j.origin_city),
                origin_state = COALESCE(c.origin_state, j.origin_state),
                origin_zip = COALESCE(c.origin_zip, j.origin_zip),
                origin_address = COALESCE(c.origin_address, j.origin_address),
                updated_at = NOW()
            FROM (
                SELECT DISTINCT ON (customer_id)
                    customer_id, origin_city, origin_state, origin_zip, origin_address
                FROM jobs
                WHERE customer_id IS NOT NULL
                AND (origin_city IS NOT NULL OR origin_state IS NOT NULL)
                ORDER BY customer_id, job_date DESC NULLS LAST
            ) j
            WHERE c.id = j.customer_id
            AND (c.origin_city IS NULL OR c.origin_state IS NULL)
        """)
        origin_updated = cursor.rowcount
        
        # Update destination addresses
        cursor.execute("""
            UPDATE customers c
            SET 
                destination_city = COALESCE(c.destination_city, j.destination_city),
                destination_state = COALESCE(c.destination_state, j.destination_state),
                destination_zip = COALESCE(c.destination_zip, j.destination_zip),
                destination_address = COALESCE(c.destination_address, j.destination_address),
                updated_at = NOW()
            FROM (
                SELECT DISTINCT ON (customer_id)
                    customer_id, destination_city, destination_state, destination_zip, destination_address
                FROM jobs
                WHERE customer_id IS NOT NULL
                AND (destination_city IS NOT NULL OR destination_state IS NOT NULL)
                ORDER BY customer_id, job_date DESC NULLS LAST
            ) j
            WHERE c.id = j.customer_id
            AND (c.destination_city IS NULL OR c.destination_state IS NULL)
        """)
        dest_updated = cursor.rowcount
        
        if dry_run:
            logger.info(f"[DRY RUN] Would update {origin_updated + dest_updated} customer addresses")
            return origin_updated + dest_updated
        
        conn.commit()
        updated = origin_updated + dest_updated
        logger.info(f"Updated {updated} customer addresses from jobs")
        return updated
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error filling customer addresses: {e}")
        raise
    finally:
        cursor.close()


def fill_customer_timeline_dates(conn, dry_run: bool = True) -> int:
    """Fill first_lead_date and conversion_date for customers."""
    cursor = conn.cursor()
    updated = 0
    
    try:
        # Check if leads table exists and has customer_id column
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'leads'
            )
        """)
        leads_exists = cursor.fetchone()[0]
        
        if leads_exists:
            # Check if customer_id column exists in leads
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name = 'leads' 
                    AND column_name = 'customer_id'
                )
            """)
            has_customer_id = cursor.fetchone()[0]
            
            if has_customer_id:
                cursor.execute("""
                    UPDATE customers c
                    SET 
                        first_lead_date = subq.earliest_lead_date,
                        updated_at = NOW()
                    FROM (
                        SELECT 
                            customer_id,
                            MIN(created_at) as earliest_lead_date
                        FROM leads
                        WHERE customer_id IS NOT NULL
                        GROUP BY customer_id
                    ) subq
                    WHERE c.id = subq.customer_id
                    AND c.first_lead_date IS NULL
                """)
                first_lead_updated = cursor.rowcount
            else:
                logger.info("leads table doesn't have customer_id column yet, skipping first_lead_date fill")
                first_lead_updated = 0
        else:
            logger.info("leads table does not exist yet, skipping first_lead_date fill (will be done after merge)")
            first_lead_updated = 0
        
        # Fill conversion_date from earliest booked opportunity or job
        cursor.execute("""
            UPDATE customers c
            SET 
                conversion_date = subq.earliest_conversion,
                updated_at = NOW()
            FROM (
                SELECT 
                    customer_id,
                    MIN(earliest) as earliest_conversion
                FROM (
                    SELECT customer_id, booked_date as earliest
                    FROM booked_opportunities
                    WHERE customer_id IS NOT NULL AND booked_date IS NOT NULL
                    UNION ALL
                    SELECT customer_id, job_date as earliest
                    FROM jobs
                    WHERE customer_id IS NOT NULL AND job_date IS NOT NULL
                ) combined
                GROUP BY customer_id
            ) subq
            WHERE c.id = subq.customer_id
            AND c.conversion_date IS NULL
        """)
        conversion_updated = cursor.rowcount
        
        if dry_run:
            logger.info(f"[DRY RUN] Would update {first_lead_updated + conversion_updated} customer timeline dates")
            return first_lead_updated + conversion_updated
        
        conn.commit()
        updated = first_lead_updated + conversion_updated
        logger.info(f"Updated {updated} customer timeline dates")
        return updated
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error filling customer timeline: {e}")
        raise
    finally:
        cursor.close()


def fill_job_customer_links(conn, dry_run: bool = True) -> int:
    """Fill customer_id in jobs by matching customer_name, email, phone."""
    cursor = conn.cursor()
    updated = 0
    
    try:
        # Match by email
        cursor.execute("""
            UPDATE jobs j
            SET customer_id = c.id, updated_at = NOW()
            FROM customers c
            WHERE j.customer_id IS NULL
            AND j.customer_email IS NOT NULL
            AND c.email = j.customer_email
        """)
        email_matched = cursor.rowcount
        
        # Match by phone
        cursor.execute("""
            UPDATE jobs j
            SET customer_id = c.id, updated_at = NOW()
            FROM customers c
            WHERE j.customer_id IS NULL
            AND j.customer_phone IS NOT NULL
            AND c.phone = j.customer_phone
        """)
        phone_matched = cursor.rowcount
        
        if dry_run:
            logger.info(f"[DRY RUN] Would match {email_matched + phone_matched} jobs to customers")
            return email_matched + phone_matched
        
        conn.commit()
        updated = email_matched + phone_matched
        logger.info(f"Matched {updated} jobs to customers (email: {email_matched}, phone: {phone_matched})")
        return updated
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error filling job customer links: {e}")
        raise
    finally:
        cursor.close()


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fill empty columns from raw data')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (no changes)')
    
    args = parser.parse_args()
    dry_run = args.dry_run
    
    # Check if script has already been executed
    if not dry_run:
        conn = get_db_connection()
        try:
            if check_and_log_execution(conn, SCRIPT_NAME):
                logger.info(f"Script '{SCRIPT_NAME}' has already been executed. Use --force to re-run.")
                return
        finally:
            conn.close()
    
    conn = get_db_connection()
    
    try:
        logger.info("="*80)
        logger.info("FILL EMPTY COLUMNS")
        logger.info("="*80)
        
        if dry_run:
            logger.info("DRY RUN MODE - No changes will be made")
        
        # Fill customer names
        logger.info("\nFilling customer names...")
        names_filled = fill_customer_names(conn, dry_run)
        
        # Fill customer addresses
        logger.info("\nFilling customer addresses from jobs...")
        addresses_filled = fill_customer_addresses_from_jobs(conn, dry_run)
        
        # Fill customer timeline dates
        logger.info("\nFilling customer timeline dates...")
        timeline_filled = fill_customer_timeline_dates(conn, dry_run)
        
        # Fill job customer links
        logger.info("\nFilling job customer links...")
        job_links_filled = fill_job_customer_links(conn, dry_run)
        
        logger.info("\n" + "="*80)
        logger.info("SUMMARY")
        logger.info("="*80)
        logger.info(f"Customer names filled: {names_filled}")
        logger.info(f"Customer addresses filled: {addresses_filled}")
        logger.info(f"Customer timeline dates filled: {timeline_filled}")
        logger.info(f"Job customer links filled: {job_links_filled}")
        logger.info("="*80)
        
        if not dry_run:
            check_and_log_execution(conn, SCRIPT_NAME, log_execution=True)
    
    finally:
        conn.close()


if __name__ == '__main__':
    main()

