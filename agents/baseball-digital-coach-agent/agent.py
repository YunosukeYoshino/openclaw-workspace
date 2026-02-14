#!/usr/bin/env python3
# baseball-digital-coach-agent
# 野球デジタルコーチエージェント。デジタルツールを活用したコーチング・指導の管理。

import asyncio
import logging
from db import Baseball_digital_coach_agentDatabase
from discord import Baseball_digital_coach_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Baseball_digital_coach_agentAgent:
    # baseball-digital-coach-agent メインエージェント

    def __init__(self, db_path: str = "baseball-digital-coach-agent.db"):
        # 初期化
        self.db = Baseball_digital_coach_agentDatabase(db_path)
        self.discord_bot = Baseball_digital_coach_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting baseball-digital-coach-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping baseball-digital-coach-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Baseball_digital_coach_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
