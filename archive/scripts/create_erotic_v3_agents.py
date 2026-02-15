#!/usr/bin/env python3
"""
エロティックコンテンツ追加エージェントV3 - 一括作成スクリプト
"""

import os
from pathlib import Path

# エージェント定義
AGENTS = {
    "erotic-rating-agent": {
        "name_en": "Erotic Content Rating & Review Agent",
        "name_ja": "えっちコンテンツ評価レビューエージェント",
        "desc_en": "An agent that manages ratings and reviews for erotic content",
        "desc_ja": "えっちなコンテンツの評価・レビューを管理するエージェント",
        "db_tables": {
            "reviews": """
                CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_id TEXT NOT NULL,
                    content_title TEXT,
                    artist TEXT,
                    rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 10),
                    review_text TEXT,
                    tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
        }
    },
    "erotic-bookmark-agent": {
        "name_en": "Erotic Content Bookmark Agent",
        "name_ja": "えっちコンテンツブックマークエージェント",
        "desc_en": "An agent that manages bookmarks for erotic content",
        "desc_ja": "えっちなコンテンツのブックマークを管理するエージェント",
        "db_tables": {
            "bookmarks": """
                CREATE TABLE IF NOT EXISTS bookmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL UNIQUE,
                    title TEXT,
                    description TEXT,
                    tags TEXT,
                    category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TIMESTAMP
                )
            """
        }
    },
    "erotic-history-agent": {
        "name_en": "Erotic Content History Tracking Agent",
        "name_ja": "えっちコンテンツ閲覧履歴エージェント",
        "desc_en": "An agent that tracks and manages viewing history of erotic content",
        "desc_ja": "えっちなコンテンツの閲覧履歴を追跡・管理するエージェント",
        "db_tables": {
            "history": """
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_id TEXT NOT NULL,
                    content_title TEXT,
                    artist TEXT,
                    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tags TEXT,
                    source TEXT
                )
            """
        }
    },
    "erotic-search-agent": {
        "name_en": "Erotic Content Advanced Search Agent",
        "name_ja": "えっちコンテンツ高度検索エージェント",
        "desc_en": "An agent that provides advanced search functionality for erotic content",
        "desc_ja": "えっちなコンテンツの高度な検索機能を提供するエージェント",
        "db_tables": {
            "search_index": """
                CREATE TABLE IF NOT EXISTS search_index (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_id TEXT NOT NULL UNIQUE,
                    title TEXT,
                    artist TEXT,
                    tags TEXT,
                    description TEXT,
                    source TEXT,
                    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            "search_queries": """
                CREATE TABLE IF NOT EXISTS search_queries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    results_count INTEGER,
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
        }
    }
}

def _get_table_creations(db_tables):
    """Generate table creation code"""
    code_lines = []
    for table_name, table_sql in db_tables.items():
        code_lines.append(f"        # {table_name}テーブル")
        code_lines.append(f'        self.conn.execute("""')
        code_lines.append(f"            {table_sql.strip()}")
        code_lines.append(f'        """)')
        code_lines.append("")
    return "\\n".join(code_lines)

def create_agent_py(agent_name, agent_info):
    """Create agent.py file"""
    class_name = "".join(word.capitalize() for word in agent_name.split("-"))
    tables_code = _get_table_creations(agent_info["db_tables"])
    content = f'''#!/usr/bin/env python3
"""
{agent_info["name_en"]}

{agent_info["desc_en"]}
"""

import sqlite3
from datetime import datetime
from pathlib import Path

class {class_name}:
    """{agent_info["name_ja"]}"""

    def __init__(self, db_path: str = None):
        """初期化"""
        self.db_path = db_path or Path(__file__).parent / "{agent_name}.db"
        self.conn = None
        self._init_db()

    def _init_db(self):
        """データベース初期化"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

        # テーブル作成
{tables_code}
        self.conn.commit()

    def get_info(self):
        """エージェント情報取得"""
        return {{
            "name": "{agent_name}",
            "name_en": "{agent_info["name_en"]}",
            "name_ja": "{agent_info["name_ja"]}",
            "description_en": "{agent_info["desc_en"]}",
            "description_ja": "{agent_info["desc_ja"]}",
        }}

    def close(self):
        """接続終了"""
        if self.conn:
            self.conn.close()

    def __del__(self):
        """デストラクタ"""
        self.close()

if __name__ == "__main__":
    agent = {class_name}()
    print(agent.get_info())
'''
    return content

def _get_table_creations(db_tables):
    """Generate table creation code"""
    code_lines = []
    for table_name, table_sql in db_tables.items():
        code_lines.append(f"        # {table_name}テーブル")
        code_lines.append(f'        self.conn.execute("""')
        code_lines.append(f"            {table_sql.strip()}")
        code_lines.append(f'        """)')
        code_lines.append("")
    return "\\n".join(code_lines)

def create_db_py(agent_name, agent_info):
    """Create db.py file"""
    tables_code = []
    for table_name, table_sql in agent_info["db_tables"].items():
        tables_code.append(f'        "{table_name}": """')
        tables_code.append(f"            {table_sql.strip()}")
        tables_code.append(f'        """')

    tables_str = "\\n".join(tables_code)

    content = f'''"""
{agent_info["name_en"]} - Database Module
"""

import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def initialize(self):
        """Initialize database with all required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 各テーブルを作成
            {tables_str}

            conn.commit()
            print("Database initialized successfully")

    def execute_query(self, query: str, params: tuple = ()):
        """Execute a SQL query"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor

    def fetch_all(self, query: str, params: tuple = ()):
        """Fetch all results from a query"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def fetch_one(self, query: str, params: tuple = ()):
        """Fetch one result from a query"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            return dict(result) if result else None
'''
    return content

def create_discord_py(agent_name, agent_info):
    """Create discord.py file"""
    class_name = "".join(word.capitalize() for word in agent_name.split("-"))
    content = f'''"""
{agent_info["name_en"]} - Discord Bot Module
"""

import discord
from discord.ext import commands
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from db import Database

class {class_name}Bot(commands.Bot):
    def __init__(self, command_prefix="!", db_path=None):
        intents = discord.Intents.default()
        intents.message_content = True

        if db_path is None:
            db_path = Path(__file__).parent / "{agent_name}.db"

        super().__init__(command_prefix=command_prefix, intents=intents)
        self.db_path = db_path
        self.db = Database(str(db_path))

    async def setup_hook(self):
        """Setup database when bot starts"""
        self.db.initialize()

    async def on_ready(self):
        print(f"{{self.user.name}} is online!")

    async def help_command(self, ctx):
        """Show help message"""
        help_text = f"""
**{agent_info["name_en"]}**

{agent_info["desc_en"]}

Commands:
- !info - Show agent information
- !help - Show this help message
"""
        await ctx.send(help_text)

    async def info_command(self, ctx):
        """Show agent information"""
        info = f"""
**{agent_info["name_en"]} / {agent_info["name_ja"]}**

{agent_info["desc_ja"]}

Description (EN):
{agent_info["desc_en"]}
"""
        await ctx.send(info)

# コマンド登録用
def setup(bot):
    """Setup function for the bot"""
    if not hasattr(bot, "add_listener"):
        print("Warning: bot.add_listener not available, running standalone")
        return

    async def on_message(message):
        if message.author.bot:
            return

        if message.content.startswith("!info"):
            info_text = f"""
**{agent_info["name_en"]} / {agent_info["name_ja"]}**

{agent_info["desc_ja"]}
"""
            await message.channel.send(info_text)
        elif message.content.startswith("!help"):
            help_text = f"""
**{agent_info["name_en"]}**

{agent_info["desc_en"]}

Commands:
- !info - Show agent information
- !help - Show this help message
"""
            await message.channel.send(help_text)

    bot.add_listener(on_message, "on_message")
'''
    return content

def create_readme_md(agent_name, agent_info):
    """Create README.md file"""
    content = f'''# {agent_name}

## {agent_info["name_en"]}

{agent_info["desc_en"]}

---

## {agent_info["name_ja"]}

{agent_info["desc_ja"]}

---

## Features

### Features in English

- Database management with SQLite
- Discord bot integration
- Bilingual support (Japanese/English)

### 機能一覧

- SQLiteによるデータベース管理
- Discordボットとの統合
- バイリンガル対応(日本語・英語)

---

## Installation

### Installation in English

```bash
cd /workspace/agents/{agent_name}
pip install -r requirements.txt
```

### インストール方法

```bash
cd /workspace/agents/{agent_name}
pip install -r requirements.txt
```

---

## Usage

### Usage in English

```python
from agent import {"".join(word.capitalize() for word in agent_name.split("-"))}

agent = {"".join(word.capitalize() for word in agent_name.split("-"))}()
```

### 使い方

```python
from agent import {"".join(word.capitalize() for word in agent_name.split("-"))}

agent = {"".join(word.capitalize() for word in agent_name.split("-"))}()
```

---

## Files

- `agent.py` - Main agent module
- `db.py` - Database module
- `discord.py` - Discord bot module
- `README.md` - This file
- `requirements.txt` - Python dependencies

---

## License

MIT License
'''
    return content

def create_requirements_txt():
    """Create requirements.txt file"""
    return """discord.py>=2.3.0
"""

def create_agent_directory(agent_name, agent_info):
    """Create all files for an agent"""
    agent_dir = Path(f"/workspace/agents/{agent_name}")
    agent_dir.mkdir(exist_ok=True)

    # Create agent.py
    (agent_dir / "agent.py").write_text(create_agent_py(agent_name, agent_info))

    # Create db.py
    (agent_dir / "db.py").write_text(create_db_py(agent_name, agent_info))

    # Create discord.py
    (agent_dir / "discord.py").write_text(create_discord_py(agent_name, agent_info))

    # Create README.md
    (agent_dir / "README.md").write_text(create_readme_md(agent_name, agent_info))

    # Create requirements.txt
    (agent_dir / "requirements.txt").write_text(create_requirements_txt())

    print(f"Created {agent_name} successfully")

def main():
    """Main function"""
    print("Creating erotic content V3 agents...")
    print(f"Total agents to create: {len(AGENTS)}")

    for agent_name, agent_info in AGENTS.items():
        create_agent_directory(agent_name, agent_info)

    print(f"\\nAll agents created successfully!")
    print(f"Total: {len(AGENTS)} agents")

if __name__ == "__main__":
    main()
'''
