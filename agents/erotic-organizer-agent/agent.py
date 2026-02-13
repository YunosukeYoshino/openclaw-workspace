#!/usr/bin/env python3
"""
erotic-organizer-agent - えっちコンテンツコレクション・アーカイブエージェント
13/25 in V36
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EroticOrganizer:
    """erotic-organizer-agent - えっちコンテンツコレクション・アーカイブエージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "erotic-organizer-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting erotic-organizer-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = EroticOrganizer()
    import asyncio
    asyncio.run(agent.run())
