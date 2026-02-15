#!/usr/bin/env python3
"""
エロティックコンテンツ関連エージェントV4オーケストレーター
Erotic Content Agents V4 Orchestrator

ユーザーの興味（えっちな女の子）に合わせた追加エージェントを作成する
"""

import os
import json
import subprocess
import shutil
from datetime import datetime

# エージェント定義
AGENTS = [
    {
        "name": "erotic-creator-agent",
        "display_name": "えっちクリエイターエージェント",
        "english_name": "Erotic Creator Agent",
        "description": "えっちなクリエイター情報、作品リスト、活動状況を管理するエージェント",
        "english_description": "An agent for managing erotic creators, their works, and activity status",
        "tables": {
            "creators": "クリエイターテーブル",
            "works": "作品テーブル"
        },
        "features": ["クリエイター管理", "作品追跡", "活動状況", "通知機能"]
    },
    {
        "name": "erotic-series-agent",
        "display_name": "えっちシリーズエージェント",
        "english_name": "Erotic Series Agent",
        "description": "えっちなシリーズ作品、連載状況、シリーズ順を管理するエージェント",
        "english_description": "An agent for managing erotic series, publication status, and series order",
        "tables": {
            "series": "シリーズテーブル",
            "volumes": "巻・回テーブル"
        },
        "features": ["シリーズ管理", "連載追跡", "巻数管理", "完結状況"]
    },
    {
        "name": "erotic-platform-agent",
        "display_name": "えっちプラットフォームエージェント",
        "english_name": "Erotic Platform Agent",
        "description": "えっちサイト、サービス情報、プラットフォームの比較を管理するエージェント",
        "english_description": "An agent for managing erotic sites, service info, and platform comparisons",
        "tables": {
            "platforms": "プラットフォームテーブル",
            "features": "機能テーブル"
        },
        "features": ["サイト管理", "機能比較", "価格情報", "利用状況"]
    },
    {
        "name": "erotic-event-agent",
        "display_name": "えっちイベントエージェント",
        "english_name": "Erotic Event Agent",
        "description": "えっちイベント、フェス、コンベンション情報を管理するエージェント",
        "english_description": "An agent for managing erotic events, festivals, and conventions",
        "tables": {
            "events": "イベントテーブル",
            "schedules": "スケジュールテーブル"
        },
        "features": ["イベント管理", "スケジュール", "参加者情報", "会場データ"]
    },
    {
        "name": "erotic-community-agent",
        "display_name": "えっちコミュニティエージェント",
        "english_name": "Erotic Community Agent",
        "description": "えっちコミュニティ、フォーラム、SNSグループ情報を管理するエージェント",
        "english_description": "An agent for managing erotic communities, forums, and social groups",
        "tables": {
            "communities": "コミュニティテーブル",
            "members": "メンバーテーブル"
        },
        "features": ["コミュニティ管理", "メンバー追跡", "議論管理", "通知機能"]
    }
]

