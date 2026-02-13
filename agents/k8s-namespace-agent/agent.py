#!/usr/bin/env python3
"""
k8s-namespace-agent - コンテナオーケストレーション・Kubernetesエージェント
25/25 in V32
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class K8sNamespace:
    """k8s-namespace-agent - コンテナオーケストレーション・Kubernetesエージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "k8s-namespace-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting k8s-namespace-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = K8sNamespace()
    import asyncio
    asyncio.run(agent.run())
