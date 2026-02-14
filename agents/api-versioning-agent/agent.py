#!/usr/bin/env python3
# api-versioning-agent
# APIバージョニングエージェント。APIバージョン管理。

import asyncio
import logging
from db import Api_versioning_agentDatabase
from discord import Api_versioning_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Api_versioning_agentAgent:
    # api-versioning-agent メインエージェント

    def __init__(self, db_path: str = "api-versioning-agent.db"):
        # 初期化
        self.db = Api_versioning_agentDatabase(db_path)
        self.discord_bot = Api_versioning_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting api-versioning-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping api-versioning-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Api_versioning_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
