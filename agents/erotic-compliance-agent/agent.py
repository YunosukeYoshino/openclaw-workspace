#!/usr/bin/env python3
# erotic-compliance-agent
# えっちコンテンツコンプライアンスエージェント。法的コンプライアンスの管理・監査。

import asyncio
import logging
from db import Erotic_compliance_agentDatabase
from discord import Erotic_compliance_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Erotic_compliance_agentAgent:
    # erotic-compliance-agent メインエージェント

    def __init__(self, db_path: str = "erotic-compliance-agent.db"):
        # 初期化
        self.db = Erotic_compliance_agentDatabase(db_path)
        self.discord_bot = Erotic_compliance_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting erotic-compliance-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping erotic-compliance-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Erotic_compliance_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
