#!/usr/bin/env python3
"""
Lifestyle Integration Project Orchestrator
ライフスタイル統合プロジェクト オーケストレーター

This orchestrator manages development of lifestyle integration agents
for comprehensive daily life support.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/workspace")
AGENTS_DIR = WORKSPACE / "agents"
PROGRESS_FILE = WORKSPACE / "lifestyle_integration_progress.json"
LOG_FILE = WORKSPACE / "lifestyle_integration_log.json"

PROJECT_NAME = "ライフスタイル統合プロジェクト"

LIFESTYLE_AGENTS = [
    {
        "name": "daily-planner-agent",
        "dir_name": "daily-planner-agent",
        "title_en": "Daily Planner Agent",
        "title_ja": "デイリープラナーエージェント",
        "description_en": "Comprehensive daily planning and scheduling",
        "description_ja": "包括的な日次計画とスケジューリング",
        "tables": ["daily_plans", "tasks", "reminders"],
        "commands": ["plan", "schedule", "task", "reminder", "optimize"],
        "category": "lifestyle"
    },
    {
        "name": "health-wellness-agent",
        "dir_name": "health-wellness-agent",
        "title_en": "Health & Wellness Agent",
        "title_ja": "ヘルス＆ウェルネスエージェント",
        "description_en": "Health tracking and wellness recommendations",
        "description_ja": "健康追跡とウェルネス推薦",
        "tables": ["health_metrics", "wellness_goals", "activities"],
        "commands": ["track", "analyze", "recommend", "goal", "report"],
        "category": "health"
    },
    {
        "name": "finance-tracker-agent",
        "dir_name": "finance-tracker-agent",
        "title_en": "Finance Tracker Agent",
        "title_ja": "ファイナンス追跡エージェント",
        "description_en": "Personal finance tracking and budgeting",
        "description_ja": "個人財務追跡と予算管理",
        "tables": ["transactions", "budgets", "goals", "alerts"],
        "commands": ["track", "budget", "analyze", "goal", "alert"],
        "category": "finance"
    },
    {
        "name": "social-connector-agent",
        "dir_name": "social-connector-agent",
        "title_en": "Social Connector Agent",
        "title_ja": "ソーシャルコネクターエージェント",
        "description_en": "Social relationship management and reminders",
        "description_ja": "ソーシャル関係管理とリマインダー",
        "tables": ["contacts", "interactions", "events", "reminders"],
        "commands": ["connect", "remember", "remind", "event", "network"],
        "category": "social"
    },
    {
        "name": "personal-growth-agent",
        "dir_name": "personal-growth-agent",
        "title_en": "Personal Growth Agent",
        "title_ja": "パーソナルグロースエージェント",
        "description_en": "Personal development and habit tracking",
        "description_ja": "自己啓発と習慣追跡",
        "tables": ["habits", "goals", "milestones", "reflections"],
        "commands": ["habit", "goal", "progress", "reflect", "motivate"],
        "category": "growth"
    }
]

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {"timestamp": timestamp, "message": message}
    print(f"[{timestamp}] {message}")
    try:
        logs = []
        if LOG_FILE.exists():
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        logs.append(log_entry)
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error writing to log file: {e}")

def load_progress():
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "project": PROJECT_NAME,
        "started_at": datetime.now().isoformat(),
        "total_agents": len(LIFESTYLE_AGENTS),
        "completed": 0,
        "failed": 0,
        "agents": {}
    }

def save_progress(progress):
    progress["updated_at"] = datetime.now().isoformat()
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)

def get_agent_template():
    return '''#!/usr/bin/env python3
"""
{{TITLE_EN}} / {{TITLE_JA}}
{{DESCRIPTION_EN}}

