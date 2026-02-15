#!/usr/bin/env python3
"""
Game Details V2 Agents Orchestrator
ゲーム詳細エージェントV2 オーケストレーター

ユーザーの興味（ゲーム）に合わせたさらなるゲーム関連エージェントを開発する。
"""

import os
import json
from pathlib import Path
from typing import Dict, List
import time

class GameDetailsV2Orchestrator:
    """ゲーム詳細エージェントV2 オーケストレーター"""

    def __init__(self):
        self.workspace = Path("/workspace")
        self.agents_dir = self.workspace / "agents"
        self.progress_file = self.workspace / "game_details_v2_progress.json"

        # 追加エージェント一覧 (5個)
        self.agents = [
            {
                "id": "game-review-agent",
                "name": "ゲームレビューエージェント",
                "name_en": "Game Review Agent",
                "description": "ゲームレビューを管理するエージェント",
                "description_en": "Agent for managing game reviews",
                "tables": ["reviews", "entries"],
                "commands": ["review", "rating", "critic"]
            },
            {
                "id": "game-dlc-agent",
                "name": "ゲームDLCエージェント",
                "name_en": "Game DLC Agent",
                "description": "ゲームDLC・追加コンテンツを管理するエージェント",
                "description_en": "Agent for managing game DLC and additional content",
                "tables": ["dlc", "entries"],
                "commands": ["dlc", "expansion", "season"]
            },
            {
                "id": "game-esports-agent",
                "name": "ゲームeスポーツエージェント",
                "name_en": "Game Esports Agent",
                "description": "ゲームeスポーツ・トーナメント情報を管理するエージェント",
                "description_en": "Agent for managing game esports and tournament information",
                "tables": ["tournaments", "entries"],
                "commands": ["esports", "tournament", "team"]
            },
            {
                "id": "game-guide-agent",
                "name": "ゲーム攻略ガイドエージェント",
                "name_en": "Game Guide Agent",
                "description": "ゲーム攻略ガイド・チュートリアルを管理するエージェント",
                "description_en": "Agent for managing game guides and tutorials",
                "tables": ["guides", "entries"],
                "commands": ["guide", "tutorial", "tip"]
            },
            {
                "id": "game-newsletter-agent",
                "name": "ゲームニュースレターエージェント",
                "name_en": "Game Newsletter Agent",
                "description": "ゲームニュース・アップデートを管理するエージェント",
                "description_en": "Agent for managing game news and updates",
                "tables": ["news", "entries"],
                "commands": ["news", "update", "patch"]
            }
        ]

        self.load_progress()

        # テンプレート
        self.agent_py_template = """#!/usr/bin/env python3
\"\"\"
{NAME}
{NAME_EN}

{DESCRIPTION}
{DESCRIPTION_EN}
\"\"\"

import asyncio
from typing import Optional
from .db import {CLASS_NAME}DB

class {CLASS_NAME}Agent:
    \"{NAME_EN}\"\"

    def __init__(self, db_path: str = \"data/{AGENT_ID}.db\"):
        self.db = {CLASS_NAME}DB(db_path)
        self.name = \"{NAME}\"

    async def process_command(self, command: str, args: list) -> str:
        \"\"\"コマンドを処理する\"\"\"
        if command in [\"review\", \"rating\", \"critic\"]:
            return await self.show_review(args)
        elif command in [\"dlc\", \"expansion\", \"season\"]:
            return await self.show_dlc(args)
        elif command in [\"esports\", \"tournament\", \"team\"]:
            return await self.show_esports(args)
        elif command in [\"guide\", \"tutorial\", \"tip\"]:
            return await self.show_guide(args)
        elif command in [\"news\", \"update\", \"patch\"]:
            return await self.show_news(args)
        else:
            return \"不明なコマンドです。\"

    async def show_review(self, args: list) -> str:
        \"\"\"レビューを表示する\"\"\"
        reviews = self.db.get_all_reviews()
        if not reviews:
            return \"レビューが登録されていません。\"
        return \"\\\\n\".join([f\"- {{r['name']}}: {{r['score']}}/10\" for r in reviews[:5]])

    async def show_dlc(self, args: list) -> str:
        \"\"\"DLCを表示する\"\"\"
        dlc_list = self.db.get_all_dlc()
        if not dlc_list:
            return \"DLCが登録されていません。\"
        return \"\\\\n\".join([f\"- {{d['name']}} ({{d['price']}})\" for d in dlc_list[:5]])

    async def show_esports(self, args: list) -> str:
        \"\"\"eスポーツを表示する\"\"\"
        tournaments = self.db.get_all_tournaments()
        if not tournaments:
            return \"トーナメントが登録されていません。\"
        return \"\\\\n\".join([f\"- {{t['name']}} ({{t['prize']}})\" for t in tournaments[:5]])

    async def show_guide(self, args: list) -> str:
        \"\"\"ガイドを表示する\"\"\"
        guides = self.db.get_all_guides()
        if not guides:
            return \"ガイドが登録されていません。\"
        return \"\\\\n\".join([f\"- {{g['name']}}: {{g['difficulty']}}\" for g in guides[:5]])

    async def show_news(self, args: list) -> str:
        \"\"\"ニュースを表示する\"\"\"
        news = self.db.get_all_news()
        if not news:
            return \"ニュースが登録されていません。\"
        return \"\\\\n\".join([f\"- {{n['title']}} ({{n['date']}})\" for n in news[:5]])

def main():
    import sys
    agent = {CLASS_NAME}Agent()
    print(f\"{{agent.name}} エージェントが準備完了\")

if __name__ == \"__main__\":
    main()
"""

        self.db_py_template = """#!/usr/bin/env python3
\"\"\"
{NAME} Database Module
{NAME_EN} データベースモジュール
\"\"\"

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

class {CLASS_NAME}DB:
    \"{NAME_EN} Database\"

    def __init__(self, db_path: str = \"data/{AGENT_ID}.db\"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.create_tables()

    def create_tables(self):
        \"\"\"テーブルを作成する\"\"\"
        cursor = self.conn.cursor()

        # reviews/dlc/tournaments/guides/news テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # entries テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT NOT NULL,
                type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.conn.commit()

    def get_all_reviews(self) -> List[Dict]:
        \"\"\"すべてのレビューを取得する\"\"\"
        cursor = self.conn.cursor()
        cursor.execute(\"SELECT * FROM items WHERE category = 'review' ORDER BY name\")
        return [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    def get_all_dlc(self) -> List[Dict]:
        \"\"\"すべてのDLCを取得する\"\"\"
        cursor = self.conn.cursor()
        cursor.execute(\"SELECT * FROM items WHERE category = 'dlc' ORDER BY name\")
        return [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    def get_all_tournaments(self) -> List[Dict]:
        \"\"\"すべてのトーナメントを取得する\"\"\"
        cursor = self.conn.cursor()
        cursor.execute(\"SELECT * FROM items WHERE category = 'tournament' ORDER BY name\")
        return [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    def get_all_guides(self) -> List[Dict]:
        \"\"\"すべてのガイドを取得する\"\"\"
        cursor = self.conn.cursor()
        cursor.execute(\"SELECT * FROM items WHERE category = 'guide' ORDER BY name\")
        return [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    def get_all_news(self) -> List[Dict]:
        \"\"\"すべてのニュースを取得する\"\"\"
        cursor = self.conn.cursor()
        cursor.execute(\"SELECT * FROM items WHERE category = 'news' ORDER BY name DESC\")
        return [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    def add_item(self, name: str, description: str, category: str = "general") -> int:
        \"\"\"アイテムを追加する\"\"\"
        cursor = self.conn.cursor()
        cursor.execute(
            \"INSERT INTO items (name, description, category) VALUES (?, ?, ?)\",
            (name, description, category)
        )
        self.conn.commit()
        return cursor.lastrowid

    def close(self):
        \"\"\"接続を閉じる\"\"\"
        self.conn.close()

def main():
    db = {CLASS_NAME}DB()
    print(\"Database initialized\")

if __name__ == \"__main__\":
    main()
"""

        self.discord_py_template = """#!/usr/bin/env python3
\"\"\"
{NAME} Discord Bot
{NAME_EN} Discord Bot
\"\"\"

import discord
from discord.ext import commands
from typing import Optional
from .agent import {CLASS_NAME}Agent
from .db import {CLASS_NAME}DB

class {CLASS_NAME}DiscordBot(commands.Bot):
    \"{NAME_EN} Discord Bot\"

    def __init__(self, command_prefix: str = \"!\", db_path: str = \"data/{AGENT_ID}.db\"):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.agent = {CLASS_NAME}Agent(db_path)

    async def setup_hook(self):
        \"\"\"起動時の処理\"\"\"
        print(f\"{{self.agent.name}} Bot が起動しました\")

    async def on_ready(self):
        \"\"\"準備完了時の処理\"\"\"
        print(f\"Logged in as {{self.user}}\")

async def main():
    import asyncio
    bot = {CLASS_NAME}DiscordBot()
    # bot.run(\"YOUR_TOKEN_HERE\")

if __name__ == \"__main__\":
    import asyncio
    asyncio.run(main())
"""

        self.readme_template = """# {NAME} / {NAME_EN}

{DESCRIPTION}
{DESCRIPTION_EN}

## Features / 機能

- レビュー管理 (Review Management)
- DLC管理 (DLC Management)
- eスポーツ情報 (Esports Information)
- 攻略ガイド (Game Guides)
- ニュース・アップデート (News & Updates)

## Installation / インストール

```bash
pip install -r requirements.txt
```

## Usage / 使用方法

```python
from agents.{AGENT_ID}.agent import {CLASS_NAME}Agent

agent = {CLASS_NAME}Agent()
result = await agent.process_command(\"review\", [\"elden-ring\"])
print(result)
```

## Database / データベース

- `items` - アイテムデータ（レビュー、DLC、トーナメント、ガイド、ニュース）
- `entries` - 一般エントリーデータ

## Commands / コマンド

- `review <name>` - レビューを表示
- `dlc <name>` - DLCを表示
- `esports <name>` - eスポーツ情報を表示
- `guide <name>` - ガイドを表示
- `news <name>` - ニュースを表示

## License / ライセンス

MIT
"""

        self.requirements_template = """discord.py>=2.3.0
aiohttp>=3.9.0
"""

    def load_progress(self):
        """進捗を読み込む"""
        if self.progress_file.exists():
            with open(self.progress_file, "r", encoding="utf-8") as f:
                self.progress = json.load(f)
        else:
            self.progress = {
                "status": "in_progress",
                "total_agents": len(self.agents),
                "completed_agents": 0,
                "failed_agents": 0,
                "agents": {}
            }

    def save_progress(self):
        """進捗を保存する"""
        with open(self.progress_file, "w", encoding="utf-8") as f:
            json.dump(self.progress, f, ensure_ascii=False, indent=2)

    def log(self, message: str):
        """ログを出力する"""
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}")

    def create_agent_directly(self, agent_info: Dict) -> bool:
        """直接エージェントを作成する"""
        agent_id = agent_info["id"]
        agent_dir = self.agents_dir / agent_id

        self.log(f"エージェント作成: {agent_id}")

        try:
            agent_dir.mkdir(parents=True, exist_ok=True)

            # クラス名生成
            class_name = agent_id.replace('-', '_').title().replace('_', '')

            # agent.pyを作成
            agent_py_content = self.agent_py_template.replace("{NAME}", agent_info["name"]) \
                .replace("{NAME_EN}", agent_info["name_en"]) \
                .replace("{DESCRIPTION}", agent_info["description"]) \
                .replace("{DESCRIPTION_EN}", agent_info["description_en"]) \
                .replace("{CLASS_NAME}", class_name) \
                .replace("{AGENT_ID}", agent_id)

            (agent_dir / "agent.py").write_text(agent_py_content, encoding="utf-8")

            # db.pyを作成
            db_py_content = self.db_py_template.replace("{NAME}", agent_info["name"]) \
                .replace("{NAME_EN}", agent_info["name_en"]) \
                .replace("{CLASS_NAME}", class_name) \
                .replace("{AGENT_ID}", agent_id)

            (agent_dir / "db.py").write_text(db_py_content, encoding="utf-8")

            # discord.pyを作成
            discord_py_content = self.discord_py_template.replace("{NAME}", agent_info["name"]) \
                .replace("{NAME_EN}", agent_info["name_en"]) \
                .replace("{CLASS_NAME}", class_name) \
                .replace("{AGENT_ID}", agent_id)

            (agent_dir / "discord.py").write_text(discord_py_content, encoding="utf-8")

            # README.mdを作成
            readme_content = self.readme_template.replace("{NAME}", agent_info["name"]) \
                .replace("{NAME_EN}", agent_info["name_en"]) \
                .replace("{DESCRIPTION}", agent_info["description"]) \
                .replace("{DESCRIPTION_EN}", agent_info["description_en"]) \
                .replace("{CLASS_NAME}", class_name) \
                .replace("{AGENT_ID}", agent_id)

            (agent_dir / "README.md").write_text(readme_content, encoding="utf-8")

            # requirements.txtを作成
            (agent_dir / "requirements.txt").write_text(self.requirements_template, encoding="utf-8")

            self.log(f"エージェント作成完了: {agent_id}")
            return True

        except Exception as e:
            self.log(f"エージェント作成エラー: {agent_id} - {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def run(self):
        """オーケストレーションを実行する"""
        self.log("=" * 60)
        self.log("ゲーム詳細エージェントV2 プロジェクト開始")
        self.log("=" * 60)

        completed = 0
        failed = 0

        for agent in self.agents:
            agent_id = agent["id"]
            self.log(f"\\n--- エージェント作成: {agent_id} ---")

            try:
                success = self.create_agent_directly(agent)

                if success:
                    completed += 1
                    self.progress["agents"][agent_id] = {"status": "completed"}
                    self.log(f"✅ {agent_id} 完了")
                else:
                    failed += 1
                    self.progress["agents"][agent_id] = {"status": "failed"}
                    self.log(f"❌ {agent_id} 失敗")

            except Exception as e:
                failed += 1
                self.progress["agents"][agent_id] = {"status": "failed", "error": str(e)}
                self.log(f"❌ {agent_id} エラー: {str(e)}")

            self.progress["completed_agents"] = completed
            self.progress["failed_agents"] = failed
            self.save_progress()

        # サマリー
        self.log("\\n" + "=" * 60)
        self.log("プロジェクト完了サマリー")
        self.log("=" * 60)
        self.log(f"総エージェント数: {len(self.agents)}")
        self.log(f"完了: {completed}")
        self.log(f"失敗: {failed}")

        if completed == len(self.agents):
            self.progress["status"] = "completed"
            self.log("\\n🎉 すべてのエージェントが完了しました！")
        else:
            self.log(f"\\n⚠️  {failed}個のエージェントが失敗しました")

        self.save_progress()
        return completed == len(self.agents)

if __name__ == "__main__":
    orchestrator = GameDetailsV2Orchestrator()
    orchestrator.run()
