"""
Scale Agent Database Module
SQLite-based data storage for scaling and capacity planning
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

class ScaleDB:
    """Database manager for scale agent"""

    def __init__(self, db_path: str = "scale.db"):
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
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resource_type TEXT NOT NULL,
                resource_name TEXT NOT NULL,
                capacity REAL NOT NULL,
                current_usage REAL DEFAULT 0,
                utilization_percent REAL,
                status TEXT DEFAULT 'active',
                environment TEXT DEFAULT 'production',
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scaling_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resource_id INTEGER,
                event_type TEXT NOT NULL,
                from_capacity REAL,
                to_capacity REAL,
                reason TEXT,
                triggered_by TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (resource_id) REFERENCES resources(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS capacity_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_name TEXT NOT NULL,
                resource_type TEXT,
                forecast_period_days INTEGER,
                projected_growth REAL,
                recommended_capacity REAL,
                estimated_date TEXT,
                priority TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'planned',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resource_id INTEGER,
                usage_value REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (resource_id) REFERENCES resources(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS thresholds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resource_id INTEGER,
                scale_up_threshold REAL,
                scale_down_threshold REAL,
                min_capacity REAL,
                max_capacity REAL,
                auto_scale_enabled INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resource_id) REFERENCES resources(id)
            )
        ''')

        conn.commit()
        conn.close()

    def add_resource(self, resource_type: str, resource_name: str, capacity: float,
                    environment: str = 'production', metadata: Dict = None) -> int:
        """Add a resource"""
        conn = self.get_connection()
        cursor = conn.cursor()

        utilization = 0.0 if capacity == 0 else 0.0

        cursor.execute('''
            INSERT INTO resources (resource_type, resource_name, capacity, utilization_percent, environment, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (resource_type, resource_name, capacity, utilization, environment,
              json.dumps(metadata) if metadata else None))

        resource_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return resource_id

    def get_resources(self, resource_type: str = None, environment: str = None,
                     status: str = None) -> List[Dict]:
        """Get resources"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM resources WHERE 1=1"
        params = []

        if resource_type:
            query += " AND resource_type = ?"
            params.append(resource_type)

        if environment:
            query += " AND environment = ?"
            params.append(environment)

        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY created_at DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def update_resource_usage(self, resource_id: int, current_usage: float) -> bool:
        """Update resource usage"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT capacity FROM resources WHERE id = ?", (resource_id,))
        row = cursor.fetchone()

        if row:
            capacity = row['capacity']
            utilization = (current_usage / capacity * 100) if capacity > 0 else 0

            cursor.execute('''
                UPDATE resources
                SET current_usage = ?, utilization_percent = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (current_usage, utilization, resource_id))

            conn.commit()
            conn.close()
            return True

        conn.close()
        return False

    def add_usage_history(self, resource_id: int, usage_value: float, notes: str = None) -> int:
        """Add usage history entry"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO usage_history (resource_id, usage_value, notes)
            VALUES (?, ?, ?)
        ''', (resource_id, usage_value, notes))

        history_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return history_id

    def get_usage_history(self, resource_id: int, limit: int = 100) -> List[Dict]:
        """Get usage history for a resource"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM usage_history
            WHERE resource_id = ?
            ORDER BY timestamp DESC LIMIT ?
        ''', (resource_id, limit))

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def add_scaling_event(self, resource_id: int, event_type: str,
                         from_capacity: float = None, to_capacity: float = None,
                         reason: str = None, triggered_by: str = None) -> int:
        """Add a scaling event"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO scaling_events (resource_id, event_type, from_capacity, to_capacity, reason, triggered_by)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (resource_id, event_type, from_capacity, to_capacity, reason, triggered_by))

        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return event_id

    def get_scaling_events(self, resource_id: int = None, status: str = None) -> List[Dict]:
        """Get scaling events"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM scaling_events WHERE 1=1"
        params = []

        if resource_id:
            query += " AND resource_id = ?"
            params.append(resource_id)

        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY created_at DESC LIMIT 50"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def complete_scaling_event(self, event_id: int) -> bool:
        """Complete a scaling event"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE scaling_events SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE id = ?", (event_id,))
        conn.commit()
        conn.close()
        return True

    def add_capacity_plan(self, plan_name: str, resource_type: str,
                         forecast_period_days: int, projected_growth: float,
                         recommended_capacity: float, estimated_date: str,
                         priority: str = 'medium', notes: str = None) -> int:
        """Add a capacity plan"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO capacity_plans (plan_name, resource_type, forecast_period_days, projected_growth,
                                       recommended_capacity, estimated_date, priority, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (plan_name, resource_type, forecast_period_days, projected_growth,
              recommended_capacity, estimated_date, priority, notes))

        plan_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return plan_id

    def get_capacity_plans(self, status: str = None, priority: str = None) -> List[Dict]:
        """Get capacity plans"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM capacity_plans WHERE 1=1"
        params = []

        if status:
            query += " AND status = ?"
            params.append(status)

        if priority:
            query += " AND priority = ?"
            params.append(priority)

        query += " ORDER BY created_at DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def update_capacity_plan(self, plan_id: int, status: str = None,
                            recommended_capacity: float = None) -> bool:
        """Update capacity plan"""
        conn = self.get_connection()
        cursor = conn.cursor()

        updates = []
        params = []

        if status:
            updates.append("status = ?")
            params.append(status)

        if recommended_capacity:
            updates.append("recommended_capacity = ?")
            params.append(recommended_capacity)

        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(plan_id)
            query = f"UPDATE capacity_plans SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
            conn.close()
            return True

        conn.close()
        return False

    def set_thresholds(self, resource_id: int, scale_up_threshold: float = None,
                      scale_down_threshold: float = None, min_capacity: float = None,
                      max_capacity: float = None, auto_scale_enabled: bool = False) -> int:
        """Set thresholds for a resource"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO thresholds
            (id, resource_id, scale_up_threshold, scale_down_threshold, min_capacity, max_capacity, auto_scale_enabled)
            VALUES (
                (SELECT id FROM thresholds WHERE resource_id = ?),
                ?, ?, ?, ?, ?, ?
            )
        ''', (resource_id, resource_id, scale_up_threshold, scale_down_threshold,
              min_capacity, max_capacity, 1 if auto_scale_enabled else 0))

        threshold_id = cursor.lastrowid if cursor.lastrowid else cursor.execute("SELECT id FROM thresholds WHERE resource_id = ?", (resource_id,)).fetchone()['id']
        conn.commit()
        conn.close()
        return threshold_id

    def get_thresholds(self, resource_id: int = None) -> List[Dict]:
        """Get thresholds"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if resource_id:
            cursor.execute("SELECT * FROM thresholds WHERE resource_id = ?", (resource_id,))
        else:
            cursor.execute("SELECT * FROM thresholds ORDER BY created_at DESC")

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def check_scale_triggers(self) -> List[Dict]:
        """Check which resources need scaling"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT r.*, t.scale_up_threshold, t.scale_down_threshold, t.min_capacity, t.max_capacity, t.auto_scale_enabled
            FROM resources r
            LEFT JOIN thresholds t ON r.id = t.resource_id
            WHERE r.status = 'active' AND t.auto_scale_enabled = 1
        ''')

        rows = cursor.fetchall()
        triggers = []

        for row in rows:
            resource = dict(row)
            utilization = resource['utilization_percent'] or 0

            if resource['scale_up_threshold'] and utilization >= resource['scale_up_threshold']:
                triggers.append({
                    'resource_id': resource['id'],
                    'resource_name': resource['resource_name'],
                    'action': 'scale_up',
                    'current_utilization': utilization,
                    'threshold': resource['scale_up_threshold'],
                    'recommended_capacity': min(resource['max_capacity'] or float('inf'), resource['capacity'] * 1.5) if resource['max_capacity'] else resource['capacity'] * 1.5
                })
            elif resource['scale_down_threshold'] and utilization <= resource['scale_down_threshold']:
                triggers.append({
                    'resource_id': resource['id'],
                    'resource_name': resource['resource_name'],
                    'action': 'scale_down',
                    'current_utilization': utilization,
                    'threshold': resource['scale_down_threshold'],
                    'recommended_capacity': max(resource['min_capacity'] or 0, resource['capacity'] * 0.7)
                })

        conn.close()
        return triggers

    def get_capacity_summary(self) -> Dict:
        """Get capacity summary"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Total resources
        cursor.execute("SELECT COUNT(*) as total FROM resources")
        total_resources = cursor.fetchone()['total']

        # Total capacity
        cursor.execute("SELECT SUM(capacity) as total FROM resources")
        total_capacity = cursor.fetchone()['total'] or 0

        # Total usage
        cursor.execute("SELECT SUM(current_usage) as total FROM resources")
        total_usage = cursor.fetchone()['total'] or 0

        # Average utilization
        cursor.execute("SELECT AVG(utilization_percent) as avg FROM resources WHERE capacity > 0")
        avg_utilization = cursor.fetchone()['avg'] or 0

        # Pending scaling events
        cursor.execute("SELECT COUNT(*) as total FROM scaling_events WHERE status = 'pending'")
        pending_events = cursor.fetchone()['total']

        # Active plans
        cursor.execute("SELECT COUNT(*) as total FROM capacity_plans WHERE status = 'planned'")
        active_plans = cursor.fetchone()['total']

        conn.close()
        return {
            'total_resources': total_resources,
            'total_capacity': total_capacity,
            'total_usage': total_usage,
            'average_utilization': avg_utilization,
            'pending_scaling_events': pending_events,
            'active_capacity_plans': active_plans
        }
