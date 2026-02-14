#!/usr/bin/env python3
# game-marketplace-agent
# ゲームマーケットプレイスエージェント。ゲーム内マーケットプレイスの運営・管理。

import asyncio
import logging
from db import Game_marketplace_agentDatabase
from discord import Game_marketplace_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Game_marketplace_agentAgent:
    # game-marketplace-agent メインエージェント

    def __init__(self, db_path: str = "game-marketplace-agent.db"):
        # 初期化
        self.db = Game_marketplace_agentDatabase(db_path)
        self.discord_bot = Game_marketplace_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting game-marketplace-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping game-marketplace-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Game_marketplace_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
