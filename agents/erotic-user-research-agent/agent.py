#!/usr/bin/env python3
# erotic-user-research-agent
# えっちコンテンツユーザーリサーチエージェント。ユーザーリサーチの実施・分析。

import asyncio
import logging
from db import Erotic_user_research_agentDatabase
from discord import Erotic_user_research_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Erotic_user_research_agentAgent:
    # erotic-user-research-agent メインエージェント

    def __init__(self, db_path: str = "erotic-user-research-agent.db"):
        # 初期化
        self.db = Erotic_user_research_agentDatabase(db_path)
        self.discord_bot = Erotic_user_research_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting erotic-user-research-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping erotic-user-research-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Erotic_user_research_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
