#!/usr/bin/env python3
# observability-monitor-agent
# オブザーバビリティモニターエージェント。システムの可視化・監視。

import asyncio
import logging
from db import Observability_monitor_agentDatabase
from discord import Observability_monitor_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Observability_monitor_agentAgent:
    # observability-monitor-agent メインエージェント

    def __init__(self, db_path: str = "observability-monitor-agent.db"):
        # 初期化
        self.db = Observability_monitor_agentDatabase(db_path)
        self.discord_bot = Observability_monitor_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting observability-monitor-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping observability-monitor-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Observability_monitor_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
