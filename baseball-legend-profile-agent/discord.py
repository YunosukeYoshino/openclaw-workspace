#!/usr/bin/env python3
"""Discord Integration for baseball-legend-profile-agent"""

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

logger = logging.getLogger('baseball-legend-profile-agent')


class BaseballLegendProfileAgentDiscordBot:
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
**baseball-legend-profile-agent Commands:**

`{self.prefix}add <name> <content>` - Add a legend profile
`{self.prefix}get <id>` - Get a legend by ID
`{self.prefix}list [team]` - List legends
`{self.prefix}search <query>` - Search legends
`{self.prefix}stats` - Show statistics
`{self.prefix}hof` - List Hall of Fame inductees

**Entry types:** legend, hof, award, record
**Statuses:** active, archived, completed
"""
            embed = discord.Embed(title="Bot Commands", description=help_text, color=discord.Color.blue())
            await ctx.send(embed=embed)

        @self.bot.command(name="add")
        async def add_command(ctx, name: str, *, content: str):
            try:
                from db import DatabaseManager
                db = DatabaseManager(self.db_path)
                await db.connect()
                entry_id = await db.add_entry("legend", name, content)
                await db.close()

                if entry_id:
                    await ctx.send(f"Added legend (ID: {entry_id}): {name}")
                else:
                    await ctx.send("Failed to add legend")
            except Exception as err:
                logger.error(f"Add command error: {err}")
                await ctx.send(f"Error: {err}")

        @self.bot.command(name="get")
        async def get_command(ctx, entry_id: int):
            try:
                from db import DatabaseManager
                db = DatabaseManager(self.db_path)
                await db.connect()
                entry = await db.get_entry(entry_id)
                await db.close()

                if entry:
                    embed = discord.Embed(title=f"Legend #{entry_id}", description=entry.get('content', ''), color=discord.Color.gold())
                    embed.add_field(name="Name", value=entry.get('title', 'N/A'))
                    embed.add_field(name="Status", value=entry.get('status', 'N/A'))
                    embed.add_field(name="Created", value=entry.get('created_at', 'N/A'))
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"Legend {entry_id} not found")
            except Exception as err:
                logger.error(f"Get command error: {err}")
                await ctx.send(f"Error: {err}")

        @self.bot.command(name="list")
        async def list_command(ctx, team: str = None, limit: int = 20):
            try:
                from db import DatabaseManager
                db = DatabaseManager(self.db_path)
                await db.connect()
                entries = await db.list_entries(team, limit=limit)
                await db.close()

                if entries:
                    msg = "**Baseball Legends:**\n\n"
                    for entry in entries[:10]:
                        msg += f"#{entry['id']} {entry.get('title', 'No name')} ({entry.get('type', 'legend')})\n"
                    if len(entries) > 10:
                        msg += f"\n... and {len(entries) - 10} more"
                    await ctx.send(msg)
                else:
                    await ctx.send("No legends found")
            except Exception as err:
                logger.error(f"List command error: {err}")
                await ctx.send(f"Error: {err}")

        @self.bot.command(name="search")
        async def search_command(ctx, *, query: str):
            try:
                from db import DatabaseManager
                db = DatabaseManager(self.db_path)
                await db.connect()
                results = await db.search_entries(query, limit=10)
                await db.close()

                if results:
                    msg = f"**Search results for '{query}':**\n\n"
                    for entry in results:
                        msg += f"#{entry['id']} {entry.get('title', 'No name')}\n"
                    await ctx.send(msg)
                else:
                    await ctx.send(f"No legends found for '{query}'")
            except Exception as err:
                logger.error(f"Search command error: {err}")
                await ctx.send(f"Error: {err}")

        @self.bot.command(name="stats")
        async def stats_command(ctx):
            try:
                from db import DatabaseManager
                db = DatabaseManager(self.db_path)
                await db.connect()
                stats = await db.get_stats()
                await db.close()

                embed = discord.Embed(title="Database Statistics", color=discord.Color.purple())
                for key, value in stats.items():
                    embed.add_field(name=key.replace('_', ' ').title(), value=str(value))
                await ctx.send(embed=embed)
            except Exception as err:
                logger.error(f"Stats command error: {err}")
                await ctx.send(f"Error: {err}")

        @self.bot.command(name="hof")
        async def hof_command(ctx, limit: int = 10):
            try:
                from db import DatabaseManager
                db = DatabaseManager(self.db_path)
                await db.connect()
                entries = await db.list_entries("hof", limit=limit)
                await db.close()

                if entries:
                    msg = "**Hall of Fame Legends:**\n\n"
                    for entry in entries:
                        msg += f"#{entry['id']} {entry.get('title', 'No name')}\n"
                    await ctx.send(msg)
                else:
                    await ctx.send("No Hall of Fame entries found")
            except Exception as err:
                logger.error(f"HOF command error: {err}")
                await ctx.send(f"Error: {err}")

    async def start(self):
        if not DISCORD_AVAILABLE:
            logger.error("Cannot start: discord.py not available")
            return False

        if not self.token:
            logger.error("No token provided")
            return False

        try:
            await self.bot.start(self.token)
            return True
        except Exception as err:
            logger.error(f"Bot start failed: {err}")
            return False


async def main():
    token = os.environ.get("DISCORD_BOT_TOKEN") or sys.argv[1] if len(sys.argv) > 1 else None
    prefix = os.environ.get("BOT_PREFIX", "!")

    bot = BaseballLegendProfileAgentDiscordBot(token=token, prefix=prefix)
    await bot.start()


if __name__ == "__main__":
    if not DISCORD_AVAILABLE:
        print("Error: discord.py is not installed")
        print("Install with: pip install -r requirements.txt")
        sys.exit(1)

    asyncio.run(main())
