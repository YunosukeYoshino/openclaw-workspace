#!/usr/bin/env python3
"""
オーケストレーター V28 - 自律的エージェント作成システム
Next Project Plan V28
"""

import os
import json
from pathlib import Path

# ワークスペースの設定
WORKSPACE = Path("/workspace")
AGENTS_DIR = WORKSPACE / "agents"
PROGRESS_FILE = WORKSPACE / "v28_progress.json"

# プロジェクト設定
PROJECT_V28 = {
    "version": "V28",
    "total_projects": 5,
    "total_agents": 25,
    "projects": [
        {
            "name": "野球スカウティング・ドラフトエージェント / Baseball Scouting & Draft Agents",
            "agents": [
                {"id": "baseball-draft-prospect-agent", "name_ja": "野球ドラフト候補エージェント", "name_en": "Baseball Draft Prospect Agent", "desc_ja": "ドラフト候補選手の評価、レポート作成、順位予想を行うエージェント", "desc_en": "Evaluates draft prospects, creates reports, and predicts draft order", "category": "baseball"},
                {"id": "baseball-scout-travel-agent", "name_ja": "野球スカウト移動エージェント", "name_en": "Baseball Scout Travel Agent", "desc_ja": "スカウト移動スケジュール、試合視聴計画、候補選手追跡を管理するエージェント", "desc_en": "Manages scout travel schedules, game viewing plans, and prospect tracking", "category": "baseball"},
                {"id": "baseball-draft-simulator-agent", "name_ja": "野球ドラフトシミュレーターエージェント", "name_en": "Baseball Draft Simulator Agent", "desc_ja": "ドラフトシミュレーション、トレード分析、戦略的ドラフト提案を行うエージェント", "desc_en": "Simulates drafts, analyzes trades, and provides strategic draft recommendations", "category": "baseball"},
                {"id": "baseball-international-signing-agent", "name_ja": "野球国際契約エージェント", "name_en": "Baseball International Signing Agent", "desc_ja": "外国人選手の契約管理、国際スカウティング、規則適合チェックを行うエージェント", "desc_en": "Manages foreign player contracts, international scouting, and compliance checks", "category": "baseball"},
                {"id": "baseball-draft-history-agent", "name_ja": "野球ドラフト歴史エージェント", "name_en": "Baseball Draft History Agent", "desc_ja": "過去のドラフトデータ、選手追跡、ドラフト成功率分析を行うエージェント", "desc_en": "Tracks past draft data, player careers, and analyzes draft success rates", "category": "baseball"}
            ]
        },
        {
            "name": "ゲームeスポーツ配信・解説エージェント / Game Esports Broadcasting & Commentary Agents",
            "agents": [
                {"id": "esports-play-by-play-agent", "name_ja": "eスポーツ実況エージェント", "name_en": "Esports Play-by-Play Agent", "desc_ja": "リアルタイム実況生成、ハイライト検出、ストーリーテリングを行うエージェント", "desc_en": "Generates real-time commentary, detects highlights, and provides storytelling", "category": "game"},
                {"id": "esports-cast-planner-agent", "name_ja": "eスポーツ配信計画エージェント", "name_en": "Esports Cast Planner Agent", "desc_ja": "配信スケジュール、キャスト担当割り当て、機材管理を行うエージェント", "desc_en": "Manages broadcast schedules, caster assignments, and equipment management", "category": "game"},
                {"id": "esports-replay-analyzer-agent", "name_ja": "eスポーツリプレイ分析エージェント", "name_en": "Esports Replay Analyzer Agent", "desc_ja": "リプレイ分析、プレイ解説、戦術図作成を行うエージェント", "desc_en": "Analyzes replays, explains plays, and creates tactical diagrams", "category": "game"},
                {"id": "esports-viewer-engagement-agent", "name_ja": "eスポーツ視聴者エンゲージメントエージェント", "name_en": "Esports Viewer Engagement Agent", "desc_ja": "チャット分析、視聴者投票、リアクション追跡を行うエージェント", "desc_en": "Analyzes chats, manages viewer polls, and tracks reactions", "category": "game"},
                {"id": "esports-interview-agent", "name_ja": "eスポーツインタビューエージェント", "name_en": "Esports Interview Agent", "desc_ja": "選手インタビュー準備、質問生成、翻訳サポートを行うエージェント", "desc_en": "Prepares player interviews, generates questions, and provides translation support", "category": "game"}
            ]
        },
        {
            "name": "えっちコンテンツクリエイターサポート・マネタイズエージェント / Erotic Content Creator Support & Monetization Agents",
            "agents": [
                {"id": "erotic-monetization-agent", "name_ja": "えっちコンテンツマネタイズエージェント", "name_en": "Erotic Content Monetization Agent", "desc_ja": "収益管理、広告連携、ファンサイト運営を支援するエージェント", "desc_en": "Manages revenue, ad partnerships, and fan site operations", "category": "erotic"},
                {"id": "erotic-patreon-manager-agent", "name_ja": "えっちPatreon管理エージェント", "name_en": "Erotic Patreon Manager Agent", "desc_ja": "Patreon運営、報酬ティア管理、限定コンテンツ配信を行うエージェント", "desc_en": "Manages Patreon operations, reward tiers, and exclusive content distribution", "category": "erotic"},
                {"id": "erotic-commission-tracker-agent", "name_ja": "えっちコミッショントラッカーエージェント", "name_en": "Erotic Commission Tracker Agent", "desc_ja": "コミッション受注、進捗管理、支払い追跡を行うエージェント", "desc_en": "Tracks commission orders, manages progress, and handles payments", "category": "erotic"},
                {"id": "erotic-brand-collab-agent", "name_ja": "えっちブランドコラボエージェント", "name_en": "Erotic Brand Collaboration Agent", "desc_ja": "ブランドコラボ企画、スポンサーシップ管理、PRキャンペーンを行うエージェント", "desc_en": "Plans brand collaborations, manages sponsorships, and runs PR campaigns", "category": "erotic"},
                {"id": "erotic-content-marketplace-agent", "name_ja": "えっちコンテンツマーケットプレイスエージェント", "name_en": "Erotic Content Marketplace Agent", "desc_ja": "コンテンツ販売、ライセンス管理、販売分析を行うエージェント", "desc_en": "Manages content sales, licensing, and sales analytics", "category": "erotic"}
            ]
        },
        {
            "name": "システムデータパイプライン・ETLエージェント / System Data Pipeline & ETL Agents",
            "agents": [
                {"id": "data-ingestor-agent", "name_ja": "データインジェスターエージェント", "name_en": "Data Ingestor Agent", "desc_ja": "各種データソースからデータを収集・取り込むエージェント", "desc_en": "Collects and ingests data from various sources", "category": "system"},
                {"id": "data-transformer-agent", "name_ja": "データトランスフォーマーエージェント", "name_en": "Data Transformer Agent", "desc_ja": "データの変換・正規化・検証を行うエージェント", "desc_en": "Transforms, normalizes, and validates data", "category": "system"},
                {"id": "data-loader-agent", "name_ja": "データローダーエージェント", "name_en": "Data Loader Agent", "desc_ja": "変換済みデータをデータストアにロードするエージェント", "desc_en": "Loads transformed data into data stores", "category": "system"},
                {"id": "pipeline-orchestrator-agent", "name_ja": "パイプラインオーケストレーターエージェント", "name_en": "Pipeline Orchestrator Agent", "desc_ja": "データパイプラインの実行管理・スケジューリングを行うエージェント", "desc_en": "Manages and schedules data pipeline executions", "category": "system"},
                {"id": "data-quality-agent", "name_ja": "データ品質エージェント", "name_en": "Data Quality Agent", "desc_ja": "データ品質チェック、異常検知、自動修正を行うエージェント", "desc_en": "Checks data quality, detects anomalies, and performs automatic fixes", "category": "system"}
            ]
        },
        {
            "name": "AI強化学習・RLエージェント / AI Reinforcement Learning Agents",
            "agents": [
                {"id": "rl-training-agent", "name_ja": "強化学習トレーニングエージェント", "name_en": "RL Training Agent", "desc_ja": "RLモデルのトレーニング、ハイパーパラメータ最適化を行うエージェント", "desc_en": "Trains RL models and optimizes hyperparameters", "category": "ai"},
                {"id": "rl-environment-agent", "name_ja": "RL環境エージェント", "name_en": "RL Environment Agent", "desc_ja": "RLシミュレーション環境の構築・管理を行うエージェント", "desc_en": "Builds and manages RL simulation environments", "category": "ai"},
                {"id": "rl-policy-agent", "name_ja": "RLポリシーエージェント", "name_en": "RL Policy Agent", "desc_ja": "RLポリシーの評価・比較・最適化を行うエージェント", "desc_en": "Evaluates, compares, and optimizes RL policies", "category": "ai"},
                {"id": "rl-game-agent", "name_ja": "RLゲームエージェント", "name_en": "RL Game Agent", "desc_ja": "ゲームAI用RLモデルのトレーニング・デプロイを行うエージェント", "desc_en": "Trains and deploys RL models for game AI", "category": "ai"},
                {"id": "rl-baseball-strategy-agent", "name_ja": "RL野球戦略エージェント", "name_en": "RL Baseball Strategy Agent", "desc_ja": "野球戦略決定用RLモデルのトレーニング・応用を行うエージェント", "desc_en": "Trains and applies RL models for baseball strategy decisions", "category": "ai"}
            ]
        }
    ]
}


