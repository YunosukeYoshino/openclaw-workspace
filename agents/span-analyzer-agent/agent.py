#!/usr/bin/env python3
"""
span-analyzer-agent - 分散トレーシング・オブザーバビリティエージェント
18/25 in V32
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpanAnalyzer:
    """span-analyzer-agent - 分散トレーシング・オブザーバビリティエージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "span-analyzer-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting span-analyzer-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = SpanAnalyzer()
    import asyncio
    asyncio.run(agent.run())
