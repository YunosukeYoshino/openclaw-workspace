#!/usr/bin/env python3
"""
野球詳細分析エージェントプロジェクト オーケストレーター
5個の野球詳細分析エージェントを作成
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# プロジェクト設定
PROJECT_NAME = "野球詳細分析エージェント"
PROJECT_ID = "baseball_stats_agents"
PROJECT_DIR = Path(__file__).parent

# 作成するエージェント一覧
AGENTS = [
    {
        "id": "baseball-stats-agent",
        "name": "詳細野球統計分析エージェント",
        "description": "野球の詳細な統計データを収集・分析するエージェント",
        "db_tables": """
        CREATE TABLE IF NOT EXISTS baseball_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id TEXT NOT NULL,
            player_name TEXT NOT NULL,
            team TEXT,
            games INTEGER DEFAULT 0,
            at_bats INTEGER DEFAULT 0,
            hits INTEGER DEFAULT 0,
            home_runs INTEGER DEFAULT 0,
            rbi INTEGER DEFAULT 0,
            batting_average REAL DEFAULT 0.0,
            era REAL DEFAULT 0.0,
            wins INTEGER DEFAULT 0,
            saves INTEGER DEFAULT 0,
            season TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_id, season)
        );

        CREATE TABLE IF NOT EXISTS stat_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id TEXT NOT NULL,
            stat_type TEXT NOT NULL,
            stat_value REAL,
            date TEXT NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
    },
    {
        "id": "baseball-prediction-agent",
        "name": "試合結果予測エージェント",
        "description": "野球の試合結果を予測するエージェント",
        "db_tables": """
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT NOT NULL,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            predicted_winner TEXT NOT NULL,
            confidence REAL DEFAULT 0.5,
            predicted_score_home INTEGER,
            predicted_score_away INTEGER,
            actual_winner TEXT,
            actual_score_home INTEGER,
            actual_score_away INTEGER,
            prediction_date TEXT NOT NULL,
            game_date TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS prediction_models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT NOT NULL,
            model_version TEXT,
            accuracy REAL DEFAULT 0.0,
            total_predictions INTEGER DEFAULT 0,
            correct_predictions INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
    },
    {
        "id": "baseball-history-agent",
        "name": "野球歴史記録管理エージェント",
        "description": "野球の歴史や記録を管理するエージェント",
        "db_tables": """
        CREATE TABLE IF NOT EXISTS baseball_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_type TEXT NOT NULL,
            record_name TEXT NOT NULL,
            holder TEXT NOT NULL,
            holder_team TEXT,
            value REAL NOT NULL,
            unit TEXT,
            date_achieved TEXT,
            season TEXT,
            notes TEXT,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS baseball_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            location TEXT,
            participants TEXT,
            result TEXT,
            description TEXT,
            significance TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS baseball_timeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            event TEXT NOT NULL,
            category TEXT,
            importance INTEGER DEFAULT 1,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
    },
    {
        "id": "baseball-scouting-agent",
        "name": "選手スカウティング情報エージェント",
        "description": "選手のスカウティング情報を管理するエージェント",
        "db_tables": """
        CREATE TABLE IF NOT EXISTS scouting_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id TEXT NOT NULL,
            player_name TEXT NOT NULL,
            position TEXT,
            team TEXT,
            level TEXT,
            report_date TEXT NOT NULL,
            overall_grade TEXT,
            hitting_grade TEXT,
            power_grade TEXT,
            speed_grade TEXT,
            defense_grade TEXT,
            arm_grade TEXT,
            strengths TEXT,
            weaknesses TEXT,
            projection TEXT,
            potential TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_id, report_date)
        );

        CREATE TABLE IF NOT EXISTS player_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id TEXT NOT NULL,
            player_name TEXT NOT NULL,
            birth_date TEXT,
            height TEXT,
            weight INTEGER,
            bats TEXT,
            throws TEXT,
            nationality TEXT,
            draft_year INTEGER,
            draft_round INTEGER,
            draft_team TEXT,
            current_team TEXT,
            position TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_id)
        );
        """,
    },
    {
        "id": "baseball-fantasy-agent",
        "name": "ファンタジー野球管理エージェント",
        "description": "ファンタジー野球のチーム・選手管理エージェント",
        "db_tables": """
        CREATE TABLE IF NOT EXISTS fantasy_teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id TEXT NOT NULL,
            team_name TEXT NOT NULL,
            league_id TEXT NOT NULL,
            owner TEXT,
            season TEXT NOT NULL,
            total_points REAL DEFAULT 0.0,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(team_id, season)
        );

        CREATE TABLE IF NOT EXISTS fantasy_rosters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id TEXT NOT NULL,
            player_id TEXT NOT NULL,
            player_name TEXT NOT NULL,
            position TEXT,
            acquisition_type TEXT,
            acquisition_date TEXT,
            cost REAL DEFAULT 0.0,
            status TEXT DEFAULT 'active',
            season TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS fantasy_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id TEXT NOT NULL,
            week INTEGER NOT NULL,
            season TEXT NOT NULL,
            points REAL DEFAULT 0.0,
            at_bats INTEGER DEFAULT 0,
            runs INTEGER DEFAULT 0,
            hits INTEGER DEFAULT 0,
            home_runs INTEGER DEFAULT 0,
            rbi INTEGER DEFAULT 0,
            stolen_bases INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_id, week, season)
        );

        CREATE TABLE IF NOT EXISTS fantasy_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id TEXT NOT NULL,
            transaction_type TEXT NOT NULL,
            player_id TEXT,
            details TEXT,
            date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
    },
]

# 進捗管理
PROGRESS_FILE = PROJECT_DIR / "baseball_stats_progress.json"


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

    def get_all(self) -> List[Dict[str, Any]]:
        """全てのデータを取得"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM baseball_stats ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    def add_stat(self, player_id: str, player_name: str, **kwargs) -> int:
        """統計データを追加"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO baseball_stats (player_id, player_name, team, games, at_bats, hits, home_runs, rbi, batting_average, era, wins, saves, season)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                player_id, player_name,
                kwargs.get("team"), kwargs.get("games", 0),
                kwargs.get("at_bats", 0), kwargs.get("hits", 0),
                kwargs.get("home_runs", 0), kwargs.get("rbi", 0),
                kwargs.get("batting_average", 0.0), kwargs.get("era", 0.0),
                kwargs.get("wins", 0), kwargs.get("saves", 0),
                kwargs.get("season", datetime.now().strftime("%Y"))
            ))
            conn.commit()
            return cursor.lastrowid

    def get_by_player(self, player_id: str) -> Optional[Dict[str, Any]]:
        """選手の統計を取得"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM baseball_stats WHERE player_id = ?", (player_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_stat(self, player_id: str, season: str, **kwargs) -> bool:
        """統計データを更新"""
        updates = ", ".join([f"{{k}} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [player_id, season]

        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE baseball_stats SET {{updates}}, updated_at = CURRENT_TIMESTAMP
                WHERE player_id = ? AND season = ?
            """, values)
            conn.commit()
            return cursor.rowcount > 0

    def delete_stat(self, player_id: str, season: str) -> bool:
        """統計データを削除"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM baseball_stats WHERE player_id = ? AND season = ?", (player_id, season))
            conn.commit()
            return cursor.rowcount > 0

    def search(self, query: str) -> List[Dict[str, Any]]:
        """統計データを検索"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM baseball_stats
                WHERE player_name LIKE ? OR team LIKE ?
                ORDER BY created_at DESC
            """, (f"%{{query}}%", f"%{{query}}%"))
            return [dict(row) for row in cursor.fetchall()]

    def get_stats_summary(self) -> Dict[str, Any]:
        """統計のサマリーを取得"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as total_players,
                       AVG(batting_average) as avg_ba,
                       AVG(era) as avg_era,
                       SUM(home_runs) as total_hr
                FROM baseball_stats
            """)
            row = cursor.fetchone()
            return dict(row) if row else {{}}


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
import re


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
                name="baseball stats"
            )
        )


