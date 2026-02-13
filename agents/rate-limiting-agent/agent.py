#!/usr/bin/env python3
"""
rate-limiting-agent - マイクロサービス・サービスメッシュエージェント
19/25 in V36
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RateLimiting:
    """rate-limiting-agent - マイクロサービス・サービスメッシュエージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "rate-limiting-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting rate-limiting-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = RateLimiting()
    import asyncio
    asyncio.run(agent.run())
