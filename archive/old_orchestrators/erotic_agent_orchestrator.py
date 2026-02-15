#!/usr/bin/env python3
"""
エロティックコンテンツ管理エージェントオーケストレーター
ユーザーの興味（えっちな女の子）に合わせたコンテンツ管理エージェントを作成

Author: ななたう
Date: 2026-02-12
"""

import os
import json
from datetime import datetime
from pathlib import Path

# エージェント情報
PROJECT_NAME = "erotic_content_agents"
PROJECT_TITLE = "エロティックコンテンツ管理エージェントプロジェクト"

AGENTS = [
    {
        "name": "erotic-artwork-agent",
        "title": "えっちなイラスト・アート管理エージェント",
        "description": "えっちなイラストやアートワークを管理・整理するエージェント",
        "emoji": "🎨"
    },
    {
        "name": "erotic-fanart-agent",
        "title": "えっちなファンアートコレクションエージェント",
        "description": "えっちなファンアートをコレクション管理するエージェント",
        "emoji": "🖼️"
    },
    {
        "name": "erotic-character-agent",
        "title": "お気に入りのえっちなキャラ管理エージェント",
        "description": "お気に入りのえっちなキャラクターを管理するエージェント",
        "emoji": "💕"
    },
    {
        "name": "erotic-artist-agent",
        "title": "えっちなイラストレーター管理エージェント",
        "description": "えっちなイラストレーターを管理・追跡するエージェント",
        "emoji": "👨‍🎨"
    },
    {
        "name": "erotic-tag-agent",
        "title": "えっちなコンテンツのタグ・検索管理エージェント",
        "description": "えっちなコンテンツのタグ付け・検索機能を提供するエージェント",
        "emoji": "🏷️"
    }
]

# テンプレート
AGENT_TEMPLATE = '''#!/usr/bin/env python3
"""
{title}

{description}
"""

import sqlite3
from datetime import datetime
from pathlib import Path

class {class_name}:
    """{title}"""

    def __init__(self, db_path: str = None):
        """初期化"""
        self.db_path = db_path or Path(__file__).parent / "erotic_content.db"
        self.conn = None
        self._init_db()

    def _init_db(self):
        """データベース初期化"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

        # テーブル作成
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                source TEXT,
                url TEXT,
                tags TEXT,
                rating INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # タグテーブル
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                count INTEGER DEFAULT 0
            )
        """)

        self.conn.commit()

    def add_entry(self, title: str, description: str = "", source: str = "", url: str = "", tags: str = "") -> int:
        """エントリー追加"""
        now = datetime.now().isoformat()
        cursor = self.conn.execute("""
            INSERT INTO entries (title, description, source, url, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (title, description, source, url, tags, now, now))
        self.conn.commit()
        return cursor.lastrowid

    def get_entry(self, entry_id: int) -> dict:
        """エントリー取得"""
        row = self.conn.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()
        return dict(row) if row else None

    def list_entries(self, limit: int = 50, offset: int = 0) -> list:
        """エントリー一覧"""
        rows = self.conn.execute("""
            SELECT * FROM entries ORDER BY created_at DESC LIMIT ? OFFSET ?
        """, (limit, offset)).fetchall()
        return [dict(row) for row in rows]

    def search_entries(self, query: str) -> list:
        """エントリー検索"""
        rows = self.conn.execute("""
            SELECT * FROM entries
            WHERE title LIKE ? OR description LIKE ? OR tags LIKE ?
            ORDER BY created_at DESC
        """, (f"%{{query}}%", f"%{{query}}%", f"%{{query}}%")).fetchall()
        return [dict(row) for row in rows]

    def update_entry(self, entry_id: int, **kwargs) -> bool:
        """エントリー更新"""
        valid_fields = ["title", "description", "source", "url", "tags", "rating"]
        updates = dict((k, v) for k, v in kwargs.items() if k in valid_fields)

        if not updates:
            return False

        updates["updated_at"] = datetime.now().isoformat()
        set_clause = ", ".join([str(k) + " = ?" for k in updates.keys()])

        self.conn.execute(f"""
            UPDATE entries SET {{set_clause}}, updated_at = ? WHERE id = ?
        """, list(updates.values()) + [entry_id])
        self.conn.commit()
        return True

    def delete_entry(self, entry_id: int) -> bool:
        """エントリー削除"""
        self.conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
        self.conn.commit()
        return True

    def get_stats(self) -> dict:
        """統計情報取得"""
        total = self.conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
        avg_rating = self.conn.execute("SELECT AVG(rating) FROM entries WHERE rating > 0").fetchone()[0] or 0
        return dict((
            ("total_entries", total),
            ("average_rating", round(avg_rating, 2))
        ))

    def close(self):
        """接続終了"""
        if self.conn:
            self.conn.close()

    def __del__(self):
        """デストラクタ"""
        self.close()


if __name__ == "__main__":
    agent = {class_name}()

    # テストエントリー追加
    agent.add_entry(
        title="サンプルエントリー",
        description="これはサンプルのエントリーです",
        source="test",
        tags="サンプル,テスト"
    )

    # エントリー一覧表示
    entries = agent.list_entries()
    for entry in entries:
        print(str(entry['id']) + ": " + str(entry['title']))

    # 統計情報表示
    stats = agent.get_stats()
    print("\\n統計: " + str(stats))
'''

