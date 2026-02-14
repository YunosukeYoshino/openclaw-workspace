#!/usr/bin/env python3
# baseball-player-contract-agent
# 野球選手契約管理エージェント。選手契約の管理・交渉。

import asyncio
import logging
from db import Baseball_player_contract_agentDatabase
from discord import Baseball_player_contract_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Baseball_player_contract_agentAgent:
    # baseball-player-contract-agent メインエージェント

    def __init__(self, db_path: str = "baseball-player-contract-agent.db"):
        # 初期化
        self.db = Baseball_player_contract_agentDatabase(db_path)
        self.discord_bot = Baseball_player_contract_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting baseball-player-contract-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping baseball-player-contract-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Baseball_player_contract_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
