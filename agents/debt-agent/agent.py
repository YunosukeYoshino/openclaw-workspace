#!/usr/bin/env python3
"""
借金管理エージェント #55 - Discord Bot
メインエントリーポイント
"""

import os
import discord
from discord.ext import commands
from discord import app_commands
from pathlib import Path

# Import discord integration
from discord import handle_message

# Import database initialization
from db import init_db

# Database path
DB_PATH = Path(__file__).parent / "debt.db"

# Initialize database
if not DB_PATH.exists():
    init_db()

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    """Botが起動した時の処理"""
    print(f'💳 借金管理エージェントが起動しました: {bot.user.name} ({bot.user.id})')
    print('------')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Error syncing commands: {e}')


@bot.event
async def on_message(message):
    """メッセージ受信時の処理"""
    # Bot自身のメッセージは無視
    if message.author == bot.user:
        return

    # メンションされた場合またはチャンネルで直接メッセージが送られた場合
    if bot.user in message.mentions or isinstance(message.channel, discord.DMChannel):
        # メンションを除去してメッセージを解析
        content = message.content.replace(f'<@{bot.user.id}>', '').replace(f'<@!{bot.user.id}>', '').strip()

        if content:
            # メッセージを処理
            response = handle_message(content)

            if response:
                # Discordのメッセージ長制限に対応
                if len(response) > 2000:
                    # 長い場合は分割して送信
                    for i in range(0, len(response), 2000):
                        await message.channel.send(response[i:i+2000])
                else:
                    await message.channel.send(response)
            else:
                await message.channel.send('❌ コマンドを理解できませんでした。\n'
                                           '使用例:\n'
                                           '借金: クレジットカード, 借入先: 銀行A, 元本: 500000, 金利: 15\n'
                                           '支払い: 1 10000\n'
                                           '借金一覧\n'
                                           '残高: 1\n'
                                           '統計')

    # コマンド処理
    await bot.process_commands(message)


@bot.tree.command(name="help", description="使い方を表示します")
async def help_command(interaction: discord.Interaction):
    """ヘルプコマンド"""
    help_text = """💳 借金管理エージェント - ヘルプ

**借金の追加**
`借金: 名前, 借入先: 銀行, 元本: 金額, 金利: %, 返済期限: 日付`

**支払いの記録**
`支払い: 借金ID 金額`

**返済プランの追加**
`プラン: 借金ID, 月次: 金額, 開始: 日付, 終了: 日付`

**一覧・確認**
- `借金一覧` - 全借金を表示
- `残高: 借金ID` - 残高を確認
- `履歴: 借金ID` - 支払い履歴
- `サマリー: 借金ID` - 支払いサマリー

**例**
```
借金: クレジットカード, 借入先: 銀行A, 元本: 500000, 金利: 15, 返済期限: 2027-12-31
支払い: 1 10000
借金一覧
```
"""
    await interaction.response.send_message(help_text)


@bot.tree.command(name="list", description="借金一覧を表示します")
async def list_command(interaction: discord.Interaction):
    """借金一覧コマンド"""
    response = handle_message("借金一覧")
    if len(response) > 2000:
        for i in range(0, len(response), 2000):
            await interaction.response.send_message(response[i:i+2000])
    else:
        await interaction.response.send_message(response)


@bot.tree.command(name="stats", description="統計情報を表示します")
async def stats_command(interaction: discord.Interaction):
    """統計コマンド"""
    # debt-agentには統計コマンドがないため、エラーメッセージ
    await interaction.response.send_message("💳 統計機能は現在開発中です。\n`借金一覧` で借金の概要を確認できます。")


def run_bot():
    """Discord Botを実行"""
    token = os.environ.get('DISCORD_TOKEN')
    if not token:
        print('❌ DISCORD_TOKEN 環境変数が設定されていません')
        print('例: export DISCORD_TOKEN="your-bot-token"')
        return

    bot.run(token)


if __name__ == '__main__':
    init_db()
    run_bot()
