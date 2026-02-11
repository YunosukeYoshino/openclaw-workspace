"""
Assistant Agent Database Module
SQLite-based data storage for assistant context and conversations
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

class AssistantDB:
    """Database manager for assistant agent"""

    def __init__(self, db_path: str = "assistant.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                channel_id TEXT NOT NULL,
                language TEXT DEFAULT 'en',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user','assistant','system')),
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS context (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                key TEXT NOT NULL,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id),
                UNIQUE(conversation_id, key)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT NOT NULL,
                command TEXT NOT NULL,
                description TEXT,
                language TEXT DEFAULT 'en'
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                language TEXT DEFAULT 'en',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def get_or_create_conversation(self, user_id: str, channel_id: str, language: str = 'en') -> int:
        """Get or create a conversation"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id FROM conversations
            WHERE user_id = ? AND channel_id = ?
            ORDER BY updated_at DESC LIMIT 1
        ''', (user_id, channel_id))

        row = cursor.fetchone()

        if row:
            conv_id = row['id']
            cursor.execute('''
                UPDATE conversations
                SET updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (conv_id,))
        else:
            cursor.execute('''
                INSERT INTO conversations (user_id, channel_id, language)
                VALUES (?, ?, ?)
            ''', (user_id, channel_id, language))
            conv_id = cursor.lastrowid

        conn.commit()
        conn.close()
        return conv_id

    def save_message(self, conversation_id: int, role: str, content: str) -> int:
        """Save a message to the conversation"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO messages (conversation_id, role, content)
            VALUES (?, ?, ?)
        ''', (conversation_id, role, content))

        msg_id = cursor.lastrowid

        # Update conversation timestamp
        cursor.execute('''
            UPDATE conversations
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (conversation_id,))

        conn.commit()
        conn.close()
        return msg_id

    def get_conversation_messages(self, conversation_id: int, limit: int = 50) -> List[Dict]:
        """Get messages from a conversation"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM messages
            WHERE conversation_id = ?
            ORDER BY timestamp DESC LIMIT ?
        ''', (conversation_id, limit))

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def set_context(self, conversation_id: int, key: str, value: str):
        """Set a context value"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO context (conversation_id, key, value, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (conversation_id, key, value))

        conn.commit()
        conn.close()

    def get_context(self, conversation_id: int) -> Dict[str, str]:
        """Get all context for a conversation"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT key, value FROM context
            WHERE conversation_id = ?
        ''', (conversation_id,))

        rows = cursor.fetchall()
        conn.close()
        return {row['key']: row['value'] for row in rows}

    def add_agent_command(self, agent_name: str, command: str, description: str, language: str = 'en'):
        """Add an agent command"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO agent_commands (agent_name, command, description, language)
            VALUES (?, ?, ?, ?)
        ''', (agent_name, command, description, language))

        conn.commit()
        conn.close()

    def get_agent_commands(self, agent_name: str = None, language: str = 'en') -> List[Dict]:
        """Get agent commands"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if agent_name:
            cursor.execute('''
                SELECT * FROM agent_commands
                WHERE agent_name = ? AND language = ?
                ORDER BY id
            ''', (agent_name, language))
        else:
            cursor.execute('''
                SELECT * FROM agent_commands
                WHERE language = ?
                ORDER BY agent_name, id
            ''', (language,))

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def add_knowledge(self, category: str, question: str, answer: str, language: str = 'en'):
        """Add knowledge base entry"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO knowledge (category, question, answer, language)
            VALUES (?, ?, ?, ?)
        ''', (category, question, answer, language))

        conn.commit()
        conn.close()

    def search_knowledge(self, query: str, language: str = 'en', limit: int = 5) -> List[Dict]:
        """Search knowledge base"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM knowledge
            WHERE language = ? AND (question LIKE ? OR answer LIKE ?)
            ORDER BY id DESC LIMIT ?
        ''', (language, f'%{query}%', f'%{query}%', limit))

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_conversation_stats(self) -> Dict:
        """Get conversation statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as total FROM conversations")
        total_convs = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as total FROM messages")
        total_msgs = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as total FROM agent_commands")
        total_cmds = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as total FROM knowledge")
        total_kb = cursor.fetchone()['total']

        conn.close()

        return {
            'conversations': total_convs,
            'messages': total_msgs,
            'agent_commands': total_cmds,
            'knowledge_entries': total_kb
        }
