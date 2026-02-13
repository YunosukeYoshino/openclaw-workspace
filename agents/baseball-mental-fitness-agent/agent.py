#!/usr/bin/env python3
"""
baseball-mental-fitness-agent - 野球選手健康管理・フィジカルエージェント
3/25 in V36
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseballMentalFitness:
    """baseball-mental-fitness-agent - 野球選手健康管理・フィジカルエージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "baseball-mental-fitness-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting baseball-mental-fitness-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = BaseballMentalFitness()
    import asyncio
    asyncio.run(agent.run())
