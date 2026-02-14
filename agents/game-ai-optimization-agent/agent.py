#!/usr/bin/env python3
# game-ai-optimization-agent
# ゲームAI最適化エージェント。AIの最適化・パフォーマンス改善。

import asyncio
import logging
from db import Game_ai_optimization_agentDatabase
from discord import Game_ai_optimization_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Game_ai_optimization_agentAgent:
    # game-ai-optimization-agent メインエージェント

    def __init__(self, db_path: str = "game-ai-optimization-agent.db"):
        # 初期化
        self.db = Game_ai_optimization_agentDatabase(db_path)
        self.discord_bot = Game_ai_optimization_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting game-ai-optimization-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping game-ai-optimization-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Game_ai_optimization_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
