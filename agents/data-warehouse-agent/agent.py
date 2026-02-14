#!/usr/bin/env python3
# data-warehouse-agent
# データウェアハウスエージェント。データウェアハウスの管理・運用。

import asyncio
import logging
from db import Data_warehouse_agentDatabase
from discord import Data_warehouse_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Data_warehouse_agentAgent:
    # data-warehouse-agent メインエージェント

    def __init__(self, db_path: str = "data-warehouse-agent.db"):
        # 初期化
        self.db = Data_warehouse_agentDatabase(db_path)
        self.discord_bot = Data_warehouse_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting data-warehouse-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping data-warehouse-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Data_warehouse_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
