#!/usr/bin/env python3
# anomaly-detection-agent
# 異常検知エージェント。異常行動・パターンの検知・分析。

import asyncio
import logging
from db import Anomaly_detection_agentDatabase
from discord import Anomaly_detection_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Anomaly_detection_agentAgent:
    # anomaly-detection-agent メインエージェント

    def __init__(self, db_path: str = "anomaly-detection-agent.db"):
        # 初期化
        self.db = Anomaly_detection_agentDatabase(db_path)
        self.discord_bot = Anomaly_detection_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting anomaly-detection-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping anomaly-detection-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Anomaly_detection_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
