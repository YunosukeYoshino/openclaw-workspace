#!/usr/bin/env python3
"""
game-ux-designer-agent - ゲームユーザーリサーチ・UXエージェント
9/25 in V33
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GameUxDesigner:
    """game-ux-designer-agent - ゲームユーザーリサーチ・UXエージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "game-ux-designer-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting game-ux-designer-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = GameUxDesigner()
    import asyncio
    asyncio.run(agent.run())
