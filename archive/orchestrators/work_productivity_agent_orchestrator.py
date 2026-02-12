#!/usr/bin/env python3
"""
ワーク・生産性エージェントオーケストレーター
Work & Productivity Agent Orchestrator

仕事や生産性を向上させるエージェントを自律的に作成する
Creates work and productivity-related agents for improving work efficiency.
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

PROJECT_CONFIG = {
    "name": "ワーク・生産性エージェントプロジェクト",
    "name_en": "Work & Productivity Agents Project",
    "version": "1.0.0",
    "created": datetime.now().isoformat()
}

AGENTS = [
    {
        "name": "task-agent",
        "name_ja": "タスク管理エージェント",
        "description": "タスクの作成・追跡・完了管理",
        "description_en": "Task creation, tracking, and completion management"
    },
    {
        "name": "time-tracking-agent",
        "name_ja": "時間追跡エージェント",
        "description": "作業時間の記録と分析",
        "description_en": "Work time recording and analysis"
    },
    {
        "name": "pomodoro-agent",
        "name_ja": "ポモドーロエージェント",
        "description": "ポモドーロテクニックによる集中時間管理",
        "description_en": "Pomodoro technique for focused time management"
    },
    {
        "name": "focus-agent",
        "name_ja": "フォーカスエージェント",
        "description": "集中モードの管理・通知抑制",
        "description_en": "Focus mode management and notification suppression"
    },
    {
        "name": "calendar-agent",
        "name_ja": "カレンダーエージェント",
        "description": "スケジュール管理・リマインダー",
        "description_en": "Schedule management and reminders"
    },
    {
        "name": "note-taking-agent",
        "name_ja": "ノート作成エージェント",
        "description": "メモ・ノートの記録と整理",
        "description_en": "Memo and note recording and organization"
    },
    {
        "name": "project-management-agent",
        "name_ja": "プロジェクト管理エージェント",
        "description": "プロジェクトの進捗・タスク・リソース管理",
        "description_en": "Project progress, task, and resource management"
    },
    {
        "name": "goal-setting-agent",
        "name_ja": "目標設定エージェント",
        "description": "目標の設定・追跡・達成記録",
        "description_en": "Goal setting, tracking, and achievement recording"
    },
]

PROGRESS_FILE = "/workspace/work_productivity_agent_progress.json"


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "started_at": datetime.now().isoformat(),
        "agents": {}
    }


def save_progress(progress):
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def create_agent_directory(agent_name):
    agent_dir = Path(f"/workspace/agents/{agent_name}")
    agent_dir.mkdir(parents=True, exist_ok=True)
    return agent_dir


def create_db_py(agent_dir, agent_name):
    content = f'''#!/usr/bin/env python3
"""
{agent_name} - Database Module

