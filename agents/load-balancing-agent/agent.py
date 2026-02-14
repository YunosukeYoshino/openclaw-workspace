#!/usr/bin/env python3
# load-balancing-agent
# ロードバランシングエージェント。ロードバランシングの管理・最適化。

import asyncio
import logging
from db import Load_balancing_agentDatabase
from discord import Load_balancing_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Load_balancing_agentAgent:
    # load-balancing-agent メインエージェント

    def __init__(self, db_path: str = "load-balancing-agent.db"):
        # 初期化
        self.db = Load_balancing_agentDatabase(db_path)
        self.discord_bot = Load_balancing_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting load-balancing-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping load-balancing-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Load_balancing_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
