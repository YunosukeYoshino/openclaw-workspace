#!/usr/bin/env python3
"""
Orchestrator for Project V91 - Baseball Team Management & Game Design & Erotic Platform & Data Lake & Zero Trust
Total: 25 agents (5 per category)
"""

import os
import json
from pathlib import Path
from datetime import datetime

# Base paths
BASE_DIR = Path("/workspace")
AGENTS_DIR = BASE_DIR / "agents"

# V91 Agent Definitions
V91_AGENTS = {
    # 野球チームマネジメント・戦略エージェント (5個)
    "baseball-team-management-agent": {
        "description": "野球チームマネジメントエージェント。チーム全体の管理・運営・戦略。",
        "category": "baseball",
        "db_tables": {
            "teams": "(id INTEGER PRIMARY KEY, name TEXT, league TEXT, division TEXT, city TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)",
            "rosters": "(id INTEGER PRIMARY KEY, team_id INTEGER, player_id INTEGER, position TEXT, number INTEGER, FOREIGN KEY (team_id) REFERENCES teams(id))",
            "staff": "(id INTEGER PRIMARY KEY, team_id INTEGER, name TEXT, role TEXT, FOREIGN KEY (team_id) REFERENCES teams(id))",
            "contracts": "(id INTEGER PRIMARY KEY, team_id INTEGER, player_id INTEGER, salary INTEGER, years INTEGER, FOREIGN KEY (team_id) REFERENCES teams(id))",
        },
        "discord_commands": ["team_info", "roster", "staff", "contracts", "manage_team"],
    },
    "baseball-strategy-agent": {
        "description": "野球戦略エージェント。チーム戦略の立案・分析・最適化。",
        "category": "baseball",
        "db_tables": {
            "strategies": "(id INTEGER PRIMARY KEY, team_id INTEGER, type TEXT, description TEXT, effectiveness REAL, FOREIGN KEY (team_id) REFERENCES teams(id))",
            "lineups": "(id INTEGER PRIMARY KEY, team_id INTEGER, date TEXT, formation JSON, FOREIGN KEY (team_id) REFERENCES teams(id))",
            "gameplans": "(id INTEGER PRIMARY KEY, opponent_id TEXT, strategy TEXT, tactics TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)",
        },
        "discord_commands": ["create_strategy", "lineup", "gameplan", "analyze_strategy"],
    },
    "baseball-scouting-v2-agent": {
        "description": "野球スカウティングV2エージェント。選手スカウティングの高度な分析・評価。",
        "category": "baseball",
        "db_tables": {
            "scouts": "(id INTEGER PRIMARY KEY, agent_id INTEGER, player_id INTEGER, rating INTEGER, notes TEXT, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)",
            "draft_targets": "(id INTEGER PRIMARY KEY, player_id INTEGER, priority INTEGER, position TEXT, estimated_pick INTEGER)",
            "combine_data": "(id INTEGER PRIMARY KEY, player_id INTEGER, run_time REAL, throw_speed REAL, bat_speed REAL, FOREIGN KEY (player_id) REFERENCES players(id))",
        },
        "discord_commands": ["scout_player", "draft_targets", "combine_data", "evaluate_player"],
    },
    "baseball-farm-system-agent": {
        "description": "野球ファームシステムエージェント。マイナーリーグ・育成選手の管理。",
        "category": "baseball",
        "db_tables": {
            "farm_teams": "(id INTEGER PRIMARY KEY, name TEXT, level TEXT, parent_team_id INTEGER)",
            "farm_players": "(id INTEGER PRIMARY KEY, player_id INTEGER, team_id INTEGER, stats JSON, progress TEXT, FOREIGN KEY (team_id) REFERENCES farm_teams(id))",
            "development_plans": "(id INTEGER PRIMARY KEY, player_id INTEGER, goals TEXT, milestones JSON, status TEXT)",
        },
        "discord_commands": ["farm_teams", "farm_players", "development_plan", "track_progress"],
    },
    "baseball-schedule-optimizer-agent": {
        "description": "野球スケジュール最適化エージェント。試合スケジュールの最適化・調整。",
        "category": "baseball",
        "db_tables": {
            "schedules": "(id INTEGER PRIMARY KEY, team_id INTEGER, opponent TEXT, date TEXT, venue TEXT, time TEXT)",
            "travel_plans": "(id INTEGER PRIMARY KEY, team_id INTEGER, from_city TEXT, to_city TEXT, travel_time REAL, mode TEXT)",
            "rest_days": "(id INTEGER PRIMARY KEY, team_id INTEGER, date TEXT, type TEXT, notes TEXT)",
        },
        "discord_commands": ["schedule", "travel_plan", "rest_days", "optimize_schedule"],
    },

    # ゲームデザイン・クリエイティブツールエージェント (5個)
    "game-design-agent": {
        "description": "ゲームデザインエージェント。ゲームのデザイン・コンセプト・メカニクスの管理。",
        "category": "game",
        "db_tables": {
            "game_designs": "(id INTEGER PRIMARY KEY, title TEXT, genre TEXT, concept TEXT, mechanics TEXT)",
            "prototypes": "(id INTEGER PRIMARY KEY, design_id INTEGER, version TEXT, notes TEXT, status TEXT, FOREIGN KEY (design_id) REFERENCES game_designs(id))",
            "design_elements": "(id INTEGER PRIMARY KEY, design_id INTEGER, type TEXT, description TEXT, priority INTEGER, FOREIGN KEY (design_id) REFERENCES game_designs(id))",
        },
        "discord_commands": ["create_design", "add_element", "prototype", "mechanics"],
    },
    "game-art-director-agent": {
        "description": "ゲームアートディレクターエージェント。ゲームアート・ビジュアルスタイルの管理。",
        "category": "game",
        "db_tables": {
            "art_styles": "(id INTEGER PRIMARY KEY, project_id INTEGER, style TEXT, palette JSON, references TEXT, FOREIGN KEY (project_id) REFERENCES projects(id))",
            "assets": "(id INTEGER PRIMARY KEY, project_id INTEGER, type TEXT, name TEXT, path TEXT, status TEXT)",
            "reviews": "(id INTEGER PRIMARY KEY, asset_id INTEGER, reviewer TEXT, rating INTEGER, feedback TEXT, FOREIGN KEY (asset_id) REFERENCES assets(id))",
        },
        "discord_commands": ["art_style", "add_asset", "review_art", "visual_guide"],
    },
    "game-audio-engineer-agent": {
        "description": "ゲームオーディオエンジニアエージェント。ゲームBGM・SE・音声の制作・管理。",
        "category": "game",
        "db_tables": {
            "audio_tracks": "(id INTEGER PRIMARY KEY, project_id INTEGER, type TEXT, name TEXT, path TEXT, duration REAL, FOREIGN KEY (project_id) REFERENCES projects(id))",
            "sound_effects": "(id INTEGER PRIMARY KEY, project_id INTEGER, name TEXT, trigger TEXT, path TEXT, FOREIGN KEY (project_id) REFERENCES projects(id))",
            "voice_overs": "(id INTEGER PRIMARY KEY, project_id INTEGER, character TEXT, text TEXT, path TEXT, language TEXT)",
        },
        "discord_commands": ["add_music", "add_sfx", "voice_over", "audio_library"],
    },
    "game-level-designer-agent": {
        "description": "ゲームレベルデザイナーエージェント。ゲームレベル・ステージのデザイン・管理。",
        "category": "game",
        "db_tables": {
            "levels": "(id INTEGER PRIMARY KEY, project_id INTEGER, name TEXT, difficulty INTEGER, length REAL, FOREIGN KEY (project_id) REFERENCES projects(id))",
            "level_objects": "(id INTEGER PRIMARY KEY, level_id INTEGER, type TEXT, position JSON, properties JSON, FOREIGN KEY (level_id) REFERENCES levels(id))",
            "level_flows": "(id INTEGER PRIMARY KEY, level_id INTEGER, sequence JSON, pacing TEXT, FOREIGN KEY (level_id) REFERENCES levels(id))",
        },
        "discord_commands": ["create_level", "add_object", "level_flow", "playtest"],
    },
    "game-asset-manager-agent": {
        "description": "ゲームアセットマネージャーエージェント。ゲームアセットの整理・管理・バージョン管理。",
        "category": "game",
        "db_tables": {
            "assets": "(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT, version INTEGER, project_id INTEGER)",
            "tags": "(id INTEGER PRIMARY KEY, asset_id INTEGER, tag TEXT, FOREIGN KEY (asset_id) REFERENCES assets(id))",
            "dependencies": "(id INTEGER PRIMARY KEY, asset_id INTEGER, depends_on INTEGER, FOREIGN KEY (asset_id) REFERENCES assets(id), FOREIGN KEY (depends_on) REFERENCES assets(id))",
        },
        "discord_commands": ["add_asset", "find_asset", "asset_tags", "check_dependencies"],
    },

    # えっちコンテンツプラットフォームエージェント (5個)
    "erotic-platform-core-agent": {
        "description": "えっちプラットフォームコアエージェント。えっちコンテンツプラットフォームの中核機能。",
        "category": "erotic",
        "db_tables": {
            "platform_config": "(id INTEGER PRIMARY KEY, key TEXT, value TEXT, description TEXT)",
            "features": "(id INTEGER PRIMARY KEY, name TEXT, status TEXT, priority INTEGER, description TEXT)",
            "integrations": "(id INTEGER PRIMARY KEY, service TEXT, config JSON, status TEXT)",
        },
        "discord_commands": ["platform_status", "config", "features", "integrations"],
    },
    "erotic-content-pipeline-agent": {
        "description": "えっちコンテンツパイプラインエージェント。コンテンツ制作〜配信のパイプライン管理。",
        "category": "erotic",
        "db_tables": {
            "content_pipelines": "(id INTEGER PRIMARY KEY, name TEXT, stages JSON, status TEXT, config JSON)",
            "pipeline_runs": "(id INTEGER PRIMARY KEY, pipeline_id INTEGER, start_time TIMESTAMP, end_time TIMESTAMP, status TEXT, output TEXT, FOREIGN KEY (pipeline_id) REFERENCES content_pipelines(id))",
            "stage_logs": "(id INTEGER PRIMARY KEY, run_id INTEGER, stage TEXT, status TEXT, log TEXT, FOREIGN KEY (run_id) REFERENCES pipeline_runs(id))",
        },
        "discord_commands": ["create_pipeline", "run_pipeline", "pipeline_status", "pipeline_logs"],
    },
    "erotic-distribution-agent": {
        "description": "えっちコンテンツ配信エージェント。コンテンツの多チャネル配信・管理。",
        "category": "erotic",
        "db_tables": {
            "channels": "(id INTEGER PRIMARY KEY, name TEXT, type TEXT, config JSON, status TEXT)",
            "distributions": "(id INTEGER PRIMARY KEY, content_id INTEGER, channel_id INTEGER, status TEXT, publish_time TIMESTAMP, FOREIGN KEY (channel_id) REFERENCES channels(id))",
            "schedules": "(id INTEGER PRIMARY KEY, content_id INTEGER, channel_id INTEGER, scheduled_time TIMESTAMP, status TEXT)",
        },
        "discord_commands": ["add_channel", "distribute", "schedule_publish", "distribution_status"],
    },
    "erotic-subscription-agent": {
        "description": "えっちサブスクリプションエージェント。サブスクリプション・会員プランの管理。",
        "category": "erotic",
        "db_tables": {
            "plans": "(id INTEGER PRIMARY KEY, name TEXT, price INTEGER, currency TEXT, duration_days INTEGER, features JSON)",
            "subscriptions": "(id INTEGER PRIMARY KEY, user_id INTEGER, plan_id INTEGER, start_date TIMESTAMP, end_date TIMESTAMP, status TEXT, FOREIGN KEY (plan_id) REFERENCES plans(id))",
            "payments": "(id INTEGER PRIMARY KEY, subscription_id INTEGER, amount INTEGER, status TEXT, method TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (subscription_id) REFERENCES subscriptions(id))",
        },
        "discord_commands": ["plans", "subscribe", "subscription_status", "cancel_subscription"],
    },
    "erotic-analytics-platform-agent": {
        "description": "えっちアナリティクスプラットフォームエージェント。プラットフォーム全体の分析・レポート。",
        "category": "erotic",
        "db_tables": {
            "metrics": "(id INTEGER PRIMARY KEY, name TEXT, value REAL, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)",
            "events": "(id INTEGER PRIMARY KEY, user_id INTEGER, event_type TEXT, properties JSON, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)",
            "reports": "(id INTEGER PRIMARY KEY, name TEXT, type TEXT, config JSON, generated_at TIMESTAMP)",
        },
        "discord_commands": ["metrics", "events", "create_report", "dashboard"],
    },

    # データレイク・ウェアハウスエージェント (5個)
    "data-lake-agent": {
        "description": "データレイクエージェント。データレイクの管理・運用。",
        "category": "data",
        "db_tables": {
            "datasets": "(id INTEGER PRIMARY KEY, name TEXT, format TEXT, size_bytes INTEGER, path TEXT, ingested_at TIMESTAMP)",
            "partitions": "(id INTEGER PRIMARY KEY, dataset_id INTEGER, partition_key TEXT, value TEXT, path TEXT, FOREIGN KEY (dataset_id) REFERENCES datasets(id))",
            "schemas": "(id INTEGER PRIMARY KEY, dataset_id INTEGER, schema JSON, version INTEGER, FOREIGN KEY (dataset_id) REFERENCES datasets(id))",
        },
        "discord_commands": ["ingest", "list_datasets", "dataset_info", "query_lake"],
    },
    "data-warehouse-agent": {
        "description": "データウェアハウスエージェント。データウェアハウスの管理・クエリ。",
        "category": "data",
        "db_tables": {
            "fact_tables": "(id INTEGER PRIMARY KEY, name TEXT, grain TEXT, source TEXT, rows INTEGER)",
            "dimensions": "(id INTEGER PRIMARY KEY, name TEXT, key_columns TEXT, attributes JSON)",
            "etl_jobs": "(id INTEGER PRIMARY KEY, name TEXT, source TEXT, target TEXT, status TEXT, last_run TIMESTAMP, next_run TIMESTAMP)",
        },
        "discord_commands": ["create_fact", "add_dimension", "run_etl", "warehouse_status"],
    },
    "etl-pipeline-agent": {
        "description": "ETLパイプラインエージェント。ETLパイプラインの設計・実行・管理。",
        "category": "data",
        "db_tables": {
            "pipelines": "(id INTEGER PRIMARY KEY, name TEXT, description TEXT, stages JSON, config JSON)",
            "pipeline_runs": "(id INTEGER PRIMARY KEY, pipeline_id INTEGER, start_time TIMESTAMP, end_time TIMESTAMP, status TEXT, rows_processed INTEGER, FOREIGN KEY (pipeline_id) REFERENCES pipelines(id))",
            "stage_runs": "(id INTEGER PRIMARY KEY, run_id INTEGER, stage_name TEXT, start_time TIMESTAMP, end_time TIMESTAMP, status TEXT, error_message TEXT, FOREIGN KEY (run_id) REFERENCES pipeline_runs(id))",
        },
        "discord_commands": ["create_pipeline", "run_pipeline", "pipeline_history", "stage_logs"],
    },
    "data-quality-agent": {
        "description": "データ品質エージェント。データ品質のチェック・監視・改善。",
        "category": "data",
        "db_tables": {
            "rules": "(id INTEGER PRIMARY KEY, name TEXT, type TEXT, config JSON, enabled INTEGER)",
            "checks": "(id INTEGER PRIMARY KEY, rule_id INTEGER, dataset_id INTEGER, passed INTEGER, failed INTEGER, checked_at TIMESTAMP, FOREIGN KEY (rule_id) REFERENCES rules(id))",
            "issues": "(id INTEGER PRIMARY KEY, check_id INTEGER, row_id INTEGER, column TEXT, description TEXT, FOREIGN KEY (check_id) REFERENCES checks(id))",
        },
        "discord_commands": ["add_rule", "run_checks", "quality_report", "fix_issues"],
    },
    "data-lakehouse-agent": {
        "description": "データレイクハウスエージェント。データレイクハウスアーキテクチャの管理。",
        "category": "data",
        "db_tables": {
            "tables": "(id INTEGER PRIMARY KEY, name TEXT, format TEXT, location TEXT, properties JSON)",
            "zones": "(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT, description TEXT)",
            "table_lineage": "(id INTEGER PRIMARY KEY, source_table INTEGER, target_table INTEGER, transformation TEXT, FOREIGN KEY (source_table) REFERENCES tables(id), FOREIGN KEY (target_table) REFERENCES tables(id))",
        },
        "discord_commands": ["create_table", "zones", "table_lineage", "query_lakehouse"],
    },

    # ゼロトラスト・セキュリティエージェント (5個)
    "zero-trust-agent": {
        "description": "ゼロトラストエージェント。ゼロトラストアーキテクチャの実装・管理。",
        "category": "security",
        "db_tables": {
            "trust_levels": "(id INTEGER PRIMARY KEY, name TEXT, description TEXT, requirements JSON)",
            "policies": "(id INTEGER PRIMARY KEY, name TEXT, resource TEXT, conditions JSON, action TEXT)",
            "trust_scores": "(id INTEGER PRIMARY KEY, entity_id INTEGER, entity_type TEXT, score REAL, factors JSON, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)",
        },
        "discord_commands": ["trust_level", "add_policy", "trust_score", "evaluate_access"],
    },
    "continuous-auth-agent": {
        "description": "継続認証エージェント。継続的な認証・再認証の管理。",
        "category": "security",
        "db_tables": {
            "sessions": "(id INTEGER PRIMARY KEY, user_id INTEGER, token TEXT, created_at TIMESTAMP, last_activity TIMESTAMP, trust_level INTEGER)",
            "auth_events": "(id INTEGER PRIMARY KEY, session_id INTEGER, event_type TEXT, success INTEGER, details JSON, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (session_id) REFERENCES sessions(id))",
            "reauth_triggers": "(id INTEGER PRIMARY KEY, name TEXT, condition JSON, action TEXT)",
        },
        "discord_commands": ["session_status", "auth_history", "set_trigger", "force_reauth"],
    },
    "device-trust-agent": {
        "description": "デバイストラストエージェント。デバイスの信頼性評価・管理。",
        "category": "security",
        "db_tables": {
            "devices": "(id INTEGER PRIMARY KEY, device_id TEXT, user_id INTEGER, os TEXT, browser TEXT, last_seen TIMESTAMP, trust_score REAL)",
            "device_checks": "(id INTEGER PRIMARY KEY, device_id TEXT, check_type TEXT, result INTEGER, details JSON, checked_at TIMESTAMP, FOREIGN KEY (device_id) REFERENCES devices(device_id))",
            "quarantined_devices": "(id INTEGER PRIMARY KEY, device_id TEXT, reason TEXT, quarantined_at TIMESTAMP)",
        },
        "discord_commands": ["device_status", "device_checks", "quarantine_device", "approve_device"],
    },
    "identity-protection-agent": {
        "description": "ID保護エージェント。ユーザーIDの保護・監視・警告。",
        "category": "security",
        "db_tables": {
            "identities": "(id INTEGER PRIMARY KEY, user_id INTEGER, type TEXT, value TEXT, verified INTEGER, protected INTEGER)",
            "breach_checks": "(id INTEGER PRIMARY KEY, identity_id INTEGER, source TEXT, found INTEGER, details JSON, checked_at TIMESTAMP, FOREIGN KEY (identity_id) REFERENCES identities(id))",
            "alerts": "(id INTEGER PRIMARY KEY, identity_id INTEGER, type TEXT, severity TEXT, message TEXT, acknowledged INTEGER, created_at TIMESTAMP, FOREIGN KEY (identity_id) REFERENCES identities(id))",
        },
        "discord_commands": ["protected_ids", "check_breach", "alerts", "acknowledge_alert"],
    },
    "privilege-access-agent": {
        "description": "特権アクセスエージェント。特権アクセスの管理・監査・承認。",
        "category": "security",
        "db_tables": {
            "privileges": "(id INTEGER PRIMARY KEY, name TEXT, description TEXT, level INTEGER, approval_required INTEGER)",
            "assignments": "(id INTEGER PRIMARY KEY, user_id INTEGER, privilege_id INTEGER, granted_by INTEGER, granted_at TIMESTAMP, expires_at TIMESTAMP, FOREIGN KEY (privilege_id) REFERENCES privileges(id))",
            "requests": "(id INTEGER PRIMARY KEY, user_id INTEGER, privilege_id INTEGER, reason TEXT, status TEXT, requested_at TIMESTAMP, approved_by INTEGER, FOREIGN KEY (privilege_id) REFERENCES privileges(id))",
        },
        "discord_commands": ["privileges", "request_access", "approve_request", "audit_log"],
    },
}

