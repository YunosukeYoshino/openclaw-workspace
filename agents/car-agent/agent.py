#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Car Agent - Discord Bot
車管理エージェント - Discord ボット
"""

import discord
from discord.ext import commands
import sqlite3
from datetime import datetime
import os
from db import CarDB

class CarAgent(commands.Bot):
    """Car Management Discord Bot"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!car ', intents=intents)
        self.db = CarDB()

    async def setup_hook(self):
        """Setup hook when bot starts"""
        print(f'{self.user} has connected to Discord!')

    async def on_ready(self):
        """Called when bot is ready"""
        print(f'Logged in as {self.user.name} (ID: {self.user.id})')
        print('------')
        activity = discord.Activity(type=discord.ActivityType.watching, name="your vehicles")
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
bot = CarAgent()

@bot.command(name='summary', aliases=['概要', 'サマリー'])
async def summary(ctx):
    """Show car management summary"""
    summary = bot.db.get_summary()
    embed = discord.Embed(
        title="🚗 車管理サマリー / Car Summary",
        color=discord.Color.blue()
    )
    embed.add_field(name="🚙 車両数 / Vehicles", value=summary['active_vehicles'], inline=True)
    embed.add_field(name="🔧 修理中 / Open Repairs", value=summary['open_repairs'], inline=True)
    embed.add_field(name="📅 リマインダー / Upcoming", value=summary['upcoming_reminders'], inline=True)
    embed.add_field(name="📄 保険期限切れ / Expiring", value=summary['expiring_insurance'], inline=True)
    embed.set_footer(text=f"Requested by {ctx.author.display_name}")
    await ctx.send(embed=embed)

@bot.command(name='vehicle', aliases=['車両', 'add'])
async def add_vehicle(ctx, name: str, make: str = None, model: str = None, year: int = None):
    """Add a new vehicle"""
    vehicle_id = bot.db.add_vehicle(name, make, model, year)
    details = f"{make or ''} {model or ''} {year or ''}".strip()
    await ctx.send(f"🚙 車両を追加しました (ID: {vehicle_id}): {name} ({details})")

@bot.command(name='vehicles', aliases=['車両一覧'])
async def list_vehicles(ctx, status: str = None):
    """List all vehicles"""
    vehicles = bot.db.get_vehicles(status=status)

    if not vehicles:
        await ctx.send("📭 車両が登録されていません。")
        return

    embed = discord.Embed(
        title=f"🚙 車両一覧 / Vehicles ({len(vehicles)})",
        color=discord.Color.blue()
    )

    for vehicle in vehicles:
        details = f"{vehicle['make'] or ''} {vehicle['model'] or ''} {vehicle['year'] or ''}".strip()
        odometer = f"{vehicle['odometer'] or 0:,} km" if vehicle['odometer'] else "N/A"
        embed.add_field(
            name=f"🚗 {vehicle['name']}",
            value=f"{details} | 走行距離: {odometer} | ナンバー: {vehicle['license_plate'] or 'N/A'}",
            inline=False
        )

    await ctx.send(embed=embed)

@bot.command(name='fuel', aliases=['給油'])
async def add_fuel(ctx, vehicle_id: int, odometer: int, liters: float, price_per_liter: float):
    """Add a fuel record"""
    fuel_id = bot.db.add_fuel_record(vehicle_id, odometer, liters, price_per_liter)
    total_price = liters * price_per_liter
    await ctx.send(f"⛽ 給油を記録しました (ID: {fuel_id}): {liters}L @ ¥{price_per_liter}/L = ¥{total_price:.2f}")

@bot.command(name='fuels', aliases=['給油記録'])
async def list_fuel(ctx, vehicle_id: int = None, limit: int = 10):
    """List fuel records"""
    records = bot.db.get_fuel_records(vehicle_id, limit)

    if not records:
        await ctx.send("📭 給油記録がありません。")
        return

    embed = discord.Embed(
        title=f"⛽ 給油記録 / Fuel Records ({len(records)})",
        color=discord.Color.gold()
    )

    for record in records:
        avg = (record['total_price'] / record['fuel_liters']) if record['fuel_liters'] else 0
        embed.add_field(
            name=f"📅 {record['fill_date']} - {record['odometer']:,} km",
            value=f"{record['fuel_liters']}L @ ¥{record['price_per_liter']}/L = ¥{record['total_price']:.2f}",
            inline=False
        )

    await ctx.send(embed=embed)

