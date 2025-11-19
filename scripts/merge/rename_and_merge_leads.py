#!/usr/bin/env python3
"""
Rename LeadStatus to Lead and merge BadLead and LostLead into unified Lead model.
Preserves all records as unique based on quote_number.
"""

import sys
from pathlib import Path
import psycopg2
import logging
import time
from typing import Dict, List
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.utils.database import get_db_connection
from scripts.utils.script_execution import check_and_log_execution

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SCRIPT_NAME = "rename_and_merge_leads"


def rename_leadstatus_to_leads(conn, dry_run: bool = True) -> int:
    """Rename LeadStatus table to leads."""
    cursor = conn.cursor()
    
    try:
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'lead_status'
            )
        """)
        exists = cursor.fetchone()[0]
        
        if not exists:
            logger.info("Table 'lead_status' does not exist, skipping rename")
            return 0
        
        # Check if leads table already exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'leads'
            )
        """)
        leads_exists = cursor.fetchone()[0]
        
        if leads_exists:
            logger.warning("Table 'leads' already exists, skipping rename")
            return 0
        
        if dry_run:
            logger.info("[DRY RUN] Would rename table 'lead_status' to 'leads'")
            return 1
        
        # Rename the table
        cursor.execute('ALTER TABLE lead_status RENAME TO leads')
        conn.commit()
        
        logger.info("Successfully renamed table 'lead_status' to 'leads'")
        return 1
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error renaming table: {e}")
        raise
    finally:
        cursor.close()


def create_lead_type_enum(conn, dry_run: bool = True) -> bool:
    """Create lead_type enum if it doesn't exist."""
    cursor = conn.cursor()
    
    try:
        # Check if enum exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM pg_type 
                WHERE typname = 'lead_type'
            )
        """)
        exists = cursor.fetchone()[0]
        
        if exists:
            logger.info("Enum 'lead_type' already exists")
            return True
        
        if dry_run:
            logger.info("[DRY RUN] Would create enum 'lead_type'")
            return True
        
        # Create enum
        cursor.execute("""
            CREATE TYPE lead_type AS ENUM ('BAD', 'LOST', 'STANDARD')
        """)
        conn.commit()
        
        logger.info("Successfully created enum 'lead_type'")
        return True
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating enum: {e}")
        raise
    finally:
        cursor.close()


def add_lead_type_column(conn, dry_run: bool = True) -> bool:
    """Add lead_type column to leads table."""
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'leads' 
                AND column_name = 'lead_type'
            )
        """)
        exists = cursor.fetchone()[0]
        
        if exists:
            logger.info("Column 'lead_type' already exists in 'leads' table")
            return True
        
        if dry_run:
            logger.info("[DRY RUN] Would add column 'lead_type' to 'leads' table")
            return True
        
        # Add column with default 'STANDARD' for existing records
        cursor.execute("""
            ALTER TABLE leads 
            ADD COLUMN lead_type lead_type DEFAULT 'STANDARD'
        """)
        conn.commit()
        
        logger.info("Successfully added 'lead_type' column to 'leads' table")
        return True
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error adding column: {e}")
        raise
    finally:
        cursor.close()


