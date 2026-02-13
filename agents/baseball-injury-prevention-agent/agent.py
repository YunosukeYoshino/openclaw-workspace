#!/usr/bin/env python3
"""
baseball-injury-prevention-agent - 野球選手健康管理・フィジカルエージェント
5/25 in V36
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseballInjuryPrevention:
    """baseball-injury-prevention-agent - 野球選手健康管理・フィジカルエージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "baseball-injury-prevention-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting baseball-injury-prevention-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = BaseballInjuryPrevention()
    import asyncio
    asyncio.run(agent.run())
