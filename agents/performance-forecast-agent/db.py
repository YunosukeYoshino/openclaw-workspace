#!/usr/bin/env python3
"""Database module for performance-forecast-agent"""

import sqlite3
from datetime import datetime
from contextlib import contextmanager

class Database:
    def __init__(self, db_path="performance-forecast-agent.db"):
        self.db_path = db_path
        self.conn = None

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def initialize(self):
        with self.get_connection() as conn:
            conn.executescript("""
CREATE TABLE IF NOT EXISTS forecasts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    forecast_type TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    metric TEXT NOT NULL,
    predicted_value REAL,
    lower_bound REAL,
    upper_bound REAL,
    confidence REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS forecast_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    forecast_id INTEGER,
    actual_value REAL,
    error REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")
            conn.commit()

    def add_analytics(self, category, metric_name, value):
        with self.get_connection() as conn:
            conn.execute(
                "INSERT INTO analytics (category, metric_name, value) VALUES (?, ?, ?)",
                (category, metric_name, value)
            )
            conn.commit()

    def get_overall_stats(self):
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT category, COUNT(*) as count, AVG(value) as avg_value
                FROM analytics GROUP BY category
            """)
            return "\n".join([f"- {row['category']}: {row['count']} entries (avg: {row['avg_value']:.2f})"
                              for row in cursor.fetchall()])

    def get_category_stats(self, category):
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT metric_name, AVG(value) as avg_value FROM analytics WHERE category = ? GROUP BY metric_name",
                (category,)
            )
            return "\n".join([f"- {row['metric_name']}: {row['avg_value']:.2f}"
                              for row in cursor.fetchall()])

    def add_trend(self, category, trend_type, current_value, predicted_value, confidence):
        with self.get_connection() as conn:
            conn.execute(
                "INSERT INTO trends (category, trend_type, current_value, predicted_value, confidence) VALUES (?, ?, ?, ?, ?)",
                (category, trend_type, current_value, predicted_value, confidence)
            )
            conn.commit()

    def get_prediction(self, category, days=7):
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM trends WHERE category = ? ORDER BY timestamp DESC LIMIT 1",
                (category,)
            )
            row = cursor.fetchone()
            if row:
                return f"Current: {row['current_value']} -> Predicted: {row['predicted_value']} (confidence: {row['confidence']:.2%})"
            return f"No prediction data for {category}"

    def get_trending_topics(self, limit=10):
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT trend_type, AVG(predicted_value) as avg_pred
                FROM trends GROUP BY trend_type ORDER BY avg_pred DESC LIMIT ?
            """, (limit,))
            return "\n".join([f"{i+1}. {row['trend_type']} (score: {row['avg_pred']:.2f})"
                              for i, row in enumerate(cursor.fetchall())])
