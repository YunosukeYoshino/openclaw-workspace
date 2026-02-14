#!/usr/bin/env python3
# erotic-license-manager-agent
# えっちコンテンツライセンス管理エージェント。コンテンツライセンスの管理・監査。

import asyncio
import logging
from db import Erotic_license_manager_agentDatabase
from discord import Erotic_license_manager_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Erotic_license_manager_agentAgent:
    # erotic-license-manager-agent メインエージェント

    def __init__(self, db_path: str = "erotic-license-manager-agent.db"):
        # 初期化
        self.db = Erotic_license_manager_agentDatabase(db_path)
        self.discord_bot = Erotic_license_manager_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting erotic-license-manager-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping erotic-license-manager-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Erotic_license_manager_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
