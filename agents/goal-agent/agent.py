#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Goal Agent - Discord Bot
目標追跡エージェント - Discord ボット
"""

import discord
from discord.ext import commands
import os
from discord import parse_message, handle_message

class GoalAgent(commands.Bot):
    """Goal Tracking Discord Bot"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!goal ', intents=intents)

    async def setup_hook(self):
        """Setup hook when bot starts"""
        print(f'{self.user} has connected to Discord!')

    async def on_ready(self):
        """Called when bot is ready"""
        print(f'Logged in as {self.user.name} (ID: {self.user.id})')
        print('------')
        activity = discord.Activity(type=discord.ActivityType.watching, name="goals 🎯")
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
bot = GoalAgent()

@bot.command(name='add', aliases=['追加'])
async def add_goal(ctx, *, content: str):
    """Add a goal"""
    parsed = parse_message(f"目標: {content}")
    if parsed and parsed.get('action') == 'add_goal':
        response = handle_message(f"目標: {content}")
        await ctx.send(response)
    else:
        await ctx.send("❌ フォーマットが正しくありません。例: `!goal add 新しい言語を学ぶ, 優先:高`")

@bot.command(name='progress', aliases=['進捗'])
async def update_progress(ctx, goal_id: int, progress: int):
    """Update goal progress"""
    if progress < 0 or progress > 100:
        await ctx.send("❌ 進捗は 0 から 100 の間で指定してください")
        return

    response = handle_message(f"進捗: {goal_id} {progress}")
    await ctx.send(response)

@bot.command(name='complete', aliases=['完了'])
async def complete(ctx, goal_id: int):
    """Mark a goal as complete"""
    response = handle_message(f"完了: {goal_id}")
    await ctx.send(response)

@bot.command(name='list', aliases=['一覧', 'list'])
async def list_goals(ctx):
    """List all goals"""
    response = handle_message("目標一覧")
    await ctx.send(response)

@bot.command(name='stats', aliases=['統計', 'stats'])
async def show_stats(ctx):
    """Show goal statistics"""
    response = handle_message("統計")
    await ctx.send(response)

@bot.command(name='help', aliases=['ヘルプ', '使い方'])
async def help_command(ctx):
    """Show help"""
    embed = discord.Embed(
        title="🎯 Goal Agent - ヘルプ",
        description="目標の追跡と達成！",
        color=discord.Color.gold()
    )

    embed.add_field(name="🎯 目標追加", value="`!goal add <タイトル>, 優先:高/中/低` - 目標追加", inline=False)
    embed.add_field(name="📈 進捗更新", value="`!goal progress <ID> <進捗%>` - 進捗更新", inline=False)
    embed.add_field(name="🎉 完了", value="`!goal complete <ID>` - 目標完了", inline=False)
    embed.add_field(name="📋 一覧", value="`!goal list` - 目標一覧", inline=False)
    embed.add_field(name="📊 統計", value="`!goal stats` - 統計情報", inline=False)
    embed.add_field(name="💬 自動解析", value="メッセージを入力すると自動解析されます", inline=False)

    embed.set_footer(text="コマンドは `!goal ` で始まります")
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
