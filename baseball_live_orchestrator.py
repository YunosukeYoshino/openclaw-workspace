#!/usr/bin/env python3
"""
野球ライブ配信エージェントオーケストレーター

野球のライブ配信、実況、ハイライトを管理するエージェントを自律的に作成する。
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime

# 設定
WORKSPACE = Path("/workspace")
AGENTS_DIR = WORKSPACE / "agents"
PROGRESS_FILE = WORKSPACE / "baseball_live_progress.json"

# エージェント定義
AGENTS = [
    {
        "name": "baseball-live-schedule-agent",
        "title": "野球ライブ配信スケジュールエージェント",
        "description": {
            "en": "Manages live baseball game schedules and streaming availability",
            "ja": "野球試合のライブ配信スケジュールと視聴可能時間を管理します"
        },
        "search_tag": "baseball live schedule",
        "features": [
            "Live game schedule tracking",
            "Streaming platform integration",
            "Game time reminders",
            "Channel availability check",
            "Multi-platform schedule sync"
        ],
        "commands": [
            "schedule today - Show today's live games",
            "schedule week - Show this week's games",
            "schedule team <team> - Show games for a team",
            "remind <game_id> - Set reminder for a game"
        ]
    },
    {
        "name": "baseball-live-highlights-agent",
        "title": "野球ライブハイライトエージェント",
        "description": {
            "en": "Creates and manages highlights from live baseball games",
            "ja": "ライブ野球中継からハイライトを作成・管理します"
        },
        "search_tag": "baseball highlights",
        "features": [
            "Auto highlight extraction",
            "Key moment detection",
            "Highlight categorization",
            "Clip management",
            "Social media sharing"
        ],
        "commands": [
            "highlights game <game_id> - Get game highlights",
            "highlights player <player> - Get player highlights",
            "highlights trending - Show trending highlights",
            "highlights create - Create custom highlight"
        ]
    },
    {
        "name": "baseball-live-commentary-agent",
        "title": "野球実況コメント分析エージェント",
        "description": {
            "en": "Analyzes commentary and chat from live baseball broadcasts",
            "ja": "野球ライブ中継の実況とコメントを分析します"
        },
        "search_tag": "baseball commentary",
        "features": [
            "Commentary sentiment analysis",
            "Key event extraction",
            "Fan reaction tracking",
            "Commentary summary",
            "Popular moment detection"
        ],
        "commands": [
            "commentary game <game_id> - Analyze commentary",
            "commentary sentiment - Show sentiment trends",
            "commentary summary - Get commentary summary",
            "commentary reactions - Show fan reactions"
        ]
    },
    {
        "name": "baseball-live-stats-agent",
        "title": "野球ライブ統計エージェント",
        "description": {
            "en": "Provides real-time statistics during live baseball games",
            "ja": "野球ライブ中継中のリアルタイム統計を提供します"
        },
        "search_tag": "baseball live stats",
        "features": [
            "Real-time pitch data",
            "Live player statistics",
            "Game probability tracking",
            "Historical comparison",
            "Stat alerts"
        ],
        "commands": [
            "stats game <game_id> - Get live game stats",
            "stats player <player> - Get player stats",
            "stats pitching - Show pitching stats",
            "stats batting - Show batting stats"
        ]
    },
    {
        "name": "baseball-live-notifications-agent",
        "title": "野球ライブ通知エージェント",
        "description": {
            "en": "Sends notifications for important events during live baseball games",
            "ja": "野球ライブ中継中の重要イベントの通知を送ります"
        },
        "search_tag": "baseball notifications",
        "features": [
            "Real-time event alerts",
            "Score change notifications",
            "Key moment alerts",
            "Game start/end reminders",
            "Custom alert rules"
        ],
        "commands": [
            "notify setup - Configure notifications",
            "notify game <game_id> - Get game notifications",
            "notify team <team> - Get team notifications",
            "notify alerts - Show active alerts"
        ]
    }
]

def log(message):
    """ログを出力"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

def create_agent_directory(agent):
    """エージェントディレクトリを作成"""
    agent_dir = AGENTS_DIR / agent["name"]
    agent_dir.mkdir(exist_ok=True)
    return agent_dir

