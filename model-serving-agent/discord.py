#!/usr/bin/env python3
"""Discord Integration for model-serving-agent"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Optional, List

try:
    import discord
    from discord.ext import commands, tasks
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False
    print("Warning: discord.py not installed")

logger = logging.getLogger('model-serving-agent')


class ModelServingAgentDiscordBot:
    def __init__(self, token: str = None, prefix: str = "!", db_path: str = None):
        self.token = token or os.environ.get("DISCORD_BOT_TOKEN")
        self.prefix = prefix
        self.db_path = db_path or os.path.join(os.path.dirname(__file__), "data.db")
        self.bot = None
        self.started = False

        if not DISCORD_AVAILABLE:
            logger.error("discord.py is not available")
            return

        intents = discord.Intents.default()
        intents.message_content = True
        intents.presences = True
        intents.members = True

        self.bot = commands.Bot(command_prefix=prefix, intents=intents, help_command=None)
        self._setup_commands()

    def _setup_commands(self):
        @self.bot.event
        async def on_ready():
            logger.info(f"Bot logged in as {self.bot.user}")
            self.started = True

        @self.bot.event
        async def on_command_error(ctx, error):
            if isinstance(error, commands.CommandNotFound):
                return
            logger.error(f"Command error: {error}")
            await ctx.send(f"Error: {error}")

        @self.bot.command(name="help", aliases=["h"])
        async def help_command(ctx):
            help_text = """
**model-serving-agent Commands:**

`{self.prefix}add <type> <content>` - Add an entry
`{self.prefix}get <id>` - Get an entry by ID
`{self.prefix}list [type]` - List entries
`{self.prefix}update <id> <status>` - Update entry status
`{self.prefix}delete <id>` - Delete an entry
`{self.prefix}stats` - Show statistics
`{self.prefix}tags` - List all tags
`{self.prefix}search <query>` - Search entries

