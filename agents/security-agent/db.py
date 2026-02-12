"""
Security Agent Database Module

Manages security threats, incidents, and countermeasures.
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Any
import json

class SecurityDB:
    """Database handler for Security Agent"""

    def __init__(self, db_path: str = "agents/security-agent/security.db"):
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

        # Threats table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS threats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                severity TEXT NOT NULL CHECK(severity IN ('low','medium','high','critical')),
                title TEXT,
                description TEXT,
                status TEXT DEFAULT 'open' CHECK(status IN ('open','investigating','resolved','false_positive')),
                source TEXT,
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP,
                metadata TEXT
            )
        """)

        # Incidents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                severity TEXT NOT NULL CHECK(severity IN ('low','medium','high','critical')),
                status TEXT DEFAULT 'active' CHECK(status IN ('active','contained','investigating','resolved','closed')),
                affected_systems TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP,
                impact TEXT
            )
        """)

        # Measures table (security measures/controls)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS measures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                type TEXT NOT NULL CHECK(type IN ('preventive','detective','corrective','deterrent')),
                status TEXT DEFAULT 'active' CHECK(status IN ('active','inactive','decommissioned')),
                implemented_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_tested_at TIMESTAMP,
                effectiveness TEXT,
                related_threats TEXT
            )
        """)

        conn.commit()
        conn.close()

    # Threat operations
    def add_threat(self, type: str, severity: str, title: str = None,
                   description: str = None, source: str = None,
                   metadata: Dict = None) -> int:
        """Add a new security threat"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO threats (type, severity, title, description, source, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (type, severity, title, description, source,
              json.dumps(metadata) if metadata else None))
        threat_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return threat_id

    def get_threats(self, status: str = None, severity: str = None,
                    limit: int = 50) -> List[Dict]:
        """Get threats, optionally filtered"""
        conn = self.connect()
        cursor = conn.cursor()

        query = "SELECT * FROM threats"
        params = []

        conditions = []
        if status:
            conditions.append("status = ?")
            params.append(status)
        if severity:
            conditions.append("severity = ?")
            params.append(severity)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY detected_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        threats = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return threats

    def update_threat_status(self, threat_id: int, status: str) -> bool:
        """Update threat status"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE threats SET status = ?, resolved_at = ?
            WHERE id = ?
        """, (status, datetime.now().isoformat() if status == 'resolved' else None, threat_id))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    # Incident operations
    def add_incident(self, title: str, severity: str, description: str = None,
                     affected_systems: str = None) -> int:
        """Add a new security incident"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO incidents (title, severity, description, affected_systems)
            VALUES (?, ?, ?, ?)
        """, (title, severity, description, affected_systems))
        incident_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return incident_id

    def get_incidents(self, status: str = None, severity: str = None,
                      limit: int = 50) -> List[Dict]:
        """Get incidents, optionally filtered"""
        conn = self.connect()
        cursor = conn.cursor()

        query = "SELECT * FROM incidents"
        params = []

        conditions = []
        if status:
            conditions.append("status = ?")
            params.append(status)
        if severity:
            conditions.append("severity = ?")
            params.append(severity)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        incidents = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return incidents

    def update_incident_status(self, incident_id: int, status: str,
                               impact: str = None) -> bool:
        """Update incident status"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE incidents SET status = ?, updated_at = ?, resolved_at = ?, impact = COALESCE(?, impact)
            WHERE id = ?
        """, (status, datetime.now().isoformat(),
              datetime.now().isoformat() if status in ('resolved', 'closed') else None,
              impact, incident_id))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    # Measure operations
    def add_measure(self, name: str, type: str, description: str = None) -> int:
        """Add a new security measure"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO measures (name, type, description)
            VALUES (?, ?, ?)
        """, (name, type, description))
        measure_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return measure_id

    def get_measures(self, type: str = None, status: str = None) -> List[Dict]:
        """Get security measures"""
        conn = self.connect()
        cursor = conn.cursor()

        query = "SELECT * FROM measures"
        params = []

        conditions = []
        if type:
            conditions.append("type = ?")
            params.append(type)
        if status:
            conditions.append("status = ?")
            params.append(status)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY implemented_at DESC"

        cursor.execute(query, params)
        measures = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return measures

    def get_stats(self) -> Dict:
        """Get security statistics"""
        conn = self.connect()
        cursor = conn.cursor()

        stats = {}

        # Threat stats
        cursor.execute("SELECT severity, COUNT(*) FROM threats WHERE status != 'resolved' GROUP BY severity")
        stats['active_threats_by_severity'] = dict(cursor.fetchall())

        cursor.execute("SELECT status, COUNT(*) FROM incidents GROUP BY status")
        stats['incidents_by_status'] = dict(cursor.fetchall())

        cursor.execute("SELECT COUNT(*) FROM threats WHERE status = 'open' AND severity = 'critical'")
        stats['critical_threats'] = cursor.fetchone()[0]

        conn.close()
        return stats
