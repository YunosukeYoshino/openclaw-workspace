#!/usr/bin/env python3
"""
Baseball Extended Agents Orchestrator
野球追加エージェントV2 オーケストレーター

ユーザーの興味（野球）に合わせたさらなる野球関連エージェントを開発する。
"""

import os
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional

class BaseballExtendedOrchestrator:
    """野球追加エージェントV2 オーケストレーター"""

    def __init__(self):
        self.workspace = Path("/workspace")
        self.agents_dir = self.workspace / "agents"
        self.progress_file = self.workspace / "baseball_extended_progress.json"
        self.subagent_sessions = {}

        # 追加エージェント一覧 (5個)
        self.agents = [
            {
                "id": "baseball-rule-agent",
                "name": "野球ルール説明エージェント",
                "name_en": "Baseball Rule Explanation Agent",
                "description": "野球のルール・用語を説明するエージェント",
                "description_en": "Agent for explaining baseball rules and terminology",
                "tables": ["rules", "entries"],
                "commands": ["rule", "term", "explain"]
            },
            {
                "id": "baseball-hof-agent",
                "name": "野球殿堂エージェント",
                "name_en": "Baseball Hall of Fame Agent",
                "description": "野球殿堂入り選手・殿堂情報を管理するエージェント",
                "description_en": "Agent for managing Baseball Hall of Fame inductees and information",
                "tables": ["hall_of_fame", "entries"],
                "commands": ["hof", "inductee", "category"]
            },
            {
                "id": "baseball-award-agent",
                "name": "野球賞エージェント",
                "name_en": "Baseball Awards Agent",
                "description": "野球の各種受賞歴を管理するエージェント",
                "description_en": "Agent for managing various baseball awards",
                "tables": ["awards", "entries"],
                "commands": ["award", "mvp", "cy"]
            },
            {
                "id": "baseball-stadium-agent",
                "name": "野球場エージェント",
                "name_en": "Baseball Stadium Agent",
                "description": "野球場情報・観戦ガイドを管理するエージェント",
                "description_en": "Agent for managing baseball stadium information and viewing guides",
                "tables": ["stadiums", "entries"],
                "commands": ["stadium", "seat", "access"]
            },
            {
                "id": "baseball-legend-agent",
                "name": "野球伝説エージェント",
                "name_en": "Baseball Legends Agent",
                "description": "野球の伝説的選手・名場面を管理するエージェント",
                "description_en": "Agent for managing legendary baseball players and famous plays",
                "tables": ["legends", "entries"],
                "commands": ["legend", "play", "record"]
            }
        ]

        self.load_progress()

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

    def spawn_agent_creator(self, agent_info: Dict) -> bool:
        """サブエージェントを起動してエージェントを作成する"""
        agent_id = agent_info["id"]

        self.log(f"サブエージェントを起動: {agent_id}")

        try:
            # サブエージェントにタスクを送信
            task = f"""
Create a new agent with the following specifications:

Agent ID: {agent_id}
Name: {agent_info["name"]}
Name (English): {agent_info["name_en"]}
Description: {agent_info["description"]}
Description (English): {agent_info["description_en"]}

Database Tables: {agent_info["tables"]}
Commands: {agent_info["commands"]}

Required files:
1. agent.py - Main agent implementation with Discord bot integration
2. db.py - SQLite database module with specified tables
3. discord.py - Discord bot module
4. README.md - Bilingual documentation (Japanese and English)
5. requirements.txt - Dependencies

Follow this structure:

agents/{agent_id}/
  ├── agent.py
  ├── db.py
  ├── discord.py
  ├── README.md
  └── requirements.txt

Create all files and ensure they are complete and functional.
"""

            # サブエージェントを起動
            session_key = f"agent-creator-{agent_id}"
            result = subprocess.run(
                ["npx", "-y", "openclaw", "sessions", "spawn", "--task", task, "--label", f"create-{agent_id}"],
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                self.log(f"サブエージェント起動成功: {agent_id}")
                self.subagent_sessions[agent_id] = {"status": "launched", "result": result.stdout}
                return True
            else:
                self.log(f"サブエージェント起動失敗: {agent_id} - {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.log(f"サブエージェント起動タイムアウト: {agent_id}")
            return False
        except Exception as e:
            self.log(f"サブエージェント起動エラー: {agent_id} - {str(e)}")
            return False

    def create_agent_directly(self, agent_info: Dict) -> bool:
        """直接エージェントを作成する（フォールバック）"""
        agent_id = agent_info["id"]
        agent_dir = self.agents_dir / agent_id

        self.log(f"エージェント作成: {agent_id}")

        try:
            agent_dir.mkdir(parents=True, exist_ok=True)

            # agent.pyを作成
            agent_py_content = f'''#!/usr/bin/env python3
"""
{agent_info["name"]}
{agent_info["name_en"]}

{agent_info["description"]}
{agent_info["description_en"]}
"""

import asyncio
from typing import Optional
from .db import {agent_id.replace('-', '_')}_db

class {agent_id.replace('-', '_').title().replace('_', '')}Agent:
    """{agent_info["name_en"]}"""

    def __init__(self, db_path: str = "data/{agent_id}.db"):
        self.db = {agent_id.replace('-', '_')}_db(db_path)
        self.name = "{agent_info["name"]}"

    async def process_command(self, command: str, args: list) -> str:
        """コマンドを処理する"""
        if command in ["rule", "term", "explain"]:
            return await self.show_rule(args)
        elif command in ["hof", "inductee", "category"]:
            return await self.show_hof(args)
        elif command in ["award", "mvp", "cy"]:
            return await self.show_award(args)
        elif command in ["stadium", "seat", "access"]:
            return await self.show_stadium(args)
        elif command in ["legend", "play", "record"]:
            return await self.show_legend(args)
        else:
            return "不明なコマンドです。"

    async def show_rule(self, args: list) -> str:
        """ルールを表示する"""
        rules = self.db.get_all_rules()
        if not rules:
            return "ルールが登録されていません。"
        return "\\n".join([f"- {{r['name']}}: {{r['description']}}" for r in rules[:5]])

    async def show_hof(self, args: list) -> str:
        """殿堂入り選手を表示する"""
        inductees = self.db.get_all_inductees()
        if not inductees:
            return "殿堂入り選手が登録されていません。"
        return "\\n".join([f"- {{i['name']}} ({{i['year']}})" for i in inductees[:5]])

    async def show_award(self, args: list) -> str:
        """賞を表示する"""
        awards = self.db.get_all_awards()
        if not awards:
            return "賞が登録されていません。"
        return "\\n".join([f"- {{a['name']}} ({{a['year']}})" for a in awards[:5]])

    async def show_stadium(self, args: list) -> str:
        """野球場を表示する"""
        stadiums = self.db.get_all_stadiums()
        if not stadiums:
            return "野球場が登録されていません。"
        return "\\n".join([f"- {{s['name']}} (収容: {{s['capacity']}})" for s in stadiums[:5]])

    async def show_legend(self, args: list) -> str:
        """伝説を表示する"""
        legends = self.db.get_all_legends()
        if not legends:
            return "伝説が登録されていません。"
        return "\\n".join([f"- {{l['name']}}: {{l['description']}}" for l in legends[:5]])

def main():
    import sys
    agent = {agent_id.replace('-', '_').title().replace('_', '')}Agent()
    print(f"{{agent.name}} エージェントが準備完了")

if __name__ == "__main__":
    main()
'''

            (agent_dir / "agent.py").write_text(agent_py_content, encoding="utf-8")

            # db.pyを作成
            db_content_template = """#!/usr/bin/env python3
\"\"\"
{NAME}
{NAME_EN} データベースモジュール
\"\"\"

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

class {CLASS_NAME}DB:
    \"\"\"{NAME_EN} Database\"\"\"

    def __init__(self, db_path: str = "data/{AGENT_ID}.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.create_tables()

    def create_tables(self):
        \"\"\"テーブルを作成する\"\"\"
        cursor = self.conn.cursor()

        # rules/stadiums/legends テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rules (
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

        self.conn.commit()"""

            class_name = agent_id.replace('-', '_').replace('-', '').title()
            db_py_content = db_content_template.replace("{NAME}", agent_info["name"]).replace("{NAME_EN}", agent_info["name_en"]).replace("{CLASS_NAME}", class_name).replace("{AGENT_ID}", agent_id)


    def get_all_rules(self) -> List[Dict]:
        \"\"\"すべてのルールを取得する\"\"\"
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM rules ORDER BY name")
        return [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    def get_all_inductees(self) -> List[Dict]:
        \"\"\"すべての殿堂入り選手を取得する（rulesテーブルを使用）\"\"\"
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM rules WHERE category = 'hof' ORDER BY name")
        return [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    def get_all_awards(self) -> List[Dict]:
        \"\"\"すべての賞を取得する（rulesテーブルを使用）\"\"\"
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM rules WHERE category = 'award' ORDER BY name")
        return [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    def get_all_stadiums(self) -> List[Dict]:
        \"\"\"すべての野球場を取得する（rulesテーブルを使用）\"\"\"
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM rules WHERE category = 'stadium' ORDER BY name")
        return [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    def get_all_legends(self) -> List[Dict]:
        \"\"\"すべての伝説を取得する（rulesテーブルを使用）\"\"\"
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM rules WHERE category = 'legend' ORDER BY name")
        return [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    def add_rule(self, name: str, description: str, category: str = "general") -> int:
        \"\"\"ルールを追加する\"\"\"
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO rules (name, description, category) VALUES (?, ?, ?)",
            (name, description, category)
        )
        self.conn.commit()
        return cursor.lastrowid

    def close(self):
        \"\"\"接続を閉じる\"\"\"
        self.conn.close()

def main():
    db = {CLASS_NAME}DB()
    print("Database initialized")

if __name__ == "__main__":
    main()
"""

            (agent_dir / "db.py").write_text(db_py_content, encoding="utf-8")

            # discord.pyを作成
            discord_py_content = f'''#!/usr/bin/env python3
"""
{agent_info["name"]} Discord Bot
{agent_info["name_en"]} Discord Bot
"""

import discord
from discord.ext import commands
from typing import Optional
from .agent import {agent_id.replace('-', '_').title().replace('_', '')}Agent
from .db import {agent_id.replace('-', '_').replace('-', '')}DB

class {agent_id.replace('-', '_').title().replace('_', '')}DiscordBot(commands.Bot):
    """{agent_info["name_en"]} Discord Bot"""

    def __init__(self, command_prefix: str = "!", db_path: str = "data/{agent_id}.db"):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.agent = {agent_id.replace('-', '_').title().replace('_', '')}Agent(db_path)

    async def setup_hook(self):
        """起動時の処理"""
        print(f"{{self.agent.name}} Bot が起動しました")

    async def on_ready(self):
        """準備完了時の処理"""
        print(f"Logged in as {{self.user}}")

async def main():
    import asyncio
    bot = {agent_id.replace('-', '_').title().replace('_', '')}DiscordBot()
    # bot.run("YOUR_TOKEN_HERE")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
'''

            (agent_dir / "discord.py").write_text(discord_py_content, encoding="utf-8")

            # README.mdを作成
            readme_content = f'''# {agent_info["name"]} / {agent_info["name_en"]}

{agent_info["description"]}
{agent_info["description_en"]}

## Features / 機能

- ルール・用語の説明 (Rule Explanation)
- 殿堂入り選手の管理 (Hall of Fame Management)
- 賞の管理 (Awards Management)
- 野球場情報の管理 (Stadium Information Management)
- 伝説的選手・名場面の管理 (Legends Management)

## Installation / インストール

```bash
pip install -r requirements.txt
```

## Usage / 使用方法

```python
from agents.{agent_id}.agent import {agent_id.replace('-', '_').title().replace('_', '')}Agent

agent = {agent_id.replace('-', '_').title().replace('_', '')}Agent()
result = await agent.process_command("rule", ["obstruction"])
print(result)
```

## Database / データベース

- `rules` - ルール・用語データ
- `entries` - 一般エントリーデータ

## Commands / コマンド

- `rule <term>` - 用語を説明
- `hof <name>` - 殿堂入り選手を表示
- `award <name>` - 賞を表示
- `stadium <name>` - 野球場情報を表示
- `legend <name>` - 伝説を表示

## License / ライセンス

MIT
'''

            (agent_dir / "README.md").write_text(readme_content, encoding="utf-8")

            # requirements.txtを作成
            requirements_content = '''discord.py>=2.3.0
aiohttp>=3.9.0
'''

            (agent_dir / "requirements.txt").write_text(requirements_content, encoding="utf-8")

            self.log(f"エージェント作成完了: {agent_id}")
            return True

        except Exception as e:
            self.log(f"エージェント作成エラー: {agent_id} - {str(e)}")
            return False

    def run(self):
        """オーケストレーションを実行する"""
        self.log("=" * 60)
        self.log("野球追加エージェントV2 プロジェクト開始")
        self.log("=" * 60)

        completed = 0
        failed = 0

        for agent in self.agents:
            agent_id = agent["id"]
            self.log(f"\\n--- エージェント作成: {agent_id} ---")

            try:
                # サブエージェントで作成を試みる
                success = self.spawn_agent_creator(agent)

                # 失敗したら直接作成
                if not success:
                    self.log(f"フォールバック: 直接作成を試みます")
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
    orchestrator = BaseballExtendedOrchestrator()
    orchestrator.run()