# Template functions
def generate_agent_py(agent_name, agent_info):
    """Generate agent.py content"""
    category = agent_info["category"]
    commands = agent_info.get("discord_commands", [])
    commands_str = ', '.join(f'"{cmd}"' for cmd in commands)

    return f'''#!/usr/bin/env python3
"""
{agent_name} - {agent_info["description"]}
"""

import json
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class {agent_name.replace("-", "_").title().replace("_", "")}:
    """{agent_info["description"]}"""

    def __init__(self, db_path=None):
        """Initialize the agent"""
        from .db import {agent_name.replace("-", "_").replace("-", "")}Database

        self.db_path = db_path or Path(f"/workspace/agents/{agent_name}/data.db")
        self.db = {agent_name.replace("-", "_").replace("-", "")}Database(self.db_path)
        self.commands = [{commands_str}]

    async def process_message(self, message: str, user_id: str = None):
        """Process incoming message"""
        logger.info(f"Processing message: {{message[:50]}}...")

        # Parse command
        parts = message.strip().split()
        if not parts:
            return {{"error": "No command provided"}}

        cmd = parts[0].lower()
        args = parts[1:]

        try:
            if cmd in self.commands:
                return await self.handle_command(cmd, args, user_id)
            else:
                return {{"error": f"Unknown command: {{cmd}}", "available_commands": self.commands}}
        except Exception as e:
            logger.error(f"Error processing message: {{e}}")
            return {{"error": str(e)}}

    async def handle_command(self, cmd: str, args: list, user_id: str = None):
        """Handle specific command"""
        logger.info(f"Handling command: {{cmd}} with args: {{args}}")

        if cmd == "{commands[0]}" and len(commands) > 0:
            return await self.{commands[0].replace("-", "_")}(args, user_id)

        # Generic handler for other commands
        return {{
            "command": cmd,
            "args": args,
            "user_id": user_id,
            "status": "processed"
        }}

    async def {commands[0].replace("-", "_")}(self, args: list, user_id: str = None):
        """Handle {commands[0]} command"""
        logger.info(f"{commands[0]}: {{args}}")

        # Implement command logic here
        return {{
            "command": "{commands[0]}",
            "args": args,
            "result": "success",
            "timestamp": datetime.now().isoformat()
        }}

    def get_status(self):
        """Get agent status"""
        return {{
            "agent": "{agent_name}",
            "category": "{category}",
            "status": "active",
            "commands": self.commands,
            "timestamp": datetime.now().isoformat()
        }}


async def main():
    """Main entry point"""
    agent = {agent_name.replace("-", "_").title().replace("_", "")}()
    print(agent.get_status())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
'''

