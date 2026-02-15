#!/usr/bin/env python3
"""
野球歴史・伝承エージェントオーケストレーター
Baseball History & Legacy Agents Orchestrator
"""

import os
import json
from datetime import datetime
from pathlib import Path

# SQL queries as constants
SQL_CREATE_ITEMS = """            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                content TEXT,
                category TEXT,
                tags TEXT,
                metadata TEXT,
                user_id TEXT,
                rating REAL DEFAULT 0,
                view_count INTEGER DEFAULT 0,
                is_public BOOLEAN DEFAULT 0,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""

SQL_CREATE_TAGS = """            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""

SQL_CREATE_ITEM_TAGS = """            CREATE TABLE IF NOT EXISTS item_tags (
                item_id INTEGER,
                tag_id INTEGER,
                PRIMARY KEY (item_id, tag_id),
                FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )"""

SQL_CREATE_FAVORITES = """            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                item_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
                UNIQUE(user_id, item_id)
            )"""

SQL_CREATE_ACTIVITY_LOG = """            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                action TEXT NOT NULL,
                item_id INTEGER,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""


class BaseballHistoryOrchestrator:
    def __init__(self, workspace="/workspace"):
        self.workspace = workspace
        self.agents_dir = Path(workspace) / "agents"
        self.progress_file = Path(workspace) / "baseball_history_progress.json"
        self.agents = [
            {
                "name": "baseball-historical-match-agent",
                "display_name_jp": "野球歴史的名試合エージェント",
                "display_name_en": "Baseball Historical Match Agent",
                "description_jp": "歴史的な名試合、ドラマチックな展開の記録・分析・管理",
                "description_en": "Records, analyzes, and manages historical memorable games and dramatic moments"
            },
            {
                "name": "baseball-legend-profile-agent",
                "display_name_jp": "野球伝説選手プロフィールエージェント",
                "display_name_en": "Baseball Legend Profile Agent",
                "description_jp": "殿堂入り選手、レジェンド選手のプロフィール・統計・エピソード管理",
                "description_en": "Manages profiles, stats, and legendary episodes of Hall of Fame and legendary players"
            },
            {
                "name": "baseball-evolution-agent",
                "display_name_jp": "野球戦術・ルール進化エージェント",
                "display_name_en": "Baseball Evolution Agent",
                "description_jp": "野球戦術の歴史的進化、ルール変更の影響、プレイスタイル比較",
                "description_en": "Tracks historical evolution of baseball tactics, rule changes, and playstyle comparisons"
            },
            {
                "name": "baseball-stadium-history-agent",
                "display_name_jp": "野球場歴史エージェント",
                "display_name_en": "Baseball Stadium History Agent",
                "description_jp": "歴史的野球場の歴史、特徴、伝説的イベント、記録的試合との紐付け",
                "description_en": "Manages stadium history, features, legendary events, and links to record-setting games"
            },
            {
                "name": "baseball-culture-agent",
                "display_name_jp": "野球文化エージェント",
                "display_name_en": "Baseball Culture Agent",
                "description_jp": "野球に関連する音楽、映画、文学、アート、ファン文化、社会的影響",
                "description_en": "Collects baseball-related music, movies, literature, art, fan culture, and social impact"
            }
        ]
        self.load_progress()

    def load_progress(self):
        if self.progress_file.exists():
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                self.progress = json.load(f)
        else:
            self.progress = {
                "project_name": "野球歴史・伝承エージェント",
                "project_name_en": "Baseball History & Legacy Agents",
                "started_at": None,
                "completed_at": None,
                "agents": {agent["name"]: False for agent in self.agents}
            }

    def save_progress(self):
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, ensure_ascii=False, indent=2)

    def create_agent(self, agent_info):
        agent_name = agent_info["name"]
        agent_dir = self.agents_dir / agent_name

        print(f"Creating agent: {agent_name}")

        if agent_dir.exists():
            print(f"  Agent directory already exists: {agent_dir}")
            return True

        agent_dir.mkdir(parents=True, exist_ok=True)

        # Write each file
        self.write_agent_py(agent_dir, agent_info)
        self.write_db_py(agent_dir, agent_info)
        self.write_discord_py(agent_dir, agent_info)
        self.write_requirements_txt(agent_dir)
        self.write_readme_md(agent_dir, agent_info)

        print(f"  Created agent: {agent_name}")
        return True

    def write_agent_py(self, agent_dir, agent_info):
        name = agent_info["name"]
        class_name = self.to_class_name(name)

        content = f'''#!/usr/bin/env python3
"""
{agent_info["display_name_jp"]} / {agent_info["display_name_en"]}
{name}

