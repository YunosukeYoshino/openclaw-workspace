#!/usr/bin/env python3
"""
baseball-scoreboard-agent - 野球ライブ中継・コメンタリーエージェント
5/25 in V35
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseballScoreboard:
    """baseball-scoreboard-agent - 野球ライブ中継・コメンタリーエージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "baseball-scoreboard-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting baseball-scoreboard-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = BaseballScoreboard()
    import asyncio
    asyncio.run(agent.run())
