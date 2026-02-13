#!/usr/bin/env python3
"""Database module"""
import sqlite3

class Database:
    def __init__(self, db_path="test-agent.db"):
        self.db_path = db_path

    def test_method(self, search_term):
        print(f"search_term: {search_term}")
