#!/usr/bin/env python3
"""
grafana-integrator-agent - Discord Botモジュール
"""

import discord
from discord.ext import commands
from db import GrafanaIntegratorAgentDB

class GrafanaIntegratorAgentDiscordBot(commands.Bot):
    """grafana-integrator-agent Discord Bot"""

    def __init__(self, db_path: str = "grafana-integrator-agent.db"):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.db = GrafanaIntegratorAgentDB(db_path)

    async def setup_hook(self):
        """Bot起動時の処理"""
        print(f"{self.__class__.__name__} is ready!")

    async def on_ready(self):
        """Bot準備完了時の処理"""
        print(f"Logged in as {self.user}")

    @commands.command()
    async def status(self, ctx: commands.Context):
        """ステータス表示"""
        entries = self.db.list_entries(limit=1)
        await ctx.send(f"{self.__class__.__name__} is running! Total entries: {len(entries)}")

    @commands.command()
    async def add(self, ctx: commands.Context, title: str, *, content: str):
        """エントリー追加"""
        entry_id = self.db.add_entry(title, content)
        await ctx.send(f"Added entry with ID: {entry_id}")

    @commands.command()
    async def list(self, ctx: commands.Context, limit: int = 10):
        """エントリー一覧"""
        entries = self.db.list_entries(limit=limit)
        if entries:
            response = "**Entries:**\n"
            for entry in entries:
                response += f"- #{entry['id']}: {entry['title']}\n"
            await ctx.send(response)
        else:
            await ctx.send("No entries found.")

def main():
    """メイン関数"""
    bot = GrafanaIntegratorAgentDiscordBot()
    # bot.run("YOUR_DISCORD_BOT_TOKEN")

if __name__ == "__main__":
    main()
