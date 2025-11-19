#!/usr/bin/env python3
"""
Create branches lookup table and populate it from existing branch_name values.
Then link Jobs, BookedOpportunities, and LeadStatus records to the lookup table.
"""

import sys
from pathlib import Path
import psycopg2
from datetime import datetime
import logging
import re

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.testing.database_connection import get_db_connection

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def normalize_branch_name(name: str) -> str:
    """Normalize a branch name for matching."""
    if not name:
        return ""
    
    # Convert to lowercase and strip
    normalized = name.lower().strip()
    
    # Remove extra whitespace
    normalized = re.sub(r'\s+', ' ', normalized)
    
    # Remove special characters except spaces and hyphens
    normalized = re.sub(r'[^\w\s-]', '', normalized)
    
    return normalized.strip()


def extract_city_from_branch_name(name: str) -> tuple[str, str]:
    """
    Extract city and state from branch name.
    
    Examples:
    - "NORTH YORK TORONTO" -> ("Toronto", "ON")
    - "MISSISSAUGA" -> ("Mississauga", None)
    """
    if not name:
        return (None, None)
    
    # Common patterns
    name_upper = name.upper()
    
    # Try to extract city name (usually the last significant word)
    words = name.split()
    if words:
        city = words[-1].title()
    else:
        city = None
    
    # State/province detection (simplified - would need more logic for real implementation)
    state = None
    if "ON" in name_upper or "ONTARIO" in name_upper:
        state = "ON"
    elif "BC" in name_upper or "BRITISH COLUMBIA" in name_upper:
        state = "BC"
    elif "AB" in name_upper or "ALBERTA" in name_upper:
        state = "AB"
    elif "QC" in name_upper or "QUEBEC" in name_upper:
        state = "QC"
    
    return (city, state)


def get_unique_branch_names(conn):
    """Get all unique branch_name values from all tables."""
    cursor = conn.cursor()
    
    branches = set()
    
    # From Jobs
    cursor.execute("SELECT DISTINCT branch_name FROM jobs WHERE branch_name IS NOT NULL")
    branches.update(row[0] for row in cursor.fetchall())
    
    # From BookedOpportunities
    cursor.execute("SELECT DISTINCT branch_name FROM booked_opportunities WHERE branch_name IS NOT NULL")
    branches.update(row[0] for row in cursor.fetchall())
    
    # From LeadStatus
    cursor.execute("SELECT DISTINCT branch_name FROM lead_status WHERE branch_name IS NOT NULL")
    branches.update(row[0] for row in cursor.fetchall())
    
    cursor.close()
    return sorted(branches)


def create_branches(conn, dry_run: bool = True):
    """Create branches lookup table entries."""
    cursor = conn.cursor()
    
    # Get all unique branch names
    branch_names = get_unique_branch_names(conn)
    logger.info(f"Found {len(branch_names)} unique branch names")
    
    created_count = 0
    branch_map = {}  # original_name -> branch_id
    
    total = len(branch_names)
    for idx, branch_name in enumerate(branch_names, 1):
        if idx % 10 == 0:
            logger.info(f"Processing branch {idx}/{total}...")
        normalized_name = normalize_branch_name(branch_name)
        city, state = extract_city_from_branch_name(branch_name)
        
        # Check if already exists
        cursor.execute("""
            SELECT id FROM branches WHERE normalized_name = %s OR name = %s
        """, (normalized_name, branch_name))
        existing = cursor.fetchone()
        
        if existing:
            branch_map[branch_name] = existing[0]
            logger.debug(f"Branch '{branch_name}' already exists")
        else:
            if not dry_run:
                cursor.execute("""
                    INSERT INTO branches (id, name, normalized_name, city, state, is_active, created_at, updated_at)
                    VALUES (gen_random_uuid(), %s, %s, %s, %s, true, NOW(), NOW())
                    RETURNING id
                """, (branch_name, normalized_name, city, state))
                new_id = cursor.fetchone()[0]
                branch_map[branch_name] = new_id
                created_count += 1
                logger.info(f"Created branch: '{branch_name}' (city: {city}, state: {state})")
            else:
                created_count += 1
                logger.info(f"[DRY RUN] Would create branch: '{branch_name}' (city: {city}, state: {state})")
    
    if not dry_run:
        conn.commit()
    
    cursor.close()
    return branch_map, created_count