bot = {camel_case(agent["id"].replace("-", "_"))}Bot()


@bot.command(name="stats")
async def show_stats(ctx, player_name: Optional[str] = None):
    """統計を表示"""
    # TODO: データベースから統計を取得して表示
    if player_name:
        await ctx.send(f"Searching for stats of: {{player_name}}")
    else:
        await ctx.send("Usage: !stats <player_name>")


@bot.command(name="add")
async def add_stat(ctx, player_id: str, player_name: str, *args):
    """統計を追加"""
    # TODO: データベースに統計を追加
    await ctx.send(f"Adding stat for {{player_name}} (ID: {{player_id}})")


@bot.command(name="update")
async def update_stat(ctx, player_id: str, *args):
    """統計を更新"""
    # TODO: データベースの統計を更新
    await ctx.send(f"Updating stat for player ID: {{player_id}}")


@bot.command(name="search")
async def search_stats(ctx, query: str):
    """統計を検索"""
    # TODO: データベースを検索
    await ctx.send(f"Searching for: {{query}}")


@bot.command(name="summary")
async def show_summary(ctx):
    """サマリーを表示"""
    # TODO: 統計のサマリーを表示
    await ctx.send("Generating summary...")


@bot.command(name="help")
async def show_help(ctx):
    """ヘルプを表示"""
    help_text = """
**{agent["name"]} Commands:**

`!stats <player_name>` - 選手の統計を表示
`!add <player_id> <player_name> [stats...]` - 統計を追加
`!update <player_id> [stats...]` - 統計を更新
`!search <query>` - 統計を検索
`!summary` - サマリーを表示
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

- Track baseball statistics
- Analyze player performance
- Search and filter data
- Discord bot integration

## Database

The agent uses SQLite with the following tables:

- `baseball_stats` - Baseball statistics data
- `stat_entries` - Individual stat entries

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
stats = agent.get_all()
print(stats)
```

### Discord Commands

- `!stats <player_name>` - 選手の統計を表示
- `!add <player_id> <player_name> [stats...]` - 統計を追加
- `!update <player_id> [stats...]` - 統計を更新
- `!search <query>` - 統計を検索
- `!summary` - サマリーを表示

## Requirements

See `requirements.txt`.

## License

MIT

---

# {agent["name"]}（詳細野球統計分析エージェント）

{agent["description"]}

## 概要

このエージェントは{agent["id"]}を管理するのに役立ちます。

## 機能

- 野球の統計を追跡
- 選手の成績を分析
- データの検索とフィルタリング
- Discordボットとの統合

## データベース

このエージェントはSQLiteを使用し、以下のテーブルを持ちます：

- `baseball_stats` - 野球統計データ
- `stat_entries` - 個別の統計エントリー

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
stats = agent.get_all()
print(stats)
```

### Discordコマンド

- `!stats <player_name>` - 選手の統計を表示
- `!add <player_id> <player_name> [stats...]` - 統計を追加
- `!update <player_id> [stats...]` - 統計を更新
- `!search <query>` - 統計を検索
- `!summary` - サマリーを表示

## 依存パッケージ

`requirements.txt` を参照してください。

## ライセンス

MIT
'''


def generate_requirements_txt() -> str:
    """requirements.txt を生成"""
    return """# {agent["name"]} Requirements

# Core
python-dotenv>=1.0.0

# Discord
discord.py>=2.3.0

# Database
# sqlite3 is included in Python standard library
"""


def camel_case(s: str) -> str:
    """スネークケースをキャメルケースに変換"""
    return "".join(word.capitalize() for word in s.split("_"))


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
