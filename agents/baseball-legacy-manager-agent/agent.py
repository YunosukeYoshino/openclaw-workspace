#!/usr/bin/env python3
"""
baseball-legacy-manager-agent - 野球選手キャリア・引退エージェント
5/25 in V32
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseballLegacyManager:
    """baseball-legacy-manager-agent - 野球選手キャリア・引退エージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "baseball-legacy-manager-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting baseball-legacy-manager-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = BaseballLegacyManager()
    import asyncio
    asyncio.run(agent.run())
