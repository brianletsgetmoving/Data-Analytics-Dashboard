#!/usr/bin/env python3
"""
Create lead_sources lookup table and populate it from existing referral_source values.
Then link LeadStatus, BadLead, and LostLead records to the lookup table.
"""

import sys
from pathlib import Path
import psycopg2
from datetime import datetime
import logging
import re

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.utils.database import get_db_connection
from scripts.utils.script_execution import check_and_log_execution

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SCRIPT_NAME = "populate_lead_sources"


def normalize_lead_source(source: str) -> tuple[str, str]:
    """
    Normalize a referral source into a category and clean name.
    
    Returns:
        Tuple of (normalized_name, category)
    """
    if not source:
        return ("Unknown", "Other")
    
    source_lower = source.lower().strip()
    
    # Define categories
    categories = {
        "online": ["google", "facebook", "instagram", "yelp", "website", "online", "web", "internet", "search"],
        "referral": ["referral", "friend", "family", "word of mouth", "recommendation"],
        "partner": ["partner", "affiliate", "corporate", "business"],
        "advertising": ["ad", "advertisement", "marketing", "promotion", "campaign"],
        "other": []
    }
    
    # Determine category
    category = "Other"
    for cat, keywords in categories.items():
        if any(keyword in source_lower for keyword in keywords):
            category = cat
            break
    
    # Clean up the name
    normalized = source.strip()
    # Remove extra whitespace
    normalized = re.sub(r'\s+', ' ', normalized)
    # Capitalize first letter of each word
    normalized = ' '.join(word.capitalize() for word in normalized.split())
    
    return (normalized, category)


def get_unique_referral_sources(conn):
    """Get all unique referral_source values from all tables."""
    cursor = conn.cursor()
    
    sources = set()
    
    # From LeadStatus
    cursor.execute("SELECT DISTINCT referral_source FROM lead_status WHERE referral_source IS NOT NULL")
    sources.update(row[0] for row in cursor.fetchall())
    
    # From BadLead (if it has referral_source - check schema)
    # Note: BadLead might not have referral_source, so we'll skip if it doesn't exist
    
    # From LostLead (if it has referral_source)
    # Note: LostLead might not have referral_source, so we'll skip if it doesn't exist
    
    # From BookedOpportunities
    cursor.execute("SELECT DISTINCT referral_source FROM booked_opportunities WHERE referral_source IS NOT NULL")
    sources.update(row[0] for row in cursor.fetchall())
    
    # From Jobs
    cursor.execute("SELECT DISTINCT referral_source FROM jobs WHERE referral_source IS NOT NULL")
    sources.update(row[0] for row in cursor.fetchall())
    
    cursor.close()
    return sorted(sources)


def create_lead_sources(conn, dry_run: bool = True, batch_size: int = 100):
    """Create lead_sources lookup table entries."""
    cursor = conn.cursor()
    
    # Get all unique referral sources
    sources = get_unique_referral_sources(conn)
    logger.info(f"Found {len(sources)} unique referral sources")
    
    created_count = 0
    source_map = {}  # original -> lead_source_id
    
    total = len(sources)
    for idx, source in enumerate(sources, 1):
        if idx % 100 == 0:
            logger.info(f"Processing lead source {idx}/{total}...")
        normalized_name, category = normalize_lead_source(source)
        
        # Check if already exists
        cursor.execute("""
            SELECT id FROM lead_sources WHERE name = %s
        """, (normalized_name,))
        existing = cursor.fetchone()
        
        if existing:
            source_map[source] = existing[0]
            logger.debug(f"Lead source '{normalized_name}' already exists")
        else:
            if not dry_run:
                cursor.execute("""
                    INSERT INTO lead_sources (id, name, category, is_active, created_at, updated_at)
                    VALUES (gen_random_uuid(), %s, %s, true, NOW(), NOW())
                    RETURNING id
                """, (normalized_name, category))
                new_id = cursor.fetchone()[0]
                source_map[source] = new_id
                created_count += 1
                logger.info(f"Created lead source: '{normalized_name}' (category: {category})")
            else:
                created_count += 1
                logger.info(f"[DRY RUN] Would create lead source: '{normalized_name}' (category: {category})")
    
    if not dry_run:
        conn.commit()
    
    cursor.close()
    return source_map, created_count


