#!/usr/bin/env python3
"""
クロスカテゴリエージェント補完オーケストレーター

不完全なcross-categoryエージェントを補完する。
"""

import os
import json
import time
from pathlib import Path

# 補完が必要なエージェントリスト
AGENTS_TO_COMPLETE = [
    "cross-category-analytics-agent",
    "cross-category-recommendation-agent",
    "cross-category-search-agent",
    "cross-category-sync-agent",
    "cross-category-trend-agent",
]

# テンプレートディレクトリ
AGENTS_DIR = Path("/workspace/agents")
PROGRESS_FILE = Path("/workspace/cross_category_completion_progress.json")

def load_progress():
    """進捗の読み込み"""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "completed": [],
        "failed": [],
        "total": len(AGENTS_TO_COMPLETE),
        "completed_count": 0,
        "failed_count": 0,
    }

def save_progress(progress):
    """進捗の保存"""
    progress["completed_count"] = len(progress["completed"])
    progress["failed_count"] = len(progress["failed"])
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)

def generate_db_py(agent_name):
    """db.pyの生成"""
    return f'''# db.py - Database Module for {agent_name}
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any

DB_PATH = Path(__file__).parent / f"{{agent_name}}.db"

class Database:
    """Database handler for {agent_name}"""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.conn = None
        self._init_db()

    def _init_db(self):
        """Initialize database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        """Create database tables"""
        cursor = self.conn.cursor()

        # Main data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                title TEXT,
                content TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                priority INTEGER DEFAULT 0,
                tags TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Relations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id INTEGER NOT NULL,
                target_id INTEGER NOT NULL,
                relation_type TEXT NOT NULL,
                strength REAL DEFAULT 1.0,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_id) REFERENCES entries(id),
                FOREIGN KEY (target_id) REFERENCES entries(id)
            )
        ''')

        # Analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_id INTEGER NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (entry_id) REFERENCES entries(id)
            )
        ''')

        self.conn.commit()

    def add_entry(
        self,
        entry_type: str,
        content: str,
        title: Optional[str] = None,
        status: str = "active",
        priority: int = 0,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Add a new entry"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO entries (type, title, content, status, priority, tags, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            entry_type,
            title,
            content,
            status,
            priority,
            json.dumps(tags) if tags else None,
            json.dumps(metadata) if metadata else None,
        ))
        self.conn.commit()
        return cursor.lastrowid

    def get_entry(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """Get entry by ID"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM entries WHERE id = ?', (entry_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def get_entries(
        self,
        entry_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Get entries with filters"""
        query = "SELECT * FROM entries WHERE 1=1"
        params = []

        if entry_type:
            query += " AND type = ?"
            params.append(entry_type)

        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def update_entry(
        self,
        entry_id: int,
        **kwargs
    ) -> bool:
        """Update entry"""
        allowed_fields = ['type', 'title', 'content', 'status', 'priority', 'tags', 'metadata']
        updates = []
        params = []

        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f"{{field}} = ?")
                if field in ['tags', 'metadata']:
                    params.append(json.dumps(value) if value else None)
                else:
                    params.append(value)

        if not updates:
            return False

        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(entry_id)

        cursor = self.conn.cursor()
        cursor.execute(f'''
            UPDATE entries
            SET {{', '.join(updates)}}
            WHERE id = ?
        ''', params)
        self.conn.commit()
        return cursor.rowcount > 0

    def delete_entry(self, entry_id: int) -> bool:
        """Delete entry"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM entries WHERE id = ?', (entry_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def add_relation(
        self,
        source_id: int,
        target_id: int,
        relation_type: str,
        strength: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Add relation between entries"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO relations (source_id, target_id, relation_type, strength, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (source_id, target_id, relation_type, strength, json.dumps(metadata) if metadata else None))
        self.conn.commit()
        return cursor.lastrowid

    def get_relations(
        self,
        entry_id: int,
        relation_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get relations for entry"""
        query = '''
            SELECT r.*,
                   s.title as source_title,
                   t.title as target_title
            FROM relations r
            LEFT JOIN entries s ON r.source_id = s.id
            LEFT JOIN entries t ON r.target_id = t.id
            WHERE r.source_id = ? OR r.target_id = ?
        '''
        params = [entry_id, entry_id]

        if relation_type:
            query += " AND r.relation_type = ?"
            params.append(relation_type)

        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def add_analytics(
        self,
        entry_id: int,
        metric_name: str,
        metric_value: float,
    ) -> int:
        """Add analytics data"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO analytics (entry_id, metric_name, metric_value)
            VALUES (?, ?, ?)
        ''', (entry_id, metric_name, metric_value))
        self.conn.commit()
        return cursor.lastrowid

    def get_analytics(
        self,
        entry_id: Optional[int] = None,
        metric_name: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get analytics data"""
        query = "SELECT * FROM analytics WHERE 1=1"
        params = []

        if entry_id:
            query += " AND entry_id = ?"
            params.append(entry_id)

        if metric_name:
            query += " AND metric_name = ?"
            params.append(metric_name)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def search(
        self,
        query: str,
        entry_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Search entries"""
        sql = "SELECT * FROM entries WHERE (title LIKE ? OR content LIKE ? OR tags LIKE ?)"
        params = [f"%{{query}}%", f"%{{query}}%", f"%{{query}}%"]

        if entry_type:
            sql += " AND type = ?"
            params.append(entry_type)

        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        cursor = self.conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM entries")
        total_entries = cursor.fetchone()[0]

        cursor.execute("SELECT type, COUNT(*) FROM entries GROUP BY type")
        by_type = dict(cursor.fetchall())

        cursor.execute("SELECT status, COUNT(*) FROM entries GROUP BY status")
        by_status = dict(cursor.fetchall())

        return {{
            "total_entries": total_entries,
            "by_type": by_type,
            "by_status": by_status,
        }}

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
'''

def generate_discord_py(agent_name):
    """discord.pyの生成"""
    return f'''# discord.py - Discord Bot Module for {agent_name}
import discord
from discord.ext import commands
from pathlib import Path
import json
from typing import Optional, List
import asyncio

from db import Database

# Configuration
INTENTS = discord.Intents.default()
INTENTS.message_content = True
INTENTS.guilds = True

class {agent_name.replace("-", " ").title().replace(" ", "")}Bot(commands.Bot):
    """Discord bot for {agent_name}"""

    def __init__(self, db: Database, command_prefix: str = "!"):
        super().__init__(
            command_prefix=command_prefix,
            intents=INTENTS,
            help_command=None,
        )
        self.db = db

    async def setup_hook(self):
        """Setup hook for bot initialization"""
        print(f"Bot is setting up...")
        # Load cogs if needed
        await self.load_extension(f"cogs.commands")

    async def on_ready(self):
        """Called when bot is ready"""
        print(f"Logged in as {{self.user}} (ID: {{self.user.id}})")
        print(f"Connected to {{len(self.guilds)}} guilds")

    async def on_command_error(self, ctx: commands.Context, error: Exception):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            return
        await ctx.send(f"Error: {{error}}")

# Helper functions
def create_embed(
    title: str,
    description: Optional[str] = None,
    color: int = discord.Color.blue(),
    fields: Optional[List[tuple]] = None,
) -> discord.Embed:
    """Create a Discord embed"""
    embed = discord.Embed(title=title, description=description, color=color)
    if fields:
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
    return embed

async def send_paginated_list(
    ctx: commands.Context,
    items: List[dict],
    title: str,
    format_func,
    per_page: int = 10,
):
    """Send paginated list of items"""
    if not items:
        await ctx.send("No items found.")
        return

    pages = []
    for i in range(0, len(items), per_page):
        page_items = items[i:i + per_page]
        description = "\\n".join([format_func(item) for item in page_items])
        embed = create_embed(
            title=f"{{title}} ({{i // per_page + 1}}/{{(len(items) - 1) // per_page + 1}})",
            description=description,
        )
        pages.append(embed)

    if len(pages) == 1:
        await ctx.send(embed=pages[0])
        return

    # Simple pagination with reactions
    current_page = 0
    message = await ctx.send(embed=pages[current_page])

    for reaction in ["◀️", "▶️", "❌"]:
        await message.add_reaction(reaction)

    def check(reaction, user):
        return (
            user == ctx.author
            and reaction.message == message
            and str(reaction.emoji) in ["◀️", "▶️", "❌"]
        )

    while True:
        try:
            reaction, user = await self.wait_for("reaction_add", check=check, timeout=60)

            if str(reaction.emoji) == "◀️" and current_page > 0:
                current_page -= 1
                await message.edit(embed=pages[current_page])
            elif str(reaction.emoji) == "▶️" and current_page < len(pages) - 1:
                current_page += 1
                await message.edit(embed=pages[current_page])
            elif str(reaction.emoji) == "❌":
                await message.delete()
                break

            await message.remove_reaction(reaction, user)

        except asyncio.TimeoutError:
            await message.clear_reactions()
            break

# Commands
async def command_add(
    ctx: commands.Context,
    entry_type: str,
    content: str,
    title: Optional[str] = None,
    priority: int = 0,
    tags: Optional[str] = None,
):
    """Add a new entry"""
    tag_list = tags.split(",") if tags else None
    entry_id = ctx.bot.db.add_entry(
        entry_type=entry_type,
        content=content,
        title=title,
        priority=priority,
        tags=tag_list,
    )
    embed = create_embed(
        title="✅ Entry Added",
        description=f"Entry ID: {{entry_id}}",
        color=discord.Color.green(),
        fields=[
            ("Type", entry_type, True),
            ("Title", title or "N/A", True),
            ("Priority", str(priority), True),
        ],
    )
    await ctx.send(embed=embed)

async def command_list(
    ctx: commands.Context,
    entry_type: Optional[str] = None,
    status: str = "active",
    limit: int = 20,
):
    """List entries"""
    entries = ctx.bot.db.get_entries(
        entry_type=entry_type,
        status=status,
        limit=limit,
    )

    if not entries:
        await ctx.send("No entries found.")
        return

    def format_entry(entry):
        return f"**{{entry['id']}}.** {{entry.get('title', 'Untitled')}} ({{entry['type']}})"

    await send_paginated_list(
        ctx,
        entries,
        f"Entries ({entry_type or 'All'})",
        format_entry,
        per_page=10,
    )

async def command_search(
    ctx: commands.Context,
    query: str,
    entry_type: Optional[str] = None,
):
    """Search entries"""
    results = ctx.bot.db.search(query=query, entry_type=entry_type, limit=20)

    if not results:
        await ctx.send(f"No results found for '{{query}}'.")
        return

    def format_result(result):
        return f"**{{result['id']}}.** {{result.get('title', 'Untitled')}}"

    await send_paginated_list(
        ctx,
        results,
        f"Search Results for '{{query}}'",
        format_result,
        per_page=10,
    )

async def command_stats(ctx: commands.Context):
    """Show database statistics"""
    stats = ctx.bot.db.get_stats()

    embed = create_embed(
        title="📊 Database Statistics",
        color=discord.Color.blue(),
        fields=[
            ("Total Entries", str(stats['total_entries']), True),
            ("Active", str(stats['by_status'].get('active', 0)), True),
            ("Archived", str(stats['by_status'].get('archived', 0)), True),
        ],
    )

    # Add type breakdown
    type_text = "\\n".join([f"• **{{k}}**: {{v}}" for k, v in stats['by_type'].items()])
    embed.add_field(name="By Type", value=type_text or "None", inline=False)

    await ctx.send(embed=embed)

async def command_relation(
    ctx: commands.Context,
    source_id: int,
    target_id: int,
    relation_type: str,
    strength: float = 1.0,
):
    """Add relation between entries"""
    relation_id = ctx.bot.db.add_relation(
        source_id=source_id,
        target_id=target_id,
        relation_type=relation_type,
        strength=strength,
    )
    embed = create_embed(
        title="🔗 Relation Added",
        description=f"Relation ID: {{relation_id}}",
        color=discord.Color.purple(),
        fields=[
            ("Source", str(source_id), True),
            ("Target", str(target_id), True),
            ("Type", relation_type, True),
            ("Strength", str(strength), True),
        ],
    )
    await ctx.send(embed=embed)

async def command_analytics(
    ctx: commands.Context,
    entry_id: int,
    metric_name: str,
    metric_value: float,
):
    """Add analytics data"""
    analytics_id = ctx.bot.db.add_analytics(
        entry_id=entry_id,
        metric_name=metric_name,
        metric_value=metric_value,
    )
    embed = create_embed(
        title="📈 Analytics Added",
        description=f"Analytics ID: {{analytics_id}}",
        color=discord.Color.orange(),
        fields=[
            ("Entry ID", str(entry_id), True),
            ("Metric", metric_name, True),
            ("Value", str(metric_value), True),
        ],
    )
    await ctx.send(embed=embed)

async def command_get_analytics(
    ctx: commands.Context,
    entry_id: Optional[int] = None,
    metric_name: Optional[str] = None,
):
    """Get analytics data"""
    analytics = ctx.bot.db.get_analytics(
        entry_id=entry_id,
        metric_name=metric_name,
        limit=50,
    )

    if not analytics:
        await ctx.send("No analytics data found.")
        return

    def format_analytics(a):
        return f"**{{a['entry_id']}}.** {{a['metric_name']}} = {{a['metric_value']}} ({{a['timestamp']}})"

    await send_paginated_list(
        ctx,
        analytics,
        "Analytics Data",
        format_analytics,
        per_page=10,
    )

async def command_relations(
    ctx: commands.Context,
    entry_id: int,
    relation_type: Optional[str] = None,
):
    """Get relations for entry"""
    relations = ctx.bot.db.get_relations(
        entry_id=entry_id,
        relation_type=relation_type,
    )

    if not relations:
        await ctx.send(f"No relations found for entry {{entry_id}}.")
        return

    def format_relation(r):
        direction = "→" if r['source_id'] == entry_id else "←"
        return f"**{{r['id']}}.** {{r['source_title'] or r['source_id']}} {{direction}} {{r['target_title'] or r['target_id']}} ({{r['relation_type']}})"

    await send_paginated_list(
        ctx,
        relations,
        f"Relations for Entry {{entry_id}}",
        format_relation,
        per_page=10,
    )
'''

def generate_readme_md(agent_name):
    """README.mdの生成"""
    return f'''# {agent_name}

A cross-category analysis and integration agent for managing cross-domain data and relationships.

## Features

- **Entry Management**: Store and manage cross-category entries
- **Relation Tracking**: Track relationships between entries
- **Analytics**: Collect and analyze metrics
- **Search**: Full-text search across all entries
- **Statistics**: Database statistics and reporting

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Python API

```python
from db import Database

# Initialize database
db = Database()

# Add an entry
entry_id = db.add_entry(
    entry_type="article",
    title="Sample Article",
    content="This is a sample article content.",
    tags=["tag1", "tag2"],
    priority=1,
)

# Add a relation
relation_id = db.add_relation(
    source_id=entry_id,
    target_id=other_id,
    relation_type="related_to",
    strength=0.8,
)

# Add analytics
db.add_analytics(
    entry_id=entry_id,
    metric_name="views",
    metric_value=100,
)

# Search
results = db.search("sample")
```

### Discord Bot

```python
from discord_bot import {agent_name.replace("-", " ").title().replace(" ", "")}Bot
from db import Database

db = Database()
bot = {agent_name.replace("-", " ").title().replace(" ", "")}Bot(db)

# Run bot
bot.run("YOUR_BOT_TOKEN")
```

## Discord Commands

- `!add <type> <content> [title] [priority] [tags]` - Add new entry
- `!list [type] [status] [limit]` - List entries
- `!search <query> [type]` - Search entries
- `!stats` - Show database statistics
- `!relation <source_id> <target_id> <type> [strength]` - Add relation
- `!relations <entry_id> [type]` - Get relations for entry
- `!analytics <entry_id> <metric> <value>` - Add analytics data
- `!get_analytics [entry_id] [metric]` - Get analytics data

## Database Schema

### entries
- id: Primary key
- type: Entry type (e.g., article, project, idea)
- title: Entry title
- content: Entry content
- status: Status (active, archived, completed)
- priority: Priority level (0-10)
- tags: JSON array of tags
- metadata: JSON metadata
- created_at: Creation timestamp
- updated_at: Update timestamp

### relations
- id: Primary key
- source_id: Source entry ID
- target_id: Target entry ID
- relation_type: Type of relation
- strength: Relation strength (0.0-1.0)
- metadata: JSON metadata
- created_at: Creation timestamp

### analytics
- id: Primary key
- entry_id: Related entry ID
- metric_name: Name of metric
- metric_value: Value of metric
- timestamp: Measurement timestamp

## Configuration

Set environment variables:

```bash
export DISCORD_BOT_TOKEN="your_bot_token_here"
```

## License

MIT License
'''

def generate_requirements_txt():
    """requirements.txtの生成"""
    return '''discord.py>=2.3.0
python-dotenv>=1.0.0
'''

def complete_agent(agent_name: str) -> bool:
    """エージェントを補完"""
    agent_dir = AGENTS_DIR / agent_name

    if not agent_dir.exists():
        print(f"❌ Agent directory not found: {{agent_name}}")
        return False

    # 既存のファイル確認
    existing_files = set(os.listdir(agent_dir))
    needed_files = {"db.py", "discord.py", "README.md", "requirements.txt"}
    missing_files = needed_files - existing_files

    if not missing_files:
        print(f"✅ {agent_name} is already complete")
        return True

    print(f"🔧 Completing {agent_name}... Missing: {missing_files}")

    try:
        if "db.py" in missing_files:
            with open(agent_dir / "db.py", "w", encoding="utf-8") as f:
                f.write(generate_db_py(agent_name))
            print(f"  ✅ Created db.py")

        if "discord.py" in missing_files:
            with open(agent_dir / "discord.py", "w", encoding="utf-8") as f:
                f.write(generate_discord_py(agent_name))
            print(f"  ✅ Created discord.py")

        if "README.md" in missing_files:
            with open(agent_dir / "README.md", "w", encoding="utf-8") as f:
                f.write(generate_readme_md(agent_name))
            print(f"  ✅ Created README.md")

        if "requirements.txt" in missing_files:
            with open(agent_dir / "requirements.txt", "w", encoding="utf-8") as f:
                f.write(generate_requirements_txt())
            print(f"  ✅ Created requirements.txt")

        print(f"✅ {agent_name} completed successfully")
        return True

    except Exception as e:
        print(f"❌ Error completing {agent_name}: {e}")
        return False

def main():
    """メイン関数"""
    print("🚀 Cross-Category Agent Completion Orchestrator")
    print("=" * 50)

    progress = load_progress()
    completed = progress.get("completed", [])
    failed = progress.get("failed", [])

    for agent_name in AGENTS_TO_COMPLETE:
        if agent_name in completed:
            print(f"⏭️  {agent_name} already completed, skipping...")
            continue

        if agent_name in failed:
            print(f"🔄 {agent_name} previously failed, retrying...")

        if complete_agent(agent_name):
            completed.append(agent_name)
            if agent_name in failed:
                failed.remove(agent_name)
        else:
            failed.append(agent_name)

        progress["completed"] = completed
        progress["failed"] = failed
        save_progress(progress)
        print()

    print("=" * 50)
    print(f"📊 Completion Summary:")
    print(f"  Total: {progress['total']}")
    print(f"  Completed: {progress['completed_count']}")
    print(f"  Failed: {progress['failed_count']}")
    print(f"  Success Rate: {progress['completed_count'] / progress['total'] * 100:.1f}%")

if __name__ == "__main__":
    main()
'''