DB_TEMPLATE = '''#!/usr/bin/env python3
"""
{title} - データベースモジュール

SQLiteを使用したデータ永続化機能
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager


class {class_name}DB:
    """{title} データベースクラス"""

    def __init__(self, db_path: Optional[str] = None):
        """初期化"""
        self.db_path = Path(db_path) if db_path else Path(__file__).parent / "{name}.db"

    @contextmanager
    def _get_connection(self):
        """データベース接続コンテキストマネージャー"""
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

    def initialize(self) -> None:
        """データベース初期化"""
        with self._get_connection() as conn:
            # entriesテーブル
            conn.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    source TEXT,
                    url TEXT,
                    tags TEXT,
                    rating INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(title, source)
                )
            """)

            # タグテーブル
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # インデックス作成
            conn.execute("CREATE INDEX IF NOT EXISTS idx_entries_title ON entries(title)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_entries_created ON entries(created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_entries_tags ON entries(tags)")

    def add_entry(self, title: str, description: str = "", source: str = "",
                  url: str = "", tags: str = "", rating: int = 0) -> int:
        """エントリー追加"""
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT OR REPLACE INTO entries
                (title, description, source, url, tags, rating, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, COALESCE((SELECT created_at FROM entries WHERE title = ? AND source = ?), ?), ?)
            """, (title, description, source, url, tags, rating, title, source, now, now))
            return cursor.lastrowid

    def get_entry(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """エントリー取得"""
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()
            return dict(row) if row else None

    def list_entries(self, limit: int = 50, offset: int = 0,
                     sort_by: str = "created_at", order: str = "DESC") -> List[Dict[str, Any]]:
        """エントリー一覧"""
        valid_sort = ["id", "title", "rating", "created_at", "updated_at"]
        valid_order = ["ASC", "DESC"]

        sort_by = sort_by if sort_by in valid_sort else "created_at"
        order = order.upper() if order.upper() in valid_order else "DESC"

        with self._get_connection() as conn:
            query = f"""
                SELECT * FROM entries
                ORDER BY {{sort_by}} {{order}}
                LIMIT ? OFFSET ?
            """
            rows = conn.execute(query, (limit, offset)).fetchall()
            return [dict(row) for row in rows]

    def search_entries(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """エントリー検索"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM entries
                WHERE title LIKE ? OR description LIKE ? OR tags LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (f"%{{query}}%", f"%{{query}}%", f"%{{query}}%", limit)).fetchall()
            return [dict(row) for row in rows]

    def get_entries_by_tag(self, tag: str, limit: int = 50) -> List[Dict[str, Any]]:
        """タグでエントリー取得"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM entries
                WHERE tags LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (f"%{{tag}}%", limit)).fetchall()
            return [dict(row) for row in rows]

    def update_entry(self, entry_id: int, **kwargs) -> bool:
        """エントリー更新"""
        valid_fields = ["title", "description", "source", "url", "tags", "rating"]
        updates = dict((k, v) for k, v in kwargs.items() if k in valid_fields)

        if not updates:
            return False

        updates["updated_at"] = datetime.now().isoformat()
        set_clause = ", ".join([str(k) + " = ?" for k in updates.keys()])

        with self._get_connection() as conn:
            query = f"""
                UPDATE entries SET {{set_clause}}, updated_at = ? WHERE id = ?
            """
            cursor = conn.execute(query, list(updates.values()) + [entry_id])
            return cursor.rowcount > 0

    def delete_entry(self, entry_id: int) -> bool:
        """エントリー削除"""
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
            return cursor.rowcount > 0

    def get_stats(self) -> Dict[str, Any]:
        """統計情報取得"""
        with self._get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
            avg_rating = conn.execute(
                "SELECT AVG(rating) FROM entries WHERE rating > 0"
            ).fetchone()[0] or 0
            top_rated = conn.execute("""
                SELECT title, rating FROM entries
                WHERE rating > 0 ORDER BY rating DESC LIMIT 5
            """).fetchall()

            return dict((
                ("total_entries", total),
                ("average_rating", round(avg_rating, 2)),
                ("top_rated", [dict(row) for row in top_rated])
            ))

    def add_tag(self, name: str) -> int:
        """タグ追加"""
        with self._get_connection() as conn:
            now = datetime.now().isoformat()
            cursor = conn.execute("""
                INSERT OR IGNORE INTO tags (name, created_at) VALUES (?, ?)
            """, (name, now))
            if cursor.rowcount > 0:
                return cursor.lastrowid

            # 既存の場合、カウント増加
            conn.execute("UPDATE tags SET count = count + 1 WHERE name = ?", (name,))
            row = conn.execute("SELECT id FROM tags WHERE name = ?", (name,)).fetchone()
            return row["id"] if row else 0

    def list_tags(self, limit: int = 100) -> List[Dict[str, Any]]:
        """タグ一覧"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM tags ORDER BY count DESC, name ASC LIMIT ?
            """, (limit,)).fetchall()
            return [dict(row) for row in rows]


if __name__ == "__main__":
    db = {class_name}DB()
    db.initialize()

    # テスト
    db.add_entry(
        title="サンプルエントリー",
        description="これはサンプルです",
        source="test",
        tags="サンプル,テスト"
    )

    entries = db.list_entries()
    print("エントリー数: " + str(len(entries)))

    stats = db.get_stats()
    print("統計: " + str(stats))
'''

