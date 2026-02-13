#!/usr/bin/env python3
"""
observability-collector-agent - 分散トレーシング・オブザーバビリティエージェント
17/25 in V32
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ObservabilityCollector:
    """observability-collector-agent - 分散トレーシング・オブザーバビリティエージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "observability-collector-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting observability-collector-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = ObservabilityCollector()
    import asyncio
    asyncio.run(agent.run())
