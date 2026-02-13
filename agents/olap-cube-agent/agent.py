#!/usr/bin/env python3
"""
olap-cube-agent - データウェアハウス・BIエージェント
23/25 in V36
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OlapCube:
    """olap-cube-agent - データウェアハウス・BIエージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "olap-cube-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting olap-cube-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = OlapCube()
    import asyncio
    asyncio.run(agent.run())
