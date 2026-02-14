#!/usr/bin/env python3
# threat-feed-manager-agent
# 脅威フィード管理エージェント。脅威インテリジェンスフィードの管理。

import asyncio
import logging
from db import Threat_feed_manager_agentDatabase
from discord import Threat_feed_manager_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Threat_feed_manager_agentAgent:
    # threat-feed-manager-agent メインエージェント

    def __init__(self, db_path: str = "threat-feed-manager-agent.db"):
        # 初期化
        self.db = Threat_feed_manager_agentDatabase(db_path)
        self.discord_bot = Threat_feed_manager_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting threat-feed-manager-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping threat-feed-manager-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Threat_feed_manager_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
