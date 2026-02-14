#!/usr/bin/env python3
# erotic-feedback-agent
# えっちコンテンツフィードバックエージェント。フィードバックの収集・分析。

import asyncio
import logging
from db import Erotic_feedback_agentDatabase
from discord import Erotic_feedback_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Erotic_feedback_agentAgent:
    # erotic-feedback-agent メインエージェント

    def __init__(self, db_path: str = "erotic-feedback-agent.db"):
        # 初期化
        self.db = Erotic_feedback_agentDatabase(db_path)
        self.discord_bot = Erotic_feedback_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting erotic-feedback-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping erotic-feedback-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Erotic_feedback_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
