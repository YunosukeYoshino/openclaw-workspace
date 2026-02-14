#!/usr/bin/env python3
# baseball-team-strategy-agent
# 野球チーム戦略エージェント。チーム戦略の立案・分析。

import asyncio
import logging
from db import Baseball_team_strategy_agentDatabase
from discord import Baseball_team_strategy_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Baseball_team_strategy_agentAgent:
    # baseball-team-strategy-agent メインエージェント

    def __init__(self, db_path: str = "baseball-team-strategy-agent.db"):
        # 初期化
        self.db = Baseball_team_strategy_agentDatabase(db_path)
        self.discord_bot = Baseball_team_strategy_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting baseball-team-strategy-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping baseball-team-strategy-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Baseball_team_strategy_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
