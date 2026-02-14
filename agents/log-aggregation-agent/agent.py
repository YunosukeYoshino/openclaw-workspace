#!/usr/bin/env python3
# log-aggregation-agent
# ログ集約エージェント。ログの収集・集約・分析。

import asyncio
import logging
from db import Log_aggregation_agentDatabase
from discord import Log_aggregation_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Log_aggregation_agentAgent:
    # log-aggregation-agent メインエージェント

    def __init__(self, db_path: str = "log-aggregation-agent.db"):
        # 初期化
        self.db = Log_aggregation_agentDatabase(db_path)
        self.discord_bot = Log_aggregation_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting log-aggregation-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping log-aggregation-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Log_aggregation_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
