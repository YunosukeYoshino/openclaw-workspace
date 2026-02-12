#!/usr/bin/env python3
"""
Audio Agent - 音楽管理エージェント
Audio Agent - Manage audio files and playlists
"""

import discord
from discord.ext import commands

class MainBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        # discord.py cogをロード
        try:
            from discord import AudioCog
            await self.add_cog(AudioCog(self))
        except ImportError:
            pass

if __name__ == '__main__':
    bot = MainBot()
    import os
    token = os.getenv('DISCORD_BOT_TOKEN')
    bot.run(token)
