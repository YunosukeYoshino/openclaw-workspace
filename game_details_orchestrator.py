#!/usr/bin/env python3
"""
ゲーム詳細エージェントプロジェクト オーケストレーター
5個のゲーム詳細エージェントを作成
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# プロジェクト設定
PROJECT_NAME = "ゲーム詳細エージェント"
PROJECT_ID = "game_details_agents"
PROJECT_DIR = Path(__file__).parent

# 作成するエージェント一覧
AGENTS = [
    {
        "id": "game-walkthrough-agent",
        "name": "ゲーム攻略・Walkthroughエージェント",
        "description": "ゲームの攻略情報・walkthroughを管理するエージェント",
        "db_tables": """
        CREATE TABLE IF NOT EXISTS walkthroughs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT NOT NULL,
            game_title TEXT NOT NULL,
            chapter_id TEXT,
            chapter_name TEXT,
            step_number INTEGER DEFAULT 1,
            step_title TEXT NOT NULL,
            step_description TEXT,
            tips TEXT,
            difficulty INTEGER DEFAULT 1,
            image_url TEXT,
            video_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS game_bosses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT NOT NULL,
            game_title TEXT NOT NULL,
            boss_name TEXT NOT NULL,
            boss_level TEXT,
            location TEXT,
            strategy TEXT,
            weaknesses TEXT,
            recommended_level TEXT,
            image_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
    },
    {
        "id": "game-cheat-agent",
        "name": "チートコード・裏技管理エージェント",
        "description": "ゲームのチートコード・裏技を管理するエージェント",
        "db_tables": """
        CREATE TABLE IF NOT EXISTS cheats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT NOT NULL,
            game_title TEXT NOT NULL,
            cheat_type TEXT NOT NULL,
            cheat_code TEXT NOT NULL,
            effect TEXT NOT NULL,
            platform TEXT,
            notes TEXT,
            verified BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS secrets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT NOT NULL,
            game_title TEXT NOT NULL,
            secret_type TEXT NOT NULL,
            secret_name TEXT NOT NULL,
            how_to_unlock TEXT,
            reward TEXT,
            location TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS easter_eggs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT NOT NULL,
            game_title TEXT NOT NULL,
            egg_name TEXT NOT NULL,
            description TEXT,
            how_to_find TEXT,
            creator TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
    },
    {
        "id": "game-mod-agent",
        "name": "MOD・カスタムコンテンツ管理エージェント",
        "description": "ゲームのMOD・カスタムコンテンツを管理するエージェント",
        "db_tables": """
        CREATE TABLE IF NOT EXISTS mods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT NOT NULL,
            game_title TEXT NOT NULL,
            mod_id TEXT NOT NULL,
            mod_name TEXT NOT NULL,
            mod_type TEXT,
            author TEXT,
            version TEXT,
            description TEXT,
            download_url TEXT,
            install_instructions TEXT,
            file_size INTEGER,
            category TEXT,
            rating REAL DEFAULT 0.0,
            download_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(mod_id)
        );

        CREATE TABLE IF NOT EXISTS mod_dependencies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mod_id TEXT NOT NULL,
            required_mod_id TEXT NOT NULL,
            required_version TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS custom_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT NOT NULL,
            game_title TEXT NOT NULL,
            content_type TEXT NOT NULL,
            content_name TEXT NOT NULL,
            creator TEXT,
            description TEXT,
            download_url TEXT,
            file_size INTEGER,
            rating REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
    },
    {
        "id": "game-community-agent",
        "name": "ゲームコミュニティ・フォーラムエージェント",
        "description": "ゲームのコミュニティ・フォーラム情報を管理するエージェント",
        "db_tables": """
        CREATE TABLE IF NOT EXISTS forums (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT NOT NULL,
            game_title TEXT NOT NULL,
            forum_name TEXT NOT NULL,
            forum_url TEXT,
            platform TEXT,
            member_count INTEGER DEFAULT 0,
            active_users INTEGER DEFAULT 0,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS threads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            forum_id TEXT NOT NULL,
            thread_id TEXT NOT NULL,
            title TEXT NOT NULL,
            author TEXT,
            url TEXT,
            views INTEGER DEFAULT 0,
            replies INTEGER DEFAULT 0,
            created_at TEXT,
            last_activity TEXT,
            tags TEXT,
            created_at_local TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS useful_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT NOT NULL,
            game_title TEXT NOT NULL,
            post_title TEXT NOT NULL,
            post_url TEXT,
            author TEXT,
            content_summary TEXT,
            upvotes INTEGER DEFAULT 0,
            category TEXT,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
    },
    {
        "id": "game-speedrun-agent",
        "name": "スピードラン記録・RTA情報エージェント",
        "description": "ゲームのスピードラン記録・RTA情報を管理するエージェント",
        "db_tables": """
        CREATE TABLE IF NOT EXISTS speedruns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT NOT NULL,
            game_title TEXT NOT NULL,
            category TEXT NOT NULL,
            runner TEXT NOT NULL,
            time_seconds INTEGER NOT NULL,
            time_formatted TEXT NOT NULL,
            platform TEXT,
            date_achieved TEXT,
            video_url TEXT,
            rank INTEGER,
            world_record BOOLEAN DEFAULT 0,
            verified BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS speedrun_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT NOT NULL,
            game_title TEXT NOT NULL,
            category_name TEXT NOT NULL,
            rules TEXT,
            world_record_time INTEGER,
            world_record_holder TEXT,
            run_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS speedrun_strategies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT NOT NULL,
            game_title TEXT NOT NULL,
            category TEXT NOT NULL,
            strategy_name TEXT NOT NULL,
            description TEXT,
            time_saving_seconds INTEGER DEFAULT 0,
            difficulty INTEGER DEFAULT 1,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
    },
]

