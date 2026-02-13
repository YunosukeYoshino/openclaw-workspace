#!/usr/bin/env python3
"""
野球歴史・伝承エージェントオーケストレーター
Baseball History & Legacy Agents Orchestrator

自律的に5個のエージェントを作成・管理するシステム
"""

import os
import json
from datetime import datetime

# エージェント定義
AGENTS = [
    {
        "name": "baseball-historical-match-agent",
        "name_ja": "野球歴史的名試合エージェント",
        "description": "歴史的な名試合、ドラマチックな展開の記録・分析エージェント",
        "description_en": "Historical match recording and analysis agent",
        "functions": [
            "historical_match_recording",
            "key_moment_analysis",
            "replay_suggestion",
            "video_audio_integration"
        ]
    },
    {
        "name": "baseball-legend-profile-agent",
        "name_ja": "野球伝説選手プロフィールエージェント",
        "description": "殿堂入り選手、レジェンド選手のプロフィール管理エージェント",
        "description_en": "Hall of Fame and legendary player profile management agent",
        "functions": [
            "legend_profile_management",
            "statistics_highlights",
            "episode_collection",
            "cross_generation_comparison"
        ]
    },
    {
        "name": "baseball-evolution-agent",
        "name_ja": "野球戦術・ルール進化エージェント",
        "description": "野球戦術の歴史的進化、ルール変更の影響分析エージェント",
        "description_en": "Baseball tactics evolution and rule change impact analysis agent",
        "functions": [
            "tactics_evolution_tracking",
            "rule_change_analysis",
            "era_style_comparison",
            "future_tactics_prediction"
        ]
    },
    {
        "name": "baseball-stadium-history-agent",
        "name_ja": "野球場歴史エージェント",
        "description": "歴史的野球場の建設、改名、移転などの歴史管理エージェント",
        "description_en": "Historical stadium history management agent",
        "functions": [
            "stadium_history_tracking",
            "feature_recording",
            "legendary_event_linking",
            "tour_suggestion"
        ]
    },
    {
        "name": "baseball-culture-agent",
        "name_ja": "野球文化エージェント",
        "description": "野球に関連する音楽、映画、文学、アートの収集エージェント",
        "description_en": "Baseball-related music, movies, literature, and art collection agent",
        "functions": [
            "culture_media_collection",
            "fan_tradition_recording",
            "social_impact_analysis",
            "culture_integration_analysis"
        ]
    }
]

# テンプレート定義（f-stringを回避）
FSTRING_LEFT_BRACE = "{{"
FSTRING_RIGHT_BRACE = "}}"
COLON = ":"

