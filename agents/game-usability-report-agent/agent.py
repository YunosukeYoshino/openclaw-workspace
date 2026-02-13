#!/usr/bin/env python3
"""
game-usability-report-agent - ゲームユーザーリサーチ・UXエージェント
10/25 in V33
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GameUsabilityReport:
    """game-usability-report-agent - ゲームユーザーリサーチ・UXエージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "game-usability-report-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting game-usability-report-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = GameUsabilityReport()
    import asyncio
    asyncio.run(agent.run())
