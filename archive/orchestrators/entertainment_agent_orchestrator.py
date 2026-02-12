#!/usr/bin/env python3
"""
エンターテイメントエージェントオーケストレーター
Entertainment Agent Orchestrator

ユーザーの興味に合わせたエンターテイメント関連エージェントを自律的に作成する
Creates entertainment-related agents based on user interests.
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

# プロジェクト設定
PROJECT_CONFIG = {
    "name": "エンターテイメントエージェントプロジェクト",
    "name_en": "Entertainment Agents Project",
    "version": "1.0.0",
    "created": datetime.now().isoformat()
}

# エージェント定義
AGENTS = [
    {
        "name": "anime-tracker-agent",
        "name_ja": "アニメ追跡エージェント",
        "description": "アニメの視聴記録と管理",
        "description_en": "Anime viewing tracking and management"
    },
    {
        "name": "movie-tracker-agent",
        "name_ja": "映画追跡エージェント",
        "description": "映画の視聴記録と評価管理",
        "description_en": "Movie viewing tracking and rating management"
    },
    {
        "name": "music-library-agent",
        "name_ja": "音楽ライブラリエージェント",
        "description": "音楽コレクションの管理",
        "description_en": "Music collection management"
    },
    {
        "name": "vtuber-agent",
        "name_ja": "VTuberエージェント",
        "description": "VTuberの配信スケジュールと情報管理",
        "description_en": "VTuber streaming schedule and information management"
    },
    {
        "name": "content-recommendation-agent",
        "name_ja": "コンテンツ推薦エージェント",
        "description": "映画・アニメ・音楽などのレコメンデーション",
        "description_en": "Movie, anime, music, and other content recommendations"
    },
    {
        "name": "streaming-service-agent",
        "name_ja": "ストリーミングサービスエージェント",
        "description": "Netflix、Amazon Prime、Disney+などの視聴記録",
        "description_en": "Viewing history for Netflix, Amazon Prime, Disney+, etc."
    },
    {
        "name": "manga-agent",
        "name_ja": "漫画エージェント",
        "description": "漫画の読書記録と管理",
        "description_en": "Manga reading tracking and management"
    },
    {
        "name": "novel-agent",
        "name_ja": "小説エージェント",
        "description": "小説・ライトノベルの読書記録と管理",
        "description_en": "Novel and light novel reading tracking and management"
    },
]

# 進捗管理ファイル
PROGRESS_FILE = "/workspace/entertainment_agent_progress.json"


def load_progress():
    """進捗をロード"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "started_at": datetime.now().isoformat(),
        "agents": {}
    }


def save_progress(progress):
    """進捗を保存"""
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def create_agent_directory(agent_name):
    """エージェントディレクトリを作成"""
    agent_dir = Path(f"/workspace/agents/{agent_name}")
    agent_dir.mkdir(parents=True, exist_ok=True)
    return agent_dir


