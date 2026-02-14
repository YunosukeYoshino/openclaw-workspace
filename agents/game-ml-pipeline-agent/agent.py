#!/usr/bin/env python3
# game-ml-pipeline-agent
# ゲーム機械学習パイプラインエージェント。MLパイプラインの管理・運用。

import asyncio
import logging
from db import Game_ml_pipeline_agentDatabase
from discord import Game_ml_pipeline_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Game_ml_pipeline_agentAgent:
    # game-ml-pipeline-agent メインエージェント

    def __init__(self, db_path: str = "game-ml-pipeline-agent.db"):
        # 初期化
        self.db = Game_ml_pipeline_agentDatabase(db_path)
        self.discord_bot = Game_ml_pipeline_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting game-ml-pipeline-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping game-ml-pipeline-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Game_ml_pipeline_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
