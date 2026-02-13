#!/usr/bin/env python3
"""
erotic-collab-platform-agent - えっちコンテンツクリエイターコミュニティツールエージェント
12/25 in V35
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EroticCollabPlatform:
    """erotic-collab-platform-agent - えっちコンテンツクリエイターコミュニティツールエージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "erotic-collab-platform-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting erotic-collab-platform-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = EroticCollabPlatform()
    import asyncio
    asyncio.run(agent.run())
