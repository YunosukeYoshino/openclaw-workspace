#!/usr/bin/env python3
# security-patch-agent
# セキュリティパッチエージェント。セキュリティパッチの管理・適用。

import asyncio
import logging
from db import Security_patch_agentDatabase
from discord import Security_patch_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Security_patch_agentAgent:
    # security-patch-agent メインエージェント

    def __init__(self, db_path: str = "security-patch-agent.db"):
        # 初期化
        self.db = Security_patch_agentDatabase(db_path)
        self.discord_bot = Security_patch_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting security-patch-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping security-patch-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Security_patch_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
