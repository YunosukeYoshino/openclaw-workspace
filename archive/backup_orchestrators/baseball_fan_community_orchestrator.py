#!/usr/bin/env python3
"""
Baseball Fan Community Agents Orchestrator
野球ファンコミュニティエージェントオーケストレーター

Orchestrates development of baseball fan community agents.
野球ファンコミュニティエージェントの開発をオーケストレーションします。
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path


# Template for agent.py
AGENT_TEMPLATE = """#!/usr/bin/env python3
\"\"\"
{agent_name} - {japanese_name}

{description}
\"\"\"

import sqlite3
from typing import Optional, List, Dict, Any
from datetime import datetime


class {class_name}:
    \"\"\"{japanese_name}\"\"\"

    def __init__(self, db_path: str = "{agent_name}.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        \"\"\"Initialize database / データベースを初期化\"\"\"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                {content_field} TEXT NOT NULL,
                username TEXT,
                team TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tags TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def add_entry(self, title: str, content: str, username: str = "",
                   team: str = "", tags: str = "") -> int:
        \"\"\"Add a community entry / コミュニティエントリーを追加\"\"\"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO {table_name} (title, {content_field}, username, team, tags)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, content, username, team, tags))

        conn.commit()
        entry_id = cursor.lastrowid
        conn.close()
        return entry_id

    def get_entry(self, entry_id: int) -> Optional[Dict[str, Any]]:
        \"\"\"Get an entry by ID / IDでエントリーを取得\"\"\"
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM {table_name} WHERE id = ?
        ''', (entry_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def list_entries(self, limit: int = 50) -> List[Dict[str, Any]]:
        \"\"\"List all entries / 全エントリーを一覧\"\"\"
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM {table_name}
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def search_by_team(self, team: str) -> List[Dict[str, Any]]:
        \"\"\"Search entries by team / チームでエントリーを検索\"\"\"
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM {table_name}
            WHERE team LIKE ?
            ORDER BY timestamp DESC
        ''', (f"%{team}%",))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def {custom_method}(self) -> Any:
        \"\"\"{custom_method_description}\"\"\"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # TODO: Implement custom logic

        conn.close()
        return None


if __name__ == "__main__":
    agent = {class_name}()
    print("{japanese_name} initialized!")
    print(f"Database: {{agent.db_path}}")
"""


# Template for db.py
DB_TEMPLATE = """#!/usr/bin/env python3
\"\"\"
Database module for {agent_name}
{agent_name}のデータベースモジュール
\"\"\"

import sqlite3
from typing import Optional, List, Dict, Any
from datetime import datetime


