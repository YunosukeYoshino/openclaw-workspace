#!/usr/bin/env python3
"""
服飾管理エージェント
Wardrobe Management Agent
Discordボットによる衣類・ワードローブ管理
"""

import discord
from discord.ext import commands
import re
from datetime import datetime
from db import ClothingDatabase
import json


class ClothingAgent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = ClothingDatabase()

    def _parse_tags(self, text: str) -> str:
        """タグを抽出"""
        tags = re.findall(r'#(\w+)', text)
        return ','.join(tags) if tags else None

    def _extract_datetime(self, text: str) -> str:
        """日時を抽出"""
        now = datetime.now()
        today_match = re.search(r'(今日|today)', text.lower())
        if today_match:
            return now.strftime('%Y-%m-%d')

        # 日付パターン
        date_patterns = [
            r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',
            r'(\d{1,2})[/-](\d{1,2})',
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                if len(match.groups()) == 3:
                    return f"{match.group(1)}-{match.group(2).zfill(2)}-{match.group(3).zfill(2)}"
                elif len(match.groups()) == 2:
                    return f"{now.year}-{match.group(1).zfill(2)}-{match.group(2).zfill(2)}"
        return None

    @commands.command(aliases=['additem', '登録', 'アイテム追加'])
    async def add_item(self, ctx, *, message: str = None):
        """アイテムを追加 / Add item"""
        if not message:
            await ctx.send("```\n使用方法: !additem <アイテム名> [カテゴリ] [詳細情報]\n例: !additem 白いTシャツ トップス ブランド:ユニクロ サイズ:M #夏服\n```")
            return

        # 自然言語解析
        parts = message.split()
        name = parts[0]

        # カテゴリの検出
        category = None
        for part in parts[1:]:
            if part in ['トップス', 'ボトムス', 'アウター', '靴', 'アクセサリー', 'インナー', 'バッグ', '帽子', 'スカーフ', 'マフラー',
                        'top', 'bottom', 'outer', 'shoes', 'accessory', 'inner', 'bag', 'hat', 'scarf', 'muffler']:
                category = part
                break

        if not category:
            category = 'その他'

        # キーワード抽出
        kwargs = {}
        brand_match = re.search(r'ブランド[:：]\s*(\S+)', message)
        if brand_match:
            kwargs['brand'] = brand_match.group(1)

        size_match = re.search(r'サイズ[:：]\s*(\S+)', message)
        if size_match:
            kwargs['size'] = size_match.group(1)

        color_match = re.search(r'色[:：]\s*(\S+)', message)
        if color_match:
            kwargs['color'] = color_match.group(1)

        price_match = re.search(r'価格[:：]\s*(\d+)', message)
        if price_match:
            kwargs['purchase_price'] = float(price_match.group(1))

        kwargs['tags'] = self._parse_tags(message)
        kwargs['notes'] = message

        try:
            item_id = self.db.add_item(name, category, **kwargs)
            await ctx.send(f"✅ アイテムを登録しました\nID: {item_id}\n名前: {name}\nカテゴリ: {category}")
        except Exception as e:
            await ctx.send(f"❌ エラー: {e}")

    @commands.command(aliases=['listitems', 'アイテム一覧', '衣類一覧'])
    async def list_items(self, ctx, *, category: str = None):
        """アイテム一覧を表示 / List items"""
        items = self.db.get_items(category)

        if not items:
            await ctx.send("📭 アイテムがありません")
            return

        msg = "👕 **アイテム一覧**\n\n"
        if category:
            msg += f"📁 カテゴリ: {category}\n\n"

        for item in items[:20]:  # 最大20件
            tags = f" #{item['tags']}" if item['tags'] else ""
            msg += f"• {item['name']} ({item['category']}){tags}\n"

        if len(items) > 20:
            msg += f"\n...他 {len(items) - 20} 件"

        await ctx.send(msg)

    @commands.command(aliases=['stats', '統計', '分析'])
    async def show_stats(self, ctx):
        """統計情報を表示 / Show statistics"""
        summary = self.db.get_summary()
        stats = self.db.get_wear_stats()

        msg = "📊 **ワードローブ統計**\n\n"
        msg += f"👔 総アイテム数: {summary['total_items']}\n"
        msg += f"👗 アウトフィット数: {summary['total_outfits']}\n"
        msg += f"🛒 買い物リスト: {summary['shopping_pending']} 件\n\n"

        msg += "**カテゴリ別:**\n"
        for cat, count in sorted(summary['by_category'].items(), key=lambda x: x[1], reverse=True):
            msg += f"  • {cat}: {count} 件\n"

        await ctx.send(msg)

    @commands.command(aliases=['outfit', 'コーデ', 'コーデ登録'])
    async def add_outfit(self, ctx, *, message: str = None):
        """アウトフィット（コーデ）を登録 / Add outfit"""
        if not message:
            await ctx.send("```\n使用方法: !outfit <名前> [アイテムID1,アイテムID2,...] [詳細]\n例: !outfit 夏のカジュアル 1,3,5 #夏\n```")
            return

        parts = message.split()
        name = parts[0]

        # IDの抽出
        ids = []
        for part in parts[1:]:
            if re.match(r'^\d+$', part):
                ids.append(int(part))
            elif ',' in part:
                for id_str in part.split(','):
                    if id_str.strip().isdigit():
                        ids.append(int(id_str.strip()))

        if len(ids) < 2:
            await ctx.send("❌ 最低2つのアイテムIDを指定してください")
            return

        kwargs = {
            'season': None,
            'occasion': None,
            'favorite': False,
            'description': message
        }

        if '夏' in message or 'summer' in message.lower():
            kwargs['season'] = 'summer'
        elif '冬' in message or 'winter' in message.lower():
            kwargs['season'] = 'winter'
        elif '春' in message or 'spring' in message.lower():
            kwargs['season'] = 'spring'
        elif '秋' in message or 'autumn' in message.lower() or 'fall' in message.lower():
            kwargs['season'] = 'autumn'

        if 'お気に入り' in message or 'favorite' in message.lower():
            kwargs['favorite'] = True

        try:
            outfit_id = self.db.add_outfit(name, ids, **kwargs)
            await ctx.send(f"✅ アウトフィットを登録しました\nID: {outfit_id}\n名前: {name}\nアイテム数: {len(ids)}")
        except Exception as e:
            await ctx.send(f"❌ エラー: {e}")

    @commands.command(aliases=['listoutfits', 'コーデ一覧'])
    async def list_outfits(self, ctx):
        """アウトフィット一覧を表示 / List outfits"""
        outfits = self.db.get_outfits()

        if not outfits:
            await ctx.send("📭 アウトフィットがありません")
            return

        msg = "👗 **アウトフィット一覧**\n\n"

        for outfit in outfits[:15]:
            item_ids = json.loads(outfit['items'])
            season = f" [{outfit['season']}]" if outfit['season'] else ""
            favorite = " ⭐" if outfit['favorite'] else ""
            msg += f"• {outfit['name']}{season}{favorite} ({len(item_ids)} アイテム)\n"

        if len(outfits) > 15:
            msg += f"\n...他 {len(outfits) - 15} 件"

        await ctx.send(msg)

    @commands.command(aliases=['wear', '着用', '着た'])
    async def log_wear(self, ctx, *, message: str = None):
        """着用を記録 / Log wear"""
        if not message:
            await ctx.send("```\n使用方法: !wear [アイテムID] [アウトフィットID] [メモ]\n例: !wear 1 今日のカジュアルコーデ\n```")
            return

        # IDの抽出
        item_id = None
        outfit_id = None
        notes = message

        for part in message.split():
            if re.match(r'^\d+$', part) and part.isdigit():
                num = int(part)
                if item_id is None:
                    item_id = num
                elif outfit_id is None:
                    outfit_id = num

        try:
            log_id = self.db.log_wear(item_id=item_id, outfit_id=outfit_id, notes=notes)
            worn_date = self._extract_datetime(message) or datetime.now().strftime('%Y-%m-%d')
            await ctx.send(f"✅ 着用を記録しました\n日付: {worn_date}")
        except Exception as e:
            await ctx.send(f"❌ エラー: {e}")

    @commands.command(aliases=['shopping', '買い物', '欲しいもの'])
    async def add_shopping(self, ctx, *, message: str = None):
        """買い物リストに追加 / Add to shopping list"""
        if not message:
            await ctx.send("```\n使用方法: !shopping <アイテム名> [カテゴリ] [予算] [URL]\n例: !shopping 黒スキニー 予算:5000\n```")
            return

        parts = message.split()
        name = parts[0]

        kwargs = {
            'priority': 'medium',
            'budget': None,
            'url': None,
            'notes': message
        }

        priority_match = re.search(r'(優先度|priority)[:：]\s*(高|中|低|high|medium|low)', message.lower())
        if priority_match:
            p = priority_match.group(2)
            if p in ['高', 'high']:
                kwargs['priority'] = 'high'
            elif p in ['中', 'medium']:
                kwargs['priority'] = 'medium'
            else:
                kwargs['priority'] = 'low'

        budget_match = re.search(r'(予算|budget|価格)[:：]\s*(\d+)', message)
        if budget_match:
            kwargs['budget'] = float(budget_match.group(2))

        url_match = re.search(r'https?://\S+', message)
        if url_match:
            kwargs['url'] = url_match.group(0)

        try:
            item_id = self.db.add_to_shopping_list(name, **kwargs)
            priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}[kwargs['priority']]
            await ctx.send(f"{priority_emoji} 買い物リストに追加しました\nID: {item_id}\n名前: {name}")
        except Exception as e:
            await ctx.send(f"❌ エラー: {e}")

    @commands.command(aliases=['listshopping', '買い物リスト'])
    async def list_shopping(self, ctx):
        """買い物リストを表示 / List shopping items"""
        items = self.db.get_shopping_list(purchased=False)

        if not items:
            await ctx.send("📭 買い物リストは空です")
            return

        msg = "🛒 **買い物リスト**\n\n"

        priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}
        for item in items[:15]:
            emoji = priority_emoji.get(item['priority'], '⚪')
            budget = f" ¥{int(item['budget']):,}" if item['budget'] else ""
            msg += f"{emoji} {item['name']}{budget}\n"

        if len(items) > 15:
            msg += f"\n...他 {len(items) - 15} 件"

        await ctx.send(msg)

    @commands.command(aliases=['help', 'help_clothing'])
    async def clothing_help(self, ctx):
        """ヘルプを表示 / Show help"""
        help_text = """
👕 **服飾管理エージェント ヘルプ**

**アイテム管理:**
  `!additem <名前> [カテゴリ] [詳細]` - アイテム追加
  `!listitems [カテゴリ]` - アイテム一覧

**コーデ管理:**
  `!outfit <名前> <ID,ID,...>` - アウトフィット登録
  `!listoutfits` - アウトフィット一覧

**記録:**
  `!wear [アイテムID] [メモ]` - 着用記録

**買い物リスト:**
  `!shopping <名前> [予算]` - 買い物リスト追加
  `!listshopping` - 買い物リスト表示

**その他:**
  `!stats` - 統計情報
        """
        await ctx.send(help_text)


def setup(bot):
    bot.add_cog(ClothingAgent(bot))