def generate_db_py(agent_name, agent_info):
    """Generate db.py content"""
    tables = agent_info.get("db_tables", {})
    create_statements = []
    for table_name, schema in tables.items():
        create_statements.append(f'        self.cursor.execute("""CREATE TABLE IF NOT EXISTS {table_name}{schema}""")')

    create_statements_str = "\n".join(create_statements)

    return f'''#!/usr/bin/env python3
"""
Database module for {agent_name}
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class {agent_name.replace("-", "_").replace("-", "")}Database:
    """Database handler for {agent_name}"""

    def __init__(self, db_path: str = None):
        """Initialize database connection"""
        self.db_path = db_path or Path(f"/workspace/agents/{agent_name}/data.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        self._init_tables()

    def _init_tables(self):
        """Initialize database tables"""
        logger.info("Initializing database tables...")
{create_statements_str}
        self.connection.commit()

    def execute(self, query: str, params: tuple = None) -> sqlite3.Cursor:
        """Execute a SQL query"""
        if params is None:
            params = ()
        self.cursor.execute(query, params)
        self.connection.commit()
        return self.cursor

    def fetchall(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Fetch all results from a query"""
        if params is None:
            params = ()
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]

    def fetchone(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """Fetch one result from a query"""
        if params is None:
            params = ()
        self.cursor.execute(query, params)
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """Insert a row into a table"""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {{table}} ({{columns}}) VALUES ({{placeholders}})"
        self.cursor.execute(query, tuple(data.values()))
        self.connection.commit()
        return self.cursor.lastrowid

    def update(self, table: str, data: Dict[str, Any], where: Dict[str, Any]) -> int:
        """Update rows in a table"""
        set_clause = ', '.join([f"{{k}} = ?" for k in data.keys()])
        where_clause = ' AND '.join([f"{{k}} = ?" for k in where.keys()])
        query = f"UPDATE {{table}} SET {{set_clause}} WHERE {{where_clause}}"
        self.cursor.execute(query, tuple(data.values()) + tuple(where.values()))
        self.connection.commit()
        return self.cursor.rowcount

    def delete(self, table: str, where: Dict[str, Any]) -> int:
        """Delete rows from a table"""
        where_clause = ' AND '.join([f"{{k}} = ?" for k in where.keys()])
        query = f"DELETE FROM {{table}} WHERE {{where_clause}}"
        self.cursor.execute(query, tuple(where.values()))
        self.connection.commit()
        return self.cursor.rowcount

    def close(self):
        """Close database connection"""
        self.connection.close()


# For logging in _init_tables
import logging
logger = logging.getLogger(__name__)
'''

