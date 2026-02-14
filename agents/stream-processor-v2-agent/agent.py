#!/usr/bin/env python3
# stream-processor-v2-agent
# ストリーム処理V2エージェント。リアルタイムストリーム処理の管理。

import asyncio
import logging
from db import Stream_processor_v2_agentDatabase
from discord import Stream_processor_v2_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Stream_processor_v2_agentAgent:
    # stream-processor-v2-agent メインエージェント

    def __init__(self, db_path: str = "stream-processor-v2-agent.db"):
        # 初期化
        self.db = Stream_processor_v2_agentDatabase(db_path)
        self.discord_bot = Stream_processor_v2_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting stream-processor-v2-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping stream-processor-v2-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Stream_processor_v2_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
