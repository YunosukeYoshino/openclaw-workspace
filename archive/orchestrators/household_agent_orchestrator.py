#!/usr/bin/env python3
"""
家事・生活エージェントオーケストレーター
Household & Living Agents Orchestrator

家事や日常生活をサポートするエージェントを自律的に作成する
Creates household and daily life support agents.
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

PROJECT_CONFIG = {
    "name": "家事・生活エージェントプロジェクト",
    "name_en": "Household & Living Agents Project",
    "version": "1.0.0",
    "created": datetime.now().isoformat()
}

AGENTS = [
    {
        "name": "household-chores-agent",
        "name_ja": "家事エージェント",
        "description": "家事タスクの管理・スケジュール・リマインダー",
        "description_en": "Household chores management, scheduling, and reminders"
    },
    {
        "name": "shopping-agent",
        "name_ja": "ショッピングエージェント",
        "description": "買い物リスト管理・在庫管理",
        "description_en": "Shopping list management and inventory tracking"
    },
    {
        "name": "meal-planning-agent",
        "name_ja": "献立計画エージェント",
        "description": "週間献立の計画・レシピ管理・買い物リスト生成",
        "description_en": "Weekly meal planning, recipe management, and shopping list generation"
    },
    {
        "name": "bill-tracking-agent",
        "name_ja": "請求管理エージェント",
        "description": "請求書・支払いの管理・リマインダー",
        "description_en": "Bill and payment management and reminders"
    },
    {
        "name": "budget-agent",
        "name_ja": "家計エージェント",
        "description": "家計の収入・支出管理・予算追跡",
        "description_en": "Household income, expense, and budget tracking"
    },
    {
        "name": "home-maintenance-agent",
        "name_ja": "ホームメンテナンスエージェント",
        "description": "家のメンテナンス・修理の計画・記録",
        "description_en": "Home maintenance and repair planning and recording"
    },
    {
        "name": "appointment-agent",
        "name_ja": "アポイントエージェント",
        "description": "予約・約束の管理・リマインダー",
        "description_en": "Appointment and commitment management and reminders"
    },
    {
        "name": "weather-reminder-agent",
        "name_ja": "天気リマインダーエージェント",
        "description": "天気予報に基づいた行動リマインダー",
        "description_en": "Weather-based activity reminders and suggestions"
    },
]

PROGRESS_FILE = "/workspace/household_agent_progress.json"


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
            "CREATE TABLE IF NOT EXISTS chores ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "title TEXT NOT NULL,"
            "description TEXT,"
            "category TEXT,"
            "frequency TEXT DEFAULT 'once',"
            "priority INTEGER DEFAULT 0,"
            "status TEXT DEFAULT 'pending',"
            "due_date TEXT,"
            "completed_date TEXT,"
            "assigned_to TEXT,"
            "notes TEXT,"
            "created_at TEXT DEFAULT CURRENT_TIMESTAMP,"
            "updated_at TEXT DEFAULT CURRENT_TIMESTAMP"
            ")"
        )

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS shopping_items ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "name TEXT NOT NULL,"
            "category TEXT,"
            "quantity INTEGER DEFAULT 1,"
            "unit TEXT,"
            "priority INTEGER DEFAULT 0,"
            "status TEXT DEFAULT 'needed',"
            "estimated_price REAL,"
            "notes TEXT,"
            "created_at TEXT DEFAULT CURRENT_TIMESTAMP"
            ")"
        )

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS bills ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "name TEXT NOT NULL,"
            "category TEXT,"
            "amount REAL NOT NULL,"
            "due_date TEXT NOT NULL,"
            "status TEXT DEFAULT 'pending',"
            "paid_date TEXT,"
            "payment_method TEXT,"
            "notes TEXT,"
            "created_at TEXT DEFAULT CURRENT_TIMESTAMP"
            ")"
        )

        self.conn.commit()

    def add_chore(self, title: str, description: str = None,
                  category: str = None, frequency: str = 'once',
                  priority: int = 0, due_date: str = None,
                  assigned_to: str = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO chores (title, description, category, frequency, priority, due_date, assigned_to) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (title, description, category, frequency, priority, due_date, assigned_to)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_chore(self, chore_id: int) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM chores WHERE id = ?', (chore_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def list_chores(self, status: str = None,
                    category: str = None) -> List[Dict]:
        cursor = self.conn.cursor()
        query = 'SELECT * FROM chores WHERE 1=1'
        params = []

        if status:
            query += ' AND status = ?'
            params.append(status)

        if category:
            query += ' AND category = ?'
            params.append(category)

        query += ' ORDER BY priority DESC, due_date ASC'
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def update_chore(self, chore_id: int, **kwargs) -> bool:
        valid_fields = ['title', 'description', 'category', 'frequency',
                       'priority', 'status', 'due_date', 'completed_date',
                       'assigned_to', 'notes']
        update_fields = {{k: v for k, v in kwargs.items() if k in valid_fields}}

        if not update_fields:
            return False

        update_fields['updated_at'] = datetime.now().isoformat()
        set_clause = ', '.join([f'{{k}} = ?' for k in update_fields.keys()])
        values = list(update_fields.values()) + [chore_id]

        cursor = self.conn.cursor()
        cursor.execute(
            f"UPDATE chores SET {{set_clause}} WHERE id = ?",
            values
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def add_shopping_item(self, name: str, category: str = None,
                         quantity: int = 1, unit: str = None,
                         priority: int = 0, estimated_price: float = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO shopping_items (name, category, quantity, unit, priority, estimated_price) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (name, category, quantity, unit, priority, estimated_price)
        )
        self.conn.commit()
        return cursor.lastrowid

    def list_shopping_items(self, status: str = None,
                            category: str = None) -> List[Dict]:
        cursor = self.conn.cursor()
        query = 'SELECT * FROM shopping_items WHERE 1=1'
        params = []

        if status:
            query += ' AND status = ?'
            params.append(status)

        if category:
            query += ' AND category = ?'
            params.append(category)

        query += ' ORDER BY priority DESC, created_at ASC'
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def add_bill(self, name: str, amount: float, due_date: str,
                 category: str = None, payment_method: str = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO bills (name, category, amount, due_date, payment_method) "
            "VALUES (?, ?, ?, ?, ?)",
            (name, category, amount, due_date, payment_method)
        )
        self.conn.commit()
        return cursor.lastrowid

    def list_bills(self, status: str = None) -> List[Dict]:
        cursor = self.conn.cursor()
        query = 'SELECT * FROM bills WHERE 1=1'
        params = []

        if status:
            query += ' AND status = ?'
            params.append(status)

        query += ' ORDER BY due_date ASC'
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def get_statistics(self) -> Dict:
        cursor = self.conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM chores WHERE status = "pending"')
        pending_chores = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM shopping_items WHERE status = "needed"')
        needed_items = cursor.fetchone()[0]

        cursor.execute('SELECT SUM(amount) FROM bills WHERE status = "pending"')
        pending_bills = cursor.fetchone()[0] or 0

        return {{
            'pending_chores': pending_chores,
            'needed_shopping_items': needed_items,
            'pending_bill_amount': round(pending_bills, 2)
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
            r'(家事|chore|追加|add|やる|do)\\s*(.+)',
            r'(掃除|cleaning|洗濯|laundry)\\s*(.+)'
        ]

        for pattern in add_patterns:
            match = re.search(pattern, content)
            if match:
                title = match.group(2).strip()
                if len(title) > 2:
                    chore_id = self.db.add_chore(title=title)
                    await message.reply(f'家事を追加しました: {{title}} (ID: {{chore_id}})')
                    return

        list_patterns = [
            r'(一覧|list|全|all|what|show)',
            r'(家事|chores|やること|todo)'
        ]

        for pattern in list_patterns:
            if re.search(pattern, content):
                chores = self.db.list_chores(status='pending')
                if chores:
                    response = "**家事一覧**:\\n"
                    for i, chore in enumerate(chores[:10], 1):
                        priority_emoji = {{3: '🔴', 2: '🟡', 1: '🟢'}}
                        emoji = priority_emoji.get(chore['priority'], '⚪')
                        response += f"{{i}}. {{emoji}} {{chore['title']}}\\n"
                else:
                    response = "家事がまだありません。"
                await message.reply(response)
                return

    @commands.command()
    async def add(self, ctx, *, title: str):
        chore_id = self.db.add_chore(title=title)
        await ctx.send(f'追加しました: {{title}} (ID: {{chore_id}})')

    @commands.command()
    async def list(self, ctx, status: Optional[str] = None):
        chores = self.db.list_chores(status=status)
        if not chores:
            await ctx.send("家事がまだありません。")
            return

        response = "**家事一覧**:\\n"
        for i, chore in enumerate(chores[:10], 1):
            priority_emoji = {{3: '🔴', 2: '🟡', 1: '🟢'}}
            emoji = priority_emoji.get(chore['priority'], '⚪')
            response += f"{{i}}. {{emoji}} {{chore['title']}}\\n"
        await ctx.send(response)

    @commands.command()
    async def done(self, ctx, chore_id: int):
        from datetime import datetime
        success = self.db.update_chore(chore_id, status='completed', completed_date=datetime.now().isoformat())
        if success:
            await ctx.send(f"ID {{chore_id}} を完了にしました。")
        else:
            await ctx.send(f"ID {{chore_id}} が見つかりません。")

    @commands.command()
    async def delete(self, ctx, chore_id: int):
        success = self.db.delete_chore(chore_id)
        if success:
            await ctx.send(f"ID {{chore_id}} を削除しました。")
        else:
            await ctx.send(f"ID {{chore_id}} が見つかりません。")

    @commands.command()
    async def stats(self, ctx):
        stats = self.db.get_statistics()
        response = "**統計**\\n"
        response += f"- 未完了家事: {{stats['pending_chores']}}\\n"
        response += f"- 必要な買い物: {{stats['needed_shopping_items']}}\\n"
        response += f"- 未払い請求: {{stats['pending_bill_amount']}}円\\n"
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

- 家事タスク管理 (Household chore management)
- ショッピングリスト管理 (Shopping list management)
- 請求管理・リマインダー (Bill management and reminders)
- 予算・支出追跡 (Budget and expense tracking)
- スケジュール管理 (Schedule management)
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

# 家事追加 (Add chore)
chore_id = db.add_chore(
    title="掃除",
    category="cleaning",
    priority=2
)

# 一覧 (List)
chores = db.list_chores(status='pending')

# 完了 (Complete)
db.update_chore(chore_id, status='completed')

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
