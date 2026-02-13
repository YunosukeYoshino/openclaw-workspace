#!/usr/bin/env python3
"""
compliance-tracker-agent - データガバナンス・コンプライアンスエージェント
22/25 in V34
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComplianceTracker:
    """compliance-tracker-agent - データガバナンス・コンプライアンスエージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "compliance-tracker-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting compliance-tracker-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = ComplianceTracker()
    import asyncio
    asyncio.run(agent.run())
