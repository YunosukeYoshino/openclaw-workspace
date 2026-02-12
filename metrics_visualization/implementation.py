#!/usr/bin/env python3
"""
Metrics Visualization - メトリクス可視化

システムメトリクスのリアルタイム可視化
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any


class MetricsVisualizer:
    """メトリクス可視化クラス"""

    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.db_path = Path(self.config.get("db_path", "data/metrics.db"))

    def _load_config(self) -> Dict[str, Any]:
        """設定を読み込む"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"db_path": "data/metrics.db", "retention_days": 30}

    def collect_metrics(self) -> Dict[str, Any]:
        """メトリクスを収集"""
        import psutil

        metrics = {
            "timestamp": datetime.now().isoformat(),
            "cpu": {
                "percent": psutil.cpu_percent(interval=1),
                "cores": psutil.cpu_count()
            },
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent
            },
            "disk": {
                "total": psutil.disk_usage('/').total,
                "used": psutil.disk_usage('/').used,
                "percent": psutil.disk_usage('/').percent
            },
            "network": {
                "bytes_sent": psutil.net_io_counters().bytes_sent,
                "bytes_recv": psutil.net_io_counters().bytes_recv
            }
        }

        self._save_metrics(metrics)
        return metrics

    def _save_metrics(self, metrics: Dict[str, Any]):
        """メトリクスを保存"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS metrics ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "timestamp TEXT NOT NULL, "
            "cpu_percent REAL, "
            "memory_percent REAL, "
            "disk_percent REAL, "
            "network_sent INTEGER, "
            "network_recv INTEGER)"
        )

        cursor.execute(
            "INSERT INTO metrics (timestamp, cpu_percent, memory_percent, disk_percent, network_sent, network_recv) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                metrics["timestamp"],
                metrics["cpu"]["percent"],
                metrics["memory"]["percent"],
                metrics["disk"]["percent"],
                metrics["network"]["bytes_sent"],
                metrics["network"]["bytes_recv"]
            )
        )

        conn.commit()
        conn.close()

    def get_metrics_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """メトリクス履歴を取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        since = datetime.now() - timedelta(hours=hours)

        cursor.execute(
            "SELECT timestamp, cpu_percent, memory_percent, disk_percent, network_sent, network_recv "
            "FROM metrics "
            "WHERE timestamp >= ? "
            "ORDER BY timestamp DESC",
            (since.isoformat(),)
        )

        metrics = []
        for row in cursor.fetchall():
            metrics.append({
                "timestamp": row[0],
                "cpu_percent": row[1],
                "memory_percent": row[2],
                "disk_percent": row[3],
                "network_sent": row[4],
                "network_recv": row[5]
            })

        conn.close()
        return metrics


def main():
    """メイン関数"""
    visualizer = MetricsVisualizer()
    metrics = visualizer.collect_metrics()

    print("Current Metrics:")
    print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
