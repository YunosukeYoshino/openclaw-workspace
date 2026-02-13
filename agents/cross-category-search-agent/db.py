#!/usr/bin/env python3
"""
Database module for Cross-Category Integration Agent
カテゴリ横断統合エージェント データベースモジュール
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any

class CrossCategorySearchAgentDB:
    """Database handler for Cross-Category Integration Agent"""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), "data.db")
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self.connect()

    def connect(self) -> None:
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()

    def _init_tables(self) -> None:
        cursor = self.conn.cursor()
        # Create cross_integrations table
        cursor.execute("CREATE TABLE IF NOT EXISTS cross_integrations (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT NOT NULL, source TEXT, category TEXT, status TEXT DEFAULT 'active', metadata TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        # Create entries table
        cursor.execute("CREATE TABLE IF NOT EXISTS entries (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT NOT NULL, title TEXT, content TEXT NOT NULL, status TEXT DEFAULT 'active', priority INTEGER DEFAULT 0, metadata TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        # Create user_preferences table
        cursor.execute("CREATE TABLE IF NOT EXISTS user_preferences (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, category TEXT, preferences TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        # Create recommendations table
        cursor.execute("CREATE TABLE IF NOT EXISTS recommendations (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, item_type TEXT, item_id TEXT, score REAL, reason TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        # Create indices
        cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_{self._sanitize_table("cross_integrations")}_status ON cross_integrations(status)')
        cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_{self._sanitize_table("cross_integrations")}_category ON cross_integrations(category)')
        cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_{self._sanitize_table("cross_integrations")}_created_at ON cross_integrations(created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_entries_status ON entries(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_entries_type ON entries(type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_recommendations_user_id ON recommendations(user_id)')
        self.conn.commit()

    def _sanitize_table(self, table_name: str) -> str:
        return table_name.replace("-", "_").replace("_integ", "")

    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """Insert record into table"""
        cursor = self.conn.cursor()
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        cursor.execute(f'INSERT INTO {table} ({columns}) VALUES ({placeholders})', list(data.values()))
        self.conn.commit()
        return cursor.lastrowid

    def select(self, table: str, where: Optional[Dict[str, Any]] = None,
               order_by: Optional[str] = None, limit: Optional[int] = None) -> List[sqlite3.Row]:
        """Select records from table"""
        cursor = self.conn.cursor()
        query = f"SELECT * FROM {table}"
        params = []

        if where:
            conditions = ' AND '.join([f"{k} = ?" for k in where.keys()])
            query += f" WHERE {conditions}"
            params.extend(where.values())

        if order_by:
            query += f" ORDER BY {order_by}"

        if limit:
            query += f" LIMIT {limit}"

        cursor.execute(query, params)
        return cursor.fetchall()

    def update(self, table: str, where: Dict[str, Any], data: Dict[str, Any]) -> int:
        """Update records in table"""
        cursor = self.conn.cursor()
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        where_clause = ' AND '.join([f"{k} = ?" for k in where.keys()])
        params = list(data.values()) + list(where.values())

        cursor.execute(f"UPDATE {table} SET {set_clause} WHERE {where_clause}", params)
        self.conn.commit()
        return cursor.rowcount

    def delete(self, table: str, where: Dict[str, Any]) -> int:
        """Delete records from table"""
        cursor = self.conn.cursor()
        where_clause = ' AND '.join([f"{k} = ?" for k in where.keys()])
        cursor.execute(f"DELETE FROM {table} WHERE {where_clause}", list(where.values()))
        self.conn.commit()
        return cursor.rowcount

    def execute_query(self, query: str, params: Optional[List] = None) -> List[sqlite3.Row]:
        """Execute custom query"""
        cursor = self.conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()

    def close(self) -> None:
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
