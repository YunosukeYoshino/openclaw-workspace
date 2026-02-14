#!/usr/bin/env python3
# sso-agent
# シングルサインオンエージェント。SSOの管理・運用。

import asyncio
import logging
from db import Sso_agentDatabase
from discord import Sso_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Sso_agentAgent:
    # sso-agent メインエージェント

    def __init__(self, db_path: str = "sso-agent.db"):
        # 初期化
        self.db = Sso_agentDatabase(db_path)
        self.discord_bot = Sso_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting sso-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping sso-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Sso_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
