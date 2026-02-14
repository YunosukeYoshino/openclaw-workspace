#!/usr/bin/env python3
# erotic-privacy-control-agent
# えっちプライバシーコントロールエージェント。ユーザープライバシー設定の管理。

import asyncio
import logging
from db import Erotic_privacy_control_agentDatabase
from discord import Erotic_privacy_control_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Erotic_privacy_control_agentAgent:
    # erotic-privacy-control-agent メインエージェント

    def __init__(self, db_path: str = "erotic-privacy-control-agent.db"):
        # 初期化
        self.db = Erotic_privacy_control_agentDatabase(db_path)
        self.discord_bot = Erotic_privacy_control_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting erotic-privacy-control-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping erotic-privacy-control-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Erotic_privacy_control_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
