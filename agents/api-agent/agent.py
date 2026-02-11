"""
API Agent - Discord Bot
API key management and request logging
"""
import discord
from discord.ext import commands
import aiohttp
import json
import re
from datetime import datetime
from typing import Dict, Optional
from db import APIDB

class APIAgent(commands.Cog):
    """API agent for managing API keys and logging requests"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = APIDB()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"API Agent ready as {self.bot.user}")

    @commands.command(name='api', help='Manage API keys | APIキーを管理')
    async def manage_api(self, ctx, action: str = None, *, args: str = None):
        """Main API management command"""
        if not action:
            embed = discord.Embed(
                title="API Agent / APIエージェント",
                description="Commands available / 利用可能なコマンド:\n"
                            "• `!api key add <name> <service> <key>` - Add API key / APIキー追加\n"
                            "• `api key list` - List API keys / APIキー一覧\n"
                            "• `api key update <id> <new_key>` - Update key / キー更新\n"
                            "• `api key remove <id>` - Remove key / キー削除\n"
                            "• `api send <key_id> <method> <endpoint>` - Send request / リクエスト送信\n"
                            "• `api requests [service]` - Show requests / リクエスト表示\n"
                            "• `api stats [service]` - Show statistics / 統計表示\n"
                            "• `api logs` - Show logs / ログ表示\n"
                            "• `api template add` - Add template / テンプレート追加",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
            return

        if action == 'key':
            if not args:
                await self._key_help(ctx)
                return
            parts = args.split(maxsplit=1)
            key_action = parts[0]
            key_args = parts[1] if len(parts) > 1 else None

            if key_action == 'add':
                await self._add_key(ctx, key_args)
            elif key_action == 'list':
                await self._list_keys(ctx)
            elif key_action == 'update':
                await self._update_key(ctx, key_args)
            elif key_action == 'remove':
                await self._remove_key(ctx, key_args)
            else:
                await self._key_help(ctx)

        elif action == 'send':
            await self._send_request(ctx, args)
        elif action == 'requests':
            await self._show_requests(ctx, args)
        elif action == 'stats':
            await self._show_stats(ctx, args)
        elif action == 'logs':
            await self._show_logs(ctx, args)
        elif action == 'template':
            await self._manage_templates(ctx, args)
        else:
            await ctx.send(f"Unknown action: {action}\nUse `!api` for help / `!api`でヘルプを表示")

    async def _key_help(self, ctx):
        """Show key subcommand help"""
        embed = discord.Embed(
            title="API Key Commands / APIキーコマンド",
            description="• `api key add <name> <service> <key> [base_url]`\n"
                       "• `api key list`\n"
                       "• `api key update <id> <new_key>`\n"
                       "• `api key remove <id>`",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

    async def _add_key(self, ctx, args: str):
        """Add a new API key"""
        if not args:
            await ctx.send("Usage: `!api key add <name> <service> <key> [base_url]`\n"
                         "Usage: `!api key add <name> <service> <key> [base_url]`")
            return

        parts = args.split(maxsplit=2)
        if len(parts) < 3:
            await ctx.send("Please provide name, service, and key.\n"
                         "名前、サービス、キーを指定してください。")
            return

        name = parts[0]
        service = parts[1]
        key_value = parts[2]

        # Check for optional base_url
        remaining = parts[2]
        if ' ' in remaining:
            key_parts = remaining.split(maxsplit=1)
            key_value = key_parts[0]
            base_url = key_parts[1]
        else:
            base_url = None

        key_id = self.db.add_api_key(name, service, key_value, base_url=base_url)

        embed = discord.Embed(
            title="✅ API Key Added / APIキー追加完了",
            description=f"Name: {name}\nService: {service}\nID: {key_id}",
            color=discord.Color.green()
        )

        if base_url:
            embed.add_field(name="Base URL", value=base_url, inline=False)

        await ctx.send(embed=embed)

    async def _list_keys(self, ctx):
        """List all API keys"""
        keys = self.db.get_api_keys()

        if not keys:
            await ctx.send("No API keys found. Use `!api key add` to add one.\n"
                         "APIキーがありません。`!api key add`で追加してください。")
            return

        embed = discord.Embed(
            title="🔑 API Keys / APIキー",
            description=f"Total: {len(keys)} keys",
            color=discord.Color.blue()
        )

        for key in keys:
            status = "✅ Active" if key['is_active'] else "⏸️ Inactive"
            masked_key = self._mask_key(key['name'])
            embed.add_field(
                name=f"#{key['id']} - {key['name']}",
                value=f"Service: {key['service']}\nStatus: {status}\nType: {key['key_type']}",
                inline=False
            )

        await ctx.send(embed=embed)

    def _mask_key(self, key: str, visible_chars: int = 4) -> str:
        """Mask API key for display"""
        if len(key) <= visible_chars:
            return '*' * len(key)
        return key[:visible_chars] + '*' * (len(key) - visible_chars)

    async def _update_key(self, ctx, args: str):
        """Update an API key"""
        if not args:
            await ctx.send("Usage: `!api key update <id> <new_key>`\n"
                         "Usage: `!api key update <id> <new_key>`")
            return

        parts = args.split(maxsplit=1)
        if len(parts) < 2:
            await ctx.send("Please provide key ID and new value.\n"
                         "キーIDと新しい値を指定してください。")
            return

        try:
            key_id = int(parts[0])
            new_key = parts[1]

            if self.db.update_api_key(key_id, key_value=new_key):
                await ctx.send("✅ API key updated.\nAPIキーを更新しました。")
            else:
                await ctx.send("❌ Failed to update API key.\nAPIキーの更新に失敗しました。")

        except ValueError:
            await ctx.send("❌ Invalid key ID.\n無効なキーIDです。")

    async def _remove_key(self, ctx, args: str):
        """Remove an API key"""
        if not args:
            await ctx.send("Usage: `!api key remove <id>`\nUsage: `!api key remove <id>`")
            return

        try:
            key_id = int(args)
            self.db.delete_api_key(key_id)
            await ctx.send("✅ API key removed.\nAPIキーを削除しました。")
        except ValueError:
            await ctx.send("❌ Invalid key ID.\n無効なキーIDです。")

    async def _send_request(self, ctx, args: str):
        """Send an API request"""
        if not args:
            await ctx.send("Usage: `!api send <key_id> <method> <endpoint>`\n"
                         "Usage: `!api send <key_id> <method> <endpoint>`")
            return

        parts = args.split(maxsplit=2)
        if len(parts) < 3:
            await ctx.send("Please provide key_id, method, and endpoint.\n"
                         "キーID、メソッド、エンドポイントを指定してください。")
            return

        try:
            key_id = int(parts[0])
            method = parts[1].upper()
            endpoint = parts[2]

            # Get API key
            api_key = self.db.get_api_key(key_id)
            if not api_key:
                await ctx.send("❌ API key not found.\nAPIキーが見つかりません。")
                return

            # Build full URL
            base_url = api_key['base_url'] or ''
            url = f"{base_url}{endpoint}" if base_url else endpoint

            # Prepare headers
            headers = {}
            key_type = api_key['key_type'].lower()
            if 'bearer' in key_type:
                headers['Authorization'] = f"Bearer {api_key['key_value']}"
            elif 'api' in key_type:
                headers['X-API-Key'] = api_key['key_value']
            else:
                headers['Authorization'] = api_key['key_value']

            # Send request
            start_time = datetime.now()
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.request(method, url, headers=headers) as response:
                        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
                        response_status = response.status
                        response_headers = dict(response.headers)

                        try:
                            response_body = await response.text()
                        except:
                            response_body = None

                        success = 200 <= response_status < 300

                        # Log request
                        self.db.log_request(
                            service=api_key['service'],
                            method=method,
                            endpoint=endpoint,
                            api_key_id=key_id,
                            request_headers=headers,
                            response_status=response_status,
                            response_headers=response_headers,
                            response_body=response_body,
                            duration_ms=duration_ms,
                            success=success
                        )

                        # Create response embed
                        color = discord.Color.green() if success else discord.Color.red()
                        embed = discord.Embed(
                            title=f"{method} {endpoint}",
                            description=f"Status: {response_status} | Duration: {duration_ms}ms",
                            color=color
                        )

                        embed.add_field(name="Service", value=api_key['service'], inline=True)
                        embed.add_field(name="Success", value="✅ Yes" if success else "❌ No", inline=True)

                        if response_body and len(response_body) <= 1000:
                            embed.add_field(name="Response", value=f"```json\n{response_body}\n```",
                                          inline=False)
                        elif response_body:
                            embed.add_field(name="Response", value=f"{response_body[:1000]}...",
                                          inline=False)

                        await ctx.send(embed=embed)

                except aiohttp.ClientError as e:
                    self.db.log_request(
                        service=api_key['service'],
                        method=method,
                        endpoint=endpoint,
                        api_key_id=key_id,
                        request_headers=headers,
                        response_status=None,
                        duration_ms=0,
                        success=False
                    )
                    await ctx.send(f"❌ Request failed: {str(e)}\nリクエスト失敗: {str(e)}")

        except ValueError:
            await ctx.send("❌ Invalid key ID.\n無効なキーIDです。")

    async def _show_requests(self, ctx, service: str = None):
        """Show recent API requests"""
        requests = self.db.get_requests(service=service, limit=20)

        if not requests:
            await ctx.send("No requests found.\nリクエストが見つかりません。")
            return

        service_name = service or "All Services / 全サービス"
        embed = discord.Embed(
            title=f"📡 API Requests / APIリクエスト - {service_name}",
            description=f"Showing {len(requests)} recent requests",
            color=discord.Color.blue()
        )

        for req in requests[:10]:
            status_emoji = "✅" if req['success'] else "❌"
            embed.add_field(
                name=f"{status_emoji} {req['method']} {req['endpoint']}",
                value=f"Service: {req['service']} | Status: {req['response_status'] or 'Failed'}\n"
                      f"Time: {req['timestamp']} | Duration: {req['duration_ms'] or 0}ms",
                inline=False
            )

        await ctx.send(embed=embed)

    async def _show_stats(self, ctx, service: str = None):
        """Show API statistics"""
        stats = self.db.get_request_stats(service=service)

        service_name = service or "All Services / 全サービス"

        embed = discord.Embed(
            title=f"📊 API Statistics / API統計 - {service_name}",
            color=discord.Color.blue()
        )

        total = stats.get('total_requests', 0)
        success = stats.get('success_count', 0)
        failure = stats.get('failure_count', 0)
        avg_duration = stats.get('avg_duration', 0)
        max_duration = stats.get('max_duration', 0)

        embed.add_field(name="Total Requests / 総リクエスト数", value=str(total), inline=True)
        embed.add_field(name="Success / 成功", value=str(success), inline=True)
        embed.add_field(name="Failure / 失敗", value=str(failure), inline=True)

        if total > 0:
            success_rate = (success / total) * 100
            embed.add_field(name="Success Rate / 成功率", value=f"{success_rate:.1f}%", inline=True)

        if avg_duration:
            embed.add_field(name="Avg Duration / 平均時間", value=f"{avg_duration:.1f}ms", inline=True)
        if max_duration:
            embed.add_field(name="Max Duration / 最大時間", value=f"{max_duration}ms", inline=True)

        await ctx.send(embed=embed)

    async def _show_logs(self, ctx, args: str = None):
        """Show API logs"""
        logs = self.db.get_logs(limit=30)

        if not logs:
            await ctx.send("No logs found.\nログが見つかりません。")
            return

        embed = discord.Embed(
            title="📋 API Logs / APIログ",
            description=f"Showing {len(logs)} recent logs",
            color=discord.Color.blue()
        )

        for log in logs[:10]:
            severity_emoji = {
                'info': 'ℹ️',
                'warning': '⚠️',
                'error': '❌',
                'debug': '🔍'
            }.get(log['severity'], '📌')

            embed.add_field(
                name=f"{severity_emoji} {log['log_type']} - {log['timestamp']}",
                value=log['message'][:200],
                inline=False
            )

        await ctx.send(embed=embed)

    async def _manage_templates(self, ctx, args: str = None):
        """Manage API request templates"""
        if not args:
            templates = self.db.get_templates()

            if not templates:
                await ctx.send("No templates found. Use `!api template add` to add one.\n"
                             "テンプレートがありません。`!api template add`で追加してください。")
                return

            embed = discord.Embed(
                title="📝 API Templates / APIテンプレート",
                description=f"Total: {len(templates)} templates",
                color=discord.Color.blue()
            )

            for template in templates:
                embed.add_field(
                    name=f"{template['name']} (ID: {template['id']})",
                    value=f"Service: {template['service']} | Method: {template['method']}\n"
                          f"Endpoint: {template['endpoint']}",
                    inline=False
                )

            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(APIAgent(bot))
