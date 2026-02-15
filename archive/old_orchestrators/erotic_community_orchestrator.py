#!/usr/bin/env python3
"""
Erotic Content Community Engagement Orchestrator
えっちコンテンツコミュニティエンゲージメントオーケストレーター

自律的にえっちコンテンツコミュニティエンゲージメントエージェントを開発するオーケストレーター
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path

# エージェント定義
AGENTS = [
    {
        "id": "erotic-fan-club-agent",
        "name_ja": "えっちファンクラブエージェント",
        "name_en": "Erotic Fan Club Agent",
        "description_ja": "お気に入りクリエイター・作品のファンクラブ管理、専用のニュース、リリース、イベント情報の提供、ファン投票、リクエスト機能、限定コンテンツへのアクセス",
        "description_en": "Fan club management for favorite creators/content, dedicated news, releases, event info, fan voting, request features, exclusive content access",
        "features": [
            "Fan Club Management",
            "News & Releases",
            "Event Information",
            "Fan Voting",
            "Request System",
            "Exclusive Content"
        ],
        "tech_stack": ["discord.py", "requests", "beautifulsoup4", "pandas", "numpy"]
    },
    {
        "id": "erotic-collection-showcase-agent",
        "name_ja": "えっちコレクションショーケースエージェント",
        "name_en": "Erotic Collection Showcase Agent",
        "description_ja": "コレクションの自動カタログ化、ギャラリー表示、テーマ別、スタイル別、タグ別での整理、シェア機能、プレビュー、コレクション比較",
        "description_en": "Auto-catalog collections, gallery display, organize by theme, style, tags, sharing features, preview, collection comparison",
        "features": [
            "Auto Catalog",
            "Gallery Display",
            "Smart Organization",
            "Sharing Features",
            "Preview System",
            "Collection Comparison"
        ],
        "tech_stack": ["Pillow", "scikit-image", "Pillow", "pandas", "numpy"]
    },
    {
        "id": "erotic-event-planner-agent",
        "name_ja": "えっちイベントプランナーエージェント",
        "name_en": "Erotic Event Planner Agent",
        "description_ja": "コミュニティイベント、チャレンジ、コンテストの企画・管理、参加者登録、投票、結果発表の自動化、タイムライン、通知、報酬システムの統合",
        "description_en": "Plan and manage community events, challenges, contests, auto participant registration, voting, result announcements, timeline, notifications, reward system integration",
        "features": [
            "Event Planning",
            "Participant Management",
            "Voting System",
            "Auto Announcements",
            "Timeline Management",
            "Reward System"
        ],
        "tech_stack": ["discord.py", "pandas", "icalendar", "pytz", "requests"]
    },
    {
        "id": "erotic-collaboration-agent",
        "name_ja": "えっちコラボレーションエージェント",
        "name_en": "Erotic Collaboration Agent",
        "description_ja": "クリエイター間のコラボ企画の提案・管理、リクエストマッチング、プロジェクト進捗管理、作品の共同作成、リリース、プロモーション",
        "description_en": "Propose and manage creator collab projects, request matching, project progress tracking, collaborative creation, releases, promotions",
        "features": [
            "Collab Proposal",
            "Request Matching",
            "Progress Tracking",
            "Co-creation Tools",
            "Release Management",
            "Promotion"
        ],
        "tech_stack": ["discord.py", "requests", "pandas", "gitpython", "yaml"]
    },
    {
        "id": "erotic-feedback-hub-agent",
        "name_ja": "えっちフィードバックハブエージェント",
        "name_en": "Erotic Feedback Hub Agent",
        "description_ja": "ファンからのフィードバック、リクエストの収集・整理、クリエイターへの定期的なフィードバックレポート、トレンド分析、人気投票、改善提案の集約",
        "description_en": "Collect and organize fan feedback and requests, periodic feedback reports to creators, trend analysis, popularity voting, improvement suggestion aggregation",
        "features": [
            "Feedback Collection",
            "Request Organization",
            "Creator Reports",
            "Trend Analysis",
            "Popularity Voting",
            "Improvement Suggestions"
        ],
        "tech_stack": ["pandas", "scikit-learn", "numpy", "discord.py", "requests"]
    }
]

# プロジェクト設定
PROJECT_NAME = "Erotic Content Community Engagement"
PROJECT_NAME_JA = "えっちコンテンツコミュニティエンゲージメント"
PROJECT_DIR = "/workspace"
PROGRESS_FILE = "/workspace/erotic_community_progress.json"


def load_progress():
    """進捗を読み込む"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "project": PROJECT_NAME,
        "started_at": datetime.utcnow().isoformat(),
        "agents": {},
        "total_agents": len(AGENTS),
        "completed_agents": 0
    }


