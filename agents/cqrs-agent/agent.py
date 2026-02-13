#!/usr/bin/env python3
"""
cqrs-agent - サーバーレスイベント駆動アーキテクチャエージェント
19/25 in V35
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Cqrs:
    """cqrs-agent - サーバーレスイベント駆動アーキテクチャエージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "cqrs-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting cqrs-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = Cqrs()
    import asyncio
    asyncio.run(agent.run())
