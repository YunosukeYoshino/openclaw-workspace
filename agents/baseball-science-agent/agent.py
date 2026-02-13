#!/usr/bin/env python3
import sqlite3
from datetime import datetime
from typing import List, Dict

class BaseballAdvancedAgent:
    def __init__(self, db_path=None):
        self.db_path = db_path or "baseball.db"
        self.init_database()

    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS entries (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, category TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        c.execute("CREATE TABLE IF NOT EXISTS metrics (id INTEGER PRIMARY KEY AUTOINCREMENT, player_id TEXT, season INTEGER, metrics_json TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        conn.commit()
        conn.close()

    def add_entry(self, title, content, category=None):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO entries (title, content, category) VALUES (?, ?, ?)", (title, content, category))
        eid = c.lastrowid
        conn.commit()
        conn.close()
        return eid

    def get_entries(self, category=None):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        if category:
            c.execute("SELECT * FROM entries WHERE category = ?", (category,))
        else:
            c.execute("SELECT * FROM entries")
        cols = [d[0] for d in c.description]
        entries = [dict(zip(cols, r)) for r in c.fetchall()]
        conn.close()
        return entries

def main():
    import sys
    agent = BaseballAdvancedAgent()
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        for e in agent.get_entries():
            print(f"ID: {e['id']} | Title: {e['title']}")

if __name__ == "__main__":
    main()
