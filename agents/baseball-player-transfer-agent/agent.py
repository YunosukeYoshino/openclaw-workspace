#!/usr/bin/env python3
# baseball-player-transfer-agent
# 野球選手移籍管理エージェント。選手移籍・トレードの管理。

import asyncio
import logging
from db import Baseball_player_transfer_agentDatabase
from discord import Baseball_player_transfer_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Baseball_player_transfer_agentAgent:
    # baseball-player-transfer-agent メインエージェント

    def __init__(self, db_path: str = "baseball-player-transfer-agent.db"):
        # 初期化
        self.db = Baseball_player_transfer_agentDatabase(db_path)
        self.discord_bot = Baseball_player_transfer_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting baseball-player-transfer-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping baseball-player-transfer-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Baseball_player_transfer_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