def write_agent_py(agent_dir, agent):
    """agent.pyを作成"""
    class_name = agent['name'].replace('-', '_').title()

    content = f'''#!/usr/bin/env python3
"""
{agent['title']}

{agent['description']['en']}
"""

import os
import json
import discord
from discord.ext import commands
from pathlib import Path
from datetime import datetime

class {class_name}(commands.Bot):
    """{agent['title']}"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )
        self.data_dir = Path(__file__).parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        self.config_file = self.data_dir / "config.json"
        self.load_config()

    def load_config(self):
        """設定を読み込む"""
        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                self.config = json.load(f)
        else:
            self.config = {{
                "prefix": "!",
                "language": "ja",
                "notifications": True,
                "channels": []
            }}
            self.save_config()

    def save_config(self):
        """設定を保存する"""
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)

    async def setup_hook(self):
        """Botの準備完了時"""
        print(f"✅ {{{agent['title']}}} の準備完了")

    async def on_ready(self):
        """Botが起動したとき"""
        print(f"🚀 {{{agent['title']}}} が起動しました！")
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="{agent['search_tag']}"
        )
        await self.change_presence(activity=activity)

    async def on_message(self, message):
        """メッセージを受信したとき"""
        if message.author.bot:
            return
        await self.process_commands(message)

def main():
    """メイン関数"""
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ DISCORD_TOKEN 環境変数が設定されていません")
        return

    bot = {class_name}()
    bot.run(token)

if __name__ == "__main__":
    main()
'''
    with open(agent_dir / "agent.py", "w", encoding="utf-8") as f:
        f.write(content)

def write_db_py(agent_dir, agent):
    """db.pyを作成"""
    class_name = agent['name'].replace('-', '_').title()
    db_name = agent['name']

    content = f'''#!/usr/bin/env python3
"""
{agent['title']} - Database Module

{agent['description']['en']}
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any

class {class_name}DB:
    """{agent['title']} Database"""

    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            db_path = Path(__file__).parent / "data" / "{db_name}.db"
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """DB接続を取得"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """データベースを初期化"""
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    type TEXT DEFAULT 'note',
                    tags TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending'
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id TEXT NOT NULL,
                    stat_type TEXT NOT NULL,
                    stat_value TEXT NOT NULL,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS highlights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    timestamp INTEGER NOT NULL,
                    video_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def add_entry(self, title: str, content: str, entry_type: str = "note",
                  tags: Optional[List[str]] = None) -> int:
        """エントリーを追加"""
        tags_json = json.dumps(tags) if tags else None
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO entries (title, content, type, tags)
                VALUES (?, ?, ?, ?)
            """, (title, content, entry_type, tags_json))
            conn.commit()
            return cursor.lastrowid

    def get_entry(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """エントリーを取得"""
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()
            if row:
                return dict(row)
            return None

    def list_entries(self, entry_type: Optional[str] = None,
                     status: str = "active", limit: int = 100) -> List[Dict[str, Any]]:
        """エントリーを一覧表示"""
        with self.get_connection() as conn:
            if entry_type:
                rows = conn.execute("""
                    SELECT * FROM entries WHERE type = ? AND status = ?
                    ORDER BY created_at DESC LIMIT ?
                """, (entry_type, status, limit)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM entries WHERE status = ?
                    ORDER BY created_at DESC LIMIT ?
                """, (status, limit)).fetchall()
            return [dict(row) for row in rows]

    def update_entry(self, entry_id: int, **kwargs) -> bool:
        """エントリーを更新"""
        if not kwargs:
            return False
        set_clause = ", ".join([f"{{key}} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [entry_id]
        with self.get_connection() as conn:
            conn.execute(f"UPDATE entries SET {{set_clause}}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)
            conn.commit()
            return True

    def delete_entry(self, entry_id: int) -> bool:
        """エントリーを削除"""
        with self.get_connection() as conn:
            conn.execute("UPDATE entries SET status = ? WHERE id = ?", ('archived', entry_id))
            conn.commit()
            return True

    def add_notification(self, event_id: str, event_type: str, message: str) -> int:
        """通知を追加"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO notifications (event_id, event_type, message)
                VALUES (?, ?, ?)
            """, (event_id, event_type, message))
            conn.commit()
            return cursor.lastrowid

    def get_pending_notifications(self) -> List[Dict[str, Any]]:
        """未送信の通知を取得"""
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM notifications WHERE status = ?
                ORDER BY created_at ASC
            """, ('pending',)).fetchall()
            return [dict(row) for row in rows]

    def mark_notification_sent(self, notification_id: int) -> bool:
        """通知を送信済みにマーク"""
        with self.get_connection() as conn:
            conn.execute("UPDATE notifications SET status = ? WHERE id = ?", ('sent', notification_id))
            conn.commit()
            return True

    def add_stat(self, game_id: str, stat_type: str, stat_value: str) -> int:
        """統計を追加"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO stats (game_id, stat_type, stat_value)
                VALUES (?, ?, ?)
            """, (game_id, stat_type, stat_value))
            conn.commit()
            return cursor.lastrowid

    def get_game_stats(self, game_id: str) -> List[Dict[str, Any]]:
        """ゲーム統計を取得"""
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM stats WHERE game_id = ?
                ORDER BY recorded_at DESC
            """, (game_id,)).fetchall()
            return [dict(row) for row in rows]

    def add_highlight(self, game_id: str, title: str, description: str,
                     timestamp: int, video_url: Optional[str] = None) -> int:
        """ハイライトを追加"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO highlights (game_id, title, description, timestamp, video_url)
                VALUES (?, ?, ?, ?, ?)
            """, (game_id, title, description, timestamp, video_url))
            conn.commit()
            return cursor.lastrowid

    def get_game_highlights(self, game_id: str) -> List[Dict[str, Any]]:
        """ゲームハイライトを取得"""
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM highlights WHERE game_id = ?
                ORDER BY timestamp ASC
            """, (game_id,)).fetchall()
            return [dict(row) for row in rows]

    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """設定を取得"""
        with self.get_connection() as conn:
            row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
            if row:
                return row['value']
            return default

    def set_setting(self, key: str, value: str) -> bool:
        """設定を保存"""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (key, value))
            conn.commit()
            return True

    def get_stats(self) -> Dict[str, int]:
        """統計情報を取得"""
        with self.get_connection() as conn:
            entries_count = conn.execute('SELECT COUNT(*) FROM entries WHERE status = "active"').fetchone()[0]
            notifications_count = conn.execute("SELECT COUNT(*) FROM notifications").fetchone()[0]
            stats_count = conn.execute("SELECT COUNT(*) FROM stats").fetchone()[0]
            highlights_count = conn.execute("SELECT COUNT(*) FROM highlights").fetchone()[0]
            return {{
                "entries": entries_count,
                "notifications": notifications_count,
                "stats": stats_count,
                "highlights": highlights_count
            }}

def main():
    """メイン関数"""
    db = {class_name}DB()
    stats = db.get_stats()
    print("📊 データベース統計:")
    for key, value in stats.items():
        print(f"  {{key}}: {{value}}")

if __name__ == "__main__":
    main()
'''
    with open(agent_dir / "db.py", "w", encoding="utf-8") as f:
        f.write(content)

