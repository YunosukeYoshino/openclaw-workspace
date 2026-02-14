#!/usr/bin/env python3
# threat-hunter-agent
# 脅威ハンターエージェント。能動的な脅威ハンティング・調査。

import asyncio
import logging
from db import Threat_hunter_agentDatabase
from discord import Threat_hunter_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Threat_hunter_agentAgent:
    # threat-hunter-agent メインエージェント

    def __init__(self, db_path: str = "threat-hunter-agent.db"):
        # 初期化
        self.db = Threat_hunter_agentDatabase(db_path)
        self.discord_bot = Threat_hunter_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting threat-hunter-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping threat-hunter-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Threat_hunter_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
