#!/usr/bin/env python3
# erotic-copyright-agent
# えっちコンテンツ著作権エージェント。著作権管理・保護・侵害対応。

import asyncio
import logging
from db import Erotic_copyright_agentDatabase
from discord import Erotic_copyright_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Erotic_copyright_agentAgent:
    # erotic-copyright-agent メインエージェント

    def __init__(self, db_path: str = "erotic-copyright-agent.db"):
        # 初期化
        self.db = Erotic_copyright_agentDatabase(db_path)
        self.discord_bot = Erotic_copyright_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting erotic-copyright-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping erotic-copyright-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Erotic_copyright_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