def write_discord_py(agent_dir, agent):
    """discord.pyを作成"""
    class_name = agent['name'].replace('-', '_').title()

    content = f'''#!/usr/bin/env python3
"""
{agent['title']} - Discord Bot Module

{agent['description']['en']}
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from pathlib import Path

class {class_name}Discord(commands.Cog):
    """{agent['title']} Discord Cog"""

    def __init__(self, bot):
        self.bot = bot
        from .db import {class_name}DB
        self.db = {class_name}DB()

    def cog_load(self):
        """Cogが読み込まれたとき"""
        print(f"✅ {{{agent['title']}}} Discord Cog の準備完了")

    def cog_unload(self):
        """Cogがアンロードされるとき"""
        print(f"👋 {{{agent['title']}}} Discord Cog をアンロード")

    @commands.Cog.listener()
    async def on_ready(self):
        """Botが起動したとき"""
        print(f"🚀 {{{agent['title']}}} Discord Cog が起動しました！")

    @commands.command(name="help")
    async def cmd_help(self, ctx: commands.Context):
        """ヘルプを表示"""
        embed = discord.Embed(
            title="{agent['title']}",
            description="{agent['description']['ja']}",
            color=discord.Color.blue()
        )
        commands_text = "\\n".join([f"• {{cmd}}" for cmd in {agent['commands']}])
        features_text = "\\n".join([f"• {{feat}}" for feat in {agent['features'][:5]}])
        embed.add_field(name="📋 コマンド", value=commands_text, inline=False)
        embed.add_field(name="🎯 主な機能", value=features_text, inline=False)
        embed.set_footer(text="{agent['search_tag']}")
        await ctx.send(embed=embed)

    @commands.command(name="stats")
    async def cmd_stats(self, ctx: commands.Context):
        """統計を表示"""
        stats = self.db.get_stats()
        embed = discord.Embed(title="📊 データベース統計", color=discord.Color.green())
        for key, value in stats.items():
            embed.add_field(name=key.capitalize(), value=str(value), inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="add")
    async def cmd_add(self, ctx: commands.Context, title: str, *, content: str):
        """エントリーを追加"""
        entry_id = self.db.add_entry(title, content)
        embed = discord.Embed(
            title="✅ エントリー追加",
            description=f"ID: {{entry_id}}",
            color=discord.Color.green()
        )
        embed.add_field(name="タイトル", value=title, inline=False)
        embed.add_field(name="内容", value=content[:500], inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="list")
    async def cmd_list(self, ctx: commands.Context, entry_type: Optional[str] = None, limit: int = 10):
        """エントリーを一覧表示"""
        entries = self.db.list_entries(entry_type=entry_type, limit=limit)
        if not entries:
            embed = discord.Embed(
                title="📋 エントリー一覧",
                description="エントリーが見つかりません",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return
        embed = discord.Embed(title=f"📋 エントリー一覧 ({{len(entries)}}件)", color=discord.Color.blue())
        for entry in entries[:10]:
            title = entry['title'][:50] + "..." if len(entry['title']) > 50 else entry['title']
            embed.add_field(
                name=f"ID {{entry['id']}}: {{title}}",
                value=f"Type: {{entry['type']}} | Created: {{entry['created_at']}}",
                inline=False
            )
        await ctx.send(embed=embed)

    @commands.command(name="search")
    async def cmd_search(self, ctx: commands.Context, query: str):
        """エントリーを検索"""
        entries = self.db.list_entries()
        filtered = [e for e in entries if query.lower() in e['title'].lower() or query.lower() in e['content'].lower()]
        if not filtered:
            embed = discord.Embed(
                title="🔍 検索結果",
                description=f"「{{query}}」に一致するエントリーが見つかりません",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return
        embed = discord.Embed(title=f"🔍 検索結果: {{query}} ({{len(filtered)}}件)", color=discord.Color.blue())
        for entry in filtered[:10]:
            title = entry['title'][:50] + "..." if len(entry['title']) > 50 else entry['title']
            embed.add_field(
                name=f"ID {{entry['id']}}: {{title}}",
                value=f"Type: {{entry['type']}}",
                inline=False
            )
        await ctx.send(embed=embed)

async def setup(bot):
    """Cogをセットアップ"""
    await bot.add_cog({class_name}Discord(bot))
    print(f"✅ {{{agent['title']}}} Discord Cog をセットアップしました")

def main():
    """メイン関数"""
    print("{agent['title']} Discord Bot Module")
    print("Use this module as a Cog in your Discord bot")

if __name__ == "__main__":
    main()
'''
    with open(agent_dir / "discord.py", "w", encoding="utf-8") as f:
        f.write(content)

