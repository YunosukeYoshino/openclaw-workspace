#!/usr/bin/env python3
"""
baseball-analyst-summary-agent - 野球統計・分析レポートエージェント
2/25 in V34
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseballAnalystSummary:
    """baseball-analyst-summary-agent - 野球統計・分析レポートエージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "baseball-analyst-summary-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting baseball-analyst-summary-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = BaseballAnalystSummary()
    import asyncio
    asyncio.run(agent.run())
