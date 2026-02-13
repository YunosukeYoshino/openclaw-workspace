#!/usr/bin/env python3
"""
microservice-discovery-agent - マイクロサービス・サービスメッシュエージェント
16/25 in V36
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MicroserviceDiscovery:
    """microservice-discovery-agent - マイクロサービス・サービスメッシュエージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "microservice-discovery-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting microservice-discovery-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = MicroserviceDiscovery()
    import asyncio
    asyncio.run(agent.run())
