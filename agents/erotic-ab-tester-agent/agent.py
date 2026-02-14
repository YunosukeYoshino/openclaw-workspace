#!/usr/bin/env python3
# erotic-ab-tester-agent
# えっちコンテンツA/Bテストエージェント。A/Bテストの実施・分析。

import asyncio
import logging
from db import Erotic_ab_tester_agentDatabase
from discord import Erotic_ab_tester_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Erotic_ab_tester_agentAgent:
    # erotic-ab-tester-agent メインエージェント

    def __init__(self, db_path: str = "erotic-ab-tester-agent.db"):
        # 初期化
        self.db = Erotic_ab_tester_agentDatabase(db_path)
        self.discord_bot = Erotic_ab_tester_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting erotic-ab-tester-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping erotic-ab-tester-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Erotic_ab_tester_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
