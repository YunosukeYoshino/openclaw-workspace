#!/usr/bin/env python3
"""
Monitor Agent - Discord Integration
Natural language processing for monitoring management
"""

import discord
from discord.ext import commands
import sqlite3
from pathlib import Path
import json
from datetime import datetime, timedelta
import re

from db import (
    init_db, create_service, get_services, record_metric, get_metrics,
    create_alert, get_alerts, trigger_alert, get_alert_triggers, acknowledge_trigger,
    record_health_check, get_health_checks, aggregate_metrics,
    create_incident, update_incident, get_incidents,
    create_dashboard, get_dashboards, add_widget, get_widgets,
    get_monitoring_summary
)

# Initialize database
DB_PATH = Path(__file__).parent / "monitor.db"
if not DB_PATH.exists():
    init_db()

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Natural language patterns
PATTERNS = {
    # Service operations
    r'サービス作成|サービス追加|create.*service|new.*service': 'create_service',
    r'サービス一覧|service|list.*service': 'list_services',

    # Metric operations
    r'メトリック記録|記録.*metric|record.*metric': 'record_metric',
    r'メトリック|metric|list.*metric': 'list_metrics',

    # Alert operations
    r'アラート作成|アラート追加|create.*alert|new.*alert': 'create_alert',
    r'アラート一覧|alert.*list|alerts': 'list_alerts',
    r'アラート履歴|alert.*history|triggered.*alert': 'alert_history',
    r'アラート承認|acknowledge.*alert': 'acknowledge_alert',

    # Health checks
    r'ヘルスチェック|health.*check': 'health_checks',

    # Incident operations
    r'インシデント作成|incident.*create': 'create_incident',
    r'インシデント一覧|incident.*list|incidents': 'list_incidents',
    r'インシデント解決|incident.*resolve': 'resolve_incident',

    # Dashboard operations
    r'ダッシュボード作成|create.*dashboard': 'create_dashboard',
    r'ダッシュボード一覧|dashboard.*list|dashboards': 'list_dashboards',

    # Summary
    r'モニタリング概要|monitoring.*summary|summary': 'monitoring_summary',

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

    if intent == 'create_service':
        # Extract name and type
        parts = message.split('"')
        if len(parts) >= 2:
            params['name'] = parts[1]
        if 'api' in message.lower():
            params['service_type'] = 'api'
        elif 'database|db' in message.lower():
            params['service_type'] = 'database'
        elif 'cache|redis' in message.lower():
            params['service_type'] = 'cache'
        elif 'queue' in message.lower():
            params['service_type'] = 'queue'

    elif intent == 'record_metric':
        # Extract metric name and value
        match = re.search(r'([a-z_]+)\s*[:\s]*([\d.]+)', message.lower())
        if match:
            params['metric_name'] = match.group(1)
            params['value'] = float(match.group(2))

    elif intent == 'create_alert':
        # Extract alert name, metric, threshold
        match = re.search(r'"([^"]+)"', message)
        if match:
            params['name'] = match.group(1)
        threshold_match = re.search(r'threshold\s*[:\s]*([\d.]+)', message.lower())
        if threshold_match:
            params['threshold'] = float(threshold_match.group(1))

    elif intent == 'acknowledge_alert':
        # Extract trigger ID
        match = re.search(r'ID[:\s]*(\d+)', message)
        if match:
            params['trigger_id'] = int(match.group(1))

    elif intent == 'resolve_incident':
        # Extract incident ID
        match = re.search(r'ID[:\s]*(\d+)', message)
        if match:
            params['incident_id'] = int(match.group(1))

    elif intent == 'create_incident':
        # Extract title
        match = re.search(r'"([^"]+)"', message)
        if match:
            params['title'] = match.group(1)
        if 'critical' in message.lower():
            params['severity'] = 'critical'

    elif intent == 'create_dashboard':
        # Extract name
        match = re.search(r'"([^"]+)"', message)
        if match:
            params['name'] = match.group(1)

    return params

async def create_service_handler(ctx, params):
    """Handle service creation"""
    if 'name' not in params:
        await ctx.send('❌ サービス名を指定してください。例: サービス作成 "API Service" api')
        return

    service_type = params.get('service_type', 'api')
    service_id = create_service(params['name'], service_type)
    await ctx.send(f'✅ サービスを作成しました (ID: {service_id}): {params["name"]} ({service_type})')

async def list_services_handler(ctx, params):
    """Handle listing services"""
    services = get_services()

    if not services:
        await ctx.send('📋 サービスがありません')
        return

    embed = discord.Embed(title='🖥️ サービス一覧', color=discord.Color.blue())

    for svc in services:
        type_emoji = {'api': '🌐', 'database': '🗄️', 'cache': '⚡', 'queue': '📬', 'worker': '👷', 'external': '🔗'}.get(svc['type'], '❓')
        health = get_health_checks(service_id=svc['id'], limit=1)
        status_emoji = {'healthy': '✅', 'unhealthy': '❌', 'degraded': '⚠️', 'unknown': '⚪'}.get(health[0]['status'] if health else 'unknown', '⚪')

        embed.add_field(
            name=f"{status_emoji} {type_emoji} ID {svc['id']}: {svc['name']}",
            value=f"Type: {svc['type']} | Environment: {svc.get('environment', 'N/A')}",
            inline=False
        )

    await ctx.send(embed=embed)

async def record_metric_handler(ctx, params):
    """Handle recording a metric"""
    if 'metric_name' not in params or 'value' not in params:
        await ctx.send('❌ メトリック名と値を指定してください。例: メトリック記録 cpu_usage 75.5')
        return

    record_metric(params['metric_name'], params['value'])
    await ctx.send(f'📊 メトリックを記録しました: {params["metric_name"]} = {params["value"]}')

async def list_metrics_handler(ctx, params):
    """Handle listing metrics"""
    metrics = get_metrics(limit=50)

    if not metrics:
        await ctx.send('📋 メトリックがありません')
        return

    embed = discord.Embed(title='📊 最近のメトリック', color=discord.Color.green())

    for metric in metrics[:15]:
        timestamp = datetime.fromisoformat(metric['timestamp']).strftime('%H:%M:%S')
        embed.add_field(
            name=f"{metric['metric_name']}",
            value=f"{metric['value']} {metric.get('unit', '')} | {timestamp}",
            inline=True
        )

    await ctx.send(embed=embed)

async def create_alert_handler(ctx, params):
    """Handle alert creation"""
    if 'name' not in params:
        await ctx.send('❌ アラート名を指定してください。例: アラート作成 "High CPU" threshold 80')
        return

    threshold = params.get('threshold', 100)
    alert_id = create_alert(params['name'], 'cpu_usage', threshold, severity='warning')
    await ctx.send(f'🚨 アラートを作成しました (ID: {alert_id}): {params["name"]} (threshold: {threshold})')

async def list_alerts_handler(ctx, params):
    """Handle listing alerts"""
    alerts = get_alerts()

    if not alerts:
        await ctx.send('📋 アラートがありません')
        return

    embed = discord.Embed(title='🚨 アラート一覧', color=discord.Color.red())

    for alert in alerts:
        severity_emoji = {'info': 'ℹ️', 'warning': '⚠️', 'error': '❌', 'critical': '🔴'}.get(alert['severity'], '⚪')
        last_triggered = datetime.fromisoformat(alert['last_triggered']).strftime('%Y-%m-%d %H:%M') if alert.get('last_triggered') else 'Never'

        embed.add_field(
            name=f"{severity_emoji} ID {alert['id']}: {alert['name']}",
            value=f"Metric: {alert['metric_name']} | Threshold: {alert['threshold']}\nTriggered: {last_triggered} | Count: {alert['trigger_count']}",
            inline=False
        )

    await ctx.send(embed=embed)

async def alert_history_handler(ctx, params):
    """Handle showing alert history"""
    triggers = get_alert_triggers(limit=20)

    if not triggers:
        await ctx.send('📋 アラート履歴がありません')
        return

    embed = discord.Embed(title='📜 アラート履歴', color=discord.Color.orange())

    for trigger in triggers[:10]:
        severity_emoji = {'info': 'ℹ️', 'warning': '⚠️', 'error': '❌', 'critical': '🔴'}.get(trigger['severity'], '⚪')
        triggered_at = datetime.fromisoformat(trigger['triggered_at']).strftime('%Y-%m-%d %H:%M')
        status = '✅' if trigger.get('acknowledged') else '⏳'

        embed.add_field(
            name=f"{status} {severity_emoji} Trigger {trigger['id']}",
            value=f"Alert ID: {trigger['alert_id']} | Value: {trigger['actual_value']}\nTime: {triggered_at}",
            inline=False
        )

    await ctx.send(embed=embed)

async def acknowledge_alert_handler(ctx, params):
    """Handle acknowledging an alert"""
    if 'trigger_id' not in params:
        await ctx.send('❌ トリガーIDを指定してください。例: アラート承認 ID: 123')
        return

    acknowledge_trigger(params['trigger_id'], ctx.author.name)
    await ctx.send(f'✅ アラートを承認しました (Trigger ID: {params["trigger_id"]})')

async def health_checks_handler(ctx, params):
    """Handle showing health checks"""
    checks = get_health_checks(limit=30)

    if not checks:
        await ctx.send('📋 ヘルスチェックがありません')
        return

    embed = discord.Embed(title='💚 ヘルスチェック', color=discord.Color.green())

    healthy = sum(1 for c in checks if c['status'] == 'healthy')
    unhealthy = sum(1 for c in checks if c['status'] == 'unhealthy')
    degraded = sum(1 for c in checks if c['status'] == 'degraded')

    embed.add_field(name='Summary', value=f'✅ Healthy: {healthy} | ⚠️ Degraded: {degraded} | ❌ Unhealthy: {unhealthy}', inline=False)

    for check in checks[:10]:
        service_name = f"Service {check['service_id']}"  # Simplified
        response_time = check.get('response_time_ms', 0)
        status_emoji = {'healthy': '✅', 'unhealthy': '❌', 'degraded': '⚠️', 'unknown': '⚪'}.get(check['status'], '⚪')
        checked_at = datetime.fromisoformat(check['checked_at']).strftime('%H:%M:%S')

        embed.add_field(
            name=f"{status_emoji} {service_name} ({check['check_type']})",
            value=f"Response: {response_time}ms | Checked: {checked_at}",
            inline=False
        )

    await ctx.send(embed=embed)

async def create_incident_handler(ctx, params):
    """Handle incident creation"""
    if 'title' not in params:
        await ctx.send('❌ タイトルを指定してください。例: インシデント作成 "API Outage" critical')
        return

    severity = params.get('severity', 'major')
    incident_id = create_incident(params['title'], severity=severity, created_by=ctx.author.name)
    await ctx.send(f'🚨 インシデントを作成しました (ID: {incident_id}): {params["title"]} ({severity})')

async def list_incidents_handler(ctx, params):
    """Handle listing incidents"""
    incidents = get_incidents(limit=20)

    if not incidents:
        await ctx.send('📋 インシデントがありません')
        return

    embed = discord.Embed(title='🚨 インシデント一覧', color=discord.Color.red())

    for incident in incidents:
        severity_emoji = {'minor': '🟡', 'major': '🟠', 'critical': '🔴'}.get(incident['severity'], '⚪')
        status_emoji = {'open': '📌', 'investigating': '🔍', 'resolved': '✅', 'closed': '📦'}.get(incident['status'], '⚪')
        detected_at = datetime.fromisoformat(incident['detected_at']).strftime('%Y-%m-%d %H:%M')

        embed.add_field(
            name=f"{status_emoji} {severity_emoji} ID {incident['id']}: {incident['title']}",
            value=f"Status: {incident['status']} | Detected: {detected_at}",
            inline=False
        )

    await ctx.send(embed=embed)

async def resolve_incident_handler(ctx, params):
    """Handle resolving an incident"""
    if 'incident_id' not in params:
        await ctx.send('❌ インシデントIDを指定してください。例: インシデント解決 ID: 123')
        return

    update_incident(params['incident_id'], status='resolved')
    await ctx.send(f'✅ インシデントを解決しました (ID: {params["incident_id"]})')

async def create_dashboard_handler(ctx, params):
    """Handle dashboard creation"""
    if 'name' not in params:
        await ctx.send('❌ ダッシュボード名を指定してください。例: ダッシュボード作成 "Main Dashboard"')
        return

    dashboard_id = create_dashboard(params['name'])
    await ctx.send(f'📊 ダッシュボードを作成しました (ID: {dashboard_id}): {params["name"]}')

async def list_dashboards_handler(ctx, params):
    """Handle listing dashboards"""
    dashboards = get_dashboards()

    if not dashboards:
        await ctx.send('📋 ダッシュボードがありません')
        return

    embed = discord.Embed(title='📊 ダッシュボード一覧', color=discord.Color.purple())

    for dash in dashboards:
        created_at = datetime.fromisoformat(dash['created_at']).strftime('%Y-%m-%d')
        embed.add_field(
            name=f"ID {dash['id']}: {dash['name']}",
            value=f"{dash.get('description', 'No description')}\nCreated: {created_at}",
            inline=False
        )

    await ctx.send(embed=embed)

async def monitoring_summary_handler(ctx, params):
    """Handle showing monitoring summary"""
    summary = get_monitoring_summary()

    embed = discord.Embed(title='📈 モニタリング概要', color=discord.Color.blue())

    # Services
    services = summary.get('services', {})
    enabled_count = services.get('enabled_services', 0)
    embed.add_field(name='Monitored Services', value=str(enabled_count), inline=True)

    # Incidents
    active_incidents = summary.get('active_incidents', 0)
    incident_emoji = '🔴' if active_incidents > 0 else '✅'
    embed.add_field(name=f'{incident_emoji} Active Incidents', value=str(active_incidents), inline=True)

    # Alerts
    recent_alerts = summary.get('recent_alerts', 0)
    alert_emoji = '🚨' if recent_alerts > 0 else '✅'
    embed.add_field(name=f'{alert_emoji} Recent Alerts (1h)', value=str(recent_alerts), inline=True)

    # Health
    health = summary.get('health', {})
    healthy = health.get('healthy', 0)
    unhealthy = health.get('unhealthy', 0)
    degraded = health.get('degraded', 0)
    embed.add_field(
        name='Health Status (5m)',
        value=f'✅ {healthy} | ⚠️ {degraded} | ❌ {unhealthy}',
        inline=False
    )

    await ctx.send(embed=embed)

async def help_handler(ctx, params):
    """Handle help command"""
    embed = discord.Embed(title='📚 Monitor Agent - ヘルプ', color=discord.Color.blue())

    embed.add_field(name='サービス', value='サービス作成 "ServiceName" (api/database/cache)\nサービス一覧', inline=False)
    embed.add_field(name='メトリック', value='メトリック記録 cpu_usage 75.5\nメトリック', inline=False)
    embed.add_field(name='アラート', value='アラート作成 "High CPU" threshold 80\nアラート一覧\nアラート履歴\nアラート承認 ID: 123', inline=False)
    embed.add_field(name='ヘルスチェック', value='ヘルスチェック', inline=False)
    embed.add_field(name='インシデント', value='インシデント作成 "API Outage"\nインシデント一覧\nインシデント解決 ID: 123', inline=False)
    embed.add_field(name='ダッシュボード', value='ダッシュボード作成 "Dashboard Name"\nダッシュボード一覧', inline=False)
    embed.add_field(name='概要', value='モニタリング概要', inline=False)

    await ctx.send(embed=embed)

# Intent handlers
HANDLERS = {
    'create_service': create_service_handler,
    'list_services': list_services_handler,
    'record_metric': record_metric_handler,
    'list_metrics': list_metrics_handler,
    'create_alert': create_alert_handler,
    'list_alerts': list_alerts_handler,
    'alert_history': alert_history_handler,
    'acknowledge_alert': acknowledge_alert_handler,
    'health_checks': health_checks_handler,
    'create_incident': create_incident_handler,
    'list_incidents': list_incidents_handler,
    'resolve_incident': resolve_incident_handler,
    'create_dashboard': create_dashboard_handler,
    'list_dashboards': list_dashboards_handler,
    'monitoring_summary': monitoring_summary_handler,
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
