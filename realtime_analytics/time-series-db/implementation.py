#!/usr/bin/env python3
"""
Time Series Database Module
時系列データベース
"""

import sqlite3
from typing import Dict, Any, List
from datetime import datetime
import json


class TimeSeriesDB:
    """時系列データベース"""

    def __init__(self, db_path: str = "timeseries.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        """データベースを初期化"""
        cursor = self.conn.cursor()
        sql1 = "CREATE TABLE IF NOT EXISTS timeseries (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT NOT NULL, metric TEXT NOT NULL, value REAL NOT NULL, tags TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)"
        cursor.execute(sql1)
        sql2 = "CREATE INDEX IF NOT EXISTS idx_timestamp ON timeseries(timestamp)"
        cursor.execute(sql2)
        sql3 = "CREATE INDEX IF NOT EXISTS idx_metric ON timeseries(metric)"
        cursor.execute(sql3)
        self.conn.commit()

    def insert(self, timestamp: str, metric: str, value: float, tags: Dict[str, str] = None):
        """データを挿入"""
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO timeseries (timestamp, metric, value, tags) VALUES (?, ?, ?, ?)",
                      (timestamp, metric, value, json.dumps(tags) if tags else None))
        self.conn.commit()


if __name__ == '__main__':
    db = TimeSeriesDB()
    print("Time Series Database Module initialized")
