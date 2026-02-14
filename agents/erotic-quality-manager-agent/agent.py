#!/usr/bin/env python3
# erotic-quality-manager-agent
# えっちコンテンツ品質管理エージェント。コンテンツ品質の管理・評価。

import asyncio
import logging
from db import Erotic_quality_manager_agentDatabase
from discord import Erotic_quality_manager_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Erotic_quality_manager_agentAgent:
    # erotic-quality-manager-agent メインエージェント

    def __init__(self, db_path: str = "erotic-quality-manager-agent.db"):
        # 初期化
        self.db = Erotic_quality_manager_agentDatabase(db_path)
        self.discord_bot = Erotic_quality_manager_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting erotic-quality-manager-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping erotic-quality-manager-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Erotic_quality_manager_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