def link_jobs_to_branches(conn, branch_map: dict, dry_run: bool = True):
    """Link Jobs records to branches."""
    cursor = conn.cursor()
    
    # Use single batch update for efficiency
    if not dry_run and branch_map:
        # Build list of (branch_id, branch_name) tuples
        updates = list(branch_map.items())
        updated_count = 0
        
        for idx, (branch_name, branch_id) in enumerate(updates, 1):
            cursor.execute("""
                UPDATE jobs
                SET branch_id = %s, updated_at = NOW()
                WHERE branch_name = %s
                  AND branch_id IS NULL
            """, (branch_id, branch_name))
            updated_count += cursor.rowcount
            
            if idx % 10 == 0:
                logger.info(f"Linked {idx}/{len(updates)} branches to jobs...")
    else:
        # Estimate for dry-run
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE branch_name IS NOT NULL")
        updated_count = cursor.fetchone()[0] if cursor.fetchone() else 0
    
    if not dry_run:
        conn.commit()
        logger.info(f"Linked {updated_count} Jobs records to branches")
    else:
        logger.info(f"[DRY RUN] Would link {updated_count} Jobs records to branches")
    
    cursor.close()
    return updated_count


def link_booked_opportunities_to_branches(conn, branch_map: dict, dry_run: bool = True):
    """Link BookedOpportunities records to branches."""
    cursor = conn.cursor()
    
    if not dry_run and branch_map:
        updates = list(branch_map.items())
        updated_count = 0
        
        for idx, (branch_name, branch_id) in enumerate(updates, 1):
            cursor.execute("""
                UPDATE booked_opportunities
                SET branch_id = %s, updated_at = NOW()
                WHERE branch_name = %s
                  AND branch_id IS NULL
            """, (branch_id, branch_name))
            updated_count += cursor.rowcount
            
            if idx % 10 == 0:
                logger.info(f"Linked {idx}/{len(updates)} branches to booked_opportunities...")
    else:
        cursor.execute("SELECT COUNT(*) FROM booked_opportunities WHERE branch_name IS NOT NULL")
        result = cursor.fetchone()
        updated_count = result[0] if result else 0
    
    if not dry_run:
        conn.commit()
        logger.info(f"Linked {updated_count} BookedOpportunities records to branches")
    else:
        logger.info(f"[DRY RUN] Would link {updated_count} BookedOpportunities records to branches")
    
    cursor.close()
    return updated_count


def link_lead_status_to_branches(conn, branch_map: dict, dry_run: bool = True):
    """Link LeadStatus records to branches."""
    cursor = conn.cursor()
    
    if not dry_run and branch_map:
        updates = list(branch_map.items())
        updated_count = 0
        
        for idx, (branch_name, branch_id) in enumerate(updates, 1):
            cursor.execute("""
                UPDATE lead_status
                SET branch_id = %s, updated_at = NOW()
                WHERE branch_name = %s
                  AND branch_id IS NULL
            """, (branch_id, branch_name))
            updated_count += cursor.rowcount
            
            if idx % 10 == 0:
                logger.info(f"Linked {idx}/{len(updates)} branches to lead_status...")
    else:
        cursor.execute("SELECT COUNT(*) FROM lead_status WHERE branch_name IS NOT NULL")
        result = cursor.fetchone()
        updated_count = result[0] if result else 0
    
    if not dry_run:
        conn.commit()
        logger.info(f"Linked {updated_count} LeadStatus records to branches")
    else:
        logger.info(f"[DRY RUN] Would link {updated_count} LeadStatus records to branches")
    
    cursor.close()
    return updated_count


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Populate branches and link records')
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
        logger.info("Creating branches...")
        branch_map, created_count = create_branches(conn, dry_run=dry_run)
        
        logger.info("Linking Jobs to branches...")
        jobs_count = link_jobs_to_branches(conn, branch_map, dry_run=dry_run)
        
        logger.info("Linking BookedOpportunities to branches...")
        bo_count = link_booked_opportunities_to_branches(conn, branch_map, dry_run=dry_run)
        
        logger.info("Linking LeadStatus to branches...")
        ls_count = link_lead_status_to_branches(conn, branch_map, dry_run=dry_run)
        
        print("\n" + "="*80)
        print("BRANCHES POPULATION SUMMARY")
        print("="*80)
        print(f"Branches created: {created_count}")
        print(f"Jobs records linked: {jobs_count}")
        print(f"BookedOpportunities records linked: {bo_count}")
        print(f"LeadStatus records linked: {ls_count}")
        print("="*80 + "\n")
        
        if dry_run:
            logger.info("Dry run complete. Review the output and run with --execute to apply changes.")
        else:
            logger.info("Population complete!")
        
        return 0
        
    except Exception as e:
        logger.error(f"Population failed: {e}")
        logger.exception(e)
        conn.rollback()
        return 1
    finally:
        conn.close()


if __name__ == '__main__':
    sys.exit(main())

