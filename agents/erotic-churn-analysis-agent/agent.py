#!/usr/bin/env python3
# erotic-churn-analysis-agent
# えっちコンテンツチャーン分析エージェント。チャーン分析・防止策。

import asyncio
import logging
from db import Erotic_churn_analysis_agentDatabase
from discord import Erotic_churn_analysis_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Erotic_churn_analysis_agentAgent:
    # erotic-churn-analysis-agent メインエージェント

    def __init__(self, db_path: str = "erotic-churn-analysis-agent.db"):
        # 初期化
        self.db = Erotic_churn_analysis_agentDatabase(db_path)
        self.discord_bot = Erotic_churn_analysis_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting erotic-churn-analysis-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping erotic-churn-analysis-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Erotic_churn_analysis_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
