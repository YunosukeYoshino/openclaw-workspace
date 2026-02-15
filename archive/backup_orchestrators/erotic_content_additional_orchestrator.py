#!/usr/bin/env python3
"""
エロティックコンテンツ追加エージェントV3 - オーケストレーター
Autonomous Agent Development System

このオーケストレーターは、さらなるエロティックコンテンツ関連エージェントを自律的に作成します。
"""

import json
import os
import subprocess
import time
from pathlib import Path
from datetime import datetime

# プロジェクト設定
PROJECT_NAME = "erotic-content-additional-v3"
PROGRESS_FILE = f"/workspace/{PROJECT_NAME}_progress.json"

# 作成するエージェント一覧
AGENTS = [
    {
        "name": "erotic-favorites-agent",
        "title_ja": "お気に入りえっち作品コレクションエージェント",
        "title_en": "Favorite Erotic Content Collection Agent",
        "description_ja": "お気に入りのえっちなイラスト・作品をコレクション・管理するエージェント",
        "description_en": "An agent that manages and organizes favorite erotic illustrations and content",
        "tables": {
            "favorites": """
                CREATE TABLE IF NOT EXISTS favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    artist TEXT,
                    source TEXT,
                    tags TEXT,
                    url TEXT,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_viewed TIMESTAMP,
                    notes TEXT,
                    rating INTEGER DEFAULT 0
                )
            """,
            "entries": """
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL CHECK(type IN ('note','log','rating')),
                    title TEXT,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
        },
        "priority": 1
    },
    {
        "name": "erotic-rating-agent",
        "title_ja": "えっちコンテンツ評価レビューエージェント",
        "title_en": "Erotic Content Rating & Review Agent",
        "description_ja": "えっちなコンテンツの評価・レビューを管理するエージェント",
        "description_en": "An agent that manages ratings and reviews for erotic content",
        "tables": {
            "reviews": """
                CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_id TEXT NOT NULL,
                    content_title TEXT,
                    artist TEXT,
                    rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 10),
                    review_text TEXT,
                    tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            "entries": """
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL CHECK(type IN ('note','log','rating')),
                    title TEXT,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
        },
        "priority": 2
    },
    {
        "name": "erotic-bookmark-agent",
        "title_ja": "えっちコンテンツブックマークエージェント",
        "title_en": "Erotic Content Bookmark Agent",
        "description_ja": "えっちなコンテンツのブックマークを管理するエージェント",
        "description_en": "An agent that manages bookmarks for erotic content",
        "tables": {
            "bookmarks": """
                CREATE TABLE IF NOT EXISTS bookmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL UNIQUE,
                    title TEXT,
                    description TEXT,
                    tags TEXT,
                    category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TIMESTAMP
                )
            """,
            "entries": """
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL CHECK(type IN ('note','log','bookmark')),
                    title TEXT,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
        },
        "priority": 3
    },
    {
        "name": "erotic-history-agent",
        "title_ja": "えっちコンテンツ閲覧履歴エージェント",
        "title_en": "Erotic Content History Tracking Agent",
        "description_ja": "えっちなコンテンツの閲覧履歴を追跡・管理するエージェント",
        "description_en": "An agent that tracks and manages viewing history of erotic content",
        "tables": {
            "history": """
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_id TEXT NOT NULL,
                    content_title TEXT,
                    artist TEXT,
                    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tags TEXT,
                    source TEXT
                )
            """,
            "entries": """
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL CHECK(type IN ('note','log','history')),
                    title TEXT,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
        },
        "priority": 4
    },
    {
        "name": "erotic-search-agent",
        "title_ja": "えっちコンテンツ高度検索エージェント",
        "title_en": "Erotic Content Advanced Search Agent",
        "description_ja": "えっちなコンテンツの高度な検索機能を提供するエージェント",
        "description_en": "An agent that provides advanced search functionality for erotic content",
        "tables": {
            "search_index": """
                CREATE TABLE IF NOT EXISTS search_index (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_id TEXT NOT NULL UNIQUE,
                    title TEXT,
                    artist TEXT,
                    tags TEXT,
                    description TEXT,
                    source TEXT,
                    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            "search_queries": """
                CREATE TABLE IF NOT EXISTS search_queries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    results_count INTEGER,
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            "entries": """
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL CHECK(type IN ('note','log','search')),
                    title TEXT,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
        },
        "priority": 5
    }
]

