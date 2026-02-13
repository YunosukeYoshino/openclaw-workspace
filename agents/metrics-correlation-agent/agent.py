#!/usr/bin/env python3
"""
metrics-correlation-agent - 分散トレーシング・オブザーバビリティエージェント
20/25 in V32
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetricsCorrelation:
    """metrics-correlation-agent - 分散トレーシング・オブザーバビリティエージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "metrics-correlation-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting metrics-correlation-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = MetricsCorrelation()
    import asyncio
    asyncio.run(agent.run())
