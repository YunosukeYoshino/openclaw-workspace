#!/usr/bin/env python3
"""
Baseball Additional Agents Orchestrator
野球追加エージェントオーケストレーター
"""

import os
import subprocess
import json
import time
from pathlib import Path

PROJECT_NAME = "baseball-additional-agents"
AGENTS = [
    {
        "name": "baseball-highlights-agent",
        "title": "Baseball Highlights Video Agent",
        "title_ja": "野球ハイライト映像管理エージェント",
        "description": "Manage baseball game highlight videos and clips",
        "description_ja": "野球試合のハイライト映像・クリップを管理するエージェント",
        "tables": ["highlights", "clips", "video_sources"]
    },
    {
        "name": "baseball-podcast-agent",
        "title": "Baseball Podcast Agent",
        "title_ja": "野球ポッドキャスト・音声コンテンツ収集エージェント",
        "description": "Collect and manage baseball podcasts and audio content",
        "description_ja": "野球ポッドキャスト・音声コンテンツを収集・管理するエージェント",
        "tables": ["podcasts", "episodes", "audio_sources"]
    },
    {
        "name": "baseball-trivia-agent",
        "title": "Baseball Trivia Agent",
        "title_ja": "野球クイズ・雑学エージェント",
        "description": "Manage baseball trivia, quizzes, and fun facts",
        "description_ja": "野球クイズ・雑学・面白い事実を管理するエージェント",
        "tables": ["trivia", "quizzes", "fun_facts"]
    }
]

PROGRESS_FILE = "/workspace/baseball_addition_progress.json"

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {"completed": [], "failed": [], "total": len(AGENTS)}

def save_progress(progress):
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

def create_agent_dir(agent_name):
    agent_dir = f"/workspace/agents/{agent_name}"
    os.makedirs(agent_dir, exist_ok=True)
    return agent_dir

def generate_db_tables(tables):
    """Generate SQLite table creation statements"""
    table_defs = ""
    for table in tables:
        table_defs += f"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS {table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        """
    return table_defs

def create_agent_py(agent_name, tables, description, description_ja):
    template = f'''#!/usr/bin/env python3
"""
{agent_name.replace('-', ' ').title().replace(' ', '')} Agent
{description_ja}
"""

import sqlite3
import os
from datetime import datetime

class {agent_name.replace('-', '_').title().replace('_', '')}Agent:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), "data.db")
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize the SQLite database with tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
{generate_db_tables(tables)}
        conn.commit()
        conn.close()
        print(f"Database initialized: {{self.db_path}}")

    def add_entry(self, data):
        """Add a new entry."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # TODO: Implement based on actual schema
        conn.commit()
        conn.close()

    def get_entries(self, limit=None):
        """Get all entries."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM {tables[0]} ORDER BY created_at DESC")
        entries = cursor.fetchall()
        conn.close()
        return entries[:limit] if limit else entries

if __name__ == "__main__":
    agent = {agent_name.replace('-', '_').title().replace('_', '')}Agent()
    print(f"{agent_name.replace('-', ' ').title()} Agent initialized")
'''
    return template

def create_db_py(agent_name, tables):
    template = f'''#!/usr/bin/env python3
"""
Database module for {agent_name}
"""

import sqlite3
import os

class Database:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), "data.db")
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
{generate_db_tables(tables)}
        conn.commit()
        conn.close()

    def get_connection(self):
        """Get a database connection."""
        return sqlite3.connect(self.db_path)

if __name__ == "__main__":
    db = Database()
    print(f"Database initialized: {{db.db_path}}")
'''
    return template

def create_discord_py(agent_name, title, title_ja):
    template = f'''#!/usr/bin/env python3
"""
Discord Bot module for {agent_name}
"""

import discord
from discord.ext import commands
import os

class {agent_name.replace('-', '_').title().replace('_', '')}Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(*args, intents=intents, **kwargs)

    async def setup_hook(self):
        """Load cogs."""
        # Load cogs here
        pass

@bot.event
async def on_ready():
    print(f'{{bot.user}} has connected to Discord!')

@bot.command(name='info')
async def info(ctx):
    """Show bot information."""
    await ctx.send(f"{title_ja} - {title}")

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("DISCORD_TOKEN environment variable not set")
        exit(1)
    bot.run(token)
'''
    return template

def create_readme_md(agent_name, title, title_ja, description, description_ja):
    template = f'''# {agent_name}

{title} / {title_ja}

{description}

## Description (Japanese)

{description_ja}

## Installation

```bash
cd {agent_name}
pip install -r requirements.txt
```

## Usage

```bash
python agent.py
```

## Features

- SQLite database for data storage
- Discord bot integration
- RESTful API endpoints (planned)

## License

MIT License
'''
    return template

def create_requirements_txt():
    return '''discord.py>=2.3.0
aiohttp>=3.9.0
'''

def spawn_subagent(agent_name, title, title_ja, description, description_ja, tables):
    """Spawn a subagent to create the agent files."""
    agent_dir = create_agent_dir(agent_name)

    # Create files directly
    agent_py = create_agent_py(agent_name, tables, description, description_ja)
    db_py = create_db_py(agent_name, tables)
    discord_py = create_discord_py(agent_name, title, title_ja)
    readme_md = create_readme_md(agent_name, title, title_ja, description, description_ja)
    requirements_txt = create_requirements_txt()

    with open(f"{agent_dir}/agent.py", 'w') as f:
        f.write(agent_py)
    with open(f"{agent_dir}/db.py", 'w') as f:
        f.write(db_py)
    with open(f"{agent_dir}/discord.py", 'w') as f:
        f.write(discord_py)
    with open(f"{agent_dir}/README.md", 'w') as f:
        f.write(readme_md)
    with open(f"{agent_dir}/requirements.txt", 'w') as f:
        f.write(requirements_txt)

    print(f"✅ Created {agent_name} ({title_ja})")
    return True

def main():
    print("=" * 60)
    print("Baseball Additional Agents Orchestrator")
    print("野球追加エージェントオーケストレーター")
    print("=" * 60)
    print(f"Total agents to create: {len(AGENTS)}")

    progress = load_progress()
    print(f"Progress: {len(progress['completed'])}/{progress['total']} completed")

    for agent in AGENTS:
        agent_name = agent["name"]

        # Skip if already completed
        if agent_name in progress["completed"]:
            print(f"⊘ Skipping {agent_name} (already completed)")
            continue

        print(f"\n🚀 Creating {agent_name}...")

        try:
            spawn_subagent(
                agent_name=agent_name,
                title=agent["title"],
                title_ja=agent["title_ja"],
                description=agent["description"],
                description_ja=agent["description_ja"],
                tables=agent["tables"]
            )

            progress["completed"].append(agent_name)
            save_progress(progress)

            print(f"✅ {agent_name} completed successfully")

        except Exception as e:
            print(f"❌ {agent_name} failed: {e}")
            progress["failed"].append({"name": agent_name, "error": str(e)})
            save_progress(progress)

    print("\n" + "=" * 60)
    print("Orchestration Complete!")
    print("=" * 60)
    print(f"Completed: {len(progress['completed'])}/{progress['total']}")
    print(f"Failed: {len(progress['failed'])}")

    if progress["failed"]:
        print("\nFailed agents:")
        for failed in progress["failed"]:
            print(f"  - {failed['name']}: {failed['error']}")

if __name__ == "__main__":
    main()
