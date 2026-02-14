#!/usr/bin/env python3
# erotic-content-safety-agent
# えっちコンテンツセーフティエージェント。コンテンツの安全性チェック・監視。

import asyncio
import logging
from db import Erotic_content_safety_agentDatabase
from discord import Erotic_content_safety_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Erotic_content_safety_agentAgent:
    # erotic-content-safety-agent メインエージェント

    def __init__(self, db_path: str = "erotic-content-safety-agent.db"):
        # 初期化
        self.db = Erotic_content_safety_agentDatabase(db_path)
        self.discord_bot = Erotic_content_safety_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting erotic-content-safety-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping erotic-content-safety-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Erotic_content_safety_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
