#!/usr/bin/env python3
# game-creators-support-agent
# ゲームクリエイターサポートエージェント。UGCクリエイターへのサポート・報酬。

import asyncio
import logging
from db import Game_creators_support_agentDatabase
from discord import Game_creators_support_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Game_creators_support_agentAgent:
    # game-creators-support-agent メインエージェント

    def __init__(self, db_path: str = "game-creators-support-agent.db"):
        # 初期化
        self.db = Game_creators_support_agentDatabase(db_path)
        self.discord_bot = Game_creators_support_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting game-creators-support-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping game-creators-support-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Game_creators_support_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
