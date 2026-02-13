#!/usr/bin/env python3
"""
baseball-career-tracker-agent - 野球選手キャリア・引退エージェント
1/25 in V32
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseballCareerTracker:
    """baseball-career-tracker-agent - 野球選手キャリア・引退エージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "baseball-career-tracker-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting baseball-career-tracker-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = BaseballCareerTracker()
    import asyncio
    asyncio.run(agent.run())
