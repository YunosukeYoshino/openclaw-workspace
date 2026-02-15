#!/usr/bin/env python3
"""
Baseball Stats V3 Agents Orchestrator
野球詳細分析エージェントV3 オーケストレーター

ユーザーの興味（野球）に合わせたさらなる野球詳細分析エージェントを開発する。
選手比較、歴史的試合記録、チーム戦力分析などの高度な機能を提供する。
"""

import os
import json
from pathlib import Path
from typing import Dict, List
import time

class BaseballStatsV3Orchestrator:
    """野球詳細分析エージェントV3 オーケストレーター"""

    def __init__(self):
        self.workspace = Path("/workspace")
        self.agents_dir = self.workspace / "agents"
        self.progress_file = self.workspace / "baseball_stats_v3_progress.json"

        # 追加エージェント一覧 (5個)
        self.agents = [
            {
                "id": "baseball-compare-agent",
                "name": "野球選手比較エージェント",
                "name_en": "Baseball Player Comparison Agent",
                "description": "選手同士の比較・統計分析を行うエージェント",
                "description_en": "Agent for comparing players and performing statistical analysis",
                "tables": ["players", "comparisons", "entries"],
                "commands": ["compare", "stats", "matchup"]
            },
            {
                "id": "baseball-history-match-agent",
                "name": "野球歴史的名試合エージェント",
                "name_en": "Baseball Historic Match Agent",
                "description": "歴史的な試合記録・名場面を管理するエージェント",
                "description_en": "Agent for managing historic matches and famous plays",
                "tables": ["matches", "plays", "entries"],
                "commands": ["match", "historic", "play"]
            },
            {
                "id": "baseball-team-analysis-agent",
                "name": "野球チーム戦力分析エージェント",
                "name_en": "Baseball Team Analysis Agent",
                "description": "チームの戦力分析・予測を行うエージェント",
                "description_en": "Agent for team strength analysis and prediction",
                "tables": ["teams", "analysis", "entries"],
                "commands": ["team", "strength", "predict"]
            },
            {
                "id": "baseball-visualization-agent",
                "name": "野球データ可視化エージェント",
                "name_en": "Baseball Data Visualization Agent",
                "description": "野球データのグラフ・チャート作成を行うエージェント",
                "description_en": "Agent for creating graphs and charts of baseball data",
                "tables": ["charts", "datasets", "entries"],
                "commands": ["chart", "graph", "visualize"]
            },
            {
                "id": "baseball-scout-report-agent",
                "name": "野球スカウティングレポートエージェント",
                "name_en": "Baseball Scouting Report Agent",
                "description": "選手のスカウティングレポートを作成・管理するエージェント",
                "description_en": "Agent for creating and managing player scouting reports",
                "tables": ["scout_reports", "players", "entries"],
                "commands": ["scout", "report", "evaluate"]
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
from typing import Optional, List, Dict
from .db import {CLASS_NAME}DB

class {CLASS_NAME}Agent:
    \"{NAME_EN}\"

    def __init__(self, db_path: str = \"data/{AGENT_ID}.db\"):
        self.db = {CLASS_NAME}DB(db_path)
        self.name = \"{NAME}\"

    async def process_command(self, command: str, args: list) -> str:
        \"\"\"コマンドを処理する\"\"\"
        if command in [\"compare\", \"stats\", \"matchup\"]:
            return await self.compare_players(args)
        elif command in [\"match\", \"historic\", \"play\"]:
            return await self.show_match(args)
        elif command in [\"team\", \"strength\", \"predict\"]:
            return await self.analyze_team(args)
        elif command in [\"chart\", \"graph\", \"visualize\"]:
            return await self.visualize_data(args)
        elif command in [\"scout\", \"report\", \"evaluate\"]:
            return await self.scout_report(args)
        else:
            return \"不明なコマンドです。\"

    async def compare_players(self, args: list) -> str:
        \"\"\"選手を比較する\"\"\"
        if len(args) < 2:
            return \"比較する選手名を2つ指定してください。\"
        player1 = args[0]
        player2 = args[1]
        comparison = self.db.get_player_comparison(player1, player2)
        if not comparison:
            return \"選手が見つかりません。\"
        return f\"\"\"**{player1} vs {player2}**

{comparison}
\"\"\"

    async def show_match(self, args: list) -> str:
        \"\"\"試合を表示する\"\"\"
        if not args:
            matches = self.db.get_all_matches()
            if not matches:
                return \"試合が登録されていません。\"
            return \"\\\\n\".join([f\"- {{m['date']}}: {{m['description']}}\" for m in matches[:5]])
        match_id = args[0]
        match = self.db.get_match(match_id)
        if not match:
            return \"試合が見つかりません。\"
        return match

    async def analyze_team(self, args: list) -> str:
        \"\"\"チームを分析する\"\"\"
        if not args:
            teams = self.db.get_all_teams()
            if not teams:
                return \"チームが登録されていません。\"
            return \"\\\\n\".join([f\"- {{t['name']}}: 戦力 {{t['strength']}}\" for t in teams[:5]])
        team_name = args[0]
        analysis = self.db.get_team_analysis(team_name)
        if not analysis:
            return \"チームが見つかりません。\"
        return f\"\"\"**{team_name} 戦力分析**

{analysis}
\"\"\"

    async def visualize_data(self, args: list) -> str:
        \"\"\"データを可視化する\"\"\"
        charts = self.db.get_all_charts()
        if not charts:
            return \"チャートが登録されていません。\"
        return \"\\\\n\".join([f\"- {{c['name']}}: {{c['type']}}\" for c in charts[:5]])

    async def scout_report(self, args: list) -> str:
        \"\"\"スカウティングレポートを表示する\"\"\"
        if not args:
            reports = self.db.get_all_reports()
            if not reports:
                return \"レポートが登録されていません。\"
            return \"\\\\n\".join([f\"- {{r['player']}}: {{r['rating']}}\" for r in reports[:5]])
        player_name = args[0]
        report = self.db.get_player_report(player_name)
        if not report:
            return \"レポートが見つかりません。\"
        return f\"\"\"**{player_name} スカウティングレポート**

{report}
\"\"\"

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

        # players/matches/teams/charts/scout_reports テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS main_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                data_type TEXT,
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

    def get_player_comparison(self, player1: str, player2: str) -> Optional[str]:
        \"\"\"選手の比較を取得する\"\"\"
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT description FROM main_table WHERE name = ? OR name = ? AND data_type = 'player'",
            (player1, player2)
        )
        rows = cursor.fetchall()
        if len(rows) < 2:
            return None
        return f\"{rows[0][0]}\\n\\n{rows[1][0]}\"

    def get_all_matches(self) -> List[Dict]:
        \"\"\"すべての試合を取得する\"\"\"
        cursor = self.conn.cursor()
        cursor.execute(\"SELECT * FROM main_table WHERE data_type = 'match' ORDER BY name\")
        return [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    def get_match(self, match_id: str) -> Optional[str]:
        \"\"\"試合を取得する\"\"\"
        cursor = self.conn.cursor()
        cursor.execute(
            \"SELECT description FROM main_table WHERE name = ? AND data_type = 'match'\",
            (match_id,)
        )
        row = cursor.fetchone()
        return row[0] if row else None

    def get_all_teams(self) -> List[Dict]:
        \"\"\"すべてのチームを取得する\"\"\"
        cursor = self.conn.cursor()
        cursor.execute(\"SELECT * FROM main_table WHERE data_type = 'team' ORDER BY name\")
        return [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    def get_team_analysis(self, team_name: str) -> Optional[str]:
        \"\"\"チーム分析を取得する\"\"\"
        cursor = self.conn.cursor()
        cursor.execute(
            \"SELECT description FROM main_table WHERE name = ? AND data_type = 'team'\",
            (team_name,)
        )
        row = cursor.fetchone()
        return row[0] if row else None

    def get_all_charts(self) -> List[Dict]:
        \"\"\"すべてのチャートを取得する\"\"\"
        cursor = self.conn.cursor()
        cursor.execute(\"SELECT * FROM main_table WHERE data_type = 'chart' ORDER BY name\")
        return [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    def get_all_reports(self) -> List[Dict]:
        \"\"\"すべてのレポートを取得する\"\"\"
        cursor = self.conn.cursor()
        cursor.execute(\"SELECT * FROM main_table WHERE data_type = 'report' ORDER BY name\")
        return [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    def get_player_report(self, player_name: str) -> Optional[str]:
        \"\"\"選手レポートを取得する\"\"\"
        cursor = self.conn.cursor()
        cursor.execute(
            \"SELECT description FROM main_table WHERE name = ? AND data_type = 'report'\",
            (player_name,)
        )
        row = cursor.fetchone()
        return row[0] if row else None

    def add_item(self, name: str, description: str, data_type: str = "general") -> int:
        \"\"\"アイテムを追加する\"\"\"
        cursor = self.conn.cursor()
        cursor.execute(
            \"INSERT INTO main_table (name, description, data_type) VALUES (?, ?, ?)\",
            (name, description, data_type)
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

- 選手比較 (Player Comparison)
- 歴史的試合記録 (Historic Match Records)
- チーム戦力分析 (Team Strength Analysis)
- データ可視化 (Data Visualization)
- スカウティングレポート (Scouting Reports)

## Installation / インストール

```bash
pip install -r requirements.txt
```

## Usage / 使用方法

```python
from agents.{AGENT_ID}.agent import {CLASS_NAME}Agent

agent = {CLASS_NAME}Agent()
result = await agent.process_command(\"compare\", [\"player1\", \"player2\"])
print(result)
```

## Database / データベース

- `main_table` - メインデータ（選手、試合、チーム、チャート、レポート）
- `entries` - 一般エントリーデータ

## Commands / コマンド

- `compare <player1> <player2>` - 選手を比較
- `match <id>` - 試合情報を表示
- `team <name>` - チーム戦力を分析
- `chart <name>` - データを可視化
- `scout <player>` - スカウティングレポートを表示

## License / ライセンス

MIT
"""

        self.requirements_template = """discord.py>=2.3.0
aiohttp>=3.9.0
matplotlib>=3.7.0
pandas>=2.0.0
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
        self.log("野球詳細分析エージェントV3 プロジェクト開始")
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
    orchestrator = BaseballStatsV3Orchestrator()
    orchestrator.run()
