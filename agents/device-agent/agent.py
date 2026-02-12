#!/usr/bin/env python3
"""
Device Agent - Discord Bot
Natural language interface for device management
"""

import discord
from discord.ext import commands
from datetime import datetime
import json
from pathlib import Path
import re
from typing import Optional

from db import DeviceDatabase


class DeviceAgent(commands.Bot):
    """Discord bot for device management with natural language understanding"""

    def __init__(self, command_prefix='!', db_path='devices.db'):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=command_prefix, intents=intents)

        self.db = DeviceDatabase(db_path)
        self.device_types = ['laptop', 'desktop', 'phone', 'tablet', 'server',
                            'printer', 'router', 'switch', 'camera', 'sensor',
                            'other']

    async def on_ready(self):
        """Called when bot is ready"""
        print(f'{self.user} has connected to Device Agent!')

    async def on_message(self, message):
        """Handle incoming messages with natural language processing"""
        if message.author == self.user:
            return

        content = message.content.lower()

        # Natural language commands
        if content.startswith('add device') or content.startswith('登録'):
            await self._handle_add_device(message)
        elif content.startswith('list devices') or content.startswith('デバイス一覧'):
            await self._handle_list_devices(message)
        elif 'device' in content and ('info' in content or '情報' in content):
            await self._handle_device_info(message)
        elif content.startswith('search') or '検索' in content:
            await self._handle_search_devices(message)
        elif 'warranty' in content or '保証' in content:
            await self._handle_warranty_check(message)
        elif 'issue' in content or '問題' in content or '故障' in content:
            await self._handle_device_issue(message)
        elif 'maintenance' in content or 'メンテナンス' in content or '修理' in content:
            await self._handle_maintenance(message)
        elif 'assign' in content or '貸出' in content:
            await self._handle_assignment(message)
        elif 'statistics' in content or '統計' in content:
            await self._handle_statistics(message)
        elif 'help' in content or 'ヘルプ' in content or '使い方' in content:
            await self._handle_help(message)
        else:
            await super().on_message(message)

    async def _handle_add_device(self, message):
        """Handle adding a new device"""
        content = message.content
        parts = content.replace('add device', '').replace('登録', '').strip().split(',')

        device_info = {
            'name': parts[0].strip() if len(parts) > 0 else 'Unknown',
            'type': parts[1].strip() if len(parts) > 1 else 'other',
            'model': parts[2].strip() if len(parts) > 2 else None,
            'serial_number': parts[3].strip() if len(parts) > 3 else None,
            'location': parts[4].strip() if len(parts) > 4 else None,
            'owner': parts[5].strip() if len(parts) > 5 else None,
        }

        try:
            device_id = self.db.add_device(**device_info)
            embed = discord.Embed(
                title="✅ デバイスを登録しました / Device Added",
                color=discord.Color.green()
            )
            embed.add_field(name="ID", value=device_id, inline=True)
            embed.add_field(name="名前 / Name", value=device_info['name'], inline=True)
            embed.add_field(name="タイプ / Type", value=device_info['type'], inline=True)
            if device_info.get('model'):
                embed.add_field(name="モデル / Model", value=device_info['model'], inline=True)
            if device_info.get('serial_number'):
                embed.add_field(name="シリアル / Serial", value=device_info['serial_number'], inline=True)
            await message.channel.send(embed=embed)
        except Exception as e:
            await message.channel.send(f"❌ エラー: {str(e)}")

    async def _handle_list_devices(self, message):
        """Handle listing devices"""
        content = message.content.lower()

        # Parse filters
        status = None
        device_type = None

        if 'active' in content or '稼働中' in content:
            status = 'active'
        elif 'inactive' in content or '非稼働' in content:
            status = 'inactive'

        for dtype in self.device_types:
            if dtype in content:
                device_type = dtype
                break

        devices = self.db.list_devices(status=status, type=device_type)

        if not devices:
            await message.channel.send("📭 デバイスが見つかりませんでした / No devices found")
            return

        embed = discord.Embed(
            title=f"📱 デバイス一覧 / Device List ({len(devices)})",
            color=discord.Color.blue()
        )

        for device in devices[:10]:  # Show first 10
            status_emoji = "🟢" if device['status'] == 'active' else "🔴"
            value = f"{status_emoji} {device['name']} ({device['type']})"
            if device.get('location'):
                value += f" - {device['location']}"
            embed.add_field(name=f"ID: {device['id']}", value=value, inline=False)

        if len(devices) > 10:
            embed.set_footer(text=f"+ {len(devices) - 10} more devices")

        await message.channel.send(embed=embed)

    async def _handle_device_info(self, message):
        """Handle getting device information"""
        # Extract device ID from message
        match = re.search(r'\d+', message.content)
        if not match:
            await message.channel.send("❌ デバイスIDを指定してください / Please specify device ID")
            return

        device_id = int(match.group())
        device = self.db.get_device(device_id)

        if not device:
            await message.channel.send(f"❌ デバイスID {device_id} が見つかりません / Device not found")
            return

        status_emoji = "🟢" if device['status'] == 'active' else "🔴"

        embed = discord.Embed(
            title=f"📱 {device['name']} - デバイス情報 / Device Info",
            color=discord.Color.blue()
        )
        embed.add_field(name="ID", value=device['id'], inline=True)
        embed.add_field(name="タイプ / Type", value=device['type'], inline=True)
        embed.add_field(name="ステータス / Status", value=f"{status_emoji} {device['status']}", inline=True)

        if device.get('model'):
            embed.add_field(name="モデル / Model", value=device['model'], inline=True)
        if device.get('serial_number'):
            embed.add_field(name="シリアル番号 / Serial", value=device['serial_number'], inline=True)
        if device.get('location'):
            embed.add_field(name="場所 / Location", value=device['location'], inline=True)
        if device.get('ip_address'):
            embed.add_field(name="IPアドレス", value=device['ip_address'], inline=True)
        if device.get('owner'):
            embed.add_field(name="所有者 / Owner", value=device['owner'], inline=True)
        if device.get('purchase_date'):
            embed.add_field(name="購入日 / Purchase Date", value=device['purchase_date'], inline=True)
        if device.get('warranty_expiry'):
            embed.add_field(name="保証期限 / Warranty", value=device['warranty_expiry'], inline=True)

        if device.get('notes'):
            embed.add_field(name="メモ / Notes", value=device['notes'][:500], inline=False)

        # Get recent issues
        issues = self.db.get_device_issues(device_id, status='open')
        if issues:
            issue_list = "\n".join([f"• {i['issue_type']}: {i['description'][:50]}" for i in issues[:3]])
            embed.add_field(name="⚠️ オープン中の問題 / Open Issues", value=issue_list, inline=False)

        # Get maintenance history
        maintenance = self.db.get_maintenance_history(device_id)
        if maintenance:
            maint_list = "\n".join([f"• {m['performed_date']}: {m['maintenance_type']}" for m in maintenance[:3]])
            embed.add_field(name="🔧 修理履歴 / Maintenance", value=maint_list, inline=False)

        await message.channel.send(embed=embed)

    async def _handle_search_devices(self, message):
        """Handle searching devices"""
        content = message.content
        search_term = content.replace('search', '').replace('検索', '').strip()

        if not search_term:
            await message.channel.send("❌ 検索語を入力してください / Please enter search term")
            return

        devices = self.db.search_devices(search_term)

        if not devices:
            await message.channel.send(f"📭 '{search_term}' に一致するデバイスが見つかりません / No devices found")
            return

        embed = discord.Embed(
            title=f"🔍 検索結果 / Search Results: '{search_term}'",
            color=discord.Color.blue()
        )

        for device in devices:
            status_emoji = "🟢" if device['status'] == 'active' else "🔴"
            value = f"{status_emoji} {device['name']} ({device['type']})"
            if device.get('model'):
                value += f" - {device['model']}"
            embed.add_field(name=f"ID: {device['id']}", value=value, inline=False)

        await message.channel.send(embed=embed)

    async def _handle_warranty_check(self, message):
        """Handle warranty expiration check"""
        devices = self.db.get_expiring_warranties(days=30)

        if not devices:
            await message.channel.send("✅ 30日以内に期限切れとなる保証はありません / No warranties expiring in 30 days")
            return

        embed = discord.Embed(
            title="⏰ 保証期限切れ間近 / Expiring Warranties",
            color=discord.Color.orange()
        )

        for device in devices:
            embed.add_field(
                name=f"{device['name']} (ID: {device['id']})",
                value=f"期限 / Expires: {device['warranty_expiry']}",
                inline=False
            )

        await message.channel.send(embed=embed)

    async def _handle_device_issue(self, message):
        """Handle device issue reporting"""
        content = message.content
        parts = content.replace('issue', '').replace('問題', '').replace('故障', '').split(',')

        if len(parts) < 2:
            await message.channel.send("❌ 形式: issue <device_id>, <issue_type>, <description>")
            return

        try:
            device_id = int(parts[0].strip())
            issue_type = parts[1].strip()
            description = parts[2].strip() if len(parts) > 2 else ""

            issue_id = self.db.add_issue(
                device_id=device_id,
                issue_type=issue_type,
                description=description,
                status='open',
                reported_date=datetime.now().strftime('%Y-%m-%d'),
                severity='medium'
            )

            embed = discord.Embed(
                title="⚠️ 問題を報告しました / Issue Reported",
                color=discord.Color.red()
            )
            embed.add_field(name="Issue ID", value=issue_id, inline=True)
            embed.add_field(name="Device ID", value=device_id, inline=True)
            embed.add_field(name="タイプ / Type", value=issue_type, inline=True)
            if description:
                embed.add_field(name="説明 / Description", value=description, inline=False)

            await message.channel.send(embed=embed)
        except Exception as e:
            await message.channel.send(f"❌ エラー: {str(e)}")

    async def _handle_maintenance(self, message):
        """Handle maintenance recording"""
        content = message.content
        parts = content.replace('maintenance', '').replace('メンテナンス', '').replace('修理', '').split(',')

        if len(parts) < 2:
            await message.channel.send("❌ 形式: maintenance <device_id>, <type>, [description], [cost]")
            return

        try:
            device_id = int(parts[0].strip())
            maint_type = parts[1].strip()
            description = parts[2].strip() if len(parts) > 2 else ""
            cost = float(parts[3].strip()) if len(parts) > 3 else None

            maint_id = self.db.add_maintenance(
                device_id=device_id,
                maintenance_type=maint_type,
                description=description,
                cost=cost,
                performed_date=datetime.now().strftime('%Y-%m-%d')
            )

            embed = discord.Embed(
                title="🔧 メンテナンスを記録しました / Maintenance Recorded",
                color=discord.Color.orange()
            )
            embed.add_field(name="ID", value=maint_id, inline=True)
            embed.add_field(name="Device ID", value=device_id, inline=True)
            embed.add_field(name="タイプ / Type", value=maint_type, inline=True)
            if cost:
                embed.add_field(name="費用 / Cost", value=f"${cost}", inline=True)
            if description:
                embed.add_field(name="説明 / Description", value=description, inline=False)

            await message.channel.send(embed=embed)
        except Exception as e:
            await message.channel.send(f"❌ エラー: {str(e)}")

    async def _handle_assignment(self, message):
        """Handle device assignment"""
        content = message.content
        parts = content.replace('assign', '').replace('貸出', '').split(',')

        if len(parts) < 2:
            await message.channel.send("❌ 形式: assign <device_id>, <assigned_to>, [purpose]")
            return

        try:
            device_id = int(parts[0].strip())
            assigned_to = parts[1].strip()
            purpose = parts[2].strip() if len(parts) > 2 else ""

            assign_id = self.db.assign_device(
                device_id=device_id,
                assigned_to=assigned_to,
                assigned_date=datetime.now().strftime('%Y-%m-%d'),
                purpose=purpose
            )

            embed = discord.Embed(
                title="📋 デバイスを貸出しました / Device Assigned",
                color=discord.Color.green()
            )
            embed.add_field(name="ID", value=assign_id, inline=True)
            embed.add_field(name="Device ID", value=device_id, inline=True)
            embed.add_field(name="貸出先 / Assigned To", value=assigned_to, inline=True)
            if purpose:
                embed.add_field(name="目的 / Purpose", value=purpose, inline=False)

            await message.channel.send(embed=embed)
        except Exception as e:
            await message.channel.send(f"❌ エラー: {str(e)}")

    async def _handle_statistics(self, message):
        """Handle statistics request"""
        stats = self.db.get_statistics()

        embed = discord.Embed(
            title="📊 デバイス統計 / Device Statistics",
            color=discord.Color.purple()
        )
        embed.add_field(name="総デバイス数 / Total", value=stats['total_devices'], inline=True)
        embed.add_field(name="稼働中 / Active", value=stats['active_devices'], inline=True)
        embed.add_field(name="オープン中の問題 / Open Issues", value=stats['open_issues'], inline=True)

        if stats['by_type']:
            type_list = "\n".join([f"• {k}: {v}" for k, v in stats['by_type'].items()])
            embed.add_field(name="タイプ別 / By Type", value=type_list, inline=False)

        await message.channel.send(embed=embed)

    async def _handle_help(self, message):
        """Handle help command"""
        embed = discord.Embed(
            title="📖 Device Agent - ヘルプ / Help",
            description="デバイス管理用Discordボット / Discord Bot for Device Management",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="コマンド / Commands",
            value="""
**デバイス登録 / Add Device:**
- `add device <name>, <type>, [model], [serial], [location], [owner]`
- `登録 <名前>, <タイプ>, ...`

**デバイス一覧 / List Devices:**
- `list devices [active|inactive] [type]`
- `デバイス一覧 [タイプ]`

**デバイス情報 / Device Info:**
- `device info <id>`
- `デバイス情報 <id>`

**検索 / Search:**
- `search <term>`
- `検索 <語句>`

**保証確認 / Warranty:**
- `warranty check`
- `保証確認`

**問題報告 / Report Issue:**
- `issue <device_id>, <type>, [description]`
- `問題 <ID>, <タイプ>`

**メンテナンス / Maintenance:**
- `maintenance <device_id>, <type>, [desc], [cost]`
- `修理 <ID>, <タイプ>`

**貸出 / Assign:**
- `assign <device_id>, <person>, [purpose]`
- `貸出 <ID>, <担当者>`

**統計 / Statistics:**
- `statistics`
- `統計`
""",
            inline=False
        )

        await message.channel.send(embed=embed)


def main():
    """Main entry point"""
    import os
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("Error: DISCORD_TOKEN environment variable not set")
        return

    bot = DeviceAgent()
    bot.run(token)


if __name__ == '__main__':
    main()
