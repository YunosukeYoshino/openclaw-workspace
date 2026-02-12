#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gift Agent - Discord Bot
ギフト記録エージェント - Discord ボット
"""

import discord
from discord.ext import commands
import os
from discord import parse_message, handle_message

class GiftAgent(commands.Bot):
    """Gift Management Discord Bot"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!gift ', intents=intents)

    async def setup_hook(self):
        """Setup hook when bot starts"""
        print(f'{self.user} has connected to Discord!')

    async def on_ready(self):
        """Called when bot is ready"""
        print(f'Logged in as {self.user.name} (ID: {self.user.id})')
        print('------')
        activity = discord.Activity(type=discord.ActivityType.watching, name="gifts 🎁")
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
bot = GiftAgent()

@bot.command(name='add', aliases=['追加', 'add'])
async def add_gift(ctx, *, content: str):
    """Add a gift record"""
    parsed = parse_message(f"ギフト: {content}")
    if parsed and parsed.get('action') == 'add_gift':
        response = handle_message(f"ギフト: {content}")
        await ctx.send(response)
    else:
        await ctx.send("❌ フォーマットが正しくありません。例: `!gift add 誕生日ケーキ, 宛: 田中さん`")

@bot.command(name='idea', aliases=['アイデア', 'idea'])
async def add_idea(ctx, *, content: str):
    """Add a gift idea"""
    parsed = parse_message(f"アイデア: {content}")
    if parsed and parsed.get('action') == 'add_idea':
        response = handle_message(f"アイデア: {content}")
        await ctx.send(response)
    else:
        await ctx.send("❌ フォーマットが正しくありません。例: `!gift idea 母, 花束`")

@bot.command(name='list', aliases=['一覧', 'list'])
async def list_gifts(ctx):
    """List all gifts"""
    response = handle_message("ギフト一覧")
    await ctx.send(response)

@bot.command(name='ideas', aliases=['アイデア一覧'])
async def list_ideas(ctx):
    """List all gift ideas"""
    response = handle_message("アイデア一覧")
    await ctx.send(response)

@bot.command(name='stats', aliases=['統計', 'stats'])
async def show_stats(ctx):
    """Show gift statistics"""
    response = handle_message("統計")
    await ctx.send(response)

@bot.command(name='help', aliases=['ヘルプ', '使い方'])
async def help_command(ctx):
    """Show help"""
    embed = discord.Embed(
        title="🎁 Gift Agent - ヘルプ",
        description="ギフトの記録とアイデア管理！",
        color=discord.Color.purple()
    )

    embed.add_field(name="🎁 ギフト追加", value="`!gift add <アイテム>, 宛: <相手>` - ギフト記録", inline=False)
    embed.add_field(name="💡 アイデア追加", value="`!gift idea <相手>, <アイテム>` - アイデア追加", inline=False)
    embed.add_field(name="📋 一覧", value="`!gift list` - ギフト一覧\n`!gift ideas` - アイデア一覧", inline=False)
    embed.add_field(name="📊 統計", value="`!gift stats` - 統計情報", inline=False)
    embed.add_field(name="💬 自動解析", value="メッセージを入力すると自動解析されます", inline=False)

    embed.set_footer(text="コマンドは `!gift ` で始まります")
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