SQLite database operations for agent.
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class Database:
    """Database manager for {agent_name}"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path(__file__).parent / "data.db"
        self.db_path = db_path
        self.conn = None
        self._initialize()

    def _initialize(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS tasks ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "title TEXT NOT NULL,"
            "description TEXT,"
            "category TEXT,"
            "priority INTEGER DEFAULT 0,"
            "status TEXT DEFAULT 'pending',"
            "due_date TEXT,"
            "completed_date TEXT,"
            "estimated_time INTEGER,"
            "actual_time INTEGER,"
            "tags TEXT,"
            "created_at TEXT DEFAULT CURRENT_TIMESTAMP,"
            "updated_at TEXT DEFAULT CURRENT_TIMESTAMP"
            ")"
        )

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS time_entries ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "task_id INTEGER,"
            "activity TEXT NOT NULL,"
            "start_time TEXT NOT NULL,"
            "end_time TEXT,"
            "duration INTEGER,"
            "notes TEXT,"
            "FOREIGN KEY (task_id) REFERENCES tasks(id)"
            ")"
        )

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS sessions ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "session_type TEXT,"
            "start_time TEXT NOT NULL,"
            "end_time TEXT,"
            "duration INTEGER,"
            "focus_score INTEGER DEFAULT 0,"
            "interruptions INTEGER DEFAULT 0,"
            "notes TEXT"
            ")"
        )

        self.conn.commit()

    def add_task(self, title: str, description: str = None,
                category: str = None, priority: int = 0,
                due_date: str = None, estimated_time: int = None,
                tags: str = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, description, category, priority, due_date, estimated_time, tags) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (title, description, category, priority, due_date, estimated_time, tags)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_task(self, task_id: int) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def list_tasks(self, status: str = None,
                   category: str = None, priority: int = None) -> List[Dict]:
        cursor = self.conn.cursor()
        query = 'SELECT * FROM tasks WHERE 1=1'
        params = []

        if status:
            query += ' AND status = ?'
            params.append(status)

        if category:
            query += ' AND category = ?'
            params.append(category)

        if priority is not None:
            query += ' AND priority >= ?'
            params.append(priority)

        query += ' ORDER BY priority DESC, due_date ASC, created_at ASC'
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def update_task(self, task_id: int, **kwargs) -> bool:
        valid_fields = ['title', 'description', 'category', 'priority',
                       'status', 'due_date', 'completed_date',
                       'estimated_time', 'actual_time', 'tags']
        update_fields = {{k: v for k, v in kwargs.items() if k in valid_fields}}

        if not update_fields:
            return False

        update_fields['updated_at'] = datetime.now().isoformat()
        set_clause = ', '.join([f'{{k}} = ?' for k in update_fields.keys()])
        values = list(update_fields.values()) + [task_id]

        cursor = self.conn.cursor()
        cursor.execute(
            f"UPDATE tasks SET {{set_clause}} WHERE id = ?",
            values
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def delete_task(self, task_id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM time_entries WHERE task_id = ?', (task_id,))
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def start_time_entry(self, task_id: int, activity: str) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO time_entries (task_id, activity, start_time) VALUES (?, ?, ?)",
            (task_id, activity, datetime.now().isoformat())
        )
        self.conn.commit()
        return cursor.lastrowid

    def end_time_entry(self, entry_id: int) -> bool:
        cursor = self.conn.cursor()
        end_time = datetime.now().isoformat()
        cursor.execute(
            "SELECT start_time FROM time_entries WHERE id = ?",
            (entry_id,)
        )
        row = cursor.fetchone()
        if not row:
            return False

        start_time = datetime.fromisoformat(row[0])
        duration = int((datetime.now() - start_time).total_seconds())

        cursor.execute(
            "UPDATE time_entries SET end_time = ?, duration = ? WHERE id = ?",
            (end_time, duration, entry_id)
        )
        self.conn.commit()
        return True

    def get_statistics(self) -> Dict:
        cursor = self.conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM tasks WHERE status = "pending"')
        pending = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM tasks WHERE status = "completed"')
        completed = cursor.fetchone()[0]

        cursor.execute('SELECT SUM(duration) FROM time_entries WHERE duration IS NOT NULL')
        total_seconds = cursor.fetchone()[0] or 0
        total_hours = round(total_seconds / 3600, 2)

        cursor.execute('SELECT COUNT(*) FROM sessions')
        total_sessions = cursor.fetchone()[0]

        return {{
            'pending_tasks': pending,
            'completed_tasks': completed,
            'total_hours': total_hours,
            'total_sessions': total_sessions
        }}

    def close(self):
        if self.conn:
            self.conn.close()


if __name__ == '__main__':
    db = Database()
    print(f"Database initialized at {{db.db_path}}")
    print(f"Statistics: {{db.get_statistics()}}")
    db.close()
'''
    with open(agent_dir / "db.py", 'w', encoding='utf-8') as f:
        f.write(content)


def create_discord_py(agent_dir, agent_name, agent_info):
    content = f'''#!/usr/bin/env python3
"""
{agent_name} - Discord Bot Module

Discord bot for {agent_name} - {agent_info['description']}
"""

import discord
from discord.ext import commands
import re
from typing import Optional
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from db import Database


class DiscordBot(commands.Bot):
    """Discord bot for {agent_name}"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix='!',
            intents=intents,
            description="{agent_info['description_en']}"
        )

        self.db = Database()

    async def on_ready(self):
        print(f'{{self.user}} has connected to Discord!')

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return

        await self._process_natural_language(message)
        await super().on_message(message)

    async def _process_natural_language(self, message: discord.Message):
        content = message.content.lower()

        add_patterns = [
            r'(タスク|task|追加|add|作成|create)\\s*(.+)',
            r'(やる|to do|する|do)\\s*(.+)'
        ]

        for pattern in add_patterns:
            match = re.search(pattern, content)
            if match:
                title = match.group(2).strip()
                if len(title) > 2:
                    task_id = self.db.add_task(title=title)
                    await message.reply(f'タスクを追加しました: {{title}} (ID: {{task_id}})')
                    return

        list_patterns = [
            r'(一覧|list|全|all|what|show)',
            r'(タスク|tasks|todo|やること)'
        ]

        for pattern in list_patterns:
            if re.search(pattern, content):
                tasks = self.db.list_tasks(status='pending')
                if tasks:
                    response = "**タスク一覧**:\\n"
                    for i, task in enumerate(tasks[:10], 1):
                        priority_emoji = {{3: '🔴', 2: '🟡', 1: '🟢'}}
                        emoji = priority_emoji.get(task['priority'], '⚪')
                        response += f"{{i}}. {{emoji}} {{task['title']}}\\n"
                else:
                    response = "タスクがまだありません。"
                await message.reply(response)
                return

    @commands.command()
    async def add(self, ctx, *, title: str):
        task_id = self.db.add_task(title=title)
        await ctx.send(f'追加しました: {{title}} (ID: {{task_id}})')

    @commands.command()
    async def list(self, ctx, status: Optional[str] = None):
        tasks = self.db.list_tasks(status=status)
        if not tasks:
            await ctx.send("タスクがまだありません。")
            return

        response = "**タスク一覧**:\\n"
        for i, task in enumerate(tasks[:10], 1):
            priority_emoji = {{3: '🔴', 2: '🟡', 1: '🟢'}}
            emoji = priority_emoji.get(task['priority'], '⚪')
            response += f"{{i}}. {{emoji}} {{task['title']}}\\n"
        await ctx.send(response)

    @commands.command()
    async def done(self, ctx, task_id: int):
        from datetime import datetime
        success = self.db.update_task(task_id, status='completed', completed_date=datetime.now().isoformat())
        if success:
            await ctx.send(f"ID {{task_id}} を完了にしました。")
        else:
            await ctx.send(f"ID {{task_id}} が見つかりません。")

    @commands.command()
    async def delete(self, ctx, task_id: int):
        success = self.db.delete_task(task_id)
        if success:
            await ctx.send(f"ID {{task_id}} を削除しました。")
        else:
            await ctx.send(f"ID {{task_id}} が見つかりません。")

    @commands.command()
    async def stats(self, ctx):
        stats = self.db.get_statistics()
        response = "**統計**\\n"
        response += f"- 未完了タスク: {{stats['pending_tasks']}}\\n"
        response += f"- 完了タスク: {{stats['completed_tasks']}}\\n"
        response += f"- 総作業時間: {{stats['total_hours']}}時間\\n"
        response += f"- セッション数: {{stats['total_sessions']}}\\n"
        await ctx.send(response)

    def close(self):
        self.db.close()


