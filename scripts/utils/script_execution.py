"""Script execution logging utilities for idempotency."""
import psycopg2
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def log_script_execution(conn: psycopg2.extensions.connection, script_name: str, notes: Optional[str] = None) -> None:
    """
    Log script execution to the database.
    
    Args:
        conn: Database connection
        script_name: Name of the script being executed
        notes: Optional notes about the execution
    """
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT log_script_execution(%s, %s)
        """, (script_name, notes))
        conn.commit()
        logger.debug(f"Logged execution of script: {script_name}")
    except Exception as e:
        logger.warning(f"Failed to log script execution: {e}")
        conn.rollback()
    finally:
        cursor.close()


def script_already_executed(conn: psycopg2.extensions.connection, script_name: str) -> bool:
    """
    Check if a script has already been executed.
    
    Args:
        conn: Database connection
        script_name: Name of the script to check
        
    Returns:
        True if script has been executed, False otherwise
    """
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT script_already_executed(%s)
        """, (script_name,))
        result = cursor.fetchone()
        return result[0] if result else False
    except Exception as e:
        logger.warning(f"Failed to check script execution status: {e}")
        return False
    finally:
        cursor.close()


def check_and_log_execution(conn: psycopg2.extensions.connection, script_name: str, 
                            force: bool = False, notes: Optional[str] = None) -> bool:
    """
    Check if script should run and log execution.
    
    Args:
        conn: Database connection
        script_name: Name of the script
        force: If True, run even if already executed
        notes: Optional notes about the execution
        
    Returns:
        True if script should run, False if already executed
    """
    if force:
        log_script_execution(conn, script_name, notes or "Forced execution")
        return True
    
    if script_already_executed(conn, script_name):
        logger.info(f"Script '{script_name}' has already been executed. Use --force to run again.")
        return False
    
    log_script_execution(conn, script_name, notes)
    return True

