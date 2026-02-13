#!/usr/bin/env python3
"""
helm-chart-manager-agent - コンテナオーケストレーション・Kubernetesエージェント
24/25 in V32
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HelmChartManager:
    """helm-chart-manager-agent - コンテナオーケストレーション・Kubernetesエージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "helm-chart-manager-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting helm-chart-manager-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = HelmChartManager()
    import asyncio
    asyncio.run(agent.run())
