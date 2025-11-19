"""Database connection utility for scripts."""
import os
import psycopg2
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def get_db_connection():
    """
    Get a database connection using environment variables.
    
    Returns:
        psycopg2.connection: Database connection object
        
    Raises:
        psycopg2.Error: If connection fails
    """
    # Get database URL from environment
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://buyer:postgres@localhost:5432/data_analytics"
    )
    
    # Parse connection string
    try:
        # Try to parse as connection string
        if database_url.startswith("postgresql://") or database_url.startswith("postgres://"):
            from urllib.parse import urlparse, unquote
            
            parsed = urlparse(database_url)
            host = parsed.hostname or "localhost"
            port = parsed.port or 5432
            database = parsed.path.lstrip("/").split("?")[0] or "data_analytics"
            user = unquote(parsed.username) if parsed.username else "buyer"
            password = unquote(parsed.password) if parsed.password else "postgres"
        else:
            # Fallback to defaults
            host, port, database, user, password = "localhost", 5432, "data_analytics", "buyer", "postgres"
    except Exception as e:
        logger.warning(f"Error parsing database URL, using defaults: {e}")
        host, port, database, user, password = "localhost", 5432, "data_analytics", "buyer", "postgres"
    
    # Create connection
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        logger.info(f"Connected to database: {database} on {host}:{port}")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