@bot.command(name='fuelstats', aliases=['燃料統計'])
async def fuel_stats(ctx, vehicle_id: int, days: int = 30):
    """Show fuel statistics"""
    stats = bot.db.get_fuel_stats(vehicle_id, days)

    if stats['fill_count'] == 0:
        await ctx.send(f"📭 過去{days}日の給油記録がありません。")
        return

    embed = discord.Embed(
        title=f"⛽ 燃料統計 / Fuel Statistics ({days}日)",
        color=discord.Color.gold()
    )

    embed.add_field(name="給油回数 / Fills", value=f"{stats['fill_count']} 回", inline=True)
    embed.add_field(name="総給油量 / Total Liters", value=f"{stats['total_liters']:.1f} L", inline=True)
    embed.add_field(name="総費用 / Total Cost", value=f"¥{stats['total_cost']:,.2f}", inline=True)
    embed.add_field(name="平均価格 / Avg Price", value=f"¥{stats['avg_price_per_liter']:.2f}/L", inline=True)

    if stats['fill_count'] > 1:
        avg_per_fill = stats['total_cost'] / stats['fill_count']
        embed.add_field(name="1回あたり / Per Fill", value=f"¥{avg_per_fill:,.2f}", inline=True)

    await ctx.send(embed=embed)

@bot.command(name='maintenance', aliases=['メンテナンス', 'maint'])
async def add_maintenance(ctx, vehicle_id: int, service_type: str, odometer: int, *, description: str = None):
    """Add a maintenance record"""
    maint_id = bot.db.add_maintenance(vehicle_id, service_type, odometer, description)
    await ctx.send(f"🔧 メンテナンスを記録しました (ID: {maint_id}): {service_type}")

@bot.command(name='maintenances', aliases=['メンテナンス一覧'])
async def list_maintenance(ctx, vehicle_id: int = None, service_type: str = None):
    """List maintenance records"""
    records = bot.db.get_maintenance(vehicle_id, service_type)

    if not records:
        await ctx.send("📭 メンテナンス記録がありません。")
        return

    embed = discord.Embed(
        title=f"🔧 メンテナンス一覧 / Maintenance ({len(records)})",
        color=discord.Color.purple()
    )

    service_emoji = {
        'oil_change': '🛢️',
        'tire_rotation': '🔘',
        'brake_service': '🛑',
        'inspection': '📋'
    }

    for record in records[:10]:
        emoji = service_emoji.get(record['service_type'], '🔧')
        cost_str = f"¥{record['cost']:,.0f}" if record['cost'] else "N/A"
        embed.add_field(
            name=f"{emoji} {record['service_type']} - {record['service_date']}",
            value=f"{record['odometer']:,} km | 費用: {cost_str}\n{record['description'] or ''}",
            inline=False
        )

    await ctx.send(embed=embed)

@bot.command(name='repair', aliases=['修理'])
async def add_repair(ctx, vehicle_id: int, issue: str, odometer: int, severity: str = 'moderate'):
    """Add a repair record"""
    repair_id = bot.db.add_repair(vehicle_id, issue, odometer, severity)
    await ctx.send(f"🔨 修理を記録しました (ID: {repair_id}): {issue}")

@bot.command(name='repairs', aliases=['修理一覧'])
async def list_repairs(ctx, vehicle_id: int = None, status: str = None):
    """List repair records"""
    repairs = bot.db.get_repairs(vehicle_id, status)

    if not repairs:
        await ctx.send("📭 修理記録がありません。")
        return

    embed = discord.Embed(
        title=f"🔨 修理一覧 / Repairs ({len(repairs)})",
        color=discord.Color.orange()
    )

    severity_color = {
        'minor': '🟢',
        'moderate': '🟡',
        'critical': '🔴'
    }

    for repair in repairs[:10]:
        status_emoji = {
            'open': '📝',
            'in_progress': '🔨',
            'completed': '✅',
            'cancelled': '❌'
        }.get(repair['status'], '❓')

        severity_emoji = severity_color.get(repair['severity'], '⚪')
        embed.add_field(
            name=f"{status_emoji} {repair['issue']} ({repair['issue_date']})",
            value=f"{severity_emoji} 重要度: {repair['severity']} | {repair['odometer'] or 0:,} km",
            inline=False
        )

    await ctx.send(embed=embed)