def snake_to_camel(snake_str: str) -> str:
    return ''.join(word.capitalize() for word in snake_str.split('-'))


def get_table_name(agent_id: str) -> str:
    return agent_id.replace('-', '_')


def get_command_group(agent_id: str) -> str:
    return agent_id.replace('-', '')


def create_agent_directory(agent_dir: Path, agent: dict) -> bool:
    class_name = snake_to_camel(agent["id"])
    table_name = get_table_name(agent["id"])
    command_group = get_command_group(agent["id"])

    agent_dir.mkdir(parents=True, exist_ok=True)

    # agent.py
    agent_py_content = '''#!/usr/bin/env python3
"""
''' + agent["id"] + ''' - ''' + agent["name_ja"] + ''' / ''' + agent["name_en"] + '''
''' + agent["desc_ja"] + '''
''' + agent["desc_en"] + '''
"""

import discord
from discord.ext import commands
from db import ''' + class_name + '''DB
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("''' + class_name + '''")

class ''' + class_name + '''(commands.Cog):
    """''' + agent["name_ja"] + ''' / ''' + agent["name_en"] + '''"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = ''' + class_name + '''DB()
        logger.info("''' + class_name + ''' initialized")

    @commands.group(name="''' + command_group + '''", invoke_without_command=True)
    async def ''' + command_group + '''(self, ctx: commands.Context):
        """''' + agent["name_ja"] + '''のメインコマンド / Main command for ''' + agent["name_en"] + '''"""
        embed = discord.Embed(
            title="''' + agent["name_ja"] + ''' / ''' + agent["name_en"] + '''",
            description="''' + agent["desc_ja"] + '''\\n\\n''' + agent["desc_en"] + '''",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Commands / コマンド",
            value="
`''' + command_group + ''' status` - ステータス確認
`''' + command_group + ''' add` - 追加
`''' + command_group + ''' list` - 一覧表示
`''' + command_group + ''' search` - 検索
`''' + command_group + ''' remove` - 削除
".strip(),
            inline=False
        )
        await ctx.send(embed=embed)

    @''' + command_group + '''.command(name="status")
    async def status(self, ctx: commands.Context):
        try:
            stats = self.db.get_stats()
            embed = discord.Embed(title="Status / ステータス", color=discord.Color.green())
            embed.add_field(name="Total Items", value=stats.get("total", 0), inline=True)
            embed.add_field(name="Active Items", value=stats.get("active", 0), inline=True)
            size_kb = stats.get("size", 0)
            embed.add_field(name="Database Size", value=str(round(size_kb, 2)) + " KB", inline=True)
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error("Error in status command: " + str(e))
            await ctx.send("Error retrieving status / ステータスの取得中にエラーが発生しました")

    @''' + command_group + '''.command(name="add")
    async def add_item(self, ctx: commands.Context, *, content: str):
        try:
            item_id = self.db.add_item(content, ctx.author.id)
            msg = "Added successfully (ID: " + str(item_id) + ") / 追加しました (ID: " + str(item_id) + ")"
            await ctx.send(msg)
        except Exception as e:
            logger.error("Error in add command: " + str(e))
            await ctx.send("Error adding item / アイテムの追加中にエラーが発生しました")

    @''' + command_group + '''.command(name="list")
    async def list_items(self, ctx: commands.Context, limit: int = 10):
        try:
            items = self.db.list_items(limit=limit)
            if not items:
                await ctx.send("No items found / アイテムが見つかりませんでした")
                return
            embed = discord.Embed(title="Items List / アイテム一覧", color=discord.Color.blue())
            for item in items[:25]:
                embed.add_field(name="ID: " + str(item['id']), value=item['content'][:100] + "...", inline=False)
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error("Error in list command: " + str(e))
            await ctx.send("Error listing items / アイテム一覧の取得中にエラーが発生しました")

    @''' + command_group + '''.command(name="search")
    async def search_items(self, ctx: commands.Context, *, query: str):
        try:
            items = self.db.search_items(query)
            if not items:
                msg = "No items found for '" + query + "' / '" + query + "' に一致するアイテムが見つかりませんでした"
                await ctx.send(msg)
                return
            embed = discord.Embed(title="Search Results: " + query + " / 検索結果: " + query, color=discord.Color.blue())
            for item in items[:25]:
                embed.add_field(name="ID: " + str(item['id']), value=item['content'][:100] + "...", inline=False)
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error("Error in search command: " + str(e))
            await ctx.send("Error searching items / アイテムの検索中にエラーが発生しました")

    @''' + command_group + '''.command(name="remove")
    async def remove_item(self, ctx: commands.Context, item_id: int):
        try:
            if self.db.remove_item(item_id):
                msg = "Item " + str(item_id) + " removed successfully / アイテム " + str(item_id) + " を削除しました"
                await ctx.send(msg)
            else:
                msg = "Item " + str(item_id) + " not found / アイテム " + str(item_id) + " が見つかりませんでした"
                await ctx.send(msg)
        except Exception as e:
            logger.error("Error in remove command: " + str(e))
            await ctx.send("Error removing item / アイテムの削除中にエラーが発生しました")

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(str(self.__class__.__name__) + " is ready")

async def setup(bot: commands.Bot):
    await bot.add_cog(''' + class_name + '''(bot))
'''
    (agent_dir / "agent.py").write_text(agent_py_content)

    # db.py
    db_py_content = '''#!/usr/bin/env python3
"""
Database module for ''' + agent["id"] + '''
''' + agent["name_ja"] + ''' / ''' + agent["name_en"] + '''
"""

import sqlite3
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path

class ''' + class_name + '''DB:
    """Database handler for ''' + agent["name_ja"] + '''"""

    def __init__(self, db_path: str = "data/''' + agent["id"] + '''.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ''' + table_name + ''' (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'active',
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""CREATE INDEX IF NOT EXISTS idx_status ON ''' + table_name + ''' (status)""")
            conn.execute("""CREATE INDEX IF NOT EXISTS idx_user_id ON ''' + table_name + ''' (user_id)""")
            conn.commit()

    def add_item(self, content: str, user_id: int, metadata: str = None) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("INSERT INTO ''' + table_name + ''' (content, user_id, metadata) VALUES (?, ?, ?)", (content, user_id, metadata))
            conn.commit()
            return cursor.lastrowid

    def get_item(self, item_id: int) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM ''' + table_name + ''' WHERE id = ?", (item_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def list_items(self, limit: int = 100, status: str = None) -> List[Dict[str, Any]]:
        query = "SELECT * FROM ''' + table_name + '''"
        params = []
        if status:
            query += " WHERE status = ?"
            params.append(status)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def search_items(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            pattern = "%" + query + "%"
            cursor = conn.execute("SELECT * FROM ''' + table_name + ''' WHERE content LIKE ? ORDER BY created_at DESC LIMIT ?", (pattern, limit))
            return [dict(row) for row in cursor.fetchall()]

    def update_item(self, item_id: int, content: str = None, status: str = None) -> bool:
        updates = []
        params = []
        if content:
            updates.append("content = ?")
            params.append(content)
        if status:
            updates.append("status = ?")
            params.append(status)
        if not updates:
            return False
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(item_id)
        query = "UPDATE ''' + table_name + ''' SET " + ", ".join(updates) + " WHERE id = ?"
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(query, params)
            conn.commit()
            return conn.total_changes > 0

    def remove_item(self, item_id: int) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM ''' + table_name + ''' WHERE id = ?", (item_id,))
            conn.commit()
            return conn.total_changes > 0

    def get_stats(self) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM ''' + table_name + '''").fetchone()[0]
            active = conn.execute("SELECT COUNT(*) FROM ''' + table_name + ''' WHERE status = 'active'").fetchone()[0]
            size = self.db_path.stat().st_size if self.db_path.exists() else 0
            return {"total": total, "active": active, "archived": total - active, "size": size / 1024}
'''
    (agent_dir / "db.py").write_text(db_py_content)

    # discord.py
    discord_py_content = '''#!/usr/bin/env python3
"""
Discord Bot for ''' + agent["id"] + '''
''' + agent["name_ja"] + ''' / ''' + agent["name_en"] + '''
"""

import discord
from discord.ext import commands
from agent import ''' + class_name + '''
import logging
from pathlib import Path
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("''' + agent["id"] + '''")

TOKEN = os.getenv("DISCORD_TOKEN", "YOUR_DISCORD_BOT_TOKEN")
INTENTS = discord.Intents.default()
INTENTS.message_content = True

bot = commands.Bot(command_prefix="!", intents=INTENTS, help_command=commands.DefaultHelpCommand())

@bot.event
async def on_ready():
    logger.info(str(bot.user.name) + " is ready!")
    logger.info("Bot ID: " + str(bot.user.id))
    logger.info("Connected to " + str(len(bot.guilds)) + " guilds")

@bot.event
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing required argument: " + str(error.param.name))
    else:
        logger.error("Command error: " + str(error))
        await ctx.send("An error occurred: " + str(error))

async def main():
    Path("data").mkdir(exist_ok=True)
    await bot.add_cog(''' + class_name + '''(bot))
    logger.info("Starting bot...")
    await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
'''
    (agent_dir / "discord.py").write_text(discord_py_content)

    # README.md
    readme_content = '''# ''' + agent["id"] + '''

''' + agent["name_ja"] + ''' / ''' + agent["name_en"] + '''

''' + agent["desc_ja"] + '''

''' + agent["desc_en"] + '''

## Features / 機能

- 追加: 新しいアイテムをデータベースに追加
- 表示: アイテム一覧の表示
- 検索: キーワードでアイテムを検索
- 削除: アイテムを削除
- ステータス: データベースの統計情報を表示

## Installation / インストール

\`\`\`bash
pip install -r requirements.txt
export DISCORD_TOKEN="your_discord_bot_token"
python discord.py
\`\`\`

## Requirements / 要件

- Python 3.8+
- discord.py 2.0+

## Commands / コマンド

| Command | Description | 説明 |
|---------|-------------|------|
| `!''' + command_group + '''` | Main menu | メインメニュー |
| `!''' + command_group + ''' status` | Show status | ステータス表示 |
| `!''' + command_group + ''' add <content>` | Add item | アイテム追加 |
| `!''' + command_group + ''' list [limit]` | List items | アイテム一覧 |
| `!''' + command_group + ''' search <query>` | Search items | アイテム検索 |
| `!''' + command_group + ''' remove <id>` | Remove item | アイテム削除 |

## Usage / 使用方法

\`\`\`
!''' + command_group + ''' add Example content
!''' + command_group + ''' list 10
!''' + command_group + ''' search keyword
!''' + command_group + ''' remove 1
\`\`\`

## Database / データベース

SQLite database. Data stored in `data/''' + agent["id"] + '''.db`.

## License / ライセンス

MIT License
'''
    (agent_dir / "README.md").write_text(readme_content)

    # requirements.txt
    (agent_dir / "requirements.txt").write_text("discord.py>=2.0.0\n")

    return True


