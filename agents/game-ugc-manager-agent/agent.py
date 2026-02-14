#!/usr/bin/env python3
# game-ugc-manager-agent
# ゲームUGCマネージャーエージェント。ユーザー生成コンテンツの管理・キュレーション。

import asyncio
import logging
from db import Game_ugc_manager_agentDatabase
from discord import Game_ugc_manager_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Game_ugc_manager_agentAgent:
    # game-ugc-manager-agent メインエージェント

    def __init__(self, db_path: str = "game-ugc-manager-agent.db"):
        # 初期化
        self.db = Game_ugc_manager_agentDatabase(db_path)
        self.discord_bot = Game_ugc_manager_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting game-ugc-manager-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping game-ugc-manager-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Game_ugc_manager_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