def write_readme(agent_dir, agent):
    """README.mdを作成"""
    class_name = agent['name'].replace('-', '_').title()

    # 機能リスト
    features_list = "\\n".join([f"- {feat}" for feat in agent['features']])

    # コマンドリスト
    commands_list = "\\n".join([f"- `{cmd}`" for cmd in agent['commands']])

    content = f'''# {agent['title']}

{agent['description']['en']}

{agent['description']['ja']}

## 機能

{features_list}

## コマンド

{commands_list}

## インストール

```bash
pip install -r requirements.txt
```

## 使い方

```bash
# エージェントを実行
python3 agent.py

# データベースを操作
python3 db.py
```

## データベーススキーマ

### entries

エントリー（ノート、タスク、アイデア等）を保存します。

| カラム | タイプ | 説明 |
|--------|--------|------|
| id | INTEGER | 主キー |
| title | TEXT | タイトル |
| content | TEXT | 内容 |
| type | TEXT | タイプ（note, task, idea, goal, project） |
| tags | TEXT | タグ（JSON） |
| status | TEXT | ステータス（active, archived, completed） |
| created_at | TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | 更新日時 |

### notifications

通知を保存します。

| カラム | タイプ | 説明 |
|--------|--------|------|
| id | INTEGER | 主キー |
| event_id | TEXT | イベントID |
| event_type | TEXT | イベントタイプ |
| message | TEXT | 通知メッセージ |
| sent_at | TIMESTAMP | 送信日時 |
| status | TEXT | ステータス（pending, sent） |

### stats

統計を保存します。

| カラム | タイプ | 説明 |
|--------|--------|------|
| id | INTEGER | 主キー |
| game_id | TEXT | ゲームID |
| stat_type | TEXT | 統計タイプ |
| stat_value | TEXT | 統計値 |
| recorded_at | TIMESTAMP | 記録日時 |

### highlights

ハイライトを保存します。

| カラム | タイプ | 説明 |
|--------|--------|------|
| id | INTEGER | 主キー |
| game_id | TEXT | ゲームID |
| title | TEXT | タイトル |
| description | TEXT | 説明 |
| timestamp | INTEGER | タイムスタンプ |
| video_url | TEXT | 動画URL |
| created_at | TIMESTAMP | 作成日時 |

### settings

設定を保存します。

| カラム | タイプ | 説明 |
|--------|--------|------|
| key | TEXT | 設定キー（主キー） |
| value | TEXT | 設定値 |
| updated_at | TIMESTAMP | 更新日時 |

## API Reference

### {class_name}DB

```python
from db import {class_name}DB

db = {class_name}DB()

# エントリーを追加
entry_id = db.add_entry("タイトル", "内容", "note", ["tag1", "tag2"])

# エントリーを取得
entry = db.get_entry(entry_id)

# エントリーを一覧表示
entries = db.list_entries(entry_type="note", limit=10)

# エントリーを更新
db.update_entry(entry_id, title="新しいタイトル", content="新しい内容")

# エントリーを削除
db.delete_entry(entry_id)

# 通知を追加
notification_id = db.add_notification("event123", "game_start", "試合開始！")

# 統計を追加
stat_id = db.add_stat("game123", "home_runs", "5")

# ハイライトを追加
highlight_id = db.add_highlight("game123", "ホームラン", "特大HR", 3600, "https://example.com/video.mp4")

# 設定を取得/設定
db.set_setting("language", "ja")
language = db.get_setting("language")
```

## License

MIT

---

## English

# {agent['title']}

{agent['description']['en']}

## Features

{features_list}

## Commands

{commands_list}

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Run the agent
python3 agent.py

# Interact with database
python3 db.py
```

## Database Schema

### entries

Stores entries (notes, tasks, ideas, etc.).

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| title | TEXT | Title |
| content | TEXT | Content |
| type | TEXT | Type (note, task, idea, goal, project) |
| tags | TEXT | Tags (JSON) |
| status | TEXT | Status (active, archived, completed) |
| created_at | TIMESTAMP | Created at |
| updated_at | TIMESTAMP | Updated at |

### notifications

Stores notifications.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| event_id | TEXT | Event ID |
| event_type | TEXT | Event type |
| message | TEXT | Notification message |
| sent_at | TIMESTAMP | Sent at |
| status | TEXT | Status (pending, sent) |

### stats

Stores statistics.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| game_id | TEXT | Game ID |
| stat_type | TEXT | Stat type |
| stat_value | TEXT | Stat value |
| recorded_at | TIMESTAMP | Recorded at |

### highlights

Stores highlights.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| game_id | TEXT | Game ID |
| title | TEXT | Title |
| description | TEXT | Description |
| timestamp | INTEGER | Timestamp |
| video_url | TEXT | Video URL |
| created_at | TIMESTAMP | Created at |

### settings

Stores settings.

| Column | Type | Description |
|--------|------|-------------|
| key | TEXT | Setting key (primary key) |
| value | TEXT | Setting value |
| updated_at | TIMESTAMP | Updated at |

## License

MIT
'''
    with open(agent_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(content)

def write_requirements_txt(agent_dir):
    """requirements.txtを作成"""
    content = '''discord.py>=2.3.0
'''
    with open(agent_dir / "requirements.txt", "w", encoding="utf-8") as f:
        f.write(content)

def create_agent(agent):
    """エージェントを作成"""
    log(f"🔧 {agent['name']} を作成中...")

    agent_dir = create_agent_directory(agent)
    write_agent_py(agent_dir, agent)
    write_db_py(agent_dir, agent)
    write_discord_py(agent_dir, agent)
    write_readme(agent_dir, agent)
    write_requirements_txt(agent_dir)

    log(f"✅ {agent['name']} 完了！")

def load_progress():
    """進捗をロード"""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {"completed": [], "total": len(AGENTS)}

def save_progress(progress):
    """進捗を保存"""
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)

def run():
    """オーケストレーターを実行"""
    log("=" * 60)
    log("🚀 野球ライブ配信エージェントオーケストレーター起動")
    log("=" * 60)

    progress = load_progress()
    completed = progress["completed"]

    log(f"📊 進捗: {{len(completed)}}/{{progress['total']}} 完了")

    for agent in AGENTS:
        if agent["name"] in completed:
            log(f"⏭️  {{agent['name']}} は完了済み")
            continue

        try:
            create_agent(agent)
            completed.append(agent["name"])
            progress["completed"] = completed
            save_progress(progress)
            log(f"📈 進捗: {{len(completed)}}/{{progress['total']}}")
        except Exception as e:
            log(f"❌ {{agent['name']}} でエラー: {{e}}")
            continue

    log("=" * 60)
    log(f"🎉 オーケストレーター完了！")
    log(f"📊 最終進捗: {{len(completed)}}/{{progress['total']}}")
    log("=" * 60)

    return progress

if __name__ == "__main__":
    run()