# テンプレート（独自プレースホルダー形式）
AGENT_PY_TEMPLATE = '''#!/usr/bin/env python3
"""
__DISPLAY_NAME__
__ENGLISH_NAME__

__DESCRIPTION__
"""

import sqlite3
from datetime import datetime
from typing import Optional, List, Dict

class __CLASS_NAME__:
    """__DISPLAY_NAME__"""

    def __init__(self, db_path: str = "__DB_NAME__.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """データベースを初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # __TABLE1_NAME__テーブル作成
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS __TABLE1_NAME__ (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                data_json TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # __TABLE2_NAME__テーブル作成
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS __TABLE2_NAME__ (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                data_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def add_entry(self, title: str, description: str, data_json: str = "{}") -> int:
        """新しいエントリーを追加"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO __TABLE1_NAME__ (title, description, data_json) VALUES (?, ?, ?)",
            (title, description, data_json)
        )
        conn.commit()
        entry_id = cursor.lastrowid
        conn.close()
        return entry_id

    def get_entry(self, entry_id: int) -> Optional[Dict]:
        """エントリーを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM __TABLE1_NAME__ WHERE id = ?",
            (entry_id,)
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "data_json": row[3],
                "status": row[4],
                "created_at": row[5],
                "updated_at": row[6]
            }
        return None

    def list_entries(self, limit: int = 100) -> List[Dict]:
        """エントリー一覧を取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM __TABLE1_NAME__ ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "data_json": row[3],
                "status": row[4],
                "created_at": row[5],
                "updated_at": row[6]
            }
            for row in rows
        ]

    def update_entry(self, entry_id: int, title: str = None, description: str = None, data_json: str = None) -> bool:
        """エントリーを更新"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        updates = []
        params = []
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        if data_json is not None:
            updates.append("data_json = ?")
            params.append(data_json)

        if not updates:
            conn.close()
            return False

        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(entry_id)

        cursor.execute(
            f"UPDATE __TABLE1_NAME__ SET {', '.join(updates)} WHERE id = ?",
            params
        )
        conn.commit()
        conn.close()
        return True

    def delete_entry(self, entry_id: int) -> bool:
        """エントリーを削除"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM __TABLE1_NAME__ WHERE id = ?", (entry_id,))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0

    def search_entries(self, query: str, limit: int = 50) -> List[Dict]:
        """エントリーを検索"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM __TABLE1_NAME__ WHERE title LIKE ? OR description LIKE ? ORDER BY created_at DESC LIMIT ?",
            (f"%{query}%", f"%{query}%", limit)
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "data_json": row[3],
                "status": row[4],
                "created_at": row[5],
                "updated_at": row[6]
            }
            for row in rows
        ]

    def get_stats(self) -> Dict:
        """統計情報を取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(f"SELECT COUNT(*) FROM __TABLE1_NAME__")
        total_entries = cursor.fetchone()[0]

        cursor.execute(f"SELECT COUNT(*) FROM __TABLE1_NAME__ WHERE status = 'active'")
        active_entries = cursor.fetchone()[0]

        cursor.execute(f"SELECT COUNT(*) FROM __TABLE2_NAME__")
        total_items = cursor.fetchone()[0]

        conn.close()

        return {
            "total_entries": total_entries,
            "active_entries": active_entries,
            "total_items": total_items
        }


def main():
    """メイン関数"""
    agent = __CLASS_NAME__()
    print("__DISPLAY_NAME__ initialized!")
    print("Database:", agent.db_path)

    # サンプルデータ追加
    entry_id = agent.add_entry(
        title="サンプルエントリー",
        description="__DISPLAY_NAME__のサンプルデータ"
    )
    print(f"Added sample entry with ID: {entry_id}")

    # 統計表示
    stats = agent.get_stats()
    print(f"Stats: {stats}")


if __name__ == "__main__":
    main()
'''

DB_PY_TEMPLATE = '''#!/usr/bin/env python3
"""
__DISPLAY_NAME__ データベースモジュール
__ENGLISH_NAME__ Database Module

__ENGLISH_DESCRIPTION__
"""

import sqlite3
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
from datetime import datetime


class __CLASS_NAME__DB:
    """__DISPLAY_NAME__ データベースクラス"""

    def __init__(self, db_path: str = "__DB_NAME__.db"):
        self.db_path = db_path

    @contextmanager
    def get_connection(self):
        """データベース接続のコンテキストマネージャー"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def init_database(self):
        """データベースを初期化"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # __TABLE1_NAME__テーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS __TABLE1_NAME__ (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    data_json TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # __TABLE2_NAME__テーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS __TABLE2_NAME__ (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    data_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # インデックス作成
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx___TABLE1_NAME___status ON __TABLE1_NAME__(status)")
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx___TABLE1_NAME___created ON __TABLE1_NAME__(created_at)")

            conn.commit()

    def insert_entry(self, title: str, description: str = "", data_json: str = "{}", status: str = "active") -> int:
        """エントリーを挿入"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                INSERT INTO __TABLE1_NAME__ (title, description, data_json, status)
                VALUES (?, ?, ?, ?)
                """,
                (title, description, data_json, status)
            )
            conn.commit()
            return cursor.lastrowid

    def get_entry(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """エントリーを取得"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT * FROM __TABLE1_NAME__ WHERE id = ?",
                (entry_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def list_entries(self, limit: int = 100, offset: int = 0, status: str = None) -> List[Dict[str, Any]]:
        """エントリー一覧を取得"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            query = f"SELECT * FROM __TABLE1_NAME__"
            params = []

            if status:
                query += " WHERE status = ?"
                params.append(status)

            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def update_entry(self, entry_id: int, **kwargs) -> bool:
        """エントリーを更新"""
        if not kwargs:
            return False

        with self.get_connection() as conn:
            cursor = conn.cursor()

            update_fields = []
            params = []

            for key, value in kwargs.items():
                if key in ["title", "description", "data_json", "status"]:
                    update_fields.append(f"{key} = ?")
                    params.append(value)

            if not update_fields:
                return False

            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            params.append(entry_id)

            cursor.execute(
                f"UPDATE __TABLE1_NAME__ SET {', '.join(update_fields)} WHERE id = ?",
                params
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete_entry(self, entry_id: int) -> bool:
        """エントリーを削除"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"DELETE FROM __TABLE1_NAME__ WHERE id = ?",
                (entry_id,)
            )
            conn.commit()
            return cursor.rowcount > 0

    def search_entries(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """エントリーを検索"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                SELECT * FROM __TABLE1_NAME__
                WHERE title LIKE ? OR description LIKE ?
                ORDER BY created_at DESC LIMIT ?
                """,
                (f"%{query}%", f"%{query}%", limit)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_stats(self) -> Dict[str, Any]:
        """統計情報を取得"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(f"SELECT COUNT(*) FROM __TABLE1_NAME__")
            total_entries = cursor.fetchone()[0]

            cursor.execute(f"SELECT COUNT(*) FROM __TABLE1_NAME__ WHERE status = 'active'")
            active_entries = cursor.fetchone()[0]

            cursor.execute(f"SELECT COUNT(*) FROM __TABLE2_NAME__")
            total_items = cursor.fetchone()[0]

            return {
                "total_entries": total_entries,
                "active_entries": active_entries,
                "total_items": total_items
            }

    def insert_item(self, name: str, data_json: str = "{}") -> int:
        """アイテムを挿入"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                INSERT INTO __TABLE2_NAME__ (name, data_json)
                VALUES (?, ?)
                """,
                (name, data_json)
            )
            conn.commit()
            return cursor.lastrowid

    def get_items(self, limit: int = 100) -> List[Dict[str, Any]]:
        """アイテム一覧を取得"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT * FROM __TABLE2_NAME__ ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
'''