def add_missing_columns_to_leads(conn, dry_run: bool = True) -> int:
    """Add columns from BadLead and LostLead that don't exist in leads."""
    cursor = conn.cursor()
    columns_added = 0
    
    # Columns to add from BadLead
    badlead_columns = [
        ('provider', 'text'),
        ('customer_name', 'text'),
        ('customer_email', 'text'),
        ('customer_phone', 'text'),
        ('move_date', 'date'),
        ('date_lead_received', 'date'),
        ('lead_bad_reason', 'text')
    ]
    
    # Columns to add from LostLead (some may already exist)
    lostlead_columns = [
        ('name', 'text'),  # May conflict with existing name field
        ('lost_date', 'date'),
        ('reason', 'text'),
        ('date_received', 'timestamp'),
        ('time_to_first_contact', 'text')
    ]
    
    all_columns = badlead_columns + lostlead_columns
    
    try:
        for column_name, column_type in all_columns:
            # Check if column exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name = 'leads' 
                    AND column_name = %s
                )
            """, (column_name,))
            exists = cursor.fetchone()[0]
            
            if exists:
                logger.debug(f"Column '{column_name}' already exists in 'leads' table")
                continue
            
            if dry_run:
                logger.info(f"[DRY RUN] Would add column '{column_name}' ({column_type}) to 'leads' table")
                columns_added += 1
            else:
                cursor.execute(f"""
                    ALTER TABLE leads 
                    ADD COLUMN {column_name} {column_type}
                """)
                columns_added += 1
                logger.info(f"Added column '{column_name}' to 'leads' table")
        
        if not dry_run and columns_added > 0:
            conn.commit()
        
        return columns_added
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error adding columns: {e}")
        raise
    finally:
        cursor.close()


def migrate_badleads_to_leads(conn, dry_run: bool = True, batch_size: int = 10000) -> int:
    """Migrate BadLead records to leads table, preserving all quote_numbers."""
    cursor = conn.cursor()
    
    try:
        # Check if bad_leads table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'bad_leads'
            )
        """)
        exists = cursor.fetchone()[0]
        
        if not exists:
            logger.info("Table 'bad_leads' does not exist, skipping migration")
            return 0
        
        # Get count of bad_leads
        cursor.execute("SELECT COUNT(*) FROM bad_leads")
        total_badleads = cursor.fetchone()[0]
        
        if total_badleads == 0:
            logger.info("No BadLead records to migrate")
            return 0
        
        logger.info(f"Found {total_badleads:,} BadLead records to migrate")
        
        if dry_run:
            logger.info("[DRY RUN] Would migrate BadLead records to leads table")
            return total_badleads
        
        # Ensure customer_id column exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'leads' 
                AND column_name = 'customer_id'
            )
        """)
        has_customer_id = cursor.fetchone()[0]
        
        if not has_customer_id:
            logger.info("Adding customer_id column to leads table...")
            # Check what type customer_id should be (match customers.id type)
            cursor.execute("""
                SELECT data_type FROM information_schema.columns 
                WHERE table_name = 'customers' AND column_name = 'id'
            """)
            customer_id_type = cursor.fetchone()[0]
            logger.info(f"  customers.id type: {customer_id_type}")
            
            # Add column without foreign key first, then we'll add the constraint after migration
            cursor.execute(f"""
                ALTER TABLE leads 
                ADD COLUMN customer_id {customer_id_type}
            """)
            conn.commit()
            logger.info("✓ Added customer_id column (foreign key will be added after migration)")
        
        start_time = time.time()
        
        # Migrate BadLead records
        # First, we need to generate quote_numbers for BadLeads that don't have them
        # Since BadLead doesn't have quote_number, we'll need to create unique identifiers
        # But wait - BadLead has lead_status_id which links to LeadStatus (now leads)
        # So we should merge BadLead data INTO existing lead records where possible
        
        # Strategy:
        # 1. For BadLeads with lead_status_id, update the existing lead record
        # 2. For BadLeads without lead_status_id, create new lead records
        
        # Step 1: Update existing leads that have matching bad_leads
        logger.info("Step 1: Updating existing leads with BadLead data...")
        cursor.execute("""
            SELECT COUNT(*) FROM bad_leads WHERE lead_status_id IS NOT NULL
        """)
        linked_count = cursor.fetchone()[0]
        logger.info(f"  Found {linked_count:,} BadLeads linked to existing leads")
        
        if linked_count > 0:
            cursor.execute("""
                UPDATE leads l
                SET 
                    lead_type = 'BAD',
                    provider = COALESCE(l.provider, bl.provider),
                    customer_name = COALESCE(l.customer_name, bl.customer_name),
                    customer_email = COALESCE(l.customer_email, bl.customer_email),
                    customer_phone = COALESCE(l.customer_phone, bl.customer_phone),
                    move_date = COALESCE(l.move_date, bl.move_date),
                    date_lead_received = COALESCE(l.date_lead_received, bl.date_lead_received),
                    lead_bad_reason = COALESCE(l.lead_bad_reason, bl.lead_bad_reason),
                    customer_id = COALESCE(l.customer_id, bl.customer_id),
                    lead_source_id = COALESCE(l.lead_source_id, bl.lead_source_id),
                    updated_at = NOW()
                FROM bad_leads bl
                WHERE l.id = bl.lead_status_id
            """)
            updated_count = cursor.rowcount
            conn.commit()
            logger.info(f"  ✓ Updated {updated_count:,} existing lead records")
        else:
            updated_count = 0
        
        # Step 2: Insert new lead records for BadLeads without lead_status_id (BATCH PROCESSING)
        logger.info("Step 2: Inserting new lead records from BadLeads (batch processing)...")
        cursor.execute("""
            SELECT COUNT(*) FROM bad_leads WHERE lead_status_id IS NULL
        """)
        unlinked_count = cursor.fetchone()[0]
        logger.info(f"  Found {unlinked_count:,} BadLeads to insert as new leads")
        
        if unlinked_count == 0:
            logger.info("  No unlinked BadLeads to insert")
            return updated_count
        
        # Process in batches
        inserted_count = 0
        batch_num = 0
        total_batches = (unlinked_count + batch_size - 1) // batch_size
        
        while True:
            batch_start = time.time()
            cursor.execute("""
                INSERT INTO leads (
                    id, quote_number, lead_type,
                    provider, customer_name, customer_email, customer_phone,
                    move_date, date_lead_received, lead_bad_reason,
                    customer_id, lead_source_id,
                    created_at, updated_at
                )
                SELECT 
                    bl.id,
                    'BAD-' || REPLACE(bl.id::text, '-', '') as quote_number,
                    'BAD'::lead_type,
                    bl.provider,
                    bl.customer_name,
                    bl.customer_email,
                    bl.customer_phone,
                    bl.move_date,
                    bl.date_lead_received,
                    bl.lead_bad_reason,
                    bl.customer_id,
                    bl.lead_source_id,
                    bl.created_at,
                    NOW()
                FROM bad_leads bl
                WHERE bl.lead_status_id IS NULL
                AND NOT EXISTS (
                    SELECT 1 FROM leads l WHERE l.quote_number = 'BAD-' || REPLACE(bl.id::text, '-', '')
                )
                AND NOT EXISTS (
                    SELECT 1 FROM leads l WHERE l.id = bl.id
                )
                LIMIT %s
            """, (batch_size,))
            
            batch_inserted = cursor.rowcount
            inserted_count += batch_inserted
            conn.commit()
            
            batch_num += 1
            batch_time = time.time() - batch_start
            elapsed = time.time() - start_time
            rate = inserted_count / elapsed if elapsed > 0 else 0
            
            logger.info(f"  Batch {batch_num}/{total_batches}: Inserted {batch_inserted:,} records "
                       f"(Total: {inserted_count:,}/{unlinked_count:,}, "
                       f"Rate: {rate:.0f} records/sec, "
                       f"Elapsed: {elapsed:.1f}s)")
            
            if batch_inserted == 0:
                break
        
        total_time = time.time() - start_time
        logger.info(f"✓ Completed BadLead migration: {inserted_count:,} records inserted in {total_time:.1f}s")
        return updated_count + inserted_count
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error migrating BadLeads: {e}")
        raise
    finally:
        cursor.close()


def migrate_lostleads_to_leads(conn, dry_run: bool = True, batch_size: int = 10000) -> int:
    """Migrate LostLead records to leads table, preserving all quote_numbers."""
    cursor = conn.cursor()
    
    try:
        # Check if lost_leads table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'lost_leads'
            )
        """)
        exists = cursor.fetchone()[0]
        
        if not exists:
            logger.info("Table 'lost_leads' does not exist, skipping migration")
            return 0
        
        # Get count of lost_leads
        cursor.execute("SELECT COUNT(*) FROM lost_leads")
        total_lostleads = cursor.fetchone()[0]
        
        if total_lostleads == 0:
            logger.info("No LostLead records to migrate")
            return 0
        
        logger.info(f"Found {total_lostleads:,} LostLead records to migrate")
        
        if dry_run:
            logger.info("[DRY RUN] Would migrate LostLead records to leads table")
            return total_lostleads
        
        start_time = time.time()
        
        # Migrate LostLead records
        # Strategy: Use quote_number to match or insert
        # If quote_number exists in leads, update it
        # If quote_number doesn't exist, insert new record
        
        # Step 1: Update existing leads that have matching quote_numbers
        cursor.execute("""
            UPDATE leads l
            SET 
                lead_type = CASE 
                    WHEN l.lead_type = 'BAD'::lead_type THEN 'BAD'::lead_type  -- Keep BAD if already set
                    ELSE 'LOST'::lead_type
                END,
                name = COALESCE(l.name, ll.name),
                lost_date = COALESCE(l.lost_date, ll.lost_date),
                move_date = COALESCE(l.move_date, ll.move_date),
                reason = COALESCE(l.reason, ll.reason),
                date_received = COALESCE(l.date_received, ll.date_received),
                time_to_first_contact = COALESCE(l.time_to_first_contact, ll.time_to_first_contact),
                booked_opportunity_id = COALESCE(l.booked_opportunity_id, ll.booked_opportunity_id),
                lead_source_id = COALESCE(l.lead_source_id, ll.lead_source_id),
                updated_at = NOW()
            FROM lost_leads ll
            WHERE l.quote_number = ll.quote_number
        """)
        updated_count = cursor.rowcount
        logger.info(f"Updated {updated_count} existing lead records with LostLead data")
        
        # Step 2: Insert new lead records for LostLeads with quote_numbers not in leads (BATCH PROCESSING)
        logger.info("Inserting LostLead records (batch processing)...")
        
        inserted_count = 0
        batch_num = 0
        total_batches = (total_lostleads + batch_size - 1) // batch_size
        
        while True:
            batch_start = time.time()
            cursor.execute("""
                INSERT INTO leads (
                    id, quote_number, lead_type,
                    name, lost_date, move_date, reason,
                    date_received, time_to_first_contact,
                    booked_opportunity_id, lead_source_id,
                    created_at, updated_at
                )
                SELECT 
                    ll.id,
                    ll.quote_number,
                    'LOST'::lead_type,
                    ll.name,
                    ll.lost_date,
                    ll.move_date,
                    ll.reason,
                    ll.date_received,
                    ll.time_to_first_contact,
                    ll.booked_opportunity_id,
                    ll.lead_source_id,
                    ll.created_at,
                    NOW()
                FROM lost_leads ll
                WHERE NOT EXISTS (
                    SELECT 1 FROM leads l WHERE l.quote_number = ll.quote_number
                )
                AND NOT EXISTS (
                    SELECT 1 FROM leads l WHERE l.id = ll.id
                )
                LIMIT %s
            """, (batch_size,))
            
            batch_inserted = cursor.rowcount
            inserted_count += batch_inserted
            conn.commit()
            
            batch_num += 1
            batch_time = time.time() - batch_start
            elapsed = time.time() - start_time
            rate = inserted_count / elapsed if elapsed > 0 else 0
            
            logger.info(f"  Batch {batch_num}/{total_batches}: Inserted {batch_inserted:,} records "
                       f"(Total: {inserted_count:,}/{total_lostleads:,}, "
                       f"Rate: {rate:.0f} records/sec, "
                       f"Elapsed: {elapsed:.1f}s)")
            
            if batch_inserted == 0:
                break
        
        total_time = time.time() - start_time
        logger.info(f"✓ Completed LostLead migration: {inserted_count:,} records inserted in {total_time:.1f}s")
        return updated_count + inserted_count
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error migrating LostLeads: {e}")
        raise
    finally:
        cursor.close()


