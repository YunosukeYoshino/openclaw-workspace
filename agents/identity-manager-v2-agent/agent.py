#!/usr/bin/env python3
# identity-manager-v2-agent
# アイデンティティ管理V2エージェント。デジタルアイデンティティの管理・制御。

import asyncio
import logging
from db import Identity_manager_v2_agentDatabase
from discord import Identity_manager_v2_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Identity_manager_v2_agentAgent:
    # identity-manager-v2-agent メインエージェント

    def __init__(self, db_path: str = "identity-manager-v2-agent.db"):
        # 初期化
        self.db = Identity_manager_v2_agentDatabase(db_path)
        self.discord_bot = Identity_manager_v2_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting identity-manager-v2-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping identity-manager-v2-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Identity_manager_v2_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
