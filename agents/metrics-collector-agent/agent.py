#!/usr/bin/env python3
# metrics-collector-agent
# メトリクス収集エージェント。システムメトリクスの収集・分析。

import asyncio
import logging
from db import Metrics_collector_agentDatabase
from discord import Metrics_collector_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Metrics_collector_agentAgent:
    # metrics-collector-agent メインエージェント

    def __init__(self, db_path: str = "metrics-collector-agent.db"):
        # 初期化
        self.db = Metrics_collector_agentDatabase(db_path)
        self.discord_bot = Metrics_collector_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting metrics-collector-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping metrics-collector-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Metrics_collector_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