# 進捗管理
PROGRESS_FILE = PROJECT_DIR / "game_details_progress.json"


def load_progress() -> Dict[str, Any]:
    """進捗ファイルを読み込む"""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "project_name": PROJECT_NAME,
        "project_id": PROJECT_ID,
        "started_at": "",
        "completed_at": None,
        "agents": {agent["id"]: {"status": "pending"} for agent in AGENTS},
    }


def save_progress(progress: Dict[str, Any]) -> None:
    """進捗ファイルを保存する"""
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def camel_case(s: str) -> str:
    """スネークケースをキャメルケースに変換"""
    return "".join(word.capitalize() for word in s.split("_"))


def generate_agent_py(agent: Dict[str, Any]) -> str:
    """agent.py のテンプレートを生成"""
    return f'''#!/usr/bin/env python3
"""
{agent["name"]}
{agent["description"]}
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional


class {camel_case(agent["id"].replace("-", "_"))}:
    """{agent["name"]}"""

    def __init__(self, db_path: str = "{agent["id"]}.db"):
        """初期化"""
        self.db_path = db_path
        self.conn = None

    def connect(self) -> sqlite3.Connection:
        """データベースに接続"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self) -> None:
        """接続を閉じる"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        """コンテキストマネージャー"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャー"""
        self.close()

    def get_all(self, table: str = "walkthroughs") -> List[Dict[str, Any]]:
        """全てのデータを取得"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {{table}} ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    def add_entry(self, table: str, data: Dict[str, Any]) -> int:
        """エントリーを追加"""
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        query = f"INSERT INTO {{table}} ({{columns}}) VALUES ({{placeholders}})"

        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, list(data.values()))
            conn.commit()
            return cursor.lastrowid

    def get_by_game(self, game_id: str, table: str = "walkthroughs") -> List[Dict[str, Any]]:
        """ゲームでデータを取得"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {{table}} WHERE game_id = ? ORDER BY step_number, created_at", (game_id,))
            return [dict(row) for row in cursor.fetchall()]

    def search(self, query: str, table: str = "walkthroughs") -> List[Dict[str, Any]]:
        """データを検索"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT * FROM {{table}}
                WHERE game_title LIKE ? OR step_title LIKE ? OR description LIKE ?
                ORDER BY created_at DESC
            """, (f"%{{query}}%", f"%{{query}}%", f"%{{query}}%"))
            return [dict(row) for row in cursor.fetchall()]

    def update_entry(self, table: str, entry_id: int, data: Dict[str, Any]) -> bool:
        """エントリーを更新"""
        set_clause = ", ".join([f"{{k}} = ?" for k in data.keys()])
        values = list(data.values()) + [entry_id]

        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE {{table}} SET {{set_clause}}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, values)
            conn.commit()
            return cursor.rowcount > 0

    def delete_entry(self, table: str, entry_id: int) -> bool:
        """エントリーを削除"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {{table}} WHERE id = ?", (entry_id,))
            conn.commit()
            return cursor.rowcount > 0


def main():
    """メイン関数"""
    agent = {camel_case(agent["id"].replace("-", "_"))}()
    print(f"{{agent.__class__.__name__}} initialized")


if __name__ == "__main__":
    main()
'''


