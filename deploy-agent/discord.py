#!/usr/bin/env python3
"""
Deploy Agent - Discord Integration
Natural language processing for deployment management
"""

import discord
from discord.ext import commands
import sqlite3
from pathlib import Path
import json
from datetime import datetime
import re

from db import (
    init_db, create_environment, get_environments, delete_environment,
    start_deployment, complete_deployment, delete_deployment, get_deployments,
    add_deployment_step, update_deployment_step, delete_deployment_step, get_deployment_steps,
    start_rollback, complete_rollback, delete_rollback, get_rollbacks,
    add_artifact, delete_artifact, get_artifacts, add_config, delete_config, get_configs,
    add_health_check, update_health_check, delete_health_check, get_health_checks,
    add_notification, delete_notification, get_notifications, get_deployment_stats
)

# Initialize database
DB_PATH = Path(__file__).parent / "deploy.db"
if not DB_PATH.exists():
    init_db()

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Natural language patterns
PATTERNS = {
    # Environment operations
    r'環境作成|環境追加|create.*environment|new.*environment': 'create_environment',
    r'環境一覧|environment|list.*env': 'list_environments',

    # Deployment operations
    r'デプロイ|deploy|デプロイ開始|start.*deploy': 'start_deployment',
    r'デプロイ中|deploying|active.*deploy': 'list_active_deployments',
    r'デプロイ履歴|deployment.*history|deploy.*history': 'deployment_history',
    r'デプロイ完了|deployment.*complete|finish.*deploy': 'complete_deployment',

    # Rollback operations
    r'ロールバック|rollback': 'rollback',
    r'ロールバック履歴|rollback.*history': 'rollback_history',

    # Artifacts and configs
    r'アーティファクト|artifact': 'artifacts',
    r'設定|config|configuration': 'configs',

    # Health checks
    r'ヘルスチェック|health.*check': 'health_checks',

    # Statistics
    r'デプロイ統計|deploy.*stat|deployment.*stat': 'deploy_stats',

    # Delete operations
    r'環境削除|delete.*environment|remove.*environment': 'delete_environment',
    r'デプロイ削除|delete.*deploy|remove.*deploy': 'delete_deployment',
    r'ロールバック削除|delete.*rollback|remove.*rollback': 'delete_rollback',
    r'アーティファクト削除|delete.*artifact|remove.*artifact': 'delete_artifact',
    r'設定削除|delete.*config|remove.*config': 'delete_config',
    r'ヘルスチェック削除|delete.*health|remove.*health': 'delete_health_check',

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

    if intent == 'create_environment':
        # Extract name and type
        parts = message.split('"')
        if len(parts) >= 2:
            params['name'] = parts[1]
        if 'staging' in message.lower():
            params['env_type'] = 'staging'
        elif 'production|prod' in message.lower():
            params['env_type'] = 'production'
        elif 'dev|development' in message.lower():
            params['env_type'] = 'development'

    elif intent == 'start_deployment':
        # Extract version, environment
        parts = message.split('"')
        if len(parts) >= 2:
            params['version'] = parts[1]
        if 'staging' in message.lower():
            params['env_type'] = 'staging'
        elif 'production|prod' in message.lower():
            params['env_type'] = 'production'
        else:
            params['env_type'] = 'development'

    elif intent == 'complete_deployment':
        # Extract deployment ID and status
        match = re.search(r'ID[:\s]*(\d+)', message)
        if match:
            params['deployment_id'] = int(match.group(1))
        if '成功|success|succeeded' in message.lower():
            params['status'] = 'success'
        elif '失敗|failed|error' in message.lower():
            params['status'] = 'failed'

    elif intent == 'rollback':
        # Extract deployment ID
        match = re.search(r'ID[:\s]*(\d+)', message)
        if match:
            params['deployment_id'] = int(match.group(1))

    elif intent == 'complete_deployment':
        # Extract deployment ID and status
        match = re.search(r'ID[:\s]*(\d+)', message)
        if match:
            params['deployment_id'] = int(match.group(1))

    elif intent == 'delete_environment':
        # Extract environment ID
        match = re.search(r'ID[:\s]*(\d+)', message)
        if match:
            params['env_id'] = int(match.group(1))

    elif intent == 'delete_deployment':
        # Extract deployment ID
        match = re.search(r'ID[:\s]*(\d+)', message)
        if match:
            params['deployment_id'] = int(match.group(1))

    elif intent == 'delete_rollback':
        # Extract rollback ID
        match = re.search(r'ID[:\s]*(\d+)', message)
        if match:
            params['rollback_id'] = int(match.group(1))

    elif intent == 'delete_artifact':
        # Extract artifact ID
        match = re.search(r'ID[:\s]*(\d+)', message)
        if match:
            params['artifact_id'] = int(match.group(1))

    elif intent == 'delete_config':
        # Extract config ID
        match = re.search(r'ID[:\s]*(\d+)', message)
        if match:
            params['config_id'] = int(match.group(1))

    elif intent == 'delete_health_check':
        # Extract health check ID
        match = re.search(r'ID[:\s]*(\d+)', message)
        if match:
            params['health_check_id'] = int(match.group(1))

    return params

async def create_environment_handler(ctx, params):
    """Handle environment creation"""
    if 'name' not in params:
        await ctx.send('❌ 環境名を指定してください。例: 環境作成 "Staging" staging')
        return

    env_type = params.get('env_type', 'development')
    env_id = create_environment(params['name'], env_type)
    await ctx.send(f'✅ 環境を作成しました (ID: {env_id}): {params["name"]} ({env_type})')

async def list_environments_handler(ctx, params):
    """Handle listing environments"""
    envs = get_environments(limit=20)

    if not envs:
        await ctx.send('📋 環境がありません')
        return

    embed = discord.Embed(title='🌍 環境一覧', color=discord.Color.blue())

    for env in envs:
        type_emoji = {'development': '🔧', 'staging': '🧪', 'production': '🚀', 'qa': '✅'}.get(env['type'], '❓')
        embed.add_field(
            name=f"{type_emoji} ID {env['id']}: {env['name']}",
            value=f"Type: {env['type']}\nBranch: {env.get('branch', 'N/A')}",
            inline=False
        )

    await ctx.send(embed=embed)

async def start_deployment_handler(ctx, params):
    """Handle starting a deployment"""
    version = params.get('version', f'v{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    env_type = params.get('env_type', 'development')

    # Find environment by type
    envs = get_environments(env_type=env_type)
    if not envs:
        await ctx.send(f'❌ {env_type} 環境が見つかりません')
        return

    env_id = envs[0]['id']
    triggered_by = ctx.author.name

    deployment_id = start_deployment(env_id, version, triggered_by)

    # Add default steps
    add_deployment_step(deployment_id, 'Build', 'build', 1)
    add_deployment_step(deployment_id, 'Test', 'test', 2)
    add_deployment_step(deployment_id, 'Deploy', 'deploy', 3)
    add_deployment_step(deployment_id, 'Verify', 'verify', 4)

    await ctx.send(f'🚀 デプロイを開始しました (ID: {deployment_id}): {version} → {envs[0]["name"]}')

async def list_active_deployments_handler(ctx, params):
    """Handle listing active deployments"""
    deployments = get_deployments(status='in_progress', limit=10)

    if not deployments:
        await ctx.send('📋 アクティブなデプロイはありません')
        return

    embed = discord.Embed(title='🔄 アクティブなデプロイ', color=discord.Color.orange())

    for dep in deployments:
        started = datetime.fromisoformat(dep['started_at']).strftime('%Y-%m-%d %H:%M')
        embed.add_field(
            name=f"ID {dep['id']}: {dep['version']}",
            value=f"Status: {dep['status']} | Started: {started}\nTriggered by: {dep['triggered_by']}",
            inline=False
        )

    await ctx.send(embed=embed)

async def deployment_history_handler(ctx, params):
    """Handle showing deployment history"""
    deployments = get_deployments(limit=10)

    if not deployments:
        await ctx.send('📋 デプロイ履歴がありません')
        return

    embed = discord.Embed(title='📜 デプロイ履歴', color=discord.Color.green())

    for dep in deployments:
        status_emoji = {'success': '✅', 'failed': '❌', 'rolled_back': '⏪', 'in_progress': '🔄'}.get(dep['status'], '⚪')
        started = datetime.fromisoformat(dep['started_at']).strftime('%Y-%m-%d %H:%M')

        embed.add_field(
            name=f"{status_emoji} ID {dep['id']}: {dep['version']}",
            value=f"Status: {dep['status']} | Started: {started}",
            inline=False
        )

    await ctx.send(embed=embed)

async def complete_deployment_handler(ctx, params):
    """Handle completing a deployment"""
    if 'deployment_id' not in params:
        await ctx.send('❌ デプロイIDを指定してください。例: デプロイ完了 ID: 123 success')
        return

    status = params.get('status', 'success')
    complete_deployment(params['deployment_id'], status, deployed_by=ctx.author.name)
    await ctx.send(f'✅ デプロイ完了 (ID: {params["deployment_id"]}): {status}')

async def rollback_handler(ctx, params):
    """Handle rollback"""
    if 'deployment_id' not in params:
        await ctx.send('❌ デプロイIDを指定してください。例: ロールバック ID: 123')
        return

    # Get the deployment to find the previous one
    deployments = get_deployments(environment_id=1, limit=10)  # Simplified, should use actual env_id
    current_idx = None
    for i, dep in enumerate(deployments):
        if dep['id'] == params['deployment_id']:
            current_idx = i
            break

    if current_idx is None or current_idx >= len(deployments) - 1:
        await ctx.send('❌ ロールバック対象が見つかりません')
        return

    original_deployment_id = deployments[current_idx + 1]['id']
    triggered_by = ctx.author.name

    rollback_id = start_rollback(params['deployment_id'], original_deployment_id, triggered_by)
    await ctx.send(f'⏪ ロールバックを開始しました (ID: {rollback_id}): {params["deployment_id"]} → {original_deployment_id}')

async def rollback_history_handler(ctx, params):
    """Handle showing rollback history"""
    rollbacks = get_rollbacks(limit=10)

    if not rollbacks:
        await ctx.send('📋 ロールバック履歴がありません')
        return

    embed = discord.Embed(title='⏪ ロールバック履歴', color=discord.Color.red())

    for rb in rollbacks:
        status_emoji = {'success': '✅', 'failed': '❌', 'pending': '⏳', 'in_progress': '🔄'}.get(rb['status'], '⚪')
        started = datetime.fromisoformat(rb['started_at']).strftime('%Y-%m-%d %H:%M')

        embed.add_field(
            name=f"{status_emoji} ID {rb['id']}: Deployment {rb['deployment_id']}",
            value=f"Status: {rb['status']} | Started: {started}\nReason: {rb.get('reason', 'N/A')}",
            inline=False
        )

    await ctx.send(embed=embed)

async def artifacts_handler(ctx, params):
    """Handle showing artifacts"""
    # Show from recent deployment
    deployments = get_deployments(limit=1)
    if not deployments:
        await ctx.send('📋 デプロイがありません')
        return

    artifacts = get_artifacts(deployment_id=deployments[0]['id'], limit=20)

    if not artifacts:
        await ctx.send('📋 アーティファクトがありません')
        return

    embed = discord.Embed(title='📦 アーティファクト', color=discord.Color.purple())

    for art in artifacts:
        size_mb = art.get('size_bytes', 0) / (1024 * 1024) if art.get('size_bytes') else 0
        embed.add_field(
            name=f"{art['artifact_name']}",
            value=f"Type: {art['artifact_type']} | Size: {size_mb:.2f} MB",
            inline=False
        )

    await ctx.send(embed=embed)

async def configs_handler(ctx, params):
    """Handle showing configs"""
    # Show from recent deployment
    deployments = get_deployments(limit=1)
    if not deployments:
        await ctx.send('📋 デプロイがありません')
        return

    configs = get_configs(deployment_id=deployments[0]['id'])

    if not configs:
        await ctx.send('📋 設定がありません')
        return

    embed = discord.Embed(title='⚙️ 設定', color=discord.Color.gold())

    for config in configs[:10]:
        value = '*** (sensitive)' if config.get('is_sensitive') else config.get('config_value', 'N/A')
        embed.add_field(
            name=f"{config['config_key']} ({config['config_type']})",
            value=value,
            inline=False
        )

    await ctx.send(embed=embed)

async def health_checks_handler(ctx, params):
    """Handle showing health checks"""
    # Show from recent deployment
    deployments = get_deployments(limit=1)
    if not deployments:
        await ctx.send('📋 デプロイがありません')
        return

    checks = get_health_checks(deployment_id=deployments[0]['id'])

    if not checks:
        await ctx.send('📋 ヘルスチェックがありません')
        return

    embed = discord.Embed(title='💚 ヘルスチェック', color=discord.Color.green())

    for check in checks:
        status_emoji = {'pass': '✅', 'fail': '❌', 'pending': '⏳'}.get(check['status'], '⚪')
        response_time = check.get('response_time_ms', 0)
        embed.add_field(
            name=f"{status_emoji} {check['check_name']}",
            value=f"Type: {check['check_type']} | Response: {response_time}ms\nEndpoint: {check.get('endpoint', 'N/A')}",
            inline=False
        )

    await ctx.send(embed=embed)

async def deploy_stats_handler(ctx, params):
    """Handle showing deployment statistics"""
    stats = get_deployment_stats(days=30)

    if not stats or stats.get('total', 0) == 0:
        await ctx.send('📋 統計データがありません')
        return

    total = stats.get('total', 0)
    successful = stats.get('successful', 0)
    failed = stats.get('failed', 0)
    rolled_back = stats.get('rolled_back', 0)
    avg_duration = stats.get('avg_duration_seconds', 0) / 60  # Convert to minutes

    success_rate = (successful / total * 100) if total > 0 else 0

    embed = discord.Embed(title='📊 デプロイ統計 (過去30日)', color=discord.Color.blue())
    embed.add_field(name='Total Deployments', value=str(total), inline=True)
    embed.add_field(name='Successful', value=str(successful), inline=True)
    embed.add_field(name='Failed', value=str(failed), inline=True)
    embed.add_field(name='Rolled Back', value=str(rolled_back), inline=True)
    embed.add_field(name='Success Rate', value=f'{success_rate:.1f}%', inline=False)
    embed.add_field(name='Avg Duration', value=f'{avg_duration:.1f} min', inline=True)

    await ctx.send(embed=embed)

async def delete_environment_handler(ctx, params):
    """Handle deleting an environment"""
    if 'env_id' not in params:
        await ctx.send('❌ 環境IDを指定してください。例: 環境削除 ID: 123')
        return

    success = delete_environment(params['env_id'])
    if success:
        await ctx.send(f'🗑️ 環境を削除しました (ID: {params["env_id"]})')
    else:
        await ctx.send(f'❌ 環境の削除に失敗しました (ID: {params["env_id"]})')

async def delete_deployment_handler(ctx, params):
    """Handle deleting a deployment"""
    if 'deployment_id' not in params:
        await ctx.send('❌ デプロイIDを指定してください。例: デプロイ削除 ID: 123')
        return

    success = delete_deployment(params['deployment_id'])
    if success:
        await ctx.send(f'🗑️ デプロイを削除しました (ID: {params["deployment_id"]})')
    else:
        await ctx.send(f'❌ デプロイの削除に失敗しました (ID: {params["deployment_id"]})')

async def delete_rollback_handler(ctx, params):
    """Handle deleting a rollback"""
    if 'rollback_id' not in params:
        await ctx.send('❌ ロールバックIDを指定してください。例: ロールバック削除 ID: 123')
        return

    success = delete_rollback(params['rollback_id'])
    if success:
        await ctx.send(f'🗑️ ロールバックを削除しました (ID: {params["rollback_id"]})')
    else:
        await ctx.send(f'❌ ロールバックの削除に失敗しました (ID: {params["rollback_id"]})')

async def delete_artifact_handler(ctx, params):
    """Handle deleting an artifact"""
    if 'artifact_id' not in params:
        await ctx.send('❌ アーティファクトIDを指定してください。例: アーティファクト削除 ID: 123')
        return

    success = delete_artifact(params['artifact_id'])
    if success:
        await ctx.send(f'🗑️ アーティファクトを削除しました (ID: {params["artifact_id"]})')
    else:
        await ctx.send(f'❌ アーティファクトの削除に失敗しました (ID: {params["artifact_id"]})')

async def delete_config_handler(ctx, params):
    """Handle deleting a config"""
    if 'config_id' not in params:
        await ctx.send('❌ 設定IDを指定してください。例: 設定削除 ID: 123')
        return

    success = delete_config(params['config_id'])
    if success:
        await ctx.send(f'🗑️ 設定を削除しました (ID: {params["config_id"]})')
    else:
        await ctx.send(f'❌ 設定の削除に失敗しました (ID: {params["config_id"]})')

async def delete_health_check_handler(ctx, params):
    """Handle deleting a health check"""
    if 'health_check_id' not in params:
        await ctx.send('❌ ヘルスチェックIDを指定してください。例: ヘルスチェック削除 ID: 123')
        return

    success = delete_health_check(params['health_check_id'])
    if success:
        await ctx.send(f'🗑️ ヘルスチェックを削除しました (ID: {params["health_check_id"]})')
    else:
        await ctx.send(f'❌ ヘルスチェックの削除に失敗しました (ID: {params["health_check_id"]})')

async def help_handler(ctx, params):
    """Handle help command"""
    embed = discord.Embed(title='📚 Deploy Agent - ヘルプ', color=discord.Color.blue())

    embed.add_field(name='環境管理', value='環境作成 "EnvName" (staging/production)\n環境一覧\n環境削除 ID: 123', inline=False)
    embed.add_field(name='デプロイ', value='デプロイ "Version" (staging/production)\nデプロイ中\nデプロイ履歴\nデプロイ完了 ID: 123 success\nデプロイ削除 ID: 123', inline=False)
    embed.add_field(name='ロールバック', value='ロールバック ID: 123\nロールバック履歴\nロールバック削除 ID: 123', inline=False)
    embed.add_field(name='詳細', value='アーティファクト\nアーティファクト削除 ID: 123\n設定\n設定削除 ID: 123\nヘルスチェック\nヘルスチェック削除 ID: 123', inline=False)
    embed.add_field(name='統計', value='デプロイ統計', inline=False)

    await ctx.send(embed=embed)

# Intent handlers
HANDLERS = {
    'create_environment': create_environment_handler,
    'list_environments': list_environments_handler,
    'start_deployment': start_deployment_handler,
    'list_active_deployments': list_active_deployments_handler,
    'deployment_history': deployment_history_handler,
    'complete_deployment': complete_deployment_handler,
    'rollback': rollback_handler,
    'rollback_history': rollback_history_handler,
    'artifacts': artifacts_handler,
    'configs': configs_handler,
    'health_checks': health_checks_handler,
    'deploy_stats': deploy_stats_handler,
    'delete_environment': delete_environment_handler,
    'delete_deployment': delete_deployment_handler,
    'delete_rollback': delete_rollback_handler,
    'delete_artifact': delete_artifact_handler,
    'delete_config': delete_config_handler,
    'delete_health_check': delete_health_check_handler,
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


# ============================================
# Test Code / テストコード
# ============================================

"""
# Test parsing
def test_parse_message():
    messages = [
        "環境作成 \"Staging\" staging",
        "環境一覧",
        "デプロイ \"v1.0.0\" staging",
        "デプロイ中",
        "デプロイ履歴",
        "デプロイ完了 ID: 123 success",
        "ロールバック ID: 123",
        "ロールバック履歴",
        "アーティファクト",
        "設定",
        "ヘルスチェック",
        "デプロイ統計",
        "環境削除 ID: 123",
        "デプロイ削除 ID: 123",
        "ロールバック削除 ID: 123",
        "アーティファクト削除 ID: 123",
        "設定削除 ID: 123",
        "ヘルスチェック削除 ID: 123",
        "ヘルプ",
    ]

    for msg in messages:
        intent = parse_message(msg)
        params = extract_params(msg, intent)
        print(f"Message: {msg}")
        print(f"  Intent: {intent}")
        print(f"  Params: {params}")
        print()

# Test create_environment
def test_create_environment():
    env_id = create_environment("Test Environment", "development")
    print(f"Created environment with ID: {env_id}")

# Test start_deployment
def test_start_deployment():
    envs = get_environments()
    if envs:
        dep_id = start_deployment(envs[0]['id'], "v1.0.0", "test_user")
        print(f"Started deployment with ID: {dep_id}")

# Test get_deployment_stats
def test_get_deployment_stats():
    stats = get_deployment_stats(days=30)
    print(f"Deployment stats: {stats}")

# Test delete functions
def test_delete():
    env_id = create_environment("Test Delete", "development")
    result = delete_environment(env_id)
    print(f"Delete environment {env_id}: {result}")

if __name__ == '__main__':
    # Run tests
    print("=== Testing Deploy Agent ===")
    test_parse_message()
    test_create_environment()
    test_start_deployment()
    test_get_deployment_stats()
    test_delete()
"""
