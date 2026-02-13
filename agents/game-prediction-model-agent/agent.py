#!/usr/bin/env python3
"""
game-prediction-model-agent - ゲームモデリング・シミュレーションエージェント
10/25 in V35
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GamePredictionModel:
    """game-prediction-model-agent - ゲームモデリング・シミュレーションエージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "game-prediction-model-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting game-prediction-model-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = GamePredictionModel()
    import asyncio
    asyncio.run(agent.run())
