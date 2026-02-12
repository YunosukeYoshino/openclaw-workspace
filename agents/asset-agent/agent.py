#!/usr/bin/env python3
"""
Asset Agent - 資産管理エージェント
Asset Agent - Track and manage assets
"""

import discord
from discord.ext import commands
from db import asset_agentDB

class AssetAgent(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        self.db = asset_agentDB()

    async def setup_hook(self):
        await self.add_command(self.add_asset)
        await self.add_command(self.list_assets)
        await self.add_command(self.show_asset)
        await self.add_command(self.update_asset)
        await self.add_command(self.delete_asset)
        await self.add_command(self.stats)

    @commands.command(name='add-asset')
    async def add_asset(self, ctx, *, args: str):
        """資産を追加 / Add an asset"""
        try:
            parts = args.split('|', 4)
            if len(parts) < 3:
                await ctx.send("使い方: !add-asset 名前|種類|価値|説明|場所\nUsage: !add-asset name|type|value|description|location")
                return

            name = parts[0].strip()
            asset_type = parts[1].strip()
            value = parts[2].strip()
            description = parts[3].strip() if len(parts) > 3 else ""
            location = parts[4].strip() if len(parts) > 4 else ""

            record = {
                'name': name,
                'type': asset_type,
                'value': value,
                'description': description,
                'location': location
            }

            self.db.add_record(record)
            await ctx.send(f"✅ 資産を追加しました！\n{name} - {value}\nAsset added! (ID: {record['id']})")
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='list-assets')
    async def list_assets(self, ctx, asset_type: str = None):
        """資産を一覧表示 / List assets"""
        try:
            records = self.db.get_all_records()

            if not records:
                await ctx.send("資産が見つかりませんでした。\nNo assets found.")
                return

            response = "📊 資産リスト / Asset List\n\n"
            for r in records:
                response += f"💰 **{r['name']}** [{r.get('type', 'N/A')}]\n"
                response += f"   価値 / Value: {r.get('value', 'N/A')}\n"
                if r.get('description'):
                    response += f"   {r['description'][:30]}...\n"
                if r.get('location'):
                    response += f"   場所 / Location: {r['location']}\n"
                response += f"   作成: {r['created_at']}\n\n"

            await ctx.send(response[:2000])
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='show-asset')
    async def show_asset(self, ctx, asset_id: int):
        """資産の詳細を表示 / Show asset details"""
        try:
            record = self.db.get_record(asset_id)

            if not record:
                await ctx.send(f"資産が見つかりません (ID: {asset_id})\nAsset not found (ID: {asset_id})")
                return

            response = f"💰 **{record['name']}**\n"
            response += f"種類 / Type: {record.get('type', 'N/A')}\n"
            response += f"価値 / Value: {record.get('value', 'N/A')}\n"
            if record.get('description'):
                response += f"説明 / Description: {record['description']}\n"
            if record.get('location'):
                response += f"場所 / Location: {record['location']}\n"
            response += f"作成日 / Created: {record['created_at']}"

            await ctx.send(response)
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='update-asset')
    async def update_asset(self, ctx, asset_id: int, *, args: str):
        """資産を更新 / Update an asset"""
        try:
            parts = args.split('|', 4)
            updates = {}
            if len(parts) > 0 and parts[0].strip():
                updates['name'] = parts[0].strip()
            if len(parts) > 1 and parts[1].strip():
                updates['type'] = parts[1].strip()
            if len(parts) > 2 and parts[2].strip():
                updates['value'] = parts[2].strip()
            if len(parts) > 3 and parts[3].strip():
                updates['description'] = parts[3].strip()
            if len(parts) > 4 and parts[4].strip():
                updates['location'] = parts[4].strip()

            self.db.update_record(asset_id, updates)
            await ctx.send(f"✅ 資産を更新しました (ID: {asset_id})\nAsset updated (ID: {asset_id})")
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='delete-asset')
    async def delete_asset(self, ctx, asset_id: int):
        """資産を削除 / Delete an asset"""
        try:
            self.db.delete_record(asset_id)
            await ctx.send(f"🗑️ 資産を削除しました (ID: {asset_id})\nAsset deleted (ID: {asset_id})")
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='asset-stats')
    async def stats(self, ctx):
        """統計情報を表示 / Show statistics"""
        try:
            records = self.db.get_all_records()
            total_value = 0
            by_type = {}

            for r in records:
                if r.get('value'):
                    try:
                        total_value += float(r['value'])
                    except:
                        pass
                t = r.get('type', 'N/A')
                by_type[t] = by_type.get(t, 0) + 1

            response = "📈 資産統計 / Asset Statistics\n\n"
            response += f"総資産数 / Total: {len(records)}\n"
            response += f"総価値 / Total Value: {total_value}\n"
            response += f"\n種類別 / By Type:\n"
            for t, count in by_type.items():
                response += f"  {t}: {count}\n"

            await ctx.send(response)
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

if __name__ == '__main__':
    bot = AssetAgent()
    import os
    token = os.getenv('DISCORD_BOT_TOKEN')
    bot.run(token)
