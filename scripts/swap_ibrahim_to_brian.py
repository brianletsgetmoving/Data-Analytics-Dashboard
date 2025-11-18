#!/usr/bin/env python3
"""
Swap all Ibrahim K references to Brian K across all tables.
This must be done before other operations to ensure data consistency.
"""

import sys
from pathlib import Path
import psycopg2
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.testing.database_connection import get_db_connection
from src.utils.progress_monitor import log_step, log_success, log_error

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def find_ibrahim_k_sales_person(conn):
    """Find Ibrahim K SalesPerson record."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name FROM sales_persons 
        WHERE name ILIKE '%ibrahim%' OR normalized_name ILIKE '%ibrahim%'
    """)
    result = cursor.fetchone()
    cursor.close()
    return result


def find_or_create_brian_k_sales_person(conn):
    """Find or create Brian K SalesPerson record."""
    cursor = conn.cursor()
    
    # Check if Brian K exists
    cursor.execute("""
        SELECT id, name FROM sales_persons 
        WHERE name ILIKE '%brian%' AND (name ILIKE '%brian k%' OR name ILIKE '%brian%k%')
    """)
    result = cursor.fetchone()
    
    if result:
        cursor.close()
        return result[0], result[1]
    
    # Create Brian K if it doesn't exist
    cursor.execute("""
        INSERT INTO sales_persons (id, name, normalized_name, created_at, updated_at)
        VALUES (gen_random_uuid()::text, 'Brian K', 'brian k', NOW(), NOW())
        RETURNING id, name
    """)
    result = cursor.fetchone()
    conn.commit()
    cursor.close()
    return result[0], result[1]


def swap_foreign_keys(conn, ibrahim_id: str, brian_id: str):
    """Swap all foreign key references from Ibrahim K to Brian K."""
    cursor = conn.cursor()
    updates = {}
    
    # Update jobs
    cursor.execute("""
        UPDATE jobs 
        SET sales_person_id = %s 
        WHERE sales_person_id = %s
    """, (brian_id, ibrahim_id))
    updates['jobs'] = cursor.rowcount
    
    # Update booked_opportunities
    cursor.execute("""
        UPDATE booked_opportunities 
        SET sales_person_id = %s 
        WHERE sales_person_id = %s
    """, (brian_id, ibrahim_id))
    updates['booked_opportunities'] = cursor.rowcount
    
    # Update lead_status
    cursor.execute("""
        UPDATE lead_status 
        SET sales_person_id = %s 
        WHERE sales_person_id = %s
    """, (brian_id, ibrahim_id))
    updates['lead_status'] = cursor.rowcount
    
    # Update user_performance
    cursor.execute("""
        UPDATE user_performance 
        SET sales_person_id = %s 
        WHERE sales_person_id = %s
    """, (brian_id, ibrahim_id))
    updates['user_performance'] = cursor.rowcount
    
    # Update sales_performance
    cursor.execute("""
        UPDATE sales_performance 
        SET sales_person_id = %s 
        WHERE sales_person_id = %s
    """, (brian_id, ibrahim_id))
    updates['sales_performance'] = cursor.rowcount
    
    conn.commit()
    cursor.close()
    return updates


def update_name_references(conn, brian_id: str):
    """Update name references in SalesPerformance and UserPerformance."""
    cursor = conn.cursor()
    updates = {}
    
    # Update SalesPerformance names
    cursor.execute("""
        UPDATE sales_performance 
        SET name = 'Brian K'
        WHERE name ILIKE '%ibrahim%'
    """)
    updates['sales_performance_names'] = cursor.rowcount
    
    # Update UserPerformance names
    cursor.execute("""
        UPDATE user_performance 
        SET name = 'Brian K'
        WHERE name ILIKE '%ibrahim%'
    """)
    updates['user_performance_names'] = cursor.rowcount
    
    conn.commit()
    cursor.close()
    return updates


def delete_ibrahim_k_sales_person(conn, ibrahim_id: str):
    """Delete Ibrahim K SalesPerson record after all references are moved."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sales_persons WHERE id = %s", (ibrahim_id,))
    deleted = cursor.rowcount
    conn.commit()
    cursor.close()
    return deleted


def main():
    """Main swap function."""
    logger.info("Starting Ibrahim K to Brian K swap")
    
    conn = get_db_connection()
    
    try:
        # Find Ibrahim K
        log_step("Swap", "Finding Ibrahim K SalesPerson")
        ibrahim_result = find_ibrahim_k_sales_person(conn)
        
        if not ibrahim_result:
            log_success("No Ibrahim K SalesPerson found - nothing to swap")
            return 0
        
        ibrahim_id, ibrahim_name = ibrahim_result
        logger.info(f"Found Ibrahim K: {ibrahim_name} (ID: {ibrahim_id})")
        
        # Find or create Brian K
        log_step("Swap", "Finding or creating Brian K SalesPerson")
        brian_id, brian_name = find_or_create_brian_k_sales_person(conn)
        logger.info(f"Using Brian K: {brian_name} (ID: {brian_id})")
        
        # Swap foreign keys
        log_step("Swap", "Swapping foreign key references")
        updates = swap_foreign_keys(conn, ibrahim_id, brian_id)
        logger.info(f"Updated references: {updates}")
        
        # Update name references
        log_step("Swap", "Updating name references")
        name_updates = update_name_references(conn, brian_id)
        logger.info(f"Updated names: {name_updates}")
        
        # Delete Ibrahim K
        log_step("Swap", "Deleting Ibrahim K SalesPerson")
        deleted = delete_ibrahim_k_sales_person(conn, ibrahim_id)
        logger.info(f"Deleted Ibrahim K SalesPerson: {deleted}")
        
        # Summary
        total_updated = sum(updates.values())
        log_success(f"Ibrahim K → Brian K swap complete: {total_updated} records updated")
        
        return 0
        
    except Exception as e:
        log_error(f"Swap failed: {e}")
        logger.exception(e)
        conn.rollback()
        return 1
    finally:
        conn.close()


if __name__ == '__main__':
    sys.exit(main())

