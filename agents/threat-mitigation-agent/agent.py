#!/usr/bin/env python3
# threat-mitigation-agent
# 脅威緩和エージェント。脅威の緩和策・対策の実装。

import asyncio
import logging
from db import Threat_mitigation_agentDatabase
from discord import Threat_mitigation_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Threat_mitigation_agentAgent:
    # threat-mitigation-agent メインエージェント

    def __init__(self, db_path: str = "threat-mitigation-agent.db"):
        # 初期化
        self.db = Threat_mitigation_agentDatabase(db_path)
        self.discord_bot = Threat_mitigation_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting threat-mitigation-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping threat-mitigation-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Threat_mitigation_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
