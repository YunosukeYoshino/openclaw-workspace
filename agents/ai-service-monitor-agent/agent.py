#!/usr/bin/env python3
"""
ai-service-monitor-agent - AIデプロイメント・サービス管理エージェント
18/25 in V34
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AiServiceMonitor:
    """ai-service-monitor-agent - AIデプロイメント・サービス管理エージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "ai-service-monitor-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting ai-service-monitor-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = AiServiceMonitor()
    import asyncio
    asyncio.run(agent.run())
