#!/usr/bin/env python3
# erotic-rating-system-agent
# えっちコンテンツ評価システムエージェント。評価システムの管理・運用。

import asyncio
import logging
from db import Erotic_rating_system_agentDatabase
from discord import Erotic_rating_system_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Erotic_rating_system_agentAgent:
    # erotic-rating-system-agent メインエージェント

    def __init__(self, db_path: str = "erotic-rating-system-agent.db"):
        # 初期化
        self.db = Erotic_rating_system_agentDatabase(db_path)
        self.discord_bot = Erotic_rating_system_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting erotic-rating-system-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping erotic-rating-system-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Erotic_rating_system_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
