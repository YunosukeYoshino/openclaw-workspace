#!/usr/bin/env python3
"""
Brainstorm Agent - ブレインストーミングエージェント
Brainstorm Agent - Capture and organize ideas
"""

import discord
from discord.ext import commands
from db import BrainstormDatabase

class BrainstormAgent(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        self.db = BrainstormDatabase()

    async def setup_hook(self):
        await self.add_command(self.add_idea)
        await self.add_command(self.list_ideas)
        await self.add_command(self.show_idea)
        await self.add_command(self.update_idea)
        await self.add_command(self.delete_idea)
        await self.add_command(self.search)

    @commands.command(name='add-idea')
    async def add_idea(self, ctx, *, args: str):
        """アイデアを追加 / Add an idea"""
        try:
            parts = args.split('|', 3)
            if len(parts) < 1:
                await ctx.send("使い方: !add-idea アイデア|カテゴリ|タグ|メモ\nUsage: !add-idea idea|category|tags|notes")
                return

            idea = parts[0].strip()
            category = parts[1].strip() if len(parts) > 1 else ""
            tags = parts[2].strip() if len(parts) > 2 else ""
            notes = parts[3].strip() if len(parts) > 3 else ""

            record = {
                'idea': idea,
                'category': category,
                'tags': tags,
                'notes': notes
            }

            self.db.add_idea(record)
            await ctx.send(f"💡 アイデアを追加しました！\n{idea}\nIdea added! (ID: {record['id']})")
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='list-ideas')
    async def list_ideas(self, ctx, category: str = None):
        """アイデアを一覧表示 / List ideas"""
        try:
            records = self.db.get_all_ideas()

            if not records:
                await ctx.send("アイデアが見つかりませんでした。\nNo ideas found.")
                return

            if category:
                records = [r for r in records if r.get('category') == category]

            response = "💡 アイデアリスト / Idea List\n\n"
            for r in records:
                response += f"💡 **{r['idea'][:50]}**... (ID: {r['id']})\n"
                if r.get('category'):
                    response += f"   カテゴリ: {r['category']}\n"
                if r.get('tags'):
                    response += f"   タグ: {r['tags']}\n"
                response += f"   作成: {r['created_at']}\n\n"

            await ctx.send(response[:2000])
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='show-idea')
    async def show_idea(self, ctx, idea_id: int):
        """アイデアの詳細を表示 / Show idea details"""
        try:
            record = self.db.get_idea(idea_id)

            if not record:
                await ctx.send(f"アイデアが見つかりません (ID: {idea_id})\nIdea not found (ID: {idea_id})")
                return

            response = f"💡 **アイデア #{record['id']}**\n"
            response += f"**{record['idea']}**\n\n"
            if record.get('category'):
                response += f"カテゴリ / Category: {record['category']}\n"
            if record.get('tags'):
                response += f"タグ / Tags: {record['tags']}\n"
            if record.get('notes'):
                response += f"メモ / Notes: {record['notes']}\n"
            response += f"作成日 / Created: {record['created_at']}"

            await ctx.send(response)
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='update-idea')
    async def update_idea(self, ctx, idea_id: int, *, args: str):
        """アイデアを更新 / Update an idea"""
        try:
            parts = args.split('|', 3)
            updates = {}
            if len(parts) > 0 and parts[0].strip():
                updates['idea'] = parts[0].strip()
            if len(parts) > 1 and parts[1].strip():
                updates['category'] = parts[1].strip()
            if len(parts) > 2 and parts[2].strip():
                updates['tags'] = parts[2].strip()
            if len(parts) > 3 and parts[3].strip():
                updates['notes'] = parts[3].strip()

            self.db.update_idea(idea_id, updates)
            await ctx.send(f"✅ アイデアを更新しました (ID: {idea_id})\nIdea updated (ID: {idea_id})")
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='delete-idea')
    async def delete_idea(self, ctx, idea_id: int):
        """アイデアを削除 / Delete an idea"""
        try:
            self.db.delete_idea(idea_id)
            await ctx.send(f"🗑️ アイデアを削除しました (ID: {idea_id})\nIdea deleted (ID: {idea_id})")
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='search-ideas')
    async def search(self, ctx, query: str):
        """アイデアを検索 / Search ideas"""
        try:
            records = self.db.get_all_ideas()

            if not records:
                await ctx.send("アイデアが見つかりませんでした。\nNo ideas found.")
                return

            query_lower = query.lower()
            results = [r for r in records if query_lower in r.get('idea', '').lower() or query_lower in r.get('tags', '').lower()]

            if not results:
                await ctx.send(f"検索結果が見つかりませんでした: {query}\nNo results found for: {query}")
                return

            response = f"💡 検索結果 / Search Results: {query}\n\n"
            for r in results:
                response += f"💡 **{r['idea'][:50]}**... (ID: {r['id']})\n\n"

            await ctx.send(response[:2000])
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

if __name__ == '__main__':
    bot = BrainstormAgent()
    import os
    token = os.getenv('DISCORD_BOT_TOKEN')
    bot.run(token)
