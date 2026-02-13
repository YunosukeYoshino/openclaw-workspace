#!/usr/bin/env python3
"""
Game Commentary Analysis Agents Orchestrator
ゲーム実況分析エージェントオーケストレーター

Orchestrates the development of game commentary analysis agents.
ゲーム実況分析エージェントの開発をオーケストレーションします。
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
        \"\"\"Initialize the database / データベースを初期化\"\"\"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                {content_field} TEXT NOT NULL,
                commentator TEXT,
                game_name TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tags TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def add_entry(self, title: str, content: str, commentator: str = "",
                   game_name: str = "", tags: str = "") -> int:
        \"\"\"Add a commentary entry / 実況エントリーを追加\"\"\"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO {table_name} (title, {content_field}, commentator, game_name, tags)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, content, commentator, game_name, tags))

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

    def search_entries(self, query: str) -> List[Dict[str, Any]]:
        \"\"\"Search entries by query / クエリでエントリーを検索\"\"\"
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM {table_name}
            WHERE title LIKE ? OR {content_field} LIKE ? OR tags LIKE ?
            ORDER BY timestamp DESC
        ''', (f"%{query}%", f"%{query}%", f"%{query}%"))

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
        entry_id = self.agent.add_entry(title, content)
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
            response += f"**#{entry['id']}** {entry['title']}\\n"

        await ctx.send(response)

    @commands.command(name="{discord_prefix}search")
    async def search_entries(self, ctx: commands.Context, *, query: str):
        \"\"\"Search {agent_short} entries / {agent_short}エントリーを検索\"\"\"
        entries = self.agent.search_entries(query)
        if not entries:
            await ctx.send(f"No entries found for: {query}")
            return

        response = f"__Search Results for: {query}__\\n\\n"
        for entry in entries[:10]:
            response += f"**#{entry['id']}** {entry['title']}\\n"

        await ctx.send(response)


def setup(bot: commands.Bot, agent):
    \"\"\"Setup the cog / Cogをセットアップ\"\"\"
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
agent.add_entry("Title", "Content")

# List entries / エントリーを一覧
entries = agent.list_entries()
```

## Database Schema / データベーススキーマ

```sql
CREATE TABLE {table_name} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    {content_field} TEXT NOT NULL,
    commentator TEXT,
    game_name TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tags TEXT
);
```

## Discord Commands / Discordコマンド

- `!{discord_prefix}add <title> <content>` - Add entry / エントリーを追加
- `!{discord_prefix}list [limit]` - List entries / エントリーを一覧
- `!{discord_prefix}search <query>` - Search entries / エントリーを検索

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
    "name": "Game Commentary Analysis Agents",
    "name_ja": "ゲーム実況分析エージェント",
    "version": "1.0.0",
    "agents": [
        {
            "agent_name": "game-commentary-analysis-agent",
            "japanese_name": "ゲーム実況分析エージェント",
            "description": "Analyzes game commentary and highlights key moments",
            "description_ja": "ゲーム実況を分析し、重要な瞬間をハイライト",
            "table_name": "commentaries",
            "content_field": "transcript",
            "custom_method": "analyze_commentary",
            "custom_method_description": "Analyze commentary and extract highlights / 実況を分析してハイライトを抽出",
            "discord_prefix": "ca",
            "full_description": "This agent analyzes game commentary from streams and videos, extracting key moments, exciting plays, and memorable quotes. It helps fans quickly find the most interesting parts of long commentary sessions.",
            "full_description_ja": "このエージェントは、ストリームや動画のゲーム実況を分析し、重要な瞬間、興奮するプレイ、記憶に残るセリフを抽出します。ファンが長い実況セッションの中から最も興味深い部分を素早く見つけられるようにします。",
            "features": """- Commentary transcription and storage / 実況の転写と保存
- Key moment detection / 重要な瞬間の検出
- Exciting play analysis / 興奮するプレイの分析
- Memorable quotes extraction / 記憶に残るセリフの抽出
- Search by commentator / 実況者で検索"""
        },
        {
            "agent_name": "game-voice-analysis-agent",
            "japanese_name": "ゲームボイス分析エージェント",
            "description": "Analyzes voice tone and emotion in game commentary",
            "description_ja": "ゲーム実況の声のトーンと感情を分析",
            "table_name": "voice_analysis",
            "content_field": "audio_data",
            "custom_method": "analyze_emotion",
            "custom_method_description": "Analyze voice emotion and sentiment / 声の感情とセンチメントを分析",
            "discord_prefix": "va",
            "full_description": "This agent analyzes voice characteristics in game commentary, detecting emotion levels, excitement, and sentiment. It provides insights into the commentator's emotional state throughout the game.",
            "full_description_ja": "このエージェントは、ゲーム実況の声の特徴を分析し、感情レベル、興奮度、センチメントを検出します。ゲームを通じての実況者の感情的状態についての洞察を提供します。",
            "features": """- Voice emotion detection / 声の感情検出
