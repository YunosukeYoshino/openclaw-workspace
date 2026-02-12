#!/usr/bin/env python3
"""
Book Agent - 本管理エージェント
Book Agent - Track and manage books
"""

import discord
from discord.ext import commands
from db import BookDatabase

class BookAgent(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        self.db = BookDatabase()

    async def setup_hook(self):
        await self.add_command(self.add_book)
        await self.add_command(self.list_books)
        await self.add_command(self.show_book)
        await self.add_command(self.update_book)
        await self.add_command(self.delete_book)
        await self.add_command(self.mark_read)
        await self.add_command(self.search)

    @commands.command(name='add-book')
    async def add_book(self, ctx, *, args: str):
        """本を追加 / Add a book"""
        try:
            parts = args.split('|', 6)
            if len(parts) < 2:
                await ctx.send("使い方: !add-book タイトル|著者|ISBN|ステータス|評価|メモ|タグ\nUsage: !add-book title|author|isbn|status|rating|notes|tags")
                return

            title = parts[0].strip()
            author = parts[1].strip()
            isbn = parts[2].strip() if len(parts) > 2 else ""
            status = parts[3].strip() if len(parts) > 3 else "to-read"
            rating = parts[4].strip() if len(parts) > 4 else ""
            notes = parts[5].strip() if len(parts) > 5 else ""
            tags = parts[6].strip() if len(parts) > 6 else ""

            record = {
                'title': title,
                'author': author,
                'isbn': isbn,
                'status': status,
                'rating': rating,
                'notes': notes,
                'tags': tags
            }

            self.db.add_book(record)
            await ctx.send(f"📚 本を追加しました！\n{title} - {author}\nBook added! (ID: {record['id']})")
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='list-books')
    async def list_books(self, ctx, status: str = None):
        """本を一覧表示 / List books"""
        try:
            records = self.db.get_all_books()

            if not records:
                await ctx.send("本が見つかりませんでした。\nNo books found.")
                return

            if status:
                records = [r for r in records if r.get('status') == status]

            response = "📚 本リスト / Book List\n\n"
            for r in records:
                status_emoji = {"to-read": "📖", "reading": "📕", "completed": "✅"}.get(r.get('status'), "📚")
                response += f"{status_emoji} **{r['title']}** - {r['author']}\n"
                if r.get('rating'):
                    response += f"   評価: {r['rating']}\n"
                if r.get('tags'):
                    response += f"   タグ: {r['tags']}\n"
                response += f"   作成: {r['created_at']}\n\n"

            await ctx.send(response[:2000])
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='show-book')
    async def show_book(self, ctx, book_id: int):
        """本の詳細を表示 / Show book details"""
        try:
            record = self.db.get_book(book_id)

            if not record:
                await ctx.send(f"本が見つかりません (ID: {book_id})\nBook not found (ID: {book_id})")
                return

            status_text = {"to-read": "未読", "reading": "読書中", "completed": "完了"}.get(record.get('status'), record.get('status'))

            response = f"📚 **{record['title']}**\n"
            response += f"著者 / Author: {record['author']}\n"
            if record.get('isbn'):
                response += f"ISBN: {record['isbn']}\n"
            response += f"ステータス / Status: {status_text}\n"
            if record.get('rating'):
                response += f"評価 / Rating: {record['rating']}\n"
            if record.get('notes'):
                response += f"メモ / Notes: {record['notes']}\n"
            if record.get('tags'):
                response += f"タグ / Tags: {record['tags']}\n"
            response += f"作成日 / Created: {record['created_at']}"

            await ctx.send(response)
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='update-book')
    async def update_book(self, ctx, book_id: int, *, args: str):
        """本を更新 / Update a book"""
        try:
            parts = args.split('|', 6)
            updates = {}
            if len(parts) > 0 and parts[0].strip():
                updates['title'] = parts[0].strip()
            if len(parts) > 1 and parts[1].strip():
                updates['author'] = parts[1].strip()
            if len(parts) > 2 and parts[2].strip():
                updates['isbn'] = parts[2].strip()
            if len(parts) > 3 and parts[3].strip():
                updates['status'] = parts[3].strip()
            if len(parts) > 4 and parts[4].strip():
                updates['rating'] = parts[4].strip()
            if len(parts) > 5 and parts[5].strip():
                updates['notes'] = parts[5].strip()
            if len(parts) > 6 and parts[6].strip():
                updates['tags'] = parts[6].strip()

            self.db.update_book(book_id, updates)
            await ctx.send(f"✅ 本を更新しました (ID: {book_id})\nBook updated (ID: {book_id})")
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='delete-book')
    async def delete_book(self, ctx, book_id: int):
        """本を削除 / Delete a book"""
        try:
            self.db.delete_book(book_id)
            await ctx.send(f"🗑️ 本を削除しました (ID: {book_id})\nBook deleted (ID: {book_id})")
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='mark-read')
    async def mark_read(self, ctx, book_id: int, rating: str = None):
        """本を完了としてマーク / Mark book as read"""
        try:
            updates = {'status': 'completed'}
            if rating:
                updates['rating'] = rating

            self.db.update_book(book_id, updates)
            await ctx.send(f"✅ 本を完了しました！ (ID: {book_id})\nBook marked as read! (ID: {book_id})")
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='search-books')
    async def search(self, ctx, query: str):
        """本を検索 / Search books"""
        try:
            records = self.db.get_all_books()

            if not records:
                await ctx.send("本が見つかりませんでした。\nNo books found.")
                return

            query_lower = query.lower()
            results = [r for r in records if query_lower in r.get('title', '').lower() or query_lower in r.get('author', '').lower()]

            if not results:
                await ctx.send(f"検索結果が見つかりませんでした: {query}\nNo results found for: {query}")
                return

            response = f"📚 検索結果 / Search Results: {query}\n\n"
            for r in results:
                response += f"📖 **{r['title']}** - {r['author']}\n\n"

            await ctx.send(response[:2000])
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

if __name__ == '__main__':
    bot = BookAgent()
    import os
    token = os.getenv('DISCORD_BOT_TOKEN')
    bot.run(token)
