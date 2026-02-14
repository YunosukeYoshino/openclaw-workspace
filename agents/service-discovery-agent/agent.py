#!/usr/bin/env python3
# service-discovery-agent
# サービスディスカバリーエージェント。サービスディスカバリーの管理。

import asyncio
import logging
from db import Service_discovery_agentDatabase
from discord import Service_discovery_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Service_discovery_agentAgent:
    # service-discovery-agent メインエージェント

    def __init__(self, db_path: str = "service-discovery-agent.db"):
        # 初期化
        self.db = Service_discovery_agentDatabase(db_path)
        self.discord_bot = Service_discovery_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting service-discovery-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping service-discovery-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Service_discovery_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
