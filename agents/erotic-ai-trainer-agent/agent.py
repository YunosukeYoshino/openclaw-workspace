#!/usr/bin/env python3
"""
erotic-ai-trainer-agent - えっちコンテンツAIトレーニング・モデル管理エージェント
11/25 in V33
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EroticAiTrainer:
    """erotic-ai-trainer-agent - えっちコンテンツAIトレーニング・モデル管理エージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "erotic-ai-trainer-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting erotic-ai-trainer-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = EroticAiTrainer()
    import asyncio
    asyncio.run(agent.run())
