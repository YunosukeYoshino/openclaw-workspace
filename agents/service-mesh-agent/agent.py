#!/usr/bin/env python3
# service-mesh-agent
# サービスメッシュエージェント。サービスメッシュの管理・運用。

import asyncio
import logging
from db import Service_mesh_agentDatabase
from discord import Service_mesh_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Service_mesh_agentAgent:
    # service-mesh-agent メインエージェント

    def __init__(self, db_path: str = "service-mesh-agent.db"):
        # 初期化
        self.db = Service_mesh_agentDatabase(db_path)
        self.discord_bot = Service_mesh_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting service-mesh-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping service-mesh-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Service_mesh_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