class {class_name}DB:
    \"\"\"Database handler for {agent_name} / {agent_name}のデータベースハンドラー\"\"\"

    def __init__(self, db_path: str = "{agent_name}.db"):
        self.db_path = db_path
        self.conn = None
        self.connect()

    def connect(self):
        \"\"\"Connect to database / データベースに接続\"\"\"
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        \"\"\"Close connection / 接続を閉じる\"\"\"
        if self.conn:
            self.conn.close()

    def execute_query(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        \"\"\"Execute a query / クエリを実行\"\"\"
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor

    def commit(self):
        \"\"\"Commit changes / 変更をコミット\"\"\"
        self.conn.commit()
"""


# Template for discord.py
DISCORD_TEMPLATE = """#!/usr/bin/env python3
\"\"\"
Discord Bot module for {agent_name}
{agent_name}のDiscord Botモジュール
\"\"\"

import discord
from discord.ext import commands
from typing import Optional
import os


class {class_name}Bot(commands.Cog):
    \"\"\"Discord Bot for {agent_name} / {agent_name}のDiscord Bot\"\"\"

    def __init__(self, bot: commands.Bot, agent):
        self.bot = bot
        self.agent = agent

    @commands.command(name="{discord_prefix}add")
    async def add_entry(self, ctx: commands.Context, title: str, *, content: str):
        \"\"\"Add a {agent_short} entry / {agent_short}エントリーを追加\"\"\"
        username = str(ctx.author)
        entry_id = self.agent.add_entry(title, content, username)
        await ctx.send(f"Added entry #{entry_id}: {title}")

    @commands.command(name="{discord_prefix}list")
    async def list_entries(self, ctx: commands.Context, limit: int = 10):
        \"\"\"List {agent_short} entries / {agent_short}エントリーを一覧\"\"\"
        entries = self.agent.list_entries(limit)
        if not entries:
            await ctx.send("No entries found / エントリーが見つかりません")
            return

        response = f"__{agent_short} Entries__\\n\\n"
        for entry in entries:
            response += f"**#{entry['id']}** {entry['title']} by {entry.get('username', 'Anonymous')}\\n"

        await ctx.send(response)

    @commands.command(name="{discord_prefix}team")
    async def search_team(self, ctx: commands.Context, team: str):
        \"\"\"Search entries by team / チームでエントリーを検索\"\"\"
        entries = self.agent.search_by_team(team)
        if not entries:
            await ctx.send(f"No entries found for team: {team}")
            return

        response = f"__{team} Entries__\\n\\n"
        for entry in entries[:10]:
            response += f"**#{entry['id']}** {entry['title']}\\n"

        await ctx.send(response)


def setup(bot: commands.Bot, agent):
    \"\"\"Setup cog / Cogをセットアップ\"\"\"
    bot.add_cog({class_name}Bot(bot, agent))
"""


# Template for README.md
README_TEMPLATE = """# {agent_name}

{japanese_name} - {description}

## Description / 概要

{full_description}

## Features / 機能

{features}

## Installation / インストール

```bash
pip install -r requirements.txt
```

## Usage / 使用方法

```python
from {agent_name} import {class_name}

# Create an agent / エージェントを作成
agent = {class_name}()

# Add an entry / エントリーを追加
agent.add_entry("Title", "Content", username="fan", team="Yankees")

# List entries / エントリーを一覧
entries = agent.list_entries()

# Search by team / チームで検索
team_entries = agent.search_by_team("Yankees")
```

## Database Schema / データベーススキーマ

```sql
CREATE TABLE {table_name} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    {content_field} TEXT NOT NULL,
    username TEXT,
    team TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tags TEXT
);
```

## Discord Commands / Discordコマンド

- `!{discord_prefix}add <title> <content>` - Add entry / エントリーを追加
- `!{discord_prefix}list [limit]` - List entries / エントリーを一覧
- `!{discord_prefix}team <team>` - Search by team / チームで検索

## Requirements / 要件

- Python 3.8+
- discord.py
- sqlite3

## License / ライセンス

MIT
"""


# Template for requirements.txt
REQUIREMENTS_TEMPLATE = """discord.py>=2.0.0
python-dotenv>=1.0.0
"""


# Project configuration
PROJECT_CONFIG = {
    "name": "Baseball Fan Community Agents",
    "name_ja": "野球ファンコミュニティエージェント",
    "version": "1.0.0",
    "agents": [
        {
            "agent_name": "baseball-fan-chat-agent",
            "japanese_name": "野球ファンチャットエージェント",
            "description": "Manages fan chat and discussions",
            "description_ja": "ファンチャットとディスカッションを管理",
            "table_name": "chats",
            "content_field": "message",
            "custom_method": "create_thread",
            "custom_method_description": "Create a discussion thread / ディスカッションスレッドを作成",
            "discord_prefix": "bfc",
            "full_description": "This agent manages baseball fan chat and discussions, allowing fans to share opinions, talk about games, and discuss player performance. Includes thread organization and moderation tools.",
            "full_description_ja": "このエージェントは、野球ファンのチャットとディスカッションを管理し、ファンが意見を共有し、試合について話し合い、選手のパフォーマンスについて議論できるようにします。スレッド編成とモデレーションツールが含まれます。",
            "features": """- Real-time chat / リアルタイムチャット
- Discussion threads / ディスカッションスレッド
- User moderation / ユーザーモデレーション
- Topic tagging / トピックタグ付け
- Search functionality / 検索機能"""
        },
        {
            "agent_name": "baseball-fan-event-agent",
            "japanese_name": "野球ファンイベントエージェント",
            "description": "Organizes fan meetups and watch parties",
            "description_ja": "ファンミートアップと観戦パーティを企画",
            "table_name": "events",
            "content_field": "event_details",
            "custom_method": "organize_event",
            "custom_method_description": "Organize a fan meetup event / ファンミートアップイベントを企画",
            "discord_prefix": "bfe",
            "full_description": "This agent organizes baseball fan meetups and watch parties. Fans can create events, RSVP, and coordinate attendance. Supports both in-person and virtual gatherings.",
            "full_description_ja": "このエージェントは、野球ファンのミートアップと観戦パーティを企画します。ファンはイベントを作成し、RSVPし、参加を調整できます。対面とバーチャルの両方の集まりをサポートします。",
            "features": """- Event creation / イベント作成
- RSVP management / RSVP管理
- Attendance tracking / 参加追跡
- Location coordination / 場所調整
- Calendar integration / カレンダー統合"""
        },
        {
            "agent_name": "baseball-fan-poll-agent",
            "japanese_name": "野球ファン投票エージェント",
            "description": "Creates and manages fan polls and predictions",
            "description_ja": "ファン投票と予測を作成・管理",
            "table_name": "polls",
            "content_field": "poll_data",
            "custom_method": "create_poll",
            "custom_method_description": "Create a fan poll / ファン投票を作成",
            "discord_prefix": "bfp",
            "full_description": "This agent creates and manages fan polls and predictions. Fans can vote on game outcomes, player rankings, team performance, and more. Results are displayed in real-time.",
            "full_description_ja": "このエージェントは、ファン投票と予測を作成・管理します。ファンは試合結果、選手ランキング、チームパフォーマンスなどに投票できます。結果はリアルタイムで表示されます。",
            "features": """- Poll creation / 投票作成
- Multiple choice options / 複数選択オプション
- Real-time results / リアルタイム結果
- Anonymous voting / 匿名投票
- Prediction tracking / 予測追跡"""
        },
        {
            "agent_name": "baseball-fan-share-agent",
            "japanese_name": "野球ファンシェアエージェント",
            "description": "Enables content sharing among fans",
            "description_ja": "ファン間のコンテンツ共有を有効化",
            "table_name": "shares",
            "content_field": "content",
            "custom_method": "share_content",
            "custom_method_description": "Share content with the community / コンテンツをコミュニティと共有",
            "discord_prefix": "bfs",
            "full_description": "This agent enables content sharing among baseball fans. Fans can share photos, videos, articles, and fan art. Includes tagging, commenting, and like functionality.",
            "full_description_ja": "このエージェントは、野球ファン間のコンテンツ共有を可能にします。ファンは写真、動画、記事、ファンアートを共有できます。タグ付け、コメント、いいね機能が含まれます。",
            "features": """- Photo sharing / 写真共有
- Video sharing / 動画共有
- Article links / 記事リンク
- Fan art gallery / ファンアートギャラリー
- Like and comment / いいねとコメント"""
        },
        {
            "agent_name": "baseball-fan-ranking-agent",
            "japanese_name": "野球ファンランキングエージェント",
            "description": "Tracks fan engagement and ranking",
            "description_ja": "ファンエンゲージメントとランキングを追跡",
            "table_name": "rankings",
            "content_field": "rank_data",
            "custom_method": "calculate_ranking",
            "custom_method_description": "Calculate fan engagement ranking / ファンエンゲージメントランキングを計算",
            "discord_prefix": "bfr",
            "full_description": "This agent tracks fan engagement and creates rankings based on activity, contributions, and participation. Recognizes top fans and community contributors.",
            "full_description_ja": "このエージェントは、ファンのエンゲージメントを追跡し、アクティビティ、貢献、参加に基づいてランキングを作成します。トップファンとコミュニティ貢献者を認識します。",
            "features": """- Activity tracking / アクティビティ追跡
- Contribution scoring / 貢献スコア
- Leaderboard display / リーダーボード表示
- Fan badges / ファンバッジ
- Monthly rankings / 月次ランキング"""
        }
    ]
}


class BaseballFanCommunityOrchestrator:
    """Orchestrator for Baseball Fan Community Agents / 野球ファンコミュニティエージェントのオーケストレーター"""

    def __init__(self, progress_file: str = "baseball_fan_community_progress.json"):
        self.progress_file = progress_file
        self.config = PROJECT_CONFIG
        self.workspace = Path("agents")
        self.progress = self._load_progress()

    def _load_progress(self) -> dict:
        """Load progress from file / ファイルから進捗を読み込む"""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "project_name": self.config["name"],
            "version": self.config["version"],
            "agents": {},
            "completed": 0,
            "total": len(self.config["agents"]),
            "started_at": None,
            "completed_at": None
        }

    def _save_progress(self):
        """Save progress to file / ファイルに進捗を保存"""
        with open(self.progress_file, "w", encoding="utf-8") as f:
            json.dump(self.progress, f, indent=2, ensure_ascii=False)

    def _get_class_name(self, agent_name: str) -> str:
        """Convert agent name to class name / エージェント名をクラス名に変換"""
        return "".join(word.capitalize() for word in agent_name.split("-"))

    def _create_agent_files(self, agent_config: dict):
        """Create all files for an agent / エージェントのすべてのファイルを作成"""
        agent_name = agent_config["agent_name"]
        class_name = self._get_class_name(agent_name)
        agent_dir = self.workspace / agent_name

        # Create directory
        agent_dir.mkdir(parents=True, exist_ok=True)

        # Generate content
        agent_content = self._generate_agent_code(agent_config, class_name)
        db_content = self._generate_db_code(agent_config, class_name)
        discord_content = self._generate_discord_code(agent_config, class_name)
        readme_content = self._generate_readme(agent_config)

        # Write files
        with open(agent_dir / "agent.py", "w", encoding="utf-8") as f:
            f.write(agent_content)

        with open(agent_dir / "db.py", "w", encoding="utf-8") as f:
            f.write(db_content)

        with open(agent_dir / "discord.py", "w", encoding="utf-8") as f:
            f.write(discord_content)

        with open(agent_dir / "README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)

        with open(agent_dir / "requirements.txt", "w", encoding="utf-8") as f:
            f.write(REQUIREMENTS_TEMPLATE)

        print(f"  Created: {agent_dir}")

    def _generate_agent_code(self, agent_config: dict, class_name: str) -> str:
        """Generate agent.py content / agent.pyの内容を生成"""
        template = AGENT_TEMPLATE
        return template.replace("__agent_name__", agent_config["agent_name"]) \
                       .replace("__japanese_name__", agent_config["japanese_name"]) \
                       .replace("__description__", agent_config["description"]) \
                       .replace("__class_name__", class_name) \
                       .replace("__table_name__", agent_config["table_name"]) \
                       .replace("__content_field__", agent_config["content_field"]) \
                       .replace("__custom_method__", agent_config["custom_method"]) \
                       .replace("__custom_method_description__", agent_config["custom_method_description"])

    def _generate_db_code(self, agent_config: dict, class_name: str) -> str:
        """Generate db.py content / db.pyの内容を生成"""
        template = DB_TEMPLATE
        return template.replace("__agent_name__", agent_config["agent_name"]) \
                       .replace("__class_name__", class_name)

    def _generate_discord_code(self, agent_config: dict, class_name: str) -> str:
        """Generate discord.py content / discord.pyの内容を生成"""
        template = DISCORD_TEMPLATE
        agent_short = agent_config["agent_name"].replace("-agent", "").replace("-", "_")
        return template.replace("__agent_name__", agent_config["agent_name"]) \
                       .replace("__class_name__", class_name) \
                       .replace("__discord_prefix__", agent_config["discord_prefix"]) \
                       .replace("__agent_short__", agent_short)

    def _generate_readme(self, agent_config: dict) -> str:
        """Generate README.md content / README.mdの内容を生成"""
        template = README_TEMPLATE
        return template.replace("__agent_name__", agent_config["agent_name"]) \
                       .replace("__japanese_name__", agent_config["japanese_name"]) \
                       .replace("__description__", agent_config["description"]) \
                       .replace("__table_name__", agent_config["table_name"]) \
                       .replace("__content_field__", agent_config["content_field"]) \
                       .replace("__discord_prefix__", agent_config["discord_prefix"]) \
                       .replace("__full_description__", agent_config["full_description"]) \
                       .replace("__full_description_ja__", agent_config["full_description_ja"]) \
                       .replace("__features__", agent_config["features"])

    def run(self):
        """Run orchestrator / オーケストレーターを実行"""
        print(f"Starting {self.config['name']} / {self.config['name_ja']}")

        if self.progress["started_at"] is None:
            self.progress["started_at"] = datetime.now().isoformat()
            self._save_progress()

        total = len(self.config["agents"])
        completed = 0

        for agent_config in self.config["agents"]:
            agent_name = agent_config["agent_name"]

            if agent_name in self.progress["agents"] and self.progress["agents"][agent_name].get("completed"):
                print(f"Skipping {agent_name} (already completed)")
                completed += 1
                continue

            print(f"Creating {agent_name}...")
            self._create_agent_files(agent_config)

            # Update progress
            self.progress["agents"][agent_name] = {
                "completed": True,
                "completed_at": datetime.now().isoformat()
            }
            completed += 1
            self.progress["completed"] = completed
            self._save_progress()

        # Finalize
        self.progress["completed_at"] = datetime.now().isoformat()
        self._save_progress()

        print(f"\\nProject completed! / プロジェクト完了！")
        print(f"Total agents: {total}")
        print(f"Completed: {completed}")
        return completed


def main():
    """Main function / メイン関数"""
    orchestrator = BaseballFanCommunityOrchestrator()
    result = orchestrator.run()

    # Update Plan.md
    print("\\nUpdating Plan.md...")
    # Note: Plan.md update will be done separately

    return result


if __name__ == "__main__":
    sys.exit(main())
