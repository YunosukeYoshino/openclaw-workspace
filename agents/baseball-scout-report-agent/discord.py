#!/usr/bin/env python3
"""
Discord Bot Integration for 野球スカウトレポートエージェント / Baseball Scout Report Agent
"""

import discord
from discord.ext import commands
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class DiscordBot(commands.Bot):
    """Discord Bot for baseball-scout-report-agent"""

    def __init__(self, command_prefix: str = "!", db=None):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.db = db
        self.agent_id = "baseball-scout-report-agent"

    async def setup_hook(self):
        """Bot setup"""
        logger.info(f"Setting up {self.agent_id} Discord bot...")
        await self.add_cog(BaseballScoutReportAgentCommands(self))

    async def on_ready(self):
        """Bot is ready"""
        logger.info(f"{self.user.name} is ready!")


class BaseballScoutReportAgentCommands(commands.Cog):
    """Commands for baseball-scout-report-agent"""

    def __init__(self, bot: DiscordBot):
        self.bot = bot

    @commands.command(name="status")
    async def status(self, ctx: commands.Context):
        """Check agent status"""
        await ctx.send(f"✅ {self.bot.agent_id} is active!")

    @commands.command(name="help")
    async def help_command(self, ctx: commands.Context):
        """Show help"""
        help_text = f"""
📚 **野球スカウトレポートエージェント Help**

**Features:**
            - Report Mgmt
            - Multi-Scout Agg
            - Bias Correction
            - Player Compare
            - Projection
            - Tool Grading

**Commands:**
- `!status` - Check agent status
- `!help` - Show this help message
- `!create <title> <content>` - Create new entry
- `!list [category]` - List entries
- `!search <query>` - Search entries
- `!get <id>` - Get entry by ID
"""
        help_text = help_text.replace("baseball-scout-report-agent", agent['id'])
        help_text = help_text.replace("野球スカウトレポートエージェント", agent['name_ja'])
        help_text = help_text.replace("            - Report Mgmt
            - Multi-Scout Agg
            - Bias Correction
            - Player Compare
            - Projection
            - Tool Grading", features_list)
        help_text = help_text.replace("BaseballScoutReportAgent", snake_to_camel(agent['id']))
        await ctx.send(help_text)

    @commands.command(name="create")
    async def create_entry(self, ctx: commands.Context, title: str, *, content: str):
        """Create a new entry"""
        if self.bot.db:
            entry_id = await self.bot.db.create_entry(title, content)
            await ctx.send(f"✅ Created entry #{entry_id}")
        else:
            await ctx.send("❌ Database not connected")

    @commands.command(name="list")
    async def list_entries(self, ctx: commands.Context, category: str = None):
        """List entries"""
        if self.bot.db:
            entries = await self.bot.db.list_entries(category, limit=10)
            if entries:
                response = "📋 **Entries:\n"
                for entry in entries:
                    response += f"- #{entry['id']}: {entry['title']}\n"
                await ctx.send(response)
            else:
                await ctx.send("No entries found")
        else:
            await ctx.send("❌ Database not connected")

    @commands.command(name="search")
    async def search_entries(self, ctx: commands.Context, *, query: str):
        """Search entries"""
        if self.bot.db:
            entries = await self.bot.db.search_entries(query)
            if entries:
                response = f"🔍 **Search Results for '{query}':\n"
                for entry in entries:
                    response += f"- #{entry['id']}: {entry['title']}\n"
                await ctx.send(response)
            else:
                await ctx.send("No results found")
        else:
            await ctx.send("❌ Database not connected")

    @commands.command(name="get")
    async def get_entry(self, ctx: commands.Context, entry_id: int):
        """Get entry by ID"""
        if self.bot.db:
            entry = await self.bot.db.get_entry(entry_id)
            if entry:
                response = f"""
📄 **Entry #{entry['id']}**
**Title:** {entry['title']}
**Category:** {entry.get('category', 'N/A')}
**Content:** {entry['content'][:500]}
{'...' if len(entry['content']) > 500 else ''}
**Tags:** {', '.join(entry.get('tags', []))}
"""
                await ctx.send(response)
            else:
                await ctx.send(f"Entry #{entry_id} not found")
        else:
            await ctx.send("❌ Database not connected")


def create_bot(db, token: str, command_prefix: str = "!") -> DiscordBot:
    """Create and return Discord bot instance"""
    bot = DiscordBot(command_prefix=command_prefix, db=db)
    return bot
