#!/usr/bin/env python3
"""
erotic-context-aware-agent - えっちコンテンツパーソナライズ・推薦エージェント
15/25 in V32
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EroticContextAware:
    """erotic-context-aware-agent - えっちコンテンツパーソナライズ・推薦エージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "erotic-context-aware-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting erotic-context-aware-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = EroticContextAware()
    import asyncio
    asyncio.run(agent.run())
