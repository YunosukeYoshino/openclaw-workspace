#!/usr/bin/env python3
# audit-manager-agent
# 監査管理エージェント。監査の計画・実施・レポート。

import asyncio
import logging
from db import Audit_manager_agentDatabase
from discord import Audit_manager_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Audit_manager_agentAgent:
    # audit-manager-agent メインエージェント

    def __init__(self, db_path: str = "audit-manager-agent.db"):
        # 初期化
        self.db = Audit_manager_agentDatabase(db_path)
        self.discord_bot = Audit_manager_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting audit-manager-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping audit-manager-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Audit_manager_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