def generate_discord_py(agent_name, agent_info):
    """Generate discord.py content"""
    commands = agent_info.get("discord_commands", [])
    commands_list = "\n".join([f'            bot.tree.command(name="{cmd}")(self.{cmd.replace("-", "_")})' for cmd in commands])

    methods = "\n\n".join([
        f'''    async def {cmd.replace("-", "_")}(self, interaction):
        """Handle {cmd} command"""
        await interaction.response.send_message(f"{{agent_name}}: {cmd} command received!")'''
        for cmd in commands
    ])

    return f'''#!/usr/bin/env python3
"""
Discord bot integration for {agent_name}
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from pathlib import Path
import sys

# Add parent directory to path to import agent
sys.path.insert(0, str(Path(__file__).parent.parent))
from agent import {agent_name.replace("-", "_").title().replace("_", "")}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiscordBot(commands.Bot):
    """Discord bot for {agent_name}"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            activity=discord.Activity(type=discord.ActivityType.watching, name="for commands")
        )

        self.agent = {agent_name.replace("-", "_").title().replace("_", "")}()

    async def setup_hook(self):
        """Setup hook for bot"""
        await self.tree.sync()
        logger.info("Commands synced")

{commands_list}

{methods}

    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f"{{self.user}} is ready!")
        logger.info(f"Connected to {{len(self.guilds)}} guilds")

    async def on_message(self, message: discord.Message):
        """Handle incoming messages"""
        # Ignore messages from the bot itself
        if message.author == self.user:
            return

        # Process message through agent
        response = await self.agent.process_message(message.content, str(message.author.id))

        # Send response if not empty
        if response and "error" not in response:
            await message.channel.send(f"Processed: {{response.get('status', 'done')}}")


async def main():
    """Main entry point"""
    # Get Discord token from environment or config
    import os
    token = os.getenv("DISCORD_TOKEN")

    if not token:
        logger.error("DISCORD_TOKEN environment variable not set")
        return

    bot = DiscordBot()
    await bot.start(token)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
'''

