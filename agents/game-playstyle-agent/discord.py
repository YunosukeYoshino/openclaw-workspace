#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Game Playstyle Agent Discord Bot Module
ゲームプレイスタイル分析エージェント Discord Botモジュール
"""

import discord
from discord.ext import commands
from pathlib import Path

class GamePlaystyleAgentDiscord(commands.Cog):
    """Game Playstyle Agent Discord Bot"""

    def __init__(self, bot, agent=None):
        self.bot = bot
        self.agent = agent

    @commands.command()
    async def gameplaystyleagent(self, ctx):
        """Main command"""
        await ctx.send("Game Playstyle Agent Bot running")

def setup(bot, agent=None):
    """Cogをセットアップ"""
    bot.add_cog(GamePlaystyleAgentDiscord(bot, agent))

def main():
    """メイン関数"""
    print("Game Playstyle Agent Discord Bot Module")

if __name__ == "__main__":
    main()