@bot.command(name='insurance', aliases=['保険'])
async def add_insurance(ctx, vehicle_id: int, provider: str, policy_number: str,
                       start_date: str, end_date: str):
    """Add an insurance policy"""
    ins_id = bot.db.add_insurance(vehicle_id, provider, policy_number, start_date, end_date)
    await ctx.send(f"📄 保険を追加しました (ID: {ins_id}): {provider}")

@bot.command(name='insurances', aliases=['保険一覧'])
async def list_insurance(ctx, vehicle_id: int = None):
    """List insurance policies"""
    policies = bot.db.get_insurance(vehicle_id)

    if not policies:
        await ctx.send("📭 保険記録がありません。")
        return

    embed = discord.Embed(
        title=f"📄 保険一覧 / Insurance Policies ({len(policies)})",
        color=discord.Color.blue()
    )

    for policy in policies:
        status_emoji = '✅' if policy['status'] == 'active' else '⚠️'
        premium_str = f"¥{policy['premium']:,.0f}/年" if policy['premium'] else "N/A"
        embed.add_field(
            name=f"{status_emoji} {policy['provider']}",
            value=f"ポリシー: {policy['policy_number']}\n期間: {policy['start_date']} ~ {policy['end_date']}\n料金: {premium_str}",
            inline=False
        )

    await ctx.send(embed=embed)

@bot.command(name='reminder', aliases=['リマインダー', 'rem'])
async def add_reminder(ctx, vehicle_id: int, reminder_type: str, description: str, *, due_date: str = None):
    """Add a reminder"""
    rem_id = bot.db.add_reminder(vehicle_id, reminder_type, description, due_date)
    due_str = f"期限: {due_date}" if due_date else ""
    await ctx.send(f"📅 リマインダーを追加しました (ID: {rem_id}): {reminder_type} - {description}\n{due_str}")

@bot.command(name='reminders', aliases=['リマインダー一覧'])
async def list_reminders(ctx, vehicle_id: int = None, status: str = None):
    """List reminders"""
    reminders = bot.db.get_reminders(vehicle_id, status)

    if not reminders:
        await ctx.send("📭 リマインダーがありません。")
        return

    embed = discord.Embed(
        title=f"📅 リマインダー / Reminders ({len(reminders)})",
        color=discord.Color.teal()
    )

    for reminder in reminders[:10]:
        status_emoji = '⏳' if reminder['status'] == 'pending' else '✅'
        due_str = f"期限: {reminder['due_date']}" if reminder['due_date'] else "期限なし"
        embed.add_field(
            name=f"{status_emoji} {reminder['reminder_type']}",
            value=f"{reminder['description']}\n{due_str}",
            inline=False
        )

    await ctx.send(embed=embed)

@bot.command(name='help', aliases=['ヘルプ', '使い方'])
async def help_command(ctx):
    """Show help"""
    embed = discord.Embed(
        title="🚗 Car Agent - ヘルプ",
        description="車両管理を簡単に！/ Manage your vehicles easily!",
        color=discord.Color.blue()
    )

    embed.add_field(name="📊 サマリー", value="`!car summary` - 全体状況を表示", inline=False)
    embed.add_field(name="🚙 車両", value="`!car vehicle <name>` - 車両追加\n`!car vehicles` - 車両一覧", inline=False)
    embed.add_field(name="⛽ 給油", value="`!car fuel <id> <odometer> <liters> <price>` - 給油記録\n`!car fuels [id]` - 記録一覧\n`!car fuelstats <id> [days]` - 統計", inline=False)
    embed.add_field(name="🔧 メンテナンス", value="`!car maintenance <id> <type> <odometer>` - 記録追加\n`!car maintenances` - 一覧", inline=False)
    embed.add_field(name="🔨 修理", value="`!car repair <id> <issue> <odometer>` - 修理追加\n`!car repairs [status]` - 一覧", inline=False)
    embed.add_field(name="📄 保険", value="`!car insurance <id> <provider> <policy> <start> <end>` - 保険追加\n`!car insurances` - 一覧", inline=False)
    embed.add_field(name="📅 リマインダー", value="`!car reminder <id> <type> <desc> [date]` - 追加\n`!car reminders` - 一覧", inline=False)

    embed.set_footer(text="コマンドは `!car ` で始まります")
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
