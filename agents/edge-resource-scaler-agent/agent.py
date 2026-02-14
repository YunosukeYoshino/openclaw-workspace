#!/usr/bin/env python3
"""
エッジリソーススケーラーエージェント - エッジ環境のリソーススケーリングを担当するエージェント
An agent responsible for resource scaling in edge environments. Provides features such as auto-scaling, cost optimization, and resource monitoring.
"""

import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
import json

class EdgeResourceScalerAgentAgent:
    """エッジリソーススケーラーエージェント"""

    def __init__(self, db_path: str = "edge-resource-scaler-agent.db"):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._init_db()

    def _init_db(self):
        self.conn = sqlite3.connect(self.db_path)
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute("CREATE TABLE IF NOT EXISTS edge_resource_scaler_agent (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, metadata TEXT, status TEXT DEFAULT 'active', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        cursor.execute("CREATE TABLE IF NOT EXISTS tags (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)")
        cursor.execute("CREATE TABLE IF NOT EXISTS edge_resource_scaler_agent_tags (edge_resource_scaler_agent_id INTEGER, tag_id INTEGER, PRIMARY KEY (edge_resource_scaler_agent_id, tag_id), FOREIGN KEY (edge_resource_scaler_agent_id) REFERENCES edge_resource_scaler_agent(id), FOREIGN KEY (tag_id) REFERENCES tags(id))")

        self.conn.commit()

    def add_entry(self, title: str, content: str, metadata: Optional[Dict[str, Any]] = None, tags: Optional[List[str]] = None) -> int:
        cursor = self.conn.cursor()
        metadata_json = json.dumps(metadata) if metadata else None

        cursor.execute("INSERT INTO edge_resource_scaler_agent (title, content, metadata) VALUES (?, ?, ?)", (title, content, metadata_json))

        entry_id = cursor.lastrowid

        if tags:
            for tag_name in tags:
                cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
                cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
                tag_id = cursor.fetchone()[0]
                cursor.execute("INSERT INTO edge_resource_scaler_agent_tags (edge_resource_scaler_agent_id, tag_id) VALUES (?, ?)", (entry_id, tag_id))

        self.conn.commit()
        return entry_id

    def get_entry(self, entry_id: int) -> Optional[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, title, content, metadata, status, created_at, updated_at FROM edge_resource_scaler_agent WHERE id = ?", (entry_id,))
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "title": row[1],
                "content": row[2],
                "metadata": json.loads(row[3]) if row[3] else None,
                "status": row[4],
                "created_at": row[5],
                "updated_at": row[6],
            }
        return None

    def list_entries(self, status: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, title, content, metadata, status, created_at, updated_at FROM edge_resource_scaler_agent ORDER BY created_at DESC LIMIT ?", (limit,))

        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "title": row[1],
                "content": row[2],
                "metadata": json.loads(row[3]) if row[3] else None,
                "status": row[4],
                "created_at": row[5],
                "updated_at": row[6],
            })

        return results

    def search_entries(self, query: str) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        search_pattern = "%" + query + "%"
        cursor.execute("SELECT id, title, content, metadata, status, created_at, updated_at FROM edge_resource_scaler_agent WHERE title LIKE ? OR content LIKE ? ORDER BY created_at DESC", (search_pattern, search_pattern))

        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "title": row[1],
                "content": row[2],
                "metadata": json.loads(row[3]) if row[3] else None,
                "status": row[4],
                "created_at": row[5],
                "updated_at": row[6],
            })

        return results

    def delete_entry(self, entry_id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM edge_resource_scaler_agent_tags WHERE edge_resource_scaler_agent_id = ?", (entry_id,))
        cursor.execute("DELETE FROM edge_resource_scaler_agent WHERE id = ?", (entry_id,))

        self.conn.commit()
        return cursor.rowcount > 0

    def get_entries_by_tag(self, tag_name: str) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT e.id, e.title, e.content, e.metadata, e.status, e.created_at, e.updated_at FROM edge_resource_scaler_agent e INNER JOIN edge_resource_scaler_agent_tags et ON e.id = et.edge_resource_scaler_agent_id INNER JOIN tags t ON et.tag_id = t.id WHERE t.name = ? ORDER BY e.created_at DESC", (tag_name,))

        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "title": row[1],
                "content": row[2],
                "metadata": json.loads(row[3]) if row[3] else None,
                "status": row[4],
                "created_at": row[5],
                "updated_at": row[6],
            })

        return results

    def get_stats(self) -> Dict[str, Any]:
        cursor = self.conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM edge_resource_scaler_agent")
        total_entries = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM edge_resource_scaler_agent WHERE status = 'active'")
        active_entries = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tags")
        total_tags = cursor.fetchone()[0]

        return {
            "total_entries": total_entries,
            "active_entries": active_entries,
            "total_tags": total_tags,
        }

    def close(self):
        if self.conn:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


if __name__ == "__main__":
    with EdgeResourceScalerAgentAgent() as agent:
        print(f"edge-resource-scaler-agent エージェント初期化完了")
        stats = agent.get_stats()
        print(f"統計情報: {stats}")
