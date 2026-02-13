#!/usr/bin/env python3
"""
game-voice-chat-agent - ゲームクロスプレイ・マルチプラットフォームエージェント
9/25 in V36
"""

import logging
from pathlib import Path
from .db import Database
from .discord import DiscordHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GameVoiceChat:
    """game-voice-chat-agent - ゲームクロスプレイ・マルチプラットフォームエージェント"""

    def __init__(self, db_path: str = None, discord_token: str = None):
        self.db = Database(db_path or str(Path(__file__).parent / "game-voice-chat-agent.db"))
        self.discord = DiscordHandler(discord_token)

    async def run(self):
        """メイン実行ループ"""
        logger.info("Starting game-voice-chat-agent...")
        await self.discord.start()

if __name__ == "__main__":
    agent = GameVoiceChat()
    import asyncio
    asyncio.run(agent.run())