def generate_db_py(agent: Dict[str, Any]) -> str:
    """db.py のテンプレートを生成"""
    return f'''#!/usr/bin/env python3
"""
{agent["name"]} - データベースモジュール
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from contextlib import contextmanager


class Database:
    """データベース管理クラス"""

    def __init__(self, db_path: str = "{agent["id"]}.db"):
        """初期化"""
        self.db_path = Path(db_path)
        self.conn = None

    @contextmanager
    def get_connection(self):
        """接続を取得（コンテキストマネージャー）"""
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
        """データベースを初期化"""
        with self.get_connection() as conn:
            conn.executescript("""
{agent["db_tables"]}
            """)

    def execute(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """クエリを実行"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def execute_many(self, query: str, params_list: List[tuple]) -> None:
        """複数のクエリを実行"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)

    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """データを挿入"""
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        query = f"INSERT INTO {{table}} ({{columns}}) VALUES ({{placeholders}})"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, list(data.values()))
            return cursor.lastrowid

    def update(self, table: str, data: Dict[str, Any], where: Dict[str, Any]) -> int:
        """データを更新"""
        set_clause = ", ".join([f"{{k}} = ?" for k in data.keys()])
        where_clause = " AND ".join([f"{{k}} = ?" for k in where.keys()])
        query = f"UPDATE {{table}} SET {{set_clause}} WHERE {{where_clause}}"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, list(data.values()) + list(where.values()))
            return cursor.rowcount

    def delete(self, table: str, where: Dict[str, Any]) -> int:
        """データを削除"""
        where_clause = " AND ".join([f"{{k}} = ?" for k in where.keys()])
        query = f"DELETE FROM {{table}} WHERE {{where_clause}}"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, list(where.values()))
            return cursor.rowcount

    def get_all(self, table: str) -> List[Dict[str, Any]]:
        """全てのデータを取得"""
        return self.execute(f"SELECT * FROM {{table}} ORDER BY id DESC")

    def get_by_id(self, table: str, record_id: int) -> Optional[Dict[str, Any]]:
        """IDでデータを取得"""
        result = self.execute(f"SELECT * FROM {{table}} WHERE id = ?", (record_id,))
        return result[0] if result else None

    def count(self, table: str) -> int:
        """レコード数を取得"""
        result = self.execute(f"SELECT COUNT(*) as count FROM {{table}}")
        return result[0]["count"] if result else 0

    def search(self, table: str, search_field: str, query: str) -> List[Dict[str, Any]]:
        """検索"""
        return self.execute(
            f"SELECT * FROM {{table}} WHERE {{search_field}} LIKE ? ORDER BY id DESC",
            (f"%{{query}}%",)
        )


def main():
    """メイン関数"""
    db = Database()
    db.initialize()
    print("Database initialized successfully")


if __name__ == "__main__":
    main()
'''