- Excitement level analysis / 興奮度の分析
- Sentiment tracking / センチメントの追跡
- Emotional timeline / 感情のタイムライン
- Commentator comparison / 実況者の比較"""
        },
        {
            "agent_name": "game-moment-clipping-agent",
            "japanese_name": "ゲームモーメントクリップエージェント",
            "description": "Automatically clips exciting game moments from commentary",
            "description_ja": "実況から興奮するゲームモーメントを自動クリップ",
            "table_name": "clips",
            "content_field": "clip_data",
            "custom_method": "generate_clip",
            "custom_method_description": "Generate a clip from timestamp / タイムスタンプからクリップを生成",
            "discord_prefix": "mc",
            "full_description": "This agent automatically identifies and clips exciting moments from game commentary based on voice analysis and gameplay events. It creates shareable short clips for social media.",
            "full_description_ja": "このエージェントは、声の分析とゲームプレイイベントに基づいて、ゲーム実況から興奮する瞬間を自動的に特定し、クリップを作成します。ソーシャルメディアで共有できる短いクリップを作成します。",
            "features": """- Automatic moment detection / 自動的な瞬間検出
- Clip generation / クリップ生成
- Timestamp tracking / タイムスタンプ追跡
- Social media export / ソーシャルメディアエクスポート
- Clip library / クリップライブラリ"""
        },
        {
            "agent_name": "game-commentary-search-agent",
            "japanese_name": "ゲーム実況検索エージェント",
            "description": "Searches and indexes game commentary for specific topics",
            "description_ja": "特定のトピックについてゲーム実況を検索・インデックス",
            "table_name": "search_index",
            "content_field": "indexed_content",
            "custom_method": "semantic_search",
            "custom_method_description": "Perform semantic search / セマンティック検索を実行",
            "discord_prefix": "cs",
            "full_description": "This agent creates a searchable index of game commentary, allowing users to find specific topics, moments, or quotes across multiple commentaries. It uses semantic search for better results.",
            "full_description_ja": "このエージェントは、ゲーム実況の検索可能なインデックスを作成し、ユーザーが複数の実況にわたって特定のトピック、瞬間、またはセリフを見つけられるようにします。より良い結果のためにセマンティック検索を使用します。",
            "features": """- Full-text search / 全文検索
- Semantic search / セマンティック検索
- Topic indexing / トピックインデックス
- Quote search / セリフ検索
- Cross-commentary search / 実況間検索"""
        },
        {
            "agent_name": "game-commentary-stats-agent",
            "japanese_name": "ゲーム実況統計エージェント",
            "description": "Provides statistics and analytics for game commentary",
            "description_ja": "ゲーム実況の統計とアナリティクスを提供",
            "table_name": "stats",
            "content_field": "stat_data",
            "custom_method": "generate_report",
            "custom_method_description": "Generate analytics report / アナリティクスレポートを生成",
            "discord_prefix": "cstat",
            "full_description": "This agent provides comprehensive statistics and analytics for game commentary, including word counts, speaking speed, vocabulary diversity, and sentiment trends over time.",
            "full_description_ja": "このエージェントは、ゲーム実況の包括的な統計とアナリティクスを提供します。単語数、話す速度、語彙の多様性、時間経過に伴うセンチメントの傾向などが含まれます。",
            "features": """- Word count analysis / 単語数分析
- Speaking speed calculation / 話す速度の計算
- Vocabulary diversity / 語彙の多様性
- Sentiment trends / センチメントの傾向
- Comparative analytics / 比較アナリティクス"""
        }
    ]
}


class GameCommentaryOrchestrator:
    """Orchestrator for Game Commentary Analysis Agents / ゲーム実況分析エージェントのオーケストレーター"""

    def __init__(self, progress_file: str = "game_commentary_progress.json"):
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
        """Run the orchestrator / オーケストレーターを実行"""
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
    orchestrator = GameCommentaryOrchestrator()
    result = orchestrator.run()

    # Update Plan.md
    print("\\nUpdating Plan.md...")
    # Note: Plan.md update will be done separately

    return result


if __name__ == "__main__":
    sys.exit(main())
