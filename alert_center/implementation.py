#!/usr/bin/env python3
"""
Alert Center - アラートセンター

アラート管理・通知センター
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from enum import Enum


class AlertSeverity(Enum):
    """アラート重要度"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertCenter:
    """アラートセンター"""

    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.db_path = Path(self.config.get("db_path", "data/alerts.db"))

    def _load_config(self) -> Dict[str, Any]:
        """設定を読み込む"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"db_path": "data/alerts.db", "retention_days": 30}

    def create_alert(self, title: str, message: str, severity: str = "info",
                     source: str = "system") -> int:
        """アラートを作成"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS alerts ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "title TEXT NOT NULL, "
            "message TEXT NOT NULL, "
            "severity TEXT NOT NULL, "
            "source TEXT NOT NULL, "
            "status TEXT DEFAULT 'active', "
            "created_at TEXT NOT NULL, "
            "acknowledged_at TEXT, "
            "acknowledged_by TEXT)"
        )

        cursor.execute(
            "INSERT INTO alerts (title, message, severity, source, status, created_at) "
            "VALUES (?, ?, ?, ?, 'active', ?)",
            (title, message, severity, source, datetime.now().isoformat())
        )

        alert_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return alert_id

    def acknowledge_alert(self, alert_id: int, acknowledged_by: str = "system"):
        """アラートを確認済みにする"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE alerts "
            "SET status = 'acknowledged', acknowledged_at = ?, acknowledged_by = ? "
            "WHERE id = ?",
            (datetime.now().isoformat(), acknowledged_by, alert_id)
        )

        conn.commit()
        conn.close()

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """アクティブなアラートを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, title, message, severity, source, status, created_at "
            "FROM alerts "
            "WHERE status = 'active' "
            "ORDER BY created_at DESC"
        )

        alerts = []
        for row in cursor.fetchall():
            alerts.append({
                "id": row[0],
                "title": row[1],
                "message": row[2],
                "severity": row[3],
                "source": row[4],
                "status": row[5],
                "created_at": row[6]
            })

        conn.close()
        return alerts

    def get_alert_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """アラート履歴を取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, title, message, severity, source, status, created_at "
            "FROM alerts "
            "ORDER BY created_at DESC "
            "LIMIT ?",
            (limit,)
        )

        alerts = []
        for row in cursor.fetchall():
            alerts.append({
                "id": row[0],
                "title": row[1],
                "message": row[2],
                "severity": row[3],
                "source": row[4],
                "status": row[5],
                "created_at": row[6]
            })

        conn.close()
        return alerts


def main():
    """メイン関数"""
    alert_center = AlertCenter()

    # テストアラート作成
    alert_id = alert_center.create_alert(
        title="Test Alert",
        message="This is a test alert",
        severity="info"
    )

    print(f"Created alert: {alert_id}")

    active_alerts = alert_center.get_active_alerts()
    print(f"Active alerts: {len(active_alerts)}")


if __name__ == "__main__":
    main()