def generate_discord_py(agent: Dict[str, Any]) -> str:
    """discord.py のテンプレートを生成"""
    return f'''#!/usr/bin/env python3
"""
{agent["name"]} - Discord Bot モジュール
"""

import discord
from discord.ext import commands
from typing import Optional


class {camel_case(agent["id"].replace("-", "_"))}Bot(commands.Bot):
    """{agent["name"]} Discord Bot"""

    def __init__(self, command_prefix: str = "!"):
        """初期化"""
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=command_prefix, intents=intents)

    async def setup_hook(self):
        """ボットの準備"""
        print(f"Logged in as {{self.user}}")

    async def on_ready(self):
        """準備完了時の処理"""
        print(f"{{self.__class__.__name__}} is ready!")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="game info"
            )
        )


bot = {camel_case(agent["id"].replace("-", "_"))}Bot()


@bot.command(name="search")
async def search_info(ctx, query: str):
    """情報を検索"""
    # TODO: データベースから情報を検索して表示
    await ctx.send(f"Searching for: {{query}}")


@bot.command(name="add")
async def add_info(ctx, game_id: str, *args):
    """情報を追加"""
    # TODO: データベースに情報を追加
    await ctx.send(f"Adding info for game: {{game_id}}")


@bot.command(name="list")
async def list_info(ctx, game_title: Optional[str] = None):
    """情報を一覧表示"""
    # TODO: データベースから情報を一覧表示
    if game_title:
        await ctx.send(f"Listing info for: {{game_title}}")
    else:
        await ctx.send("Usage: !list <game_title>")


@bot.command(name="update")
async def update_info(ctx, entry_id: int, *args):
    """情報を更新"""
    # TODO: データベースの情報を更新
    await ctx.send(f"Updating info ID: {{entry_id}}")


@bot.command(name="delete")
async def delete_info(ctx, entry_id: int):
    """情報を削除"""
    # TODO: データベースの情報を削除
    await ctx.send(f"Deleting info ID: {{entry_id}}")


@bot.command(name="help")
async def show_help(ctx):
    """ヘルプを表示"""
    help_text = """
**{agent["name"]} Commands:**

`!search <query>` - 情報を検索
`!add <game_id> [data...]` - 情報を追加
`!list <game_title>` - 情報を一覧表示
`!update <entry_id> [data...]` - 情報を更新
`!delete <entry_id>` - 情報を削除
`!help` - このヘルプを表示
"""
    await ctx.send(help_text)


def main():
    """メイン関数"""
    import os
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("DISCORD_TOKEN environment variable not set")
        return
    bot.run(token)


if __name__ == "__main__":
    main()
'''


def generate_readme_md(agent: Dict[str, Any]) -> str:
    """README.md を生成"""
    return f'''# {agent["name"]}

{agent["description"]}

## Overview

This agent helps manage {agent["id"]}.

## Features

- Track game information
- Search and filter data
- Discord bot integration
- Custom content management

## Database

The agent uses SQLite with the following tables:

- Various game-related tables for {agent["id"]}

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Initialize the database:
```bash
python db.py
```

3. Run the agent:
```bash
python agent.py
```

4. Run the Discord bot (optional):
```bash
export DISCORD_TOKEN=your_token_here
python discord.py
```

## Usage

### As a Module

```python
from agent import {camel_case(agent["id"].replace("-", "_"))}

agent = {camel_case(agent["id"].replace("-", "_"))}()
info = agent.get_all()
print(info)
```

### Discord Commands

- `!search <query>` - 情報を検索
- `!add <game_id> [data...]` - 情報を追加
- `!list <game_title>` - 情報を一覧表示
- `!update <entry_id> [data...]` - 情報を更新
- `!delete <entry_id>` - 情報を削除

## Requirements

See `requirements.txt`.

## License

MIT

---

# {agent["name"]}（{agent["id"]}）

{agent["description"]}

## 概要

このエージェントは{agent["id"]}を管理するのに役立ちます。

## 機能

- ゲーム情報を追跡
- データの検索とフィルタリング
- Discordボットとの統合
- カスタムコンテンツ管理

## データベース

このエージェントはSQLiteを使用し、{agent["id"]}関連のテーブルを持ちます。

## セットアップ

1. 依存パッケージをインストール：
```bash
pip install -r requirements.txt
```

2. データベースを初期化：
```bash
python db.py
```

3. エージェントを実行：
```bash
python agent.py
```

4. Discordボットを実行（オプション）：
```bash
export DISCORD_TOKEN=your_token_here
python discord.py
```

## 使用方法

### モジュールとして使用

```python
from agent import {camel_case(agent["id"].replace("-", "_"))}

agent = {camel_case(agent["id"].replace("-", "_"))}()
info = agent.get_all()
print(info)
```

### Discordコマンド

- `!search <query>` - 情報を検索
- `!add <game_id> [data...]` - 情報を追加
- `!list <game_title>` - 情報を一覧表示
- `!update <entry_id> [data...]` - 情報を更新
- `!delete <entry_id>` - 情報を削除

## 依存パッケージ

`requirements.txt` を参照してください。

## ライセンス

MIT
'''


