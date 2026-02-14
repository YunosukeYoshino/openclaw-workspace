#!/usr/bin/env python3
# behavioral-analysis-agent
# 挙動分析エージェント。ユーザー挙動・システム挙動の分析。

import asyncio
import logging
from db import Behavioral_analysis_agentDatabase
from discord import Behavioral_analysis_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Behavioral_analysis_agentAgent:
    # behavioral-analysis-agent メインエージェント

    def __init__(self, db_path: str = "behavioral-analysis-agent.db"):
        # 初期化
        self.db = Behavioral_analysis_agentDatabase(db_path)
        self.discord_bot = Behavioral_analysis_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting behavioral-analysis-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping behavioral-analysis-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Behavioral_analysis_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
