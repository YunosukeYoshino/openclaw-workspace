#!/usr/bin/env python3
"""
oauth-manager-agent - セキュリティ認証・認可管理エージェント
22/25 in V35
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OauthManager:
    """oauth-manager-agent - セキュリティ認証・認可管理エージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "oauth-manager-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting oauth-manager-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = OauthManager()
    import asyncio
    asyncio.run(agent.run())
