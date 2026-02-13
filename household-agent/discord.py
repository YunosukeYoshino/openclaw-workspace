#!/usr/bin/env python3
"""Discord Integration for household-agent"""

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

logger = logging.getLogger('household-agent')


class HouseholdAgentDiscordBot:
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
**household-agent Commands:**

`{self.prefix}add <type> <content>` - Add an entry
`{self.prefix}get <id>` - Get an entry by ID
`{self.prefix}list [type]` - List entries
`{self.prefix}update <id> <status>` - Update entry status
`{self.prefix}delete <id>` - Delete an entry
`{self.prefix}stats` - Show statistics

**Entry types:** chore, shopping, meal, appointment, reminder
**Statuses:** active, completed, archived
"""
            embed = discord.Embed(title="Bot Commands", description=help_text, color=discord.Color.blue())
            await ctx.send(embed=embed)

        @self.bot.command(name="add")
        async def add_command(ctx, entry_type: str, *, content: str):
            try:
                from db import DatabaseManager
                db = DatabaseManager(self.db_path)
                await db.connect()
                entry_id = await db.add_entry(entry_type, content)
                await db.close()

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
                await db.connect()
                entry = await db.get_entry(entry_id)
                await db.close()

                if entry:
                    embed = discord.Embed(title=f"Entry #{entry_id}", description=entry.get('content', ''), color=discord.Color.green())
                    embed.add_field(name="Type", value=entry.get('type', 'N/A'))
                    embed.add_field(name="Status", value=entry.get('status', 'N/A'))
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"Entry {entry_id} not found")
            except Exception as err:
                logger.error(f"Get command error: {err}")
                await ctx.send(f"Error: {err}")

        @self.bot.command(name="list")
        async def list_command(ctx, entry_type: str = None, limit: int = 20):
            try:
                from db import DatabaseManager
                db = DatabaseManager(self.db_path)
                await db.connect()
                entries = await db.list_entries(entry_type, limit=limit)
                await db.close()

                if entries:
                    msg = "**Entries:**\n\n"
                    for entry in entries[:10]:
                        msg += f"#{entry['id']} {entry.get('type', 'entry')} - {entry.get('content', '')[:50]}...\n"
                    if len(entries) > 10:
                        msg += f"\n... and {len(entries) - 10} more"
                    await ctx.send(msg)
                else:
                    await ctx.send("No entries found")
            except Exception as err:
                logger.error(f"List command error: {err}")
                await ctx.send(f"Error: {err}")

        @self.bot.command(name="update")
        async def update_command(ctx, entry_id: int, new_status: str):
            try:
                from db import DatabaseManager
                db = DatabaseManager(self.db_path)
                await db.connect()
                result = await db.update_entry_status(entry_id, new_status)
                await db.close()

                if result:
                    await ctx.send(f"Updated entry {entry_id} to {new_status}")
                else:
                    await ctx.send("Failed to update entry")
            except Exception as err:
                logger.error(f"Update command error: {err}")
                await ctx.send(f"Error: {err}")

        @self.bot.command(name="delete")
        async def delete_command(ctx, entry_id: int):
            try:
                from db import DatabaseManager
                db = DatabaseManager(self.db_path)
                await db.connect()
                result = await db.delete_entry(entry_id)
                await db.close()

                if result:
                    await ctx.send(f"Deleted entry {entry_id}")
                else:
                    await ctx.send("Failed to delete entry")
            except Exception as err:
                logger.error(f"Delete command error: {err}")
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

    bot = HouseholdAgentDiscordBot(token=token, prefix=prefix)
    await bot.start()


if __name__ == "__main__":
    if not DISCORD_AVAILABLE:
        print("Error: discord.py is not installed")
        print("Install with: pip install -r requirements.txt")
        sys.exit(1)

    asyncio.run(main())
