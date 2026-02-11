"""
Automation Agent Database Module
SQLite-based data storage for automation tasks and workflows
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

class AutomationDB:
    """Database manager for automation agent"""

    def __init__(self, db_path: str = "automation.db"):
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
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                task_type TEXT NOT NULL,
                config_json TEXT NOT NULL,
                enabled BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                steps_json TEXT NOT NULL,
                enabled BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS triggers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                trigger_type TEXT NOT NULL,
                config_json TEXT NOT NULL,
                target_task_id INTEGER,
                target_workflow_id INTEGER,
                enabled BOOLEAN DEFAULT 1,
                last_triggered TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (target_task_id) REFERENCES tasks(id),
                FOREIGN KEY (target_workflow_id) REFERENCES workflows(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                workflow_id INTEGER,
                status TEXT NOT NULL,
                result_json TEXT,
                error_message TEXT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks(id),
                FOREIGN KEY (workflow_id) REFERENCES workflows(id)
            )
        ''')

        conn.commit()
        conn.close()

    def create_task(self, name: str, task_type: str, config: Dict, description: str = None) -> int:
        """Create a new task"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO tasks (name, description, task_type, config_json)
            VALUES (?, ?, ?, ?)
        ''', (name, description, task_type, json.dumps(config)))

        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return task_id

    def get_tasks(self, enabled_only: bool = False) -> List[Dict]:
        """Get all tasks"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if enabled_only:
            cursor.execute("SELECT * FROM tasks WHERE enabled = 1")
        else:
            cursor.execute("SELECT * FROM tasks")

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_task(self, task_id: int) -> Optional[Dict]:
        """Get a specific task"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None

    def update_task(self, task_id: int, name: str = None, config: Dict = None, enabled: bool = None):
        """Update a task"""
        conn = self.get_connection()
        cursor = conn.cursor()

        updates = []
        params = []

        if name:
            updates.append("name = ?")
            params.append(name)
        if config:
            updates.append("config_json = ?")
            params.append(json.dumps(config))
        if enabled is not None:
            updates.append("enabled = ?")
            params.append(enabled)

        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(task_id)

        cursor.execute(f'''
            UPDATE tasks
            SET {', '.join(updates)}
            WHERE id = ?
        ''', params)

        conn.commit()
        conn.close()

    def create_workflow(self, name: str, steps: List[Dict], description: str = None) -> int:
        """Create a new workflow"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO workflows (name, description, steps_json)
            VALUES (?, ?, ?)
        ''', (name, description, json.dumps(steps)))

        workflow_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return workflow_id

    def get_workflows(self, enabled_only: bool = False) -> List[Dict]:
        """Get all workflows"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if enabled_only:
            cursor.execute("SELECT * FROM workflows WHERE enabled = 1")
        else:
            cursor.execute("SELECT * FROM workflows")

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_workflow(self, workflow_id: int) -> Optional[Dict]:
        """Get a specific workflow"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM workflows WHERE id = ?", (workflow_id,))
        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None

    def create_trigger(self, name: str, trigger_type: str, config: Dict,
                       target_task_id: int = None, target_workflow_id: int = None) -> int:
        """Create a new trigger"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO triggers (name, trigger_type, config_json, target_task_id, target_workflow_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, trigger_type, json.dumps(config), target_task_id, target_workflow_id))

        trigger_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return trigger_id

    def get_triggers(self, enabled_only: bool = False) -> List[Dict]:
        """Get all triggers"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if enabled_only:
            cursor.execute("SELECT * FROM triggers WHERE enabled = 1")
        else:
            cursor.execute("SELECT * FROM triggers")

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def log_execution(self, task_id: int = None, workflow_id: int = None,
                      status: str = 'running', result: Dict = None, error: str = None) -> int:
        """Log a task/workflow execution"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO executions (task_id, workflow_id, status, result_json, error_message)
            VALUES (?, ?, ?, ?, ?)
        ''', (task_id, workflow_id, status, json.dumps(result) if result else None, error))

        exec_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return exec_id

    def update_execution(self, exec_id: int, status: str, result: Dict = None, error: str = None):
        """Update execution status"""
        conn = self.get_connection()
        cursor = conn.cursor()

        updates = ["status = ?"]
        params = [status]

        if result:
            updates.append("result_json = ?")
            params.append(json.dumps(result))
        if error:
            updates.append("error_message = ?")
            params.append(error)

        if status == 'completed' or status == 'failed':
            updates.append("completed_at = CURRENT_TIMESTAMP")

        params.append(exec_id)

        cursor.execute(f'''
            UPDATE executions
            SET {', '.join(updates)}
            WHERE id = ?
        ''', params)

        conn.commit()
        conn.close()

    def get_executions(self, task_id: int = None, workflow_id: int = None, limit: int = 50) -> List[Dict]:
        """Get execution logs"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if task_id:
            cursor.execute('''
                SELECT * FROM executions
                WHERE task_id = ?
                ORDER BY started_at DESC LIMIT ?
            ''', (task_id, limit))
        elif workflow_id:
            cursor.execute('''
                SELECT * FROM executions
                WHERE workflow_id = ?
                ORDER BY started_at DESC LIMIT ?
            ''', (workflow_id, limit))
        else:
            cursor.execute('''
                SELECT * FROM executions
                ORDER BY started_at DESC LIMIT ?
            ''', (limit,))

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_statistics(self) -> Dict:
        """Get automation statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as total_tasks FROM tasks")
        total_tasks = cursor.fetchone()['total_tasks']

        cursor.execute("SELECT COUNT(*) as enabled_tasks FROM tasks WHERE enabled = 1")
        enabled_tasks = cursor.fetchone()['enabled_tasks']

        cursor.execute("SELECT COUNT(*) as total_workflows FROM workflows")
        total_workflows = cursor.fetchone()['total_workflows']

        cursor.execute("SELECT COUNT(*) as total_triggers FROM triggers")
        total_triggers = cursor.fetchone()['total_triggers']

        cursor.execute("SELECT status, COUNT(*) as count FROM executions GROUP BY status")
        exec_stats = {row['status']: row['count'] for row in cursor.fetchall()}

        conn.close()

        return {
            'tasks': {
                'total': total_tasks,
                'enabled': enabled_tasks
            },
            'workflows': total_workflows,
            'triggers': total_triggers,
            'executions': exec_stats
        }