# エージェントテンプレート
AGENT_TEMPLATE = '''#!/usr/bin/env python3
\"\"\"
{agent_name_ja} / {agent_name}
{description}
\"\"\"

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

class {agent_class}:
    \"\"\"{agent_name_ja}クラス\"\"\"

    def __init__(self, db_path: str = "{agent_name}.db"):
        self.db_path = db_path
        self._init_database()

    def _init_database(self) -> None:
        \"\"\"データベース初期化\"\"\"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # matches テーブル
        cursor.execute(\"\"\"
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                home_team TEXT NOT NULL,
                away_team TEXT NOT NULL,
                score TEXT,
                description TEXT,
                key_moments TEXT,
                historical_significance INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        \"\"\")

        # legends テーブル
        cursor.execute(\"\"\"
            CREATE TABLE IF NOT EXISTS legends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                team TEXT,
                position TEXT,
                career_years TEXT,
                statistics TEXT,
                hall_of_fame INTEGER DEFAULT 0,
                highlights TEXT,
                episodes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        \"\"\")

        conn.commit()
        conn.close()

    def add_match(self, date: str, home_team: str, away_team: str,
                  score: str, description: str, key_moments: List[Dict],
                  historical_significance: int = 1) -> int:
        \"\"\"歴史的試合を追加\"\"\"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(\"\"\"
            INSERT INTO matches (date, home_team, away_team, score, description, key_moments, historical_significance)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        \"\"\", (date, home_team, away_team, score, description, json.dumps(key_moments), historical_significance))

        match_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return match_id

    def get_match(self, match_id: int) -> Optional[Dict[str, Any]]:
        \"\"\"試合情報を取得\"\"\"
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM matches WHERE id = ?", (match_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def get_historical_matches(self, limit: int = 50) -> List[Dict[str, Any]]:
        \"\"\"歴史的試合一覧を取得\"\"\"
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(\"\"\"
            SELECT * FROM matches
            WHERE historical_significance > 0
            ORDER BY historical_significance DESC, date DESC
            LIMIT ?
        \"\"\", (limit,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def add_legend(self, name: str, team: str, position: str,
                   career_years: str, statistics: Dict, hall_of_fame: bool = False,
                   highlights: List[str] = None, episodes: List[str] = None) -> int:
        \"\"\"伝説選手を追加\"\"\"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(\"\"\"
            INSERT INTO legends (name, team, position, career_years, statistics, hall_of_fame, highlights, episodes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        \"\"\", (name, team, position, career_years, json.dumps(statistics),
                1 if hall_of_fame else 0,
                json.dumps(highlights or []),
                json.dumps(episodes or [])))

        legend_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return legend_id

    def get_legend(self, legend_id: int) -> Optional[Dict[str, Any]]:
        \"\"\"伝説選手情報を取得\"\"\"
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM legends WHERE id = ?", (legend_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def get_hall_of_fame_legends(self) -> List[Dict[str, Any]]:
        \"\"\"殿堂入りの伝説選手一覧を取得\"\"\"
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM legends WHERE hall_of_fame = 1 ORDER BY name")
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def search_legends(self, query: str) -> List[Dict[str, Any]]:
        \"\"\"伝説選手を検索\"\"\"
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(\"\"\"
            SELECT * FROM legends
            WHERE name LIKE ? OR team LIKE ? OR position LIKE ?
            ORDER BY name
        \"\"\", (f"%{query}%", f"%{query}%", f"%{query}%"))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_statistics(self) -> Dict[str, Any]:
        \"\"\"統計情報を取得\"\"\"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM matches")
        match_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM legends")
        legend_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM legends WHERE hall_of_fame = 1")
        hof_count = cursor.fetchone()[0]

        conn.close()

        return {{
            "total_matches": match_count,
            "total_legends": legend_count,
            "hall_of_fame_count": hof_count
        }}

if __name__ == "__main__":
    agent = {agent_class}()
    print(f"{agent_name_ja}が初期化されました")
    print(agent.get_statistics())
'''

