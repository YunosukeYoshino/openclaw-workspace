#!/usr/bin/env python3
"""残りのエージェントのagent.pyを補完"""
from pathlib import Path

# agent.pyテンプレート
AGENT_TEMPLATE = """#!/usr/bin/env python3
import sqlite3
from pathlib import Path

class {class_name}:
    def __init__(self, db_path=None):
        self.db_path = db_path or Path(__file__).parent / '{name}.db'
        self.db_path = str(self.db_path)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT,
                category TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def add_entry(self, title, content, category=None, tags=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO entries (title, content, category, tags)
            VALUES (?, ?, ?, ?)
        ''', (title, content, category, tags))
        conn.commit()
        conn.close()
        return cursor.lastrowid

    def get_entries(self, category=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if category:
            cursor.execute('SELECT * FROM entries WHERE category = ? ORDER BY created_at DESC', (category,))
        else:
            cursor.execute('SELECT * FROM entries ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_entry(self, entry_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM entries WHERE id = ?', (entry_id,))
        row = cursor.fetchone()
        conn.close()
        return row

    def delete_entry(self, entry_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM entries WHERE id = ?', (entry_id,))
        conn.commit()
        conn.close()

if __name__ == '__main__':
    agent = {class_name}()
    print(f'{name} エージェントが初期化されました。')
"""

# 不足しているエージェント
incomplete_agents = ['focus-agent', 'gardening-agent', 'household-chores-agent', 'pomodoro-agent']

for agent_name in incomplete_agents:
    class_name = ''.join(word.capitalize() for word in agent_name.replace('-', ' ').split())
    content = AGENT_TEMPLATE.format(name=agent_name, class_name=class_name)

    agent_dir = Path('agents') / agent_name
    with open(agent_dir / 'agent.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'✅ Created {agent_name}/agent.py')