def generate_readme_md(agent_name, agent_info):
    """Generate README.md content"""
    category = agent_info["category"]
    commands = agent_info.get("discord_commands", [])

    return f'''# {agent_name}

{agent_info["description"]}

## 概要 / Overview

**日本語:**
{agent_info["description"]}を提供するエージェント。

**English:**
An agent providing {agent_info["description"]}.

## カテゴリ / Category

- `{category}`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
{chr(10).join([f'| `!{cmd}` | {cmd} コマンド | {cmd} command |' for cmd in commands])}

## インストール / Installation

```bash
cd agents/{agent_name}
pip install -r requirements.txt
```

## 使用方法 / Usage

### エージェントの実行 / Run Agent

```bash
python agent.py
```

### Discord Bot の起動 / Start Discord Bot

```bash
export DISCORD_TOKEN="your_bot_token"
python discord.py
```

## データベース / Database

データベースファイル: `data.db`

### テーブル / Tables

{chr(10).join([f'- **{table}**: {schema.strip("()")}' for table, schema in agent_info.get("db_tables", {}).items()])}

## 開発 / Development

```bash
# テスト
python -m pytest

# フォーマット
black agent.py db.py discord.py
```

## ライセンス / License

MIT License

---

_This agent is part of the OpenClaw Agents ecosystem._
'''