def link_lead_status_to_sources(conn, source_map: dict, dry_run: bool = True):
    """Link LeadStatus records to lead_sources."""
    cursor = conn.cursor()
    
    # Use batch update for efficiency
    if not dry_run and source_map:
        # Build batch update query
        updates = []
        for original_source, lead_source_id in source_map.items():
            normalized_name, _ = normalize_lead_source(original_source)
            updates.append((lead_source_id, original_source))
        
        # Execute in batches
        batch_size = 100
        updated_count = 0
        for i in range(0, len(updates), batch_size):
            batch = updates[i:i+batch_size]
            placeholders = ','.join(['%s'] * len(batch))
            # Use a more efficient update approach
            for lead_source_id, original_source in batch:
                cursor.execute("""
                    UPDATE lead_status
                    SET lead_source_id = %s, updated_at = NOW()
                    WHERE referral_source = %s
                      AND lead_source_id IS NULL
                """, (lead_source_id, original_source))
                updated_count += cursor.rowcount
            if (i // batch_size + 1) % 10 == 0:
                logger.info(f"Processed {i + len(batch)}/{len(updates)} lead source links...")
    else:
        updated_count = len(source_map)  # Estimate for dry-run
    
    if not dry_run:
        conn.commit()
        logger.info(f"Linked {updated_count} LeadStatus records to lead_sources")
    else:
        logger.info(f"[DRY RUN] Would link {updated_count} LeadStatus records to lead_sources")
    
    cursor.close()
    return updated_count


def link_bad_leads_to_sources(conn, source_map: dict, dry_run: bool = True):
    """Link BadLead records to lead_sources (if they have referral_source)."""
    # Note: BadLead might not have referral_source field
    # This is a placeholder - adjust based on actual schema
    return 0


def link_lost_leads_to_sources(conn, source_map: dict, dry_run: bool = True):
    """Link LostLead records to lead_sources (if they have referral_source)."""
    # Note: LostLead might not have referral_source field
    # This is a placeholder - adjust based on actual schema
    return 0


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Populate lead_sources and link records')
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
                                                      notes="Populate lead_sources lookup table"):
            return 0
        
        # Check if there's any work to do
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                (SELECT COUNT(*) FROM lead_status WHERE referral_source IS NOT NULL AND lead_source_id IS NULL) as ls_unlinked,
                (SELECT COUNT(*) FROM booked_opportunities WHERE referral_source IS NOT NULL) as bo_with_source,
                (SELECT COUNT(*) FROM jobs WHERE referral_source IS NOT NULL) as jobs_with_source
        """)
        result = cursor.fetchone()
        cursor.close()
        
        ls_unlinked = result[0] if result else 0
        bo_with_source = result[1] if result else 0
        jobs_with_source = result[2] if result else 0
        
        if ls_unlinked == 0 and bo_with_source == 0 and jobs_with_source == 0:
            logger.info("No unlinked records found. All lead sources are already populated.")
            return 0
        
        logger.info("Creating lead_sources...")
        source_map, created_count = create_lead_sources(conn, dry_run=dry_run)
        
        logger.info("Linking LeadStatus to lead_sources...")
        ls_count = link_lead_status_to_sources(conn, source_map, dry_run=dry_run)
        
        logger.info("Linking BadLead to lead_sources...")
        bl_count = link_bad_leads_to_sources(conn, source_map, dry_run=dry_run)
        
        logger.info("Linking LostLead to lead_sources...")
        ll_count = link_lost_leads_to_sources(conn, source_map, dry_run=dry_run)
        
        print("\n" + "="*80)
        print("LEAD SOURCES POPULATION SUMMARY")
        print("="*80)
        print(f"Lead sources created: {created_count}")
        print(f"LeadStatus records linked: {ls_count}")
        print(f"BadLead records linked: {bl_count}")
        print(f"LostLead records linked: {ll_count}")
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

