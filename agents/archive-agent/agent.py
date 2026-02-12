#!/usr/bin/env python3
"""
Archive Agent - アーカイブ管理エージェント
Archive Agent - Manage archive items and categories
"""

import discord
from discord.ext import commands
from discord import ArchiveAgent

class MainBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        await self.add_cog(ArchiveAgent(self))

if __name__ == '__main__':
    bot = MainBot()
    import os
    token = os.getenv('DISCORD_BOT_TOKEN')
    bot.run(token)
