#!/usr/bin/env python3
# baseball-smart-stadium-agent
# 野球スマートスタジアムエージェント。スタジアムのIoT・スマート機能の管理。

import asyncio
import logging
from db import Baseball_smart_stadium_agentDatabase
from discord import Baseball_smart_stadium_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Baseball_smart_stadium_agentAgent:
    # baseball-smart-stadium-agent メインエージェント

    def __init__(self, db_path: str = "baseball-smart-stadium-agent.db"):
        # 初期化
        self.db = Baseball_smart_stadium_agentDatabase(db_path)
        self.discord_bot = Baseball_smart_stadium_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting baseball-smart-stadium-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping baseball-smart-stadium-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Baseball_smart_stadium_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
