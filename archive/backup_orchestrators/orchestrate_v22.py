#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
オーケストレーター V22 - 次期プロジェクト案 V22
自律的なエージェント作成システム
"""

import os
import json
from pathlib import Path

BASE_DIR = Path("/workspace")

# プロジェクト定義
PROJECTS = [
    {
        "name": "baseball-business-front-office",
        "display_name": "野球ビジネス・フロントオフィスエージェント",
        "agents": [
            {
                "name": "baseball-salary-cap-agent",
                "display_name": "野球サラリーキャップエージェント",
                "display_name_en": "Baseball Salary Cap Agent",
                "description": "チームのサラリーキャップ、契約管理、予算配分を分析・管理するエージェント",
                "description_en": "Agent for analyzing and managing team salary caps, contract management, and budget allocation"
            },
            {
                "name": "baseball-trade-analyzer-agent",
                "display_name": "野球トレード分析エージェント",
                "display_name_en": "Baseball Trade Analyzer Agent",
                "description": "トレード提案の分析、価値評価、影響予測を支援するエージェント",
                "description_en": "Agent for supporting trade proposal analysis, value assessment, and impact prediction"
            },
            {
                "name": "baseball-free-agency-agent",
                "display_name": "野球フリーエージェンシーエージェント",
                "display_name_en": "Baseball Free Agency Agent",
                "description": "FA選手の市場動向、契約交渉、チームマッチングを支援するエージェント",
                "description_en": "Agent for supporting FA player market trends, contract negotiations, and team matching"
            },
            {
                "name": "baseball-scouting-analytics-agent",
                "display_name": "野球スカウティング分析エージェント",
                "display_name_en": "Baseball Scouting Analytics Agent",
                "description": "アマチュア選手の評価、ドラフト戦略、スカウティングデータ分析を支援するエージェント",
                "description_en": "Agent for supporting amateur player evaluation, draft strategy, and scouting data analysis"
            },
            {
                "name": "baseball-revenue-optimizer-agent",
                "display_name": "野球収益最適化エージェント",
                "display_name_en": "Baseball Revenue Optimizer Agent",
                "description": "チケット販売、マーチャンダイジング、メディア権利収益の最適化を支援するエージェント",
                "description_en": "Agent for supporting ticket sales, merchandising, and media rights revenue optimization"
            }
        ]
    },
    {
        "name": "game-live-streaming-content",
        "display_name": "ゲームライブストリーミング・コンテンツエージェント",
        "agents": [
            {
                "name": "game-stream-analytics-agent",
                "display_name": "ゲーム配信分析エージェント",
                "display_name_en": "Game Stream Analytics Agent",
                "description": "ライブ配信の視聴者数、エンゲージメント、収益を分析するエージェント",
                "description_en": "Agent for analyzing live stream viewership, engagement, and revenue"
            },
            {
                "name": "game-stream-overlay-agent",
                "display_name": "ゲーム配信オーバーレイエージェント",
                "display_name_en": "Game Stream Overlay Agent",
                "description": "配信用オーバーレイ、アラート、インタラクティブ要素を管理するエージェント",
                "description_en": "Agent for managing streaming overlays, alerts, and interactive elements"
            },
            {
                "name": "game-stream-chat-agent",
                "display_name": "ゲーム配信チャットエージェント",
                "display_name_en": "Game Stream Chat Agent",
                "description": "配信チャットの管理、モデレーション、視聴者エンゲージメントを支援するエージェント",
                "description_en": "Agent for supporting stream chat management, moderation, and viewer engagement"
            },
            {
                "name": "game-stream-schedule-agent",
                "display_name": "ゲーム配信スケジュールエージェント",
                "display_name_en": "Game Stream Schedule Agent",
                "description": "配信スケジュールの管理、通知、タイミング最適化を支援するエージェント",
                "description_en": "Agent for supporting stream schedule management, notifications, and timing optimization"
            },
            {
                "name": "game-stream-collab-agent",
                "display_name": "ゲーム配信コラボエージェント",
                "display_name_en": "Game Stream Collaboration Agent",
                "description": "配信者間のコラボ企画、クロスプロモーションを支援するエージェント",
                "description_en": "Agent for supporting streamer collaboration projects and cross-promotion"
            }
        ]
    },
    {
        "name": "erotic-ai-creative",
        "display_name": "えっちコンテンツAIクリエイティブエージェント",
        "agents": [
            {
                "name": "erotic-ai-image-enhancer-agent",
                "display_name": "えっちAI画像強化エージェント",
                "display_name_en": "Erotic AI Image Enhancer Agent",
                "description": "えっち画像の画質向上、修復、強調をAIで支援するエージェント",
                "description_en": "Agent for supporting erotic image quality improvement, restoration, and enhancement using AI"
            },
            {
                "name": "erotic-ai-style-transfer-agent",
                "display_name": "えっちAIスタイル変換エージェント",
                "display_name_en": "Erotic AI Style Transfer Agent",
                "description": "えっち画像のアートスタイル変換、フィルタ適用を支援するエージェント",
                "description_en": "Agent for supporting erotic image art style transfer and filter application"
            },
            {
                "name": "erotic-ai-pose-editor-agent",
                "display_name": "えっちAIポーズ編集エージェント",
                "display_name_en": "Erotic AI Pose Editor Agent",
                "description": "キャラクターのポーズ、表情、角度の調整をAIで支援するエージェント",
                "description_en": "Agent for supporting character pose, expression, and angle adjustment using AI"
            },
            {
                "name": "erotic-ai-character-generator-agent",
                "display_name": "えっちAIキャラクター生成エージェント",
                "display_name_en": "Erotic AI Character Generator Agent",
                "description": "新しいえっちキャラクター、外観、特徴の生成をAIで支援するエージェント",
                "description_en": "Agent for supporting new erotic character, appearance, and feature generation using AI"
            },
            {
                "name": "erotic-ai-background-generator-agent",
                "display_name": "えっちAI背景生成エージェント",
                "display_name_en": "Erotic AI Background Generator Agent",
                "description": "えっちシーンの背景、環境、設定の生成をAIで支援するエージェント",
                "description_en": "Agent for supporting erotic scene background, environment, and setting generation using AI"
            }
        ]
    },
    {
        "name": "baseball-data-science-engineering",
        "display_name": "野球データサイエンス・エンジニアリングエージェント",
        "agents": [
            {
                "name": "baseball-data-pipeline-agent",
                "display_name": "野球データパイプラインエージェント",
                "display_name_en": "Baseball Data Pipeline Agent",
                "description": "野球データの収集、ETL、パイプライン管理を自動化するエージェント",
                "description_en": "Agent for automating baseball data collection, ETL, and pipeline management"
            },
            {
                "name": "baseball-data-warehouse-agent",
                "display_name": "野球データウェアハウスエージェント",
                "display_name_en": "Baseball Data Warehouse Agent",
                "description": "野球データのウェアハウス設計、管理、最適化を支援するエージェント",
                "description_en": "Agent for supporting baseball data warehouse design, management, and optimization"
            },
            {
                "name": "baseball-feature-engineering-agent",
                "display_name": "野球特徴量エンジニアリングエージェント",
                "display_name_en": "Baseball Feature Engineering Agent",
                "description": "野球分析用の特徴量抽出、変換、選択を支援するエージェント",
                "description_en": "Agent for supporting baseball analysis feature extraction, transformation, and selection"
            },
            {
                "name": "baseball-model-deployment-agent",
                "display_name": "野球モデルデプロイメントエージェント",
                "display_name_en": "Baseball Model Deployment Agent",
                "description": "MLモデルのデプロイ、モニタリング、再学習を管理するエージェント",
                "description_en": "Agent for managing ML model deployment, monitoring, and retraining"
            },
            {
                "name": "baseball-data-governance-agent",
                "display_name": "野球データガバナンスエージェント",
                "display_name_en": "Baseball Data Governance Agent",
                "description": "野球データの品質管理、ポリシー、コンプライアンスを管理するエージェント",
                "description_en": "Agent for managing baseball data quality management, policies, and compliance"
            }
        ]
    },
    {
        "name": "game-ai-npc-dialogue",
        "display_name": "ゲームAI・NPC・対話エージェント",
        "agents": [
            {
                "name": "game-ai-npc-behavior-agent",
                "display_name": "ゲームAI NPC行動エージェント",
                "display_name_en": "Game AI NPC Behavior Agent",
                "description": "NPCの行動AI、ルート設定、意思決定を管理するエージェント",
                "description_en": "Agent for managing NPC behavior AI, pathfinding, and decision making"
            },
            {
                "name": "game-ai-dialogue-system-agent",
                "display_name": "ゲームAI対話システムエージェント",
                "display_name_en": "Game AI Dialogue System Agent",
                "description": "対話システム、選択肢、ストーリー分岐を管理するエージェント",
                "description_en": "Agent for managing dialogue systems, choices, and story branching"
            },
            {
                "name": "game-ai-voice-synthesis-agent",
                "display_name": "ゲームAI音声合成エージェント",
                "display_name_en": "Game AI Voice Synthesis Agent",
                "description": "キャラクター音声の生成、感情表現、TTSを管理するエージェント",
                "description_en": "Agent for managing character voice generation, emotional expression, and TTS"
            },
            {
                "name": "game-ai-enemy-ai-agent",
                "display_name": "ゲームAI敵対AIエージェント",
                "display_name_en": "Game AI Enemy AI Agent",
                "description": "敵対AIの戦略、適応、難易度調整を管理するエージェント",
                "description_en": "Agent for managing enemy AI strategy, adaptation, and difficulty adjustment"
            },
            {
                "name": "game-ai-world-simulation-agent",
                "display_name": "ゲームAI世界シミュレーションエージェント",
                "display_name_en": "Game AI World Simulation Agent",
                "description": "ゲーム世界のシミュレーション、NPC間インタラクションを管理するエージェント",
                "description_en": "Agent for managing game world simulation and NPC interactions"
            }
        ]
    }
]

# テンプレート（変数を分離してf-stringエスケープ問題を回避）
AGENT_TEMPLATE = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{display_name_en}
{display_name}
"""

