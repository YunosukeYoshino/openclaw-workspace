#!/usr/bin/env python3
# baseball-mental-health-agent
# 野球メンタルヘルスエージェント。選手のメンタルヘルス・心理状態の管理。

import asyncio
import logging
from db import Baseball_mental_health_agentDatabase
from discord import Baseball_mental_health_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Baseball_mental_health_agentAgent:
    # baseball-mental-health-agent メインエージェント

    def __init__(self, db_path: str = "baseball-mental-health-agent.db"):
        # 初期化
        self.db = Baseball_mental_health_agentDatabase(db_path)
        self.discord_bot = Baseball_mental_health_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting baseball-mental-health-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping baseball-mental-health-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Baseball_mental_health_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