DISCORD_PY_TEMPLATE = '''#!/usr/bin/env python3
"""
__DISPLAY_NAME__ Discord Bot Module
__ENGLISH_NAME__ Discord Bot

__ENGLISH_DESCRIPTION__
"""

import discord
from discord.ext import commands
from typing import Optional, List
import json


class __CLASS_NAME__Bot(commands.Bot):
    """__DISPLAY_NAME__ Discord Bot"""

    def __init__(self, db_path: str = "__DB_NAME__.db", command_prefix: str = "!"):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=command_prefix, intents=intents)

        self.db_path = db_path

    async def on_ready(self):
        """Bot起動時"""
        print(f'Logged in as {self.user}')

    @commands.command(name='__AGENT_CMD__add')
    async def add_entry(self, ctx, title: str, *, description: str = ""):
        """新しいエントリーを追加"""
        from __AGENT_NAME__ import __CLASS_NAME__
        agent = __CLASS_NAME__(self.db_path)
        entry_id = agent.add_entry(title, description)
        await ctx.send(f"Added entry with ID: {entry_id}")

    @commands.command(name='__AGENT_CMD__list')
    async def list_entries(self, ctx, limit: int = 10):
        """エントリー一覧を表示"""
        from __AGENT_NAME__ import __CLASS_NAME__
        agent = __CLASS_NAME__(self.db_path)
        entries = agent.list_entries(limit)

        if not entries:
            await ctx.send("No entries found.")
            return

        embed = discord.Embed(
            title="__DISPLAY_NAME__ Entries",
            description=f"Showing {len(entries)} entries",
            color=discord.Color.blue()
        )

        for entry in entries:
            embed.add_field(
                name=f"{entry['title']} (ID: {entry['id']})",
                value=entry['description'][:100] or "No description",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name='__AGENT_CMD__get')
    async def get_entry(self, ctx, entry_id: int):
        """エントリーの詳細を表示"""
        from __AGENT_NAME__ import __CLASS_NAME__
        agent = __CLASS_NAME__(self.db_path)
        entry = agent.get_entry(entry_id)

        if not entry:
            await ctx.send(f"Entry with ID {entry_id} not found.")
            return

        embed = discord.Embed(
            title=entry['title'],
            description=entry['description'] or "No description",
            color=discord.Color.green()
        )
        embed.add_field(name="ID", value=entry['id'])
        embed.add_field(name="Status", value=entry['status'])
        embed.add_field(name="Created", value=entry['created_at'])

        await ctx.send(embed=embed)

    @commands.command(name='__AGENT_CMD__search')
    async def search_entries(self, ctx, *, query: str):
        """エントリーを検索"""
        from __AGENT_NAME__ import __CLASS_NAME__
        agent = __CLASS_NAME__(self.db_path)
        entries = agent.search_entries(query)

        if not entries:
            await ctx.send(f"No entries found for query: {query}")
            return

        embed = discord.Embed(
            title=f"Search Results for: {query}",
            description=f"Found {len(entries)} entries",
            color=discord.Color.purple()
        )

        for entry in entries[:10]:
            embed.add_field(
                name=f"{entry['title']} (ID: {entry['id']})",
                value=entry['description'][:100] or "No description",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name='__AGENT_CMD__stats')
    async def get_stats(self, ctx):
        """統計情報を表示"""
        from __AGENT_NAME__ import __CLASS_NAME__
        agent = __CLASS_NAME__(self.db_path)
        stats = agent.get_stats()

        embed = discord.Embed(
            title="__DISPLAY_NAME__ Statistics",
            color=discord.Color.gold()
        )
        embed.add_field(name="Total Entries", value=stats['total_entries'])
        embed.add_field(name="Active Entries", value=stats['active_entries'])
        embed.add_field(name="Total Items", value=stats['total_items'])

        await ctx.send(embed=embed)

    @commands.command(name='__AGENT_CMD__help')
    async def show_help(self, ctx):
        """ヘルプを表示"""
        embed = discord.Embed(
            title="__DISPLAY_NAME__ Commands",
            description="Available commands:",
            color=discord.Color.blue()
        )
        embed.add_field(name="__PREFIX____AGENT_CMD__add <title> [description]", value="Add a new entry", inline=False)
        embed.add_field(name="__PREFIX____AGENT_CMD__list [limit]", value="List entries", inline=False)
        embed.add_field(name="__PREFIX____AGENT_CMD__get <id>", value="Get entry details", inline=False)
        embed.add_field(name="__PREFIX____AGENT_CMD__search <query>", value="Search entries", inline=False)
        embed.add_field(name="__PREFIX____AGENT_CMD__stats", value="Show statistics", inline=False)
        embed.add_field(name="__PREFIX____AGENT_CMD__help", value="Show this help", inline=False)

        await ctx.send(embed=embed)


def main():
    """メイン関数"""
    import os
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        print("DISCORD_TOKEN environment variable not set")
        return

    bot = __CLASS_NAME__Bot()
    bot.run(token)


if __name__ == "__main__":
    main()
'''