import asyncio
import logging
from typing import Optional, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger({name_str})


class {agent_class_name}:
    """{display_name_en}"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.state = {}
        logger.info(f"{display_name_str} initialized")

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return result."""
        logger.info(f"Processing: {display_name_str}")
        result = {"status": "success", "data": input_data}
        return result

    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data and return insights."""
        logger.info(f"Analyzing: {display_name_str}")
        insights = {"insights": []}
        return insights

    async def recommend(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide recommendations based on context."""
        logger.info(f"Recommending: {display_name_str}")
        recommendations = {"recommendations": []}
        return recommendations


async def main():
    """Main entry point."""
    agent = {agent_class_name}()
    result = await agent.process({{"test": "data"}})
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
'''

DB_TEMPLATE = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database for {display_name_en}
{display_name}
"""

import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

DB_PATH = Path(__file__).parent / "{name}.db"


class {db_class_name}:
    """Database handler for {display_name_en}"""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self._init_db()

    def _init_db(self):
        """Initialize database tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Main entries table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    type TEXT DEFAULT 'default',
                    status TEXT DEFAULT 'active',
                    priority INTEGER DEFAULT 0,
                    tags TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Tags table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Entry-tags mapping table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entry_tags (
                    entry_id INTEGER NOT NULL,
                    tag_id INTEGER NOT NULL,
                    PRIMARY KEY (entry_id, tag_id),
                    FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE,
                    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
                )
            """)

            # Activity log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT NOT NULL,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

    def add_entry(self, title: str, content: str, **kwargs) -> int:
        """Add a new entry."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO entries (title, content, type, status, priority, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                title, content,
                kwargs.get('type', 'default'),
                kwargs.get('status', 'active'),
                kwargs.get('priority', 0),
                kwargs.get('tags', ''),
                kwargs.get('metadata', '')
            ))
            conn.commit()
            self._log_activity('add_entry', f"Added entry: {title}")
            return cursor.lastrowid

    def get_entry(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """Get entry by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def list_entries(self, status: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """List entries with optional status filter."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if status:
                cursor.execute(
                    "SELECT * FROM entries WHERE status = ? ORDER BY updated_at DESC LIMIT ?",
                    (status, limit)
                )
            else:
                cursor.execute(
                    "SELECT * FROM entries ORDER BY updated_at DESC LIMIT ?",
                    (limit,)
                )
            return [dict(row) for row in cursor.fetchall()]

    def update_entry(self, entry_id: int, **kwargs) -> bool:
        """Update entry."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            fields = []
            values = []
            for key, value in kwargs.items():
                if key in ['title', 'content', 'type', 'status', 'priority', 'tags', 'metadata']:
                    fields.append(f"{key} = ?")
                    values.append(value)
            if not fields:
                return False
            values.append(entry_id)
            cursor.execute(f"""
                UPDATE entries SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, values)
            conn.commit()
            self._log_activity('update_entry', f"Updated entry: {entry_id}")
            return cursor.rowcount > 0

    def delete_entry(self, entry_id: int) -> bool:
        """Delete entry."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
            conn.commit()
            self._log_activity('delete_entry', f"Deleted entry: {entry_id}")
            return cursor.rowcount > 0

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            total_entries = cursor.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
            active_entries = cursor.execute("SELECT COUNT(*) FROM entries WHERE status = 'active'").fetchone()[0]
            total_tags = cursor.execute("SELECT COUNT(*) FROM tags").fetchone()[0]

            return {
                "total_entries": total_entries,
                "active_entries": active_entries,
                "total_tags": total_tags
            }

    def _log_activity(self, action: str, details: str = ""):
        """Log activity to database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO activity_log (action, details) VALUES (?, ?)",
                (action, details)
            )
            conn.commit()


if __name__ == "__main__":
    db = {db_class_name}()
    print(f"Database initialized: {display_name_str}")
    print(f"Stats: {db.get_stats()}")
'''

