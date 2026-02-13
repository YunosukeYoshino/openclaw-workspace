#!/usr/bin/env python3
"""
えっちコンテンツ高度検索エージェント - Discord連携
Erotic Content Advanced Search Agent - Discord Integration
"""

import discord
from discord.ext import commands
from agent import EroticSearchAgent


class EroticSearchAgentBot(commands.Bot):
    """えっちコンテンツ高度検索エージェント Discord Bot"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        self.agent = EroticSearchAgent()

    async def on_ready(self):
        """Bot起動時"""
        print(f'✅ {self.user.name} が起動しました / Logged in as {self.user.name}')

    async def on_message(self, message):
        """メッセージ受信時"""
        # 自分のメッセージは無視
        if message.author == self.user:
            return

        # プライベートメッセージまたはメンションの場合に応答
        if isinstance(message.channel, discord.DMChannel) or self.user in message.mentions:
            content = message.content.replace(f'<@{self.user.id}>', '').replace(f'<@!{self.user.id}>', '').strip()
            result = self.agent.handle_message(content)
            if result:
                await message.reply(result)

        await self.process_commands(message)

    async def process_commands(self, message):
        """コマンド処理"""
        content = message.content.strip()

        if content.startswith('!help'):
            await self.help_command(message)
        elif content.startswith('!info'):
            await self.info_command(message)

    async def help_command(self, ctx):
        """ヘルプメッセージ"""
        help_text = """
**えっちコンテンツ高度検索エージェント**
**Erotic Content Advanced Search Agent**

🔍 検索機能 / Search Features

コマンド / Commands:

📝 基本コマンド / Basic Commands:
- 検索: キーワード - キーワードで検索
- 検索: タグ:タグ - タグで検索
- 検索: アーティスト:名前 - アーティストで検索
- 追加: id:001, タイトル:作品 - インデックスに追加
- 更新: 1, タイトル:新タイトル - インデックスを更新
- 削除: 1 - インデックスから削除
- 履歴 - 検索履歴を表示
- 統計 - 統計情報を表示
- 再構築 - インデックスを再構築

💡 ヒント / Tips:
- タイトルで検索: `検索: タイトル:素晴らしい作品`
- タグで検索: `検索: タグ:最高,おすすめ`
- 複数条件: `検索: タグ:最高, アーティスト:名前`
"""
        await ctx.send(help_text)

    async def info_command(self, ctx):
        """情報メッセージ"""
        info = """
**えっちコンテンツ高度検索エージェント**
**Erotic Content Advanced Search Agent**

📖 概要 / Overview
えっちなコンテンツの高度な検索機能を提供するエージェント。

🗄️ データベース / Database
- search_index: コンテンツインデックス
- search_queries: 検索クエリ履歴

🔍 検索方法 / Search Methods
- キーワード検索
- タグ検索
- アーティスト検索
- ソース検索

📊 統計 / Statistics
- インデックス件数
- 検索クエリ数
- 平均結果数
- トップ検索クエリ
"""
        await ctx.send(info)


def main():
    """メイン関数"""
    import os
    from dotenv import load_dotenv

    load_dotenv()

    bot = EroticSearchAgentBot()
    token = os.getenv('DISCORD_TOKEN')

    if not token:
        print("❌ DISCORD_TOKEN が設定されていません / DISCORD_TOKEN not set")
        return

    bot.run(token)


if __name__ == '__main__':
    main()
