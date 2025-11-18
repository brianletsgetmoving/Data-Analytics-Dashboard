"""Database connection and session management."""
import os
import psycopg2
from psycopg2 import pool
from typing import Optional
import logging
from contextlib import contextmanager

from .config import settings

logger = logging.getLogger(__name__)


class Database:
    """Database connection manager."""
    
    def __init__(self):
        """Initialize database connection pool."""
        self.pool: Optional[pool.ThreadedConnectionPool] = None
        self._init_pool()
    
    def _init_pool(self):
        """Initialize connection pool."""
        db_url = settings.database_url
        
        # Use psycopg2's connection string parsing if available, otherwise parse manually
        try:
            # Try using psycopg2's parse_dsn for proper parsing
            from urllib.parse import urlparse, unquote
            
            if db_url.startswith("postgresql://") or db_url.startswith("postgres://"):
                parsed = urlparse(db_url)
                host = parsed.hostname or "localhost"
                port = parsed.port or 5432
                database = parsed.path.lstrip("/").split("?")[0] or "data_analytics"
                user = unquote(parsed.username) if parsed.username else "buyer"
                password = unquote(parsed.password) if parsed.password else None
            else:
                # Fallback to manual parsing
                host, port, database, user, password = "localhost", 5432, "data_analytics", "buyer", None
        except Exception as e:
            logger.warning(f"Error parsing database URL, using defaults: {e}")
            host, port, database, user, password = "localhost", 5432, "data_analytics", "buyer", None
        
        try:
            pool_kwargs = {
                "minconn": 2,
                "maxconn": 10,
                "host": host,
                "port": port,
                "database": database,
                "user": user,
            }
            if password:
                pool_kwargs["password"] = password
            
            self.pool = pool.ThreadedConnectionPool(**pool_kwargs)
            logger.info("Database connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get database connection from pool."""
        conn = None
        try:
            conn = self.pool.getconn()
            yield conn
        finally:
            if conn:
                self.pool.putconn(conn)
    
    def execute_query(self, query: str, params: Optional[tuple] = None):
        """Execute a query and return results."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, params)
                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    return [dict(zip(columns, row)) for row in rows]
                else:
                    conn.commit()
                    return {"affected_rows": cursor.rowcount}
            except psycopg2.Error as e:
                logger.error(f"Database error executing query: {e}")
                conn.rollback()
                raise
            except Exception as e:
                logger.error(f"Unexpected error executing query: {e}")
                conn.rollback()
                raise
            finally:
                cursor.close()
    
    def close(self):
        """Close all connections."""
        if self.pool:
            self.pool.closeall()


# Global database instance
db = Database()

