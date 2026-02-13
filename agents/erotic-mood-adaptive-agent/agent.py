#!/usr/bin/env python3
"""
erotic-mood-adaptive-agent - えっちコンテンツパーソナライズ・推薦エージェント
13/25 in V32
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EroticMoodAdaptive:
    """erotic-mood-adaptive-agent - えっちコンテンツパーソナライズ・推薦エージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "erotic-mood-adaptive-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting erotic-mood-adaptive-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = EroticMoodAdaptive()
    import asyncio
    asyncio.run(agent.run())
