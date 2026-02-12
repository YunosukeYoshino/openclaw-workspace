#!/usr/bin/env python3
"""
Log Agent - Discord Integration
Natural language processing for log management
"""

import discord
from discord.ext import commands
import sqlite3
from pathlib import Path
import json
from datetime import datetime
import re

from db import (
    init_db, add_log, get_logs, get_log_stats,
    create_source, get_sources, create_alert, get_alerts,
    get_alert_history, acknowledge_alert, export_logs_to_file, search_logs
)

# Initialize database
DB_PATH = Path(__file__).parent / "log.db"
if not DB_PATH.exists():
    init_db()

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Natural language patterns
PATTERNS = {
    # Log operations
    r'ログ記録|add.*log|record.*log|log.*add': 'add_log',
    r'ログ表示|show.*log|view.*log': 'show_logs',
    r'error.*log|エラー.*ログ': 'error_logs',
    r'warning.*log|警告.*ログ': 'warning_logs',
    r'ログ検索|search.*log': 'search_logs',
    r'ログ統計|log.*stat|statistics': 'log_stats',

    # Source operations
    r'ソース|sources|log.*source': 'sources',

    # Alert operations
    r'アラート|alert': 'alerts',
    r'アラート履歴|alert.*history|triggered.*alert': 'alert_history',
    r'アラート作成|create.*alert': 'create_alert',

    # Export
    r'ログエクスポート|export.*log': 'export_logs',

    # Help
    r'ヘルプ|使い方|help': 'help',
}

def parse_message(message):
    """Parse natural language message to extract intent and parameters"""
    message_lower = message.lower()

    for pattern, intent in PATTERNS.items():
        if re.search(pattern, message_lower, re.IGNORECASE):
            return intent

    return None

def extract_params(message, intent):
    """Extract parameters from message based on intent"""
    params = {}

    if intent == 'add_log':
        # Extract level and message
        if 'error|err' in message.lower():
            params['level'] = 'ERROR'
        elif 'warning|warn' in message.lower():
            params['level'] = 'WARNING'
        elif 'critical' in message.lower():
            params['level'] = 'CRITICAL'
        elif 'debug' in message.lower():
            params['level'] = 'DEBUG'
        else:
            params['level'] = 'INFO'

        # Extract message content
        parts = message.split('"')
        if len(parts) >= 2:
            params['message'] = parts[1]
        else:
            # Get message after "ログ記録 " or similar
            for marker in ['ログ記録 ', 'add log ', 'record log ']:
                if marker in message.lower():
                    idx = message.lower().find(marker) + len(marker)
                    params['message'] = message[idx:].strip()
                    break

    elif intent == 'search_logs':
        # Extract search query
        parts = message.split('"')
        if len(parts) >= 2:
            params['query'] = parts[1]
        else:
            # Get query after "ログ検索 " or similar
            for marker in ['ログ検索 ', 'search log ', 'search logs ']:
                if marker in message.lower():
                    idx = message.lower().find(marker) + len(marker)
                    params['query'] = message[idx:].strip()
                    break

    elif intent == 'create_alert':
        # Extract alert name
        parts = message.split('"')
        if len(parts) >= 2:
            params['name'] = parts[1]

        # Extract threshold
        threshold_match = re.search(r'threshold\s*[:\s]*([\d]+)', message.lower())
        if threshold_match:
            params['threshold'] = int(threshold_match.group(1))

    elif intent == 'acknowledge_alert':
        # Extract alert history ID
        match = re.search(r'ID[:\s]*(\d+)', message)
        if match:
            params['alert_history_id'] = int(match.group(1))

    return params

async def add_log_handler(ctx, params):
    """Handle adding a log"""
    if 'message' not in params:
        await ctx.send('❌ ログメッセージを指定してください。例: ログ記録 "Error occurred"')
        return

    level = params.get('level', 'INFO')
    log_id = add_log(level=level, message=params['message'], source='discord')
    await ctx.send(f'📝 ログを記録しました (ID: {log_id}): [{level}] {params["message"]}')

