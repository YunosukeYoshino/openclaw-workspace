#!/usr/bin/env python3
"""
game-visual-effects-agent - ゲームアセット・リソース管理エージェント
10/25 in V32
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GameVisualEffects:
    """game-visual-effects-agent - ゲームアセット・リソース管理エージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "game-visual-effects-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting game-visual-effects-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = GameVisualEffects()
    import asyncio
    asyncio.run(agent.run())
