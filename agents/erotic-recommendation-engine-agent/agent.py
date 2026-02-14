#!/usr/bin/env python3
# erotic-recommendation-engine-agent
# えっちコンテンツリコメンデーションエンジンエージェント。レコメンデーションエンジンの構築・運用。

import asyncio
import logging
from db import Erotic_recommendation_engine_agentDatabase
from discord import Erotic_recommendation_engine_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Erotic_recommendation_engine_agentAgent:
    # erotic-recommendation-engine-agent メインエージェント

    def __init__(self, db_path: str = "erotic-recommendation-engine-agent.db"):
        # 初期化
        self.db = Erotic_recommendation_engine_agentDatabase(db_path)
        self.discord_bot = Erotic_recommendation_engine_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting erotic-recommendation-engine-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping erotic-recommendation-engine-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Erotic_recommendation_engine_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
