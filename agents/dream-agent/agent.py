#!/usr/bin/env python3
"""
夢日記エージェント #16 - Discord Bot
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
DB_PATH = Path(__file__).parent / "dreams.db"

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
    print(f'🌙 夢日記エージェントが起動しました: {bot.user.name} ({bot.user.id})')
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
                                           '夢: 空を飛んでいた, 感情: 嬉しい\n'
                                           '夢: 怪物に追われていた, 種類: 悪夢, 感情: 怖い\n'
                                           '夢一覧\n'
                                           '統計')

    # コマンド処理
    await bot.process_commands(message)


@bot.tree.command(name="help", description="使い方を表示します")
async def help_command(interaction: discord.Interaction):
    """ヘルプコマンド"""
    help_text = """🌙 夢日記エージェント - ヘルプ

**夢の追加**
`夢: 内容, 感情: 感情, 種類: 種類, タグ: タグ1,タグ2`

**種類**
- はっきり (clear) - 明晰な夢
- ぼやけ (vague) - 曖昧な夢
- 悪夢 (nightmare) - 怖い夢
- ラシッド (lucid) - 明夢
- 再発 (recurrent) - 繰り返しの夢

**一覧・確認**
- `夢一覧` - 全夢を表示
- `統計` - 週間統計
- `検索: キーワード` - キーワード検索

**例**
```
夢: 空を飛んでいた, 感情: 嬉しい
夢: 怪物に追われていた, 種類: 悪夢, 感情: 怖い
夢: 再発夢、いつも同じ場所, 種類: 再発
夢一覧
統計
```
"""
    await interaction.response.send_message(help_text)


@bot.tree.command(name="list", description="夢一覧を表示します")
async def list_command(interaction: discord.Interaction):
    """夢一覧コマンド"""
    response = handle_message("夢一覧")
    if len(response) > 2000:
        for i in range(0, len(response), 2000):
            await interaction.response.send_message(response[i:i+2000])
    else:
        await interaction.response.send_message(response)


@bot.tree.command(name="stats", description="統計情報を表示します")
async def stats_command(interaction: discord.Interaction):
    """統計コマンド"""
    response = handle_message("統計")
    if len(response) > 2000:
        for i in range(0, len(response), 2000):
            await interaction.response.send_message(response[i:i+2000])
    else:
        await interaction.response.send_message(response)


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
