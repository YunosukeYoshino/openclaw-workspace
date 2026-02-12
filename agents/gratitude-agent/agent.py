#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gratitude Agent - Discord Bot
グラティチュードエージェント - Discord ボット
"""

import discord
from discord.ext import commands
import os
from discord import parse_message, handle_message

class GratitudeAgent(commands.Bot):
    """Gratitude Journal Discord Bot"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!gratitude ', intents=intents)

    async def setup_hook(self):
        """Setup hook when bot starts"""
        print(f'{self.user} has connected to Discord!')

    async def on_ready(self):
        """Called when bot is ready"""
        print(f'Logged in as {self.user.name} (ID: {self.user.id})')
        print('------')
        activity = discord.Activity(type=discord.ActivityType.watching, name="gratitude 🙏")
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
bot = GratitudeAgent()

@bot.command(name='add', aliases=['追加'])
async def add_gratitude(ctx, *, content: str):
    """Add a gratitude entry"""
    parsed = parse_message(f"感謝: {content}")
    if parsed and parsed.get('action') == 'add':
        response = handle_message(f"感謝: {content}")
        await ctx.send(response)
    else:
        await ctx.send("❌ フォーマットが正しくありません。例: `!gratitude add 家族、仕事、健康`")

@bot.command(name='multi', aliases=['複数追加'])
async def add_multi(ctx, *, content: str):
    """Add multiple gratitude entries"""
    parsed = parse_message(f"感謝: {content}")
    if parsed and parsed.get('action') == 'add_multi':
        response = handle_message(f"感謝: {content}")
        await ctx.send(response)
    else:
        await ctx.send("❌ フォーマットが正しくありません。例: `!gratitude multi 家族、仕事、健康`")

@bot.command(name='update', aliases=['更新'])
async def update(ctx, gratitude_id: int, *, content: str):
    """Update a gratitude entry"""
    response = handle_message(f"更新: {gratitude_id} {content}")
    await ctx.send(response)

@bot.command(name='delete', aliases=['削除', 'remove'])
async def delete(ctx, gratitude_id: int):
    """Delete a gratitude entry"""
    response = handle_message(f"削除: {gratitude_id}")
    await ctx.send(response)

@bot.command(name='search', aliases=['検索'])
async def search(ctx, keyword: str):
    """Search gratitude entries"""
    response = handle_message(f"検索: {keyword}")
    await ctx.send(response)

@bot.command(name='list', aliases=['一覧', 'list'])
async def list_gratitude(ctx):
    """List all gratitude entries"""
    response = handle_message("感謝一覧")
    await ctx.send(response)

@bot.command(name='today', aliases=['今日'])
async def today(ctx):
    """Show today's gratitude"""
    response = handle_message("今日")
    await ctx.send(response)

@bot.command(name='yesterday', aliases=['昨日'])
async def yesterday(ctx):
    """Show yesterday's gratitude"""
    response = handle_message("昨日")
    await ctx.send(response)

@bot.command(name='week', aliases=['今週'])
async def this_week(ctx):
    """Show this week's gratitude"""
    response = handle_message("今週")
    await ctx.send(response)

@bot.command(name='categories', aliases=['カテゴリ'])
async def list_categories(ctx):
    """List categories"""
    response = handle_message("カテゴリ")
    await ctx.send(response)

@bot.command(name='stats', aliases=['統計', 'stats'])
async def show_stats(ctx):
    """Show gratitude statistics"""
    response = handle_message("統計")
    await ctx.send(response)

@bot.command(name='help', aliases=['ヘルプ', '使い方'])
async def help_command(ctx):
    """Show help"""
    embed = discord.Embed(
        title="🙏 Gratitude Agent - ヘルプ",
        description="感謝日記を記録しよう！",
        color=discord.Color.teal()
    )

    embed.add_field(name="🙏 追加", value="`!gratitude add <感謝内容>` - 感謝追加\n`!gratitude multi <内容1>、<内容2>、<内容3>` - 複数追加", inline=False)
    embed.add_field(name="✏️ 編集", value="`!gratitude update <ID> <内容>` - 更新\n`!gratitude delete <ID>` - 削除", inline=False)
    embed.add_field(name="🔍 検索・一覧", value="`!gratitude search <キーワード>` - 検索\n`!gratitude list` - 一覧", inline=False)
    embed.add_field(name="📅 日別表示", value="`!gratitude today` - 今日\n`!gratitude yesterday` - 昨日\n`!gratitude week` - 今週", inline=False)
    embed.add_field(name="📊 統計", value="`!gratitude categories` - カテゴリ\n`!gratitude stats` - 統計", inline=False)
    embed.add_field(name="💬 自動解析", value="メッセージを入力すると自動解析されます", inline=False)

    embed.set_footer(text="コマンドは `!gratitude ` で始まります")
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
