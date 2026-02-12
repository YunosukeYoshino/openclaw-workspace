#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Habit Agent - Discord Bot
習慣トラッカーエージェント - Discord ボット
"""

import discord
from discord.ext import commands
import os
from discord import parse_message, handle_message

class HabitAgent(commands.Bot):
    """Habit Tracking Discord Bot"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!habit ', intents=intents)

    async def setup_hook(self):
        """Setup hook when bot starts"""
        print(f'{self.user} has connected to Discord!')

    async def on_ready(self):
        """Called when bot is ready"""
        print(f'Logged in as {self.user.name} (ID: {self.user.id})')
        print('------')
        activity = discord.Activity(type=discord.ActivityType.watching, name="habits 🔄")
        await self.change_presence(activity=activity)

    async def on_message(self, message):
        """Handle messages"""
        if message.author.bot:
            return

        # Check if message starts with bot prefix
        if message.content.startswith(self.command_prefix):
            await self.process_commands(message)
            return

        # Try to parse and handle the message
        response = handle_message(message.content)
        if response:
            await message.channel.send(response)

    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"⚠️ 必要な引数が不足しています: {error.param.name}")
        else:
            print(f'Error: {error}')
            await ctx.send("❌ エラーが発生しました。")

# Bot instance
bot = HabitAgent()

@bot.command(name='add', aliases=['追加'])
async def add_habit_cmd(ctx, *, content: str):
    """Add a habit"""
    parsed = parse_message(f"習慣: {content}")
    if parsed and parsed.get('action') == 'add':
        response = handle_message(f"習慣: {content}")
        await ctx.send(response)
    else:
        await ctx.send("❌ フォーマットが正しくありません。例: `!habit add 早起き, 目標: 30日`")

@bot.command(name='log', aliases=['記録'])
async def log_habit_cmd(ctx, habit_id: int):
    """Log a habit completion"""
    response = handle_message(f"記録: {habit_id}")
    await ctx.send(response)

@bot.command(name='search', aliases=['検索'])
async def search(ctx, keyword: str):
    """Search habits"""
    response = handle_message(f"検索: {keyword}")
    await ctx.send(response)

@bot.command(name='list', aliases=['一覧', 'list'])
async def list_habits(ctx):
    """List all habits"""
    response = handle_message("習慣一覧")
    await ctx.send(response)

@bot.command(name='help', aliases=['ヘルプ', '使い方'])
async def help_command(ctx):
    """Show help"""
    embed = discord.Embed(
        title="🔄 Habit Agent - ヘルプ",
        description="習慣の記録とストリーク追跡！",
        color=discord.Color.orange()
    )

    embed.add_field(name="🔄 習慣追加", value="`!habit add <習慣名>, 頻度:日/週/月` - 習慣追加", inline=False)
    embed.add_field(name="✅ 記録", value="`!habit log <ID>` - 習慣完了を記録", inline=False)
    embed.add_field(name="🔍 検索", value="`!habit search <キーワード>` - 習慣検索", inline=False)
    embed.add_field(name="📋 一覧", value="`!habit list` - 習慣一覧とストリーク", inline=False)
    embed.add_field(name="💬 自動解析", value="メッセージを入力すると自動解析されます", inline=False)

    embed.set_footer(text="コマンドは `!habit ` で始まります")
    await ctx.send(embed=embed)

def main():
    """Run the bot"""
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("Error: DISCORD_TOKEN environment variable not set")
        return

    bot.run(token)

if __name__ == '__main__':
    main()
