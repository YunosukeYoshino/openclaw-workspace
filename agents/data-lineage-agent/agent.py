#!/usr/bin/env python3
"""
data-lineage-agent - データガバナンス・コンプライアンスエージェント
23/25 in V34
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLineage:
    """data-lineage-agent - データガバナンス・コンプライアンスエージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "data-lineage-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting data-lineage-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = DataLineage()
    import asyncio
    asyncio.run(agent.run())
