#!/usr/bin/env python3
import sqlite3
from typing import List, Dict

class BaseballAdvancedDB:
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