DISCORD_TEMPLATE = '''#!/usr/bin/env python3
"""
{title} - Discord Botモジュール

Discordを介したエージェント操作インターフェース
"""

import discord
from discord.ext import commands
from typing import Optional
import asyncio

from db import {class_name}DB


class {class_name}Bot(commands.Bot):
    """{title} Discord Bot"""

    def __init__(self, db_path: str = None, command_prefix: str = "!"):
        """初期化"""
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(
            command_prefix=command_prefix,
            intents=intents,
            help_command=None
        )
        self.db = {class_name}DB(db_path)
        self.db.initialize()

    async def setup_hook(self):
        """Bot起動時の処理"""
        print(str(self.user) + " が起動しました")

    async def on_ready(self):
        """Bot準備完了時の処理"""
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="えっちなコンテンツ"
        )
        await self.change_presence(activity=activity)
        print(str(self.user.name) + " が準備完了しました")

    async def on_command_error(self, ctx: commands.Context, error: Exception):
        """コマンドエラー処理"""
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("❌ そのコマンドは存在しません")
        else:
            await ctx.send("❌ エラーが発生しました: " + str(error))


# Botインスタンス
bot = None


def get_bot(db_path: str = None, command_prefix: str = "!"):
    """Botインスタンス取得"""
    global bot
    if bot is None:
        bot = {class_name}Bot(db_path, command_prefix)

        # コマンド登録
        @bot.command(name="追加", aliases=["add"])
        async def add_entry(ctx: commands.Context, title: str, *, description: str = ""):
            """エントリー追加"""
            entry_id = bot.db.add_entry(title=title, description=description, source="discord")
            embed = discord.Embed(
                title="✅ エントリー追加完了",
                description="ID: " + str(entry_id) + "\\nタイトル: " + str(title),
                color=0x00ff00
            )
            await ctx.send(embed=embed)

        @bot.command(name="検索", aliases=["search", "find"])
        async def search_entries(ctx: commands.Context, *, query: str):
            """エントリー検索"""
            entries = bot.db.search_entries(query, limit=10)

            if not entries:
                await ctx.send("🔍 該当するエントリーが見つかりませんでした")
                return

            embed = discord.Embed(
                title="🔍 検索結果: " + str(query),
                description=str(len(entries)) + "件見つかりました",
                color=0x00aaff
            )

            for entry in entries[:5]:
                desc = entry.get("description", "")[:50] + "..." if len(entry.get("description", "")) > 50 else entry.get("description", "")
                embed.add_field(
                    name=str(entry['id']) + ": " + str(entry['title']),
                    value=desc or "説明なし",
                    inline=False
                )

            await ctx.send(embed=embed)

        @bot.command(name="一覧", aliases=["list", "ls"])
        async def list_entries(ctx: commands.Context, limit: int = 10):
            """エントリー一覧"""
            entries = bot.db.list_entries(limit=limit)

            if not entries:
                await ctx.send("📋 エントリーがまだありません")
                return

            embed = discord.Embed(
                title="📋 エントリー一覧 (最新" + str(limit) + "件)",
                color=0xffaa00
            )

            for entry in entries:
                desc = entry.get("description", "")[:30] + "..." if len(entry.get("description", "")) > 30 else entry.get("description", "")
                embed.add_field(
                    name=str(entry['id']) + ": " + str(entry['title']),
                    value=desc or "説明なし",
                    inline=False
                )

            await ctx.send(embed=embed)

        @bot.command(name="詳細", aliases=["detail", "info"])
        async def get_detail(ctx: commands.Context, entry_id: int):
            """エントリー詳細"""
            entry = bot.db.get_entry(entry_id)

            if not entry:
                await ctx.send("❌ ID " + str(entry_id) + " のエントリーが見つかりません")
                return

            embed = discord.Embed(
                title="📖 " + str(entry['title']),
                description=entry.get("description", "説明なし") or "説明なし",
                color=0xff00ff
            )
            embed.add_field(name="ソース", value=entry.get("source", "なし") or "なし", inline=True)
            embed.add_field(name="評価", value="⭐ " + str(entry.get('rating', 0)) or "⭐ 0", inline=True)
            if entry.get("tags"):
                embed.add_field(name="タグ", value=entry.get("tags"), inline=False)
            embed.add_field(name="作成日", value=entry.get("created_at", "")[:10], inline=True)

            await ctx.send(embed=embed)

        @bot.command(name="タグ検索", aliases=["tag"])
        async def search_by_tag(ctx: commands.Context, tag: str):
            """タグで検索"""
            entries = bot.db.get_entries_by_tag(tag, limit=10)

            if not entries:
                await ctx.send("🏷️ タグ「" + str(tag) + "」のエントリーが見つかりません")
                return

            embed = discord.Embed(
                title="🏷️ タグ「" + str(tag) + "」の結果",
                description=str(len(entries)) + "件見つかりました",
                color=0x00aaff
            )

            for entry in entries[:5]:
                embed.add_field(
                    name=str(entry['id']) + ": " + str(entry['title']),
                    value=entry.get("description", "")[:30] or "説明なし",
                    inline=False
                )

            await ctx.send(embed=embed)

        @bot.command(name="統計", aliases=["stats", "stat"])
        async def get_stats(ctx: commands.Context):
            """統計情報"""
            stats = bot.db.get_stats()

            embed = discord.Embed(
                title="📊 統計情報",
                color=0xffaa00
            )
            embed.add_field(name="総エントリー数", value=str(stats['total_entries']) + "件", inline=True)
            embed.add_field(name="平均評価", value="⭐ " + str(stats['average_rating']), inline=True)

            if stats.get("top_rated"):
                top_list = "\\n".join([str(i+1) + ". " + str(r['title']) + " (⭐" + str(r['rating']) + ")" for i, r in enumerate(stats['top_rated'][:3])])
                embed.add_field(name="🏆 高評価TOP3", value=top_list, inline=False)

            await ctx.send(embed=embed)

        @bot.command(name="削除", aliases=["delete", "rm"])
        async def delete_entry(ctx: commands.Context, entry_id: int):
            """エントリー削除"""
            entry = bot.db.get_entry(entry_id)

            if not entry:
                await ctx.send("❌ ID " + str(entry_id) + " のエントリーが見つかりません")
                return

            if bot.db.delete_entry(entry_id):
                embed = discord.Embed(
                    title="🗑️ 削除完了",
                    description="ID " + str(entry_id) + ": " + str(entry['title']) + " を削除しました",
                    color=0xff0000
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ 削除に失敗しました")

        @bot.command(name="ヘルプ", aliases=["help", "?"])
        async def show_help(ctx: commands.Context):
            """ヘルプ表示"""
            embed = discord.Embed(
                title="🤖 " + str(bot.user.name) + " コマンド一覧",
                description="{title}の使い方",
                color=0x00aaff
            )

            commands_list = [
                ("!追加 <タイトル> [説明]", "エントリーを追加"),
                ("!検索 <キーワード>", "キーワードで検索"),
                ("!一覧 [件数]", "エントリー一覧を表示"),
                ("!詳細 <ID>", "指定IDの詳細を表示"),
                ("!タグ検索 <タグ名>", "タグで検索"),
                ("!統計", "統計情報を表示"),
                ("!削除 <ID>", "エントリーを削除"),
                ("!ヘルプ", "このヘルプを表示")
            ]

            for cmd, desc in commands_list:
                embed.add_field(name=cmd, value=desc, inline=False)

            await ctx.send(embed=embed)

    return bot


def run_bot(token: str, db_path: str = None, command_prefix: str = "!"):
    """Bot実行"""
    bot = get_bot(db_path, command_prefix)
    bot.run(token)


if __name__ == "__main__":
    import os

    # 環境変数からトークン取得
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("DISCORD_TOKEN 環境変数を設定してください")
        exit(1)

    run_bot(token)
'''

