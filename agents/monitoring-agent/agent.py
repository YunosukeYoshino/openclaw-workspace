"""
Monitoring Agent - Discord Bot
System monitoring, error detection, and performance tracking
"""
import discord
from discord.ext import commands
import re
from datetime import datetime
from typing import Dict, List
from db import MonitoringDB

class MonitoringAgent(commands.Cog):
    """Monitoring agent for system health and performance"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = MonitoringDB()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Monitoring Agent ready as {self.bot.user}")

    @commands.command(name='monitor', help='Monitor system | システムを監視')
    async def monitor(self, ctx, action: str = None, *, args: str = None):
        """Monitoring commands"""
        if not action:
            embed = discord.Embed(
                title="Monitoring Agent / 監視エージェント",
                description="Commands available / 利用可能なコマンド:\n"
                            "• `!monitor metric <name> <value> [unit]` - Record metric / メトリックを記録\n"
                            "• `!monitor alerts` - View alerts / アラートを表示\n"
                            "• `!monitor resolve <alert_id>` - Resolve alert / アラートを解決\n"
                            "• `!monitor performance` - View performance / パフォーマンスを表示\n"
                            "• `!monitor threshold <name> <warning> <critical>` - Set threshold / 閾値を設定",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return

        if action == 'metric':
            if not args:
                await ctx.send("Usage: `!monitor metric <name> <value> [unit]`\n"
                             "使い方: `!monitor metric <名前> <値> [単位]`")
                return

            parts = args.split()
            if len(parts) < 2:
                await ctx.send("❌ Metric name and value are required.\nメトリック名と値が必要です。")
                return

            metric_name = parts[0]
            try:
                value = float(parts[1])
                unit = parts[2] if len(parts) > 2 else None
            except ValueError:
                await ctx.send("❌ Value must be a number.\n値は数値である必要があります。")
                return

            metric_id = self.db.record_metric(metric_name, value, unit)
            await ctx.send(f"✅ Metric recorded: {metric_name} = {value} {unit or ''} (ID: {metric_id})")

        elif action == 'alerts':
            alerts = self.db.get_alerts()

            if alerts:
                embed = discord.Embed(
                    title="System Alerts / システムアラート",
                    description=f"Total alerts: {len(alerts)}",
                    color=discord.Color.red()
                )

                for alert in alerts[:10]:
                    status_emoji = "🔴" if not alert['resolved'] else "✅"
                    severity_color = {
                        'info': '🔵',
                        'warning': '🟡',
                        'error': '🟠',
                        'critical': '🔴'
                    }.get(alert['severity'], '⚪')

                    embed.add_field(
                        name=f"{status_emoji} {severity_color} {alert['alert_type']} (ID: {alert['id']})",
                        value=f"{alert['message']}\n{alert['created_at']}",
                        inline=False
                    )

                await ctx.send(embed=embed)
            else:
                await ctx.send("✅ No active alerts.\nアクティブなアラートはありません。")

        elif action == 'resolve':
            if not args or not args.isdigit():
                await ctx.send("Usage: `!monitor resolve <alert_id>`\n"
                             "使い方: `!monitor resolve <アラートID>`")
                return

            alert_id = int(args)
            success = self.db.resolve_alert(alert_id)

            if success:
                await ctx.send(f"✅ Alert {alert_id} resolved.\nアラート {alert_id} が解決されました。")
            else:
                await ctx.send(f"❌ Alert {alert_id} not found.\nアラート {alert_id} が見つかりません。")

        elif action == 'performance':
            logs = self.db.get_performance_logs(limit=20)

            if logs:
                embed = discord.Embed(
                    title="Performance Logs / パフォーマンスログ",
                    description=f"Total logs: {len(logs)}",
                    color=discord.Color.blue()
                )

                for log in logs[:10]:
                    status = "✅" if log['success'] else "❌"
                    response_time = f"{log['response_time']:.2f}ms" if log['response_time'] else "N/A"
                    embed.add_field(
                        name=f"{status} {log['service_name']}",
                        value=f"Response: {response_time} | Status: {log['status_code'] or 'N/A'}",
                        inline=False
                    )

                await ctx.send(embed=embed)
            else:
                await ctx.send("No performance logs found.\nパフォーマンスログが見つかりません。")

        elif action == 'threshold':
            if not args:
                await ctx.send("Usage: `!monitor threshold <metric_name> <warning> <critical>`\n"
                             "使い方: `!monitor threshold <メトリック名> <警告値> <重大値>`")
                return

            parts = args.split()
            if len(parts) < 3:
                await ctx.send("❌ Metric name, warning, and critical values are required.\n"
                             "メトリック名、警告値、重大値が必要です。")
                return

            metric_name = parts[0]
            try:
                warning = float(parts[1])
                critical = float(parts[2])
            except ValueError:
                await ctx.send("❌ Threshold values must be numbers.\n閾値は数値である必要があります。")
                return

            threshold_id = self.db.set_threshold(metric_name, warning, critical)
            await ctx.send(f"✅ Threshold set: {metric_name} (Warning: {warning}, Critical: {critical})")

        else:
            await ctx.send("Unknown action. Use `!monitor` to see available commands.\n"
                         "不明なアクションです。`!monitor`でコマンドを確認してください。")

    @commands.command(name='check', help='Check system status | システム状態をチェック')
    async def check_status(self, ctx):
        """Check current system status"""
        metrics = self.db.get_metrics(limit=50)
        alerts = self.db.get_alerts(resolved=False)
        performance = self.db.get_performance_logs(limit=10)

        # Calculate summary
        active_alerts = len(alerts)
        avg_response = None
        if performance and any(p['response_time'] for p in performance):
            response_times = [p['response_time'] for p in performance if p['response_time']]
            avg_response = sum(response_times) / len(response_times)

        embed = discord.Embed(
            title="System Status / システム状態",
            timestamp=datetime.utcnow(),
            color=discord.Color.green() if active_alerts == 0 else discord.Color.orange()
        )

        embed.add_field(
            name="Active Alerts / アクティブなアラート",
            value=f"{active_alerts}",
            inline=True
        )

        embed.add_field(
            name="Metrics Recorded / 記録されたメトリック",
            value=f"{len(metrics)}",
            inline=True
        )

        embed.add_field(
            name="Avg Response Time / 平均応答時間",
            value=f"{avg_response:.2f}ms" if avg_response else "N/A",
            inline=True
        )

        # Recent metrics
        if metrics:
            recent_metrics = metrics[:5]
            metrics_text = "\n".join([
                f"• {m['metric_name']}: {m['value']} {m['unit'] or ''}"
                for m in recent_metrics
            ])
            embed.add_field(
                name="Recent Metrics / 最近のメトリック",
                value=metrics_text,
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name='alert', help='Create manual alert | 手動でアラート作成')
    async def create_alert(self, ctx, severity: str, alert_type: str, *, message: str):
        """Create a manual alert"""
        valid_severities = ['info', 'warning', 'error', 'critical']

        if severity not in valid_severities:
            await ctx.send(f"❌ Invalid severity. Use: {', '.join(valid_severities)}\n"
                         f"無効な重大度です。次を使用: {', '.join(valid_severities)}")
            return

        alert_id = self.db.create_alert(alert_type, severity, message, source="manual")

        severity_colors = {
            'info': discord.Color.blue(),
            'warning': discord.Color.yellow(),
            'error': discord.Color.orange(),
            'critical': discord.Color.red()
        }

        embed = discord.Embed(
            title=f"Alert Created: {alert_type} / アラート作成: {alert_type}",
            description=message,
            color=severity_colors.get(severity, discord.Color.greyple())
        )
        embed.add_field(name="Alert ID", value=str(alert_id), inline=True)
        embed.add_field(name="Severity", value=severity.upper(), inline=True)

        await ctx.send(embed=embed)

def setup(bot: commands.Bot):
    """Setup function for discord.py"""
    bot.add_cog(MonitoringAgent(bot))
