#!/usr/bin/env python3
# threat-simulation-agent
# 脅威シミュレーションエージェント。攻撃シミュレーション・テスト。

import asyncio
import logging
from db import Threat_simulation_agentDatabase
from discord import Threat_simulation_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Threat_simulation_agentAgent:
    # threat-simulation-agent メインエージェント

    def __init__(self, db_path: str = "threat-simulation-agent.db"):
        # 初期化
        self.db = Threat_simulation_agentDatabase(db_path)
        self.discord_bot = Threat_simulation_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting threat-simulation-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping threat-simulation-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Threat_simulation_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
