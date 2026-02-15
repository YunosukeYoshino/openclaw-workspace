#!/usr/bin/env python3
"""
Baseball Visualization Agents Orchestrator
野球データ可視化エージェントオーケストレーター

Orchestrates development of baseball data visualization agents.
野球データ可視化エージェントの開発をオーケストレーションします。
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
        \"\"\"Initialize database / データベースを初期化\"\"\"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                {content_field} TEXT NOT NULL,
                chart_type TEXT,
                data_source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def add_entry(self, title: str, content: str, chart_type: str = "",
                   data_source: str = "") -> int:
        \"\"\"Add a visualization entry / 可視化エントリーを追加\"\"\"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO {table_name} (title, {content_field}, chart_type, data_source)
            VALUES (?, ?, ?, ?)
        ''', (title, content, chart_type, data_source))

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
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))

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
        # TODO: Implement search functionality
        await ctx.send(f"Search functionality for '{query}' - coming soon!")


def setup(bot: commands.Bot, agent):
    \"\"\"Setup cog / Cogをセットアップ\"\"\"
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
    chart_type TEXT,
    data_source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
- matplotlib (for visualization)

## License / ライセンス

MIT
"""


# Template for requirements.txt
REQUIREMENTS_TEMPLATE = """discord.py>=2.0.0
python-dotenv>=1.0.0
matplotlib>=3.5.0
plotly>=5.0.0
pandas>=1.3.0
"""


# Project configuration
PROJECT_CONFIG = {
    "name": "Baseball Visualization Agents",
    "name_ja": "野球データ可視化エージェント",
    "version": "1.0.0",
    "agents": [
        {
            "agent_name": "baseball-chart-agent",
            "japanese_name": "野球チャート生成エージェント",
            "description": "Generates charts from baseball statistics data",
            "description_ja": "野球統計データからチャートを生成",
            "table_name": "charts",
            "content_field": "chart_data",
            "custom_method": "generate_chart",
            "custom_method_description": "Generate a chart from baseball data / 野球データからチャートを生成",
            "discord_prefix": "bc",
            "full_description": "This agent generates various charts from baseball statistics data, including bar charts, line graphs, and scatter plots. It helps visualize player performance, team statistics, and game trends.",
            "full_description_ja": "このエージェントは、野球統計データから棒グラフ、折れ線グラフ、散布図など、様々なチャートを生成します。選手のパフォーマンス、チームの統計、試合の傾向を視覚化するのに役立ちます。",
            "features": """- Bar charts for player stats / 選手統計の棒グラフ
- Line graphs for trends / 傾向の折れ線グラフ
- Scatter plots for correlations / 相関関係の散布図
- Custom chart styles / カスタムチャートスタイル
- Export to PNG/SVG / PNG/SVG形式でエクスポート"""
        },
        {
            "agent_name": "baseball-graph-agent",
            "japanese_name": "野球グラフ生成エージェント",
            "description": "Creates interactive graphs for baseball data analysis",
            "description_ja": "野球データ分析用のインタラクティブグラフを作成",
            "table_name": "graphs",
            "content_field": "graph_data",
            "custom_method": "create_graph",
            "custom_method_description": "Create an interactive graph / インタラクティブグラフを作成",
            "discord_prefix": "bg",
            "full_description": "This agent creates interactive graphs using Plotly, allowing users to explore baseball data through zooming, panning, and hover tooltips. Great for deep data analysis.",
            "full_description_ja": "このエージェントは、Plotlyを使用してインタラクティブグラフを作成し、ユーザーがズーム、パン、ホーバーツールチップを通じて野球データを探索できるようにします。詳細なデータ分析に最適です。",
            "features": """- Interactive Plotly graphs / インタラクティブPlotlyグラフ
- Zoom and pan / ズームとパン
- Hover tooltips / ホーバーツールチップ
- Time series graphs / 時系列グラフ
- 3D visualization / 3D可視化"""
        },
        {
            "agent_name": "baseball-dashboard-agent",
            "japanese_name": "野球ダッシュボードエージェント",
            "description": "Builds comprehensive dashboards for baseball metrics",
            "description_ja": "野球メトリクスの包括的なダッシュボードを構築",
            "table_name": "dashboards",
            "content_field": "dashboard_config",
            "custom_method": "build_dashboard",
            "custom_method_description": "Build a comprehensive dashboard / 包括的なダッシュボードを構築",
            "discord_prefix": "bd",
            "full_description": "This agent creates comprehensive dashboards that display multiple baseball metrics at once. Includes player cards, team stats, recent games, and trend analysis.",
            "full_description_ja": "このエージェントは、複数の野球メトリクスを一度に表示する包括的なダッシュボードを作成します。選手カード、チーム統計、最近の試合、傾向分析が含まれます。",
            "features": """- Multi-metric display / 複数メトリクス表示
- Player cards / 選手カード
- Team overview / チーム概要
- Recent games summary / 最近の試合概要
- Real-time updates / リアルタイム更新"""
        },
        {
            "agent_name": "baseball-report-agent",
            "japanese_name": "野球レポート生成エージェント",
            "description": "Generates detailed baseball analysis reports with visualizations",
            "description_ja": "可視化を含む詳細な野球分析レポートを生成",
            "table_name": "reports",
            "content_field": "report_content",
            "custom_method": "generate_report",
            "custom_method_description": "Generate a detailed analysis report / 詳細な分析レポートを生成",
            "discord_prefix": "br",
            "full_description": "This agent generates detailed baseball analysis reports with embedded charts, graphs, and tables. Perfect for scouting reports, game analysis, and performance reviews.",
            "full_description_ja": "このエージェントは、埋め込まれたチャート、グラフ、テーブルを含む詳細な野球分析レポートを生成します。スカウティングレポート、試合分析、パフォーマンスレビューに最適です。",
            "features": """- Embedded visualizations / 埋め込み可視化
- Statistical summaries / 統計サマリー
- Player comparisons / 選手比較
- PDF export / PDFエクスポート
- Custom templates / カスタムテンプレート"""
        },
        {
            "agent_name": "baseball-presentation-agent",
            "japanese_name": "野球プレゼンテーションエージェント",
            "description": "Creates presentations and slides for baseball analysis",
            "description_ja": "野球分析用のプレゼンテーションとスライドを作成",
            "table_name": "presentations",
            "content_field": "slide_content",
            "custom_method": "create_presentation",
            "custom_method_description": "Create a presentation / プレゼンテーションを作成",
            "discord_prefix": "bp",
            "full_description": "This agent creates professional presentations and slides for baseball analysis. Includes auto-generated slides with charts, key insights, and talking points.",
            "full_description_ja": "このエージェントは、野球分析用のプロフェッショナルなプレゼンテーションとスライドを作成します。チャート、主要な洞察、トーキングポイントを含む自動生成スライドが含まれます。",
            "features": """- Professional slides / プロフェッショナルスライド
- Auto-generated insights / 自動生成洞察
- Chart integration / チャート統合
- Talking points / トーキングポイント
- PowerPoint export / PowerPointエクスポート"""
        }
    ]
}


class BaseballVisualizationOrchestrator:
    """Orchestrator for Baseball Visualization Agents / 野球データ可視化エージェントのオーケストレーター"""

    def __init__(self, progress_file: str = "baseball_visualization_progress.json"):
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
        """Run orchestrator / オーケストレーターを実行"""
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
    orchestrator = BaseballVisualizationOrchestrator()
    result = orchestrator.run()

    # Update Plan.md
    print("\\nUpdating Plan.md...")
    # Note: Plan.md update will be done separately

    return result


if __name__ == "__main__":
    sys.exit(main())