def save_progress(progress):
    """進捗を保存する"""
    progress["updated_at"] = datetime.utcnow().isoformat()
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)


def create_agent_directory(agent):
    """エージェントディレクトリを作成"""
    agent_dir = f"{PROJECT_DIR}/agents/{agent['id']}"
    os.makedirs(agent_dir, exist_ok=True)
    return agent_dir


def generate_agent_py(agent):
    """agent.py を生成"""
    template = '''#!/usr/bin/env python3
"""
__NAME_JA__ / __NAME_EN__
__AGENT_ID__

__DESCRIPTION_JA__
__DESCRIPTION_EN__
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from .db import Database
from .discord import DiscordBot

logger = logging.getLogger(__name__)


class __CLASS_NAME__:
    """__NAME_JA__"""

    def __init__(self, db: Database, discord: Optional[DiscordBot] = None):
        self.db = db
        self.discord = discord
        self.agent_id = "__AGENT_ID__"

    async def initialize(self):
        """初期化処理"""
        logger.info(f"Initializing {self.agent_id}...")
        await self.db.initialize()

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        メイン処理

        Args:
            data: 入力データ

        Returns:
            処理結果
        """
        try:
            result = {"status": "success", "data": data}
            return result
        except Exception as e:
            logger.error(f"Error in {self.agent_id}: {e}")
            return {"status": "error", "message": str(e)}

    async def get_status(self) -> Dict[str, Any]:
        """ステータス取得"""
        return {
            "agent_id": self.agent_id,
            "status": "active",
            "timestamp": datetime.utcnow().isoformat()
        }

    async def cleanup(self):
        """クリーンアップ"""
        logger.info(f"Cleaning up {self.agent_id}...")
'''
    class_name = snake_to_camel(agent['id'])
    template = template.replace("__AGENT_ID__", agent['id'])
    template = template.replace("__NAME_JA__", agent['name_ja'])
    template = template.replace("__NAME_EN__", agent['name_en'])
    template = template.replace("__DESCRIPTION_JA__", agent['description_ja'])
    template = template.replace("__DESCRIPTION_EN__", agent['description_en'])
    template = template.replace("__CLASS_NAME__", class_name)
    return template


