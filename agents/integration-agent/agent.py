"""
Integration Agent - Discord Bot
Multi-service integration, data synchronization, and API connections
"""
import discord
from discord.ext import commands
import json
from typing import Dict, List
from db import IntegrationDB

class IntegrationAgent(commands.Cog):
    """Integration agent for connecting multiple services"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = IntegrationDB()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Integration Agent ready as {self.bot.user}")

    @commands.command(name='service', help='Manage services | サービスを管理')
    async def manage_services(self, ctx, action: str = None, *, args: str = None):
        """Service management commands"""
        if not action:
            embed = discord.Embed(
                title="Integration Agent / 統合エージェント",
                description="Commands available / 利用可能なコマンド:\n"
                            "• `!service add <name> <type> [base_url]` - Add service / サービス追加\n"
                            "• `!service list` - List services / サービス一覧\n"
                            "• `!service info <name>` - Service details / サービス詳細\n"
                            "• `!service logs <name>` - API logs / APIログ\n\n"
                            "• `!sync create <source> <target> <type>` - Create sync / 同期作成\n"
                            "• `!sync status` - Sync status / 同期状態\n"
                            "• `!webhook add <name> <url>` - Add webhook / Webhook追加\n"
                            "• `!webhook list` - List webhooks / Webhook一覧",
                color=discord.Color.blurple()
            )
            await ctx.send(embed=embed)
            return

        if action == 'add':
            if not args:
                await ctx.send("Usage: `!service add <name> <type> [base_url]`\n"
                             "使い方: `!service add <名前> <タイプ> [URL]`")
                return

            parts = args.split(maxsplit=2)
            if len(parts) < 2:
                await ctx.send("❌ Service name and type are required.\n"
                             "サービス名とタイプが必要です。")
                return

            name = parts[0]
            service_type = parts[1]
            base_url = parts[2] if len(parts) > 2 else None

            try:
                service_id = self.db.add_service(name, service_type, base_url)
                await ctx.send(f"✅ Service added: {name} (ID: {service_id})\n"
                             f"Type: {service_type}")
            except ValueError as e:
                await ctx.send(f"❌ {str(e)}")

        elif action == 'list':
            services = self.db.get_services(enabled_only=True)

            if services:
                embed = discord.Embed(
                    title="Configured Services / 設定済みサービス",
                    description=f"Total: {len(services)} services",
                    color=discord.Color.blurple()
                )

                for service in services:
                    status = "✅" if service['enabled'] else "❌"
                    embed.add_field(
                        name=f"{status} {service['name']}",
                        value=f"Type: {service['service_type']} | URL: {service['base_url'] or 'N/A'}",
                        inline=False
                    )

                await ctx.send(embed=embed)
            else:
                await ctx.send("No services configured. Use `!service add` to add one.\n"
                             "設定されたサービスがありません。`!service add`で追加してください。")

        elif action == 'info':
            if not args:
                await ctx.send("Usage: `!service info <name>`\n"
                             "使い方: `!service info <名前>`")
                return

            service = self.db.get_service(args)

            if service:
                config = json.loads(service['config_json']) if service['config_json'] else {}

                embed = discord.Embed(
                    title=f"Service: {service['name']}",
                    color=discord.Color.blurple()
                )

                embed.add_field(name="Service ID", value=str(service['id']), inline=True)
                embed.add_field(name="Type", value=service['service_type'], inline=True)
                embed.add_field(name="Status", value="Enabled" if service['enabled'] else "Disabled", inline=True)
                embed.add_field(name="Base URL", value=service['base_url'] or "N/A", inline=False)
                embed.add_field(name="API Key", value="Set" if service['api_key'] else "Not set", inline=True)
                embed.add_field(name="Created", value=service['created_at'], inline=True)

                if config:
                    embed.add_field(name="Configuration", value=f"```json\n{json.dumps(config, indent=2)[:500]}```", inline=False)

                await ctx.send(embed=embed)
            else:
                await ctx.send(f"❌ Service '{args}' not found.\nサービス '{args}' が見つかりません。")

        elif action == 'logs':
            if not args:
                await ctx.send("Usage: `!service logs <name>`\n"
                             "使い方: `!service logs <名前>`")
                return

            service = self.db.get_service(args)
            if not service:
                await ctx.send(f"❌ Service '{args}' not found.\nサービス '{args}' が見つかりません。")
                return

            logs = self.db.get_api_logs(service_id=service['id'], limit=10)

            if logs:
                embed = discord.Embed(
                    title=f"API Logs for {service['name']}",
                    description=f"Total: {len(logs)} calls",
                    color=discord.Color.blue()
                )

                for log in logs:
                    status_emoji = "✅" if 200 <= (log['response_status'] or 0) < 300 else "❌"
                    response_time = f"{log['response_time']:.0f}ms" if log['response_time'] else "N/A"

                    embed.add_field(
                        name=f"{status_emoji} {log['method']} {log['endpoint']}",
                        value=f"Status: {log['response_status']} | Time: {response_time} | {log['timestamp']}",
                        inline=False
                    )

                await ctx.send(embed=embed)
            else:
                await ctx.send("No API logs found.\nAPIログが見つかりません。")

        else:
            await ctx.send("Unknown action. Use `!service` to see available commands.\n"
                         "不明なアクションです。`!service`でコマンドを確認してください。")

    @commands.command(name='sync', help='Manage data sync | データ同期を管理')
    async def manage_syncs(self, ctx, action: str = None, *, args: str = None):
        """Data synchronization commands"""
        if not action:
            await ctx.send("Usage: `!sync <create|status>`\n"
                         "使い方: `!sync <create|status>`")
            return

        if action == 'create':
            if not args:
                await ctx.send("Usage: `!sync create <source> <target> <type>`\n"
                             "使い方: `!sync create <ソース> <ターゲット> <タイプ>`")
                return

            parts = args.split()
            if len(parts) < 3:
                await ctx.send("❌ Source, target, and type are required.\n"
                             "ソース、ターゲット、タイプが必要です。")
                return

            source = parts[0]
            target = parts[1]
            sync_type = parts[2]

            sync_id = self.db.create_sync(source, target, sync_type)

            embed = discord.Embed(
                title="Sync Created / 同期作成完了",
                color=discord.Color.green()
            )
            embed.add_field(name="Sync ID", value=str(sync_id), inline=True)
            embed.add_field(name="Source", value=source, inline=True)
            embed.add_field(name="Target", value=target, inline=True)
            embed.add_field(name="Type", value=sync_type, inline=True)

            await ctx.send(embed=embed)

        elif action == 'status':
            syncs = self.db.get_syncs()

            if syncs:
                embed = discord.Embed(
                    title="Data Sync Status / データ同期状態",
                    description=f"Total syncs: {len(syncs)}",
                    color=discord.Color.blue()
                )

                for sync in syncs[:10]:
                    status_emoji = {
                        'pending': '⏳',
                        'running': '🔄',
                        'completed': '✅',
                        'failed': '❌'
                    }.get(sync['status'], '❓')

                    embed.add_field(
                        name=f"{status_emoji} Sync {sync['id']}",
                        value=f"{sync['source_service']} → {sync['target_service']}\n"
                              f"Type: {sync['sync_type']} | Status: {sync['status']}\n"
                              f"Processed: {sync['records_processed']} | Failed: {sync['records_failed']}",
                        inline=False
                    )

                await ctx.send(embed=embed)
            else:
                await ctx.send("No sync tasks found. Use `!sync create` to create one.\n"
                             "同期タスクがありません。`!sync create`で作成してください。")

    @commands.command(name='webhook', help='Manage webhooks | Webhookを管理')
    async def manage_webhooks(self, ctx, action: str = None, *, args: str = None):
        """Webhook management commands"""
        if not action:
            await ctx.send("Usage: `!webhook <add|list|toggle>`\n"
                         "使い方: `!webhook <add|list|toggle>`")
            return

        if action == 'add':
            if not args:
                await ctx.send("Usage: `!webhook add <name> <url>`\n"
                             "使い方: `!webhook add <名前> <URL>`")
                return

            parts = args.split(maxsplit=1)
            if len(parts) < 2:
                await ctx.send("❌ Webhook name and URL are required.\n"
                             "Webhook名とURLが必要です。")
                return

            name = parts[0]
            url = parts[1]

            webhook_id = self.db.add_webhook(name, url)

            embed = discord.Embed(
                title="Webhook Added / Webhook追加完了",
                color=discord.Color.green()
            )
            embed.add_field(name="Webhook ID", value=str(webhook_id), inline=True)
            embed.add_field(name="Name", value=name, inline=True)
            embed.add_field(name="URL", value=url[:50], inline=False)

            await ctx.send(embed=embed)

        elif action == 'list':
            webhooks = self.db.get_webhooks(active_only=True)

            if webhooks:
                embed = discord.Embed(
                    title="Active Webhooks / アクティブなWebhook",
                    description=f"Total: {len(webhooks)} webhooks",
                    color=discord.Color.purple()
                )

                for webhook in webhooks:
                    status = "✅ Active" if webhook['active'] else "❌ Inactive"
                    embed.add_field(
                        name=f"{webhook['name']} (ID: {webhook['id']})",
                        value=f"{status}\nURL: {webhook['url'][:50]}...",
                        inline=False
                    )

                await ctx.send(embed=embed)
            else:
                await ctx.send("No webhooks configured. Use `!webhook add` to add one.\n"
                             "Webhookが設定されていません。`!webhook add`で追加してください。")

        elif action == 'toggle':
            if not args:
                await ctx.send("Usage: `!webhook toggle <webhook_id> <true|false>`\n"
                             "使い方: `!webhook toggle <webhook_id> <true|false>`")
                return

            parts = args.split()
            if len(parts) < 2:
                await ctx.send("❌ Webhook ID and state are required.\n"
                             "Webhook IDと状態が必要です。")
                return

            try:
                webhook_id = int(parts[0])
                active = parts[1].lower() in ['true', 'yes', '1', 'on']

                success = self.db.toggle_webhook(webhook_id, active)

                if success:
                    await ctx.send(f"✅ Webhook {webhook_id} {'enabled' if active else 'disabled'}.\n"
                                 f"Webhook {webhook_id} を{'有効' if active else '無効'}にしました。")
                else:
                    await ctx.send(f"❌ Webhook {webhook_id} not found.\n"
                                 f"Webhook {webhook_id} が見つかりません。")
            except ValueError:
                await ctx.send("❌ Invalid webhook ID.\nWebhook IDが正しくありません。")

def setup(bot: commands.Bot):
    """Setup function for discord.py"""
    bot.add_cog(IntegrationAgent(bot))
