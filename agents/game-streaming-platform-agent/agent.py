#!/usr/bin/env python3
# game-streaming-platform-agent
# ゲーム配信プラットフォームエージェント。ゲーム配信プラットフォームの運営・管理。

import asyncio
import logging
from db import Game_streaming_platform_agentDatabase
from discord import Game_streaming_platform_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Game_streaming_platform_agentAgent:
    # game-streaming-platform-agent メインエージェント

    def __init__(self, db_path: str = "game-streaming-platform-agent.db"):
        # 初期化
        self.db = Game_streaming_platform_agentDatabase(db_path)
        self.discord_bot = Game_streaming_platform_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting game-streaming-platform-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping game-streaming-platform-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Game_streaming_platform_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
