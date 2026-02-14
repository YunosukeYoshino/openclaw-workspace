#!/usr/bin/env python3
# baseball-rehabilitation-agent
# 野球リハビリ管理エージェント。選手のリハビリテーション・回復管理。

import asyncio
import logging
from db import Baseball_rehabilitation_agentDatabase
from discord import Baseball_rehabilitation_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Baseball_rehabilitation_agentAgent:
    # baseball-rehabilitation-agent メインエージェント

    def __init__(self, db_path: str = "baseball-rehabilitation-agent.db"):
        # 初期化
        self.db = Baseball_rehabilitation_agentDatabase(db_path)
        self.discord_bot = Baseball_rehabilitation_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting baseball-rehabilitation-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping baseball-rehabilitation-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Baseball_rehabilitation_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
