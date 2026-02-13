#!/usr/bin/env python3
"""
Database module for rl-policy-agent
RLポリシーエージェント / RL Policy Agent
"""

import sqlite3
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path

class RlPolicyAgentDB:
    """Database handler for RLポリシーエージェント"""

    def __init__(self, db_path: str = "data/rl-policy-agent.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rl_policy_agent (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'active',
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""CREATE INDEX IF NOT EXISTS idx_status ON rl_policy_agent (status)""")
            conn.execute("""CREATE INDEX IF NOT EXISTS idx_user_id ON rl_policy_agent (user_id)""")
            conn.commit()

    def add_item(self, content: str, user_id: int, metadata: str = None) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("INSERT INTO rl_policy_agent (content, user_id, metadata) VALUES (?, ?, ?)", (content, user_id, metadata))
            conn.commit()
            return cursor.lastrowid

    def get_item(self, item_id: int) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM rl_policy_agent WHERE id = ?", (item_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def list_items(self, limit: int = 100, status: str = None) -> List[Dict[str, Any]]:
        query = "SELECT * FROM rl_policy_agent"
        params = []
        if status:
            query += " WHERE status = ?"
            params.append(status)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def search_items(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            pattern = "%" + query + "%"
            cursor = conn.execute("SELECT * FROM rl_policy_agent WHERE content LIKE ? ORDER BY created_at DESC LIMIT ?", (pattern, limit))
            return [dict(row) for row in cursor.fetchall()]

    def update_item(self, item_id: int, content: str = None, status: str = None) -> bool:
        updates = []
        params = []
        if content:
            updates.append("content = ?")
            params.append(content)
        if status:
            updates.append("status = ?")
            params.append(status)
        if not updates:
            return False
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(item_id)
        query = "UPDATE rl_policy_agent SET " + ", ".join(updates) + " WHERE id = ?"
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(query, params)
            conn.commit()
            return conn.total_changes > 0

    def remove_item(self, item_id: int) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM rl_policy_agent WHERE id = ?", (item_id,))
            conn.commit()
            return conn.total_changes > 0

    def get_stats(self) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM rl_policy_agent").fetchone()[0]
            active = conn.execute("SELECT COUNT(*) FROM rl_policy_agent WHERE status = 'active'").fetchone()[0]
            size = self.db_path.stat().st_size if self.db_path.exists() else 0
            return {"total": total, "active": active, "archived": total - active, "size": size / 1024}
