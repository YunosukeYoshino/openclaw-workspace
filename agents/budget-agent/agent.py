#!/usr/bin/env python3
"""
Budget Agent - 予算管理エージェント
Budget Agent - Manage budgets
"""

import discord
from discord.ext import commands
from db import BudgetDatabase

class BudgetAgent(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        self.db = BudgetDatabase()

    async def setup_hook(self):
        await self.add_command(self.add_budget)
        await self.add_command(self.list_budgets)
        await self.add_command(self.show_budget)
        await self.add_command(self.update_budget)
        await self.add_command(self.delete_budget)

    @commands.command(name='add-budget')
    async def add_budget(self, ctx, *, args: str):
        """予算を追加 / Add a budget"""
        try:
            parts = args.split('|', 4)
            if len(parts) < 3:
                await ctx.send("使い方: !add-budget 名前|カテゴリ|金額|期間|説明\nUsage: !add-budget name|category|amount|period|description")
                return

            name = parts[0].strip()
            category = parts[1].strip()
            amount = float(parts[2].strip())
            period = parts[3].strip() if len(parts) > 3 else "monthly"
            description = parts[4].strip() if len(parts) > 4 else ""

            record = {
                'name': name,
                'category': category,
                'amount': amount,
                'period': period,
                'description': description
            }

            self.db.add_budget(record)
            await ctx.send(f"💰 予算を追加しました！\n{name} - {amount}\nBudget added! (ID: {record['id']})")
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='list-budgets')
    async def list_budgets(self, ctx, category: str = None):
        """予算を一覧表示 / List budgets"""
        try:
            budgets = self.db.get_all_budgets()

            if not budgets:
                await ctx.send("予算が見つかりませんでした。\nNo budgets found.")
                return

            if category:
                budgets = [b for b in budgets if b.get('category') == category]

            response = "💰 予算リスト / Budget List\n\n"
            for b in budgets:
                response += f"💰 **{b['name']}** - {b['amount']} ({b['period']})\n"
                if b.get('category'):
                    response += f"   カテゴリ: {b['category']}\n"
                if b.get('description'):
                    response += f"   {b['description'][:30]}...\n"
                response += f"   作成: {b['created_at']}\n\n"

            await ctx.send(response[:2000])
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='show-budget')
    async def show_budget(self, ctx, budget_id: int):
        """予算の詳細を表示 / Show budget details"""
        try:
            budget = self.db.get_budget(budget_id)

            if not budget:
                await ctx.send(f"予算が見つかりません (ID: {budget_id})\nBudget not found (ID: {budget_id})")
                return

            response = f"💰 **{budget['name']}**\n"
            response += f"金額 / Amount: {budget['amount']}\n"
            if budget.get('category'):
                response += f"カテゴリ / Category: {budget['category']}\n"
            response += f"期間 / Period: {budget['period']}\n"
            if budget.get('description'):
                response += f"説明 / Description: {budget['description']}\n"
            response += f"作成日 / Created: {budget['created_at']}"

            await ctx.send(response)
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='update-budget')
    async def update_budget(self, ctx, budget_id: int, *, args: str):
        """予算を更新 / Update a budget"""
        try:
            parts = args.split('|', 4)
            updates = {}
            if len(parts) > 0 and parts[0].strip():
                updates['name'] = parts[0].strip()
            if len(parts) > 1 and parts[1].strip():
                updates['category'] = parts[1].strip()
            if len(parts) > 2 and parts[2].strip():
                updates['amount'] = float(parts[2].strip())
            if len(parts) > 3 and parts[3].strip():
                updates['period'] = parts[3].strip()
            if len(parts) > 4 and parts[4].strip():
                updates['description'] = parts[4].strip()

            self.db.update_budget(budget_id, updates)
            await ctx.send(f"✅ 予算を更新しました (ID: {budget_id})\nBudget updated (ID: {budget_id})")
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='delete-budget')
    async def delete_budget(self, ctx, budget_id: int):
        """予算を削除 / Delete a budget"""
        try:
            self.db.delete_budget(budget_id)
            await ctx.send(f"🗑️ 予算を削除しました (ID: {budget_id})\nBudget deleted (ID: {budget_id})")
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

if __name__ == '__main__':
    bot = BudgetAgent()
    import os
    token = os.getenv('DISCORD_BOT_TOKEN')
    bot.run(token)
