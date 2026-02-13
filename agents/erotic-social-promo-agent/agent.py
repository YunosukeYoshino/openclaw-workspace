#!/usr/bin/env python3
"""
erotic-social-promo-agent - えっちコンテンツコンテンツマーケティングエージェント
13/25 in V34
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EroticSocialPromo:
    """erotic-social-promo-agent - えっちコンテンツコンテンツマーケティングエージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "erotic-social-promo-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting erotic-social-promo-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = EroticSocialPromo()
    import asyncio
    asyncio.run(agent.run())
