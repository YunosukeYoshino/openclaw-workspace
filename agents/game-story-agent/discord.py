#!/usr/bin/env python3
"""
Discord integration for game-story-agent
"""

import discord
from discord.ext import commands
import logging

class Game_Story_AgentDiscord(commands.Cog):
    """Discord bot for game-story-agent"""

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.command(name="game_story_agent")
    async def main_command(self, ctx, *, query=None):
        """Main command for game-story-agent"""
        if not query:
            await ctx.send("Please provide a query.")
            return

        self.logger.info(f"Command invoked by {ctx.author}: {query}")
        # TODO: Implement command logic
        await ctx.send(f"Processing: {query}")

    @commands.command(name="game_story_agent_status")
    async def status_command(self, ctx):
        """Status command for game-story-agent"""
        await ctx.send(f"Game Story Agent is operational.")

def setup(bot):
    """Setup the Discord cog"""
    bot.add_cog(Game_Story_AgentDiscord(bot))

if __name__ == "__main__":
    # Example usage
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)
    setup(bot)
