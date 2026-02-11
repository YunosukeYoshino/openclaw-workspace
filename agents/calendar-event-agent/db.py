"""
Calendar Event Agent Database Module
SQLite-based data storage for calendar event management
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

class CalendarEventDB:
    """Database manager for calendar event agent"""

    def __init__(self, db_path: str = "calendar_events.db"):
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
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                location TEXT,
                start_datetime TEXT NOT NULL,
                end_datetime TEXT,
                all_day INTEGER DEFAULT 0,
                timezone TEXT DEFAULT 'UTC',
                recurrence_rule TEXT,
                reminder_minutes INTEGER,
                color TEXT,
                status TEXT DEFAULT 'confirmed',
                calendar TEXT DEFAULT 'default',
                attendees TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recurring_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                recurrence_rule TEXT NOT NULL,
                next_occurrence TEXT NOT NULL,
                end_recurrence TEXT,
                occurrences_generated INTEGER DEFAULT 0,
                FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                notification_time TEXT NOT NULL,
                message TEXT,
                sent INTEGER DEFAULT 0,
                sent_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                changes TEXT,
                performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
            )
        ''')

        conn.commit()
        conn.close()

    def create_event(self, title: str, start_datetime: str, end_datetime: str = None,
                     description: str = None, location: str = None, all_day: bool = False,
                     timezone: str = 'UTC', recurrence_rule: str = None,
                     reminder_minutes: int = None, color: str = None,
                     status: str = 'confirmed', calendar: str = 'default',
                     attendees: str = None) -> int:
        """Create a new calendar event"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO events (
                title, description, location, start_datetime, end_datetime,
                all_day, timezone, recurrence_rule, reminder_minutes, color,
                status, calendar, attendees
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            title, description, location, start_datetime, end_datetime,
            1 if all_day else 0, timezone, recurrence_rule, reminder_minutes,
            color, status, calendar, attendees
        ))

        event_id = cursor.lastrowid

        # Add to history
        cursor.execute('''
            INSERT INTO event_history (event_id, action, changes)
            VALUES (?, 'created', ?)
        ''', (event_id, json.dumps({'title': title, 'start': start_datetime})))

        conn.commit()
        conn.close()
        return event_id

    def get_event(self, event_id: int) -> Optional[Dict]:
        """Get a specific event"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_events(self, start_date: str = None, end_date: str = None,
                   status: str = None, calendar: str = None) -> List[Dict]:
        """Get events with optional filters"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM events WHERE 1=1"
        params = []

        if start_date:
            query += " AND start_datetime >= ?"
            params.append(start_date)

        if end_date:
            query += " AND start_datetime <= ?"
            params.append(end_date)

        if status:
            query += " AND status = ?"
            params.append(status)

        if calendar:
            query += " AND calendar = ?"
            params.append(calendar)

        query += " ORDER BY start_datetime ASC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_upcoming_events(self, days: int = 7, limit: int = 20) -> List[Dict]:
        """Get events in the next N days"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM events
            WHERE start_datetime >= datetime('now')
            AND start_datetime <= datetime('now', '+' || ? || ' days')
            ORDER BY start_datetime ASC
            LIMIT ?
        ''', (days, limit))

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def update_event(self, event_id: int, title: str = None, description: str = None,
                    location: str = None, start_datetime: str = None,
                    end_datetime: str = None, status: str = None,
                    reminder_minutes: int = None) -> bool:
        """Update an existing event"""
        conn = self.get_connection()
        cursor = conn.cursor()

        updates = []
        params = []
        changes = {}

        if title:
            updates.append("title = ?")
            params.append(title)
            changes['title'] = title

        if description:
            updates.append("description = ?")
            params.append(description)
            changes['description'] = description

        if location:
            updates.append("location = ?")
            params.append(location)
            changes['location'] = location

        if start_datetime:
            updates.append("start_datetime = ?")
            params.append(start_datetime)
            changes['start_datetime'] = start_datetime

        if end_datetime:
            updates.append("end_datetime = ?")
            params.append(end_datetime)
            changes['end_datetime'] = end_datetime

        if status:
            updates.append("status = ?")
            params.append(status)
            changes['status'] = status

        if reminder_minutes:
            updates.append("reminder_minutes = ?")
            params.append(reminder_minutes)
            changes['reminder_minutes'] = reminder_minutes

        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(event_id)
            query = f"UPDATE events SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)

            # Log changes
            cursor.execute('''
                INSERT INTO event_history (event_id, action, changes)
                VALUES (?, 'updated', ?)
            ''', (event_id, json.dumps(changes)))

            conn.commit()
            conn.close()
            return True

        conn.close()
        return False

    def delete_event(self, event_id: int) -> bool:
        """Delete an event"""
        conn = self.get_connection()
        cursor = conn.cursor()

        event = self.get_event(event_id)
        if event:
            cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
            conn.commit()
            conn.close()
            return True

        conn.close()
        return False

    def create_recurring_event(self, event_id: int, recurrence_rule: str,
                               end_recurrence: str = None) -> int:
        """Create a recurring event schedule"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Get the base event
        event = self.get_event(event_id)
        if not event:
            conn.close()
            return None

        # Calculate next occurrence
        next_occurrence = self._calculate_next_occurrence(
            event['start_datetime'], recurrence_rule
        )

        cursor.execute('''
            INSERT INTO recurring_events (event_id, recurrence_rule, next_occurrence, end_recurrence)
            VALUES (?, ?, ?, ?)
        ''', (event_id, recurrence_rule, next_occurrence, end_recurrence))

        recurring_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return recurring_id

    def _calculate_next_occurrence(self, current_time: str, rule: str) -> str:
        """Calculate the next occurrence based on recurrence rule"""
        # Simple implementation - in production, use dateutil.rrule
        # Daily: 'FREQ=DAILY', Weekly: 'FREQ=WEEKLY', Monthly: 'FREQ=MONTHLY'
        # This is a simplified version
        return current_time  # Placeholder

    def get_recurring_events(self) -> List[Dict]:
        """Get all recurring events"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT r.*, e.title, e.description, e.start_datetime as base_time
            FROM recurring_events r
            JOIN events e ON r.event_id = e.id
            ORDER BY r.next_occurrence ASC
        ''')

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def create_notification(self, event_id: int, notification_time: str,
                           message: str = None) -> int:
        """Create a notification for an event"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO notifications (event_id, notification_time, message)
            VALUES (?, ?, ?)
        ''', (event_id, notification_time, message))

        notif_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return notif_id

    def get_pending_notifications(self) -> List[Dict]:
        """Get notifications that need to be sent"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT n.*, e.title, e.start_datetime, e.location
            FROM notifications n
            JOIN events e ON n.event_id = e.id
            WHERE n.sent = 0
            AND n.notification_time <= datetime('now')
            ORDER BY n.notification_time ASC
        ''')

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def mark_notification_sent(self, notif_id: int) -> bool:
        """Mark a notification as sent"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE notifications
            SET sent = 1, sent_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (notif_id,))

        conn.commit()
        conn.close()
        return True

    def get_event_history(self, event_id: int) -> List[Dict]:
        """Get the history of changes for an event"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM event_history
            WHERE event_id = ?
            ORDER BY performed_at DESC
        ''', (event_id,))

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def search_events(self, query: str) -> List[Dict]:
        """Search events by title or description"""
        conn = self.get_connection()
        cursor = conn.cursor()

        search_term = f"%{query}%"
        cursor.execute('''
            SELECT * FROM events
            WHERE title LIKE ? OR description LIKE ? OR location LIKE ?
            ORDER BY start_datetime ASC
        ''', (search_term, search_term, search_term))

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_events_by_calendar(self, calendar: str) -> List[Dict]:
        """Get all events in a specific calendar"""
        return self.get_events(calendar=calendar)
