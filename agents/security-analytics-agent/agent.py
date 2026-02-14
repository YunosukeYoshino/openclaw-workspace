#!/usr/bin/env python3
# security-analytics-agent
# セキュリティアナリティクスエージェント。セキュリティデータの分析・インサイト。

import asyncio
import logging
from db import Security_analytics_agentDatabase
from discord import Security_analytics_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Security_analytics_agentAgent:
    # security-analytics-agent メインエージェント

    def __init__(self, db_path: str = "security-analytics-agent.db"):
        # 初期化
        self.db = Security_analytics_agentDatabase(db_path)
        self.discord_bot = Security_analytics_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting security-analytics-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping security-analytics-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Security_analytics_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
