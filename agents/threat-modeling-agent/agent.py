#!/usr/bin/env python3
# threat-modeling-agent
# 脅威モデリングエージェント。脅威モデルの作成・分析。

import asyncio
import logging
from db import Threat_modeling_agentDatabase
from discord import Threat_modeling_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Threat_modeling_agentAgent:
    # threat-modeling-agent メインエージェント

    def __init__(self, db_path: str = "threat-modeling-agent.db"):
        # 初期化
        self.db = Threat_modeling_agentDatabase(db_path)
        self.discord_bot = Threat_modeling_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting threat-modeling-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping threat-modeling-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Threat_modeling_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