# DBテンプレート
DB_TEMPLATE = '''#!/usr/bin/env python3
\"\"\"
{agent_name_ja} データベースモジュール
{agent_name} Database Module
\"\"\"

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

class {agent_name}DB:
    \"\"\"{agent_name_ja} データベースクラス\"\"\"

    def __init__(self, db_path: str = "{agent_name}.db"):
        self.db_path = db_path
        self._init_database()

    def _init_database(self) -> None:
        \"\"\"データベース初期化\"\"\"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # matches テーブル
        cursor.execute(\"\"\"
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                home_team TEXT NOT NULL,
                away_team TEXT NOT NULL,
                score TEXT,
                description TEXT,
                key_moments TEXT,
                historical_significance INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        \"\"\")

        # legends テーブル
        cursor.execute(\"\"\"
            CREATE TABLE IF NOT EXISTS legends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                team TEXT,
                position TEXT,
                career_years TEXT,
                statistics TEXT,
                hall_of_fame INTEGER DEFAULT 0,
                highlights TEXT,
                episodes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        \"\"\")

        # evolution テーブル
        cursor.execute(\"\"\"
            CREATE TABLE IF NOT EXISTS evolution (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                era TEXT NOT NULL,
                tactic_type TEXT NOT NULL,
                description TEXT,
                rule_changes TEXT,
                impact_analysis TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        \"\"\")

        # stadiums テーブル
        cursor.execute(\"\"\"
            CREATE TABLE IF NOT EXISTS stadiums (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                location TEXT,
                opened_year INTEGER,
                capacity INTEGER,
                history TEXT,
                legendary_events TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        \"\"\")

        # culture テーブル
        cursor.execute(\"\"\"
            CREATE TABLE IF NOT EXISTS culture (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                title TEXT,
                description TEXT,
                baseball_relevance TEXT,
                year INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        \"\"\")

        conn.commit()
        conn.close()

    def add_match(self, data: Dict[str, Any]) -> int:
        \"\"\"歴史的試合を追加\"\"\"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(\"\"\"
            INSERT INTO matches (date, home_team, away_team, score, description, key_moments, historical_significance)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        \"\"\", (
            data.get("date"),
            data.get("home_team"),
            data.get("away_team"),
            data.get("score"),
            data.get("description"),
            json.dumps(data.get("key_moments", [])),
            data.get("historical_significance", 1)
        ))

        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return record_id

    def add_legend(self, data: Dict[str, Any]) -> int:
        \"\"\"伝説選手を追加\"\"\"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(\"\"\"
            INSERT INTO legends (name, team, position, career_years, statistics, hall_of_fame, highlights, episodes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        \"\"\", (
            data.get("name"),
            data.get("team"),
            data.get("position"),
            data.get("career_years"),
            json.dumps(data.get("statistics", {})),
            1 if data.get("hall_of_fame") else 0,
            json.dumps(data.get("highlights", [])),
            json.dumps(data.get("episodes", []))
        ))

        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return record_id

    def add_evolution(self, data: Dict[str, Any]) -> int:
        \"\"\"進化情報を追加\"\"\"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(\"\"\"
            INSERT INTO evolution (era, tactic_type, description, rule_changes, impact_analysis)
            VALUES (?, ?, ?, ?, ?)
        \"\"\", (
            data.get("era"),
            data.get("tactic_type"),
            data.get("description"),
            json.dumps(data.get("rule_changes", [])),
            json.dumps(data.get("impact_analysis", {}))
        ))

        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return record_id

    def add_stadium(self, data: Dict[str, Any]) -> int:
        \"\"\"球場情報を追加\"\"\"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(\"\"\"
            INSERT INTO stadiums (name, location, opened_year, capacity, history, legendary_events)
            VALUES (?, ?, ?, ?, ?, ?)
        \"\"\", (
            data.get("name"),
            data.get("location"),
            data.get("opened_year"),
            data.get("capacity"),
            data.get("history"),
            json.dumps(data.get("legendary_events", []))
        ))

        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return record_id

    def add_culture(self, data: Dict[str, Any]) -> int:
        \"\"\"文化情報を追加\"\"\"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(\"\"\"
            INSERT INTO culture (type, title, description, baseball_relevance, year)
            VALUES (?, ?, ?, ?, ?)
        \"\"\", (
            data.get("type"),
            data.get("title"),
            data.get("description"),
            data.get("baseball_relevance"),
            data.get("year")
        ))

        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return record_id

    def get_match(self, match_id: int) -> Optional[Dict[str, Any]]:
        \"\"\"試合情報を取得\"\"\"
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM matches WHERE id = ?", (match_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            data = dict(row)
            if data.get("key_moments"):
                data["key_moments"] = json.loads(data["key_moments"])
            return data
        return None

    def get_legend(self, legend_id: int) -> Optional[Dict[str, Any]]:
        \"\"\"伝説選手情報を取得\"\"\"
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM legends WHERE id = ?", (legend_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            data = dict(row)
            for field in ["statistics", "highlights", "episodes"]:
                if data.get(field):
                    data[field] = json.loads(data[field])
            return data
        return None

    def get_historical_matches(self, limit: int = 50) -> List[Dict[str, Any]]:
        \"\"\"歴史的試合一覧を取得\"\"\"
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(\"\"\"
            SELECT * FROM matches
            WHERE historical_significance > 0
            ORDER BY historical_significance DESC, date DESC
            LIMIT ?
        \"\"\", (limit,))

        rows = cursor.fetchall()
        conn.close()

        results = []
        for row in rows:
            data = dict(row)
            if data.get("key_moments"):
                data["key_moments"] = json.loads(data["key_moments"])
            results.append(data)
        return results

    def get_hall_of_fame_legends(self) -> List[Dict[str, Any]]:
        \"\"\"殿堂入りの伝説選手一覧を取得\"\"\"
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM legends WHERE hall_of_fame = 1 ORDER BY name")
        rows = cursor.fetchall()
        conn.close()

        results = []
        for row in rows:
            data = dict(row)
            for field in ["statistics", "highlights", "episodes"]:
                if data.get(field):
                    data[field] = json.loads(data[field])
            results.append(data)
        return results

    def search_legends(self, query: str) -> List[Dict[str, Any]]:
        \"\"\"伝説選手を検索\"\"\"
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(\"\"\"
            SELECT * FROM legends
            WHERE name LIKE ? OR team LIKE ? OR position LIKE ?
            ORDER BY name
        \"\"\", (f"%{query}%", f"%{query}%", f"%{query}%"))

        rows = cursor.fetchall()
        conn.close()

        results = []
        for row in rows:
            data = dict(row)
            for field in ["statistics", "highlights", "episodes"]:
                if data.get(field):
                    data[field] = json.loads(data[field])
            results.append(data)
        return results

    def get_statistics(self) -> Dict[str, Any]:
        \"\"\"統計情報を取得\"\"\"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {{}}

        cursor.execute("SELECT COUNT(*) FROM matches")
        stats["total_matches"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM legends")
        stats["total_legends"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM legends WHERE hall_of_fame = 1")
        stats["hall_of_fame_count"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM evolution")
        stats["total_evolution"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM stadiums")
        stats["total_stadiums"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM culture")
        stats["total_culture"] = cursor.fetchone()[0]

        conn.close()
        return stats
'''

