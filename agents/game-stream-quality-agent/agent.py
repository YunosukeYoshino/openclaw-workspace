#!/usr/bin/env python3
# game-stream-quality-agent
# ゲーム配信品質管理エージェント。配信品質・ビットレート・遅延の管理。

import asyncio
import logging
from db import Game_stream_quality_agentDatabase
from discord import Game_stream_quality_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Game_stream_quality_agentAgent:
    # game-stream-quality-agent メインエージェント

    def __init__(self, db_path: str = "game-stream-quality-agent.db"):
        # 初期化
        self.db = Game_stream_quality_agentDatabase(db_path)
        self.discord_bot = Game_stream_quality_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting game-stream-quality-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping game-stream-quality-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Game_stream_quality_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
