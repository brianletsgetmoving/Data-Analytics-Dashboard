#!/usr/bin/env python3
"""
Replace Ibrahim K with Brian K across all jobs and link all jobs to SalesPerson records.
"""
import sys
from pathlib import Path
import psycopg2
import logging
from typing import Dict

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.utils.database import get_db_connection

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def replace_ibrahim_with_brian(conn, dry_run: bool = True) -> int:
    """Replace Ibrahim K with Brian K in jobs table."""
    cursor = conn.cursor()
    
    try:
        # Count jobs with Ibrahim variations (handle trailing spaces)
        cursor.execute("""
            SELECT COUNT(*) FROM jobs 
            WHERE TRIM(sales_person_name) ILIKE '%Ibrahim%'
        """)
        ibrahim_count = cursor.fetchone()[0]
        logger.info(f"Found {ibrahim_count:,} jobs with Ibrahim variations")
        
        if ibrahim_count == 0:
            logger.info("No jobs with Ibrahim found")
            return 0
        
        if dry_run:
            logger.info("[DRY RUN] Would replace 'Ibrahim K' with 'Brian K' in jobs")
            return ibrahim_count
        
        # Replace Ibrahim K variations with Brian K (handle trailing spaces)
        cursor.execute("""
            UPDATE jobs 
            SET sales_person_name = 'Brian K',
                updated_at = NOW()
            WHERE TRIM(sales_person_name) ILIKE '%Ibrahim%'
            AND (TRIM(sales_person_name) ILIKE '%Ibrahim K%' 
                 OR TRIM(sales_person_name) ILIKE '%Ibrahim Keshavarz%'
                 OR TRIM(sales_person_name) = 'Ibrahim')
        """)
        updated = cursor.rowcount
        conn.commit()
        
        logger.info(f"✓ Replaced 'Ibrahim K' with 'Brian K' in {updated:,} jobs")
        return updated
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error replacing Ibrahim K: {e}")
        raise
    finally:
        cursor.close()


