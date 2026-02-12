#!/usr/bin/env python3
"""
Log Agent - Discord Bot
System logs and monitoring management with natural language interface
"""

import discord
from discord.ext import commands
import json
from datetime import datetime, timedelta
from db import (
    init_db, add_log, get_logs, get_log_stats,
    create_source, get_sources, create_alert, get_alerts,
    get_alert_history, acknowledge_alert, export_logs_to_file, search_logs
)

# Database initialization
init_db()

# Discord Bot Configuration
INTENTS = discord.Intents.default()
INTENTS.message_content = True

bot = commands.Bot(command_prefix='!', intents=INTENTS)

@bot.event
async def on_ready():
    print(f'✅ Log Agent ready as {bot.user}')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.lower()

    # Add log
    if any(keyword in content for keyword in ['ログ記録', 'ログ追加', 'log', 'log entry']):
        # Try to extract log level and message
        level = 'INFO'
        log_message = message.content

        if 'error' in content or 'エラー' in content:
            level = 'ERROR'
        elif 'warning' in content or '警告' in content:
            level = 'WARNING'
        elif 'critical' in content or '致命' in content or '重大' in content:
            level = 'CRITICAL'
        elif 'debug' in content or 'デバッグ' in content:
            level = 'DEBUG'

        # Clean up message
        log_message = log_message.replace('ログ記録', '').replace('ログ追加', '').replace('log entry', '').strip()

        if log_message:
            add_log(level, log_message, source='discord', correlation_id=str(datetime.now().timestamp()))
            await message.reply(f"✅ ログを記録しました [{level}]: {log_message[:100]}")
        else:
            await message.reply("💡 ログメッセージを入力してください")
        return

    # Show recent logs
    if any(keyword in content for keyword in ['最新ログ', 'ログ表示', 'show logs', 'recent logs']):
        level = None
        if 'error' in content:
            level = 'ERROR'
        elif 'warning' in content:
            level = 'WARNING'

        logs = get_logs(level=level, limit=10)
        if logs:
            response = "📋 **最新ログ**\n\n"
            for log in logs[:10]:
                level_icon = {
                    'DEBUG': '🔍',
                    'INFO': 'ℹ️',
                    'WARNING': '⚠️',
                    'ERROR': '❌',
                    'CRITICAL': '🚨'
                }.get(log['level'], '📝')

                ts = log['timestamp'][:19] if log['timestamp'] else 'N/A'
                msg = log['message'][:60] + '...' if len(log['message']) > 60 else log['message']
                response += f"{level_icon} [{ts}] {log['level']}: {msg}\n"
            await message.reply(response)
        else:
            await message.reply("📋 ログがありません")
        return

    # Show log statistics
    if any(keyword in content for keyword in ['ログ統計', '統計', 'log stats', 'statistics']):
        stats = get_log_stats(days=7)
        if stats:
            total = sum(stats.values())
            response = f"📊 **ログ統計 (過去7日間)**\n\n"
            response += f"**合計**: {total} 件\n\n"

            level_icons = {
                'DEBUG': '🔍',
                'INFO': 'ℹ️',
                'WARNING': '⚠️',
                'ERROR': '❌',
                'CRITICAL': '🚨'
            }

            for level, count in sorted(stats.items()):
                icon = level_icons.get(level, '📝')
                percentage = (count / total * 100) if total > 0 else 0
                response += f"{icon} {level}: {count} 件 ({percentage:.1f}%)\n"

            await message.reply(response)
        else:
            await message.reply("📋 統計データがありません")
        return

    # Search logs
    if any(keyword in content for keyword in ['ログ検索', '検索', 'search log', 'search']):
        # Extract search query
        import re
        # Remove common phrases
        query = content.replace('ログ検索', '').replace('検索', '').replace('search log', '').replace('search', '').strip()

        if query:
            logs = search_logs(query, limit=10)
            if logs:
                response = f"🔍 **検索結果: \"{query}\"**\n\n"
                for log in logs[:10]:
                    ts = log['timestamp'][:19] if log['timestamp'] else 'N/A'
                    msg = log['message'][:60] + '...' if len(log['message']) > 60 else log['message']
                    response += f"[{ts}] {log['level']}: {msg}\n"
                await message.reply(response)
            else:
                await message.reply(f"🔍 \"{query}\" に一致するログが見つかりませんでした")
        else:
            await message.reply("💡 検索語句を入力してください (例: ログ検索 データベース)")
        return

    # Show alerts
    if any(keyword in content for keyword in ['アラート', 'alert', '警告']):
        alerts = get_alerts(active_only=True)
        if alerts:
            response = "🚨 **アクティブアラート**\n\n"
            for alert in alerts:
                last_triggered = alert['last_triggered'][:19] if alert['last_triggered'] else 'Never'
                response += f"• {alert['name']}\n"
                response += f"  Level: {alert['level']}\n"
                response += f"  最終トリガー: {last_triggered}\n"
                response += f"  回数: {alert['notification_count']}\n\n"
            await message.reply(response)
        else:
            await message.reply("✅ アクティブなアラートはありません")
        return

    # Show alert history
    if any(keyword in content for keyword in ['アラート履歴', 'alert history', '履歴']):
        history = get_alert_history(acknowledged=False, limit=10)
        if history:
            response = "📜 **未確認アラート履歴**\n\n"
            for h in history:
                triggered = h['triggered_at'][:19] if h['triggered_at'] else 'N/A'
                response += f"• ID: {h['id']}\n"
                response += f"  Time: {triggered}\n\n"
            await message.reply(response)
        else:
            await message.reply("✅ 未確認のアラートはありません")
        return

    # Create alert
    if any(keyword in content for keyword in ['アラート作成', 'create alert', '新規アラート']):
        alert_name = "Custom Alert"
        condition = "ERROR logs > 5 in 1 hour"
        create_alert(alert_name, condition, level='ERROR', threshold=5, time_window=60)
        await message.reply(f"✅ アラートを作成しました: `{alert_name}`")
        return

    # Show sources
    if any(keyword in content for keyword in ['ソース', 'sources', 'ログソース']):
        sources = get_sources(enabled_only=True)
        if sources:
            response = "📡 **ログソース**\n\n"
            for s in sources:
                last_log = s['last_log'][:19] if s['last_log'] else 'Never'
                response += f"• {s['name']} ({s['type']})\n"
                response += f"  最終ログ: {last_log}\n\n"
            await message.reply(response)
        else:
            await message.reply("📋 ログソースがありません")
        return

    # Export logs
    if any(keyword in content for keyword in ['ログエクスポート', 'export logs', 'ログ出力']):
        export_path = export_logs_to_file()
        await message.reply(f"✅ ログをエクスポートしました: `{export_path.name}`")
        return

    # Show help
    if any(keyword in content for keyword in ['ヘルプ', '使い方', 'help']):
        help_text = """
📋 **Log Agent - コマンド**

**自然言語で操作:**
• 「ログ記録」または「log entry」 - ログを追加
• 「error ログ記録」 - エラーレベルでログ追加
• 「warning ログ記録」 - 警告レベルでログ追加

• 「最新ログ」 - 最新のログを表示
• 「error ログ表示」 - エラーログのみ表示
• 「warning ログ表示」 - 警告ログのみ表示

• 「ログ統計」 - 過去7日間の統計を表示
• 「統計」 - 統計情報を表示

• 「ログ検索 キーワード」 - ログを検索
• 「検索 データベース」 - キーワードで検索

• 「アラート」 - アクティブなアラートを表示
• 「アラート履歴」 - 未確認アラート履歴を表示
• 「アラート作成」 - 新しいアラートを作成

• 「ソース」 - ログソースを表示
• 「ログエクスポート」 - ログをエクスポート

**ログレベル:**
• DEBUG - デバッグ情報
• INFO - 一般情報
• WARNING - 警告
• ERROR - エラー
• CRITICAL - 致命的エラー
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
