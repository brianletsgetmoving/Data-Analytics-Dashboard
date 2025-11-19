#!/usr/bin/env python3
"""Quick script to check migration status."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import psycopg2
from scripts.utils.database import get_db_connection

def check_status():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Check table existence
        cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'leads')")
        leads_exists = cur.fetchone()[0]
        print(f"✓ leads table exists: {leads_exists}")
        
        cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'bad_leads')")
        bad_leads_exists = cur.fetchone()[0]
        print(f"✓ bad_leads table exists: {bad_leads_exists}")
        
        cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'lost_leads')")
        lost_leads_exists = cur.fetchone()[0]
        print(f"✓ lost_leads table exists: {lost_leads_exists}")
        
        if leads_exists:
            cur.execute("SELECT COUNT(*) FROM leads")
            total = cur.fetchone()[0]
            print(f"\n📊 leads table: {total:,} total records")
            
            cur.execute("SELECT COUNT(*) FROM leads WHERE lead_type = 'BAD'")
            bad = cur.fetchone()[0]
            print(f"   - BAD: {bad:,}")
            
            cur.execute("SELECT COUNT(*) FROM leads WHERE lead_type = 'LOST'")
            lost = cur.fetchone()[0]
            print(f"   - LOST: {lost:,}")
            
            cur.execute("SELECT COUNT(*) FROM leads WHERE lead_type IS NULL OR lead_type = 'STANDARD'")
            standard = cur.fetchone()[0]
            print(f"   - STANDARD/NULL: {standard:,}")
            
            cur.execute("SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'leads' AND column_name = 'customer_id')")
            has_customer_id = cur.fetchone()[0]
            print(f"\n✓ customer_id column exists: {has_customer_id}")
        
        if bad_leads_exists:
            cur.execute("SELECT COUNT(*) FROM bad_leads")
            bad_count = cur.fetchone()[0]
            print(f"\n📊 bad_leads table: {bad_count:,} records remaining")
            
            cur.execute("SELECT COUNT(*) FROM bad_leads WHERE lead_status_id IS NOT NULL")
            linked = cur.fetchone()[0]
            print(f"   - Linked to leads: {linked:,}")
            
            cur.execute("SELECT COUNT(*) FROM bad_leads WHERE lead_status_id IS NULL")
            unlinked = cur.fetchone()[0]
            print(f"   - Not linked: {unlinked:,}")
        
        if lost_leads_exists:
            cur.execute("SELECT COUNT(*) FROM lost_leads")
            lost_count = cur.fetchone()[0]
            print(f"\n📊 lost_leads table: {lost_count:,} records remaining")
        
        # Check execution log
        cur.execute("SELECT executed_at FROM script_execution_log WHERE script_name = 'rename_and_merge_leads' ORDER BY executed_at DESC LIMIT 1")
        row = cur.fetchone()
        if row:
            print(f"\n⏰ Last execution logged: {row[0]}")
        else:
            print("\n⏰ No execution logged")
            
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    check_status()

