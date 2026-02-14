#!/usr/bin/env python3
# security-reporter-agent
# セキュリティレポーターエージェント。セキュリティレポートの生成・配信。

import asyncio
import logging
from db import Security_reporter_agentDatabase
from discord import Security_reporter_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Security_reporter_agentAgent:
    # security-reporter-agent メインエージェント

    def __init__(self, db_path: str = "security-reporter-agent.db"):
        # 初期化
        self.db = Security_reporter_agentDatabase(db_path)
        self.discord_bot = Security_reporter_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting security-reporter-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping security-reporter-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Security_reporter_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