def create_agent(agent: Dict[str, Any]) -> bool:
    """エージェントを作成"""
    agent_dir = PROJECT_DIR / "agents" / agent["id"]

    try:
        # ディレクトリを作成
        agent_dir.mkdir(parents=True, exist_ok=True)

        # ファイルを作成
        (agent_dir / "agent.py").write_text(generate_agent_py(agent), encoding="utf-8")
        (agent_dir / "db.py").write_text(generate_db_py(agent), encoding="utf-8")
        (agent_dir / "discord.py").write_text(generate_discord_py(agent), encoding="utf-8")
        (agent_dir / "README.md").write_text(generate_readme_md(agent), encoding="utf-8")
        (agent_dir / "requirements.txt").write_text("discord.py>=2.3.0\npython-dotenv>=1.0.0\n", encoding="utf-8")

        return True
    except Exception as e:
        print(f"Error creating agent {{agent['id']}}: {{e}}")
        return False


def main():
    """メイン関数"""
    print(f"Starting {{PROJECT_NAME}} project...")
    print(f"Agents to create: {{len(AGENTS)}}")

    # 進捗を読み込み
    progress = load_progress()

    # 開始時刻を記録
    if not progress["started_at"]:
        progress["started_at"] = datetime.now().isoformat()
        save_progress(progress)

    # 各エージェントを作成
    for agent in AGENTS:
        agent_id = agent["id"]
        print(f"\\nProcessing: {{agent_id}} - {{agent['name']}}")

        if progress["agents"][agent_id]["status"] == "completed":
            print(f"  ✅ Already completed, skipping...")
            continue

        # エージェントを作成
        if create_agent(agent):
            progress["agents"][agent_id]["status"] = "completed"
            progress["agents"][agent_id]["created_at"] = datetime.now().isoformat()
            save_progress(progress)
            print(f"  ✅ Created successfully")
        else:
            print(f"  ❌ Failed to create")
            progress["agents"][agent_id]["status"] = "failed"
            save_progress(progress)

    # 完了時刻を記録
    all_completed = all(a["status"] == "completed" for a in progress["agents"].values())
    if all_completed and not progress["completed_at"]:
        progress["completed_at"] = datetime.now().isoformat()
        save_progress(progress)

    # サマリーを表示
    print(f"\\n" + "="*50)
    print(f"Project: {{PROJECT_NAME}}")
    print(f"Status: {'✅ Completed' if all_completed else '⚠️  In progress'}")
    print(f"Completed: {{sum(1 for a in progress['agents'].values() if a['status'] == 'completed')}}/{{len(AGENTS)}}")
    print(f"Started at: {{progress['started_at']}}")
    print(f"Completed at: {{progress.get('completed_at', 'N/A')}}")
    print("="*50)

    return all_completed


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
