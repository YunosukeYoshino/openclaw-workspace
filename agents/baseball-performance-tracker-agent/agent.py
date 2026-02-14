#!/usr/bin/env python3
# baseball-performance-tracker-agent
# 野球パフォーマンストラッカーエージェント。選手のパフォーマンスデータの追跡・分析。

import asyncio
import logging
from db import Baseball_performance_tracker_agentDatabase
from discord import Baseball_performance_tracker_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Baseball_performance_tracker_agentAgent:
    # baseball-performance-tracker-agent メインエージェント

    def __init__(self, db_path: str = "baseball-performance-tracker-agent.db"):
        # 初期化
        self.db = Baseball_performance_tracker_agentDatabase(db_path)
        self.discord_bot = Baseball_performance_tracker_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting baseball-performance-tracker-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping baseball-performance-tracker-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Baseball_performance_tracker_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