# Discordテンプレート
DISCORD_TEMPLATE = '''#!/usr/bin/env python3
\"\"\"
{agent_name_ja} Discordボット
{agent_name} Discord Bot
\"\"\"

import discord
from discord.ext import commands
import sqlite3
import json
from typing import Dict, List, Any
from db import {agent_class}DB

# Bot設定
INTENTS = discord.Intents.default()
INTENTS.message_content = True
INTENTS.guilds = True

class {agent_class}Bot(commands.Bot):
    \"\"\"{agent_name_ja} Discordボットクラス\"\"\"

    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=INTENTS,
            help_command=None
        )
        self.db = {agent_class}DB()

    async def setup_hook(self):
        \"\"\"ボット初期化時の処理\"\"\"
        print(f"{agent_name_ja}ボットが準備完了")

    async def on_ready(self):
        \"\"\"ボット起動時の処理\"\"\"
        print(f"{agent_name_ja}ボットがログインしました")
        activity = discord.Activity(
            name="野球の歴史と伝説",
            type=discord.ActivityType.watching
        )
        await self.change_presence(activity=activity)

    async def on_command_error(self, ctx: commands.Context, error: Exception):
        \"\"\"コマンドエラー処理\"\"\"
        if isinstance(error, commands.CommandNotFound):
            return
        print(f"Error: {{error}}")
        await ctx.send(f"エラーが発生しました: {{error}}")

bot = {agent_class}Bot()

@bot.command(name="help")
async def help_command(ctx: commands.Context):
    \"\"\"ヘルプを表示\"\"\"
    embed = discord.Embed(
        title="{agent_name_ja} ヘルプ",
        description="野球の歴史と伝説に関するコマンド一覧",
        color=discord.Color.blue()
    )

    commands_list = [
        ("!match <ID>", "歴史的試合情報を表示"),
        ("!matches", "歴史的試合一覧を表示"),
        ("!legend <ID>", "伝説選手情報を表示"),
        ("!hof", "殿堂入りの選手一覧を表示"),
        ("!search <キーワード>", "伝説選手を検索"),
        ("!stats", "統計情報を表示"),
        ("!help", "このヘルプを表示")
    ]

    for cmd, desc in commands_list:
        embed.add_field(name=cmd, value=desc, inline=False)

    await ctx.send(embed=embed)

@bot.command(name="match")
async def match_command(ctx: commands.Context, match_id: int = None):
    \"\"\"歴史的試合情報を表示\"\"\"
    if match_id is None:
        await ctx.send("試合IDを指定してください: !match <ID>")
        return

    match = bot.db.get_match(match_id)
    if not match:
        await ctx.send(f"試合ID {{match_id}} が見つかりませんでした")
        return

    embed = discord.Embed(
        title=f"{{match['date']}} {{match['home_team']}} vs {{match['away_team']}}",
        description=match.get("description", ""),
        color=discord.Color.gold()
    )

    if match.get("score"):
        embed.add_field(name="スコア", value=match["score"], inline=False)

    if match.get("key_moments"):
        moments = match["key_moments"]
        moments_text = "\\n".join([f"• {{m}}" for m in moments[:5]])
        embed.add_field(name="重要場面", value=moments_text, inline=False)

    embed.add_field(
        name="歴史的意義",
        value="⭐" * match.get("historical_significance", 0),
        inline=False
    )

    await ctx.send(embed=embed)

@bot.command(name="matches")
async def matches_command(ctx: commands.Context, limit: int = 10):
    \"\"\"歴史的試合一覧を表示\"\"\"
    matches = bot.db.get_historical_matches(limit=limit)

    if not matches:
        await ctx.send("歴史的試合が見つかりませんでした")
        return

    embed = discord.Embed(
        title=f"歴史的試合一覧 (最新{{len(matches)}}件)",
        color=discord.Color.blue()
    )

    for match in matches:
        stars = "⭐" * match.get("historical_significance", 1)
        embed.add_field(
            name=f"ID: {{match['id']}} - {{match['date']}}",
            value=f"{{match['home_team']}} vs {{match['away_team']}} {{stars}}",
            inline=False
        )

    await ctx.send(embed=embed)

@bot.command(name="legend")
async def legend_command(ctx: commands.Context, legend_id: int = None):
    \"\"\"伝説選手情報を表示\"\"\"
    if legend_id is None:
        await ctx.send("選手IDを指定してください: !legend <ID>")
        return

    legend = bot.db.get_legend(legend_id)
    if not legend:
        await ctx.send(f"選手ID {{legend_id}} が見つかりませんでした")
        return

    embed = discord.Embed(
        title=f"{{legend['name']}}",
        color=discord.Color.purple()
    )

    if legend.get("team"):
        embed.add_field(name="チーム", value=legend["team"], inline=True)
    if legend.get("position"):
        embed.add_field(name="ポジション", value=legend["position"], inline=True)
    if legend.get("career_years"):
        embed.add_field(name="現役年", value=legend["career_years"], inline=True)

    if legend.get("hall_of_fame"):
        embed.add_field(name="殿堂入り", value="🏆 Yes", inline=True)

    if legend.get("highlights"):
        highlights = legend["highlights"][:3]
        highlights_text = "\\n".join([f"• {{h}}" for h in highlights])
        embed.add_field(name="ハイライト", value=highlights_text, inline=False)

    await ctx.send(embed=embed)

@bot.command(name="hof")
async def hof_command(ctx: commands.Context):
    \"\"\"殿堂入りの選手一覧を表示\"\"\"
    legends = bot.db.get_hall_of_fame_legends()

    if not legends:
        await ctx.send("殿堂入りの選手が見つかりませんでした")
        return

    embed = discord.Embed(
        title=f"殿堂入り選手一覧 ({{len(legends)}}人)",
        color=discord.Color.gold()
    )

    for legend in legends[:10]:
        team_info = f" ({{legend['team']}})" if legend.get("team") else ""
        embed.add_field(
            name=f"ID: {{legend['id']}} - {{legend['name']}}{team_info}",
            value=legend.get("position", ""),
            inline=True
        )

    await ctx.send(embed=embed)

@bot.command(name="search")
async def search_command(ctx: commands.Context, *, query: str):
    \"\"\"伝説選手を検索\"\"\"
    if not query:
        await ctx.send("検索キーワードを指定してください: !search <キーワード>")
        return

    legends = bot.db.search_legends(query)

    if not legends:
        await ctx.send(f"「{{query}}」に一致する選手が見つかりませんでした")
        return

    embed = discord.Embed(
        title=f"検索結果: {{query}} ({{len(legends)}}件)",
        color=discord.Color.green()
    )

    for legend in legends[:10]:
        hof_mark = "🏆" if legend.get("hall_of_fame") else ""
        embed.add_field(
            name=f"ID: {{legend['id']}} - {{legend['name']}} {hof_mark}",
            value=f"{{legend.get('team', '')}} / {{legend.get('position', '')}}",
            inline=False
        )

    await ctx.send(embed=embed)

@bot.command(name="stats")
async def stats_command(ctx: commands.Context):
    \"\"\"統計情報を表示\"\"\"
    stats = bot.db.get_statistics()

    embed = discord.Embed(
        title="📊 統計情報",
        color=discord.Color.blue()
    )

    embed.add_field(name="歴史的試合", value=stats.get("total_matches", 0), inline=True)
    embed.add_field(name="伝説選手", value=stats.get("total_legends", 0), inline=True)
    embed.add_field(name="殿堂入り", value=stats.get("hall_of_fame_count", 0), inline=True)
    embed.add_field(name="進化情報", value=stats.get("total_evolution", 0), inline=True)
    embed.add_field(name="球場情報", value=stats.get("total_stadiums", 0), inline=True)
    embed.add_field(name="文化情報", value=stats.get("total_culture", 0), inline=True)

    await ctx.send(embed=embed)

if __name__ == "__main__":
    import os

    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        print("環境変数 DISCORD_TOKEN が設定されていません")
        exit(1)

    bot.run(token)
'''