README_TEMPLATE = '''# __DISPLAY_NAME__

__ENGLISH_NAME__

## Description / 説明

__DESCRIPTION__

__ENGLISH_DESCRIPTION__

## Features / 機能

- __FEATURE_0__
- __FEATURE_1__
- __FEATURE_2__
- __FEATURE_3__

## Installation / インストール

```bash
pip install -r requirements.txt
```

## Usage / 使用方法

### Python API / Python API

```python
from __AGENT_NAME__ import __CLASS_NAME__

# エージェント初期化 / Initialize agent
agent = __CLASS_NAME__()

# エントリー追加 / Add entry
entry_id = agent.add_entry("タイトル", "説明")

# エントリー取得 / Get entry
entry = agent.get_entry(entry_id)

# エントリー一覧 / List entries
entries = agent.list_entries(limit=10)

# 検索 / Search
results = agent.search_entries("検索クエリ")

# 統計情報 / Statistics
stats = agent.get_stats()
```

### Database / データベース

```python
from __AGENT_NAME__.db import __CLASS_NAME__DB

# データベース初期化 / Initialize database
db = __CLASS_NAME__DB()
db.init_database()

# エントリー挿入 / Insert entry
entry_id = db.insert_entry("タイトル", "説明")

# エントリー取得 / Get entry
entry = db.get_entry(entry_id)
```

### Discord Bot / Discordボット

```python
from __AGENT_NAME__.discord import __CLASS_NAME__Bot

# Bot起動 / Start bot
bot = __CLASS_NAME__Bot(command_prefix="!")
bot.run("YOUR_DISCORD_TOKEN")
```

## Commands / コマンド

| Command / コマンド | Description / 説明 |
|---------------------|---------------------|
| `__PREFIX____AGENT_CMD__add <title> [description]` | 新しいエントリーを追加 / Add new entry |
| `__PREFIX____AGENT_CMD__list [limit]` | エントリー一覧を表示 / List entries |
| `__PREFIX____AGENT_CMD__get <id>` | エントリーの詳細を表示 / Get entry details |
| `__PREFIX____AGENT_CMD__search <query>` | エントリーを検索 / Search entries |
| `__PREFIX____AGENT_CMD__stats` | 統計情報を表示 / Show statistics |
| `__PREFIX____AGENT_CMD__help` | ヘルプを表示 / Show help |

## Database Schema / データベース構造

### __TABLE1_NAME__ / __TABLE1_JP__

| Column / カラム | Type / 型 | Description / 説明 |
|------------------|-----------|---------------------|
| id | INTEGER | Primary Key / 主キー |
| title | TEXT | Title / タイトル |
| description | TEXT | Description / 説明 |
| data_json | TEXT | JSON Data / JSONデータ |
| status | TEXT | Status / ステータス |
| created_at | TIMESTAMP | Created Time / 作成日時 |
| updated_at | TIMESTAMP | Updated Time / 更新日時 |

### __TABLE2_NAME__ / __TABLE2_JP__

| Column / カラム | Type / 型 | Description / 説明 |
|------------------|-----------|---------------------|
| id | INTEGER | Primary Key / 主キー |
| name | TEXT | Name / 名前 |
| data_json | TEXT | JSON Data / JSONデータ |
| created_at | TIMESTAMP | Created Time / 作成日時 |
| updated_at | TIMESTAMP | Updated Time / 更新日時 |

## Project Structure / プロジェクト構造

```
__AGENT_NAME__/
├── agent.py          # エージェント本体 / Main agent
├── db.py            # データベースモジュール / Database module
├── discord.py       # Discord Bot / Discord Bot
├── README.md        # このファイル / This file
└── requirements.txt # 依存パッケージ / Dependencies
```

## License / ライセンス

MIT License
'''

