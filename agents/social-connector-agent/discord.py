#!/usr/bin/env python3
"""
Discord Bot module for Social Connector Agent
ソーシャルコネクターエージェント Discord Botモジュール
"""

import discord
from discord.ext import commands
import sqlite3
import os
from typing import Optional

class SocialConnectorAgentDiscord(commands.Cog):
    """Discord Cog for Social Connector Agent"""

    def __init__(self, bot):
        self.bot = bot
        self.db_path = os.path.join(os.path.dirname(__file__), "data.db")

    @commands.command(name="sochelp")
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="Social Connector Agent Commands",
            description="ソーシャル関係管理とリマインダー",
            color=discord.Color.blue()
        )
        embed.add_field(name="socadd", value="Add new item", inline=False)
        embed.add_field(name="soclist", value="List items", inline=False)
        embed.add_field(name="socupdate", value="Update item", inline=False)
        embed.add_field(name="socdelete", value="Delete item", inline=False)
        embed.add_field(name="socsummary", value="Get summary", inline=False)
        embed.set_footer(text="Lifestyle management")
        await ctx.send(embed=embed)

    @commands.command(name="socadd")
    async def add_item(self, ctx, title: str, *, content: str):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO contacts (title, content, source) VALUES (?, ?, ?)", (title, content, ctx.author.name))
            conn.commit()
            item_id = cursor.lastrowid
            conn.close()

            embed = discord.Embed(
                title="✅ Added",
                description=f"Item #{item_id}",
                color=discord.Color.green()
            )
            embed.add_field(name="Title", value=title, inline=False)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Error: {e}")

    @commands.command(name="soclist")
    async def list_items(self, ctx, limit: int = 10):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM contacts ORDER BY priority DESC, created_at DESC LIMIT {limit}")
            items = cursor.fetchall()
            conn.close()

            if not items:
                await ctx.send("No items found.")
                return

            embed = discord.Embed(
                title="Items",
                color=discord.Color.blue()
            )
            for item in items[:10]:
                status_emoji = "✅" if item['status'] == 'active' else "📌"
                embed.add_field(name=f"{status_emoji} #{item['id']} - {item['title']}", value=item['content'][:100], inline=False)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Error: {e}")

    @commands.command(name="socsummary")
    async def summary(self, ctx):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as total, COUNT(CASE WHEN status='active' THEN 1 END) as active FROM contacts")
            result = cursor.fetchone()
            conn.close()

            embed = discord.Embed(
                title="Summary",
                color=discord.Color.gold()
            )
            embed.add_field(name="Total", value=str(result['total']), inline=True)
            embed.add_field(name="Active", value=str(result['active']), inline=True)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Error: {e}")

def setup(bot):
    bot.add_cog(SocialConnectorAgentDiscord(bot))

async def main_bot(token: str):
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print(f"Bot ready: {bot.user}")

    bot.add_cog(SocialConnectorAgentDiscord(bot))
    await bot.start(token)

if __name__ == "__main__":
    import asyncio
    token = os.getenv("DISCORD_TOKEN", "YOUR_BOT_TOKEN_HERE")
    asyncio.run(main_bot(token))
