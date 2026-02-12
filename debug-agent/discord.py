#!/usr/bin/env python3
"""
Debug Agent - Discord Integration
Natural language processing for debug management
"""

import discord
from discord.ext import commands
import sqlite3
from pathlib import Path
import json
from datetime import datetime
import re

from db import (
    init_db, create_session, get_session, list_sessions, update_session_status,
    create_issue, get_issues, update_issue_status,
    add_note, get_notes, create_solution, get_solutions, verify_solution,
    add_resource, get_resources, start_time_entry, end_time_entry
)

# Initialize database
DB_PATH = Path(__file__).parent / "debug.db"
if not DB_PATH.exists():
    init_db()

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Natural language patterns
PATTERNS = {
    # Session operations
    r'セッション作成|session.*create|create.*session|new.*session': 'create_session',
    r'セッション一覧|sessions|list.*session': 'list_sessions',
    r'セッション完了|session.*complete|finish.*session': 'complete_session',

    # Issue operations
    r'課題作成|issue.*create|create.*issue': 'create_issue',
    r'課題一覧|issues|list.*issue': 'list_issues',
    r'課題解決|issue.*resolve|resolve.*issue': 'resolve_issue',

    # Note operations
    r'ノート|note.*add|add.*note': 'add_note',

    # Solution operations
    r'解決策|solution.*add|add.*solution': 'add_solution',
    r'解決策検証|solution.*verify|verify.*solution': 'verify_solution',

    # Resource operations
    r'リソース|resource|add.*resource': 'add_resource',

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

    if intent == 'create_session':
        # Extract title and description
        parts = message.split('"')
        if len(parts) >= 2:
            params['title'] = parts[1]
        if len(parts) >= 4:
            params['description'] = parts[3]

        if '高|high' in message.lower():
            params['priority'] = 'high'
        elif '重要|critical' in message.lower():
            params['priority'] = 'critical'

    elif intent == 'create_issue':
        # Extract title
        parts = message.split('"')
        if len(parts) >= 2:
            params['title'] = parts[1]

        # Extract session ID
        match = re.search(r'セッションID[:\s]*(\d+)|session.*id[:\s]*(\d+)', message.lower())
        if match:
            params['session_id'] = int(match.group(1) if match.group(1) else match.group(2))

        if '重要|critical' in message.lower():
            params['severity'] = 'critical'
        elif '重大|major' in message.lower():
            params['severity'] = 'major'

    elif intent == 'complete_session':
        # Extract session ID
        match = re.search(r'ID[:\s]*(\d+)', message)
        if match:
            params['session_id'] = int(match.group(1))

    elif intent == 'resolve_issue':
        # Extract issue ID
        match = re.search(r'ID[:\s]*(\d+)', message)
        if match:
            params['issue_id'] = int(match.group(1))

    elif intent == 'add_note':
        # Extract note content
        parts = message.split('"')
        if len(parts) >= 2:
            params['content'] = parts[1]

        # Extract session ID
        match = re.search(r'セッションID[:\s]*(\d+)', message.lower())
        if match:
            params['session_id'] = int(match.group(1))

    elif intent == 'add_solution':
        # Extract description
        parts = message.split('"')
        if len(parts) >= 2:
            params['description'] = parts[1]

        # Extract issue ID
        match = re.search(r'課題ID[:\s]*(\d+)|issue.*id[:\s]*(\d+)', message.lower())
        if match:
            params['issue_id'] = int(match.group(1) if match.group(1) else match.group(2))

    elif intent == 'verify_solution':
        # Extract solution ID
        match = re.search(r'ID[:\s]*(\d+)', message)
        if match:
            params['solution_id'] = int(match.group(1))

    elif intent == 'add_resource':
        # Extract description
        parts = message.split('"')
        if len(parts) >= 2:
            params['description'] = parts[1]

        # Extract session ID
        match = re.search(r'セッションID[:\s]*(\d+)', message.lower())
        if match:
            params['session_id'] = int(match.group(1))

        if 'screenshot|スクリーンショット' in message.lower():
            params['resource_type'] = 'screenshot'
        elif 'log|ログ' in message.lower():
            params['resource_type'] = 'log'

    return params

async def create_session_handler(ctx, params):
    """Handle creating a debug session"""
    if 'title' not in params:
        await ctx.send('❌ セッションタイトルを指定してください。例: セッション作成 "Login Bug"')
        return

    priority = params.get('priority', 'normal')
    session_id = create_session(params['title'], description=params.get('description'), priority=priority)
    await ctx.send(f'🔍 デバッグセッションを作成しました (ID: {session_id}): {params["title"]} ({priority})')

async def list_sessions_handler(ctx, params):
    """Handle listing debug sessions"""
    sessions = list_sessions(limit=20)

    if not sessions:
        await ctx.send('📋 セッションがありません')
        return

    embed = discord.Embed(title='🔍 デバッグセッション一覧', color=discord.Color.blue())

    for session in sessions:
        status_emoji = {'active': '🔄', 'paused': '⏸️', 'completed': '✅', 'abandoned': '📦'}.get(session['status'], '⚪')
        priority_emoji = {'low': '🟢', 'normal': '🟡', 'high': '🟠', 'critical': '🔴'}.get(session['priority'], '⚪')
        created_at = datetime.fromisoformat(session['created_at']).strftime('%Y-%m-%d %H:%M')

        embed.add_field(
            name=f"{status_emoji} {priority_emoji} ID {session['id']}: {session['title']}",
            value=f"Status: {session['status']} | Created: {created_at}",
            inline=False
        )

    await ctx.send(embed=embed)

async def complete_session_handler(ctx, params):
    """Handle completing a debug session"""
    if 'session_id' not in params:
        await ctx.send('❌ セッションIDを指定してください。例: セッション完了 ID: 123')
        return

    update_session_status(params['session_id'], 'completed')
    await ctx.send(f'✅ セッションを完了しました (ID: {params["session_id"]})')

async def create_issue_handler(ctx, params):
    """Handle creating an issue"""
    if 'title' not in params:
        await ctx.send('❌ 課題タイトルを指定してください。例: 課題作成 "Login Error"')
        return

    # Use the most recent session if no session_id specified
    session_id = params.get('session_id')
    if not session_id:
        sessions = list_sessions(limit=1)
        if sessions:
            session_id = sessions[0]['id']
        else:
            await ctx.send('❌ 先にセッションを作成してください')
            return

    severity = params.get('severity', 'major')
    issue_id = create_issue(session_id, params['title'], severity=severity)
    await ctx.send(f'🐛 課題を作成しました (ID: {issue_id}): {params["title"]} (severity: {severity})')

async def list_issues_handler(ctx, params):
    """Handle listing issues"""
    issues = get_issues(limit=20)

    if not issues:
        await ctx.send('📋 課題がありません')
        return

    embed = discord.Embed(title='🐛 課題一覧', color=discord.Color.red())

    for issue in issues[:10]:
        status_emoji = {'open': '📌', 'investigating': '🔍', 'resolved': '✅', 'closed': '📦', 'reopened': '🔄'}.get(issue['status'], '⚪')
        severity_emoji = {'info': '🔵', 'minor': '🟢', 'major': '🟠', 'critical': '🔴'}.get(issue['severity'], '⚪')

        embed.add_field(
            name=f"{status_emoji} {severity_emoji} ID {issue['id']}: {issue['title']}",
            value=f"Status: {issue['status']} | Session ID: {issue['session_id']}",
            inline=False
        )

    await ctx.send(embed=embed)

async def resolve_issue_handler(ctx, params):
    """Handle resolving an issue"""
    if 'issue_id' not in params:
        await ctx.send('❌ 課題IDを指定してください。例: 課題解決 ID: 123')
        return

    update_issue_status(params['issue_id'], 'resolved')
    await ctx.send(f'✅ 課題を解決しました (ID: {params["issue_id"]})')

async def add_note_handler(ctx, params):
    """Handle adding a debug note"""
    if 'content' not in params:
        await ctx.send('❌ ノート内容を指定してください。例: ノート "This is a note"')
        return

    # Use the most recent session if no session_id specified
    session_id = params.get('session_id')
    if not session_id:
        sessions = list_sessions(limit=1)
        if sessions:
            session_id = sessions[0]['id']
        else:
            await ctx.send('❌ 先にセッションを作成してください')
            return

    add_note(session_id, params['content'], author=ctx.author.name)
    await ctx.send(f'📝 ノートを追加しました: {params["content"]}')

async def add_solution_handler(ctx, params):
    """Handle adding a solution"""
    if 'description' not in params:
        await ctx.send('❌ 解決策を指定してください。例: 解決策 "Fixed by updating API"')
        return

    # Get the most recent issue if no issue_id specified
    issue_id = params.get('issue_id')
    if not issue_id:
        issues = get_issues(limit=1)
        if issues:
            issue_id = issues[0]['id']
            session_id = issues[0]['session_id']
        else:
            await ctx.send('❌ 先に課題を作成してください')
            return
    else:
        # Find session_id from issue
        issues = get_issues(limit=100)
        for issue in issues:
            if issue['id'] == issue_id:
                session_id = issue['session_id']
                break

    create_solution(session_id, issue_id, params['description'])
    await ctx.send(f'💡 解決策を追加しました: {params["description"]}')

async def verify_solution_handler(ctx, params):
    """Handle verifying a solution"""
    if 'solution_id' not in params:
        await ctx.send('❌ 解決策IDを指定してください。例: 解決策検証 ID: 123')
        return

    verify_solution(params['solution_id'])
    await ctx.send(f'✅ 解決策を検証しました (ID: {params["solution_id"]})')

async def add_resource_handler(ctx, params):
    """Handle adding a resource"""
    if 'description' not in params:
        await ctx.send('❌ リソース説明を指定してください。例: リソース "Error screenshot"')
        return

    # Use the most recent session if no session_id specified
    session_id = params.get('session_id')
    if not session_id:
        sessions = list_sessions(limit=1)
        if sessions:
            session_id = sessions[0]['id']
        else:
            await ctx.send('❌ 先にセッションを作成してください')
            return

    resource_type = params.get('resource_type', 'other')
    add_resource(session_id, resource_type, description=params['description'])
    await ctx.send(f'📎 リソースを追加しました: {params["description"]} ({resource_type})')

async def help_handler(ctx, params):
    """Handle help command"""
    embed = discord.Embed(title='📚 Debug Agent - ヘルプ', color=discord.Color.blue())

    embed.add_field(name='セッション', value='セッション作成 "Title"\nセッション一覧\nセッション完了 ID: 123', inline=False)
    embed.add_field(name='課題', value='課題作成 "Title"\n課題一覧\n課題解決 ID: 123', inline=False)
    embed.add_field(name='ノート', value='ノート "Note content"', inline=False)
    embed.add_field(name='解決策', value='解決策 "Solution description"\n解決策検証 ID: 123', inline=False)
    embed.add_field(name='リソース', value='リソース "Description" (screenshot/log)', inline=False)

    await ctx.send(embed=embed)

# Intent handlers
HANDLERS = {
    'create_session': create_session_handler,
    'list_sessions': list_sessions_handler,
    'complete_session': complete_session_handler,
    'create_issue': create_issue_handler,
    'list_issues': list_issues_handler,
    'resolve_issue': resolve_issue_handler,
    'add_note': add_note_handler,
    'add_solution': add_solution_handler,
    'verify_solution': verify_solution_handler,
    'add_resource': add_resource_handler,
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
