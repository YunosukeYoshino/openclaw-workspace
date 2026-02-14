#!/usr/bin/env python3
# baseball-injury-prevention-agent
# 野球怪我予防エージェント。選手の怪我予防・リスク評価。

import asyncio
import logging
from db import Baseball_injury_prevention_agentDatabase
from discord import Baseball_injury_prevention_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Baseball_injury_prevention_agentAgent:
    # baseball-injury-prevention-agent メインエージェント

    def __init__(self, db_path: str = "baseball-injury-prevention-agent.db"):
        # 初期化
        self.db = Baseball_injury_prevention_agentDatabase(db_path)
        self.discord_bot = Baseball_injury_prevention_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting baseball-injury-prevention-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping baseball-injury-prevention-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Baseball_injury_prevention_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