def generate_db_py(agent):
    """db.py を生成"""
    template = '''#!/usr/bin/env python3
"""
Database for __NAME_JA__ / __NAME_EN__
"""

import sqlite3
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class Database:
    """Database for __AGENT_ID__"""

    def __init__(self, db_path: str = "data/__AGENT_ID__.db"):
        self.db_path = Path(db_path)
        self.conn: Optional[sqlite3.Connection] = None

    async def initialize(self):
        """Initialize database and create tables"""
        self.conn = sqlite3.connect(self.db_path)
        self._create_tables()
        logger.info(f"Database initialized: {self.db_path}")

    def _create_tables(self):
        """Create database tables"""
        cursor = self.conn.cursor()

        # Main entries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tags table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Entry tags relation table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entry_tags (
                entry_id INTEGER,
                tag_id INTEGER,
                PRIMARY KEY (entry_id, tag_id),
                FOREIGN KEY (entry_id) REFERENCES entries(id),
                FOREIGN KEY (tag_id) REFERENCES tags(id)
            )
        """)

        self.conn.commit()

    async def create_entry(self, title: str, content: str, category: str = None, tags: List[str] = None) -> int:
        """Create a new entry"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO entries (title, content, category, tags)
            VALUES (?, ?, ?, ?)
        """, (title, content, category, ','.join(tags or [])))
        self.conn.commit()
        entry_id = cursor.lastrowid

        if tags:
            for tag in tags:
                await self._add_tag_to_entry(entry_id, tag)

        return entry_id

    async def _add_tag_to_entry(self, entry_id: int, tag_name: str):
        """Add a tag to an entry"""
        cursor = self.conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO tags (name) VALUES (?)', (tag_name,))
        self.conn.commit()
        cursor.execute('SELECT id FROM tags WHERE name = ?', (tag_name,))
        tag_id = cursor.fetchone()[0]
        cursor.execute('INSERT OR IGNORE INTO entry_tags (entry_id, tag_id) VALUES (?, ?)',
                      (entry_id, tag_id))
        self.conn.commit()

    async def get_entry(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """Get an entry by ID"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM entries WHERE id = ?', (entry_id,))
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0], "title": row[1], "content": row[2],
                "category": row[3], "tags": row[4].split(',') if row[4] else [],
                "created_at": row[5], "updated_at": row[6]
            }
        return None

    async def list_entries(self, category: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """List entries"""
        cursor = self.conn.cursor()
        if category:
            cursor.execute('SELECT * FROM entries WHERE category = ? ORDER BY created_at DESC LIMIT ?',
                          (category, limit))
        else:
            cursor.execute('SELECT * FROM entries ORDER BY created_at DESC LIMIT ?', (limit,))
        rows = cursor.fetchall()
        return [{
            "id": row[0], "title": row[1], "content": row[2],
            "category": row[3], "tags": row[4].split(',') if row[4] else [],
            "created_at": row[5], "updated_at": row[6]
        } for row in rows]

    async def search_entries(self, query: str) -> List[Dict[str, Any]]:
        """Search entries"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM entries WHERE title LIKE ? OR content LIKE ? ORDER BY created_at DESC
        """, (f'%{query}%', f'%{query}%'))
        rows = cursor.fetchall()
        return [{
            "id": row[0], "title": row[1], "content": row[2],
            "category": row[3], "tags": row[4].split(',') if row[4] else [],
            "created_at": row[5], "updated_at": row[6]
        } for row in rows]

    async def update_entry(self, entry_id: int, title: str = None, content: str = None,
                          category: str = None, tags: List[str] = None) -> bool:
        """Update an entry"""
        cursor = self.conn.cursor()
        updates = []
        values = []

        if title:
            updates.append("title = ?")
            values.append(title)
        if content:
            updates.append("content = ?")
            values.append(content)
        if category:
            updates.append("category = ?")
            values.append(category)
        if tags is not None:
            updates.append("tags = ?")
            values.append(','.join(tags))

        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            values.append(entry_id)
            cursor.execute(f"UPDATE entries SET {', '.join(updates)} WHERE id = ?", values)
            self.conn.commit()
            return cursor.rowcount > 0
        return False

    async def delete_entry(self, entry_id: int) -> bool:
        """Delete an entry"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM entry_tags WHERE entry_id = ?', (entry_id,))
        cursor.execute('DELETE FROM entries WHERE id = ?', (entry_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
'''
    template = template.replace("__AGENT_ID__", agent['id'])
    template = template.replace("__NAME_JA__", agent['name_ja'])
    template = template.replace("__NAME_EN__", agent['name_en'])
    return template