DISCORD_TEMPLATE = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord Integration for {display_name_en}
{display_name}
"""

import discord
from discord.ext import commands, tasks
import logging
from typing import Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger({name_str})


class {discord_class_name}(commands.Bot):
    """Discord bot for {display_name_en}"""

    def __init__(self, command_prefix: str = "!", intents: Optional[discord.Intents] = None):
        intents = intents or discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.started = False

    async def setup_hook(self):
        """Called when the bot is starting."""
        await self.add_commands()
        logger.info(f"{display_name_str} Discord bot ready")

    async def add_commands(self):
        """Add bot commands."""

        @self.command(name="status")
        async def status(ctx):
            """Show bot status."""
            embed = discord.Embed(
                title="{display_name_en} Status",
                color=discord.Color.blue()
            )
            embed.add_field(name="Status", value="✅ Online", inline=True)
            embed.add_field(name="Version", value="1.0.0", inline=True)
            await ctx.send(embed=embed)

        @self.command(name="help")
        async def help_cmd(ctx):
            """Show help message."""
            embed = discord.Embed(
                title="{display_name_en} - Help",
                description="{display_name}",
                color=discord.Color.green()
            )
            embed.add_field(name="Commands", value="`!status` - Show status\\n`!help` - Show this help", inline=False)
            await ctx.send(embed=embed)

    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f"{display_name_str} bot logged in as {self.user}")
        self.started = True

    async def on_message(self, message):
        """Called when a message is received."""
        if message.author == self.user:
            return
        await self.process_commands(message)

    async def send_notification(self, channel_id: int, content: str, **kwargs):
        """Send notification to a channel."""
        try:
            channel = self.get_channel(channel_id)
            if channel:
                await channel.send(content, **kwargs)
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")

    async def send_embed(self, channel_id: int, title: str, description: str, **kwargs):
        """Send an embed to a channel."""
        try:
            channel = self.get_channel(channel_id)
            if channel:
                embed = discord.Embed(title=title, description=description, **kwargs)
                await channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Failed to send embed: {e}")


async def run_bot(token: str):
    """Run the Discord bot."""
    bot = {discord_class_name}()
    await bot.start(token)


if __name__ == "__main__":
    import os
    token = os.getenv("DISCORD_TOKEN", "")
    if not token:
        logger.warning("DISCORD_TOKEN not set, running without Discord")
    else:
        import asyncio
        asyncio.run(run_bot(token))
'''

README_TEMPLATE = '''# {display_name_en}

{display_name}

## 概要 / Overview

{description}

## 機能 / Features

- データ収集 / Data collection
- 分析・解析 / Analysis
- レポート生成 / Report generation
- 通知機能 / Notification system

## インストール / Installation

```bash
pip install -r requirements.txt
```

## 使用方法 / Usage

### エージェントの実行 / Running the Agent

```bash
python agent.py
```

### データベースの初期化 / Database Initialization

```bash
python db.py
```

### Discordボットの起動 / Starting Discord Bot

```bash
DISCORD_TOKEN=your_token_here python discord.py
```

## 設定 / Configuration

環境変数を使用して設定をカスタマイズできます。

```bash
export DISCORD_TOKEN=your_bot_token
export LOG_LEVEL=INFO
```

## API / API Reference

### add_entry(title, content, **kwargs)

新しいエントリを追加します。

### get_entry(entry_id)

エントリIDでエントリを取得します。

### list_entries(status=None, limit=100)

エントリの一覧を取得します。

## ライセンス / License

MIT License
'''

REQUIREMENTS_TEMPLATE = '''# Requirements for {name}

discord.py>=2.3.0
aiohttp>=3.9.0
python-dotenv>=1.0.0
'''


def snake_to_camel(name: str) -> str:
    """Convert snake_case to CamelCase."""
    return ''.join(word.capitalize() for word in name.replace('-', '_').split('_'))


def create_agent_directory(agent_info: dict, project_name: str) -> bool:
    """Create all files for an agent."""
    agent_name = agent_info["name"]
    display_name = agent_info["display_name"]
    display_name_en = agent_info["display_name_en"]
    description = agent_info["description"]
    description_en = agent_info["description_en"]

    # Class names
    agent_class = snake_to_camel(agent_name)
    db_class = snake_to_camel(agent_name) + "DB"
    discord_class = snake_to_camel(agent_name) + "Discord"

    # Directory path
    dir_path = BASE_DIR / "agents" / agent_name
    dir_path.mkdir(parents=True, exist_ok=True)

    # String replacements for templates
    replacements = {
        "display_name_en": display_name_en,
        "display_name": display_name,
        "name": agent_name,
        "name_str": f'"{agent_name}"',
        "display_name_str": f'"{display_name}"',
        "description": description,
        "description_en": description_en,
        "agent_class_name": agent_class,
        "db_class_name": db_class,
        "discord_class_name": discord_class
    }

    def replace_in_template(template: str, repl: dict) -> str:
        """Replace placeholders in template."""
        result = template
        for key, value in repl.items():
            result = result.replace(f'{{{key}}}', str(value))
        return result

    # Create agent.py
    agent_content = replace_in_template(AGENT_TEMPLATE, replacements)
    (dir_path / "agent.py").write_text(agent_content, encoding="utf-8")

    # Create db.py
    db_content = replace_in_template(DB_TEMPLATE, replacements)
    (dir_path / "db.py").write_text(db_content, encoding="utf-8")

    # Create discord.py
    discord_content = replace_in_template(DISCORD_TEMPLATE, replacements)
    (dir_path / "discord.py").write_text(discord_content, encoding="utf-8")

    # Create README.md
    readme_content = replace_in_template(README_TEMPLATE, replacements)
    (dir_path / "README.md").write_text(readme_content, encoding="utf-8")

    # Create requirements.txt
    req_content = replace_in_template(REQUIREMENTS_TEMPLATE, {"name": agent_name})
    (dir_path / "requirements.txt").write_text(req_content, encoding="utf-8")

    print(f"✅ Created agent: {agent_name} - {display_name}")
    return True


def load_progress() -> dict:
    """Load progress from JSON file."""
    progress_file = BASE_DIR / "v22_progress.json"
    if progress_file.exists():
        return json.loads(progress_file.read_text(encoding="utf-8"))
    return {
        "started_at": None,
        "completed_projects": [],
        "completed_agents": [],
        "total_agents": sum(len(p["agents"]) for p in PROJECTS),
        "status": "not_started"
    }


def save_progress(progress: dict):
    """Save progress to JSON file."""
    progress_file = BASE_DIR / "v22_progress.json"
    progress_file.write_text(json.dumps(progress, indent=2, ensure_ascii=False), encoding="utf-8")


def run_orchestration():
    """Run the orchestration process."""
    print("=" * 60)
    print("オーケストレーター V22 - 次期プロジェクト案 V22")
    print("=" * 60)
    print()

    progress = load_progress()

    if progress["status"] == "completed":
        print("✅ プロジェクト V22 は既に完了しています")
        print(f"完了エージェント: {len(progress['completed_agents'])}/{progress['total_agents']}")
        return

    # Mark as started
    if progress["status"] == "not_started":
        from datetime import datetime
        progress["started_at"] = datetime.utcnow().isoformat()
        progress["status"] = "in_progress"
        save_progress(progress)

    print(f"進捗: {len(progress['completed_agents'])}/{progress['total_agents']} エージェント")
    print()

    # Create agents for each project
    for project in PROJECTS:
        project_name = project["name"]
        project_display = project["display_name"]

        if project_name in progress["completed_projects"]:
            print(f"⏭️  スキップ: {project_display} (既に完了)")
            continue

        print(f"📦 プロジェクト: {project_display}")
        print(f"   エージェント数: {len(project['agents'])}")
        print()

        for agent_info in project["agents"]:
            agent_name = agent_info["name"]

            if agent_name in progress["completed_agents"]:
                print(f"   ⏭️  スキップ: {agent_name}")
                continue

            try:
                success = create_agent_directory(agent_info, project_name)
                if success:
                    progress["completed_agents"].append(agent_name)
                    save_progress(progress)
                    print(f"   ✅ 完了: {agent_name} ({len(progress['completed_agents'])}/{progress['total_agents']})")
            except Exception as e:
                print(f"   ❌ エラー: {agent_name} - {e}")
                print(f"   Continuing...")

        # Mark project as completed
        if project_name not in progress["completed_projects"]:
            progress["completed_projects"].append(project_name)
            save_progress(progress)

        print()

    # Final status
    print("=" * 60)
    if len(progress["completed_agents"]) == progress["total_agents"]:
        progress["status"] = "completed"
        from datetime import datetime
        progress["completed_at"] = datetime.utcnow().isoformat()
        save_progress(progress)
        print("✅ プロジェクト V22 完了!")
        print(f"完了エージェント: {len(progress['completed_agents'])}/{progress['total_agents']}")
    else:
        print(f"⚠️  未完了のエージェントがあります: {progress['total_agents'] - len(progress['completed_agents'])}")
    print("=" * 60)


if __name__ == "__main__":
    run_orchestration()
