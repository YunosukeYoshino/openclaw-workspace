#!/usr/bin/env python3
# dashboard-visualization-agent
# ダッシュボード可視化エージェント。データの可視化・ダッシュボード管理。

import asyncio
import logging
from db import Dashboard_visualization_agentDatabase
from discord import Dashboard_visualization_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Dashboard_visualization_agentAgent:
    # dashboard-visualization-agent メインエージェント

    def __init__(self, db_path: str = "dashboard-visualization-agent.db"):
        # 初期化
        self.db = Dashboard_visualization_agentDatabase(db_path)
        self.discord_bot = Dashboard_visualization_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting dashboard-visualization-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping dashboard-visualization-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Dashboard_visualization_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
