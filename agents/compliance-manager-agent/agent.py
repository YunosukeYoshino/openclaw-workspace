#!/usr/bin/env python3
# compliance-manager-agent
# コンプライアンス管理エージェント。コンプライアンスの管理・監視。

import asyncio
import logging
from db import Compliance_manager_agentDatabase
from discord import Compliance_manager_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Compliance_manager_agentAgent:
    # compliance-manager-agent メインエージェント

    def __init__(self, db_path: str = "compliance-manager-agent.db"):
        # 初期化
        self.db = Compliance_manager_agentDatabase(db_path)
        self.discord_bot = Compliance_manager_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting compliance-manager-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping compliance-manager-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Compliance_manager_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