REQUIREMENTS_TEMPLATE = '''discord.py>=2.3.0
'''

def to_class_name(agent_name: str) -> str:
    """エージェント名をクラス名に変換"""
    parts = agent_name.replace('-', ' ').split()
    return ''.join(p.capitalize() for p in parts)

def to_agent_cmd(agent_name: str) -> str:
    """エージェント名をコマンド名に変換"""
    return agent_name.replace('erotic-', '').replace('-', '')

def create_agent(agent_info: dict):
    """エージェントを作成"""
    agent_name = agent_info["name"]
    display_name = agent_info["display_name"]
    english_name = agent_info["english_name"]
    description = agent_info["description"]
    english_description = agent_info["english_description"]
    tables = agent_info["tables"]
    features = agent_info["features"]

    # ディレクトリ作成
    agent_dir = f"agents/{agent_name}"
    os.makedirs(agent_dir, exist_ok=True)

    db_name = agent_name
    class_name = to_class_name(agent_name)
    table1_name = list(tables.keys())[0]
    table2_name = list(tables.keys())[1]
    table1_jp = list(tables.values())[0]
    table2_jp = list(tables.values())[1]
    agent_cmd = to_agent_cmd(agent_name)
    prefix = "!"

    # agent.py 作成（replace方式）
    agent_py = AGENT_PY_TEMPLATE
    agent_py = agent_py.replace("__DISPLAY_NAME__", display_name)
    agent_py = agent_py.replace("__ENGLISH_NAME__", english_name)
    agent_py = agent_py.replace("__DESCRIPTION__", description)
    agent_py = agent_py.replace("__ENGLISH_DESCRIPTION__", english_description)
    agent_py = agent_py.replace("__CLASS_NAME__", class_name)
    agent_py = agent_py.replace("__DB_NAME__", db_name)
    agent_py = agent_py.replace("__TABLE1_NAME__", table1_name)
    agent_py = agent_py.replace("__TABLE2_NAME__", table2_name)

    with open(f"{agent_dir}/{agent_name}.py", "w", encoding="utf-8") as f:
        f.write(agent_py)

    # db.py 作成（replace方式）
    db_py = DB_PY_TEMPLATE
    db_py = db_py.replace("__DISPLAY_NAME__", display_name)
    db_py = db_py.replace("__ENGLISH_NAME__", english_name)
    db_py = db_py.replace("__ENGLISH_DESCRIPTION__", english_description)
    db_py = db_py.replace("__CLASS_NAME__", class_name)
    db_py = db_py.replace("__DB_NAME__", db_name)
    db_py = db_py.replace("__TABLE1_NAME__", table1_name)
    db_py = db_py.replace("__TABLE2_NAME__", table2_name)

    with open(f"{agent_dir}/db.py", "w", encoding="utf-8") as f:
        f.write(db_py)

    # discord.py 作成（replace方式）
    discord_py = DISCORD_PY_TEMPLATE
    discord_py = discord_py.replace("__DISPLAY_NAME__", display_name)
    discord_py = discord_py.replace("__ENGLISH_NAME__", english_name)
    discord_py = discord_py.replace("__ENGLISH_DESCRIPTION__", english_description)
    discord_py = discord_py.replace("__CLASS_NAME__", class_name)
    discord_py = discord_py.replace("__DB_NAME__", db_name)
    discord_py = discord_py.replace("__AGENT_NAME__", agent_name)
    discord_py = discord_py.replace("__AGENT_CMD__", agent_cmd)
    discord_py = discord_py.replace("__PREFIX__", prefix)

    with open(f"{agent_dir}/discord.py", "w", encoding="utf-8") as f:
        f.write(discord_py)

    # README.md 作成（replace方式）
    readme = README_TEMPLATE
    readme = readme.replace("__DISPLAY_NAME__", display_name)
    readme = readme.replace("__ENGLISH_NAME__", english_name)
    readme = readme.replace("__DESCRIPTION__", description)
    readme = readme.replace("__ENGLISH_DESCRIPTION__", english_description)
    readme = readme.replace("__FEATURE_0__", features[0])
    readme = readme.replace("__FEATURE_1__", features[1])
    readme = readme.replace("__FEATURE_2__", features[2])
    readme = readme.replace("__FEATURE_3__", features[3])
    readme = readme.replace("__AGENT_NAME__", agent_name)
    readme = readme.replace("__CLASS_NAME__", class_name)
    readme = readme.replace("__TABLE1_NAME__", table1_name)
    readme = readme.replace("__TABLE2_NAME__", table2_name)
    readme = readme.replace("__TABLE1_JP__", table1_jp)
    readme = readme.replace("__TABLE2_JP__", table2_jp)
    readme = readme.replace("__AGENT_CMD__", agent_cmd)
    readme = readme.replace("__PREFIX__", prefix)

    with open(f"{agent_dir}/README.md", "w", encoding="utf-8") as f:
        f.write(readme)

    # requirements.txt 作成
    with open(f"{agent_dir}/requirements.txt", "w", encoding="utf-8") as f:
        f.write(REQUIREMENTS_TEMPLATE)

    print(f"Created agent: {agent_name}")

    return agent_dir