# READMEテンプレート
README_TEMPLATE = '''# {agent_name_ja} / {agent_name}

{description}

## 機能 / Features

- {functions_list_ja}

- {functions_list_en}

## インストール / Installation

```bash
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして実行 / Run as Agent

```bash
python agent.py
```

### Discordボットとして実行 / Run as Discord Bot

```bash
python discord.py
```

## Discordコマンド / Discord Commands

| コマンド / Command | 説明 / Description |
|---------------------|---------------------|
| `!match <ID>` | 歴史的試合情報を表示 / Show historical match info |
| `!matches` | 歴史的試合一覧を表示 / Show historical matches list |
| `!legend <ID>` | 伝説選手情報を表示 / Show legend player info |
| `!hof` | 殿堂入りの選手一覧を表示 / Show Hall of Fame players |
| `!search <キーワード>` | 伝説選手を検索 / Search legend players |
| `!stats` | 統計情報を表示 / Show statistics |
| `!help` | ヘルプを表示 / Show help |

## データベース / Database

SQLiteデータベースを使用して、以下の情報を管理します:

- **matches**: 歴史的試合情報
- ** legends**: 伝説選手プロフィール
- **evolution**: 戦術・ルール進化情報
- **stadiums**: 球場の歴史情報
- **culture**: 野球文化関連情報

## ライセンス / License

MIT License
'''

