#!/usr/bin/env python3
"""
baseball-trend-analyzer-agent - 野球統計・分析レポートエージェント
4/25 in V34
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseballTrendAnalyzer:
    """baseball-trend-analyzer-agent - 野球統計・分析レポートエージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "baseball-trend-analyzer-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting baseball-trend-analyzer-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = BaseballTrendAnalyzer()
    import asyncio
    asyncio.run(agent.run())
