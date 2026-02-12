#!/usr/bin/env python3
"""
エージェントのdb.pyを自動生成するスクリプト
"""

import sys
from pathlib import Path

def generate_db(agent_name: str) -> str:
    """db.pyを生成"""
    db_name = agent_name.replace("-", "_")

    db_code = f'''#!/usr/bin/env python3
"""
{agent_name} Database Module
SQLite database management for {agent_name}
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

class {db_name.title()}DB:
    """{agent_name} Database Manager"""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection"""
        if db_path is None:
            db_path = Path(__file__).parent / "{agent_name}.db"
        self.db_path = db_path
        self.conn = None
        self.connect()
        self.create_tables()

    def connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def create_tables(self):
        """Create database tables"""
        cursor = self.conn.cursor()

        # Main table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS {db_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                status TEXT DEFAULT 'active',
                priority INTEGER DEFAULT 0,
                tags TEXT,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Tags table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Entry tags association table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entry_tags (
                entry_id INTEGER,
                tag_id INTEGER,
                PRIMARY KEY (entry_id, tag_id),
                FOREIGN KEY (entry_id) REFERENCES {db_name}(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )
        ''')

        self.conn.commit()

    def add_entry(self, data: Dict[str, Any]) -> int:
        """Add a new entry"""
        cursor = self.conn.cursor()

        cursor.execute('''
            INSERT INTO {db_name} (title, description, status, priority, tags, data)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data.get('title', ''),
            data.get('description', ''),
            data.get('status', 'active'),
            data.get('priority', 0),
            ','.join(data.get('tags', [])) if data.get('tags') else '',
            str(data.get('data', {}))
        ))

        entry_id = cursor.lastrowid

        # Add tags
        if data.get('tags'):
            self._add_tags(entry_id, data['tags'])

        self.conn.commit()
        return entry_id

    def get_entry(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """Get a single entry by ID"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM {db_name} WHERE id = ?', (entry_id,))
        row = cursor.fetchone()

        if row:
            return self._row_to_dict(row)
        return None

    def get_all_entries(self, status: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all entries, optionally filtered by status"""
        cursor = self.conn.cursor()

        if status:
            cursor.execute('''
                SELECT * FROM {db_name}
                WHERE status = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (status, limit))
        else:
            cursor.execute('''
                SELECT * FROM {db_name}
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))

        return [self._row_to_dict(row) for row in cursor.fetchall()]

    def update_entry(self, entry_id: int, data: Dict[str, Any]) -> bool:
        """Update an existing entry"""
        cursor = self.conn.cursor()

        cursor.execute('''
            UPDATE {db_name}
            SET title = ?, description = ?, status = ?, priority = ?, tags = ?, data = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            data.get('title', ''),
            data.get('description', ''),
            data.get('status', 'active'),
            data.get('priority', 0),
            ','.join(data.get('tags', [])) if data.get('tags') else '',
            str(data.get('data', {})),
            entry_id
        ))

        self.conn.commit()
        return cursor.rowcount > 0

    def delete_entry(self, entry_id: int) -> bool:
        """Delete an entry"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM {db_name} WHERE id = ?', (entry_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def search_entries(self, query: str) -> List[Dict[str, Any]]:
        """Search entries by title or description"""
        cursor = self.conn.cursor()
        search_term = f'%{{query}}%'

        cursor.execute('''
            SELECT * FROM {db_name}
            WHERE title LIKE ? OR description LIKE ?
            ORDER BY created_at DESC
            LIMIT 50
        ''', (search_term, search_term))

        return [self._row_to_dict(row) for row in cursor.fetchall()]

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics"""
        cursor = self.conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM {db_name}')
        total = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM {db_name} WHERE status = "active"')
        active = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM {db_name} WHERE status = "completed"')
        completed = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM {db_name} WHERE status = "archived"')
        archived = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM tags')
        tags = cursor.fetchone()[0]

        return {{
            'total': total,
            'active': active,
            'completed': completed,
            'archived': archived,
            'tags': tags
        }}

    def _add_tags(self, entry_id: int, tag_names: List[str]):
        """Add tags to an entry"""
        cursor = self.conn.cursor()

        for tag_name in tag_names:
            # Create tag if it doesn't exist
            cursor.execute('''
                INSERT OR IGNORE INTO tags (name) VALUES (?)
            ''', (tag_name,))

            # Get tag ID
            cursor.execute('SELECT id FROM tags WHERE name = ?', (tag_name,))
            tag_id = cursor.fetchone()[0]

            # Link entry to tag
            cursor.execute('''
                INSERT OR IGNORE INTO entry_tags (entry_id, tag_id) VALUES (?, ?)
            ''', (entry_id, tag_id))

        self.conn.commit()

    def _row_to_dict(self, row) -> Dict[str, Any]:
        """Convert database row to dictionary"""
        return dict(row)

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

if __name__ == '__main__':
    # Test database
    with {db_name.title()}DB() as db:
        # Add test entry
        entry_id = db.add_entry({{
            'title': 'Test Entry',
            'description': 'This is a test entry',
            'tags': ['test', 'demo']
        }})

        print(f"✅ Added entry with ID: {{entry_id}}")

        # Get entry
        entry = db.get_entry(entry_id)
        print(f"✅ Retrieved entry: {{entry}}")

        # Get stats
        stats = db.get_stats()
        print(f"✅ Stats: {{stats}}")
'''
    return db_code

def main():
    """メイン処理"""
    if len(sys.argv) < 2:
        print("Usage: python3 generate_db.py <agent-name>")
        return

    agent_name = sys.argv[1]
    agents_dir = Path("/workspace/agents")
    agent_dir = agents_dir / agent_name

    if not agent_dir.exists():
        print(f"Error: Agent directory '{agent_dir}' does not exist")
        return

    db_path = agent_dir / "db.py"
    if db_path.exists():
        print(f"db.py already exists: {db_path}")
        return

    db_content = generate_db(agent_name)
    db_path.write_text(db_content)
    print(f"✅ Created db.py for {agent_name}")

if __name__ == '__main__':
    main()
