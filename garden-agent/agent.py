#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Garden Agent - Discord Bot
園芸記録エージェント - Discord ボット
"""

import discord
from discord.ext import commands
import sqlite3
from datetime import datetime
import os
from db import GardenDB

class GardenAgent(commands.Bot):
    """Garden Management Discord Bot"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!garden ', intents=intents)
        self.db = GardenDB()

    async def setup_hook(self):
        """Setup hook when bot starts"""
        print(f'{self.user} has connected to Discord!')

    async def on_ready(self):
        """Called when bot is ready"""
        print(f'Logged in as {self.user.name} (ID: {self.user.id})')
        print('------')
        activity = discord.Activity(type=discord.ActivityType.watching, name="your garden")
        await self.change_presence(activity=activity)

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
bot = GardenAgent()

@bot.command(name='summary', aliases=['概要', 'サマリー'])
async def summary(ctx):
    """Show garden summary"""
    summary = bot.db.get_summary()
    embed = discord.Embed(
        title="🌱 園芸サマリー / Garden Summary",
        color=discord.Color.green()
    )
    embed.add_field(name="🌿 活躍中の植物 / Active Plants", value=summary['active_plants'], inline=True)
    embed.add_field(name="🐛 対処中の害虫/病気 / Active Pests", value=summary['active_pests'], inline=True)
    embed.add_field(name="🥬 今週の収穫 / Recent Harvests", value=summary['recent_harvests'], inline=True)
    embed.add_field(name="💧 水やり必要 / Needs Watering", value=summary['needs_watering'], inline=True)
    embed.set_footer(text=f"Requested by {ctx.author.display_name}")
    await ctx.send(embed=embed)

@bot.command(name='plant', aliases=['植物', '追加'])
async def add_plant(ctx, name: str, category: str, *, details: str = None):
    """Add a new plant"""
    plant_id = bot.db.add_plant(name, category, notes=details)
    await ctx.send(f"🌿 植物を追加しました (ID: {plant_id}): {name}")

@bot.command(name='plants', aliases=['植物一覧'])
async def list_plants(ctx, category: str = None):
    """List all plants or filter by category"""
    plants = bot.db.get_plants(category=category)

    if not plants:
        await ctx.send("📭 植物が登録されていません。")
        return

    embed = discord.Embed(
        title=f"🌿 植物一覧 / Plants ({len(plants)})",
        color=discord.Color.green()
    )

    category_emoji = {
        'vegetable': '🥬',
        'flower': '🌸',
        'herb': '🌿',
        'tree': '🌳',
        'shrub': '🌲'
    }

    for plant in plants[:10]:
        emoji = category_emoji.get(plant['category'], '🌱')
        location = plant['location'] or 'N/A'
        embed.add_field(
            name=f"{emoji} {plant['name']} ({plant['variety'] or ''})",
            value=f"カテゴリ: {plant['category']} | 場所: {location}",
            inline=False
        )

    await ctx.send(embed=embed)

@bot.command(name='harvest', aliases=['収穫'])
async def add_harvest(ctx, plant_id: int, quantity: float, unit: str, quality: str = 'good'):
    """Add a harvest record"""
    harvest_id = bot.db.add_harvest(plant_id, quantity, unit, quality)
    await ctx.send(f"🥬 収穫を記録しました (ID: {harvest_id}): {quantity}{unit}")

@bot.command(name='harvests', aliases=['収穫一覧'])
async def list_harvests(ctx):
    """List all harvests"""
    harvests = bot.db.get_harvests()

    if not harvests:
        await ctx.send("📭 収穫記録がありません。")
        return

    embed = discord.Embed(
        title=f"🥬 収穫一覧 / Harvests ({len(harvests)})",
        color=discord.Color.gold()
    )

    for harvest in harvests[:10]:
        quality_emoji = {
            'excellent': '⭐',
            'good': '✅',
            'fair': '👌',
            'poor': '❌'
        }.get(harvest['quality'], '❓')

        embed.add_field(
            name=f"{quality_emoji} {harvest['quantity']}{harvest['unit']}",
            value=f"植物ID: {harvest['plant_id']} | 日付: {harvest['harvest_date']}",
            inline=True
        )

    await ctx.send(embed=embed)

@bot.command(name='activity', aliases=['活動', 'act'])
async def add_activity(ctx, activity_type: str, *, description: str = None):
    """Add a garden activity"""
    activity_id = bot.db.add_activity(activity_type, description=description)
    await ctx.send(f"🌱 園芸活動を記録しました (ID: {activity_id}): {activity_type}")

@bot.command(name='activities', aliases=['活動一覧'])
async def list_activities(ctx, activity_type: str = None):
    """List garden activities"""
    activities = bot.db.get_activities(activity_type=activity_type)

    if not activities:
        await ctx.send("📭 活動記録がありません。")
        return

    embed = discord.Embed(
        title=f"🌱 園芸活動一覧 / Garden Activities ({len(activities)})",
        color=discord.Color.light_grey()
    )

    activity_emoji = {
        'sowing': '🌱',
        'transplanting': '🪴',
        'weeding': '🌿',
        'mulching': '🍂',
        'pruning': '✂️',
        'watering': '💧',
        'fertilizing': '🧪'
    }

    for act in activities[:10]:
        emoji = activity_emoji.get(act['activity_type'], '🌱')
        embed.add_field(
            name=f"{emoji} {act['activity_type']}",
            value=f"日付: {act['activity_date']} | {act['description'] or ''}",
            inline=False
        )

    await ctx.send(embed=embed)

