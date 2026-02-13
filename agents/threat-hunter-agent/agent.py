#!/usr/bin/env python3
"""
threat-hunter-agent - セキュリティインシデント・脅威対応エージェント
22/25 in V33
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThreatHunter:
    """threat-hunter-agent - セキュリティインシデント・脅威対応エージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "threat-hunter-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting threat-hunter-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = ThreatHunter()
    import asyncio
    asyncio.run(agent.run())
