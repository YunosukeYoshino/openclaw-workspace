#!/usr/bin/env python3
"""
baseball-social-media-agent - 野球メディア・コンテンツ制作エージェント
5/25 in V33
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseballSocialMedia:
    """baseball-social-media-agent - 野球メディア・コンテンツ制作エージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "baseball-social-media-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting baseball-social-media-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = BaseballSocialMedia()
    import asyncio
    asyncio.run(agent.run())