def update_foreign_key_references(conn, dry_run: bool = True) -> int:
    """Update foreign key references from bad_leads.lead_status_id to point to leads."""
    cursor = conn.cursor()
    updates = 0
    
    try:
        # Check if bad_leads table still exists and has lead_status_id
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'bad_leads' 
                AND column_name = 'lead_status_id'
            )
        """)
        has_column = cursor.fetchone()[0] if cursor.rowcount > 0 else False
        
        if not has_column:
            logger.info("bad_leads.lead_status_id column doesn't exist or table is gone")
            return 0
        
        # The foreign key should already point to the renamed table
        # But we need to update the constraint name if it references lead_status
        # Actually, PostgreSQL should handle this automatically when we rename the table
        # So this might not be needed, but let's check
        
        logger.info("Foreign key references should be automatically updated by table rename")
        return 0
    
    except Exception as e:
        logger.warning(f"Error updating foreign keys: {e}")
        return 0
    finally:
        cursor.close()


def drop_old_tables(conn, dry_run: bool = True) -> int:
    """Drop BadLead and LostLead tables after migration."""
    cursor = conn.cursor()
    dropped = 0
    
    try:
        tables_to_drop = ['bad_leads', 'lost_leads']
        
        for table_name in tables_to_drop:
            cursor.execute(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = '{table_name}'
                )
            """)
            exists = cursor.fetchone()[0]
            
            if not exists:
                logger.info(f"Table '{table_name}' does not exist, skipping")
                continue
            
            if dry_run:
                logger.info(f"[DRY RUN] Would drop table '{table_name}'")
                dropped += 1
            else:
                cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
                dropped += 1
                logger.info(f"Dropped table '{table_name}'")
        
        if not dry_run and dropped > 0:
            conn.commit()
        
        return dropped
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error dropping tables: {e}")
        raise
    finally:
        cursor.close()


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Rename LeadStatus to Lead and merge BadLead/LostLead')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (no changes)')
    parser.add_argument('--force', action='store_true', help='Force execution even if already run')
    
    args = parser.parse_args()
    dry_run = args.dry_run
    
    # Check if script has already been executed
    if not dry_run:
        conn = get_db_connection()
        try:
            if not check_and_log_execution(conn, SCRIPT_NAME, force=args.force):
                logger.info(f"Script '{SCRIPT_NAME}' has already been executed. Use --force to re-run.")
                return
        finally:
            conn.close()
    
    conn = get_db_connection()
    
    try:
        logger.info("="*80)
        logger.info("RENAME AND MERGE LEADS")
        logger.info("="*80)
        
        if dry_run:
            logger.info("DRY RUN MODE - No changes will be made")
        
        # Step 1: Rename LeadStatus to leads
        logger.info("\nStep 1: Renaming LeadStatus to leads...")
        rename_leadstatus_to_leads(conn, dry_run)
        
        # Step 2: Create lead_type enum
        logger.info("\nStep 2: Creating lead_type enum...")
        create_lead_type_enum(conn, dry_run)
        
        # Step 3: Add lead_type column
        logger.info("\nStep 3: Adding lead_type column...")
        add_lead_type_column(conn, dry_run)
        
        # Step 4: Add missing columns from BadLead/LostLead
        logger.info("\nStep 4: Adding missing columns to leads table...")
        add_missing_columns_to_leads(conn, dry_run)
        
        # Step 5: Migrate BadLead records
        logger.info("\nStep 5: Migrating BadLead records...")
        badlead_count = migrate_badleads_to_leads(conn, dry_run, batch_size=10000)
        
        # Step 6: Migrate LostLead records
        logger.info("")
        logger.info("Step 6: Migrating LostLead records...")
        lostlead_count = migrate_lostleads_to_leads(conn, dry_run, batch_size=10000)
        
        # Step 7: Add foreign key constraint for customer_id if it doesn't exist
        if not dry_run:
            logger.info("")
            logger.info("Step 7: Adding foreign key constraint for customer_id...")
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.table_constraints 
                        WHERE table_name = 'leads' 
                        AND constraint_name = 'leads_customer_id_fkey'
                    )
                """)
                fk_exists = cursor.fetchone()[0]
                
                if not fk_exists:
                    cursor.execute("""
                        ALTER TABLE leads 
                        ADD CONSTRAINT leads_customer_id_fkey 
                        FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL
                    """)
                    conn.commit()
                    logger.info("✓ Added foreign key constraint for customer_id")
                else:
                    logger.info("Foreign key constraint already exists")
            except Exception as e:
                logger.warning(f"Could not add foreign key constraint: {e}")
                conn.rollback()
            finally:
                cursor.close()
        
        # Step 7: Update foreign key references
        logger.info("\nStep 7: Updating foreign key references...")
        update_foreign_key_references(conn, dry_run)
        
        # Step 8: Drop old tables (only if not dry run)
        if not dry_run:
            logger.info("\nStep 8: Dropping old tables...")
            drop_old_tables(conn, dry_run)
        
        logger.info("\n" + "="*80)
        logger.info("SUMMARY")
        logger.info("="*80)
        logger.info(f"BadLead records migrated: {badlead_count}")
        logger.info(f"LostLead records migrated: {lostlead_count}")
        logger.info("="*80)
        
        if not dry_run:
            check_and_log_execution(conn, SCRIPT_NAME, force=args.force, log_execution=True)
    
    finally:
        conn.close()


if __name__ == '__main__':
    main()

