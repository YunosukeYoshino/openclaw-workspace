#!/usr/bin/env python3
# etl-pipeline-agent
# ETLパイプラインエージェント。ETLパイプラインの管理・実行。

import asyncio
import logging
from db import Etl_pipeline_agentDatabase
from discord import Etl_pipeline_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Etl_pipeline_agentAgent:
    # etl-pipeline-agent メインエージェント

    def __init__(self, db_path: str = "etl-pipeline-agent.db"):
        # 初期化
        self.db = Etl_pipeline_agentDatabase(db_path)
        self.discord_bot = Etl_pipeline_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting etl-pipeline-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping etl-pipeline-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Etl_pipeline_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
