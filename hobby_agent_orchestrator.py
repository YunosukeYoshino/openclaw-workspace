#!/usr/bin/env python3
"""
趣味・DIYエージェントオーケストレーター
Hobby & DIY Agent Orchestrator

趣味やDIY活動をサポートするエージェントを自律的に作成する
Creates hobby and DIY-related agents for supporting hobbies and DIY activities.
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

PROJECT_CONFIG = {
    "name": "趣味・DIYエージェントプロジェクト",
    "name_en": "Hobby & DIY Agents Project",
    "version": "1.0.0",
    "created": datetime.now().isoformat()
}

AGENTS = [
    {
        "name": "craft-agent",
        "name_ja": "クラフトエージェント",
        "description": "手芸・工作のプロジェクトと材料管理",
        "description_en": "Craft and DIY project and material management"
    },
    {
        "name": "diy-project-agent",
        "name_ja": "DIYプロジェクトエージェント",
        "description": "DIYプロジェクトの計画・追跡・記録",
        "description_en": "DIY project planning, tracking, and recording"
    },
    {
        "name": "photography-agent",
        "name_ja": "写真エージェント",
        "description": "写真の撮影記録・管理・共有",
        "description_en": "Photography shooting records, management, and sharing"
    },
    {
        "name": "cooking-agent",
        "name_ja": "料理エージェント",
        "description": "レシピ管理・献立計画・料理記録",
        "description_en": "Recipe management, meal planning, and cooking records"
    },
    {
        "name": "gardening-agent",
        "name_ja": "園芸エージェント",
        "description": "植物の世話・育成記録・カレンダー",
        "description_en": "Plant care, growing records, and calendar"
    },
    {
        "name": "collection-agent",
        "name_ja": "コレクションエージェント",
        "description": "コレクションアイテムの管理・カタログ化",
        "description_en": "Collection item management and cataloging"
    },
    {
        "name": "learning-agent",
        "name_ja": "学習エージェント",
        "description": "新しいスキルの習得・学習記録・進捗管理",
        "description_en": "New skill acquisition, learning records, and progress management"
    },
    {
        "name": "hobby-event-agent",
        "name_ja": "趣味イベントエージェント",
        "description": "趣味関連のイベント・フェア・展示会の管理",
        "description_en": "Hobby-related events, fairs, and exhibition management"
    },
]

PROGRESS_FILE = "/workspace/hobby_agent_progress.json"


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

SQLite database operations for the agent.
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
            "CREATE TABLE IF NOT EXISTS projects ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "title TEXT NOT NULL,"
            "description TEXT,"
            "category TEXT,"
            "status TEXT DEFAULT 'planned',"
            "start_date TEXT,"
            "end_date TEXT,"
            "progress INTEGER DEFAULT 0,"
            "notes TEXT,"
            "tags TEXT,"
            "created_at TEXT DEFAULT CURRENT_TIMESTAMP,"
            "updated_at TEXT DEFAULT CURRENT_TIMESTAMP"
            ")"
        )

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS items ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "name TEXT NOT NULL,"
            "description TEXT,"
            "category TEXT,"
            "quantity INTEGER DEFAULT 1,"
            "location TEXT,"
            "status TEXT DEFAULT 'available',"
            "created_at TEXT DEFAULT CURRENT_TIMESTAMP"
            ")"
        )

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS logs ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "project_id INTEGER,"
            "title TEXT,"
            "content TEXT,"
            "log_date TEXT DEFAULT CURRENT_TIMESTAMP,"
            "FOREIGN KEY (project_id) REFERENCES projects(id)"
            ")"
        )

        self.conn.commit()

    def add_project(self, title: str, description: str = None,
                   category: str = None, status: str = 'planned',
                   notes: str = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO projects (title, description, category, status, notes) VALUES (?, ?, ?, ?, ?)",
            (title, description, category, status, notes)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_project(self, project_id: int) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def list_projects(self, status: str = None,
                     category: str = None) -> List[Dict]:
        cursor = self.conn.cursor()
        query = 'SELECT * FROM projects WHERE 1=1'
        params = []

        if status:
            query += ' AND status = ?'
            params.append(status)

        if category:
            query += ' AND category = ?'
            params.append(category)

        query += ' ORDER BY created_at DESC'
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def update_project(self, project_id: int, **kwargs) -> bool:
        valid_fields = ['title', 'description', 'category', 'status',
                       'start_date', 'end_date', 'progress', 'notes']
        update_fields = {{k: v for k, v in kwargs.items() if k in valid_fields}}

        if not update_fields:
            return False

        update_fields['updated_at'] = datetime.now().isoformat()
        set_clause = ', '.join([f'{{k}} = ?' for k in update_fields.keys()])
        values = list(update_fields.values()) + [project_id]

        cursor = self.conn.cursor()
        cursor.execute(
            f"UPDATE projects SET {{set_clause}} WHERE id = ?",
            values
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def add_item(self, name: str, description: str = None,
                category: str = None, quantity: int = 1,
                location: str = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO items (name, description, category, quantity, location) VALUES (?, ?, ?, ?, ?)",
            (name, description, category, quantity, location)
        )
        self.conn.commit()
        return cursor.lastrowid

    def list_items(self, category: str = None) -> List[Dict]:
        cursor = self.conn.cursor()
        query = 'SELECT * FROM items WHERE 1=1'
        params = []

        if category:
            query += ' AND category = ?'
            params.append(category)

        query += ' ORDER BY created_at DESC'
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def add_log(self, project_id: int, title: str, content: str = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO logs (project_id, title, content) VALUES (?, ?, ?)",
            (project_id, title, content)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_statistics(self) -> Dict:
        cursor = self.conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM projects')
        total_projects = cursor.fetchone()[0]

        cursor.execute("SELECT status, COUNT(*) FROM projects GROUP BY status")
        by_status = {{row[0]: row[1] for row in cursor.fetchall()}}

        cursor.execute('SELECT COUNT(*) FROM items')
        total_items = cursor.fetchone()[0]

        return {{
            'total_projects': total_projects,
            'by_status': by_status,
            'total_items': total_items
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
            r'(追加|add|作成|create|start)\\s*(.+)',
            r'(始めた|started|始める|開始)\\s*(.+)'
        ]

        for pattern in add_patterns:
            match = re.search(pattern, content)
            if match:
                title = match.group(2).strip()
                if len(title) > 2:
                    project_id = self.db.add_project(title=title)
                    await message.reply(f'プロジェクトを追加しました: {{title}} (ID: {{project_id}})')
                    return

        list_patterns = [
            r'(一覧|list|全|all|what|show)',
            r'(見てる|進行中|doing|working on)'
        ]

        for pattern in list_patterns:
            if re.search(pattern, content):
                projects = self.db.list_projects()
                if projects:
                    response = "**プロジェクト一覧**:\\n"
                    for i, project in enumerate(projects[:10], 1):
                        status_emoji = {{'planned': '📋', 'in_progress': '🔨', 'completed': '✅'}}
                        emoji = status_emoji.get(project['status'], '📌')
                        response += f"{{i}}. {{emoji}} {{project['title']}}\\n"
                else:
                    response = "プロジェクトがまだありません。"
                await message.reply(response)
                return

    @commands.command()
    async def add(self, ctx, *, title: str):
        project_id = self.db.add_project(title=title)
        await ctx.send(f'追加しました: {{title}} (ID: {{project_id}})')

    @commands.command()
    async def list(self, ctx, status: Optional[str] = None):
        projects = self.db.list_projects(status=status)
        if not projects:
            await ctx.send("プロジェクトがまだありません。")
            return

        response = "**プロジェクト一覧**:\\n"
        for i, project in enumerate(projects[:10], 1):
            status_emoji = {{'planned': '📋', 'in_progress': '🔨', 'completed': '✅'}}
            emoji = status_emoji.get(project['status'], '📌')
            response += f"{{i}}. {{emoji}} {{project['title']}}\\n"
        await ctx.send(response)

    @commands.command()
    async def update(self, ctx, project_id: int, **kwargs):
        success = self.db.update_project(project_id, **kwargs)
        if success:
            await ctx.send(f"ID {{project_id}} を更新しました。")
        else:
            await ctx.send(f"ID {{project_id}} が見つかりません。")

    @commands.command()
    async def stats(self, ctx):
        stats = self.db.get_statistics()
        response = "**統計**\\n"
        response += f"- プロジェクト: {{stats['total_projects']}}\\n"
        response += f"- アイテム: {{stats['total_items']}}\\n"
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

- プロジェクトの計画と追跡 (Project planning and tracking)
- アイテム・材料の管理 (Item and material management)
- ログ・記録の保存 (Log and record keeping)
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

# プロジェクト追加 (Add project)
project_id = db.add_project(
    title="Example Project",
    description="Description",
    category="category"
)

# 一覧 (List)
projects = db.list_projects()

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
