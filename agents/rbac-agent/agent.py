#!/usr/bin/env python3
# rbac-agent
# ロールベースアクセス制御エージェント。RBACの管理・運用。

import asyncio
import logging
from db import Rbac_agentDatabase
from discord import Rbac_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Rbac_agentAgent:
    # rbac-agent メインエージェント

    def __init__(self, db_path: str = "rbac-agent.db"):
        # 初期化
        self.db = Rbac_agentDatabase(db_path)
        self.discord_bot = Rbac_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting rbac-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping rbac-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Rbac_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