# Requirementsテンプレート
REQUIREMENTS_TEMPLATE = '''discord.py>=2.3.0
'''


def create_agent(agent_info: Dict[str, Any]) -> bool:
    \"\"\"エージェントを作成\"\"\"
    name = agent_info["name"]
    name_ja = agent_info["name_ja"]
    description = agent_info["description"]

    # クラス名生成
    class_name = name.replace("-", "_").replace(" ", "_").title()

    # エージェントディレクトリ作成
    agent_dir = f"agents/{name}"
    os.makedirs(agent_dir, exist_ok=True)

    # テンプレート変数準備
    template_vars = {{
        "agent_name": name,
        "agent_name_ja": name_ja,
        "agent_class": class_name,
        "description": description,
        "agent_name": name,
        "agent_name": name,
    }}

    # 関数リスト
    functions_list = agent_info.get("functions", [])
    functions_ja = "\\n- ".join(functions_list)
    functions_en = "\\n- ".join([f.replace("_", " ").title() for f in functions_list])

    # テンプレート生成
    agent_content = AGENT_TEMPLATE.format(**template_vars)
    agent_content = agent_content.replace("{{functions_list_ja}}", functions_ja)
    agent_content = agent_content.replace("{{functions_list_en}}", functions_en)

    # ファイル書き込み
    with open(f"{agent_dir}/agent.py", "w", encoding="utf-8") as f:
        f.write(agent_content)

    with open(f"{agent_dir}/db.py", "w", encoding="utf-8") as f:
        f.write(DB_TEMPLATE.format(**template_vars))

    with open(f"{agent_dir}/discord.py", "w", encoding="utf-8") as f:
        f.write(DISCORD_TEMPLATE.format(**template_vars))

    with open(f"{agent_dir}/README.md", "w", encoding="utf-8") as f:
        readme = README_TEMPLATE.format(**template_vars)
        readme = readme.replace("{{functions_list_ja}}", functions_ja)
        readme = readme.replace("{{functions_list_en}}", functions_en)
        f.write(readme)

    with open(f"{agent_dir}/requirements.txt", "w") as f:
        f.write(REQUIREMENTS_TEMPLATE)

    print(f"✓ {name_ja}を作成しました")
    return True


