#!/usr/bin/env python3
"""
service-mesh-agent - マイクロサービス・サービスメッシュエージェント
17/25 in V36
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceMesh:
    """service-mesh-agent - マイクロサービス・サービスメッシュエージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "service-mesh-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting service-mesh-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = ServiceMesh()
    import asyncio
    asyncio.run(agent.run())
