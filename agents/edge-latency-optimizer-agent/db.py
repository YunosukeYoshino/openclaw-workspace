#!/usr/bin/env python3
"""
edge-latency-optimizer-agent - データベースモジュール
"""

import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

DB_PATH = Path(__file__).parent / "edge-latency-optimizer-agent.db"

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS edge_latency_optimizer_agent (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, content TEXT NOT NULL, metadata TEXT, status TEXT DEFAULT 'active', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    cursor.execute("CREATE TABLE IF NOT EXISTS tags (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS edge_latency_optimizer_agent_tags (edge_latency_optimizer_agent_id INTEGER NOT NULL, tag_id INTEGER NOT NULL, PRIMARY KEY (edge_latency_optimizer_agent_id, tag_id), FOREIGN KEY (edge_latency_optimizer_agent_id) REFERENCES edge_latency_optimizer_agent(id) ON DELETE CASCADE, FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE)")

    cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_edge_latency_optimizer_agent_created_at ON edge_latency_optimizer_agent(created_at)')
    cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_edge_latency_optimizer_agent_status ON edge_latency_optimizer_agent(status)')

    conn.commit()
    conn.close()

def create_entry(title: str, content: str, metadata: Optional[Dict[str, Any]] = None, tags: Optional[List[str]] = None) -> int:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        metadata_json = json.dumps(metadata) if metadata else None

        cursor.execute(f"INSERT INTO edge_latency_optimizer_agent (title, content, metadata) VALUES (?, ?, ?)", (title, content, metadata_json))

        entry_id = cursor.lastrowid

        if tags:
            for tag_name in tags:
                cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
                cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
                tag_id = cursor.fetchone()[0]
                cursor.execute(f"INSERT INTO edge_latency_optimizer_agent_tags (edge_latency_optimizer_agent_id, tag_id) VALUES (?, ?)", (entry_id, tag_id))

        conn.commit()
        return entry_id

def get_entry(entry_id: int) -> Optional[Dict[str, Any]]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT id, title, content, metadata, status, created_at, updated_at FROM edge_latency_optimizer_agent WHERE id = ?", (entry_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

def list_entries(status: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        cursor = conn.cursor()

        if status:
            cursor.execute(f"SELECT id, title, content, metadata, status, created_at, updated_at FROM edge_latency_optimizer_agent WHERE status = ? ORDER BY created_at DESC LIMIT ? OFFSET ?", (status, limit, offset))
        else:
            cursor.execute(f"SELECT id, title, content, metadata, status, created_at, updated_at FROM edge_latency_optimizer_agent ORDER BY created_at DESC LIMIT ? OFFSET ?", (limit, offset))

        return [dict(row) for row in cursor.fetchall()]

def search_entries(query: str, limit: int = 100) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        search_pattern = "%" + query + "%"
        cursor.execute(f"SELECT id, title, content, metadata, status, created_at, updated_at FROM edge_latency_optimizer_agent WHERE title LIKE ? OR content LIKE ? ORDER BY created_at DESC LIMIT ?", (search_pattern, search_pattern, limit))

        return [dict(row) for row in cursor.fetchall()]

def update_entry(entry_id: int, **kwargs) -> bool:
    valid_fields = ["title", "content", "metadata", "status"]
    update_fields = {k: v for k, v in kwargs.items() if k in valid_fields}

    if not update_fields:
        return False

    if "metadata" in update_fields and update_fields["metadata"]:
        update_fields["metadata"] = json.dumps(update_fields["metadata"])

    set_clause = ", ".join([f"{k} = ?" for k in update_fields.keys()])
    values = list(update_fields.values())
    values.append(entry_id)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE edge_latency_optimizer_agent SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)
        conn.commit()
        return cursor.rowcount > 0

def delete_entry(entry_id: int) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM edge_latency_optimizer_agent_tags WHERE edge_latency_optimizer_agent_id = ?", (entry_id,))
        cursor.execute(f"DELETE FROM edge_latency_optimizer_agent WHERE id = ?", (entry_id,))
        conn.commit()
        return cursor.rowcount > 0

def add_tag_to_entry(entry_id: int, tag_name: str) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
        cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
        row = cursor.fetchone()
        if not row:
            return False

        tag_id = row[0]
        cursor.execute(f"INSERT OR IGNORE INTO edge_latency_optimizer_agent_tags (edge_latency_optimizer_agent_id, tag_id) VALUES (?, ?)", (entry_id, tag_id))
        conn.commit()
        return True

def remove_tag_from_entry(entry_id: int, tag_name: str) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM edge_latency_optimizer_agent_tags WHERE edge_latency_optimizer_agent_id = ? AND tag_id = (SELECT id FROM tags WHERE name = ?)", (entry_id, tag_name))
        conn.commit()
        return cursor.rowcount > 0

def get_all_tags() -> List[str]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM tags ORDER BY name")
        return [row[0] for row in cursor.fetchall()]

def get_entries_by_tag(tag_name: str, limit: int = 100) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT e.id, e.title, e.content, e.metadata, e.status, e.created_at, e.updated_at FROM edge_latency_optimizer_agent e INNER JOIN edge_latency_optimizer_agent_tags et ON e.id = et.edge_latency_optimizer_agent_id INNER JOIN tags t ON et.tag_id = t.id WHERE t.name = ? ORDER BY e.created_at DESC LIMIT ?", (tag_name, limit))

        return [dict(row) for row in cursor.fetchall()]

def get_stats() -> Dict[str, Any]:
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(f"SELECT COUNT(*) FROM edge_latency_optimizer_agent")
        total_entries = cursor.fetchone()[0]

        cursor.execute(f"SELECT COUNT(*) FROM edge_latency_optimizer_agent WHERE status = 'active'")
        active_entries = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tags")
        total_tags = cursor.fetchone()[0]

        cursor.execute(f"SELECT name, COUNT(*) as count FROM edge_latency_optimizer_agent_tags INNER JOIN tags ON edge_latency_optimizer_agent_tags.tag_id = tags.id GROUP BY name ORDER BY count DESC LIMIT 10")
        top_tags = [{"name": row[0], "count": row[1]} for row in cursor.fetchall()]

        return {
            "total_entries": total_entries,
            "active_entries": active_entries,
            "archived_entries": total_entries - active_entries,
            "total_tags": total_tags,
            "top_tags": top_tags,
        }

if __name__ == "__main__":
    init_db()
    print("データベース初期化完了")
    print("統計情報:", get_stats())