def update_progress(progress: Dict[str, Any]) -> None:
    \"\"\"進捗を更新\"\"\"
    with open("baseball_history_legacy_progress.json", "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def main():
    \"\"\"メイン処理\"\"\"
    print("=== 野球歴史・伝承エージェントオーケストレーター ===")
    print("=== Baseball History & Legacy Agents Orchestrator ===\\n")

    # 進捗ファイル読み込み
    progress_file = "baseball_history_legacy_progress.json"
    if os.path.exists(progress_file):
        with open(progress_file, "r", encoding="utf-8") as f:
            progress = json.load(f)
    else:
        progress = {{
            "started_at": datetime.now().isoformat(),
            "completed": [],
            "current_index": 0,
            "status": "in_progress"
        }}

    # エージェント作成
    for i, agent_info in enumerate(AGENTS):
        if i < progress.get("current_index", 0):
            continue

        if agent_info["name"] in progress.get("completed", []):
            continue

        print(f"\\n--- {i+1}/{len(AGENTS)}: {agent_info['name_ja']} ---")

        try:
            create_agent(agent_info)
            progress["completed"].append(agent_info["name"])
            progress["current_index"] = i + 1
            update_progress(progress)
        except Exception as e:
            print(f"✗ エラー: {e}")
            progress["status"] = "error"
            update_progress(progress)
            return

    # 完了
    progress["status"] = "completed"
    progress["completed_at"] = datetime.now().isoformat()
    update_progress(progress)

    print(f"\\n{'='*50}")
    print("✓ 全エージェントの作成が完了しました！")
    print(f"✓ All agents created successfully!")
    print(f"{'='*50}")
    print(f"\\n完了エージェント数: {{len(progress['completed'])}}/{len(AGENTS)}")
    print(f"Completed agents: {{len(progress['completed'])}}/{len(AGENTS)}")


if __name__ == "__main__":
    main()
'''

# 進捗管理ファイル初期化
def init_progress():
    progress = {
        "started_at": datetime.now().isoformat(),
        "completed": [],
        "current_index": 0,
        "status": "in_progress",
        "total_agents": len(AGENTS)
    }
    with open("baseball_history_legacy_progress.json", "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    init_progress()
    exec(ORCHESTRATOR_CODE)
