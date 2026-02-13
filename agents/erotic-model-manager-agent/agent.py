#!/usr/bin/env python3
"""
erotic-model-manager-agent - えっちコンテンツAIトレーニング・モデル管理エージェント
12/25 in V33
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EroticModelManager:
    """erotic-model-manager-agent - えっちコンテンツAIトレーニング・モデル管理エージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "erotic-model-manager-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting erotic-model-manager-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = EroticModelManager()
    import asyncio
    asyncio.run(agent.run())
