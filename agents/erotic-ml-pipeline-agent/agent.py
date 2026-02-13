#!/usr/bin/env python3
"""
erotic-ml-pipeline-agent - えっちコンテンツAIトレーニング・モデル管理エージェント
15/25 in V33
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EroticMlPipeline:
    """erotic-ml-pipeline-agent - えっちコンテンツAIトレーニング・モデル管理エージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "erotic-ml-pipeline-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting erotic-ml-pipeline-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = EroticMlPipeline()
    import asyncio
    asyncio.run(agent.run())