**Entry types:** idea, goal, project, vision, note, task
**Statuses:** active, archived, completed
"""
            embed = discord.Embed(title="Bot Commands", description=help_text, color=discord.Color.blue())
            await ctx.send(embed=embed)

        @self.bot.command(name="add")
        async def add_command(ctx, entry_type: str, *, content: str):
            valid_types = ["idea", "goal", "project", "vision", "note", "task"]
            if entry_type not in valid_types:
                await ctx.send(f"Invalid type. Valid types: {', '.join(valid_types)}")
                return

            try:
                from db import DatabaseManager
                db = DatabaseManager(self.db_path)
                db.connect()
                entry_id = db.add_entry(entry_type, content)
                db.close()

                if entry_id:
                    await ctx.send(f"Added {entry_type} (ID: {entry_id})")
                else:
                    await ctx.send("Failed to add entry")
            except Exception as err:
                logger.error(f"Add command error: {err}")
                await ctx.send(f"Error: {err}")

        @self.bot.command(name="get")
        async def get_command(ctx, entry_id: int):
            try:
                from db import DatabaseManager
                db = DatabaseManager(self.db_path)
                db.connect()
                entry = db.get_entry(entry_id)
                db.close()

                if entry:
                    embed = discord.Embed(
                        title=entry.get("title") or f"{entry['type'].title()} #{entry_id}",
                        description=entry.get("content", ""),
                        color=discord.Color.green()
                    )
                    embed.add_field(name="Type", value=entry["type"])
                    embed.add_field(name="Status", value=entry["status"])
                    embed.add_field(name="Priority", value=str(entry.get("priority", 0)))
                    if entry.get("tags"):
                        embed.add_field(name="Tags", value=", ".join(entry["tags"]))
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"Entry {entry_id} not found")
            except Exception as err:
                logger.error(f"Get command error: {err}")
                await ctx.send(f"Error: {err}")

        @self.bot.command(name="list")
        async def list_command(ctx, entry_type: str = None):
            try:
                from db import DatabaseManager
                db = DatabaseManager(self.db_path)
                db.connect()
                entries = db.list_entries(entry_type=entry_type, limit=20)
                db.close()

                if entries:
                    title = f"{entry_type.title()} Entries" if entry_type else "All Entries"
                    lines = []
                    for entry in entries[:20]:
                        status_emoji = {"active": "🟢", "archived": "📦", "completed": "✅"}.get(entry["status"], "⚪")
                        content_preview = entry.get("content", "")[:50] + "..." if len(entry.get("content", "")) > 50 else entry.get("content", "")
                        lines.append(f"{status_emoji} `#{entry['id']}` {content_preview}")

                    embed = discord.Embed(title=title, description="\n".join(lines), color=discord.Color.blue())
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("No entries found")
            except Exception as err:
                logger.error(f"List command error: {err}")
                await ctx.send(f"Error: {err}")

        @self.bot.command(name="update")
        async def update_command(ctx, entry_id: int, status: str):
            valid_statuses = ["active", "archived", "completed"]
            if status not in valid_statuses:
                await ctx.send(f"Invalid status. Valid: {', '.join(valid_statuses)}")
                return

            try:
                from db import DatabaseManager
                db = DatabaseManager(self.db_path)
                db.connect()
                success = db.update_entry(entry_id, status=status)
                db.close()

                if success:
                    await ctx.send(f"Updated entry {entry_id} to {status}")
                else:
                    await ctx.send(f"Failed to update entry {entry_id}")
            except Exception as err:
                logger.error(f"Update command error: {err}")
                await ctx.send(f"Error: {err}")

        @self.bot.command(name="delete")
        async def delete_command(ctx, entry_id: int):
            try:
                from db import DatabaseManager
                db = DatabaseManager(self.db_path)
                db.connect()
                success = db.delete_entry(entry_id)
                db.close()

                if success:
                    await ctx.send(f"Deleted entry {entry_id}")
                else:
                    await ctx.send(f"Failed to delete entry {entry_id}")
            except Exception as err:
                logger.error(f"Delete command error: {err}")
                await ctx.send(f"Error: {err}")

        @self.bot.command(name="stats")
        async def stats_command(ctx):
            try:
                from db import DatabaseManager
                db = DatabaseManager(self.db_path)
                db.connect()
                stats = db.get_stats()
                db.close()

                embed = discord.Embed(title="Database Statistics", color=discord.Color.purple())
                embed.add_field(name="Total Entries", value=str(stats.get("total_entries", 0)))
                embed.add_field(name="Total Tags", value=str(stats.get("total_tags", 0)))
                embed.add_field(name="Total Activities", value=str(stats.get("total_activities", 0)))

                if stats.get("entries_by_type"):
                    type_text = "\n".join([f"{k}: {v}" for k, v in stats["entries_by_type"].items()])
                    embed.add_field(name="By Type", value=type_text, inline=False)

                if stats.get("entries_by_status"):
                    status_text = "\n".join([f"{k}: {v}" for k, v in stats["entries_by_status"].items()])
                    embed.add_field(name="By Status", value=status_text, inline=False)

                await ctx.send(embed=embed)
            except Exception as err:
                logger.error(f"Stats command error: {err}")
                await ctx.send(f"Error: {err}")

        @self.bot.command(name="tags")
        async def tags_command(ctx):
            try:
                from db import DatabaseManager
                db = DatabaseManager(self.db_path)
                db.connect()
                tags = db.get_tags()
                db.close()

                if tags:
                    tag_list = [f"**{tag['name']}** ({tag['entry_count']})" for tag in tags]
                    embed = discord.Embed(title="Tags", description=", ".join(tag_list), color=discord.Color.orange())
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("No tags found")
            except Exception as err:
                logger.error(f"Tags command error: {err}")
                await ctx.send(f"Error: {err}")

        @self.bot.command(name="search")
        async def search_command(ctx, *, query: str):
            try:
                from db import DatabaseManager
                db = DatabaseManager(self.db_path)
                db.connect()
                entries = db.list_entries(limit=100)
                db.close()

                results = [
                    e for e in entries
                    if query.lower() in e.get("content", "").lower()
                    or (e.get("title") and query.lower() in e["title"].lower())
                ]

                if results:
                    lines = []
                    for entry in results[:10]:
                        status_emoji = {"active": "🟢", "archived": "📦", "completed": "✅"}.get(entry["status"], "⚪")
                        content_preview = entry.get("content", "")[:40] + "..." if len(entry.get("content", "")) > 40 else entry.get("content", "")
                        lines.append(f"{status_emoji} `#{entry['id']}` {content_preview}")

                    embed = discord.Embed(title=f"Search Results: {query}", description="\n".join(lines), color=discord.Color.teal())
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("No results found")
            except Exception as err:
                logger.error(f"Search command error: {err}")
                await ctx.send(f"Error: {err}")

    async def start(self):
        if not DISCORD_AVAILABLE:
            logger.error("Cannot start: discord.py not available")
            return False

        if not self.token:
            logger.error("No Discord token provided")
            return False

        try:
            await self.bot.start(self.token)
            return True
        except Exception as err:
            logger.error(f"Bot start error: {err}")
            return False

    def run(self):
        if not DISCORD_AVAILABLE:
            logger.error("Cannot run: discord.py not available")
            return False

        if not self.token:
            logger.error("No Discord token provided")
            return False

        try:
            self.bot.run(self.token)
            return True
        except Exception as err:
            logger.error(f"Bot run error: {err}")
            return False

    async def stop(self):
        if self.bot:
            await self.bot.close()
            self.started = False


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Discord bot for model-serving-agent")
    parser.add_argument("--token", help="Discord bot token")
    parser.add_argument("--prefix", default="!", help="Command prefix")
    args = parser.parse_args()

    bot = ModelServingAgentDiscordBot(token=args.token, prefix=args.prefix)
    if bot.run():
        print("Bot started successfully")
    else:
        print("Bot failed to start")
        sys.exit(1)


if __name__ == "__main__":
    main()
