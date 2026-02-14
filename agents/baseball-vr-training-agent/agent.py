#!/usr/bin/env python3
# baseball-vr-training-agent
# 野球VRトレーニングエージェント。VRを活用したトレーニングプログラムの管理。

import asyncio
import logging
from db import Baseball_vr_training_agentDatabase
from discord import Baseball_vr_training_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Baseball_vr_training_agentAgent:
    # baseball-vr-training-agent メインエージェント

    def __init__(self, db_path: str = "baseball-vr-training-agent.db"):
        # 初期化
        self.db = Baseball_vr_training_agentDatabase(db_path)
        self.discord_bot = Baseball_vr_training_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting baseball-vr-training-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping baseball-vr-training-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Baseball_vr_training_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
