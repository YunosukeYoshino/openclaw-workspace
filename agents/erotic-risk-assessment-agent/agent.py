#!/usr/bin/env python3
# erotic-risk-assessment-agent
# えっちリスク評価エージェント。コンテンツのリスク評価・分析。

import asyncio
import logging
from db import Erotic_risk_assessment_agentDatabase
from discord import Erotic_risk_assessment_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Erotic_risk_assessment_agentAgent:
    # erotic-risk-assessment-agent メインエージェント

    def __init__(self, db_path: str = "erotic-risk-assessment-agent.db"):
        # 初期化
        self.db = Erotic_risk_assessment_agentDatabase(db_path)
        self.discord_bot = Erotic_risk_assessment_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting erotic-risk-assessment-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping erotic-risk-assessment-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Erotic_risk_assessment_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
