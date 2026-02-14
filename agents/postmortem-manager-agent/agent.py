#!/usr/bin/env python3
# postmortem-manager-agent
# ポストモーテム管理エージェント。事後分析・レポート作成。

import asyncio
import logging
from db import Postmortem_manager_agentDatabase
from discord import Postmortem_manager_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Postmortem_manager_agentAgent:
    # postmortem-manager-agent メインエージェント

    def __init__(self, db_path: str = "postmortem-manager-agent.db"):
        # 初期化
        self.db = Postmortem_manager_agentDatabase(db_path)
        self.discord_bot = Postmortem_manager_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting postmortem-manager-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping postmortem-manager-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Postmortem_manager_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
