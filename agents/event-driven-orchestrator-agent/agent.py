#!/usr/bin/env python3
"""
event-driven-orchestrator-agent - サーバーレスイベント駆動アーキテクチャエージェント
17/25 in V35
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventDrivenOrchestrator:
    """event-driven-orchestrator-agent - サーバーレスイベント駆動アーキテクチャエージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "event-driven-orchestrator-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting event-driven-orchestrator-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = EventDrivenOrchestrator()
    import asyncio
    asyncio.run(agent.run())
