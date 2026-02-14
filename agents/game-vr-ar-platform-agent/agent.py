#!/usr/bin/env python3
# game-vr-ar-platform-agent
# ゲームVR・ARプラットフォームエージェント。VR・ARプラットフォームの運営・管理。

import asyncio
import logging
from db import Game_vr_ar_platform_agentDatabase
from discord import Game_vr_ar_platform_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Game_vr_ar_platform_agentAgent:
    # game-vr-ar-platform-agent メインエージェント

    def __init__(self, db_path: str = "game-vr-ar-platform-agent.db"):
        # 初期化
        self.db = Game_vr_ar_platform_agentDatabase(db_path)
        self.discord_bot = Game_vr_ar_platform_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting game-vr-ar-platform-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping game-vr-ar-platform-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Game_vr_ar_platform_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
