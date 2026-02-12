#!/usr/bin/env python3
"""
Debug Agent - Discord Bot
Debug sessions and issues management with natural language interface
"""

import discord
from discord.ext import commands
import json
from datetime import datetime
from db import (
    init_db, create_session, get_session, list_sessions, update_session_status,
    create_issue, get_issues, update_issue_status,
    add_note, get_notes, create_solution, get_solutions, verify_solution,
    add_resource, get_resources
)

# Database initialization
init_db()

# Discord Bot Configuration
INTENTS = discord.Intents.default()
INTENTS.message_content = True

bot = commands.Bot(command_prefix='!', intents=INTENTS)

@bot.event
async def on_ready():
    print(f'✅ Debug Agent ready as {bot.user}')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.lower()

    # Create debug session
    if any(keyword in content for keyword in ['デバッグ開始', 'デバッグセッション', 'debug session', '新規デバッグ']):
        title = message.content.split('デバッグ開始')[1].split('デバッグセッション')[0].strip() if 'デバッグ開始' in content else "New Debug Session"

        priority = 'normal'
        if '緊急' in content or 'critical' in content or '高' in content:
            priority = 'high'

        session_id = create_session(title, description=message.content, priority=priority)
        await message.reply(f"🐛 デバッグセッションを作成しました (ID: {session_id})\nタイトル: {title}")
        return

    # Show sessions
    if any(keyword in content for keyword in ['セッション一覧', 'デバッグセッション', 'sessions', 'list sessions']):
        status = None
        if 'active' in content or 'アクティブ' in content:
            status = 'active'
        elif 'completed' in content or '完了' in content:
            status = 'completed'

        sessions = list_sessions(status=status, limit=10)
        if sessions:
            response = "📋 **デバッグセッション**\n\n"
            for s in sessions:
                status_icon = {
                    'active': '🟢',
                    'paused': '⏸️',
                    'completed': '✅',
                    'abandoned': '🗑️'
                }.get(s['status'], '📝')

                priority_icon = {
                    'low': '🔵',
                    'normal': '⚪',
                    'high': '🟠',
                    'critical': '🔴'
                }.get(s['priority'], '⚪')

                created = s['created_at'][:10] if s['created_at'] else 'N/A'
                response += f"{status_icon} {priority_icon} **{s['title']}** (ID: {s['id']})\n"
                response += f"  ステータス: {s['status']} | 作成: {created}\n\n"
            await message.reply(response)
        else:
            await message.reply("📋 セッションがありません")
        return

    # Create issue
    if any(keyword in content for keyword in ['問題追加', 'バグ報告', 'create issue', '新規バグ']):
        # Extract session ID (use last session if not specified)
        sessions = list_sessions(status='active', limit=1)
        if not sessions:
            await message.reply("💡 先にアクティブなデバッグセッションを作成してください")
            return

        session_id = sessions[0]['id']

        # Extract issue details
        severity = 'major'
        if 'critical' in content or '致命' in content:
            severity = 'critical'
        elif 'minor' in content or '軽微' in content:
            severity = 'minor'

        title = message.content.split('問題追加')[1].split('バグ報告')[0].strip() if '問題追加' in content else "New Issue"

        issue_id = create_issue(session_id, title, description=message.content, severity=severity)
        await message.reply(f"🐛 問題を追加しました (ID: {issue_id})\nセッション: {session_id}")
        return

    # Show issues
    if any(keyword in content for keyword for keyword in ['問題一覧', 'バグ一覧', 'issues', 'list issues']):
        severity = None
        if 'critical' in content:
            severity = 'critical'
        elif 'major' in content or '重大' in content:
            severity = 'major'

        issues = get_issues(severity=severity, limit=10)
        if issues:
            response = "🐛 **問題リスト**\n\n"
            for i in issues:
                severity_icon = {
                    'info': 'ℹ️',
                    'minor': '🟢',
                    'major': '🟡',
                    'critical': '🔴'
                }.get(i['severity'], '📝')

                status_icon = {
                    'open': '📌',
                    'investigating': '🔍',
                    'resolved': '✅',
                    'closed': '🔒',
                    'reopened': '🔄'
                }.get(i['status'], '📝')

                response += f"{severity_icon} {status_icon} **{i['title']}** (ID: {i['id']})\n"
                response += f"  重大度: {i['severity']} | ステータス: {i['status']}\n\n"
            await message.reply(response)
        else:
            await message.reply("🐛 問題がありません")
        return

    # Update issue status
    if any(keyword in content for keyword in ['解決', 'resolved', '解決済み', 'クローズ']):
        # Try to extract issue ID from message
        import re
        numbers = re.findall(r'\d+', content)
        if numbers:
            issue_id = int(numbers[0])
            update_issue_status(issue_id, 'resolved')
            await message.reply(f"✅ 問題 {issue_id} を解決済みにしました")
        else:
            await message.reply("💡 問題IDを指定してください (例: 問題1を解決)")
        return

    # Add note
    if any(keyword in content for keyword in ['ノート', 'メモ', 'note', '覚書']):
        # Get active session
        sessions = list_sessions(status='active', limit=1)
        if not sessions:
            await message.reply("💡 先にアクティブなデバッグセッションを作成してください")
            return

        session_id = sessions[0]['id']

        # Extract note content
        note_content = message.content.replace('ノート', '').replace('メモ', '').replace('note', '').replace('覚書', '').strip()
        if note_content:
            add_note(session_id, note_content, author=str(message.author))
            await message.reply(f"📝 ノートを追加しました")
        else:
            await message.reply("💡 ノート内容を入力してください")
        return

    # Show notes
    if any(keyword in content for keyword in ['ノート表示', 'メモ表示', 'show notes']):
        sessions = list_sessions(status='active', limit=1)
        if sessions:
            notes = get_notes(session_id=sessions[0]['id'], limit=20)
            if notes:
                response = f"📝 **ノート (セッション {sessions[0]['id']})**\n\n"
                for n in notes[:10]:
                    ts = n['created_at'][:16] if n['created_at'] else 'N/A'
                    content = n['content'][:80] + '...' if len(n['content']) > 80 else n['content']
                    response += f"[{ts}] {content}\n\n"
                await message.reply(response)
            else:
                await message.reply("📋 ノートがありません")
        else:
            await message.reply("💡 アクティブなセッションがありません")
        return

    # Create solution
    if any(keyword in content for keyword in ['ソリューション', '解決策', 'solution', '修正方法']):
        # Try to get issue ID
        import re
        numbers = re.findall(r'\d+', content)
        issue_id = int(numbers[0]) if numbers else None

        if not issue_id:
            await message.reply("💡 問題IDを指定してください (例: 問題1の解決策: 修正方法...)")
            return

        description = message.content.replace('ソリューション', '').replace('解決策', '').replace('solution', '').replace('修正方法', '').strip()
        create_solution(None, issue_id, description)
        await message.reply(f"✅ 解決策を追加しました (問題ID: {issue_id})")
        return

    # Show solutions
    if any(keyword in content for keyword in ['解決策表示', 'ソリューション一覧', 'show solutions']):
        solutions = get_solutions(limit=20)
        if solutions:
            response = "✅ **解決策**\n\n"
            for s in solutions[:10]:
                verified_icon = '✅' if s['verified'] else '⏳'
                response += f"{verified_icon} 問題ID: {s['issue_id']}\n"
                desc = s['description'][:100] + '...' if len(s['description']) > 100 else s['description']
                response += f"  {desc}\n\n"
            await message.reply(response)
        else:
            await message.reply("📋 解決策がありません")
        return

    # Verify solution
    if any(keyword in content for keyword in ['検証', 'verify', '確認済み']):
        import re
        numbers = re.findall(r'\d+', content)
        if numbers:
            solution_id = int(numbers[0])
            verify_solution(solution_id)
            await message.reply(f"✅ 解決策 {solution_id} を検証済みにしました")
        else:
            await message.reply("💡 解決策IDを指定してください")
        return

    # Add resource
    if any(keyword in content for keyword in ['リソース追加', 'add resource', 'ファイル追加']):
        sessions = list_sessions(status='active', limit=1)
        if not sessions:
            await message.reply("💡 先にアクティブなデバッグセッションを作成してください")
            return

        session_id = sessions[0]['id']
        resource_type = 'other'
        if 'log' in content or 'ログ' in content:
            resource_type = 'log'
        elif 'screenshot' in content or 'スクリーンショット' in content:
            resource_type = 'screenshot'
        elif 'code' in content or 'コード' in content:
            resource_type = 'code'

        description = message.content.replace('リソース追加', '').replace('add resource', '').replace('ファイル追加', '').strip()
        add_resource(session_id, resource_type, description=description)
        await message.reply(f"📎 リソースを追加しました ({resource_type})")
        return

    # Show resources
    if any(keyword in content for keyword in ['リソース表示', 'show resources', 'ファイル一覧']):
        sessions = list_sessions(status='active', limit=1)
        if sessions:
            resources = get_resources(session_id=sessions[0]['id'], limit=20)
            if resources:
                response = f"📎 **リソース (セッション {sessions[0]['id']})**\n\n"
                for r in resources:
                    response += f"• {r['resource_type']}: {r['description'] or 'No description'}\n"
                    if r['file_path']:
                        response += f"  File: {r['file_path']}\n\n"
                await message.reply(response)
            else:
                await message.reply("📋 リソースがありません")
        else:
            await message.reply("💡 アクティブなセッションがありません")
        return

    # Help
    if any(keyword in content for keyword in ['ヘルプ', '使い方', 'help']):
        help_text = """
🐛 **Debug Agent - コマンド**

**セッション管理:**
• 「デバッグ開始」 - 新しいデバッグセッションを作成
• 「デバッグ開始 APIエラー調査」 - タイトル付きで作成
• 「セッション一覧」 - すべてのセッションを表示
• 「アクティブセッション」 - アクティブなセッションのみ表示

**問題管理:**
• 「問題追加」 - 新しい問題を追加
• 「バグ報告」 - バグを報告
• 「問題一覧」 - すべての問題を表示
• 「critical 問題一覧」 - 重大な問題のみ表示
• 「問題1を解決」 - 問題を解決済みにする

**ノート:**
• 「ノート テキスト」 - ノートを追加
• 「ノート表示」 - ノートを表示

**解決策:**
• 「ソリューション 修正内容...」 - 解決策を追加
• 「解決策表示」 - 解決策を表示
• 「検証 1」 - 解決策を検証済みにする

**リソース:**
• 「リソース追加 ログファイル」 - リソースを追加
• 「リソース表示」 - リソースを表示

**重大度:**
• info - 情報
• minor - 軽微
• major - 重大
• critical - 致命的
        """
        await message.reply(help_text)
        return

    await bot.process_commands(message)

if __name__ == '__main__':
    import os
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ DISCORD_TOKEN environment variable not set")
        exit(1)

    bot.run(token)
