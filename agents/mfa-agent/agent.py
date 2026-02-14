#!/usr/bin/env python3
# mfa-agent
# マルチファクタ認証エージェント。MFAの管理・運用。

import asyncio
import logging
from db import Mfa_agentDatabase
from discord import Mfa_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Mfa_agentAgent:
    # mfa-agent メインエージェント

    def __init__(self, db_path: str = "mfa-agent.db"):
        # 初期化
        self.db = Mfa_agentDatabase(db_path)
        self.discord_bot = Mfa_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting mfa-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping mfa-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Mfa_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
