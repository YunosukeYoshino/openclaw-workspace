"""
Message Agent Database Module

Manages text messages and communication logs.
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import json

class MessageDB:
    """Database handler for Message Agent"""

    def __init__(self, db_path: str = "agents/message-agent/messages.db"):
        self.db_path = db_path
        self.conn = None
        self.init_db()

    def connect(self):
        """Create database connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def init_db(self):
        """Initialize database tables"""
        conn = self.connect()
        cursor = conn.cursor()

        # Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT NOT NULL,
                recipient TEXT NOT NULL,
                content TEXT NOT NULL,
                platform TEXT,
                message_type TEXT DEFAULT 'text' CHECK(message_type IN ('text','image','video','file','audio')),
                status TEXT DEFAULT 'sent' CHECK(status IN ('sent','delivered','read','failed')),
                thread_id TEXT,
                tags TEXT,
                metadata TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Communication logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS communication_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                participants TEXT NOT NULL,
                platform TEXT,
                communication_type TEXT DEFAULT 'chat' CHECK(communication_type IN ('chat','call','video','email','meeting')),
                title TEXT,
                summary TEXT,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                duration_minutes INTEGER,
                message_count INTEGER DEFAULT 0,
                tags TEXT
            )
        """)

        # Contacts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                identifier TEXT NOT NULL,
                platform TEXT,
                relationship TEXT,
                notes TEXT,
                last_contacted TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    # Message operations
    def add_message(self, sender: str, recipient: str, content: str,
                    platform: str = None, message_type: str = 'text',
                    thread_id: str = None) -> int:
        """Add a new message"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO messages (sender, recipient, content, platform, message_type, thread_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (sender, recipient, content, platform, message_type, thread_id))
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return message_id

    def get_messages(self, sender: str = None, recipient: str = None,
                     platform: str = None, limit: int = 50) -> List[Dict]:
        """Get messages, optionally filtered"""
        conn = self.connect()
        cursor = conn.cursor()

        query = "SELECT * FROM messages"
        params = []

        conditions = []
        if sender:
            conditions.append("sender = ?")
            params.append(sender)
        if recipient:
            conditions.append("recipient = ?")
            params.append(recipient)
        if platform:
            conditions.append("platform = ?")
            params.append(platform)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        messages = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return messages

    def update_message_status(self, message_id: int, status: str) -> bool:
        """Update message status"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE messages SET status = ? WHERE id = ?
        """, (status, message_id))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    def search_messages(self, keyword: str, limit: int = 20) -> List[Dict]:
        """Search messages by content"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM messages WHERE content LIKE ? ORDER BY timestamp DESC LIMIT ?
        """, (f"%{keyword}%", limit))
        messages = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return messages

    # Communication log operations
    def start_communication(self, participants: str, platform: str,
                          comm_type: str = 'chat', title: str = None) -> int:
        """Start a new communication log"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO communication_logs (participants, platform, communication_type, title)
            VALUES (?, ?, ?, ?)
        """, (participants, platform, comm_type, title))
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return log_id

    def end_communication(self, log_id: int, summary: str = None,
                         message_count: int = 0) -> bool:
        """End a communication log"""
        conn = self.connect()
        cursor = conn.cursor()

        # Get start time
        cursor.execute("SELECT start_time FROM communication_logs WHERE id = ?", (log_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return False

        start_time = datetime.fromisoformat(row['start_time'])
        end_time = datetime.now()
        duration = int((end_time - start_time).total_seconds() / 60)

        cursor.execute("""
            UPDATE communication_logs
            SET end_time = ?, duration_minutes = ?, summary = ?, message_count = ?
            WHERE id = ?
        """, (end_time.isoformat(), duration, summary, message_count, log_id))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    def get_communication_logs(self, platform: str = None,
                               comm_type: str = None, limit: int = 30) -> List[Dict]:
        """Get communication logs"""
        conn = self.connect()
        cursor = conn.cursor()

        query = "SELECT * FROM communication_logs"
        params = []

        conditions = []
        if platform:
            conditions.append("platform = ?")
            params.append(platform)
        if comm_type:
            conditions.append("communication_type = ?")
            params.append(comm_type)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY start_time DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return logs

    # Contact operations
    def add_contact(self, name: str, identifier: str, platform: str,
                   relationship: str = None) -> int:
        """Add a new contact"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO contacts (name, identifier, platform, relationship)
            VALUES (?, ?, ?, ?)
        """, (name, identifier, platform, relationship))
        contact_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return contact_id

    def get_contacts(self, platform: str = None, relationship: str = None) -> List[Dict]:
        """Get contacts"""
        conn = self.connect()
        cursor = conn.cursor()

        query = "SELECT * FROM contacts"
        params = []

        conditions = []
        if platform:
            conditions.append("platform = ?")
            params.append(platform)
        if relationship:
            conditions.append("relationship = ?")
            params.append(relationship)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY name"

        cursor.execute(query, params)
        contacts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return contacts

    def get_stats(self) -> Dict:
        """Get message statistics"""
        conn = self.connect()
        cursor = conn.cursor()

        stats = {}

        # Message stats
        cursor.execute("SELECT platform, COUNT(*) FROM messages GROUP BY platform")
        stats['messages_by_platform'] = dict(cursor.fetchall())

        cursor.execute("SELECT status, COUNT(*) FROM messages GROUP BY status")
        stats['messages_by_status'] = dict(cursor.fetchall())

        cursor.execute("SELECT COUNT(*) FROM messages WHERE DATE(timestamp) = DATE('now')")
        stats['messages_today'] = cursor.fetchone()[0]

        # Communication stats
        cursor.execute("SELECT communication_type, COUNT(*) FROM communication_logs GROUP BY communication_type")
        stats['communications_by_type'] = dict(cursor.fetchall())

        cursor.execute("SELECT AVG(duration_minutes) FROM communication_logs WHERE end_time IS NOT NULL")
        result = cursor.fetchone()[0]
        stats['avg_communication_duration'] = round(result, 1) if result else 0

        # Contact stats
        cursor.execute("SELECT COUNT(*) FROM contacts")
        stats['total_contacts'] = cursor.fetchone()[0]

        conn.close()
        return stats