def generate_requirements_txt(agent_name, agent_info):
    """Generate requirements.txt content"""
    return '''discord.py>=2.3.0
aiohttp>=3.9.0
python-dotenv>=1.0.0
pytest>=7.4.0
pytest-asyncio>=0.21.0
black>=23.12.0
'''

def create_agent_directory(agent_name, agent_info):
    """Create all files for an agent"""
    agent_dir = AGENTS_DIR / agent_name
    agent_dir.mkdir(parents=True, exist_ok=True)

    files = {
        "agent.py": generate_agent_py(agent_name, agent_info),
        "db.py": generate_db_py(agent_name, agent_info),
        "discord.py": generate_discord_py(agent_name, agent_info),
        "README.md": generate_readme_md(agent_name, agent_info),
        "requirements.txt": generate_requirements_txt(agent_name, agent_info),
    }

    for filename, content in files.items():
        filepath = agent_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Created: {filepath}")

    return True

def update_progress(progress_file, agent_name, status="created"):
    """Update progress tracking file"""
    progress_path = BASE_DIR / progress_file

    if not progress_path.exists():
        progress_data = {
            "version": "V91",
            "started_at": datetime.now().isoformat(),
            "agents": {}
        }
    else:
        with open(progress_path, "r", encoding="utf-8") as f:
            progress_data = json.load(f)

    progress_data["agents"][agent_name] = {
        "status": status,
        "updated_at": datetime.now().isoformat()
    }

    with open(progress_path, "w", encoding="utf-8") as f:
        json.dump(progress_data, f, indent=2, ensure_ascii=False)

    return progress_data

