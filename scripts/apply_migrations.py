#!/usr/bin/env python3
"""
Apply Prisma migrations to the database.
"""

import sys
from pathlib import Path
import psycopg2
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.testing import get_db_connection
from src.utils.progress_monitor import log_step, log_success, log_error

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_table_exists(conn, table_name: str) -> bool:
    """Check if a table exists."""
    cursor = conn.cursor()
    cursor.execute("""
        select exists (
            select from information_schema.tables 
            where table_schema = 'public' 
            and table_name = %s
        );
    """, (table_name,))
    exists = cursor.fetchone()[0]
    cursor.close()
    return exists


def check_column_exists(conn, table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    cursor = conn.cursor()
    cursor.execute("""
        select exists (
            select from information_schema.columns 
            where table_schema = 'public' 
            and table_name = %s
            and column_name = %s
        );
    """, (table_name, column_name))
    exists = cursor.fetchone()[0]
    cursor.close()
    return exists


def split_sql_statements(sql: str) -> list:
    """Split SQL into individual statements."""
    # Remove comments
    lines = []
    for line in sql.split('\n'):
        if '--' in line:
            line = line[:line.index('--')]
        lines.append(line)
    sql_clean = '\n'.join(lines)
    
    # Split by semicolon, but keep statements that are part of blocks
    statements = []
    current_statement = []
    in_string = False
    string_char = None
    
    for char in sql_clean:
        current_statement.append(char)
        
        if char in ("'", '"') and (not current_statement or current_statement[-2] != '\\'):
            if not in_string:
                in_string = True
                string_char = char
            elif char == string_char:
                in_string = False
                string_char = None
        
        if char == ';' and not in_string:
            stmt = ''.join(current_statement).strip()
            if stmt and not stmt.startswith('--'):
                statements.append(stmt)
            current_statement = []
    
    # Add remaining statement if any
    if current_statement:
        stmt = ''.join(current_statement).strip()
        if stmt and not stmt.startswith('--'):
            statements.append(stmt)
    
    return [s for s in statements if s]


def apply_migration(conn, migration_file: Path, migration_name: str):
    """Apply a single migration file with idempotency checks."""
    try:
        migration_sql = migration_file.read_text()
        cursor = conn.cursor()
        
        # Check if this migration needs to be applied
        if "create table \"sales_persons\"" in migration_sql.lower():
            if check_table_exists(conn, "sales_persons"):
                log_step(f"Migration: {migration_name}", "sales_persons table already exists, skipping")
                cursor.close()
                return True
        
        # Check for column additions
        if "add column" in migration_sql.lower():
            # Parse which columns are being added
            if "sales_person_id" in migration_sql or "booked_opportunity_id" in migration_sql:
                tables_to_check = []
                if "alter table \"jobs\"" in migration_sql:
                    tables_to_check.append(("jobs", "sales_person_id"))
                if "alter table \"booked_opportunities\"" in migration_sql:
                    tables_to_check.append(("booked_opportunities", "sales_person_id"))
                if "alter table \"lead_status\"" in migration_sql:
                    if "booked_opportunity_id" in migration_sql:
                        tables_to_check.append(("lead_status", "booked_opportunity_id"))
                    if "sales_person_id" in migration_sql:
                        tables_to_check.append(("lead_status", "sales_person_id"))
                if "alter table \"lost_leads\"" in migration_sql:
                    tables_to_check.append(("lost_leads", "booked_opportunity_id"))
                if "alter table \"user_performance\"" in migration_sql:
                    tables_to_check.append(("user_performance", "sales_person_id"))
                if "alter table \"sales_performance\"" in migration_sql:
                    tables_to_check.append(("sales_performance", "sales_person_id"))
                
                # Check if all columns already exist
                all_exist = all(check_column_exists(conn, table, col) for table, col in tables_to_check)
                if all_exist and tables_to_check:
                    log_step(f"Migration: {migration_name}", "All columns already exist, skipping")
                    cursor.close()
                    return True
        
        # Split into individual statements and execute
        statements = split_sql_statements(migration_sql)
        
        for i, statement in enumerate(statements, 1):
            try:
                cursor.execute(statement)
            except psycopg2.Error as e:
                error_msg = str(e)
                # Check if it's a "already exists" or "duplicate key" error - that's okay for some operations
                if any(msg in error_msg.lower() for msg in ["already exists", "duplicate key", "violates unique constraint"]):
                    # For populate migration, these are expected
                    if "populate" in migration_name.lower() or "insert" in statement.lower():
                        logger.debug(f"Statement {i} skipped (already exists): {statement[:50]}...")
                        continue
                    else:
                        log_step(f"Migration: {migration_name}", f"Statement {i} already applied (skipping)")
                        continue
                else:
                    raise
        
        conn.commit()
        cursor.close()
        log_success(f"Applied migration: {migration_name} ({len(statements)} statements)")
        return True
    except Exception as e:
        error_msg = str(e)
        # Check if it's a "already exists" error - that's okay
        if "already exists" in error_msg.lower():
            log_step(f"Migration: {migration_name}", "Already applied (skipping)")
            conn.rollback()
            cursor.close()
            return True
        conn.rollback()
        cursor.close()
        log_error(f"Failed to apply {migration_name}: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return False


def main():
    """Apply all new migrations."""
    migrations_dir = Path("prisma/migrations")
    
    # New migrations to apply
    migrations = [
        "20251117185005_add_sales_person_table/migration.sql",
        "20251117185006_add_quote_number_foreign_keys/migration.sql",
        "20251117185007_populate_sales_person_links/migration.sql",
    ]
    
    log_step("Migrations", f"Applying {len(migrations)} migrations")
    
    try:
        conn = get_db_connection()
        
        for migration_path in migrations:
            migration_file = migrations_dir / migration_path
            migration_name = Path(migration_path).parent.name
            if not migration_file.exists():
                log_error(f"Migration file not found: {migration_file}")
                conn.close()
                return 1
            
            if not apply_migration(conn, migration_file, migration_name):
                conn.close()
                return 1
        
        conn.close()
        log_success("All migrations applied successfully")
        return 0
        
    except Exception as e:
        log_error(f"Migration failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())

