"""
Performance Agent Database Module
SQLite-based data storage for performance metrics and optimization tracking
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

class PerformanceDB:
    """Database manager for performance agent"""

    def __init__(self, db_path: str = "performance.db"):
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
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_unit TEXT,
                component TEXT,
                environment TEXT DEFAULT 'production',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tags TEXT,
                notes TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS benchmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                benchmark_name TEXT NOT NULL,
                benchmark_type TEXT NOT NULL,
                baseline_value REAL,
                target_value REAL,
                current_value REAL,
                unit TEXT,
                status TEXT DEFAULT 'pending',
                last_run TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS optimizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                optimization_name TEXT NOT NULL,
                component TEXT,
                description TEXT,
                before_value REAL,
                after_value REAL,
                improvement_percent REAL,
                unit TEXT,
                status TEXT DEFAULT 'planned',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                notes TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT NOT NULL,
                severity TEXT DEFAULT 'warning',
                metric_name TEXT,
                threshold REAL,
                current_value REAL,
                message TEXT,
                resolved INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_name TEXT NOT NULL,
                report_type TEXT NOT NULL,
                start_date TEXT,
                end_date TEXT,
                summary TEXT,
                insights TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def add_metric(self, metric_name: str, metric_value: float,
                   metric_unit: str = None, component: str = None,
                   environment: str = 'production', tags: List[str] = None,
                   notes: str = None) -> int:
        """Add a performance metric"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO metrics (metric_name, metric_value, metric_unit, component, environment, tags, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (metric_name, metric_value, metric_unit, component, environment,
              json.dumps(tags) if tags else None, notes))

        metric_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return metric_id

    def get_metrics(self, metric_name: str = None, component: str = None,
                    environment: str = None, limit: int = 100) -> List[Dict]:
        """Get metrics with optional filters"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM metrics WHERE 1=1"
        params = []

        if metric_name:
            query += " AND metric_name = ?"
            params.append(metric_name)

        if component:
            query += " AND component = ?"
            params.append(component)

        if environment:
            query += " AND environment = ?"
            params.append(environment)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_metric_trend(self, metric_name: str, hours: int = 24) -> List[Dict]:
        """Get metric trend over time"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT timestamp, metric_value
            FROM metrics
            WHERE metric_name = ?
            AND timestamp >= datetime('now', '-' || ? || ' hours')
            ORDER BY timestamp ASC
        ''', (metric_name, hours))

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def add_benchmark(self, benchmark_name: str, benchmark_type: str,
                     baseline_value: float = None, target_value: float = None,
                     current_value: float = None, unit: str = None,
                     status: str = 'pending', notes: str = None) -> int:
        """Add a benchmark"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO benchmarks (benchmark_name, benchmark_type, baseline_value, target_value, current_value, unit, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (benchmark_name, benchmark_type, baseline_value, target_value,
              current_value, unit, status, notes))

        benchmark_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return benchmark_id

    def get_benchmarks(self, benchmark_type: str = None, status: str = None) -> List[Dict]:
        """Get benchmarks"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM benchmarks WHERE 1=1"
        params = []

        if benchmark_type:
            query += " AND benchmark_type = ?"
            params.append(benchmark_type)

        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY created_at DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def update_benchmark(self, benchmark_id: int, current_value: float = None,
                       status: str = None) -> bool:
        """Update benchmark"""
        conn = self.get_connection()
        cursor = conn.cursor()

        updates = []
        params = []

        if current_value is not None:
            updates.append("current_value = ?")
            params.append(current_value)

        if status:
            updates.append("status = ?")
            params.append(status)

        if updates:
            updates.append("last_run = CURRENT_TIMESTAMP")
            params.append(benchmark_id)
            query = f"UPDATE benchmarks SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
            conn.close()
            return True

        conn.close()
        return False

    def add_optimization(self, optimization_name: str, component: str = None,
                        description: str = None, before_value: float = None,
                        after_value: float = None, unit: str = None,
                        status: str = 'planned', notes: str = None) -> int:
        """Add an optimization"""
        conn = self.get_connection()
        cursor = conn.cursor()

        improvement = None
        if before_value and after_value and before_value > 0:
            improvement = ((before_value - after_value) / before_value) * 100

        cursor.execute('''
            INSERT INTO optimizations (optimization_name, component, description, before_value, after_value, improvement_percent, unit, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (optimization_name, component, description, before_value, after_value,
              improvement, unit, status, notes))

        opt_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return opt_id

    def get_optimizations(self, status: str = None) -> List[Dict]:
        """Get optimizations"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if status:
            cursor.execute("SELECT * FROM optimizations WHERE status = ? ORDER BY created_at DESC", (status,))
        else:
            cursor.execute("SELECT * FROM optimizations ORDER BY created_at DESC")

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def update_optimization(self, opt_id: int, after_value: float = None,
                           status: str = None) -> bool:
        """Update optimization"""
        conn = self.get_connection()
        cursor = conn.cursor()

        updates = []
        params = []

        if after_value is not None:
            updates.append("after_value = ?")
            params.append(after_value)

            # Recalculate improvement
            cursor.execute("SELECT before_value FROM optimizations WHERE id = ?", (opt_id,))
            row = cursor.fetchone()
            if row and row['before_value']:
                improvement = ((row['before_value'] - after_value) / row['before_value']) * 100
                updates.append("improvement_percent = ?")
                params.append(improvement)

        if status:
            updates.append("status = ?")
            params.append(status)

        if status == 'completed':
            updates.append("completed_at = CURRENT_TIMESTAMP")

        if updates:
            params.append(opt_id)
            query = f"UPDATE optimizations SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
            conn.close()
            return True

        conn.close()
        return False

    def add_alert(self, alert_type: str, severity: str = 'warning',
                 metric_name: str = None, threshold: float = None,
                 current_value: float = None, message: str = None) -> int:
        """Add an alert"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO alerts (alert_type, severity, metric_name, threshold, current_value, message)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (alert_type, severity, metric_name, threshold, current_value, message))

        alert_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return alert_id

    def get_alerts(self, resolved: bool = None, severity: str = None) -> List[Dict]:
        """Get alerts"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM alerts WHERE 1=1"
        params = []

        if resolved is not None:
            query += " AND resolved = ?"
            params.append(1 if resolved else 0)

        if severity:
            query += " AND severity = ?"
            params.append(severity)

        query += " ORDER BY created_at DESC LIMIT 50"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def resolve_alert(self, alert_id: int) -> bool:
        """Resolve an alert"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE alerts SET resolved = 1, resolved_at = CURRENT_TIMESTAMP WHERE id = ?", (alert_id,))
        conn.commit()
        conn.close()
        return True

    def add_report(self, report_name: str, report_type: str,
                   start_date: str, end_date: str, summary: str = None,
                   insights: str = None) -> int:
        """Add a report"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO reports (report_name, report_type, start_date, end_date, summary, insights)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (report_name, report_type, start_date, end_date, summary, insights))

        report_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return report_id

    def get_reports(self, report_type: str = None) -> List[Dict]:
        """Get reports"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if report_type:
            cursor.execute("SELECT * FROM reports WHERE report_type = ? ORDER BY created_at DESC", (report_type,))
        else:
            cursor.execute("SELECT * FROM reports ORDER BY created_at DESC")

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_performance_summary(self) -> Dict:
        """Get performance summary statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Total metrics
        cursor.execute("SELECT COUNT(*) as total FROM metrics")
        total_metrics = cursor.fetchone()['total']

        # Active benchmarks
        cursor.execute("SELECT COUNT(*) as total FROM benchmarks WHERE status = 'active'")
        active_benchmarks = cursor.fetchone()['total']

        # Completed optimizations
        cursor.execute("SELECT COUNT(*) as total FROM optimizations WHERE status = 'completed'")
        completed_opts = cursor.fetchone()['total']

        # Total improvement
        cursor.execute("SELECT AVG(improvement_percent) as avg_improvement FROM optimizations WHERE status = 'completed' AND improvement_percent IS NOT NULL")
        avg_improvement = cursor.fetchone()['avg_improvement']

        # Unresolved alerts
        cursor.execute("SELECT COUNT(*) as total FROM alerts WHERE resolved = 0")
        unresolved_alerts = cursor.fetchone()['total']

        conn.close()
        return {
            'total_metrics': total_metrics,
            'active_benchmarks': active_benchmarks,
            'completed_optimizations': completed_opts,
            'average_improvement': avg_improvement,
            'unresolved_alerts': unresolved_alerts
        }
