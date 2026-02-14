#!/usr/bin/env python3
# threat-intelligence-collector-agent
# 脅威インテリジェンスコレクターエージェント。脅威インテリジェンスの収集・分析。

import asyncio
import logging
from db import Threat_intelligence_collector_agentDatabase
from discord import Threat_intelligence_collector_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Threat_intelligence_collector_agentAgent:
    # threat-intelligence-collector-agent メインエージェント

    def __init__(self, db_path: str = "threat-intelligence-collector-agent.db"):
        # 初期化
        self.db = Threat_intelligence_collector_agentDatabase(db_path)
        self.discord_bot = Threat_intelligence_collector_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting threat-intelligence-collector-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping threat-intelligence-collector-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Threat_intelligence_collector_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
