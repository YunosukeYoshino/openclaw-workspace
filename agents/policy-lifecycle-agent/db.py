"""Database module for agent"""

import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any

class AgentDatabase:
    """Agent database management"""

    def __init__(self, db_path: str = "agent.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            content TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS status_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT NOT NULL,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        conn.close()

    def add_item(self, name: str, content: str = "", status: str = "active") -> int:
        """Add an item"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO items (name, content, status)
        VALUES (?, ?, ?)
        """, (name, content, status))

        item_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return item_id

    def get_item(self, item_id: int) -> Optional[Dict[str, Any]]:
        """Get an item by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        row = cursor.fetchone()

        conn.close()

        if row:
            return {
                "id": row[0],
                "name": row[1],
                "content": row[2],
                "status": row[3],
                "created_at": row[4],
                "updated_at": row[5]
            }
        return None

    def update_item(self, item_id: int, **kwargs) -> bool:
        """Update an item"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        update_fields = []
        values = []

        for key, value in kwargs.items():
            if key in ["name", "content", "status"]:
                update_fields.append(f"{{key}} = ?")
                values.append(value)

        if not update_fields:
            conn.close()
            return False

        values.append(item_id)
        query = f"UPDATE items SET {{', '.join(update_fields)}}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"

        cursor.execute(query, values)
        conn.commit()
        conn.close()

        return True

    def delete_item(self, item_id: int) -> bool:
        """Delete an item"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()

        return cursor.rowcount > 0

    def list_items(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all items"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if status:
            cursor.execute("SELECT * FROM items WHERE status = ?", (status,))
        else:
            cursor.execute("SELECT * FROM items")

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "id": row[0],
                "name": row[1],
                "content": row[2],
                "status": row[3],
                "created_at": row[4],
                "updated_at": row[5]
            }
            for row in rows
        ]

    def set_status(self, status: str, message: str = ""):
        """Set current status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO status_log (status, message)
        VALUES (?, ?)
        """, (status, message))

        conn.commit()
        conn.close()

    def get_status(self) -> Dict[str, Any]:
        """Get latest status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM status_log
        ORDER BY created_at DESC
        LIMIT 1
        """)

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "id": row[0],
                "status": row[1],
                "message": row[2],
                "created_at": row[3]
            }
        return {"status": "unknown"}
