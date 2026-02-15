#!/usr/bin/env python3
"""
Orchestrator for Project V101 - Baseball Big Data & Game VR/AR/Metaverse & Erotic AI Recommendations & AI/ML Engineering & Security Compliance
Total: 25 agents (5 per category)
"""

import os
import json
from pathlib import Path
from datetime import datetime

# Base paths
BASE_DIR = Path("/workspace")
AGENTS_DIR = BASE_DIR / "agents"

# V101 Agent Definitions
V101_AGENTS = {
    # 野球データ・ビッグデータ分析エージェント (5個)
    "baseball-bigdata-agent": {
        "description": "野球ビッグデータエージェント。大規模野球データの収集・分析。",
        "category": "baseball",
        "db_tables": {
            "big_datasets": "(id INTEGER PRIMARY KEY, name TEXT, source TEXT, size_bytes INTEGER, record_count INTEGER, schema TEXT)",
            "data_partitions": "(id INTEGER PRIMARY KEY, dataset_id INTEGER, partition_key TEXT, value TEXT, path TEXT, FOREIGN KEY (dataset_id) REFERENCES big_datasets(id))",
            "data_jobs": "(id INTEGER PRIMARY KEY, dataset_id INTEGER, job_type TEXT, status TEXT, started_at TIMESTAMP, completed_at TIMESTAMP, FOREIGN KEY (dataset_id) REFERENCES big_datasets(id))",
        },
        "discord_commands": ["ingest_data", "query_data", "data_jobs", "data_info"],
    },
    "baseball-data-science-platform-agent": {
        "description": "野球データサイエンスプラットフォームエージェント。野球データサイエンスのための統合プラットフォーム。",
        "category": "baseball",
        "db_tables": {
            "notebooks": "(id INTEGER PRIMARY KEY, title TEXT, author TEXT, code TEXT, created_at TIMESTAMP, updated_at TIMESTAMP)",
            "experiments": "(id INTEGER PRIMARY KEY, name TEXT, parameters TEXT, metrics TEXT, status TEXT, created_at TIMESTAMP)",
            "models": "(id INTEGER PRIMARY KEY, name TEXT, version TEXT, accuracy REAL, created_at TIMESTAMP, path TEXT)",
        },
        "discord_commands": ["create_notebook", "run_experiment", "list_models", "platform_status"],
    },
    "baseball-statistical-modeling-agent": {
        "description": "野球統計モデリングエージェント。野球データの統計的モデリング・予測。",
        "category": "baseball",
        "db_tables": {
            "models": "(id INTEGER PRIMARY KEY, name TEXT, type TEXT, features TEXT, hyperparameters TEXT, accuracy REAL)",
            "predictions": "(id INTEGER PRIMARY KEY, model_id INTEGER, player_id INTEGER, prediction TEXT, confidence REAL, created_at TIMESTAMP, FOREIGN KEY (model_id) REFERENCES models(id))",
            "model_evaluations": "(id INTEGER PRIMARY KEY, model_id INTEGER, metric TEXT, value REAL, evaluated_at TIMESTAMP, FOREIGN KEY (model_id) REFERENCES models(id))",
        },
        "discord_commands": ["create_model", "train_model", "predict", "evaluate_model"],
    },
    "baseball-data-visualization-agent": {
        "description": "野球データ可視化エージェント。野球データの高度な可視化・ダッシュボード。",
        "category": "baseball",
        "db_tables": {
            "dashboards": "(id INTEGER PRIMARY KEY, name TEXT, layout JSON, widgets TEXT, created_at TIMESTAMP, updated_at TIMESTAMP)",
            "charts": "(id INTEGER PRIMARY KEY, dashboard_id INTEGER, type TEXT, data_source TEXT, config JSON, FOREIGN KEY (dashboard_id) REFERENCES dashboards(id))",
            "reports": "(id INTEGER PRIMARY KEY, name TEXT, type TEXT, schedule TEXT, recipients TEXT, created_at TIMESTAMP)",
        },
        "discord_commands": ["create_dashboard", "add_chart", "view_dashboard", "schedule_report"],
    },
    "baseball-data-governance-agent": {
        "description": "野球データガバナンスエージェント。野球データの品質管理・ガバナンス。",
        "category": "baseball",
        "db_tables": {
            "data_quality_rules": "(id INTEGER PRIMARY KEY, name TEXT, table TEXT, column TEXT, condition TEXT, severity TEXT)",
            "quality_checks": "(id INTEGER PRIMARY KEY, rule_id INTEGER, checked_at TIMESTAMP, passed INTEGER, failed_count INTEGER, details TEXT, FOREIGN KEY (rule_id) REFERENCES data_quality_rules(id))",
            "data_lineage": "(id INTEGER PRIMARY KEY, source_table TEXT, target_table TEXT, transformation TEXT, created_at TIMESTAMP)",
        },
        "discord_commands": ["add_rule", "run_checks", "lineage", "governance_status"],
    },

    # ゲームVR・AR・メタバースエージェント (5個)
    "game-vr-engine-agent": {
        "description": "ゲームVRエンジンエージェント。VRゲーム開発エンジンの管理・最適化。",
        "category": "game",
        "db_tables": {
            "vr_engines": "(id INTEGER PRIMARY KEY, name TEXT, version TEXT, capabilities JSON, performance_metrics JSON)",
            "vr_scenes": "(id INTEGER PRIMARY KEY, project_id INTEGER, name TEXT, settings JSON, assets JSON, FOREIGN KEY (project_id) REFERENCES projects(id))",
            "vr_interactions": "(id INTEGER PRIMARY KEY, scene_id INTEGER, type TEXT, action TEXT, parameters JSON, FOREIGN KEY (scene_id) REFERENCES vr_scenes(id))",
        },
        "discord_commands": ["vr_engine", "create_scene", "add_interaction", "optimize_vr"],
    },
    "game-ar-engine-agent": {
        "description": "ゲームARエンジンエージェント。ARゲーム開発エンジンの管理・最適化。",
        "category": "game",
        "db_tables": {
            "ar_engines": "(id INTEGER PRIMARY KEY, name TEXT, version TEXT, capabilities JSON, tracking_type TEXT)",
            "ar_experiences": "(id INTEGER PRIMARY KEY, project_id INTEGER, name TEXT, markers JSON, content JSON, FOREIGN KEY (project_id) REFERENCES projects(id))",
            "ar_analytics": "(id INTEGER PRIMARY KEY, experience_id INTEGER, user_id INTEGER, interaction_type TEXT, timestamp TIMESTAMP, FOREIGN KEY (experience_id) REFERENCES ar_experiences(id))",
        },
        "discord_commands": ["ar_engine", "create_experience", "add_marker", "ar_analytics"],
    },
    "game-metaverse-agent": {
        "description": "ゲームメタバースエージェント。メタバース空間の作成・管理・運営。",
        "category": "game",
        "db_tables": {
            "worlds": "(id INTEGER PRIMARY KEY, name TEXT, description TEXT, capacity INTEGER, settings JSON)",
            "avatars": "(id INTEGER PRIMARY KEY, user_id INTEGER, world_id INTEGER, appearance JSON, position JSON, FOREIGN KEY (world_id) REFERENCES worlds(id))",
            "metaverse_events": "(id INTEGER PRIMARY KEY, world_id INTEGER, event_type TEXT, data JSON, timestamp TIMESTAMP, FOREIGN KEY (world_id) REFERENCES worlds(id))",
        },
        "discord_commands": ["create_world", "manage_avatar", "world_events", "metaverse_stats"],
    },
    "game-3d-content-agent": {
        "description": "ゲーム3Dコンテンツエージェント。3Dモデル・アセットの作成・管理。",
        "category": "game",
        "db_tables": {
            "models": "(id INTEGER PRIMARY KEY, name TEXT, format TEXT, polygon_count INTEGER, texture_count INTEGER, path TEXT)",
            "materials": "(id INTEGER PRIMARY KEY, model_id INTEGER, name TEXT, type TEXT, properties JSON, FOREIGN KEY (model_id) REFERENCES models(id))",
            "animations": "(id INTEGER PRIMARY KEY, model_id INTEGER, name TEXT, duration REAL, frame_rate INTEGER, FOREIGN KEY (model_id) REFERENCES models(id))",
        },
        "discord_commands": ["add_model", "add_material", "add_animation", "3d_library"],
    },
    "game-immersive-agent": {
        "description": "ゲームイマーシブエージェント。没入型体験の設計・実装。",
        "category": "game",
        "db_tables": {
            "experiences": "(id INTEGER PRIMARY KEY, name TEXT, type TEXT, immersion_level TEXT, devices JSON)",
            "haptics": "(id INTEGER PRIMARY KEY, experience_id INTEGER, effect_type TEXT, intensity REAL, duration REAL, FOREIGN KEY (experience_id) REFERENCES experiences(id))",
            "spatial_audio": "(id INTEGER PRIMARY KEY, experience_id INTEGER, source TEXT, position JSON, reverb TEXT, FOREIGN KEY (experience_id) REFERENCES experiences(id))",
        },
        "discord_commands": ["create_experience", "add_haptics", "configure_audio", "immersion_test"],
    },

    # えっちコンテンツAI推薦・レコメンデーションエージェント (5個)
    "erotic-recommendation-v3-agent": {
        "description": "えっちコンテンツ推薦V3エージェント。高度なAIによるパーソナライズ推薦。",
        "category": "erotic",
        "db_tables": {
            "models": "(id INTEGER PRIMARY KEY, name TEXT, algorithm TEXT, features TEXT, accuracy REAL, version TEXT)",
            "recommendations": "(id INTEGER PRIMARY KEY, user_id INTEGER, content_id INTEGER, score REAL, reason TEXT, created_at TIMESTAMP)",
            "feedback": "(id INTEGER PRIMARY KEY, recommendation_id INTEGER, rating INTEGER, clicked INTEGER, timestamp TIMESTAMP)",
        },
        "discord_commands": ["recommend", "train_model", "model_performance", "recommendation_history"],
    },
    "erotic-collaborative-filtering-agent": {
        "description": "えっち協調フィルタリングエージェント。ユーザー間の類似性に基づく推薦。",
        "category": "erotic",
        "db_tables": {
            "user_preferences": "(id INTEGER PRIMARY KEY, user_id INTEGER, content_id INTEGER, rating INTEGER, timestamp TIMESTAMP)",
            "similar_users": "(id INTEGER PRIMARY KEY, user_id INTEGER, similar_user_id INTEGER, similarity_score REAL, updated_at TIMESTAMP)",
            "item_similarities": "(id INTEGER PRIMARY KEY, item_id INTEGER, similar_item_id INTEGER, similarity_score REAL, updated_at TIMESTAMP)",
        },
        "discord_commands": ["find_similar_users", "find_similar_items", "user_neighborhood", "collaborative_recommend"],
    },
    "erotic-content-embedding-agent": {
        "description": "えっちコンテンツ埋め込みエージェント。コンテンツのベクトル埋め込み生成。",
        "category": "erotic",
        "db_tables": {
            "embeddings": "(id INTEGER PRIMARY KEY, content_id INTEGER, vector BLOB, model_version TEXT, dimensions INTEGER, created_at TIMESTAMP)",
            "similarity_search": "(id INTEGER PRIMARY KEY, query_vector BLOB, results JSON, search_time REAL, timestamp TIMESTAMP)",
            "embedding_models": "(id INTEGER PRIMARY KEY, name TEXT, architecture TEXT, dimensions INTEGER, training_data TEXT)",
        },
        "discord_commands": ["generate_embedding", "similarity_search", "batch_embed", "model_info"],
    },
    "erotic-hybrid-recommendation-agent": {
        "description": "えっちハイブリッド推薦エージェント。複数のアルゴリズムを組み合わせた推薦。",
        "category": "erotic",
        "db_tables": {
            "strategies": "(id INTEGER PRIMARY KEY, name TEXT, type TEXT, weight REAL, parameters JSON)",
            "hybrid_models": "(id INTEGER PRIMARY KEY, name TEXT, strategies JSON, ensemble_method TEXT, performance_metrics JSON)",
            "recommendations": "(id INTEGER PRIMARY KEY, user_id INTEGER, content_id INTEGER, hybrid_score REAL, strategy_scores JSON, created_at TIMESTAMP)",
        },
        "discord_commands": ["create_hybrid_model", "add_strategy", "hybrid_recommend", "tune_weights"],
    },
    "erotic-exploration-agent": {
        "description": "えっち探索エージェント。ユーザーの新たな興味を発見・提案。",
        "category": "erotic",
        "db_tables": {
            "exploration_items": "(id INTEGER PRIMARY KEY, user_id INTEGER, content_id INTEGER, score REAL, reason TEXT, suggested_at TIMESTAMP)",
            "diversity_metrics": "(id INTEGER PRIMARY KEY, user_id INTEGER, diversity_score REAL, novelty_score REAL, serendipity_score REAL, calculated_at TIMESTAMP)",
            "exploration_history": "(id INTEGER PRIMARY KEY, user_id INTEGER, content_id INTEGER, accepted INTEGER, interaction_type TEXT, timestamp TIMESTAMP)",
        },
        "discord_commands": ["discover_new", "diversity_report", "exploration_history", "tune_exploration"],
    },

    # AI/MLエンジニアリングエージェント (5個)
    "ai-model-pipeline-agent": {
        "description": "AIモデルパイプラインエージェント。MLパイプラインの自動化・管理。",
        "category": "ai",
        "db_tables": {
            "pipelines": "(id INTEGER PRIMARY KEY, name TEXT, stages JSON, config JSON, status TEXT)",
            "pipeline_runs": "(id INTEGER PRIMARY KEY, pipeline_id INTEGER, start_time TIMESTAMP, end_time TIMESTAMP, status TEXT, metrics JSON, FOREIGN KEY (pipeline_id) REFERENCES pipelines(id))",
            "stage_runs": "(id INTEGER PRIMARY KEY, run_id INTEGER, stage_name TEXT, start_time TIMESTAMP, end_time TIMESTAMP, status TEXT, output_path TEXT, FOREIGN KEY (run_id) REFERENCES pipeline_runs(id))",
        },
        "discord_commands": ["create_pipeline", "run_pipeline", "pipeline_history", "stage_logs"],
    },
    "ai-model-monitoring-agent": {
        "description": "AIモデル監視エージェント。モデルのパフォーマンス・ドリフト監視。",
        "category": "ai",
        "db_tables": {
            "models": "(id INTEGER PRIMARY KEY, name TEXT, version TEXT, deployed_at TIMESTAMP, baseline_metrics JSON)",
            "metrics": "(id INTEGER PRIMARY KEY, model_id INTEGER, metric_name TEXT, value REAL, threshold REAL, status TEXT, timestamp TIMESTAMP, FOREIGN KEY (model_id) REFERENCES models(id))",
            "alerts": "(id INTEGER PRIMARY KEY, model_id INTEGER, alert_type TEXT, severity TEXT, message TEXT, acknowledged INTEGER, created_at TIMESTAMP, FOREIGN KEY (model_id) REFERENCES models(id))",
        },
        "discord_commands": ["model_status", "metrics_history", "alerts", "acknowledge_alert"],
    },
    "ai-feature-store-agent": {
        "description": "AIフィーチャーストアエージェント。MLフィーチャーの管理・提供。",
        "category": "ai",
        "db_tables": {
            "features": "(id INTEGER PRIMARY KEY, name TEXT, type TEXT, source TEXT, description TEXT, schema JSON)",
            "feature_groups": "(id INTEGER PRIMARY KEY, name TEXT, features JSON, refresh_schedule TEXT)",
            "feature_values": "(id INTEGER PRIMARY KEY, feature_id INTEGER, entity_id INTEGER, value TEXT, timestamp TIMESTAMP, FOREIGN KEY (feature_id) REFERENCES features(id))",
        },
        "discord_commands": ["add_feature", "create_group", "get_features", "feature_history"],
    },
    "ai-experiment-tracking-agent": {
        "description": "AI実験追跡エージェント。ML実験の記録・管理。",
        "category": "ai",
        "db_tables": {
            "experiments": "(id INTEGER PRIMARY KEY, name TEXT, project_id INTEGER, parameters TEXT, metrics TEXT, status TEXT, created_at TIMESTAMP)",
            "runs": "(id INTEGER PRIMARY KEY, experiment_id INTEGER, run_id TEXT, start_time TIMESTAMP, end_time TIMESTAMP, metrics TEXT, artifacts TEXT, FOREIGN KEY (experiment_id) REFERENCES experiments(id))",
            "comparisons": "(id INTEGER PRIMARY KEY, experiment_ids TEXT, comparison_metrics JSON, conclusion TEXT, created_at TIMESTAMP)",
        },
        "discord_commands": ["create_experiment", "log_run", "compare_runs", "experiment_history"],
    },
    "ai-model-registry-agent": {
        "description": "AIモデルレジストリエージェント。モデルのバージョン管理・デプロイ。",
        "category": "ai",
        "db_tables": {
            "registered_models": "(id INTEGER PRIMARY KEY, name TEXT, description TEXT, project_id INTEGER)",
            "model_versions": "(id INTEGER PRIMARY KEY, model_id INTEGER, version TEXT, artifact_path TEXT, framework TEXT, metrics JSON, created_at TIMESTAMP, FOREIGN KEY (model_id) REFERENCES registered_models(id))",
            "deployments": "(id INTEGER PRIMARY KEY, version_id INTEGER, environment TEXT, endpoint TEXT, deployed_at TIMESTAMP, status TEXT, FOREIGN KEY (version_id) REFERENCES model_versions(id))",
        },
        "discord_commands": ["register_model", "add_version", "deploy_model", "model_metadata"],
    },

    # セキュリティコンプライアンス・規制対応エージェント (5個)
    "security-compliance-agent": {
        "description": "セキュリティコンプライアンスエージェント。コンプライアンス要件の管理・監視。",
        "category": "security",
        "db_tables": {
            "frameworks": "(id INTEGER PRIMARY KEY, name TEXT, description TEXT, requirements JSON)",
            "controls": "(id INTEGER PRIMARY KEY, framework_id INTEGER, control_id TEXT, description TEXT, status TEXT, evidence TEXT, FOREIGN KEY (framework_id) REFERENCES frameworks(id))",
            "assessments": "(id INTEGER PRIMARY KEY, framework_id INTEGER, assessment_type TEXT, score REAL, findings JSON, assessed_at TIMESTAMP, FOREIGN KEY (framework_id) REFERENCES frameworks(id))",
        },
        "discord_commands": ["frameworks", "controls", "run_assessment", "compliance_report"],
    },
    "security-gdpr-agent": {
        "description": "セキュリティGDPRエージェント。GDPRコンプライアンスの管理・対応。",
        "category": "security",
        "db_tables": {
            "data_subjects": "(id INTEGER PRIMARY KEY, user_id INTEGER, consent_records JSON, data_categories TEXT, created_at TIMESTAMP)",
            "consent_records": "(id INTEGER PRIMARY KEY, subject_id INTEGER, consent_type TEXT, granted INTEGER, timestamp TEXT, expiry TEXT, FOREIGN KEY (subject_id) REFERENCES data_subjects(id))",
            "data_requests": "(id INTEGER PRIMARY KEY, subject_id INTEGER, request_type TEXT, status TEXT, response_data TEXT, completed_at TIMESTAMP, FOREIGN KEY (subject_id) REFERENCES data_subjects(id))",
        },
        "discord_commands": ["subject_info", "manage_consent", "handle_request", "privacy_audit"],
    },
    "security-pci-dss-agent": {
        "description": "セキュリティPCI DSSエージェント。PCI DSSコンプライアンスの管理・対応。",
        "category": "security",
        "db_tables": {
            "requirements": "(id INTEGER PRIMARY KEY, requirement_id TEXT, description TEXT, control_procedures TEXT, status TEXT)",
            "scans": "(id INTEGER PRIMARY KEY, scan_type TEXT, start_time TIMESTAMP, end_time TIMESTAMP, vulnerabilities JSON, status TEXT)",
            "remediations": "(id INTEGER PRIMARY KEY, requirement_id INTEGER, vulnerability_id TEXT, plan TEXT, status TEXT, completed_at TIMESTAMP, FOREIGN KEY (requirement_id) REFERENCES requirements(id))",
        },
        "discord_commands": ["requirements", "run_scan", "remediation_plan", "compliance_status"],
    },
    "security-hipaa-agent": {
        "description": "セキュリティHIPAAエージェント。HIPAAコンプライアンスの管理・対応。",
        "category": "security",
        "db_tables": {
            "phi_records": "(id INTEGER PRIMARY KEY, record_id TEXT, phi_type TEXT, access_controls TEXT, encryption_status TEXT)",
            "audit_logs": "(id INTEGER PRIMARY KEY, phi_id INTEGER, action_type TEXT, user_id INTEGER, timestamp TIMESTAMP, details TEXT, FOREIGN KEY (phi_id) REFERENCES phi_records(id))",
            "risk_assessments": "(id INTEGER PRIMARY KEY, phi_id INTEGER, risk_level TEXT, mitigation_plan TEXT, assessed_at TIMESTAMP, FOREIGN KEY (phi_id) REFERENCES phi_records(id))",
        },
        "discord_commands": ["phi_inventory", "access_audit", "risk_assessment", "compliance_check"],
    },
    "security-soc2-agent": {
        "description": "セキュリティSOC 2エージェント。SOC 2コンプライアンスの管理・対応。",
        "category": "security",
        "db_tables": {
            "trust_services": "(id INTEGER PRIMARY KEY, service_type TEXT, criteria TEXT, controls JSON, status TEXT)",
            "evidence": "(id INTEGER PRIMARY KEY, control_id INTEGER, evidence_type TEXT, file_path TEXT, collected_at TIMESTAMP, reviewer_id INTEGER)",
            "audit_reports": "(id INTEGER PRIMARY KEY, report_id TEXT, report_type TEXT, period_start TEXT, period_end TEXT, status TEXT, issued_at TIMESTAMP)",
        },
        "discord_commands": ["trust_services", "collect_evidence", "audit_status", "soc2_report"],
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
        """Initialize agent"""
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
        # Ignore messages from bot itself
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

_This agent is part of OpenClaw Agents ecosystem._
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
            "version": "V101",
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
    print("🚀 Project V101 Orchestration Started")
    print("=" * 60)

    created_count = 0
    failed_count = 0
    progress_file = "v101_progress.json"

    # Create each agent
    for agent_name, agent_info in V101_AGENTS.items():
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
    progress_data["total"] = len(V101_AGENTS)
    progress_data["created"] = created_count
    progress_data["failed"] = failed_count
    progress_data["completed_at"] = datetime.now().isoformat()

    with open(BASE_DIR / progress_file, "w", encoding="utf-8") as f:
        json.dump(progress_data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Progress saved to {progress_file}")

    # Git commit hint
    print(f"\n💡 Remember to commit your changes:")
    print(f"   git add -A")
    print(f"   git commit -m 'feat: 次期プロジェクト案 V101 完了 ({created_count}/{len(V101_AGENTS)})'")
    print(f"   git push")


if __name__ == "__main__":
    main()
