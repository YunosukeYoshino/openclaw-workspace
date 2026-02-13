#!/usr/bin/env python3
"""
game-perf-tuning-agent - ゲームパフォーマンス・最適化エージェント
10/25 in V34
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GamePerfTuning:
    """game-perf-tuning-agent - ゲームパフォーマンス・最適化エージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "game-perf-tuning-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting game-perf-tuning-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = GamePerfTuning()
    import asyncio
    asyncio.run(agent.run())
