#!/usr/bin/env python3
"""
container-health-agent - コンテナオーケストレーション・Kubernetesエージェント
22/25 in V32
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContainerHealth:
    """container-health-agent - コンテナオーケストレーション・Kubernetesエージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "container-health-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting container-health-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = ContainerHealth()
    import asyncio
    asyncio.run(agent.run())