def create_db_py(agent_dir, agent_name):
    """db.pyを作成"""
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
        """Initialize database"""
        if db_path is None:
            db_path = Path(__file__).parent / "data.db"
        self.db_path = db_path
        self.conn = None
        self._initialize()

    def _initialize(self):
        """Initialize database connection and create tables"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        """Create database tables"""
        cursor = self.conn.cursor()

        # Main records table
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS records ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "title TEXT NOT NULL,"
            "description TEXT,"
            "category TEXT,"
            "rating INTEGER DEFAULT 0,"
            "status TEXT DEFAULT 'watching',"
            "start_date TEXT,"
            "end_date TEXT,"
            "notes TEXT,"
            "tags TEXT,"
            "created_at TEXT DEFAULT CURRENT_TIMESTAMP,"
            "updated_at TEXT DEFAULT CURRENT_TIMESTAMP"
            ")"
        )

        # Categories table
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS categories ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "name TEXT UNIQUE NOT NULL,"
            "description TEXT,"
            "created_at TEXT DEFAULT CURRENT_TIMESTAMP"
            ")"
        )

        # Tags table
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS tags ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "name TEXT UNIQUE NOT NULL,"
            "created_at TEXT DEFAULT CURRENT_TIMESTAMP"
            ")"
        )

        # Record tags junction table
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS record_tags ("
            "record_id INTEGER,"
            "tag_id INTEGER,"
            "PRIMARY KEY (record_id, tag_id),"
            "FOREIGN KEY (record_id) REFERENCES records(id),"
            "FOREIGN KEY (tag_id) REFERENCES tags(id)"
            ")"
        )

        self.conn.commit()

    def add_record(self, title: str, description: str = None,
                   category: str = None, rating: int = 0,
                   status: str = 'watching', notes: str = None,
                   tags: List[str] = None) -> int:
        """Add a new record"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO records (title, description, category, rating, status, notes) VALUES (?, ?, ?, ?, ?, ?)",
            (title, description, category, rating, status, notes)
        )
        record_id = cursor.lastrowid

        # Add tags
        if tags:
            for tag_name in tags:
                tag_id = self._get_or_create_tag(tag_name)
                cursor.execute(
                    "INSERT INTO record_tags (record_id, tag_id) VALUES (?, ?)",
                    (record_id, tag_id)
                )

        self.conn.commit()
        return record_id

    def get_record(self, record_id: int) -> Optional[Dict]:
        """Get a record by ID"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM records WHERE id = ?', (record_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def list_records(self, status: str = None,
                    category: str = None) -> List[Dict]:
        """List records with optional filters"""
        cursor = self.conn.cursor()
        query = 'SELECT * FROM records WHERE 1=1'
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

    def update_record(self, record_id: int, **kwargs) -> bool:
        """Update a record"""
        valid_fields = ['title', 'description', 'category', 'rating',
                       'status', 'start_date', 'end_date', 'notes']
        update_fields = {{k: v for k, v in kwargs.items() if k in valid_fields}}

        if not update_fields:
            return False

        update_fields['updated_at'] = datetime.now().isoformat()

        set_clause = ', '.join([f'{{k}} = ?' for k in update_fields.keys()])
        values = list(update_fields.values()) + [record_id]

        cursor = self.conn.cursor()
        cursor.execute(
            f"UPDATE records SET {{set_clause}} WHERE id = ?",
            values
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def delete_record(self, record_id: int) -> bool:
        """Delete a record"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM record_tags WHERE record_id = ?', (record_id,))
        cursor.execute('DELETE FROM records WHERE id = ?', (record_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def get_statistics(self) -> Dict:
        """Get statistics"""
        cursor = self.conn.cursor()

        # Total records
        cursor.execute('SELECT COUNT(*) FROM records')
        total = cursor.fetchone()[0]

        # By status
        cursor.execute(
            "SELECT status, COUNT(*) as count FROM records GROUP BY status"
        )
        by_status = {{row[0]: row[1] for row in cursor.fetchall()}}

        # Average rating
        cursor.execute('SELECT AVG(rating) FROM records WHERE rating > 0')
        avg_rating = cursor.fetchone()[0] or 0

        return {{
            'total': total,
            'by_status': by_status,
            'average_rating': round(avg_rating, 2)
        }}

    def _get_or_create_tag(self, tag_name: str) -> int:
        """Get or create a tag"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM tags WHERE name = ?', (tag_name,))
        row = cursor.fetchone()

        if row:
            return row[0]

        cursor.execute('INSERT INTO tags (name) VALUES (?)', (tag_name,))
        self.conn.commit()
        return cursor.lastrowid

    def close(self):
        """Close database connection"""
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
    """discord.pyを作成"""
    content = f'''#!/usr/bin/env python3
"""
{agent_name} - Discord Bot Module

Discord bot for {agent_name} - {agent_info['description']}
"""

import discord
from discord.ext import commands
import re
from typing import Optional, List
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))
from db import Database


class DiscordBot(commands.Bot):
    """Discord bot for {agent_name}"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True

        super().__init__(
            command_prefix='!',
            intents=intents,
            description="{agent_info['description_en']}"
        )

        self.db = Database()

    async def on_ready(self):
        """Bot is ready"""
        print(f'{{self.user}} has connected to Discord!')
        print(f'Guilds: {{len(self.guilds)}}')

    async def on_message(self, message: discord.Message):
        """Handle incoming messages"""
        if message.author == self.user:
            return

        await self._process_natural_language(message)
        await super().on_message(message)

    async def _process_natural_language(self, message: discord.Message):
        """Process natural language messages"""
        content = message.content.lower()

        add_patterns = [
            r'(追加|add|記録|track|登録)\\s*(.+)',
            r'(見た|watched|読んだ|read|聞いた|listened)\\s*(.+)'
        ]

        for pattern in add_patterns:
            match = re.search(pattern, content)
            if match:
                title = match.group(2).strip()
                if len(title) > 2:
                    record_id = self.db.add_record(
                        title=title,
                        status='completed',
                        start_date=message.created_at.isoformat()
                    )
                    await message.reply(f'記録しました: {{title}} (ID: {{record_id}})')
                    return

        list_patterns = [
            r'(一覧|list|全|all|what|what\\s+do|show)',
            r'(見てる|watching|読んでる|reading|聞いてる|listening)'
        ]

        for pattern in list_patterns:
            if re.search(pattern, content):
                records = self.db.list_records()
                if records:
                    response = "**一覧**:\\n"
                    for i, record in enumerate(records[:10], 1):
                        status_emoji = {{'watching': '👀', 'completed': '✅', 'planned': '📋'}}
                        emoji = status_emoji.get(record['status'], '📌')
                        response += f"{{i}}. {{emoji}} {{record['title']}}\\n"
                    if len(records) > 10:
                        response += f"\\n...他 {{len(records) - 10}}件"
                else:
                    response = "記録がまだありません。"
                await message.reply(response)
                return

        help_patterns = [r'(help|ヘルプ|使い方|how|使う)']
        for pattern in help_patterns:
            if re.search(pattern, content):
                await self._send_help(message)
                return

    async def _send_help(self, message: discord.Message):
        """Send help message"""
        help_text = "**" + agent_info['name_ja'] + "** - " + agent_info['description'] + "\n\n"
        help_text += "**コマンド**:\n"
        help_text += "- `!add <タイトル>` - 追加\n"
        help_text += "- `!list` - 一覧\n"
        help_text += "- `!update <ID> [status|rating]` - 更新\n"
        help_text += "- `!delete <ID>` - 削除\n"
        help_text += "- `!stats` - 統計\n\n"
        help_text += "**自然言語**:\n"
        help_text += '- "○○を追加" "○○を見た" - 記録追加\n'
        help_text += '- "一覧" "何見てる？" - 一覧表示'
        await message.reply(help_text)

    @commands.command()
    async def add(self, ctx, *, title: str):
        """Add a record"""
        record_id = self.db.add_record(title=title)
        await ctx.send(f'追加しました: {{title}} (ID: {{record_id}})')

    @commands.command()
    async def list(self, ctx, status: Optional[str] = None):
        """List records"""
        records = self.db.list_records(status=status)

        if not records:
            await ctx.send("記録がまだありません。")
            return

        response = "**一覧**:\\n"
        for i, record in enumerate(records[:10], 1):
            status_emoji = {{'watching': '👀', 'completed': '✅', 'planned': '📋'}}
            emoji = status_emoji.get(record['status'], '📌')
            response += f"{{i}}. {{emoji}} {{record['title']}}"
            if record['rating'] > 0:
                response += f" ⭐{{record['rating']}}"
            response += "\\n"

        if len(records) > 10:
            response += f"\\n...他 {{len(records) - 10}}件"

        await ctx.send(response)

    @commands.command()
    async def update(self, ctx, record_id: int, **kwargs):
        """Update a record"""
        success = self.db.update_record(record_id, **kwargs)
        if success:
            await ctx.send(f"ID {{record_id}} を更新しました。")
        else:
            await ctx.send(f"ID {{record_id}} が見つかりません。")

    @commands.command()
    async def delete(self, ctx, record_id: int):
        """Delete a record"""
        success = self.db.delete_record(record_id)
        if success:
            await ctx.send(f"ID {{record_id}} を削除しました。")
        else:
            await ctx.send(f"ID {{record_id}} が見つかりません。")

    @commands.command()
    async def stats(self, ctx):
        """Show statistics"""
        stats = self.db.get_statistics()
        response = "**統計**\\n"
        response += f"- 総数: {{stats['total']}}\\n"
        response += f"- 平均評価: {{stats['average_rating']}}\\n\\n"
        response += "**ステータス別**:\\n"
        for status, count in stats['by_status'].items():
            response += f"- {{status}}: {{count}}\\n"
        await ctx.send(response)

    def close(self):
        """Close database connection"""
        self.db.close()


def main():
    """Main function"""
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
    """README.mdを作成（バイリンガル）"""
    content = f'''# {agent_name}

## 概要 (Overview)

{agent_info['description']}

{agent_info['description_en']}

## 機能 (Features)

- コンテンツの記録と追跡 (Record and track content)
- 評価・タグ付け機能 (Rating and tagging)
- カテゴリ分類 (Category classification)
- 統計情報の表示 (Statistics display)
- Discord Botによる自然言語操作 (Natural language control via Discord Bot)

## インストール (Installation)

```bash
pip install -r requirements.txt
```

## 環境変数 (Environment Variables)

- `DISCORD_TOKEN` - Discord Botトークン (Discord Bot token)

## 使用方法 (Usage)

### データベース操作 (Database Operations)

```python
from db import Database

db = Database()

# 追加 (Add)
record_id = db.add_record(
    title="Example Title",
    description="Description",
    category="category",
    rating=8,
    status="watching"
)

# 一覧 (List)
records = db.list_records()

# 統計 (Statistics)
stats = db.get_statistics()
```

### Discord Bot (Discord Bot)

```bash
python discord.py
```

**コマンド**:
- `!add <タイトル>` - 追加 (Add)
- `!list` - 一覧 (List)
- `!update <ID> [status|rating]` - 更新 (Update)
- `!delete <ID>` - 削除 (Delete)
- `!stats` - 統計 (Statistics)

**自然言語**:
- 「○○を追加」「○○を見た」 - 記録追加 (Add record)
- 「一覧」「何見てる？」 - 一覧表示 (Show list)

## データベース構造 (Database Schema)

### records テーブル
- `id` - ID
- `title` - タイトル
- `description` - 説明
- `category` - カテゴリ
- `rating` - 評価
- `status` - ステータス
- `start_date` - 開始日
- `end_date` - 終了日
- `notes` - メモ
- `created_at` - 作成日時
- `updated_at` - 更新日時

## ライセンス (License)

MIT
'''
    with open(agent_dir / "README.md", 'w', encoding='utf-8') as f:
        f.write(content)


def create_requirements_txt(agent_dir):
    """requirements.txtを作成"""
    content = 'discord.py>=2.3.0\n'
    with open(agent_dir / "requirements.txt", 'w', encoding='utf-8') as f:
        f.write(content)


def create_agent(agent):
    """エージェントを作成"""
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
    """メイン処理"""
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
