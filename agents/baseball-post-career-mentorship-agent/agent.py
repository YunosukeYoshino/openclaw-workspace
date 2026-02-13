#!/usr/bin/env python3
"""
baseball-post-career-mentorship-agent - 野球選手キャリア・引退エージェント
3/25 in V32
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseballPostCareerMentorship:
    """baseball-post-career-mentorship-agent - 野球選手キャリア・引退エージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "baseball-post-career-mentorship-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting baseball-post-career-mentorship-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = BaseballPostCareerMentorship()
    import asyncio
    asyncio.run(agent.run())
