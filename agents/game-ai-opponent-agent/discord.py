#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Game AI Opponent Agent Discord Bot Module
ゲームAI対戦エージェント Discord Botモジュール
"""

import discord
from discord.ext import commands
from pathlib import Path

class GameAiOpponentAgentDiscord(commands.Cog):
    """Game AI Opponent Agent Discord Bot"""

    def __init__(self, bot, agent=None):
        self.bot = bot
        self.agent = agent

    @commands.command()
    async def gameaiopponentagent(self, ctx):
        """Main command"""
        await ctx.send("Game AI Opponent Agent Bot running")

def setup(bot, agent=None):
    """Cogをセットアップ"""
    bot.add_cog(GameAiOpponentAgentDiscord(bot, agent))

def main():
    """メイン関数"""
    print("Game AI Opponent Agent Discord Bot Module")

if __name__ == "__main__":
    main()
