#!/usr/bin/env python3
# game-stream-audience-agent
# ゲーム配信視聴者管理エージェント。視聴者の管理・分析・エンゲージメント。

import asyncio
import logging
from db import Game_stream_audience_agentDatabase
from discord import Game_stream_audience_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Game_stream_audience_agentAgent:
    # game-stream-audience-agent メインエージェント

    def __init__(self, db_path: str = "game-stream-audience-agent.db"):
        # 初期化
        self.db = Game_stream_audience_agentDatabase(db_path)
        self.discord_bot = Game_stream_audience_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting game-stream-audience-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping game-stream-audience-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Game_stream_audience_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
