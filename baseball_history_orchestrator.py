#!/usr/bin/env python3
"""
Baseball History & Legacy Agents Orchestrator
野球歴史・伝承エージェントオーケストレーター

自律的に5個の野球歴史・伝承エージェントを作成するオーケストレーター
"""

import os
import json
from pathlib import Path

class BaseballHistoryOrchestrator:
    def __init__(self, workspace="/workspace"):
        self.workspace = Path(workspace)
        self.agents_dir = self.workspace / "agents"
        self.progress_file = self.workspace / "baseball_history_progress.json"
        self.agents = [
            {
                "name": "baseball-historical-match-agent",
                "name_ja": "野球歴史的名試合エージェント",
                "name_en": "Baseball Historical Match Agent",
                "description_ja": "歴史的な名試合、ドラマチックな展開の記録・分析",
                "description_en": "Records and analyzes historic legendary matches and dramatic moments",
                "keywords": ["historical", "matches", "baseball", "history", "records"]
            },
            {
                "name": "baseball-legend-profile-agent",
                "name_ja": "野球伝説選手プロフィールエージェント",
                "name_en": "Baseball Legend Profile Agent",
                "description_ja": "殿堂入り選手、レジェンド選手のプロフィール管理",
                "description_en": "Manages profiles of Hall of Fame and legendary players",
                "keywords": ["legend", "hall_of_fame", "player", "profile", "baseball"]
            },
            {
                "name": "baseball-evolution-agent",
                "name_ja": "野球戦術・ルール進化エージェント",
                "name_en": "Baseball Evolution Agent",
                "description_ja": "野球戦術の歴史的進化、ルール変更の影響分析",
                "description_en": "Tracks historical evolution of baseball tactics and analyzes rule changes",
                "keywords": ["evolution", "tactics", "rules", "baseball", "strategy"]
            },
            {
                "name": "baseball-stadium-history-agent",
                "name_ja": "野球場歴史エージェント",
                "name_en": "Baseball Stadium History Agent",
                "description_ja": "歴史的野球場の歴史、特徴、伝説的なイベント",
                "description_en": "History of historic baseball stadiums, features, and legendary events",
                "keywords": ["stadium", "ballpark", "history", "baseball", "venues"]
            },
            {
                "name": "baseball-culture-agent",
                "name_ja": "野球文化エージェント",
                "name_en": "Baseball Culture Agent",
                "description_ja": "野球に関連する音楽、映画、文学、アート、ファン文化",
                "description_en": "Baseball-related music, movies, literature, art, and fan culture",
                "keywords": ["culture", "music", "movies", "literature", "baseball", "art"]
            }
        ]

    def load_progress(self):
        if self.progress_file.exists():
            return json.loads(self.progress_file.read_text())
        return {"completed": [], "total": len(self.agents)}

    def save_progress(self, progress):
        self.progress_file.write_text(json.dumps(progress, indent=2, ensure_ascii=False))

    def create_agent(self, agent_info):
        agent_dir = self.agents_dir / agent_info["name"]
        agent_dir.mkdir(parents=True, exist_ok=True)

        # Create agent.py
        agent_py = self._generate_agent_py(agent_info)
        (agent_dir / "agent.py").write_text(agent_py, encoding="utf-8")

        # Create db.py
        db_py = self._generate_db_py(agent_info)
        (agent_dir / "db.py").write_text(db_py, encoding="utf-8")

        # Create discord.py
        discord_py = self._generate_discord_py(agent_info)
        (agent_dir / "discord.py").write_text(discord_py, encoding="utf-8")

        # Create requirements.txt
        requirements_txt = self._generate_requirements_txt()
        (agent_dir / "requirements.txt").write_text(requirements_txt, encoding="utf-8")

        # Create README.md
        readme_md = self._generate_readme_md(agent_info)
        (agent_dir / "README.md").write_text(readme_md, encoding="utf-8")

        return agent_dir

    def _generate_agent_py(self, agent_info):
        return f'''#!/usr/bin/env python3
"""
{agent_info["name_ja"]} / {agent_info["name_en"]}
{agent_info["description_ja"]}
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class {self._to_class_name(agent_info["name"])}:
    """野球歴史・伝承エージェント"""

    def __init__(self, config: Dict = None):
        self.config = config or {{}}
        self.name = "{agent_info["name"]}"
        self.keywords = {agent_info["keywords"]}

    async def analyze_historical_data(self, query: str) -> Dict:
        """歴史データを分析"""
        return {{
            "query": query,
            "result": f"Historical analysis for {{query}}",
            "timestamp": datetime.now().isoformat()
        }}

    async def search_records(self, criteria: Dict) -> List[Dict]:
        """記録を検索"""
        return [
            {{
                "id": 1,
                "type": "record",
                "description": f"Record matching {{criteria}}"
            }}
        ]

    async def get_legacy_info(self, entity_type: str, entity_id: str) -> Optional[Dict]:
        """伝承情報を取得"""
        return {{
            "entity_type": entity_type,
            "entity_id": entity_id,
            "legacy_data": "Historical information"
        }}

    async def run(self, task: str) -> Dict:
        """タスクを実行"""
        logger.info(f"Running task: {{task}}")

        if "analyze" in task.lower():
            return await self.analyze_historical_data(task)
        elif "search" in task.lower():
            return await self.search_records({{"query": task}})
        elif "legacy" in task.lower():
            return await self.get_legacy_info("baseball", "1")
        else:
            return {{"status": "unknown_task", "task": task}}

def main():
    import asyncio

    agent = {self._to_class_name(agent_info["name"])}()
    result = asyncio.run(agent.run("analyze"))
    print(result)

if __name__ == "__main__":
    main()
'''

    def _generate_db_py(self, agent_info):
        return f'''#!/usr/bin/env python3
"""
{agent_info["name_ja"]} - Database Module
野球歴史・伝承エージェントデータベースモジュール
"""

import sqlite3
import logging
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class {self._to_class_name(agent_info["name"])}Database:
    """野球歴史・伝承データベースクラス"""

    def __init__(self, db_path: str = "baseball_history.db"):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {{e}}")
            raise
        finally:
            conn.close()

    def _init_db(self):
        """データベースを初期化"""
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS historical_matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    match_date TEXT NOT NULL,
                    teams TEXT NOT NULL,
                    score TEXT NOT NULL,
                    importance TEXT,
                    description TEXT,
                    highlights TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS legends (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    team TEXT,
                    era TEXT,
                    achievements TEXT,
                    stats TEXT,
                    bio TEXT,
                    image_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS stadiums (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    location TEXT,
                    year_opened INTEGER,
                    year_closed INTEGER,
                    capacity INTEGER,
                    features TEXT,
                    memorable_events TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS culture (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    year INTEGER,
                    description TEXT,
                    related_teams TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS evolution (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    era TEXT NOT NULL,
                    description TEXT NOT NULL,
                    impact TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_match_date ON historical_matches(match_date);
                CREATE INDEX IF NOT EXISTS idx_legend_name ON legends(name);
                CREATE INDEX IF NOT EXISTS idx_stadium_name ON stadiums(name);
                CREATE INDEX IF NOT EXISTS idx_culture_type ON culture(type);
            """)

    def add_historical_match(self, match_data: Dict) -> int:
        """歴史的名試合を追加"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO historical_matches
                   (match_date, teams, score, importance, description, highlights)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    match_data.get("match_date"),
                    match_data.get("teams"),
                    match_data.get("score"),
                    match_data.get("importance"),
                    match_data.get("description"),
                    json.dumps(match_data.get("highlights", []))
                )
            )
            return cursor.lastrowid

    def get_historical_matches(self, limit: int = 50) -> List[Dict]:
        """歴史的名試合一覧を取得"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM historical_matches ORDER BY match_date DESC LIMIT ?",
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def add_legend(self, legend_data: Dict) -> int:
        """伝説選手を追加"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO legends
                   (name, team, era, achievements, stats, bio, image_url)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    legend_data.get("name"),
                    legend_data.get("team"),
                    legend_data.get("era"),
                    json.dumps(legend_data.get("achievements", [])),
                    json.dumps(legend_data.get("stats", {{}})),
                    legend_data.get("bio"),
                    legend_data.get("image_url")
                )
            )
            return cursor.lastrowid

    def get_legends(self, team: Optional[str] = None, era: Optional[str] = None) -> List[Dict]:
        """伝説選手一覧を取得"""
        query = "SELECT * FROM legends WHERE 1=1"
        params = []

        if team:
            query += " AND team = ?"
            params.append(team)

        if era:
            query += " AND era = ?"
            params.append(era)

        query += " ORDER BY name"

        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def add_stadium(self, stadium_data: Dict) -> int:
        """野球場を追加"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO stadiums
                   (name, location, year_opened, year_closed, capacity, features, memorable_events)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    stadium_data.get("name"),
                    stadium_data.get("location"),
                    stadium_data.get("year_opened"),
                    stadium_data.get("year_closed"),
                    stadium_data.get("capacity"),
                    json.dumps(stadium_data.get("features", [])),
                    json.dumps(stadium_data.get("memorable_events", []))
                )
            )
            return cursor.lastrowid

    def get_stadiums(self) -> List[Dict]:
        """野球場一覧を取得"""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM stadiums ORDER BY year_opened")
            return [dict(row) for row in cursor.fetchall()]

    def add_culture_item(self, item_data: Dict) -> int:
        """文化アイテムを追加"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO culture
                   (type, title, year, description, related_teams)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    item_data.get("type"),
                    item_data.get("title"),
                    item_data.get("year"),
                    item_data.get("description"),
                    json.dumps(item_data.get("related_teams", []))
                )
            )
            return cursor.lastrowid

    def get_culture_items(self, item_type: Optional[str] = None) -> List[Dict]:
        """文化アイテム一覧を取得"""
        query = "SELECT * FROM culture WHERE 1=1"
        params = []

        if item_type:
            query += " AND type = ?"
            params.append(item_type)

        query += " ORDER BY year DESC, title"

        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def add_evolution(self, evolution_data: Dict) -> int:
        """進化情報を追加"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO evolution
                   (type, era, description, impact)
                   VALUES (?, ?, ?, ?)""",
                (
                    evolution_data.get("type"),
                    evolution_data.get("era"),
                    evolution_data.get("description"),
                    evolution_data.get("impact")
                )
            )
            return cursor.lastrowid

    def get_evolution_history(self, ev_type: Optional[str] = None) -> List[Dict]:
        """進化履歴を取得"""
        query = "SELECT * FROM evolution WHERE 1=1"
        params = []

        if ev_type:
            query += " AND type = ?"
            params.append(ev_type)

        query += " ORDER BY era"

        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

def main():
    """テスト実行"""
    db = {self._to_class_name(agent_info["name"])}Database()

    # テストデータを追加
    match_id = db.add_historical_match({{
        "match_date": "1960-10-13",
        "teams": "Pittsburgh Pirates vs New York Yankees",
        "score": "10-9",
        "importance": "World Series Game 7",
        "description": "Bill Mazeroski's walk-off home run",
        "highlights": ["Mazeroski HR"]
    }})

    print(f"Added match ID: {{match_id}}")
    print(f"Historical matches: {{len(db.get_historical_matches())}}")

if __name__ == "__main__":
    import json
    main()
'''

    def _generate_discord_py(self, agent_info):
        return f'''#!/usr/bin/env python3
"""
{agent_info["name_ja"]} - Discord Bot Module
野球歴史・伝承エージェントDiscordボットモジュール
"""

import discord
from discord.ext import commands
import logging
import json
from typing import Optional
from datetime import datetime

from db import {self._to_class_name(agent_info["name"])}Database

logger = logging.getLogger(__name__)

class {self._to_class_name(agent_info["name"])}Bot(commands.Bot):
    """野球歴史・伝承Discordボット"""

    def __init__(self, command_prefix: str = "!history", db_path: str = "baseball_history.db"):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=command_prefix, intents=intents)

        self.db = {self._to_class_name(agent_info["name"])}Database(db_path)

    async def on_ready(self):
        logger.info(f"{{self.user.name}} is ready!")

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return

        await self.process_commands(message)

    @commands.command(name="match", aliases=["m"])
    async def get_historical_match(self, ctx: commands.Context, limit: int = 5):
        """歴史的名試合一覧を表示"""
        matches = self.db.get_historical_matches(limit=limit)

        if not matches:
            await ctx.send("No historical matches found.")
            return

        embed = discord.Embed(
            title="Historical Baseball Matches / 歴史的名試合",
            color=discord.Color.blue()
        )

        for match in matches:
            embed.add_field(
                name=f"{{match['teams']}} ({{match['match_date']}})",
                value=f"Score: {{match['score']}}\\nImportance: {{match.get('importance', 'N/A')}}",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name="legend", aliases=["l"])
    async def get_legend(self, ctx: commands.Context, *, name: Optional[str] = None):
        """伝説選手情報を表示"""
        if name:
            legends = [l for l in self.db.get_legends() if name.lower() in l["name"].lower()]
        else:
            legends = self.db.get_legends()[:5]

        if not legends:
            await ctx.send("No legends found.")
            return

        embed = discord.Embed(
            title="Baseball Legends / 野球伝説選手",
            color=discord.Color.gold()
        )

        for legend in legends:
            achievements = json.loads(legend.get("achievements", "[]"))
            achievements_text = ", ".join(achievements[:3]) if achievements else "N/A"

            embed.add_field(
                name=f"{{legend['name']}} ({{legend.get('team', 'N/A')}})",
                value=f"Era: {{legend.get('era', 'N/A')}}\\nAchievements: {{achievements_text}}",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name="stadium", aliases=["s"])
    async def get_stadium(self, ctx: commands.Context, *, name: Optional[str] = None):
        """野球場情報を表示"""
        stadiums = self.db.get_stadiums()

        if name:
            stadiums = [s for s in stadiums if name.lower() in s["name"].lower()]

        if not stadiums:
            await ctx.send("No stadiums found.")
            return

        embed = discord.Embed(
            title="Baseball Stadiums / 野球場",
            color=discord.Color.green()
        )

        for stadium in stadiums[:5]:
            years = f"{{stadium.get('year_opened')}}-{{stadium.get('year_closed', 'present')}}"
            embed.add_field(
                name=f"{{stadium['name']}}",
                value=f"Location: {{stadium.get('location', 'N/A')}}\\nYears: {{years}}",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name="culture", aliases=["c"])
    async def get_culture(self, ctx: commands.Context, item_type: Optional[str] = None):
        """野球文化を表示"""
        items = self.db.get_culture_items(item_type)

        if not items:
            await ctx.send("No culture items found.")
            return

        embed = discord.Embed(
            title="Baseball Culture / 野球文化",
            color=discord.Color.purple()
        )

        for item in items[:5]:
            embed.add_field(
                name=f"{{item.get('type')}}: {{item['title']}} ({{item.get('year', 'N/A')}})",
                value=item.get('description', 'N/A')[:200],
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name="evolution", aliases=["e"])
    async def get_evolution(self, ctx: commands.Context, ev_type: Optional[str] = None):
        """野球戦術・ルールの進化を表示"""
        evolutions = self.db.get_evolution_history(ev_type)

        if not evolutions:
            await ctx.send("No evolution data found.")
            return

        embed = discord.Embed(
            title="Baseball Evolution / 野球の進化",
            color=discord.Color.orange()
        )

        for evo in evolutions[:5]:
            embed.add_field(
                name=f"{{evo.get('type')}}: {{evo.get('era')}}",
                value=f"{{evo.get('description', 'N/A')}}\\nImpact: {{evo.get('impact', 'N/A')}}",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name="search", aliases=["find"])
    async def search_history(self, ctx: commands.Context, *, query: str):
        """歴史情報を検索"""
        # 各テーブルを検索
        results = []

        matches = self.db.get_historical_matches(limit=50)
        results.extend([m for m in matches if query.lower() in str(m).lower()])

        legends = self.db.get_legends()
        results.extend([l for l in legends if query.lower() in str(l).lower()])

        stadiums = self.db.get_stadiums()
        results.extend([s for s in stadiums if query.lower() in str(s).lower()])

        if not results:
            await ctx.send(f"No results found for: {{query}}")
            return

        embed = discord.Embed(
            title=f"Search Results: {{query}}",
            color=discord.Color.blue()
        )

        for result in results[:5]:
            result_type = result.get("teams", result.get("name", result.get("title", "Unknown")))
            embed.add_field(
                name=result_type[:50],
                value=str(result)[:200],
                inline=False
            )

        await ctx.send(embed=embed)

def main():
    import os

    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("DISCORD_TOKEN environment variable not set")
        return

    bot = {self._to_class_name(agent_info["name"])}Bot()
    bot.run(token)

if __name__ == "__main__":
    main()
'''

    def _generate_requirements_txt(self):
        return '''discord.py>=2.3.0
aiohttp>=3.9.0
python-dotenv>=1.0.0
'''

    def _generate_readme_md(self, agent_info):
        return f'''# {agent_info["name_ja"]} / {agent_info["name_en"]}

{agent_info["description_ja"]}

## 概要 / Overview

{agent_info["description_en"]}

## 機能 / Features

- 歴史データの分析
- 記録の検索と表示
- 伝承情報の管理
- Discord Bot インテグレーション

## インストール / Installation

```bash
pip install -r requirements.txt
```

## 使用方法 / Usage

### エージェントとして使用 / As Agent

```python
from agent import {self._to_class_name(agent_info["name"])}

agent = {self._to_class_name(agent_info["name"])}()
result = await agent.run("analyze historical matches")
```

### データベースとして使用 / As Database

```python
from db import {self._to_class_name(agent_info["name"])}Database

db = {self._to_class_name(agent_info["name"])}Database()
matches = db.get_historical_matches(limit=10)
```

### Discord Bot として使用 / As Discord Bot

```bash
export DISCORD_TOKEN=your_bot_token
python discord.py
```

## コマンド / Commands

- `!history match [limit]` - 歴史的名試合一覧 / Historical matches
- `!history legend [name]` - 伝説選手情報 / Legends info
- `!history stadium [name]` - 野球場情報 / Stadiums info
- `!history culture [type]` - 野球文化 / Baseball culture
- `!history evolution [type]` - 野球の進化 / Baseball evolution
- `!history search <query>` - 検索 / Search

## データベース構造 / Database Schema

### historical_matches
- id: プライマリキー
- match_date: 試合日
- teams: 対戦チーム
- score: スコア
- importance: 重要度
- description: 説明
- highlights: ハイライト（JSON）

### legends
- id: プライマリキー
- name: 選手名
- team: チーム
- era: 時代
- achievements: 実績（JSON）
- stats: 統計（JSON）
- bio: 経歴
- image_url: 画像URL

### stadiums
- id: プライマリキー
- name: 野球場名
- location: 場所
- year_opened: 開場年
- year_closed: 閉場年
- capacity: 収容人数
- features: 特徴（JSON）
- memorable_events: 記念イベント（JSON）

### culture
- id: プライマリキー
- type: タイプ
- title: タイトル
- year: 年
- description: 説明
- related_teams: 関連チーム（JSON）

### evolution
- id: プライマリキー
- type: タイプ
- era: 時代
- description: 説明
- impact: 影響

## ライセンス / License

MIT License

## 作者 / Author

OpenClaw Project
'''

    def _to_class_name(self, name: str) -> str:
        """エージェント名をクラス名に変換"""
        return "".join(word.capitalize() for word in name.replace("-", " ").split())

    def run(self):
        """オーケストレーターを実行"""
        progress = self.load_progress()

        for agent_info in self.agents:
            if agent_info["name"] in progress["completed"]:
                print(f"Skipping {agent_info['name']} (already completed)")
                continue

            print(f"Creating {agent_info['name']}...")
            agent_dir = self.create_agent(agent_info)
            print(f"Created {agent_dir}")

            progress["completed"].append(agent_info["name"])
            self.save_progress(progress)

        print(f"Orchestration complete! {len(progress['completed'])}/{len(self.agents)} agents created.")


if __name__ == "__main__":
    orchestrator = BaseballHistoryOrchestrator()
    orchestrator.run()
