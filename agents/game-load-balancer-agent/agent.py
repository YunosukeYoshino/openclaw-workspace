#!/usr/bin/env python3
"""
game-load-balancer-agent - ゲームパフォーマンス・最適化エージェント
8/25 in V34
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GameLoadBalancer:
    """game-load-balancer-agent - ゲームパフォーマンス・最適化エージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "game-load-balancer-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting game-load-balancer-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = GameLoadBalancer()
    import asyncio
    asyncio.run(agent.run())