async def show_logs_handler(ctx, params):
    """Handle showing logs"""
    logs = get_logs(limit=20)

    if not logs:
        await ctx.send('📋 ログがありません')
        return

    embed = discord.Embed(title='📝 最近のログ', color=discord.Color.blue())

    for log in logs[:10]:
        timestamp = datetime.fromisoformat(log['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        level_emoji = {'DEBUG': '🔍', 'INFO': 'ℹ️', 'WARNING': '⚠️', 'ERROR': '❌', 'CRITICAL': '🔴'}.get(log['level'], '⚪')

        embed.add_field(
            name=f"{level_emoji} {log['level']} - {timestamp}",
            value=log['message'][:200],
            inline=False
        )

    await ctx.send(embed=embed)

async def error_logs_handler(ctx, params):
    """Handle showing error logs"""
    logs = get_logs(level='ERROR', limit=20)

    if not logs:
        await ctx.send('📋 エラーログがありません')
        return

    embed = discord.Embed(title='❌ エラーログ', color=discord.Color.red())

    for log in logs[:10]:
        timestamp = datetime.fromisoformat(log['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        embed.add_field(
            name=f"{timestamp} - {log.get('source', 'N/A')}",
            value=log['message'][:200],
            inline=False
        )

    await ctx.send(embed=embed)

async def warning_logs_handler(ctx, params):
    """Handle showing warning logs"""
    logs = get_logs(level='WARNING', limit=20)

    if not logs:
        await ctx.send('📋 警告ログがありません')
        return

    embed = discord.Embed(title='⚠️ 警告ログ', color=discord.Color.orange())

    for log in logs[:10]:
        timestamp = datetime.fromisoformat(log['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        embed.add_field(
            name=f"{timestamp} - {log.get('source', 'N/A')}",
            value=log['message'][:200],
            inline=False
        )

    await ctx.send(embed=embed)

async def search_logs_handler(ctx, params):
    """Handle searching logs"""
    if 'query' not in params:
        await ctx.send('❌ 検索クエリを指定してください。例: ログ検索 "database"')
        return

    logs = search_logs(params['query'], limit=20)

    if not logs:
        await ctx.send(f'📋 "{params["query"]}" に一致するログがありません')
        return

    embed = discord.Embed(title=f'🔍 検索結果: "{params["query"]}"', color=discord.Color.green())

    for log in logs[:10]:
        timestamp = datetime.fromisoformat(log['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        level_emoji = {'DEBUG': '🔍', 'INFO': 'ℹ️', 'WARNING': '⚠️', 'ERROR': '❌', 'CRITICAL': '🔴'}.get(log['level'], '⚪')

        embed.add_field(
            name=f"{level_emoji} {log['level']} - {timestamp}",
            value=log['message'][:200],
            inline=False
        )

    await ctx.send(embed=embed)

async def log_stats_handler(ctx, params):
    """Handle showing log statistics"""
    stats = get_log_stats(days=7)

    if not stats:
        await ctx.send('📋 統計データがありません')
        return

    embed = discord.Embed(title='📊 ログ統計 (過去7日)', color=discord.Color.blue())

    total = sum(stats.values())
    for level, count in sorted(stats.items()):
        percentage = (count / total * 100) if total > 0 else 0
        level_emoji = {'DEBUG': '🔍', 'INFO': 'ℹ️', 'WARNING': '⚠️', 'ERROR': '❌', 'CRITICAL': '🔴'}.get(level, '⚪')

        embed.add_field(name=f"{level_emoji} {level}", value=f"{count} ({percentage:.1f}%)", inline=True)

    embed.add_field(name='Total', value=str(total), inline=False)

    await ctx.send(embed=embed)

async def sources_handler(ctx, params):
    """Handle showing log sources"""
    sources = get_sources()

    if not sources:
        await ctx.send('📋 ログソースがありません')
        return

    embed = discord.Embed(title='📍 ログソース', color=discord.Color.purple())

    for source in sources:
        type_emoji = {'application': '📱', 'system': '⚙️', 'service': '🔧', 'external': '🔗'}.get(source['type'], '❓')
        status = '✅' if source.get('enabled') else '❌'

        embed.add_field(
            name=f"{status} {type_emoji} {source['name']}",
            value=f"Type: {source['type']} | Last Log: {source.get('last_log', 'Never')}",
            inline=False
        )

    await ctx.send(embed=embed)

async def alerts_handler(ctx, params):
    """Handle showing alerts"""
    alerts = get_alerts()

    if not alerts:
        await ctx.send('📋 アラートがありません')
        return

    embed = discord.Embed(title='🚨 アラート', color=discord.Color.red())

    for alert in alerts:
        level_emoji = {'WARNING': '⚠️', 'ERROR': '❌', 'CRITICAL': '🔴'}.get(alert['level'], '⚪')
        last_triggered = datetime.fromisoformat(alert['last_triggered']).strftime('%Y-%m-%d %H:%M') if alert.get('last_triggered') else 'Never'

        embed.add_field(
            name=f"{level_emoji} {alert['name']}",
            value=f"Condition: {alert['condition']}\nLast Triggered: {last_triggered} | Count: {alert['trigger_count']}",
            inline=False
        )

    await ctx.send(embed=embed)

async def alert_history_handler(ctx, params):
    """Handle showing alert history"""
    history = get_alert_history(limit=20)

    if not history:
        await ctx.send('📋 アラート履歴がありません')
        return

    embed = discord.Embed(title='📜 アラート履歴', color=discord.Color.orange())

    for trigger in history[:10]:
        status = '✅' if trigger.get('acknowledged') else '⏳'
        triggered_at = datetime.fromisoformat(trigger['triggered_at']).strftime('%Y-%m-%d %H:%M')

        embed.add_field(
            name=f"{status} Trigger {trigger['id']} - Alert {trigger['alert_id']}",
            value=f"Triggered: {triggered_at}\nAcked by: {trigger.get('acknowledged_by', 'N/A')}",
            inline=False
        )

    await ctx.send(embed=embed)

async def create_alert_handler(ctx, params):
    """Handle creating an alert"""
    if 'name' not in params:
        await ctx.send('❌ アラート名を指定してください。例: アラート作成 "High Errors" threshold 10')
        return

    threshold = params.get('threshold', 10)
    create_alert(params['name'], f'ERROR logs > {threshold}', level='ERROR', threshold=threshold)
    await ctx.send(f'🚨 アラートを作成しました: {params["name"]} (threshold: {threshold})')

async def export_logs_handler(ctx, params):
    """Handle exporting logs"""
    output_path = export_logs_to_file()
    await ctx.send(f'📤 ログをエクスポートしました: {output_path}')

async def help_handler(ctx, params):
    """Handle help command"""
    embed = discord.Embed(title='📚 Log Agent - ヘルプ', color=discord.Color.blue())

    embed.add_field(name='ログ操作', value='ログ記録 "Message"\nログ表示\nerror ログ\nwarning ログ\nログ検索 "query"\nログ統計', inline=False)
    embed.add_field(name='ソース', value='ソース', inline=False)
    embed.add_field(name='アラート', value='アラート\nアラート履歴\nアラート作成 "Alert Name" threshold 10', inline=False)
    embed.add_field(name='エクスポート', value='ログエクスポート', inline=False)

    await ctx.send(embed=embed)

# Intent handlers
HANDLERS = {
    'add_log': add_log_handler,
    'show_logs': show_logs_handler,
    'error_logs': error_logs_handler,
    'warning_logs': warning_logs_handler,
    'search_logs': search_logs_handler,
    'log_stats': log_stats_handler,
    'sources': sources_handler,
    'alerts': alerts_handler,
    'alert_history': alert_history_handler,
    'create_alert': create_alert_handler,
    'export_logs': export_logs_handler,
    'help': help_handler,
}

@bot.event
async def on_ready():
    print(f'{bot.user.name} が起動しました')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Check for bot mention
    if bot.user in message.mentions:
        content = message.content.replace(f'<@{bot.user.id}>', '').strip()

        # Parse intent
        intent = parse_message(content)
        if not intent:
            await message.channel.send('❌ コマンドを理解できませんでした。「ヘルプ」を入力すると使い方を確認できます。')
            return

        # Extract parameters
        params = extract_params(message.content, intent)

        # Execute handler
        handler = HANDLERS.get(intent)
        if handler:
            ctx = await bot.get_context(message)
            await handler(ctx, params)
        else:
            await message.channel.send('❌ コマンド処理エラーが発生しました')

    await bot.process_commands(message)

def run_bot(token):
    """Run the Discord bot"""
    bot.run(token)

if __name__ == '__main__':
    init_db()
    # token = os.environ.get('DISCORD_TOKEN')
    # if token:
    #     run_bot(token)
