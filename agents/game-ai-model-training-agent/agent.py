#!/usr/bin/env python3
# game-ai-model-training-agent
# ゲームAIモデルトレーニングエージェント。AIモデルのトレーニング・管理。

import asyncio
import logging
from db import Game_ai_model_training_agentDatabase
from discord import Game_ai_model_training_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Game_ai_model_training_agentAgent:
    # game-ai-model-training-agent メインエージェント

    def __init__(self, db_path: str = "game-ai-model-training-agent.db"):
        # 初期化
        self.db = Game_ai_model_training_agentDatabase(db_path)
        self.discord_bot = Game_ai_model_training_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting game-ai-model-training-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping game-ai-model-training-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Game_ai_model_training_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
