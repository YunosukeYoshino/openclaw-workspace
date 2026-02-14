#!/usr/bin/env python3
# erotic-legal-agent
# えっちコンテンツ法務エージェント。法務対応・契約・紛争解決。

import asyncio
import logging
from db import Erotic_legal_agentDatabase
from discord import Erotic_legal_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Erotic_legal_agentAgent:
    # erotic-legal-agent メインエージェント

    def __init__(self, db_path: str = "erotic-legal-agent.db"):
        # 初期化
        self.db = Erotic_legal_agentDatabase(db_path)
        self.discord_bot = Erotic_legal_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting erotic-legal-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping erotic-legal-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Erotic_legal_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