def main():
    """メイン関数"""
    print("=" * 60)
    print("エロティックコンテンツ関連エージェントV4オーケストレーター")
    print("Erotic Content Agents V4 Orchestrator")
    print("=" * 60)
    print(f"開始時刻: {datetime.now().isoformat()}")
    print()

    # 進捗管理用JSON
    progress_file = "erotic_v4_progress.json"
    progress = {
        "project_name": "エロティックコンテンツ関連エージェントV4プロジェクト",
        "start_time": datetime.now().isoformat(),
        "agents": AGENTS,
        "completed": [],
        "failed": [],
        "status": "running"
    }

    # 各エージェントを作成
    for agent_info in AGENTS:
        try:
            agent_dir = create_agent(agent_info)
            progress["completed"].append(agent_info["name"])
            print(f"  OK: {agent_dir}")
        except Exception as e:
            progress["failed"].append({"name": agent_info["name"], "error": str(e)})
            print(f"  FAILED: {agent_info['name']} - {e}")

    # 進捗保存
    with open(progress_file, "w", encoding="utf-8") as f:
        progress["end_time"] = datetime.now().isoformat()
        progress["status"] = "completed" if not progress["failed"] else "partial"
        json.dump(progress, f, ensure_ascii=False, indent=2)

    print()
    print("=" * 60)
    print(f"完了: {len(progress['completed'])}/{len(AGENTS)} エージェント")
    if progress["failed"]:
        print(f"失敗: {len(progress['failed'])} エージェント")
        for failed in progress["failed"]:
            print(f"  - {failed['name']}: {failed['error']}")
    print("=" * 60)
    print(f"進捗ファイル: {progress_file}")

    # Git commit
    print()
    print("Git commit...")
    try:
        subprocess.run(["git", "add", "-A"], check=True)
        subprocess.run([
            "git", "commit", "-m",
            "feat: エロティックコンテンツ関連エージェントV4プロジェクト完了 (5/5)"
        ], check=True)
        subprocess.run(["git", "push"], check=True)
        print("Git commit & push 完了")
    except subprocess.CalledProcessError as e:
        print(f"Git commit 失敗: {e}")

if __name__ == "__main__":
    main()