def generate_discord_py(agent):
    """discord.py を生成"""
    features_list = '\n'.join([f'            - {f}' for f in agent['features']])
    template = '''#!/usr/bin/env python3
"""
Discord Bot Integration for __NAME_JA__ / __NAME_EN__
"""

import discord
from discord.ext import commands
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class DiscordBot(commands.Bot):
    """Discord Bot for __AGENT_ID__"""

    def __init__(self, command_prefix: str = "!", db=None):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.db = db
        self.agent_id = "__AGENT_ID__"

    async def setup_hook(self):
        """Bot setup"""
        logger.info(f"Setting up {self.agent_id} Discord bot...")
        await self.add_cog(__CLASS_NAME__Commands(self))

    async def on_ready(self):
        """Bot is ready"""
        logger.info(f"{self.user.name} is ready!")


class __CLASS_NAME__Commands(commands.Cog):
    """Commands for __AGENT_ID__"""

    def __init__(self, bot: DiscordBot):
        self.bot = bot

    @commands.command(name="status")
    async def status(self, ctx: commands.Context):
        """Check agent status"""
        await ctx.send(f"✅ {self.bot.agent_id} is active!")

    @commands.command(name="help")
    async def help_command(self, ctx: commands.Context):
        """Show help"""
        help_text = f"""
📚 **__NAME_JA__ Help**

**Features:**
__FEATURES_LIST__

**Commands:**
- `!status` - Check agent status
- `!help` - Show this help message
- `!create <title> <content>` - Create new entry
- `!list [category]` - List entries
- `!search <query>` - Search entries
- `!get <id>` - Get entry by ID
"""
        help_text = help_text.replace("__AGENT_ID__", agent['id'])
        help_text = help_text.replace("__NAME_JA__", agent['name_ja'])
        help_text = help_text.replace("__FEATURES_LIST__", features_list)
        help_text = help_text.replace("__CLASS_NAME__", snake_to_camel(agent['id']))
        await ctx.send(help_text)

    @commands.command(name="create")
    async def create_entry(self, ctx: commands.Context, title: str, *, content: str):
        """Create a new entry"""
        if self.bot.db:
            entry_id = await self.bot.db.create_entry(title, content)
            await ctx.send(f"✅ Created entry #{entry_id}")
        else:
            await ctx.send("❌ Database not connected")

    @commands.command(name="list")
    async def list_entries(self, ctx: commands.Context, category: str = None):
        """List entries"""
        if self.bot.db:
            entries = await self.bot.db.list_entries(category, limit=10)
            if entries:
                response = "📋 **Entries:\\n"
                for entry in entries:
                    response += f"- #{entry['id']}: {entry['title']}\\n"
                await ctx.send(response)
            else:
                await ctx.send("No entries found")
        else:
            await ctx.send("❌ Database not connected")

    @commands.command(name="search")
    async def search_entries(self, ctx: commands.Context, *, query: str):
        """Search entries"""
        if self.bot.db:
            entries = await self.bot.db.search_entries(query)
            if entries:
                response = f"🔍 **Search Results for '{query}':\\n"
                for entry in entries:
                    response += f"- #{entry['id']}: {entry['title']}\\n"
                await ctx.send(response)
            else:
                await ctx.send("No results found")
        else:
            await ctx.send("❌ Database not connected")

    @commands.command(name="get")
    async def get_entry(self, ctx: commands.Context, entry_id: int):
        """Get entry by ID"""
        if self.bot.db:
            entry = await self.bot.db.get_entry(entry_id)
            if entry:
                response = f"""
📄 **Entry #{entry['id']}**
**Title:** {entry['title']}
**Category:** {entry.get('category', 'N/A')}
**Content:** {entry['content'][:500]}
{'...' if len(entry['content']) > 500 else ''}
**Tags:** {', '.join(entry.get('tags', []))}
"""
                await ctx.send(response)
            else:
                await ctx.send(f"Entry #{entry_id} not found")
        else:
            await ctx.send("❌ Database not connected")


def create_bot(db, token: str, command_prefix: str = "!") -> DiscordBot:
    """Create and return Discord bot instance"""
    bot = DiscordBot(command_prefix=command_prefix, db=db)
    return bot
'''
    class_name = snake_to_camel(agent['id'])
    template = template.replace("__AGENT_ID__", agent['id'])
    template = template.replace("__NAME_JA__", agent['name_ja'])
    template = template.replace("__NAME_EN__", agent['name_en'])
    template = template.replace("__CLASS_NAME__", class_name)
    template = template.replace("__FEATURES_LIST__", features_list)
    return template


def generate_readme(agent):
    """README.md を生成"""
    tech_list = ', '.join(agent['tech_stack'])
    features_list = '\n'.join([f'- {f}' for f in agent['features']])
    class_name = snake_to_camel(agent['id'])
    template = '''# __NAME_JA__ / __NAME_EN__

__AGENT_ID__

## 概要 / Overview

__DESCRIPTION_JA__

__DESCRIPTION_EN__

## 機能 / Features

__FEATURES_LIST__

## 技術スタック / Tech Stack

- __TECH_LIST__

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd __AGENT_ID__

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import __CLASS_NAME__

# Initialize database
db = Database(db_path="data/__AGENT_ID__.db")
await db.initialize()

# Initialize agent
agent = __CLASS_NAME__(db)
await agent.initialize()

# Process data
result = await agent.process({"key": "value"})
print(result)
```

### Discord Botとして使用 / As a Discord Bot

```python
from discord import DiscordBot

# Create bot
bot = create_bot(db, token="YOUR_DISCORD_TOKEN", command_prefix="!")

# Run bot
bot.run()
```

## データベース構造 / Database Schema

### entries テーブル

| カラム | 型 | 説明 |
|--------|------|------|
| id | INTEGER | 主キー |
| title | TEXT | タイトル |
| content | TEXT | コンテンツ |
| category | TEXT | カテゴリ |
| tags | TEXT | タグ（カンマ区切り） |
| created_at | TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | 更新日時 |

## Discordコマンド / Discord Commands

| コマンド | 説明 |
|----------|------|
| `!status` | エージェントのステータスを確認 |
| `!help` | ヘルプを表示 |
| `!create <title> <content>` | 新しいエントリーを作成 |
| `!list [category]` | エントリーを一覧表示 |
| `!search <query>` | エントリーを検索 |
| `!get <id>` | IDでエントリーを取得 |

## ライセンス / License

MIT License
'''
    template = template.replace("__AGENT_ID__", agent['id'])
    template = template.replace("__NAME_JA__", agent['name_ja'])
    template = template.replace("__NAME_EN__", agent['name_en'])
    template = template.replace("__DESCRIPTION_JA__", agent['description_ja'])
    template = template.replace("__DESCRIPTION_EN__", agent['description_en'])
    template = template.replace("__FEATURES_LIST__", features_list)
    template = template.replace("__TECH_LIST__", tech_list)
    template = template.replace("__CLASS_NAME__", class_name)
    return template


