#!/usr/bin/env python3
# pwa-builder-agent
# PWAビルダーエージェント。プログレッシブWebアプリのビルド・管理。

import asyncio
import logging
from db import Pwa_builder_agentDatabase
from discord import Pwa_builder_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Pwa_builder_agentAgent:
    # pwa-builder-agent メインエージェント

    def __init__(self, db_path: str = "pwa-builder-agent.db"):
        # 初期化
        self.db = Pwa_builder_agentDatabase(db_path)
        self.discord_bot = Pwa_builder_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting pwa-builder-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping pwa-builder-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Pwa_builder_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
