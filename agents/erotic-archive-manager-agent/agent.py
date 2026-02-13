#!/usr/bin/env python3
"""
erotic-archive-manager-agent - えっちコンテンツコレクション・アーカイブエージェント
11/25 in V36
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EroticArchiveManager:
    """erotic-archive-manager-agent - えっちコンテンツコレクション・アーカイブエージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "erotic-archive-manager-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting erotic-archive-manager-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = EroticArchiveManager()
    import asyncio
    asyncio.run(agent.run())
