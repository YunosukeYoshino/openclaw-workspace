#!/usr/bin/env python3
"""
Test Agent - Discord Integration
Natural language processing for test management
"""

import discord
from discord.ext import commands
import sqlite3
from pathlib import Path
import json
from datetime import datetime
import re

from db import (
    init_db, create_suite, get_suites, delete_suite,
    create_case, get_cases, delete_case,
    start_test_run, complete_test_run, delete_test_run,
    add_test_result, get_test_results, delete_test_result,
    get_test_runs, add_test_data, get_test_data, delete_test_data,
    save_coverage, get_coverage, delete_coverage,
    create_test_issue, get_test_issues, resolve_issue, delete_test_issue,
    get_test_summary
)

# Initialize database
DB_PATH = Path(__file__).parent / "test.db"
if not DB_PATH.exists():
    init_db()

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Natural language patterns
PATTERNS = {
    # Suite operations
    r'スイート作成|テストスイート作成|create.*suite|new.*suite': 'create_suite',
    r'スイート一覧|テストスイート|suites|list.*suites': 'list_suites',

    # Case operations
    r'テストケース作成|ケース作成|create.*case|new.*case': 'create_case',
    r'テストケース|ケース一覧|cases|list.*cases': 'list_cases',

    # Run operations
    r'テスト実行|テスト開始|start.*test|run.*test': 'start_run',
    r'テスト実行中|running.*tests': 'list_running_tests',
    r'テスト結果|test.*results|results': 'test_results',

    # Coverage
    r'カバレッジ|coverage': 'coverage',

    # Issues
    r'テスト課題|test.*issues|issues': 'test_issues',
    r'課題解決|resolve.*issue': 'resolve_issue',

    # Summary
    r'テスト概要|test.*summary|summary': 'test_summary',

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

    if intent == 'create_suite':
        # Extract name and description
        parts = message.split('"')
        if len(parts) >= 2:
            params['name'] = parts[1]
        if len(parts) >= 4:
            params['description'] = parts[3]

    elif intent == 'create_case':
        # Extract name, suite, type, priority
        parts = message.split('"')
        if len(parts) >= 2:
            params['name'] = parts[1]
        if 'ユニットテスト|unit.*test' in message.lower():
            params['test_type'] = 'unit'
        elif '結合テスト|integration.*test' in message.lower():
            params['test_type'] = 'integration'
        elif 'e2eテスト|e2e.*test' in message.lower():
            params['test_type'] = 'e2e'
        elif 'パフォーマンステスト|performance.*test' in message.lower():
            params['test_type'] = 'performance'

        if '高|high' in message.lower():
            params['priority'] = 'high'
        elif '重要|critical' in message.lower():
            params['priority'] = 'critical'

    elif intent == 'start_run':
        # Extract name, environment, build version
        parts = message.split('"')
        if len(parts) >= 2:
            params['name'] = parts[1]
        if 'staging' in message.lower():
            params['environment'] = 'staging'
        elif 'production|prod' in message.lower():
            params['environment'] = 'production'
        else:
            params['environment'] = 'development'

    elif intent == 'resolve_issue':
        # Extract issue ID
        match = re.search(r'(\d+)', message)
        if match:
            params['issue_id'] = int(match.group(1))

    return params

async def create_suite_handler(ctx, params):
    """Handle test suite creation"""
    if 'name' not in params:
        await ctx.send('❌ スイート名を指定してください。例: スイート作成 "My Suite" "Description"')
        return

    suite_id = create_suite(params['name'], params.get('description'))
    await ctx.send(f'✅ テストスイートを作成しました (ID: {suite_id}): {params["name"]}')

async def list_suites_handler(ctx, params):
    """Handle listing test suites"""
    suites = get_suites(limit=20)

    if not suites:
        await ctx.send('📋 テストスイートがありません')
        return

    embed = discord.Embed(title='📋 テストスイート一覧', color=discord.Color.blue())
    for suite in suites:
        desc = suite.get('description') or '説明なし'
        component = suite.get('component') or 'N/A'
        embed.add_field(name=f"ID {suite['id']}: {suite['name']}", value=f'{desc}\nComponent: {component}', inline=False)

    await ctx.send(embed=embed)

async def create_case_handler(ctx, params):
    """Handle test case creation"""
    if 'name' not in params:
        await ctx.send('❌ テストケース名を指定してください。例: ケース作成 "My Case" - スイートID: 1')
        return

    # Get suite ID from message or default to 1
    match = re.search(r'スイートID[:\s]*(\d+)', ctx.message.content)
    suite_id = int(match.group(1)) if match else 1

    case_id = create_case(
        suite_id=suite_id,
        name=params['name'],
        test_type=params.get('test_type', 'functional'),
        priority=params.get('priority', 'medium')
    )

    await ctx.send(f'✅ テストケースを作成しました (ID: {case_id}): {params["name"]}')

async def list_cases_handler(ctx, params):
    """Handle listing test cases"""
    cases = get_cases(limit=50)

    if not cases:
        await ctx.send('📋 テストケースがありません')
        return

    embed = discord.Embed(title='📋 テストケース一覧', color=discord.Color.blue())

    for case in cases[:10]:  # Limit to 10 for readability
        status_emoji = {'active': '✅', 'deprecated': '⚠️', 'archived': '📦'}.get(case['status'], '❓')
        priority_emoji = {'low': '🟢', 'medium': '🟡', 'high': '🟠', 'critical': '🔴'}.get(case['priority'], '⚪')

        embed.add_field(
            name=f"{status_emoji} {priority_emoji} ID {case['id']}: {case['name']}",
            value=f"Type: {case['test_type']} | Suite ID: {case['suite_id']}",
            inline=False
        )

    if len(cases) > 10:
        embed.set_footer(text=f'他 {len(cases) - 10} 件のテストケースがあります')

    await ctx.send(embed=embed)

async def start_run_handler(ctx, params):
    """Handle starting a test run"""
    name = params.get('name', f'Test Run {datetime.now().strftime("%Y%m%d_%H%M%S")}')
    environment = params.get('environment', 'development')

    run_id = start_test_run(name, environment)
    await ctx.send(f'🚀 テスト実行を開始しました (ID: {run_id}): {name} ({environment})')

async def list_running_tests_handler(ctx, params):
    """Handle listing running tests"""
    runs = get_test_runs(status='running', limit=10)

    if not runs:
        await ctx.send('📋 実行中のテストはありません')
        return

    embed = discord.Embed(title='🔄 実行中のテスト', color=discord.Color.orange())

    for run in runs:
        started = datetime.fromisoformat(run['started_at']).strftime('%Y-%m-%d %H:%M')
        embed.add_field(name=f"ID {run['id']}: {run['name']}", value=f'Environment: {run["environment"]} | Started: {started}', inline=False)

    await ctx.send(embed=embed)

async def test_results_handler(ctx, params):
    """Handle showing test results"""
    runs = get_test_runs(status='completed', limit=5)

    if not runs:
        await ctx.send('📋 テスト結果がありません')
        return

    embed = discord.Embed(title='📊 テスト結果', color=discord.Color.green())

    for run in runs:
        pass_rate = (run['passed'] / run['total_tests'] * 100) if run['total_tests'] > 0 else 0
        status_emoji = '✅' if run['failed'] == 0 else '❌'

        embed.add_field(
            name=f"{status_emoji} {run['name']}",
            value=f"Passed: {run['passed']}/{run['total_tests']} | Failed: {run['failed']} | Pass Rate: {pass_rate:.1f}%",
            inline=False
        )

    await ctx.send(embed=embed)

async def coverage_handler(ctx, params):
    """Handle showing test coverage"""
    coverage_data = get_coverage(limit=20)

    if not coverage_data:
        await ctx.send('📋 カバレッジデータがありません')
        return

    embed = discord.Embed(title='📈 テストカバレッジ', color=discord.Color.purple())

    for cov in coverage_data[:10]:
        if cov['total_lines'] > 0:
            line_pct = (cov['covered_lines'] / cov['total_lines'] * 100)
            embed.add_field(
                name=f"{cov['component']}: {cov['file_path']}",
                value=f"Lines: {line_pct:.1f}% | Branch: {cov['branch_coverage']}% | Function: {cov['function_coverage']}%",
                inline=False
            )

    await ctx.send(embed=embed)

async def test_issues_handler(ctx, params):
    """Handle showing test issues"""
    issues = get_test_issues(limit=20)

    if not issues:
        await ctx.send('📋 テスト課題がありません')
        return

    embed = discord.Embed(title='🐛 テスト課題', color=discord.Color.red())

    for issue in issues[:10]:
        severity_emoji = {'low': '🟢', 'medium': '🟡', 'high': '🟠', 'critical': '🔴'}.get(issue['severity'], '⚪')
        type_emoji = {'flaky': '🔄', 'bug': '🐛', 'performance': '⚡', 'security': '🔒'}.get(issue['issue_type'], '❓')

        embed.add_field(
            name=f"{severity_emoji} {type_emoji} ID {issue['id']}: {issue['title']}",
            value=f"Type: {issue['issue_type']} | Status: {issue['status']}",
            inline=False
        )

    await ctx.send(embed=embed)

async def resolve_issue_handler(ctx, params):
    """Handle resolving an issue"""
    if 'issue_id' not in params:
        await ctx.send('❌ 課題IDを指定してください。例: 課題解決 ID: 123')
        return

    resolve_issue(params['issue_id'])
    await ctx.send(f'✅ 課題を解決しました (ID: {params["issue_id"]})')

async def test_summary_handler(ctx, params):
    """Handle showing test summary"""
    summary = get_test_summary()

    if not summary or summary.get('total_tests', 0) == 0:
        await ctx.send('📋 テスト概要がありません')
        return

    pass_rate = summary.get('pass_rate', 0)
    total = summary.get('total_tests', 0)
    passed = summary.get('passed', 0)
    failed = summary.get('failed', 0)
    skipped = summary.get('skipped', 0)

    embed = discord.Embed(title='📊 テスト概要', color=discord.Color.blue())
    embed.add_field(name='Total Tests', value=str(total), inline=True)
    embed.add_field(name='Passed', value=str(passed), inline=True)
    embed.add_field(name='Failed', value=str(failed), inline=True)
    embed.add_field(name='Skipped', value=str(skipped), inline=True)
    embed.add_field(name='Pass Rate', value=f'{pass_rate}%', inline=False)

    await ctx.send(embed=embed)

async def help_handler(ctx, params):
    """Handle help command"""
    embed = discord.Embed(title='📚 Test Agent - ヘルプ', color=discord.Color.blue())

    embed.add_field(name='テストスイート', value='スイート作成 "Suite Name"\nスイート一覧', inline=False)
    embed.add_field(name='テストケース', value='ケース作成 "Case Name" - スイートID: 1\nテストケース', inline=False)
    embed.add_field(name='テスト実行', value='テスト実行 "Run Name" (environment: staging)\nテスト実行中\nテスト結果', inline=False)
    embed.add_field(name='カバレッジ', value='カバレッジ', inline=False)
    embed.add_field(name='課題管理', value='テスト課題\n課題解決 ID: 123', inline=False)
    embed.add_field(name='概要', value='テスト概要', inline=False)

    await ctx.send(embed=embed)

# Intent handlers
HANDLERS = {
    'create_suite': create_suite_handler,
    'list_suites': list_suites_handler,
    'create_case': create_case_handler,
    'list_cases': list_cases_handler,
    'start_run': start_run_handler,
    'list_running_tests': list_running_tests_handler,
    'test_results': test_results_handler,
    'coverage': coverage_handler,
    'test_issues': test_issues_handler,
    'resolve_issue': resolve_issue_handler,
    'test_summary': test_summary_handler,
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