@bot.command(name='pest', aliases=['害虫', 'pest'])
async def add_pest(ctx, plant_id: int, pest_disease_name: str,
                  type: str, severity: str = 'moderate'):
    """Add a pest/disease record"""
    pd_id = bot.db.add_pest_disease(plant_id, pest_disease_name, type, severity)
    await ctx.send(f"🐛 害虫/病気を記録しました (ID: {pd_id}): {pest_disease_name}")

@bot.command(name='pests', aliases=['害虫一覧'])
async def list_pests(ctx, status: str = None):
    """List pests/diseases"""
    pests = bot.db.get_pests_diseases(status=status)

    if not pests:
        await ctx.send("📭 害虫/病気の記録がありません。")
        return

    embed = discord.Embed(
        title=f"🐛 害虫・病気一覧 / Pests & Diseases ({len(pests)})",
        color=discord.Color.red()
    )

    for pest in pests[:10]:
        severity_emoji = {
            'mild': '🟢',
            'moderate': '🟡',
            'severe': '🔴'
        }.get(pest['severity'], '⚪')

        type_emoji = '🐛' if pest['type'] == 'pest' else '🦠'
        embed.add_field(
            name=f"{type_emoji} {pest['pest_disease_name']}",
            value=f"{severity_emoji} 重要度: {pest['severity']} | 植物ID: {pest['plant_id']}",
            inline=False
        )

    await ctx.send(embed=embed)

@bot.command(name='seed', aliases=['種子', '種'])
async def add_seed(ctx, plant_name: str, quantity: int, *, details: str = None):
    """Add seeds to inventory"""
    seed_id = bot.db.add_seed(plant_name, quantity, notes=details)
    await ctx.send(f"🌰 種子を追加しました (ID: {seed_id}): {plant_name} x {quantity}")

@bot.command(name='seeds', aliases=['種子一覧'])
async def list_seeds(ctx):
    """List all seeds"""
    seeds = bot.db.get_seeds()

    if not seeds:
        await ctx.send("📭 種子の記録がありません。")
        return

    embed = discord.Embed(
        title=f"🌰 種子在庫 / Seeds Inventory ({len(seeds)})",
        color=discord.Color.brown()
    )

    for seed in seeds[:15]:
        embed.add_field(
            name=f"🌰 {seed['plant_name']} ({seed['variety'] or ''})",
            value=f"数量: {seed['quantity']} | 保存場所: {seed['storage_location'] or 'N/A'}",
            inline=True
        )

    await ctx.send(embed=embed)

@bot.command(name='water', aliases=['水やり'])
async def add_care(ctx, plant_id: int, care_type: str = 'watering', *, notes: str = None):
    """Add care record (default: watering)"""
    care_id = bot.db.add_care(plant_id, care_type, notes=notes)
    care_name = {'watering': '水やり', 'fertilizing': '施肥', 'pruning': '剪定'}.get(care_type, care_type)
    await ctx.send(f"💧 ケアを記録しました (ID: {care_id}): {care_name}")

@bot.command(name='watering', aliases=['水やり予定'])
async def list_watering(ctx):
    """List watering schedule"""
    schedules = bot.db.get_watering_schedule()

    if not schedules:
        await ctx.send("📭 水やりの予定がありません。")
        return

    embed = discord.Embed(
        title=f"💧 水やりスケジュール / Watering Schedule ({len(schedules)})",
        color=discord.Color.blue()
    )

    for sched in schedules[:10]:
        next_date = sched['next_watering'] or '未定'
        days_until = sched['next_watering'] or ''
        embed.add_field(
            name=f"🌿 {sched['plant_name']}",
            value=f"次回: {next_date} (頻度: {sched['frequency']}日ごと)",
            inline=False
        )

    await ctx.send(embed=embed)

@bot.command(name='help', aliases=['ヘルプ', '使い方'])
async def help_command(ctx):
    """Show help"""
    embed = discord.Embed(
        title="🌱 Garden Agent - ヘルプ",
        description="園芸記録を簡単に！/ Track your garden easily!",
        color=discord.Color.green()
    )

    embed.add_field(name="📊 サマリー", value="`!garden summary` - 全体状況を表示", inline=False)
    embed.add_field(name="🌿 植物", value="`!garden plant <名前> <カテゴリ>` - 植物追加\n`!garden plants [カテゴリ]` - 植物一覧", inline=False)
    embed.add_field(name="🥬 収穫", value="`!garden harvest <ID> <数量> <単位>` - 収穫記録\n`!garden harvests` - 収穫一覧", inline=False)
    embed.add_field(name="🌱 活動", value="`!garden activity <種類>` - 活動記録\n`!garden activities [種類]` - 活動一覧", inline=False)
    embed.add_field(name="🐛 害虫/病気", value="`!garden pest <ID> <名前> <種類>` - 記録追加\n`!garden pests [状態]` - 一覧", inline=False)
    embed.add_field(name="🌰 種子", value="`!garden seed <名前> <数量>` - 種子追加\n`!garden seeds` - 種子在庫", inline=False)
    embed.add_field(name="💧 ケア", value="`!garden water <ID> [種類]` - ケア記録\n`!garden watering` - 水やり予定", inline=False)

    embed.set_footer(text="コマンドは `!garden ` で始まります")
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
