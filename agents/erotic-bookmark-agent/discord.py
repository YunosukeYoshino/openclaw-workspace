#!/usr/bin/env python3
"""
えっちコンテンツブックマークエージェント - Discord連携
Erotic Content Bookmark Agent - Discord Integration
"""

import discord
from discord.ext import commands
from agent import EroticBookmarkAgent


class EroticBookmarkAgentBot(commands.Bot):
    """えっちコンテンツブックマークエージェント Discord Bot"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        self.agent = EroticBookmarkAgent()

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


def main():
    """メイン関数"""
    import os
    from dotenv import load_dotenv

    load_dotenv()

    bot = EroticBookmarkAgentBot()
    token = os.getenv('DISCORD_TOKEN')

    if not token:
        print("❌ DISCORD_TOKEN が設定されていません / DISCORD_TOKEN not set")
        return

    bot.run(token)


if __name__ == '__main__':
    main()
