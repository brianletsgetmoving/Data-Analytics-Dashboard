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
        
        # Parse connection string
        if db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "")
            parts = db_url.split("@")
            if len(parts) == 2:
                user = parts[0].split(":")[0] if ":" in parts[0] else parts[0]
                host_port_db = parts[1].split("/")
                host_port = host_port_db[0].split(":")
                host = host_port[0]
                port = int(host_port[1]) if len(host_port) > 1 else 5432
                database = host_port_db[1].split("?")[0] if len(host_port_db) > 1 else "data_analytics"
            else:
                host, port, database, user = "localhost", 5432, "data_analytics", "buyer"
        else:
            host, port, database, user = "localhost", 5432, "data_analytics", "buyer"
        
        try:
            self.pool = pool.ThreadedConnectionPool(
                minconn=2,
                maxconn=10,
                host=host,
                port=port,
                database=database,
                user=user
            )
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
            finally:
                cursor.close()
    
    def close(self):
        """Close all connections."""
        if self.pool:
            self.pool.closeall()


# Global database instance
db = Database()