{agent_info["description_jp"]}
{agent_info["description_en"]}
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

class {class_name}:
    """{name} - Main Agent Class"""

    def __init__(self, db_manager=None, logger=None):
        self.db_manager = db_manager
        self.logger = logger or logging.getLogger(__name__)
        self.name = "{name}"
        self.version = "1.0.0"

    async def initialize(self):
        """Initialize the agent"""
        self.logger.info("Initializing " + self.name + "...")
        if self.db_manager:
            await self.db_manager.initialize()
        self.logger.info(self.name + " initialized successfully")

    async def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a user query"""
        self.logger.info("Processing query: " + query[:50] + "...")

        query_lower = query.lower()

        if any(kw in query_lower for kw in ['search', 'find', '検索', '探し']):
            return await self._handle_search(query, context)
        elif any(kw in query_lower for kw in ['add', 'create', '登録', '追加']):
            return await self._handle_add(query, context)
        elif any(kw in query_lower for kw in ['update', 'edit', '更新', '編集']):
            return await self._handle_update(query, context)
        elif any(kw in query_lower for kw in ['delete', 'remove', '削除', '除去']):
            return await self._handle_delete(query, context)
        elif any(kw in query_lower for kw in ['stats', 'statistics', '統計', '分析']):
            return await self._handle_stats(query, context)
        else:
            return await self._handle_general(query, context)

    async def _handle_search(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle search queries"""
        results = []
        if self.db_manager:
            results = await self.db_manager.search(query)

        return {{
            "status": "success",
            "query": query,
            "results": results,
            "count": len(results)
        }}

    async def _handle_add(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle add/create queries"""
        data = self._extract_data_from_query(query)
        if self.db_manager:
            result = await self.db_manager.add(data)
            return {{
                "status": "success",
                "action": "added",
                "data": data,
                "result": result
            }}
        return {{
            "status": "error",
            "message": "Database manager not available"
        }}

    async def _handle_update(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle update/edit queries"""
        data = self._extract_data_from_query(query)
        item_id = self._extract_id_from_query(query)

        if self.db_manager and item_id:
            result = await self.db_manager.update(item_id, data)
            return {{
                "status": "success",
                "action": "updated",
                "id": item_id,
                "result": result
            }}
        return {{
            "status": "error",
            "message": "Database manager not available or missing ID"
        }}

    async def _handle_delete(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle delete/remove queries"""
        item_id = self._extract_id_from_query(query)

        if self.db_manager and item_id:
            result = await self.db_manager.delete(item_id)
            return {{
                "status": "success",
                "action": "deleted",
                "id": item_id,
                "result": result
            }}
        return {{
            "status": "error",
            "message": "Database manager not available or missing ID"
        }}

    async def _handle_stats(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle statistics queries"""
        if self.db_manager:
            stats = await self.db_manager.get_statistics()
            return {{
                "status": "success",
                "statistics": stats
            }}
        return {{
            "status": "error",
            "message": "Database manager not available"
        }}

    async def _handle_general(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle general queries"""
        return {{
            "status": "success",
            "message": "Processed: " + query[:100],
            "suggestions": [
                "Try searching for specific items",
                "Use 'add' to create new entries",
                "Use 'stats' to see statistics"
            ]
        }}

    def _extract_data_from_query(self, query: str) -> Dict[str, Any]:
        """Extract structured data from natural language query"""
        return {{
            "query": query,
            "timestamp": datetime.now().isoformat()
        }}

    def _extract_id_from_query(self, query: str) -> Optional[int]:
        """Extract item ID from query"""
        import re
        match = re.search(r'id[:\s]*(\d+)', query.lower())
        if match:
            return int(match.group(1))
        return None

    async def get_recommendations(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get personalized recommendations"""
        if self.db_manager:
            return await self.db_manager.get_recommendations(user_id, limit)
        return []

    async def get_trending(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending items"""
        if self.db_manager:
            return await self.db_manager.get_trending(limit)
        return []

    async def get_related(self, item_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Get related items"""
        if self.db_manager:
            return await self.db_manager.get_related(item_id, limit)
        return []

    async def shutdown(self):
        """Shutdown the agent"""
        self.logger.info("Shutting down " + self.name + "...")
        if self.db_manager:
            await self.db_manager.close()
        self.logger.info(self.name + " shut down successfully")


def create_agent(db_manager=None, logger=None) -> {class_name}:
    """Factory function to create agent instance"""
    return {class_name}(db_manager, logger)
'''

        with open(agent_dir / "agent.py", 'w', encoding='utf-8') as f:
            f.write(content)

    def write_db_py(self, agent_dir, agent_info):
        name = agent_info["name"]
        class_name = self.to_class_name(name)
        db_path = "data/" + name + ".db"

        content = f'''#!/usr/bin/env python3
"""
Database Manager for {agent_info["display_name_jp"]}
{name} - Database Layer
"""

import sqlite3
import aiosqlite
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path

class {class_name}DBManager:
    """Database manager for {name}"""

    def __init__(self, db_path: str = None, logger=None):
        self.db_path = db_path or "{db_path}"
        self.logger = logger or logging.getLogger(__name__)
        self.connection = None

    async def initialize(self):
        """Initialize database and create tables"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        self.connection = await aiosqlite.connect(self.db_path)

        await self._create_tables()
        await self._create_indexes()

        self.logger.info("Database initialized: " + self.db_path)

    async def _create_tables(self):
        """Create database tables"""

        await self.connection.execute('''
{SQL_CREATE_ITEMS}
        ''')

        await self.connection.execute('''
{SQL_CREATE_TAGS}
        ''')

        await self.connection.execute('''
{SQL_CREATE_ITEM_TAGS}
        ''')

        await self.connection.execute('''
{SQL_CREATE_FAVORITES}
        ''')

        await self.connection.execute('''
{SQL_CREATE_ACTIVITY_LOG}
        ''')

        await self.connection.commit()

    async def _create_indexes(self):
        """Create database indexes for better performance"""
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_items_category ON items(category)',
            'CREATE INDEX IF NOT EXISTS idx_items_status ON items(status)',
            'CREATE INDEX IF NOT EXISTS idx_items_rating ON items(rating)',
            'CREATE INDEX IF NOT EXISTS idx_items_created_at ON items(created_at)',
            'CREATE INDEX IF NOT EXISTS idx_activity_log_user_id ON activity_log(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_activity_log_action ON activity_log(action)',
            'CREATE INDEX IF NOT EXISTS idx_favorites_user_id ON favorites(user_id)'
        ]

        for index in indexes:
            await self.connection.execute(index)
        await self.connection.commit()

    async def add(self, data: Dict[str, Any]) -> int:
        """Add a new item"""
        async with self.connection.execute('''
            INSERT INTO items (title, description, content, category, tags, metadata, user_id, rating, is_public)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('title', ''),
            data.get('description', ''),
            data.get('content', ''),
            data.get('category', 'general'),
            json.dumps(data.get('tags', [])),
            json.dumps(data.get('metadata', {{}})),
            data.get('user_id'),
            data.get('rating', 0),
            data.get('is_public', False)
        )) as cursor:
            item_id = cursor.lastrowid
            await self.connection.commit()

            if 'tags' in data:
                await self._add_tags(item_id, data['tags'])

            await self._log_activity(data.get('user_id'), 'add', item_id)

            return item_id

    async def update(self, item_id: int, data: Dict[str, Any]) -> bool:
        """Update an existing item"""
        update_fields = []
        values = []

        for field in ['title', 'description', 'content', 'category', 'rating', 'is_public', 'status']:
            if field in data:
                update_fields.append(field + " = ?")
                values.append(data[field])

        if not update_fields:
            return False

        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(item_id)

        await self.connection.execute(
            'UPDATE items SET ' + ', '.join(update_fields) + ' WHERE id = ?',
            values
        )

        await self.connection.commit()

        if 'tags' in data:
            await self._update_tags(item_id, data['tags'])

        await self._log_activity(None, 'update', item_id)

        return True

    async def delete(self, item_id: int) -> bool:
        """Delete an item"""
        await self.connection.execute('DELETE FROM items WHERE id = ?', (item_id,))
        await self.connection.commit()
        return True

    async def get(self, item_id: int) -> Optional[Dict[str, Any]]:
        """Get an item by ID"""
        async with self.connection.execute(
            'SELECT * FROM items WHERE id = ?',
            (item_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return await self._row_to_dict(cursor, row)
        return None

    async def search(self, query: str, category: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Search items"""
        search_pattern = '%' + query + '%'

        if category:
            async with self.connection.execute('''
                SELECT * FROM items
                WHERE (title LIKE ? OR description LIKE ? OR content LIKE ?)
                AND category = ?
                AND status = 'active'
                ORDER BY rating DESC, created_at DESC
                LIMIT ?
            ''', (search_pattern, search_pattern, search_pattern, category, limit)) as cursor:
                rows = await cursor.fetchall()
                return await self._rows_to_dicts(cursor, rows)
        else:
            async with self.connection.execute('''
                SELECT * FROM items
                WHERE (title LIKE ? OR description LIKE ? OR content LIKE ?)
                AND status = 'active'
                ORDER BY rating DESC, created_at DESC
                LIMIT ?
            ''', (search_pattern, search_pattern, search_pattern, limit)) as cursor:
                rows = await cursor.fetchall()
                return await self._rows_to_dicts(cursor, rows)

    async def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        async with self.connection.execute('SELECT COUNT(*) FROM items WHERE status = "active"') as cursor:
            total_items = (await cursor.fetchone())[0]

        async with self.connection.execute('SELECT category, COUNT(*) FROM items WHERE status = "active" GROUP BY category') as cursor:
            by_category = dict(await cursor.fetchall())

        async with self.connection.execute('SELECT AVG(rating) FROM items WHERE status = "active" AND rating > 0') as cursor:
            avg_rating = (await cursor.fetchone())[0] or 0

        async with self.connection.execute('SELECT COUNT(DISTINCT user_id) FROM items') as cursor:
            total_users = (await cursor.fetchone())[0]

        async with self.connection.execute('SELECT COUNT(*) FROM tags') as cursor:
            total_tags = (await cursor.fetchone())[0]

        return {{
            "total_items": total_items,
            "by_category": by_category,
            "average_rating": round(avg_rating, 2),
            "total_users": total_users,
            "total_tags": total_tags
        }}

    async def get_recommendations(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get personalized recommendations for a user"""
        async with self.connection.execute('''
            SELECT * FROM items
            WHERE id NOT IN (SELECT item_id FROM favorites WHERE user_id = ?)
            AND status = 'active'
            AND is_public = 1
            ORDER BY rating DESC, view_count DESC
            LIMIT ?
        ''', (user_id, limit)) as cursor:
            rows = await cursor.fetchall()
            return await self._rows_to_dicts(cursor, rows)

    async def get_trending(self, limit: int = 10, days: int = 7) -> List[Dict[str, Any]]:
        """Get trending items (most viewed in recent days)"""
        cutoff_date = datetime.now() - timedelta(days=days)

        async with self.connection.execute('''
            SELECT * FROM items
            WHERE created_at >= ?
            AND status = 'active'
            ORDER BY view_count DESC, rating DESC
            LIMIT ?
        ''', (cutoff_date.isoformat(), limit)) as cursor:
            rows = await cursor.fetchall()
            return await self._rows_to_dicts(cursor, rows)

    async def get_related(self, item_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Get related items"""
        item = await self.get(item_id)
        if not item:
            return []

        async with self.connection.execute('''
            SELECT * FROM items
            WHERE category = ?
            AND id != ?
            AND status = 'active'
            ORDER BY rating DESC
            LIMIT ?
        ''', (item.get('category'), item_id, limit)) as cursor:
            rows = await cursor.fetchall()
            return await self._rows_to_dicts(cursor, rows)

    async def add_favorite(self, user_id: str, item_id: int) -> bool:
        """Add item to user's favorites"""
        try:
            await self.connection.execute(
                'INSERT INTO favorites (user_id, item_id) VALUES (?, ?)',
                (user_id, item_id)
            )
            await self.connection.commit()
            await self._log_activity(user_id, 'favorite', item_id)
            return True
        except sqlite3.IntegrityError:
            return False

    async def remove_favorite(self, user_id: str, item_id: int) -> bool:
        """Remove item from user's favorites"""
        await self.connection.execute(
            'DELETE FROM favorites WHERE user_id = ? AND item_id = ?',
            (user_id, item_id)
        )
        await self.connection.commit()
        return True

    async def increment_view_count(self, item_id: int):
        """Increment item view count"""
        await self.connection.execute(
            'UPDATE items SET view_count = view_count + 1 WHERE id = ?',
            (item_id,)
        )
        await self.connection.commit()

    async def _add_tags(self, item_id: int, tags: List[str]):
        """Add tags to an item"""
        for tag_name in tags:
            async with self.connection.execute(
                'SELECT id FROM tags WHERE name = ?',
                (tag_name,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    tag_id = row[0]
                    await self.connection.execute(
                        'UPDATE tags SET count = count + 1 WHERE id = ?',
                        (tag_id,)
                    )
                else:
                    await self.connection.execute(
                        'INSERT INTO tags (name, count) VALUES (?, 1)',
                        (tag_name,)
                    )
                    tag_id = cursor.lastrowid

            try:
                await self.connection.execute(
                    'INSERT INTO item_tags (item_id, tag_id) VALUES (?, ?)',
                    (item_id, tag_id)
                )
            except sqlite3.IntegrityError:
                pass

        await self.connection.commit()

    async def _update_tags(self, item_id: int, tags: List[str]):
        """Update tags for an item"""
        await self.connection.execute(
            'DELETE FROM item_tags WHERE item_id = ?',
            (item_id,)
        )
        await self._add_tags(item_id, tags)

    async def _log_activity(self, user_id: Optional[str], action: str, item_id: Optional[int]):
        """Log user activity"""
        await self.connection.execute(
            'INSERT INTO activity_log (user_id, action, item_id) VALUES (?, ?, ?)',
            (user_id, action, item_id)
        )
        await self.connection.commit()

    async def _rows_to_dicts(self, cursor, rows) -> List[Dict[str, Any]]:
        """Convert query result rows to dictionaries"""
        results = []
        for row in rows:
            results.append(await self._row_to_dict(cursor, row))
        return results

    async def _row_to_dict(self, cursor, row) -> Dict[str, Any]:
        """Convert a query result row to dictionary"""
        columns = [description[0] for description in cursor.description]
        result = dict(zip(columns, row))

        for field in ['tags', 'metadata']:
            if field in result and result[field]:
                try:
                    result[field] = json.loads(result[field])
                except:
                    pass

        return result

    async def close(self):
        """Close database connection"""
        if self.connection:
            await self.connection.close()
            self.logger.info("Database connection closed")
'''

        with open(agent_dir / "db.py", 'w', encoding='utf-8') as f:
            f.write(content)

    def write_discord_py(self, agent_dir, agent_info):
        name = agent_info["name"]
        display_name_jp = agent_info["display_name_jp"]
        desc_jp = agent_info["description_jp"]
        class_name = self.to_class_name(name)

        content = f'''#!/usr/bin/env python3
"""
Discord Bot Integration for {display_name_jp}
{name} - Discord Interface
"""

import discord
from discord.ext import commands
import logging
from typing import Optional
from datetime import datetime

class {class_name}DiscordBot(commands.Bot):
    """Discord bot for {name}"""

    def __init__(self, agent, command_prefix: str = "!"):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True
        intents.guilds = True

        super().__init__(
            command_prefix=command_prefix,
            intents=intents,
            help_command=commands.DefaultHelpCommand()
        )

        self.agent = agent
        self.logger = logging.getLogger(__name__)

    async def on_ready(self):
        """Called when bot is ready"""
        self.logger.info(str(self.user) + " has connected to Discord!")
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="{display_name_jp}"
        )
        await self.change_presence(activity=activity)

    async def on_message(self, message):
        """Handle incoming messages"""
        if message.author == self.user:
            return

        await self.process_commands(message)

    @commands.command(name="search", aliases=["s", "検索"])
    async def search_command(self, ctx, *, query: str):
        """Search for items"""
        self.logger.info("Search command from " + str(ctx.author.name) + ": " + query)

        try:
            result = await self.agent.process_query(query, {{"type": "search"}})

            if result["status"] == "success":
                embed = discord.Embed(
                    title="🔍 検索結果: " + query,
                    color=discord.Color.blue()
                )
                embed.set_footer(text=str(result["count"]) + "件見つかりました")

                for item in result["results"][:5]:
                    embed.add_field(
                        name=item.get("title", "No Title"),
                        value=item.get("description", "No Description")[:100],
                        inline=False
                    )

                await ctx.send(embed=embed)
            else:
                await ctx.send("検索中にエラーが発生しました。")

        except Exception as e:
            self.logger.error("Error in search command: " + str(e))
            await ctx.send("エラー: " + str(e))

    @commands.command(name="add", aliases=["a", "追加", "登録"])
    async def add_command(self, ctx, *, content: str):
        """Add a new item"""
        self.logger.info("Add command from " + str(ctx.author.name))

        try:
            data = {{
                "title": content[:50],
                "description": content,
                "user_id": str(ctx.author.id),
                "is_public": True
            }}

            result = await self.agent.process_query(content, {{"type": "add", "data": data}})

            if result["status"] == "success":
                embed = discord.Embed(
                    title="✅ 追加完了",
                    description="「" + content[:50] + "」を追加しました。",
                    color=discord.Color.green()
                )
                embed.set_footer(text="ID: " + str(result.get('result')))
                await ctx.send(embed=embed)
            else:
                await ctx.send("追加中にエラーが発生しました。")

        except Exception as e:
            self.logger.error("Error in add command: " + str(e))
            await ctx.send("エラー: " + str(e))

    @commands.command(name="stats", aliases=["stat", "statistics", "統計"])
    async def stats_command(self, ctx):
        """Show statistics"""
        self.logger.info("Stats command from " + str(ctx.author.name))

        try:
            result = await self.agent.process_query("stats", {{"type": "stats"}})

            if result["status"] == "success":
                stats = result.get("statistics", {{}})

                embed = discord.Embed(
                    title="📊 統計情報",
                    color=discord.Color.purple()
                )
                embed.add_field(name="総アイテム数", value=stats.get("total_items", 0), inline=True)
                embed.add_field(name="平均評価", value=stats.get("average_rating", 0), inline=True)
                embed.add_field(name="総タグ数", value=stats.get("total_tags", 0), inline=True)
                embed.set_footer(text="{display_name_jp}")

                await ctx.send(embed=embed)
            else:
                await ctx.send("統計の取得中にエラーが発生しました。")

        except Exception as e:
            self.logger.error("Error in stats command: " + str(e))
            await ctx.send("エラー: " + str(e))

    @commands.command(name="trending", aliases=["t", "トレンド"])
    async def trending_command(self, ctx, limit: int = 5):
        """Show trending items"""
        self.logger.info("Trending command from " + str(ctx.author.name))

        try:
            items = await self.agent.get_trending(limit)

            if items:
                embed = discord.Embed(
                    title="🔥 トレンド",
                    description="最近人気のあるアイテム",
                    color=discord.Color.orange()
                )

                for i, item in enumerate(items, 1):
                    embed.add_field(
                        name=str(i) + ". " + item.get("title", "No Title"),
                        value="評価: " + str(item.get("rating", 0)) + " | 閲覧: " + str(item.get("view_count", 0)),
                        inline=False
                    )

                await ctx.send(embed=embed)
            else:
                await ctx.send("表示できるトレンドがありません。")

        except Exception as e:
            self.logger.error("Error in trending command: " + str(e))
            await ctx.send("エラー: " + str(e))

    @commands.command(name="recommend", aliases=["rec", "おすすめ"])
    async def recommend_command(self, ctx, limit: int = 5):
        """Get personalized recommendations"""
        self.logger.info("Recommend command from " + str(ctx.author.name))

        try:
            user_id = str(ctx.author.id)
            items = await self.agent.get_recommendations(user_id, limit)

            if items:
                embed = discord.Embed(
                    title="💡 おすすめ",
                    description=str(ctx.author.name) + "さんへのおすすめ",
                    color=discord.Color.teal()
                )

                for i, item in enumerate(items, 1):
                    embed.add_field(
                        name=str(i) + ". " + item.get("title", "No Title"),
                        value=item.get("description", "No Description")[:100],
                        inline=False
                    )

                await ctx.send(embed=embed)
            else:
                await ctx.send("おすすめのアイテムが見つかりませんでした。")

        except Exception as e:
            self.logger.error("Error in recommend command: " + str(e))
            await ctx.send("エラー: " + str(e))

    @commands.command(name="help", aliases=["h", "ヘルプ"])
    async def help_command(self, ctx):
        """Show help"""
        embed = discord.Embed(
            title="{display_name_jp} - ヘルプ",
            description="{desc_jp}",
            color=discord.Color.blue()
        )

        embed.add_field(name="!search <クエリ>", value="アイテムを検索", inline=False)
        embed.add_field(name="!add <内容>", value="新しいアイテムを追加", inline=False)
        embed.add_field(name="!stats", value="統計情報を表示", inline=False)
        embed.add_field(name="!trending [件数]", value="トレンドを表示", inline=False)
        embed.add_field(name="!recommend [件数]", value="おすすめを表示", inline=False)

        await ctx.send(embed=embed)


def create_discord_bot(agent, command_prefix: str = "!"):
    """Factory function to create Discord bot instance"""
    return {class_name}DiscordBot(agent, command_prefix)
'''

        with open(agent_dir / "discord.py", 'w', encoding='utf-8') as f:
            f.write(content)

    def write_requirements_txt(self, agent_dir):
        content = """discord.py>=2.3.0
aiosqlite>=0.19.0
python-dotenv>=1.0.0
"""
        with open(agent_dir / "requirements.txt", 'w', encoding='utf-8') as f:
            f.write(content)

    def write_readme_md(self, agent_dir, agent_info):
        name = agent_info["name"]
        display_name_jp = agent_info["display_name_jp"]
        display_name_en = agent_info["display_name_en"]
        desc_jp = agent_info["description_jp"]
        desc_en = agent_info["description_en"]
        class_name = self.to_class_name(name)

        content = f'''# {display_name_jp} / {display_name_en}

{name}

---

## 概要 / Overview

{desc_jp}

{desc_en}

---

## 機能 / Features

### 日本語 / Japanese

- **検索**: キーワードでアイテムを検索
- **追加**: 新しいアイテムを追加
- **更新**: 既存のアイテムを更新
- **削除**: アイテムを削除
- **統計**: 統計情報を表示
- **おすすめ**: パーソナライズされたおすすめを表示
- **トレンド**: 人気のアイテムを表示

### English

- **Search**: Search items by keywords
- **Add**: Add new items
- **Update**: Update existing items
- **Delete**: Delete items
- **Statistics**: View statistics
- **Recommendations**: Get personalized recommendations
- **Trending**: View trending items

---

## インストール / Installation

```bash
pip install -r requirements.txt
```

---

## 使い方 / Usage

### Python / Python API

```python
from agent import {class_name}
from db import {class_name}DBManager

# Create database manager
db = {class_name}DBManager()
await db.initialize()

# Create agent
agent = {class_name}(db)
await agent.initialize()

# Search items
result = await agent.process_query("検索クエリ")

# Get recommendations
recommendations = await agent.get_recommendations("user_id")

# Get trending items
trending = await agent.get_trending(limit=10)
```

### Discord Bot / Discord Bot

```python
from agent import {class_name}
from db import {class_name}DBManager
from discord import {class_name}DiscordBot

# Initialize
db = {class_name}DBManager()
await db.initialize()

agent = {class_name}(db)
await agent.initialize()

# Create bot
bot = {class_name}DiscordBot(agent, command_prefix="!")

# Run bot
bot.run("YOUR_BOT_TOKEN")
```

#### Discord Commands / Discordコマンド

| Command / コマンド | Description / 説明 |
|-------------------|---------------------|
| `!search <query>` | Search items / アイテムを検索 |
| `!s <query>` | Short search / 検索（短縮） |
| `!add <content>` | Add new item / 新規アイテム追加 |
| `!stats` | Show statistics / 統計表示 |
| `!trending [n]` | Show trending / トレンド表示 |
| `!recommend [n]` | Get recommendations / おすすめ表示 |
| `!help` | Show help / ヘルプ表示 |

---

## データベース構造 / Database Schema

### items テーブル

| Column / カラム | Type / 型 | Description / 説明 |
|------------------|-----------|---------------------|
| id | INTEGER | Primary key / 主キー |
| title | TEXT | Item title / アイテムタイトル |
| description | TEXT | Item description / アイテム説明 |
| content | TEXT | Full content / コンテンツ全文 |
| category | TEXT | Category / カテゴリ |
| tags | TEXT (JSON) | Tags / タグ（JSON形式） |
| metadata | TEXT (JSON) | Metadata / メタデータ |
| user_id | TEXT | Creator user ID / 作成者ID |
| rating | REAL | Rating (0-5) / 評価 |
| view_count | INTEGER | View count / 閲覧数 |
| is_public | BOOLEAN | Public visibility / 公開フラグ |
| status | TEXT | Status / ステータス |
| created_at | TIMESTAMP | Created at / 作成日時 |
| updated_at | TIMESTAMP | Updated at / 更新日時 |

---

## License / ライセンス

MIT License
'''

        with open(agent_dir / "README.md", 'w', encoding='utf-8') as f:
            f.write(content)

    def to_class_name(self, name: str) -> str:
        """Convert kebab-case to CamelCase class name"""
        parts = name.replace('-', ' ').split()
        return ''.join(part.capitalize() for part in parts)

    def run(self):
        """Run orchestrator"""
        if self.progress["started_at"] is None:
            self.progress["started_at"] = datetime.now().isoformat()

        print("\\n" + "=" * 60)
        print("野球歴史・伝承エージェントオーケストレーター")
        print("Baseball History & Legacy Agents Orchestrator")
        print("=" * 60 + "\\n")

        total = len(self.agents)
        completed = sum(1 for agent in self.progress["agents"].values() if agent)

        print("Progress: " + str(completed) + "/" + str(total) + " agents completed\\n")

        for agent_info in self.agents:
            agent_name = agent_info["name"]

            if self.progress["agents"][agent_name]:
                print("✓ " + agent_name + " - Already completed")
                continue

            print("Creating: " + agent_name)
            success = self.create_agent(agent_info)

            if success:
                self.progress["agents"][agent_name] = True
                self.save_progress()
                print("✓ " + agent_name + " - Completed\\n")
            else:
                print("✗ " + agent_name + " - Failed\\n")

        # Check if all agents are completed
        all_completed = all(self.progress["agents"].values())

        if all_completed and self.progress["completed_at"] is None:
            self.progress["completed_at"] = datetime.now().isoformat()
            self.save_progress()

        print("\\n" + "=" * 60)
        if all_completed:
            print("🎉 All agents completed!")
            print("Project completed at: " + self.progress["completed_at"])
        else:
            completed = sum(1 for agent in self.progress["agents"].values() if agent)
            print("Progress: " + str(completed) + "/" + str(total) + " agents completed")
        print("=" * 60 + "\\n")


def main():
    orchestrator = BaseballHistoryOrchestrator()
    orchestrator.run()


if __name__ == "__main__":
    main()
'''

        # Fix escaped newlines
        content = content.replace('\\n', '\n')

        with open(self.progress_file, 'w', encoding='utf-8') as f:
            f.write(content)