def load_progress() -> dict:
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text())
    return {"completed": [], "current_project": None, "current_agent": None}


def save_progress(progress: dict):
    PROGRESS_FILE.write_text(json.dumps(progress, indent=2))


def orchestrate_v28():
    print("=== Orchestration V28 Starting ===")
    print("Total Projects: " + str(PROJECT_V28['total_projects']))
    print("Total Agents: " + str(PROJECT_V28['total_agents']))

    progress = load_progress()
    completed_agents = set(progress.get("completed", []))

    agents_created = 0
    agents_skipped = 0

    for project_idx, project in enumerate(PROJECT_V28["projects"], 1):
        print("\n--- Project " + str(project_idx) + "/" + str(PROJECT_V28['total_projects']) + ": " + project['name'] + " ---")

        for agent in project["agents"]:
            agent_dir = AGENTS_DIR / agent["id"]

            if agent["id"] in completed_agents and agent_dir.exists():
                print("  [SKIP] " + agent['id'] + " - Already exists")
                agents_skipped += 1
                continue

            try:
                if create_agent_directory(agent_dir, agent):
                    print("  [DONE] " + agent['id'] + " - " + agent['name_ja'])
                    completed_agents.add(agent["id"])
                    agents_created += 1
                    progress["completed"] = list(completed_agents)
                    save_progress(progress)

            except Exception as e:
                print("  [ERROR] " + agent['id'] + " - " + str(e))

    print("\n=== Orchestration V28 Complete ===")
    print("Agents Created: " + str(agents_created) + "/" + str(PROJECT_V28['total_agents']))
    print("Agents Skipped: " + str(agents_skipped))
    print("Total Agents: " + str(len(completed_agents)) + "/" + str(PROJECT_V28['total_agents']))

    if len(completed_agents) >= PROJECT_V28["total_agents"]:
        PROGRESS_FILE.unlink()
        print("Progress file cleaned up!")

    return len(completed_agents)


if __name__ == "__main__":
    result = orchestrate_v28()
    exit(0 if result >= PROJECT_V28["total_agents"] else 1)
