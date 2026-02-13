#!/usr/bin/env python3
"""
security-dashboard-agent - セキュリティインシデント・脅威対応エージェント
25/25 in V33
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityDashboard:
    """security-dashboard-agent - セキュリティインシデント・脅威対応エージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "security-dashboard-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting security-dashboard-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = SecurityDashboard()
    import asyncio
    asyncio.run(agent.run())
