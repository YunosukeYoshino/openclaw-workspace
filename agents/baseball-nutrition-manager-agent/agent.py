#!/usr/bin/env python3
# baseball-nutrition-manager-agent
# 野球栄養管理エージェント。選手の栄養管理・食事計画の提供。

import asyncio
import logging
from db import Baseball_nutrition_manager_agentDatabase
from discord import Baseball_nutrition_manager_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Baseball_nutrition_manager_agentAgent:
    # baseball-nutrition-manager-agent メインエージェント

    def __init__(self, db_path: str = "baseball-nutrition-manager-agent.db"):
        # 初期化
        self.db = Baseball_nutrition_manager_agentDatabase(db_path)
        self.discord_bot = Baseball_nutrition_manager_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting baseball-nutrition-manager-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping baseball-nutrition-manager-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Baseball_nutrition_manager_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
