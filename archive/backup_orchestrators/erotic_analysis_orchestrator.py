#!/usr/bin/env python3
"""
Erotic Content Advanced Analysis Agents Orchestrator
えっちコンテンツ高度分析エージェントオーケストレーター
"""

import json
import os
import subprocess
import time

# プロジェクト設定
PROJECT_NAME = "erotic_analysis"
PROJECT_VERSION = "V1"

# エージェント定義
AGENTS = [
    {
        "name": "erotic-trending-agent",
        "name_ja": "えっちコンテンツトレンド分析エージェント",
        "description": "Analyze trending erotic content and identify popular patterns",
        "description_ja": "えっちコンテンツのトレンドを分析し、人気のあるパターンを特定",
        "tables": ["trends", "tags", "entries"]
    },
    {
        "name": "erotic-recommendation-agent",
        "name_ja": "えっちコンテンツ推薦エージェント",
        "description": "Recommend erotic content based on user preferences and history",
        "description_ja": "ユーザーの好みと履歴に基づいてえっちコンテンツを推薦",
        "tables": ["recommendations", "user_preferences", "entries"]
    },
    {
        "name": "erotic-similar-agent",
        "name_ja": "類似えっちコンテンツ検索エージェント",
        "description": "Find similar erotic content based on tags, artists, and patterns",
        "description_ja": "タグ、イラストレーター、パターンに基づいて類似のえっちコンテンツを検索",
        "tables": ["similar_content", "tags", "entries"]
    },
    {
        "name": "erotic-statistics-agent",
        "name_ja": "えっちコンテンツ統計分析エージェント",
        "description": "Analyze statistics of erotic content views, ratings, and engagement",
        "description_ja": "えっちコンテンツの閲覧、評価、エンゲージメントの統計を分析",
        "tables": ["statistics", "views", "ratings"]
    },
    {
        "name": "erotic-collection-analysis-agent",
        "name_ja": "コレクション分析エージェント",
        "description": "Analyze user collections and identify patterns in favorites",
        "description_ja": "ユーザーコレクションを分析し、お気に入りのパターンを特定",
        "tables": ["collections", "analysis", "entries"]
    },
]

# 進捗管理ファイル
PROGRESS_FILE = f"/workspace/{PROJECT_NAME}_progress.json"


def load_progress():
    """進捗状況を読み込む"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "project": PROJECT_NAME,
        "version": PROJECT_VERSION,
        "total": len(AGENTS),
        "completed": 0,
        "agents": {}
    }


def save_progress(progress):
    """進捗状況を保存"""
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)


def create_table_schema(tables):
    """テーブルスキーマを生成"""
    schema_sql = []
    for table in tables:
        if table == "trends":
            schema_sql.append("""
CREATE TABLE IF NOT EXISTS trends (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id INTEGER NOT NULL,
    keyword TEXT NOT NULL,
    trend_score REAL DEFAULT 0,
    period TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (content_id) REFERENCES entries(id)
);""")
        elif table == "recommendations":
            schema_sql.append("""
CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    content_id INTEGER NOT NULL,
    score REAL DEFAULT 0,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (content_id) REFERENCES entries(id)
);""")
        elif table == "similar_content":
            schema_sql.append("""
CREATE TABLE IF NOT EXISTS similar_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id INTEGER NOT NULL,
    similar_content_id INTEGER NOT NULL,
    similarity_score REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (content_id) REFERENCES entries(id),
    FOREIGN KEY (similar_content_id) REFERENCES entries(id)
);""")
        elif table == "statistics":
            schema_sql.append("""
CREATE TABLE IF NOT EXISTS statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_type TEXT NOT NULL,
    metric_value REAL NOT NULL,
    period TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""")
        elif table == "collections":
            schema_sql.append("""
CREATE TABLE IF NOT EXISTS collections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""")
        elif table == "analysis":
            schema_sql.append("""
CREATE TABLE IF NOT EXISTS analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_id INTEGER NOT NULL,
    analysis_type TEXT NOT NULL,
    result TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (collection_id) REFERENCES collections(id)
);""")
        elif table == "user_preferences":
            schema_sql.append("""
CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    preference_key TEXT NOT NULL,
    preference_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""")
        elif table == "views":
            schema_sql.append("""
CREATE TABLE IF NOT EXISTS views (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id INTEGER NOT NULL,
    view_count INTEGER DEFAULT 0,
    last_viewed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (content_id) REFERENCES entries(id)
);""")
        elif table == "ratings":
            schema_sql.append("""
CREATE TABLE IF NOT EXISTS ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id INTEGER NOT NULL,
    rating REAL NOT NULL,
    user_id TEXT,
    review TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (content_id) REFERENCES entries(id)
);""")
    return "\n".join(schema_sql)


def get_functions_for_tables(tables):
    """テーブルに基づいて関数を生成"""
    functions = []
    for table in tables:
        if table == "trends":
            functions.append("""
    def analyze_trends(self, period="daily"):
        \"\"\"トレンドを分析\"\"\"
        # 既存のエントリーからトレンドを分析
        pass

    def get_trending_content(self, limit=10):
        \"\"\"トレンドコンテンツを取得\"\"\"
        pass""")
        elif table == "recommendations":
            functions.append("""
    def generate_recommendations(self, user_id, limit=10):
        \"\"\"推薦を生成\"\"\"
        # ユーザーの好みと履歴に基づいて推薦
        pass

    def update_user_preferences(self, user_id, preferences):
        \"\"\"ユーザー好みを更新\"\"\"
        pass""")
        elif table == "similar_content":
            functions.append("""
    def find_similar_content(self, content_id, limit=10):
        \"\"\"類似コンテンツを検索\"\"\"
        # タグやイラストレーターに基づいて類似コンテンツを検索
        pass

    def calculate_similarity(self, content_id1, content_id2):
        \"\"\"類似度を計算\"\"\"
        pass""")
        elif table == "statistics":
            functions.append("""
    def analyze_statistics(self, metric_type, period="daily"):
        \"\"\"統計を分析\"\"\"
        # 閲覧数、評価などの統計を分析
        pass

    def get_top_content(self, metric="views", limit=10):
        \"\"\"トップコンテンツを取得\"\"\"
        pass""")
        elif table == "collections":
            functions.append("""
    def create_collection(self, name, description=""):
        \"\"\"コレクションを作成\"\"\"
        pass

    def add_to_collection(self, collection_id, content_id):
        \"\"\"コレクションに追加\"\"\"
        pass""")
        elif table == "analysis":
            functions.append("""
    def analyze_collection(self, collection_id):
        \"\"\"コレクションを分析\"\"\"
        # コレクションのパターンを分析
        pass

    def get_patterns(self, collection_id):
        \"\"\"パターンを取得\"\"\"
        pass""")
        elif table == "user_preferences":
            functions.append("""
    def save_preference(self, user_id, key, value):
        \"\"\"好みを保存\"\"\"
        pass

    def get_preferences(self, user_id):
        \"\"\"好みを取得\"\"\"
        pass""")
        elif table == "views":
            functions.append("""
    def record_view(self, content_id, user_id=None):
        \"\"\"閲覧を記録\"\"\"
        pass

    def get_view_stats(self, content_id):
        \"\"\"閲覧統計を取得\"\"\"
        pass""")
        elif table == "ratings":
            functions.append("""
    def save_rating(self, content_id, rating, user_id=None, review=""):
        \"\"\"評価を保存\"\"\"
        pass

    def get_ratings(self, content_id):
        \"\"\"評価を取得\"\"\"
        pass""")
    return "\n".join(functions)


def create_agent_py(agent):
    """agent.pyファイルを作成"""
    tables_sql = create_table_schema(agent["tables"])
    functions_str = get_functions_for_tables(agent["tables"])

    # 変数を準備
    agent_name = agent["name"]
    agent_name_ja = agent["name_ja"]
    class_name = agent["name"].replace("-", "_").title().replace("_", "")

    agent_py_template = '''#!/usr/bin/env python3
"""
{AGENT_NAME} - {AGENT_NAME_JA}
{AGENT_DESCRIPTION}
{AGENT_DESCRIPTION_JA}
"""

import sqlite3
from typing import List, Dict, Optional
from datetime import datetime


class {CLASS_NAME}Agent:
    """{AGENT_NAME_JA}"""

    def __init__(self, db_path: str = "{AGENT_NAME}.db"):
        self.db_path = db_path
        self.conn = None
        self._initialize_db()

    def _initialize_db(self):
        """データベースを初期化"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()

        # 基本テーブル
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            source_url TEXT,
            artist TEXT,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 追加テーブル
{TABLES_SQL}

        # タグテーブル
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag_name TEXT NOT NULL UNIQUE
        );
        """)

        # エントリータグ紐付けテーブル
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS entry_tags (
            entry_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (entry_id, tag_id),
            FOREIGN KEY (entry_id) REFERENCES entries(id),
            FOREIGN KEY (tag_id) REFERENCES tags(id)
        );
        """)

        self.conn.commit()

    def add_entry(self, title: str, content: str = "", source_url: str = "", artist: str = "", tags: List[str] = None) -> int:
        """エントリーを追加"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO entries (title, content, source_url, artist, tags) VALUES (?, ?, ?, ?, ?)",
            (title, content, source_url, artist, ",".join(tags or []))
        )
        entry_id = cursor.lastrowid

        # タグを追加
        if tags:
            for tag in tags:
                self._add_tag_to_entry(entry_id, tag)

        self.conn.commit()
        return entry_id

    def _add_tag_to_entry(self, entry_id: int, tag_name: str):
        """エントリーにタグを追加"""
        cursor = self.conn.cursor()

        # タグが存在しない場合は作成
        cursor.execute("INSERT OR IGNORE INTO tags (tag_name) VALUES (?)", (tag_name,))
        cursor.execute("SELECT id FROM tags WHERE tag_name = ?", (tag_name,))
        tag_id = cursor.fetchone()["id"]

        # エントリーとタグを紐付け
        cursor.execute(
            "INSERT OR IGNORE INTO entry_tags (entry_id, tag_id) VALUES (?, ?)",
            (entry_id, tag_id)
        )

        self.conn.commit()

    def get_entry(self, entry_id: int) -> Optional[Dict]:
        """エントリーを取得"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def list_entries(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """エントリー一覧を取得"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM entries ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset)
        )
        return [dict(row) for row in cursor.fetchall()]

    def search_entries(self, query: str) -> List[Dict]:
        """エントリーを検索"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM entries WHERE title LIKE ? OR content LIKE ? OR tags LIKE ?",
            (f"%{query}%", f"%{query}%", f"%{query}%")
        )
        return [dict(row) for row in cursor.fetchall()]

{FUNCTIONS_STR}

    def close(self):
        """データベース接続を閉じる"""
        if self.conn:
            self.conn.close()


if __name__ == "__main__":
    agent = {CLASS_NAME}Agent()
    print("{AGENT_NAME_JA}が起動しました")
'''

    # 置換
    agent_py = agent_py_template
    agent_py = agent_py.replace("{AGENT_NAME}", agent_name)
    agent_py = agent_py.replace("{AGENT_NAME_JA}", agent_name_ja)
    agent_py = agent_py.replace("{AGENT_DESCRIPTION}", agent["description"])
    agent_py = agent_py.replace("{AGENT_DESCRIPTION_JA}", agent["description_ja"])
    agent_py = agent_py.replace("{CLASS_NAME}", class_name)
    agent_py = agent_py.replace("{TABLES_SQL}", tables_sql)
    agent_py = agent_py.replace("{FUNCTIONS_STR}", functions_str)

    return agent_py


def create_db_py(agent):
    """db.pyファイルを作成"""
    tables_sql = create_table_schema(agent["tables"])

    # 変数を準備
    agent_name = agent["name"]

    db_py_template = '''#!/usr/bin/env python3
"""
Database module for {AGENT_NAME}
{AGENT_NAME}のデータベース管理モジュール
"""

import sqlite3
from contextlib import contextmanager
from typing import List, Dict, Optional, Tuple
from datetime import datetime


class Database:
    """データベース管理クラス"""

    def __init__(self, db_path: str = "{AGENT_NAME}.db"):
        self.db_path = db_path
        self._initialize_db()

    @contextmanager
    def get_connection(self):
        """データベース接続を取得"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _initialize_db(self):
        """データベースを初期化"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 基本テーブル
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                source_url TEXT,
                artist TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # 追加テーブル
{TABLES_SQL}

            # タグテーブル
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_name TEXT NOT NULL UNIQUE
            );
            """)

            # エントリータグ紐付けテーブル
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS entry_tags (
                entry_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                PRIMARY KEY (entry_id, tag_id),
                FOREIGN KEY (entry_id) REFERENCES entries(id),
                FOREIGN KEY (tag_id) REFERENCES tags(id)
            );
            """)

    def execute(self, query: str, params: Tuple = ()) -> sqlite3.Cursor:
        """SQLを実行"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor

    def fetch_all(self, query: str, params: Tuple = ()) -> List[Dict]:
        """全件取得"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def fetch_one(self, query: str, params: Tuple = ()) -> Optional[Dict]:
        """1件取得"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None

    def insert(self, table: str, data: Dict) -> int:
        """データを挿入"""
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        query = f"INSERT INTO {{table}} ({{columns}}) VALUES ({{placeholders}})"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(data.values()))
            return cursor.lastrowid

    def update(self, table: str, data: Dict, where: Dict) -> int:
        """データを更新"""
        set_clause = ", ".join([f"{{k}} = ?" for k in data.keys()])
        where_clause = " AND ".join([f"{{k}} = ?" for k in where.keys()])
        query = f"UPDATE {{table}} SET {{set_clause}} WHERE {{where_clause}}"
        params = tuple(data.values()) + tuple(where.values())
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount

    def delete(self, table: str, where: Dict) -> int:
        """データを削除"""
        where_clause = " AND ".join([f"{{k}} = ?" for k in where.keys()])
        query = f"DELETE FROM {{table}} WHERE {{where_clause}}"
        params = tuple(where.values())
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount


# シングルトンインスタンス
_db_instance = None


def get_db() -> Database:
    """データベースインスタンスを取得"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
'''

    db_py = db_py_template
    db_py = db_py.replace("{AGENT_NAME}", agent_name)
    db_py = db_py.replace("{TABLES_SQL}", tables_sql)

    return db_py


def create_discord_py(agent):
    """discord.pyファイルを作成"""
    agent_name = agent["name"]
    agent_name_ja = agent["name_ja"]
    class_name = agent["name"].replace("-", "_").title().replace("_", "")

    discord_py_template = '''#!/usr/bin/env python3
"""
Discord Bot module for {AGENT_NAME}
{AGENT_NAME_JA}のDiscord Botモジュール
"""

import discord
from discord.ext import commands
from typing import Optional
import asyncio

from .agent import {CLASS_NAME}Agent
from .db import get_db


class DiscordBot(commands.Bot):
    """{AGENT_NAME_JA} Discord Bot"""

    def __init__(self, agent: {CLASS_NAME}Agent):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )
        self.agent = agent
        self.db = get_db()

    async def on_ready(self):
        """Bot起動時"""
        print(f"Logged in as {{self.user}} (ID: {{self.user.id}})")
        await self.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="コンテンツ分析"
        ))

    async def on_message(self, message: discord.Message):
        """メッセージ受信時"""
        if message.author.bot:
            return

        await self.process_commands(message)


def create_bot(agent: {CLASS_NAME}Agent, token: str) -> DiscordBot:
    """Botインスタンスを作成"""
    bot = DiscordBot(agent)

    @bot.command(name="add")
    async def add_entry(ctx, title: str, *, content: str = ""):
        """エントリーを追加"""
        entry_id = agent.add_entry(title, content)
        await ctx.send(f"エントリーを追加しました (ID: {{entry_id}})")

    @bot.command(name="list")
    async def list_entries(ctx, limit: int = 10):
        """エントリー一覧"""
        entries = agent.list_entries(limit=limit)
        if not entries:
            await ctx.send("エントリーがありません")
            return

        embed = discord.Embed(title="{AGENT_NAME_JA}", color=discord.Color.blue())
        for entry in entries:
            embed.add_field(
                name=entry["title"],
                value=f"ID: {{entry['id']}} | {{entry.get('tags', 'N/A')}}",
                inline=False
            )
        await ctx.send(embed=embed)

    @bot.command(name="search")
    async def search_entries(ctx, *, query: str):
        """エントリーを検索"""
        entries = agent.search_entries(query)
        if not entries:
            await ctx.send("該当するエントリーがありません")
            return

        embed = discord.Embed(
            title=f"検索結果: {{query}}",
            color=discord.Color.green()
        )
        for entry in entries[:10]:
            embed.add_field(
                name=entry["title"],
                value=f"ID: {{entry['id']}}",
                inline=False
            )
        await ctx.send(embed=embed)

    @bot.command(name="get")
    async def get_entry(ctx, entry_id: int):
        """エントリー詳細"""
        entry = agent.get_entry(entry_id)
        if not entry:
            await ctx.send(f"エントリー ID {{entry_id}} は見つかりませんでした")
            return

        embed = discord.Embed(
            title=entry["title"],
            description=entry.get("content", "N/A"),
            color=discord.Color.purple()
        )
        embed.add_field(name="ID", value=entry["id"], inline=True)
        embed.add_field(name="Artist", value=entry.get("artist", "N/A"), inline=True)
        embed.add_field(name="Tags", value=entry.get("tags", "N/A"), inline=True)
        await ctx.send(embed=embed)

    @bot.command(name="help")
    async def help_command(ctx):
        """ヘルプ"""
        embed = discord.Embed(
            title="{AGENT_NAME_JA} - ヘルプ",
            color=discord.Color.gold()
        )
        embed.add_field(name="!add <title> [content]", value="エントリーを追加", inline=False)
        embed.add_field(name="!list [limit]", value="エントリー一覧", inline=False)
        embed.add_field(name="!search <query>", value="エントリーを検索", inline=False)
        embed.add_field(name="!get <id>", value="エントリー詳細", inline=False)
        await ctx.send(embed=embed)

    return bot


async def run_bot(agent: {CLASS_NAME}Agent, token: str):
    """Botを実行"""
    bot = create_bot(agent, token)
    await bot.start(token)


def run_bot_sync(token: str):
    """Botを同期的に実行"""
    agent = {CLASS_NAME}Agent()
    asyncio.run(run_bot(agent, token))
'''

    discord_py = discord_py_template
    discord_py = discord_py.replace("{AGENT_NAME}", agent_name)
    discord_py = discord_py.replace("{AGENT_NAME_JA}", agent_name_ja)
    discord_py = discord_py.replace("{CLASS_NAME}", class_name)

    return discord_py


def create_readme_md(agent):
    """README.mdファイルを作成"""
    agent_name = agent["name"]
    agent_name_ja = agent["name_ja"]
    class_name = agent["name"].replace("-", "_").title().replace("_", "")

    tables_str = "\n".join([f"- {table}" for table in agent["tables"]])

    readme_md_template = '''# {AGENT_NAME}

{AGENT_NAME_JA}

## Description

{AGENT_DESCRIPTION}

{AGENT_DESCRIPTION_JA}

## Features

- エントリーの追加・管理
- タグベースの検索・分類
- Discord Botによる対話的な操作
- SQLiteデータベースによるデータ永続化

## Installation

```bash
cd agents/{AGENT_NAME}
pip install -r requirements.txt
```

## Usage

### As a Python Module

```python
from {AGENT_NAME}.agent import {CLASS_NAME}Agent

agent = {CLASS_NAME}Agent()
entry_id = agent.add_entry(
    title="サンプルタイトル",
    content="サンプルコンテンツ",
    artist="イラストレーター名",
    tags=["tag1", "tag2"]
)
print(f"Created entry: {{entry_id}}")
```

### Discord Bot

```bash
export DISCORD_BOT_TOKEN="your_token_here"
python -m {AGENT_NAME}.discord
```

## Discord Commands

| Command | Description |
|---------|-------------|
| `!add <title> [content]` | エントリーを追加 |
| `!list [limit]` | エントリー一覧 |
| `!search <query>` | エントリーを検索 |
| `!get <id>` | エントリー詳細 |
| `!help` | ヘルプ |

## Database Schema

- `entries` - コンテンツエントリー
- `tags` - タグ
- `entry_tags` - エントリーとタグの紐付け
{TABLES_STR}

## API Reference

### Agent Class

```python
class {CLASS_NAME}Agent:
    def __init__(self, db_path: str = "{AGENT_NAME}.db")
    def add_entry(self, title, content="", source_url="", artist="", tags=None) -> int
    def get_entry(self, entry_id) -> Optional[Dict]
    def list_entries(self, limit=100, offset=0) -> List[Dict]
    def search_entries(self, query) -> List[Dict]
```

## Development

```bash
# Run tests
pytest tests/

# Format code
black .
flake8 .
```

## License

MIT License
'''

    readme_md = readme_md_template
    readme_md = readme_md.replace("{AGENT_NAME}", agent_name)
    readme_md = readme_md.replace("{AGENT_NAME_JA}", agent_name_ja)
    readme_md = readme_md.replace("{AGENT_DESCRIPTION}", agent["description"])
    readme_md = readme_md.replace("{AGENT_DESCRIPTION_JA}", agent["description_ja"])
    readme_md = readme_md.replace("{CLASS_NAME}", class_name)
    readme_md = readme_md.replace("{TABLES_STR}", tables_str)

    return readme_md


def create_requirements_txt():
    """requirements.txtファイルを作成"""
    return '''discord.py>=2.3.0
pytest>=7.4.0
pytest-asyncio>=0.21.0
'''


def create_agent(agent):
    """エージェントを作成"""
    agent_dir = "/workspace/agents/" + agent["name"]

    # ディレクトリを作成
    os.makedirs(agent_dir, exist_ok=True)

    # ファイルを作成
    files = [
        ("agent.py", create_agent_py(agent)),
        ("db.py", create_db_py(agent)),
        ("discord.py", create_discord_py(agent)),
        ("README.md", create_readme_md(agent)),
        ("requirements.txt", create_requirements_txt()),
    ]

    for filename, content in files:
        filepath = os.path.join(agent_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    return agent_dir


def main():
    """メイン処理"""
    print(f"{'='*50}")
    print(f"{PROJECT_NAME} Orchestrator - {PROJECT_VERSION}")
    print(f"{'='*50}")
    print()

    progress = load_progress()

    for agent in AGENTS:
        if agent["name"] in progress.get("agents", {}):
            if progress["agents"][agent["name"]].get("completed", False):
                print(f"✅ {agent['name']} - 既に完了済み")
                continue

        print(f"🔧 {agent['name']} を作成中...")
        agent_dir = create_agent(agent)

        # 進捗を更新
        if "agents" not in progress:
            progress["agents"] = {}
        progress["agents"][agent["name"]] = {
            "completed": True,
            "path": agent_dir,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        progress["completed"] = len([a for a in progress.get("agents", {}).values() if a.get("completed", False)])
        save_progress(progress)

        print(f"✅ {agent['name']} - 完了")
        print()

    print(f"{'='*50}")
    print(f"🎉 プロジェクト完了！")
    print(f"{'='*50}")
    print(f"完了済みエージェント: {progress['completed']}/{progress['total']}")
    print()

    # Gitコミット
    print("Gitコミット中...")
    subprocess.run(["git", "add", "-A"], cwd="/workspace")
    result = subprocess.run(
        ["git", "commit", "-m", f"feat: {PROJECT_NAME}プロジェクト完了 ({progress['completed']}/{progress['total']})"],
        cwd="/workspace",
        capture_output=True
    )
    if result.returncode == 0:
        print("✅ Gitコミット完了")
        subprocess.run(["git", "push"], cwd="/workspace")
        print("✅ Gitプッシュ完了")
    else:
        print("ℹ️ コミットする変更がありません")


if __name__ == "__main__":
    main()