README_TEMPLATE = '''# {name}

{description}

{emoji}

## 機能

- エントリーの追加・編集・削除
- キーワード検索
- タグによるフィルタリング
- 評価機能
- 統計情報の表示
- Discord Botからの操作

## インストール

```bash
pip install -r requirements.txt
```

## 使い方

### Python API

```python
from db import {class_name}DB

# データベース初期化
db = {class_name}DB()
db.initialize()

# エントリー追加
db.add_entry(
    title="サンプル",
    description="これはサンプルです",
    source="test",
    tags="サンプル,テスト"
)

# エントリー検索
entries = db.search_entries("サンプル")
for entry in entries:
    print(str(entry['title']) + ": " + str(entry['description']))

# 統計情報
stats = db.get_stats()
print("総エントリー数: " + str(stats['total_entries']))
```

### Discord Bot

```bash
export DISCORD_TOKEN="your_bot_token"
python discord.py
```

## Discordコマンド

| コマンド | 説明 |
|----------|------|
| `!追加 <タイトル> [説明]` | エントリーを追加 |
| `!検索 <キーワード>` | キーワードで検索 |
| `!一覧 [件数]` | エントリー一覧を表示 |
| `!詳細 <ID>` | 指定IDの詳細を表示 |
| `!タグ検索 <タグ名>` | タグで検索 |
| `!統計` | 統計情報を表示 |
| `!削除 <ID>` | エントリーを削除 |
| `!ヘルプ` | ヘルプを表示 |

## データベース構造

### entriesテーブル

| カラム | 型 | 説明 |
|--------|------|------|
| id | INTEGER | 主キー |
| title | TEXT | タイトル |
| description | TEXT | 説明 |
| source | TEXT | ソース |
| url | TEXT | URL |
| tags | TEXT | タグ（カンマ区切り） |
| rating | INTEGER | 評価 (0-5) |
| created_at | TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | 更新日時 |

### tagsテーブル

| カラム | 型 | 説明 |
|--------|------|------|
| id | INTEGER | 主キー |
| name | TEXT | タグ名 |
| count | INTEGER | 使用回数 |
| created_at | TIMESTAMP | 作成日時 |

## ライセンス

MIT

---

# {name} (English)

{description_en}

{emoji}

## Features

- Add, edit, and delete entries
- Keyword search
- Filter by tags
- Rating system
- Statistics display
- Discord Bot control

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Python API

```python
from db import {class_name}DB

# Initialize database
db = {class_name}DB()
db.initialize()

# Add entry
db.add_entry(
    title="Sample",
    description="This is a sample",
    source="test",
    tags="sample,test"
)

# Search entries
entries = db.search_entries("sample")
for entry in entries:
    print(str(entry['title']) + ": " + str(entry['description']))

# Statistics
stats = db.get_stats()
print("Total entries: " + str(stats['total_entries']))
```

### Discord Bot

```bash
export DISCORD_TOKEN="your_bot_token"
python discord.py
```

## Discord Commands

| Command | Description |
|---------|-------------|
| `!add <title> [description]` | Add an entry |
| `!search <keyword>` | Search by keyword |
| `!list [count]` | List entries |
| `!detail <id>` | Show entry details |
| `!tag <tagname>` | Search by tag |
| `!stats` | Show statistics |
| `!delete <id>` | Delete an entry |
| `!help` | Show help |

## License

MIT
'''

