#!/usr/bin/env python3
# game-live-stream-analytics-agent
# ゲームライブ配信分析エージェント。ライブ配信のデータ分析・統計。

import asyncio
import logging
from db import Game_live_stream_analytics_agentDatabase
from discord import Game_live_stream_analytics_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Game_live_stream_analytics_agentAgent:
    # game-live-stream-analytics-agent メインエージェント

    def __init__(self, db_path: str = "game-live-stream-analytics-agent.db"):
        # 初期化
        self.db = Game_live_stream_analytics_agentDatabase(db_path)
        self.discord_bot = Game_live_stream_analytics_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting game-live-stream-analytics-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping game-live-stream-analytics-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Game_live_stream_analytics_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
