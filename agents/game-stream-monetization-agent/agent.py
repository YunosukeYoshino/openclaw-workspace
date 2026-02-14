#!/usr/bin/env python3
# game-stream-monetization-agent
# ゲーム配信収益化エージェント。配信の収益化・広告・スポンサー管理。

import asyncio
import logging
from db import Game_stream_monetization_agentDatabase
from discord import Game_stream_monetization_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Game_stream_monetization_agentAgent:
    # game-stream-monetization-agent メインエージェント

    def __init__(self, db_path: str = "game-stream-monetization-agent.db"):
        # 初期化
        self.db = Game_stream_monetization_agentDatabase(db_path)
        self.discord_bot = Game_stream_monetization_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting game-stream-monetization-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping game-stream-monetization-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Game_stream_monetization_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