REQUIREMENTS_TEMPLATE = '''discord.py>=2.3.0
'''

PROJECT_JSON_TEMPLATE = """{
    "name": "{name}",
    "title": "{title}",
    "description": "{description}",
    "agents": {agent_count},
    "created_at": "2026-02-12",
    "status": "completed"
}"""

PROGRESS_JSON_TEMPLATE = """{
    "project": "{name}",
    "total": {agent_count},
    "completed": 0,
    "failed": 0,
    "agents": [],
    "started_at": null,
    "completed_at": null
}"""


def snake_to_camel(name: str) -> str:
    """スネークケースをキャメルケースに変換"""
    return ''.join(word.capitalize() for word in name.replace('-', '_').split('_'))


def create_agent(agent_info: dict) -> dict:
    """エージェント作成"""
    name = agent_info["name"]
    title = agent_info["title"]
    description = agent_info["description"]
    class_name = snake_to_camel(name)
    agent_dir = Path("agents") / name

    result = {
        "name": name,
        "status": "pending",
        "files": []
    }

    try:
        # ディレクトリ作成
        agent_dir.mkdir(parents=True, exist_ok=True)
        print("📁 ディレクトリ作成: {}".format(agent_dir))

        # agent.py作成
        agent_file = agent_dir / "agent.py"
        agent_file.write_text(AGENT_TEMPLATE.format(
            title=title,
            description=description,
            class_name=class_name
        ), encoding="utf-8")
        result["files"].append("agent.py")
        print("  ✅ agent.py")

        # db.py作成
        db_file = agent_dir / "db.py"
        db_file.write_text(DB_TEMPLATE.format(
            title=title,
            class_name=class_name,
            name=name
        ), encoding="utf-8")
        result["files"].append("db.py")
        print("  ✅ db.py")

        # discord.py作成
        discord_file = agent_dir / "discord.py"
        discord_file.write_text(DISCORD_TEMPLATE.format(
            title=title,
            class_name=class_name,
            name=name
        ), encoding="utf-8")
        result["files"].append("discord.py")
        print("  ✅ discord.py")

        # README.md作成
        readme_file = agent_dir / "README.md"
        readme_file.write_text(README_TEMPLATE.format(
            name=name,
            title=title,
            description=description,
            description_en=description.replace("エージェント", "Agent"),
            class_name=class_name,
            emoji=agent_info.get("emoji", "🤖")
        ), encoding="utf-8")
        result["files"].append("README.md")
        print("  ✅ README.md")

        # requirements.txt作成
        req_file = agent_dir / "requirements.txt"
        req_file.write_text(REQUIREMENTS_TEMPLATE, encoding="utf-8")
        result["files"].append("requirements.txt")
        print("  ✅ requirements.txt")

        result["status"] = "completed"
        return result

    except Exception as e:
        import traceback
        print("  ❌ エラー: {}".format(e))
        traceback.print_exc()
        result["status"] = "failed"
        result["error"] = str(e)
        return result


