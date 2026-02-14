#!/usr/bin/env python3
# erotic-age-verification-agent
# えっち年齢認証エージェント。年齢認証システムの管理・運用。

import asyncio
import logging
from db import Erotic_age_verification_agentDatabase
from discord import Erotic_age_verification_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Erotic_age_verification_agentAgent:
    # erotic-age-verification-agent メインエージェント

    def __init__(self, db_path: str = "erotic-age-verification-agent.db"):
        # 初期化
        self.db = Erotic_age_verification_agentDatabase(db_path)
        self.discord_bot = Erotic_age_verification_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting erotic-age-verification-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping erotic-age-verification-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Erotic_age_verification_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