def main():
    """Main orchestration function"""
    print("=" * 60)
    print("🚀 Project V91 Orchestration Started")
    print("=" * 60)

    created_count = 0
    failed_count = 0
    progress_file = "v91_progress.json"

    # Create each agent
    for agent_name, agent_info in V91_AGENTS.items():
        print(f"\n📦 Creating {agent_name}...")
        try:
            create_agent_directory(agent_name, agent_info)
            update_progress(progress_file, agent_name, "created")
            created_count += 1
        except Exception as e:
            print(f"❌ Failed to create {agent_name}: {e}")
            update_progress(progress_file, agent_name, f"failed: {str(e)}")
            failed_count += 1

    # Final summary
    print("\n" + "=" * 60)
    print(f"📊 Summary: {created_count} created, {failed_count} failed")
    print("=" * 60)

    # Save final progress
    progress_data = update_progress(progress_file, "__summary__", "completed")
    progress_data["total"] = len(V91_AGENTS)
    progress_data["created"] = created_count
    progress_data["failed"] = failed_count
    progress_data["completed_at"] = datetime.now().isoformat()

    with open(BASE_DIR / progress_file, "w", encoding="utf-8") as f:
        json.dump(progress_data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Progress saved to {progress_file}")

    # Git commit hint
    print(f"\n💡 Remember to commit your changes:")
    print(f"   git add -A")
    print(f"   git commit -m 'feat: 次期プロジェクト案 V91 完了 ({created_count}/{len(V91_AGENTS)})'")
    print(f"   git push")


if __name__ == "__main__":
    main()
