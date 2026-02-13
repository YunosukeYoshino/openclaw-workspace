#!/usr/bin/env python3
"""
cloud-event-handler-agent - サーバーレス・クラウドネイティブエージェント
17/25 in V33
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CloudEventHandler:
    """cloud-event-handler-agent - サーバーレス・クラウドネイティブエージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "cloud-event-handler-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting cloud-event-handler-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = CloudEventHandler()
    import asyncio
    asyncio.run(agent.run())
