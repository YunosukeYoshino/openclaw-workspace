#!/usr/bin/env python3
"""
game-achievement-sync-agent - ゲームクロスプレイ・マルチプラットフォームエージェント
8/25 in V36
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GameAchievementSync:
    """game-achievement-sync-agent - ゲームクロスプレイ・マルチプラットフォームエージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "game-achievement-sync-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting game-achievement-sync-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = GameAchievementSync()
    import asyncio
    asyncio.run(agent.run())