def generate_requirements_txt(agent):
    """requirements.txt を生成"""
    template = '''# Core dependencies
discord.py>=2.3.2
aiohttp>=3.9.0

# Database
aiosqlite>=0.19.0

# Tech stack specific
'''
    for tech in agent['tech_stack']:
        template += f'{tech}\n'

    template += '''
# Utilities
python-dotenv>=1.0.0
pyyaml>=6.0
'''
    return template


def snake_to_camel(snake_str: str) -> str:
    """snake_case to CamelCase"""
    return ''.join(x.capitalize() for x in snake_str.replace('-', ' ').replace('_', ' ').split())


def create_agent(agent):
    """エージェントを作成"""
    logger.info(f"Creating agent: {agent['id']}")

    agent_dir = create_agent_directory(agent)

    files = {
        f"{agent_dir}/agent.py": generate_agent_py(agent),
        f"{agent_dir}/db.py": generate_db_py(agent),
        f"{agent_dir}/discord.py": generate_discord_py(agent),
        f"{agent_dir}/README.md": generate_readme(agent),
        f"{agent_dir}/requirements.txt": generate_requirements_txt(agent),
    }

    for filepath, content in files.items():
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Created: {filepath}")

    class_name = snake_to_camel(agent['id'])
    with open(f"{agent_dir}/__init__.py", 'w', encoding='utf-8') as f:
        f.write(f'''"""
{agent['name_ja']} / {agent['name_en']}
{agent['id']}
"""

from .agent import {class_name}
from .db import Database
from .discord import DiscordBot, create_bot

__all__ = ['{class_name}', 'Database', 'DiscordBot', 'create_bot']
''')

    logger.info(f"✅ Agent created: {agent['id']}")


def main():
    """メイン処理"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    global logger
    logger = logging.getLogger(__name__)

    progress = load_progress()

    for agent in AGENTS:
        if agent['id'] in progress['agents'] and progress['agents'][agent['id']].get('completed'):
            logger.info(f"Skipping completed agent: {agent['id']}")
            continue

        try:
            create_agent(agent)

            progress['agents'][agent['id']] = {
                'completed': True,
                'completed_at': datetime.utcnow().isoformat()
            }
            progress['completed_agents'] += 1
            save_progress(progress)

        except Exception as e:
            logger.error(f"Error creating agent {agent['id']}: {e}")
            progress['agents'][agent['id']] = {
                'completed': False,
                'error': str(e),
                'failed_at': datetime.utcnow().isoformat()
            }
            save_progress(progress)

    logger.info("=" * 50)
    logger.info(f"Project: {PROJECT_NAME}")
    logger.info(f"Total Agents: {progress['total_agents']}")
    logger.info(f"Completed: {progress['completed_agents']}")
    logger.info(f"Failed: {progress['total_agents'] - progress['completed_agents']}")
    logger.info("=" * 50)

    if progress['completed_agents'] == progress['total_agents']:
        logger.info("🎉 All agents created successfully!")
        progress['completed_at'] = datetime.utcnow().isoformat()
        save_progress(progress)
    else:
        logger.info("⚠️ Some agents failed. Check progress for details.")


if __name__ == '__main__':
    main()
