#!/usr/bin/env python3
# erotic-segmentation-agent
# えっちコンテンツセグメンテーションエージェント。ユーザーセグメンテーション・分析。

import asyncio
import logging
from db import Erotic_segmentation_agentDatabase
from discord import Erotic_segmentation_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Erotic_segmentation_agentAgent:
    # erotic-segmentation-agent メインエージェント

    def __init__(self, db_path: str = "erotic-segmentation-agent.db"):
        # 初期化
        self.db = Erotic_segmentation_agentDatabase(db_path)
        self.discord_bot = Erotic_segmentation_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting erotic-segmentation-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping erotic-segmentation-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Erotic_segmentation_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
