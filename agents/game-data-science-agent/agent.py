#!/usr/bin/env python3
# game-data-science-agent
# ゲームデータサイエンスエージェント。データ分析・インサイト生成。

import asyncio
import logging
from db import Game_data_science_agentDatabase
from discord import Game_data_science_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Game_data_science_agentAgent:
    # game-data-science-agent メインエージェント

    def __init__(self, db_path: str = "game-data-science-agent.db"):
        # 初期化
        self.db = Game_data_science_agentDatabase(db_path)
        self.discord_bot = Game_data_science_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting game-data-science-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping game-data-science-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Game_data_science_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
