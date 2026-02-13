#!/usr/bin/env python3
"""
ユーザー行動分析エージェント
ユーザーの行動パターンを分析するエージェント
"""

import sqlite3
from datetime import datetime

class User_behavior_agentAgent:
    def __init__(self, db_path="user-behavior-agent.db"):
        self.db_path = db_path
        self.conn = None
        self.connect()

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def initialize_db(self):
        if self.conn:
            self.conn.executescript("""
CREATE TABLE IF NOT EXISTS user_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    action_type TEXT NOT NULL,
    category TEXT NOT NULL,
    context TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS behavior_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_name TEXT NOT NULL,
    description TEXT,
    frequency INTEGER,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
            """)
            self.conn.commit()

    def add_analytics(self, category, metric_name, value):
        if self.conn:
            self.conn.execute(
                "INSERT INTO analytics (category, metric_name, value) VALUES (?, ?, ?)",
                (category, metric_name, value)
            )
            self.conn.commit()

    def get_overall_stats(self):
        if self.conn:
            cursor = self.conn.execute("""
                SELECT category, COUNT(*) as count, AVG(value) as avg_value
                FROM analytics GROUP BY category
            """)
            return "\n".join([f"- {row['category']}: {row['count']} entries (avg: {row['avg_value']:.2f})"
                              for row in cursor.fetchall()])
        return "No database connection"

    def get_category_stats(self, category):
        if self.conn:
            cursor = self.conn.execute(
                "SELECT metric_name, AVG(value) as avg_value FROM analytics WHERE category = ? GROUP BY metric_name",
                (category,)
            )
            return "\n".join([f"- {row['metric_name']}: {row['avg_value']:.2f}"
                              for row in cursor.fetchall()])
        return f"No data for {category}"

    def close(self):
        if self.conn:
            self.conn.close()

def main():
    agent = User_behavior_agentAgent()
    agent.initialize_db()
    print(f"ユーザー行動分析エージェント initialized successfully")

if __name__ == "__main__":
    main()
