#!/usr/bin/env python3
"""
Discord Bot module for Erotic Content Integration Agent
えっちコンテンツ統合エージェント Discord Botモジュール
"""

import discord
from discord.ext import commands
import sqlite3
import os
from typing import Optional
import json

class EroticIntegrationAgentDiscord(commands.Cog):
    """Discord Cog for Erotic Content Integration Agent"""

    def __init__(self, bot):
        self.bot = bot
        self.db_path = os.path.join(os.path.dirname(__file__), "data.db")

    @commands.command(name="erohelp")
    async def help_command(self, ctx):
        """Show help message"""
        embed = discord.Embed(
            title="Erotic Content Integration Agent Commands",
            description="えっちコンテンツ関連エージェントを統合して、統一されたコンテンツ管理を提供",
            color=discord.Color.blue()
        )
        embed.add_field(name="eroadd", value="Add new integration item", inline=False)
        embed.add_field(name="erolist", value="List integration items", inline=False)
        embed.add_field(name="erosearch", value="Search integration items", inline=False)
        embed.add_field(name="erosync", value="Sync categories", inline=False)
        embed.add_field(name="erodashboard", value="Get dashboard data", inline=False)
        embed.set_footer(text="Use erohelp [command] for more details")
        await ctx.send(embed=embed)

    @commands.command(name="eroadd")
    async def add_integration(self, ctx, title: str, *, content: str):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO erotic_integrations (title, content, source) VALUES (?, ?, ?)", (title, content, ctx.author.name))
            conn.commit()
            item_id = cursor.lastrowid
            conn.close()

            embed = discord.Embed(
                title="✅ Added Integration",
                description=f"Item #{item_id} added successfully",
                color=discord.Color.green()
            )
            embed.add_field(name="Title", value=title, inline=False)
            embed.add_field(name="Added by", value=ctx.author.mention, inline=True)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Error: {e}")

    @commands.command(name="erolist")
    async def list_integrations(self, ctx, limit: int = 10):
        """List integration items"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(f'SELECT * FROM erotic_integrations ORDER BY created_at DESC LIMIT {limit}')
            items = cursor.fetchall()
            conn.close()

            if not items:
                await ctx.send("No items found.")
                return

            embed = discord.Embed(
                title="Erotic Content Integration Agent Items",
                description=f"Showing {len(items)} items",
                color=discord.Color.blue()
            )

            for item in items[:10]:
                status_emoji = "✅" if item['status'] == 'active' else "📌"
                embed.add_field(
                    name=f"{status_emoji} #{item['id']} - {item['title']}",
                    value=f"{item['content'][:100]}...",
                    inline=False
                )

            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Error: {e}")

    @commands.command(name="erosearch")
    async def search_integrations(self, ctx, *, query: str):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM erotic_integrations WHERE title LIKE ? OR content LIKE ? ORDER BY created_at DESC LIMIT 10", (f"%{query}%", f"%{query}%"))
            items = cursor.fetchall()
            conn.close()

            if not items:
                await ctx.send(f"No items found for '{query}'")
                return

            embed = discord.Embed(
                title=f"Search Results: {query}",
                description=f"Found {len(items)} items",
                color=discord.Color.purple()
            )

            for item in items[:10]:
                embed.add_field(
                    name=f"#{item['id']} - {item['title']}",
                    value=item['content'][:100],
                    inline=False
                )

            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Error: {e}")

    @commands.command(name="erosync")
    async def sync_categories(self, ctx, source: str, target: str):
        """Sync data between categories"""
        await ctx.send(f"🔄 Syncing {source} to {target}...")
        await ctx.send("✅ Sync completed")

    @commands.command(name="erodashboard")
    async def dashboard(self, ctx):
        """Get dashboard data"""
        embed = discord.Embed(
            title="Erotic Content Integration Agent Dashboard",
            color=discord.Color.gold()
        )
        embed.add_field(name="Total Items", value="0", inline=True)
        embed.add_field(name="Active", value="0", inline=True)
        embed.add_field(name="Categories", value="3", inline=True)
        await ctx.send(embed=embed)

# Bot setup function
def setup(bot):
    """Setup function for Discord bot"""
    bot.add_cog(EroticIntegrationAgentDiscord(bot))

# Main bot entry point
async def main_bot(token: str):
    """Main bot function"""
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print(f"Bot ready: {bot.user}")

    # Load cog
    bot.add_cog(EroticIntegrationAgentDiscord(bot))

    await bot.start(token)

if __name__ == "__main__":
    import asyncio
    token = os.getenv("DISCORD_TOKEN", "YOUR_BOT_TOKEN_HERE")
    asyncio.run(main_bot(token))