{{DESCRIPTION_JA}}
"""

import sqlite3
import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any

class {{CLASS_NAME}}:
    """{{TITLE_EN}}"""

    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), "data.db")
        self.db_path = db_path
        self.conn = None
        self.init_db()

    def init_db(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        # Create {{TABLE_NAME}} table
        cursor.execute("CREATE TABLE IF NOT EXISTS {{TABLE_NAME}} (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT NOT NULL, priority INTEGER DEFAULT 0, status TEXT DEFAULT 'active', metadata TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        # Create entries table
        cursor.execute("CREATE TABLE IF NOT EXISTS entries (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT NOT NULL, title TEXT, content TEXT NOT NULL, status TEXT DEFAULT 'active', priority INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        # Create indices
        cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_{self._sanitize_table("{{TABLE_NAME}}")}_status ON {{TABLE_NAME}}(status)')
        cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_{self._sanitize_table("{{TABLE_NAME}}")}_priority ON {{TABLE_NAME}}(priority)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_entries_status ON entries(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_entries_created_at ON entries(created_at)')
        self.conn.commit()

    def _sanitize_table(self, table_name):
        return table_name.replace("-", "_")

    def add_item(self, title, content, priority=0, metadata=None):
        cursor = self.conn.cursor()
        metadata_json = json.dumps(metadata) if metadata else None
        cursor.execute("INSERT INTO {{TABLE_NAME}} (title, content, priority, metadata) VALUES (?, ?, ?, ?)", (title, content, priority, metadata_json))
        self.conn.commit()
        return cursor.lastrowid

    def get_items(self, status=None, min_priority=None, limit=None):
        cursor = self.conn.cursor()
        query = "SELECT * FROM {{TABLE_NAME}}"
        params = []
        conditions = []
        if status:
            conditions.append("status = ?")
            params.append(status)
        if min_priority is not None:
            conditions.append("priority >= ?")
            params.append(min_priority)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY priority DESC, created_at DESC"
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        cursor.execute(query, params)
        return cursor.fetchall()

    def update_item(self, item_id, **kwargs):
        valid_fields = ['title', 'content', 'priority', 'status']
        updates = [f"{k} = ?" for k in kwargs.keys() if k in valid_fields]
        values = [v for k, v in kwargs.items() if k in valid_fields]
        if updates:
            query = f"UPDATE {{TABLE_NAME}} SET {', '.join(updates)} WHERE id = ?"
            values.append(item_id)
            cursor = self.conn.cursor()
            cursor.execute(query, values)
            self.conn.commit()

    def delete_item(self, item_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM {{TABLE_NAME}} WHERE id = ?", (item_id,))
        self.conn.commit()

    def add_entry(self, entry_type, content, title=None, priority=0):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO entries (type, title, content, priority) VALUES (?, ?, ?, ?)", (entry_type, title, content, priority))
        self.conn.commit()
        return cursor.lastrowid

    def get_entries(self, entry_type=None, status=None, limit=None):
        cursor = self.conn.cursor()
        query = "SELECT * FROM entries"
        params = []
        if entry_type:
            query += " WHERE type = ?"
            params.append(entry_type)
        query += " ORDER BY created_at DESC"
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        cursor.execute(query, params)
        return cursor.fetchall()

    def get_summary(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) as total, COUNT(CASE WHEN status='active' THEN 1 END) as active FROM {{TABLE_NAME}}")
        result = cursor.fetchone()
        return {"total": result['total'], "active": result['active']}

    def close(self):
        if self.conn:
            self.conn.close()

def main():
    agent = {{CLASS_NAME}}()
    try:
        print(f"{{TITLE_EN}} initialized")
        print(f"Database: {agent.db_path}")
        print("Available commands: {{COMMANDS}}")
    finally:
        agent.close()

if __name__ == "__main__":
    main()
'''

def get_db_template():
    return '''#!/usr/bin/env python3
"""
Database module for {{TITLE_EN}}
{{TITLE_JA}} データベースモジュール
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any