def link_all_jobs_to_salespersons(conn, dry_run: bool = True) -> dict:
    """
    Link all jobs to SalesPerson records using sales_person_name.
    Creates a mapping and updates sales_person_id.
    """
    cursor = conn.cursor()
    results = {}
    
    try:
        # Get all unique sales_person_names from jobs (normalize by trimming)
        cursor.execute("""
            SELECT DISTINCT TRIM(sales_person_name) as clean_name, 
                   MIN(sales_person_name) as original_name
            FROM jobs 
            WHERE sales_person_name IS NOT NULL 
            AND TRIM(sales_person_name) != ''
            GROUP BY TRIM(sales_person_name)
            ORDER BY TRIM(sales_person_name)
        """)
        # Create mapping: original_name -> clean_name for later use
        job_name_mapping = {}
        job_names_clean = []
        for clean_name, original_name in cursor.fetchall():
            job_names_clean.append(clean_name)
            job_name_mapping[clean_name] = original_name
        
        logger.info(f"Found {len(job_names_clean)} unique sales_person_name values in jobs (after trimming)")
        job_names = job_names_clean  # Use cleaned names for matching
        
        # Get all SalesPerson records
        cursor.execute("""
            SELECT id, name FROM sales_persons ORDER BY name
        """)
        salespersons = {row[1]: row[0] for row in cursor.fetchall()}
        logger.info(f"Found {len(salespersons)} SalesPerson records")
        
        # Create mapping: job sales_person_name -> SalesPerson id
        mapping = {}
        unmatched = []
        
        # Special mapping for known replacements
        special_mappings = {
            'Ibrahim K': 'Brian K',
            'Ibrahim Keshavarz': 'Brian K',
            'Ibrahim': 'Brian K',
        }
        
        for job_name in job_names:
            cleaned_name = job_name.strip() if job_name else ""
            
            # Apply special mappings first
            if cleaned_name in special_mappings:
                target_name = special_mappings[cleaned_name]
                if target_name in salespersons:
                    mapping[job_name] = salespersons[target_name]
                    logger.debug(f"Mapped '{job_name}' -> '{target_name}' (special mapping)")
                    continue
            
            # Try exact match first
            if cleaned_name in salespersons:
                mapping[job_name] = salespersons[cleaned_name]
            else:
                # Try case-insensitive match
                found = False
                cleaned_lower = cleaned_name.lower()
                
                for sp_name, sp_id in salespersons.items():
                    sp_name_lower = sp_name.lower().strip()
                    
                    # Exact case-insensitive match
                    if sp_name_lower == cleaned_lower:
                        mapping[job_name] = sp_id
                        found = True
                        logger.debug(f"Matched '{job_name}' -> '{sp_name}' (case-insensitive)")
                        break
                    
                    # Try removing emojis and special prefixes for matching
                    # Remove emojis, underscores, and leading special chars
                    import re
                    job_clean = re.sub(r'[🚚_]+', '', cleaned_name).strip()
                    sp_clean = re.sub(r'[🚚_]+', '', sp_name).strip()
                    
                    if job_clean.lower() == sp_clean.lower() and job_clean:
                        mapping[job_name] = sp_id
                        found = True
                        logger.debug(f"Matched '{job_name}' -> '{sp_name}' (cleaned)")
                        break
                    
                    # Try extracting just the name part (remove prefixes like "🚚__", "__")
                    # Pattern: emoji + underscores + name
                    job_match = re.match(r'[🚚_]*([A-Za-z].*)', cleaned_name)
                    sp_match = re.match(r'[🚚_]*([A-Za-z].*)', sp_name)
                    
                    if job_match and sp_match:
                        job_base = job_match.group(1).strip()
                        sp_base = sp_match.group(1).strip()
                        if job_base.lower() == sp_base.lower():
                            mapping[job_name] = sp_id
                            found = True
                            logger.debug(f"Matched '{job_name}' -> '{sp_name}' (extracted base)")
                            break
                    
                    # Try matching just the base name (first word + last initial)
                    # e.g., "🚚__Suraj S" might match if we have "Suraj" in CSV
                    # But we don't have Suraj in CSV, so skip this for now
                    
                    # Try fuzzy matching - extract first name and last initial
                    job_parts = cleaned_name.split()
                    if len(job_parts) >= 2:
                        job_first = job_parts[0]
                        job_last_initial = job_parts[-1][0] if len(job_parts[-1]) > 0 else ''
                        job_pattern = f"{job_first} {job_last_initial}".strip()
                        
                        sp_parts = sp_name.split()
                        if len(sp_parts) >= 2:
                            sp_first = sp_parts[0]
                            sp_last_initial = sp_parts[-1][0] if len(sp_parts[-1]) > 0 else ''
                            sp_pattern = f"{sp_first} {sp_last_initial}".strip()
                            
                            if job_pattern.lower() == sp_pattern.lower() and job_pattern:
                                mapping[job_name] = sp_id
                                found = True
                                logger.debug(f"Matched '{job_name}' -> '{sp_name}' (first+initial)")
                                break
                
                if not found:
                    unmatched.append(job_name)
        
        if unmatched:
            logger.warning(f"Could not match {len(unmatched)} sales_person_name values:")
            for name in unmatched[:20]:
                logger.warning(f"  - '{name}'")
            if len(unmatched) > 20:
                logger.warning(f"  ... and {len(unmatched) - 20} more")
        
        logger.info(f"Matched {len(mapping)} sales_person_name values to SalesPerson records")
        
        if dry_run:
            logger.info("[DRY RUN] Would link jobs to SalesPerson records")
            results['matched'] = len(mapping)
            results['unmatched'] = len(unmatched)
            return results
        
        # Update jobs with sales_person_id (handle all variations of the name)
        # First, update jobs that are already linked but might need updating
        total_updated = 0
        for clean_name, sp_id in mapping.items():
            # Update all jobs with this name (including variations with trailing spaces)
            # Update even if already linked (in case the link was wrong)
            cursor.execute("""
                UPDATE jobs 
                SET sales_person_id = %s,
                    updated_at = NOW()
                WHERE TRIM(sales_person_name) = %s
                AND sales_person_id != %s
            """, (sp_id, clean_name, sp_id))
            updated = cursor.rowcount
            total_updated += updated
            
            # Also update jobs that are NULL
            cursor.execute("""
                UPDATE jobs 
                SET sales_person_id = %s,
                    updated_at = NOW()
                WHERE TRIM(sales_person_name) = %s
                AND sales_person_id IS NULL
            """, (sp_id, clean_name))
            updated = cursor.rowcount
            total_updated += updated
        
        conn.commit()
        logger.info(f"✓ Linked {total_updated:,} jobs to SalesPerson records")
        
        results['matched'] = len(mapping)
        results['unmatched'] = len(unmatched)
        results['updated'] = total_updated
        
        return results
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error linking jobs to SalesPerson: {e}")
        raise
    finally:
        cursor.close()


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Replace Ibrahim K with Brian K and link jobs to SalesPerson')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (no changes)')
    
    args = parser.parse_args()
    dry_run = args.dry_run
    
    logger.info("="*80)
    logger.info("REPLACE IBRAHIM K WITH BRIAN K AND LINK JOBS")
    logger.info("="*80)
    
    if dry_run:
        logger.info("DRY RUN MODE - No changes will be made")
    
    conn = get_db_connection()
    
    try:
        # Step 1: Replace Ibrahim K with Brian K
        logger.info("")
        logger.info("Step 1: Replacing Ibrahim K with Brian K...")
        ibrahim_replaced = replace_ibrahim_with_brian(conn, dry_run)
        
        # Step 2: Link all jobs to SalesPerson records
        logger.info("")
        logger.info("Step 2: Linking all jobs to SalesPerson records...")
        link_results = link_all_jobs_to_salespersons(conn, dry_run)
        
        logger.info("")
        logger.info("="*80)
        logger.info("SUMMARY")
        logger.info("="*80)
        logger.info(f"Ibrahim K -> Brian K: {ibrahim_replaced:,} jobs")
        logger.info(f"Jobs linked to SalesPerson: {link_results.get('updated', 0):,}")
        logger.info(f"Matched names: {link_results.get('matched', 0)}")
        logger.info(f"Unmatched names: {link_results.get('unmatched', 0)}")
        
        # Final verification
        if not dry_run:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT COUNT(*) FROM jobs WHERE sales_person_id IS NOT NULL")
                linked_count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM jobs WHERE sales_person_id IS NULL AND sales_person_name IS NOT NULL")
                unlinked_count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM jobs")
                total_count = cursor.fetchone()[0]
                
                logger.info("")
                logger.info("Final Status:")
                logger.info(f"  Total jobs: {total_count:,}")
                logger.info(f"  Jobs with sales_person_id: {linked_count:,}")
                logger.info(f"  Jobs without sales_person_id (but have name): {unlinked_count:,}")
            finally:
                cursor.close()
        
        logger.info("="*80)
    
    finally:
        conn.close()


if __name__ == "__main__":
    main()

