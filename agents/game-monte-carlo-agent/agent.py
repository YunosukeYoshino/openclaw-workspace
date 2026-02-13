#!/usr/bin/env python3
"""
game-monte-carlo-agent - ゲームモデリング・シミュレーションエージェント
9/25 in V35
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GameMonteCarlo:
    """game-monte-carlo-agent - ゲームモデリング・シミュレーションエージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "game-monte-carlo-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting game-monte-carlo-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = GameMonteCarlo()
    import asyncio
    asyncio.run(agent.run())
