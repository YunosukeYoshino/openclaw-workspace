#!/usr/bin/env python3
# microbatch-processor-agent
# マイクロバッチ処理エージェント。マイクロバッチ処理の管理・実行。

import asyncio
import logging
from db import Microbatch_processor_agentDatabase
from discord import Microbatch_processor_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Microbatch_processor_agentAgent:
    # microbatch-processor-agent メインエージェント

    def __init__(self, db_path: str = "microbatch-processor-agent.db"):
        # 初期化
        self.db = Microbatch_processor_agentDatabase(db_path)
        self.discord_bot = Microbatch_processor_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting microbatch-processor-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping microbatch-processor-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Microbatch_processor_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