def main():
    import os
    token = os.environ.get('DISCORD_TOKEN')
    if not token:
        print("Error: DISCORD_TOKEN environment variable not set")
        return
    bot = DiscordBot()
    bot.run(token)


if __name__ == '__main__':
    main()
'''
    with open(agent_dir / "discord.py", 'w', encoding='utf-8') as f:
        f.write(content)


def create_readme_md(agent_dir, agent_name, agent_info):
    content = f'''# {agent_name}

## 概要 (Overview)

{agent_info['description']}

{agent_info['description_en']}

## 機能 (Features)

- タスクの作成・追跡・完了 (Task creation, tracking, and completion)
- 時間追跡・記録 (Time tracking and recording)
- 優先度管理 (Priority management)
- 期限管理 (Due date management)
- 統計情報の表示 (Statistics display)
- Discord Botによる自然言語操作 (Natural language control via Discord Bot)

## インストール (Installation)

```bash
pip install -r requirements.txt
```

## 使用方法 (Usage)

```python
from db import Database

db = Database()

# タスク追加 (Add task)
task_id = db.add_task(
    title="Example Task",
    description="Description",
    priority=2
)

# 一覧 (List)
tasks = db.list_tasks(status='pending')

# 完了 (Complete)
db.update_task(task_id, status='completed')

# 統計 (Statistics)
stats = db.get_statistics()
```

## ライセンス (License)

MIT
'''
    with open(agent_dir / "README.md", 'w', encoding='utf-8') as f:
        f.write(content)


def create_requirements_txt(agent_dir):
    content = 'discord.py>=2.3.0\n'
    with open(agent_dir / "requirements.txt", 'w', encoding='utf-8') as f:
        f.write(content)


def create_agent(agent):
    agent_name = agent['name']

    print(f"Creating agent: {agent_name}...")

    agent_dir = create_agent_directory(agent_name)

    create_db_py(agent_dir, agent_name)
    create_discord_py(agent_dir, agent_name, agent)
    create_readme_md(agent_dir, agent_name, agent)
    create_requirements_txt(agent_dir)

    print(f"  ✓ Created: {agent_dir}")

    return True


def main():
    print("=" * 60)
    print(f"{PROJECT_CONFIG['name']} / {PROJECT_CONFIG['name_en']}")
    print(f"Version: {PROJECT_CONFIG['version']}")
    print("=" * 60)
    print()

    progress = load_progress()
    completed = progress.get('agents', {})

    remaining = [a for a in AGENTS if a['name'] not in completed]

    if not remaining:
        print("All agents already completed!")
        return

    print(f"Remaining agents: {len(remaining)} / {len(AGENTS)}")
    print()

    for agent in remaining:
        try:
            create_agent(agent)

            completed[agent['name']] = {
                "completed_at": datetime.now().isoformat(),
                "status": "completed"
            }
            save_progress(progress)

            print()

        except Exception as e:
            print(f"  ✗ Error creating {agent['name']}: {e}")
            continue

    print("=" * 60)
    print(f"Completed: {len(completed)} / {len(AGENTS)}")
    print("=" * 60)

    if len(completed) == len(AGENTS):
        print("\n🎉 All agents created successfully!")
        print("\n📊 Summary:")
        for agent in AGENTS:
            print(f"  ✓ {agent['name_ja']}")


if __name__ == '__main__':
    main()
