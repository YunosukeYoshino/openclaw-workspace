#!/usr/bin/env python3
"""Test orchestrator to debug the issue"""

import os
from datetime import datetime

TEST_AGENT = {
    "name": "test-agent",
    "title": "Test Agent",
    "title_en": "Test Agent",
    "description": "Test",
    "description_en": "Test",
    "db_tables": """CREATE TABLE IF NOT EXISTS test (
    id INTEGER PRIMARY KEY
);""",
    "discord_commands": """
@bot.command()
async def test(ctx):
    await ctx.send("test")
"""
}

def create_agent_test():
    agent_dir = f"agents/{TEST_AGENT['name']}"
    os.makedirs(agent_dir, exist_ok=True)

    db_py_content = f'''#!/usr/bin/env python3
"""Database module"""
import sqlite3

class Database:
    def __init__(self, db_path="{TEST_AGENT['name']}.db"):
        self.db_path = db_path

    def test_method(self, search_term):
        print(f"search_term: {{search_term}}")
'''

    with open(f"{agent_dir}/db.py", "w", encoding="utf-8") as f:
        f.write(db_py_content)

    print(f"✅ Created: {TEST_AGENT['name']}")

if __name__ == "__main__":
    try:
        create_agent_test()
    except Exception as e:
        import traceback
        print(f"❌ Error: {e}")
        traceback.print_exc()