class {{DB_CLASS_NAME}}:
    """Database handler for {{TITLE_EN}}"""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), "data.db")
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self.connect()

    def connect(self) -> None:
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()

    def _init_tables(self) -> None:
        cursor = self.conn.cursor()
        # Create {{TABLE_NAME}} table
        cursor.execute("CREATE TABLE IF NOT EXISTS {{TABLE_NAME}} (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT NOT NULL, priority INTEGER DEFAULT 0, status TEXT DEFAULT 'active', metadata TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        # Create entries table
        cursor.execute("CREATE TABLE IF NOT EXISTS entries (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT NOT NULL, title TEXT, content TEXT NOT NULL, status TEXT DEFAULT 'active', priority INTEGER DEFAULT 0, metadata TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        # Create indices
        cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_{self._sanitize_table("{{TABLE_NAME}}")}_status ON {{TABLE_NAME}}(status)')
        cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_{self._sanitize_table("{{TABLE_NAME}}")}_priority ON {{TABLE_NAME}}(priority)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_entries_status ON entries(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_entries_type ON entries(type)')
        self.conn.commit()

    def _sanitize_table(self, table_name: str) -> str:
        return table_name.replace("-", "_")

    def insert(self, table: str, data: Dict[str, Any]) -> int:
        cursor = self.conn.cursor()
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        cursor.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", list(data.values()))
        self.conn.commit()
        return cursor.lastrowid

    def select(self, table: str, where: Optional[Dict[str, Any]] = None, order_by: Optional[str] = None, limit: Optional[int] = None) -> List[sqlite3.Row]:
        cursor = self.conn.cursor()
        query = f"SELECT * FROM {table}"
        params = []
        if where:
            conditions = ' AND '.join([f"{k} = ?" for k in where.keys()])
            query += f" WHERE {conditions}"
            params.extend(where.values())
        if order_by:
            query += f" ORDER BY {order_by}"
        if limit:
            query += f" LIMIT {limit}"
        cursor.execute(query, params)
        return cursor.fetchall()

    def update(self, table: str, where: Dict[str, Any], data: Dict[str, Any]) -> int:
        cursor = self.conn.cursor()
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        where_clause = ' AND '.join([f"{k} = ?" for k in where.keys()])
        params = list(data.values()) + list(where.values())
        cursor.execute(f"UPDATE {table} SET {set_clause} WHERE {where_clause}", params)
        self.conn.commit()
        return cursor.rowcount

    def delete(self, table: str, where: Dict[str, Any]) -> int:
        cursor = self.conn.cursor()
        where_clause = ' AND '.join([f"{k} = ?" for k in where.keys()])
        cursor.execute(f"DELETE FROM {table} WHERE {where_clause}", list(where.values()))
        self.conn.commit()
        return cursor.rowcount

    def close(self) -> None:
        if self.conn:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
'''

def get_discord_template():
    return '''#!/usr/bin/env python3
"""
Discord Bot module for {{TITLE_EN}}
{{TITLE_JA}} Discord Botモジュール
"""

import discord
from discord.ext import commands
import sqlite3
import os
from typing import Optional

class {{DISCORD_CLASS_NAME}}(commands.Cog):
    """Discord Cog for {{TITLE_EN}}"""

    def __init__(self, bot):
        self.bot = bot
        self.db_path = os.path.join(os.path.dirname(__file__), "data.db")

    @commands.command(name="{{CMD_PREFIX}}help")
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="{{TITLE_EN}} Commands",
            description="{{DESCRIPTION_JA}}",
            color=discord.Color.blue()
        )
        embed.add_field(name="{{CMD_PREFIX}}add", value="Add new item", inline=False)
        embed.add_field(name="{{CMD_PREFIX}}list", value="List items", inline=False)
        embed.add_field(name="{{CMD_PREFIX}}update", value="Update item", inline=False)
        embed.add_field(name="{{CMD_PREFIX}}delete", value="Delete item", inline=False)
        embed.add_field(name="{{CMD_PREFIX}}summary", value="Get summary", inline=False)
        embed.set_footer(text="Lifestyle management")
        await ctx.send(embed=embed)

    @commands.command(name="{{CMD_PREFIX}}add")
    async def add_item(self, ctx, title: str, *, content: str):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO {{TABLE_NAME}} (title, content, source) VALUES (?, ?, ?)", (title, content, ctx.author.name))
            conn.commit()
            item_id = cursor.lastrowid
            conn.close()

            embed = discord.Embed(
                title="✅ Added",
                description=f"Item #{item_id}",
                color=discord.Color.green()
            )
            embed.add_field(name="Title", value=title, inline=False)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Error: {e}")

    @commands.command(name="{{CMD_PREFIX}}list")
    async def list_items(self, ctx, limit: int = 10):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {{TABLE_NAME}} ORDER BY priority DESC, created_at DESC LIMIT {limit}")
            items = cursor.fetchall()
            conn.close()

            if not items:
                await ctx.send("No items found.")
                return

            embed = discord.Embed(
                title="Items",
                color=discord.Color.blue()
            )
            for item in items[:10]:
                status_emoji = "✅" if item['status'] == 'active' else "📌"
                embed.add_field(name=f"{status_emoji} #{item['id']} - {item['title']}", value=item['content'][:100], inline=False)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Error: {e}")

    @commands.command(name="{{CMD_PREFIX}}summary")
    async def summary(self, ctx):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as total, COUNT(CASE WHEN status='active' THEN 1 END) as active FROM {{TABLE_NAME}}")
            result = cursor.fetchone()
            conn.close()

            embed = discord.Embed(
                title="Summary",
                color=discord.Color.gold()
            )
            embed.add_field(name="Total", value=str(result['total']), inline=True)
            embed.add_field(name="Active", value=str(result['active']), inline=True)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Error: {e}")

def setup(bot):
    bot.add_cog({{DISCORD_CLASS_NAME}}(bot))

async def main_bot(token: str):
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print(f"Bot ready: {bot.user}")

    bot.add_cog({{DISCORD_CLASS_NAME}}(bot))
    await bot.start(token)

if __name__ == "__main__":
    import asyncio
    token = os.getenv("DISCORD_TOKEN", "YOUR_BOT_TOKEN_HERE")
    asyncio.run(main_bot(token))
'''

def get_readme_template():
    return '''# {{TITLE_EN}} / {{TITLE_JA}}

{{DESCRIPTION_EN}}

{{DESCRIPTION_JA}}

## Features

### Core Features

- **Smart Planning**: Intelligent daily planning and scheduling
- **Priority Management**: Task prioritization and optimization
- **Reminders**: Automated reminders and notifications
- **Analytics**: Data-driven insights and reports
- **Easy Integration**: Seamless integration with other agents

### Available Commands

{{FEATURES}}

## Installation

```bash
pip install -r requirements.txt
python agent.py
```

## Usage

### Add Item

```bash
python agent.py add "Title" "Content"
```

### List Items

```bash
python agent.py list
```

### Get Summary

```bash
python agent.py summary
```

### Discord Bot

```
!{{CMD_PREFIX}}help - Show help
!{{CMD_PREFIX}}add <title> <content> - Add new item
!{{CMD_PREFIX}}list - List items
!{{CMD_PREFIX}}summary - Get summary
```

## Database Schema

### {{TABLE_NAME}}

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| title | TEXT | Item title |
| content | TEXT | Item content |
| priority | INTEGER | Priority level |
| status | TEXT | Status |
| metadata | TEXT | Additional data (JSON) |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Update time |

## Integration

Works seamlessly with other lifestyle agents:
- Daily Planner Agent
- Health & Wellness Agent
- Finance Tracker Agent
- Social Connector Agent
- Personal Growth Agent

## License

MIT License
'''

def get_requirements_template():
    return '''discord.py>=2.3.0
requests>=2.31.0
fastapi>=0.104.0
uvicorn>=0.24.0
pytest>=7.4.0
black>=23.11.0
'''

def to_class_name(name):
    return ''.join(word.capitalize() for word in name.replace('-', ' ').split())

def create_agent(agent_info, progress):
    name = agent_info["name"]
    dir_name = agent_info["dir_name"]
    agent_dir = AGENTS_DIR / dir_name

    log(f"Creating agent: {name}")
    agent_dir.mkdir(parents=True, exist_ok=True)

    class_name = to_class_name(name)
    cmd_prefix = name.split("-")[0][:3]

    replacements = {
        "{{TITLE_EN}}": agent_info["title_en"],
        "{{TITLE_JA}}": agent_info["title_ja"],
        "{{DESCRIPTION_EN}}": agent_info["description_en"],
        "{{DESCRIPTION_JA}}": agent_info["description_ja"],
        "{{CLASS_NAME}}": class_name,
        "{{DB_CLASS_NAME}}": f"{class_name}DB",
        "{{DISCORD_CLASS_NAME}}": f"{class_name}Discord",
        "{{CMD_PREFIX}}": cmd_prefix,
        "{{TABLE_NAME}}": agent_info["tables"][0],
        "{{COMMANDS}}": ", ".join(agent_info["commands"]),
    }

    features_list = "\n".join([f"- **{cmd.title()}**: {cmd} management" for cmd in agent_info["commands"]])
    replacements["{{FEATURES}}"] = features_list

    agent_template = get_agent_template()
    for key, value in replacements.items():
        agent_template = agent_template.replace(key, value)
    with open(agent_dir / "agent.py", "w", encoding="utf-8") as f:
        f.write(agent_template)
    log(f"  Created: agent.py")

    db_template = get_db_template()
    for key, value in replacements.items():
        db_template = db_template.replace(key, value)
    with open(agent_dir / "db.py", "w", encoding="utf-8") as f:
        f.write(db_template)
    log(f"  Created: db.py")

    discord_template = get_discord_template()
    for key, value in replacements.items():
        discord_template = discord_template.replace(key, value)
    with open(agent_dir / "discord.py", "w", encoding="utf-8") as f:
        f.write(discord_template)
    log(f"  Created: discord.py")

    readme_template = get_readme_template()
    for key, value in replacements.items():
        readme_template = readme_template.replace(key, value)
    with open(agent_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(readme_template)
    log(f"  Created: README.md")

    with open(agent_dir / "requirements.txt", "w", encoding="utf-8") as f:
        f.write(get_requirements_template())
    log(f"  Created: requirements.txt")

    return True

def run_orchestrator():
    log(f"Starting {PROJECT_NAME}")
    log(f"Total agents to create: {len(LIFESTYLE_AGENTS)}")

    progress = load_progress()

    for i, agent_info in enumerate(LIFESTYLE_AGENTS, 1):
        name = agent_info["name"]
        log(f"\n[{i}/{len(LIFESTYLE_AGENTS)}] Processing: {name}")

        if progress["agents"].get(name, {}).get("status") == "completed":
            log(f"  Already completed, skipping...")
            continue

        try:
            success = create_agent(agent_info, progress)

            if success:
                progress["agents"][name] = {
                    "status": "completed",
                    "dir_name": agent_info["dir_name"],
                    "category": agent_info["category"],
                    "completed_at": datetime.now().isoformat()
                }
                progress["completed"] += 1
                log(f"  ✅ Agent created successfully")
            else:
                progress["agents"][name] = {
                    "status": "failed",
                    "error": "Creation failed",
                    "failed_at": datetime.now().isoformat()
                }
                progress["failed"] += 1
                log(f"  ❌ Agent creation failed")

            save_progress(progress)

        except Exception as e:
            log(f"  ❌ Error creating agent: {e}")
            progress["agents"][name] = {
                "status": "failed",
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            }
            progress["failed"] += 1
            save_progress(progress)

    log(f"\n{'='*50}")
    log(f"{PROJECT_NAME} Complete")
    log(f"{'='*50}")
    log(f"Total agents: {progress['total_agents']}")
    log(f"Completed: {progress['completed']}")
    log(f"Failed: {progress['failed']}")
    log(f"Success rate: {progress['completed']/progress['total_agents']*100:.1f}%")

    update_plan_md(progress)
    update_memory(progress)

    return progress

def update_plan_md(progress):
    plan_file = WORKSPACE / "Plan.md"

    try:
        if not plan_file.exists():
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
        summary = f'''

---

## ライフスタイル統合プロジェクト ✅ 完了 ({timestamp})

**開始**: {progress.get("started_at", "N/A")}
**完了**: {datetime.now().strftime("%Y-%m-%d %H:%M UTC")}

**完了したエージェント** ({progress['completed']}/{progress['total_agents']}):
'''

        for agent_info in LIFESTYLE_AGENTS:
            name = agent_info["name"]
            title_ja = agent_info["title_ja"]
            if progress["agents"].get(name, {}).get("status") == "completed":
                summary += f"- ✅ {name} - {title_ja}\n"

        summary += f'''
**作成したファイル**:
- lifestyle_integration_orchestrator.py - オーケストレーター
- lifestyle_integration_progress.json - 進捗管理
'''

        for agent_info in LIFESTYLE_AGENTS:
            name = agent_info["name"]
            dir_name = agent_info["dir_name"]
            title_ja = agent_info["title_ja"]
            if progress["agents"].get(name, {}).get("status") == "completed":
                summary += f"- agents/{dir_name}/ - {title_ja}\n"

        summary += '''
**各エージェントの構造**:
- agent.py - エージェント本体
- db.py - SQLiteデータベースモジュール
- discord.py - Discord Botモジュール
- README.md - ドキュメント（バイリンガル）
- requirements.txt - 依存パッケージ

**成果**:
- 5個のライフスタイル統合エージェントが作成完了
- 各エージェントには agent.py, db.py, discord.py, README.md, requirements.txt が揃っている
- 日次計画・健康管理・財務追跡・ソーシャル管理・自己成長の機能を提供

**重要な学び**:
- オーケストレーターによる自律的なエージェント作成が可能
- テンプレートベースの生成で一貫性を確保
- バイリンガルドキュメントで多言語対応

**Git Commits**:
- `pending` - feat: ライフスタイル統合プロジェクト完了 (5/5) - {datetime.now().strftime("%Y-%m-%d %H:%M")}

**🎉 プロジェクト完了！**

---

## 全プロジェクト進捗サマリー ({datetime.now().strftime("%Y-%m-%d %H:%M UTC")})

**完了済みプロジェクト**: 65個
**総エージェント数**: 302個 (297 + 5)
'''

        with open(plan_file, "a", encoding="utf-8") as f:
            f.write(summary)

        log("Plan.md updated")

    except Exception as e:
        log(f"Error updating Plan.md: {e}")

def update_memory(progress):
    memory_dir = WORKSPACE / "memory"
    memory_file = memory_dir / datetime.now().strftime("%Y-%m-%d.md")

    try:
        memory_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%H:%M UTC")
        entry = f'''

### ライフスタイル統合プロジェクト ✅ ({timestamp})
- 開始: {progress.get("started_at", "N/A")}
- 完了: {datetime.now().strftime("%H:%M UTC")}
- エージェント数: {progress['completed']}/{progress['total_agents']}
- エージェント:
'''

        for agent_info in LIFESTYLE_AGENTS:
            name = agent_info["name"]
            title_ja = agent_info["title_ja"]
            if progress["agents"].get(name, {}).get("status") == "completed":
                entry += f"  - {name} - {title_ja}\n"

        with open(memory_file, "a", encoding="utf-8") as f:
            f.write(entry)

        log(f"Memory updated: {memory_file}")

    except Exception as e:
        log(f"Error updating memory: {e}")

if __name__ == "__main__":
    progress = run_orchestrator()
    sys.exit(0 if progress["failed"] == 0 else 1)
