#!/usr/bin/env python3
# baseball-team-marketing-agent
# 野球チームマーケティングエージェント。チームマーケティングの企画・実行。

import asyncio
import logging
from db import Baseball_team_marketing_agentDatabase
from discord import Baseball_team_marketing_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Baseball_team_marketing_agentAgent:
    # baseball-team-marketing-agent メインエージェント

    def __init__(self, db_path: str = "baseball-team-marketing-agent.db"):
        # 初期化
        self.db = Baseball_team_marketing_agentDatabase(db_path)
        self.discord_bot = Baseball_team_marketing_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting baseball-team-marketing-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping baseball-team-marketing-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Baseball_team_marketing_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
