#!/usr/bin/env python3
"""
Database module for data-lakehouse-agent
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class data_lakehouse_agentDatabase:
    """Database handler for data-lakehouse-agent"""

    def __init__(self, db_path: str = None):
        """Initialize database connection"""
        self.db_path = db_path or Path(f"/workspace/agents/data-lakehouse-agent/data.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        self._init_tables()

    def _init_tables(self):
        """Initialize database tables"""
        logger.info("Initializing database tables...")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS tables(id INTEGER PRIMARY KEY, name TEXT, format TEXT, location TEXT, properties JSON)""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS zones(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT, description TEXT)""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS table_lineage(id INTEGER PRIMARY KEY, source_table INTEGER, target_table INTEGER, transformation TEXT, FOREIGN KEY (source_table) REFERENCES tables(id), FOREIGN KEY (target_table) REFERENCES tables(id))""")
        self.connection.commit()

    def execute(self, query: str, params: tuple = None) -> sqlite3.Cursor:
        """Execute a SQL query"""
        if params is None:
            params = ()
        self.cursor.execute(query, params)
        self.connection.commit()
        return self.cursor

    def fetchall(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Fetch all results from a query"""
        if params is None:
            params = ()
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]

    def fetchone(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """Fetch one result from a query"""
        if params is None:
            params = ()
        self.cursor.execute(query, params)
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """Insert a row into a table"""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        self.cursor.execute(query, tuple(data.values()))
        self.connection.commit()
        return self.cursor.lastrowid

    def update(self, table: str, data: Dict[str, Any], where: Dict[str, Any]) -> int:
        """Update rows in a table"""
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        where_clause = ' AND '.join([f"{k} = ?" for k in where.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        self.cursor.execute(query, tuple(data.values()) + tuple(where.values()))
        self.connection.commit()
        return self.cursor.rowcount

    def delete(self, table: str, where: Dict[str, Any]) -> int:
        """Delete rows from a table"""
        where_clause = ' AND '.join([f"{k} = ?" for k in where.keys()])
        query = f"DELETE FROM {table} WHERE {where_clause}"
        self.cursor.execute(query, tuple(where.values()))
        self.connection.commit()
        return self.cursor.rowcount

    def close(self):
        """Close database connection"""
        self.connection.close()


# For logging in _init_tables
import logging
logger = logging.getLogger(__name__)
