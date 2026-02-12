#!/usr/bin/env python3
"""
Report Agent - Discord Bot
Reports, analytics, and exports management with natural language interface
"""

import discord
from discord.ext import commands
import json
from pathlib import Path
from db import (
    init_db, create_report, get_report, list_reports,
    add_analytics, get_analytics, create_template, get_template,
    export_report, get_exports
)

# Database initialization
init_db()

# Discord Bot Configuration
INTENTS = discord.Intents.default()
INTENTS.message_content = True

bot = commands.Bot(command_prefix='!', intents=INTENTS)

def format_analytics_table(analytics):
    """Format analytics data as table"""
    if not analytics:
        return "No analytics data available"

    lines = ["```\n"]
    lines.append(f"{'Timestamp':<20} | {'Metric':<20} | {'Value':<12} | {'Unit':<10}")
    lines.append("-" * 70)

    for a in analytics:
        ts = a['timestamp'][:19] if a['timestamp'] else 'N/A'
        metric = a['metric_name'][:18] if a['metric_name'] else 'N/A'
        value = f"{a['metric_value']:.2f}" if a['metric_value'] else 'N/A'
        unit = a['metric_unit'][:8] if a['metric_unit'] else 'N/A'
        lines.append(f"{ts:<20} | {metric:<20} | {value:<12} | {unit:<10}")

    lines.append("```")
    return "\n".join(lines)

@bot.event
async def on_ready():
    print(f'✅ Report Agent ready as {bot.user}')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Natural language processing for report requests
    content = message.content.lower()

    # Report creation
    if any(keyword in content for keyword in ['レポート作成', '作成レポート', '新しいレポート', 'create report']):
        # Extract title
        title = None
        report_type = 'summary'

        if '分析' in content or 'analytics' in content:
            title = "Analytics Report"
            report_type = 'analytics'
        elif 'トレンド' in content or 'trend' in content:
            title = "Trend Report"
            report_type = 'trend'
        elif '比較' in content or 'comparison' in content:
            title = "Comparison Report"
            report_type = 'comparison'
        else:
            title = "Summary Report"

        report_id = create_report(title, report_type, description=message.content)
        await message.reply(f"✅ レポートを作成しました (ID: {report_id})\nタイトル: {title}\nタイプ: {report_type}")
        return

    # Add analytics data
    if any(keyword in content for keyword in ['データ追加', 'アナリティクス', '記録', 'log data', 'add metric']):
        try:
            # Try to extract metric value from message
            import re
            numbers = re.findall(r'[-+]?\d*\.\d+|\d+', message.content)
            if numbers:
                value = float(numbers[0])
                # Find metric name (assume it's before the number)
                parts = message.content.split(str(numbers[0]))[0].strip()
                metric_name = parts.split()[-1] if parts else "custom_metric"
                add_analytics(1, metric_name, value)
                await message.reply(f"✅ アナリティクスを追加しました: {metric_name} = {value}")
            else:
                await message.reply("💡 データを追加するには、メトリクス名と値を指定してください (例: sales 12345)")
        except Exception as e:
            await message.reply(f"❌ エラー: {str(e)}")
        return

    # Show report
    if any(keyword in content for keyword in ['レポート表示', 'レポートを見て', 'show report', 'display report']):
        reports = list_reports(status='ready', limit=5)
        if reports:
            response = "📊 **最新レポート**\n\n"
            for r in reports:
                response += f"ID: {r['id']} | {r['title']} ({r['report_type']})\n"
                response += f"  作成: {r['created_at'][:19]}\n\n"
            await message.reply(response)
        else:
            await message.reply("📋 利用可能なレポートがありません")
        return

    # Show analytics
    if any(keyword in content for keyword in ['アナリティクス', '分析', 'analytics', 'show analytics']):
        reports = list_reports(status='ready', limit=1)
        if reports:
            analytics = get_analytics(reports[0]['id'])
            if analytics:
                table = format_analytics_table(analytics[:20])  # Limit to 20 entries
                await message.reply(f"📈 **{reports[0]['title']} - アナリティクス**\n{table}")
            else:
                await message.reply("📋 このレポートにはアナリティクスデータがありません")
        else:
            await message.reply("📋 アナリティクスを表示するレポートがありません")
        return

    # Export report
    if any(keyword in content for keyword in ['エクスポート', 'export', 'csv', 'json']):
        reports = list_reports(status='ready', limit=1)
        if reports:
            format_type = 'csv' if 'csv' in content else 'json'
            file_path = export_report(reports[0]['id'], format_type)
            if file_path:
                await message.reply(f"✅ レポートをエクスポートしました: `{Path(file_path).name}`")
            else:
                await message.reply("❌ エクスポートに失敗しました")
        else:
            await message.reply("📋 エクスポートするレポートがありません")
        return

    # List exports
    if any(keyword in content for keyword in ['エクスポート履歴', 'export history', 'エクスポート一覧']):
        exports = get_exports()[:10]
        if exports:
            response = "📁 **エクスポート履歴**\n\n"
            for e in exports:
                status_icon = "✅" if e['status'] == 'completed' else "❌"
                response += f"{status_icon} {e['format']} | {e['created_at'][:19]}\n"
                if e['file_path']:
                    response += f"   File: {Path(e['file_path']).name}\n\n"
            await message.reply(response)
        else:
            await message.reply("📋 エクスポート履歴がありません")
        return

    # Create template
    if any(keyword in content for keyword in ['テンプレート作成', 'テンプレート', 'template']):
        template_name = "default_template"
        config = {"metrics": ["sales", "users", "revenue"], "timeframe": "7d"}
        create_template(template_name, 'analytics', config, "Default analytics template")
        await message.reply(f"✅ テンプレートを作成しました: `{template_name}`")
        return

    # Show help
    if any(keyword in content for keyword in ['ヘルプ', '使い方', 'help']):
        help_text = """
📊 **Report Agent - コマンド**

**自然言語で操作:**
• 「レポート作成」 - 新しいレポートを作成
• 「分析レポート作成」 - 分析レポートを作成
• 「データ追加 sales 12345」 - アナリティクスデータを追加
• 「レポート表示」 - 最新レポートを表示
• 「アナリティクス」 - アナリティクスデータを表示
• 「csvエクスポート」 - レポートをCSVでエクスポート
• 「jsonエクスポート」 - レポートをJSONでエクスポート
• 「エクスポート履歴」 - エクスポート履歴を表示
• 「テンプレート作成」 - テンプレートを作成

**タイプ:**
• summary - サマリー
• analytics - 分析
• trend - トレンド
• comparison - 比較
• custom - カスタム
        """
        await message.reply(help_text)
        return

    await bot.process_commands(message)

if __name__ == '__main__':
    # Load token from environment variable
    import os
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ DISCORD_TOKEN environment variable not set")
        exit(1)

    bot.run(token)