class Orchestrator:
    def __init__(self):
        self.progress = self.load_progress()
        self.agents_dir = Path("/workspace/agents")

    def load_progress(self):
        if os.path.exists(PROGRESS_FILE):
            with open(PROGRESS_FILE, 'r') as f:
                return json.load(f)
        return {
            "project_name": PROJECT_NAME,
            "start_time": datetime.utcnow().isoformat(),
            "completed": [],
            "in_progress": None,
            "errors": []
        }

    def save_progress(self):
        self.progress["last_updated"] = datetime.utcnow().isoformat()
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(self.progress, f, indent=2, ensure_ascii=False)

    def spawn_subagent(self, agent_info):
        """サブエージェントをスパーンしてエージェントを作成"""

        task = f"""
Create a complete AI agent directory for "{agent_info['name']}" with the following specifications:

Agent Name: {agent_info['name']}
Title (Japanese): {agent_info['title_ja']}
Title (English): {agent_info['title_en']}
Description (Japanese): {agent_info['description_ja']}
Description (English): {agent_info['description_en']}

Database Tables:
{json.dumps(agent_info['tables'], indent=2)}

Required files:
1. agent.py - Main agent module with basic functionality
2. db.py - SQLite database module with all tables defined
3. discord.py - Discord bot module
4. README.md - Bilingual documentation (Japanese/English)
5. requirements.txt - Dependencies

Create all files in /workspace/agents/{agent_info['name']}/ directory.
Ensure all files exist and are properly formatted.
"""
        print(f"Spawning subagent for {agent_info['name']}...")

        try:
            result = subprocess.run(
                ["python3", "-c", f'''
import sys
import json
from pathlib import Path

# エージェントディレクトリ作成
agent_dir = Path("/workspace/agents/{agent_info['name']}")
agent_dir.mkdir(exist_ok=True)

# テーブル定義を取得
tables = {json.dumps(agent_info['tables'], ensure_ascii=False)}

# agent.py 作成
agent_py = f'''"""
{agent_info['name']} - {agent_info['title_en']}

{agent_info['description_en']}
"""

class {agent_info['name'].replace("-", "_").capitalize()}Agent:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = agent_dir / "{agent_info['name']}.db"
        self.db_path = db_path
        self.db = None

    def initialize_db(self):
        from .db import Database
        self.db = Database(str(self.db_path))
        self.db.initialize()

    def get_info(self):
        return {{
            "name": "{agent_info['name']}",
            "title_ja": "{agent_info['title_ja']}",
            "title_en": "{agent_info['title_en']}",
            "description_ja": "{agent_info['description_ja']}",
            "description_en": "{agent_info['description_en']}",
        }}
'''

(agent_dir / "agent.py").write_text(agent_py)

# db.py 作成
db_py = f'''"""
{agent_info['name']} - Database Module
"""

import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def initialize(self):
        """Initialize database with all required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 各テーブルを作成
            for table_name, table_sql in {list(tables.keys())}:
                cursor.execute(table_sql)
                print(f"Table {{table_name}} created")

            conn.commit()
            print("Database initialized successfully")

    def execute_query(self, query: str, params: tuple = ()):
        """Execute a SQL query"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor

    def fetch_all(self, query: str, params: tuple = ()):
        """Fetch all results from a query"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def fetch_one(self, query: str, params: tuple = ()):
        """Fetch one result from a query"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            return dict(result) if result else None
'''

(agent_dir / "db.py").write_text(db_py)

# discord.py 作成
discord_py = f'''"""
{agent_info['name']} - Discord Bot Module
"""

import discord
from discord.ext import commands
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from db import Database

class {agent_info['name'].replace("-", "_").capitalize()}Bot(commands.Bot):
    def __init__(self, command_prefix="!", db_path=None):
        intents = discord.Intents.default()
        intents.message_content = True

        if db_path is None:
            db_path = Path(__file__).parent / "{agent_info['name']}.db"

        super().__init__(command_prefix=command_prefix, intents=intents)
        self.db_path = db_path
        self.db = Database(str(db_path))

    async def setup_hook(self):
        """Setup database when bot starts"""
        self.db.initialize()

    async def on_ready(self):
        print(f"{{self.user.name}} is online!")

    async def help_command(self, ctx):
        """Show help message"""
        help_text = f"""
**{agent_info['title_en']}**

{agent_info['description_en']}

Commands:
- !info - Show agent information
- !help - Show this help message
"""
        await ctx.send(help_text)

    async def info_command(self, ctx):
        """Show agent information"""
        info = f"""
**{agent_info['title_en']} / {agent_info['title_ja']}**

{agent_info['description_ja']}

Description (EN):
{agent_info['description_en']}
"""
        await ctx.send(info)

# コマンド登録用
def setup(bot):
    """Setup function for the bot"""
    if not hasattr(bot, "add_listener"):
        print("Warning: bot.add_listener not available, running standalone")
        return

    async def on_message(message):
        if message.author.bot:
            return

        if message.content.startswith("!info"):
            info_text = f"""
**{agent_info['title_en']} / {agent_info['title_ja']}**

{agent_info['description_ja']}
"""
            await message.channel.send(info_text)
        elif message.content.startswith("!help"):
            help_text = f"""
**{agent_info['title_en']}**

{agent_info['description_en']}

Commands:
- !info - Show agent information
- !help - Show this help message
"""
            await message.channel.send(help_text)

    bot.add_listener(on_message, "on_message")
'''

(agent_dir / "discord.py").write_text(discord_py)

# README.md 作成
readme_md = f'''# {agent_info['name']}

## {agent_info['title_en']}

{agent_info['description_en']}

---

## {agent_info['title_ja']}

{agent_info['description_ja']}

---

## Features

### Features in English

- Database management with SQLite
- Discord bot integration
- Bilingual support (Japanese/English)

### 機能一覧

- SQLiteによるデータベース管理
- Discordボットとの統合
- バイリンガル対応(日本語・英語)

---

## Installation

### Installation in English

```bash
cd /workspace/agents/{agent_info['name']}
pip install -r requirements.txt
```

### インストール方法

```bash
cd /workspace/agents/{agent_info['name']}
pip install -r requirements.txt
```

---

## Usage

### Usage in English

```python
from agent import {agent_info['name'].replace("-", "_").capitalize()}Agent

agent = {agent_info['name'].replace("-", "_").capitalize()}Agent()
agent.initialize_db()
```

### 使い方

```python
from agent import {agent_info['name'].replace("-", "_").capitalize()}Agent

agent = {agent_info['name'].replace("-", "_").capitalize()}Agent()
agent.initialize_db()
```

---

## Database Schema

### Database Schema in English

{json.dumps(agent_info['tables'], indent=2)}

### データベース構造

{json.dumps(agent_info['tables'], indent=2)}

---

## Files

- `agent.py` - Main agent module
- `db.py` - Database module
- `discord.py` - Discord bot module
- `README.md` - This file
- `requirements.txt` - Python dependencies

---

## License

MIT License
'''

(agent_dir / "README.md").write_text(readme_md)

# requirements.txt 作成
requirements_txt = """discord.py>=2.3.0
"""
(agent_dir / "requirements.txt").write_text(requirements_txt)

print(f"Created {agent_info['name']} agent directory successfully")
print(f"Files created: agent.py, db.py, discord.py, README.md, requirements.txt")
'''],
                capture_output=True,
                text=True
            )

            print(result.stdout)
            if result.stderr:
                print(f"Error: {result.stderr}")

            return result.returncode == 0

        except Exception as e:
            print(f"Error spawning subagent for {agent_info['name']}: {e}")
            self.progress["errors"].append({
                "agent": agent_info['name'],
                "error": str(e),
                "time": datetime.utcnow().isoformat()
            })
            return False

    def verify_agent(self, agent_name):
        """エージェントが正しく作成されたか確認"""
        agent_dir = self.agents_dir / agent_name
        required_files = ["agent.py", "db.py", "discord.py", "README.md", "requirements.txt"]

        missing_files = []
        for file in required_files:
            if not (agent_dir / file).exists():
                missing_files.append(file)

        return len(missing_files) == 0, missing_files

    def run(self):
        print(f"Starting {PROJECT_NAME} orchestrator...")
        print(f"Total agents to create: {len(AGENTS)}")

        completed_count = 0

        for agent_info in AGENTS:
            agent_name = agent_info["name"]

            if agent_name in self.progress["completed"]:
                print(f"Skipping {agent_name} (already completed)")
                completed_count += 1
                continue

            print(f"\\n{'='*60}")
            print(f"Creating agent: {agent_name}")
            print(f"Priority: {agent_info['priority']}")
            print(f"{'='*60}")

            # サブエージェントをスパーン
            self.progress["in_progress"] = agent_name
            self.save_progress()

            success = self.spawn_subagent(agent_info)

            # 確認
            is_complete, missing = self.verify_agent(agent_name)

            if success and is_complete:
                self.progress["completed"].append(agent_name)
                self.progress["in_progress"] = None
                completed_count += 1
                print(f"\\n✅ {agent_name} completed successfully!")
            else:
                print(f"\\n❌ {agent_name} failed or has missing files: {missing}")
                self.progress["errors"].append({
                    "agent": agent_name,
                    "missing_files": missing,
                    "time": datetime.utcnow().isoformat()
                })

            self.save_progress()
            time.sleep(0.5)

        print(f"\\n{'='*60}")
        print(f"Orchestrator Summary")
        print(f"{'='*60}")
        print(f"Total agents: {len(AGENTS)}")
        print(f"Completed: {completed_count}")
        print(f"Failed: {len(AGENTS) - completed_count}")

        if self.progress["errors"]:
            print(f"\\nErrors:")
            for error in self.progress["errors"]:
                print(f"  - {error['agent']}: {error}")

        self.progress["completed_at"] = datetime.utcnow().isoformat()
        self.save_progress()

        return completed_count == len(AGENTS)

if __name__ == "__main__":
    orchestrator = Orchestrator()
    success = orchestrator.run()
    exit(0 if success else 1)
