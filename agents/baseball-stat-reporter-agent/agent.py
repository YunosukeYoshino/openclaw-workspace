#!/usr/bin/env python3
"""
baseball-stat-reporter-agent - 野球統計・分析レポートエージェント
1/25 in V34
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseballStatReporter:
    """baseball-stat-reporter-agent - 野球統計・分析レポートエージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "baseball-stat-reporter-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting baseball-stat-reporter-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = BaseballStatReporter()
    import asyncio
    asyncio.run(agent.run())