def main():
    """メイン処理"""
    print("\n" + "="*60)
    print(PROJECT_TITLE)
    print("="*60 + "\n")

    # 進捗管理ファイル初期化
    progress_file = Path("erotic_agent_progress.json")
    if progress_file.exists():
        with open(progress_file, "r", encoding="utf-8") as f:
            progress = json.load(f)
    else:
        progress = json.loads(PROGRESS_JSON_TEMPLATE.format(
            name=PROJECT_NAME,
            agent_count=len(AGENTS)
        ))
        progress["started_at"] = datetime.now().isoformat()

    total = len(AGENTS)
    completed = 0
    failed = 0

    # 各エージェント作成
    for i, agent_info in enumerate(AGENTS, 1):
        print("\n[{}/{}] {} {}".format(i, total, agent_info['emoji'], agent_info['title']))

        result = create_agent(agent_info)
        progress["agents"].append(result)

        if result["status"] == "completed":
            completed += 1
        else:
            failed += 1

    # 進捗更新
    progress["completed"] = completed
    progress["failed"] = failed
    progress["completed_at"] = datetime.now().isoformat()

    with open(progress_file, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

    # プロジェクト設定ファイル作成
    project_file = Path("erotic_agent_project.json")
    project_data = {
        "name": PROJECT_NAME,
        "title": PROJECT_TITLE,
        "description": "ユーザーの興味（えっちな女の子）に合わせたコンテンツ管理エージェント",
        "agents": len(AGENTS),
        "created_at": "2026-02-12",
        "status": "completed"
    }
    with open(project_file, "w", encoding="utf-8") as f:
        json.dump(project_data, f, ensure_ascii=False, indent=2)

    # 結果サマリ
    print("\n" + "="*60)
    print("📊 プロジェクト完了サマリ")
    print("="*60)
    print("✅ 完了: {}/{}".format(completed, total))
    if failed > 0:
        print("❌ 失敗: {}/{}".format(failed, total))
    print("📈 完了率: {:.1f}%".format(completed/total*100))
    print("="*60 + "\n")

    # 作成したエージェント一覧
    print("作成したエージェント:")
    for agent in progress["agents"]:
        status = "✅" if agent["status"] == "completed" else "❌"
        print("  {} {}".format(status, agent['name']))


if __name__ == "__main__":
    main()
