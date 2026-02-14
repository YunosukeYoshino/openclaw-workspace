#!/usr/bin/env python3
# trace-manager-agent
# トレース管理エージェント。分散トレースの管理・可視化。

import asyncio
import logging
from db import Trace_manager_agentDatabase
from discord import Trace_manager_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Trace_manager_agentAgent:
    # trace-manager-agent メインエージェント

    def __init__(self, db_path: str = "trace-manager-agent.db"):
        # 初期化
        self.db = Trace_manager_agentDatabase(db_path)
        self.discord_bot = Trace_manager_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting trace-manager-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping trace-manager-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Trace_manager_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
