#!/usr/bin/env python3
# api-gateway-v2-agent
# APIゲートウェイV2エージェント。APIゲートウェイの管理・運用。

import asyncio
import logging
from db import Api_gateway_v2_agentDatabase
from discord import Api_gateway_v2_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Api_gateway_v2_agentAgent:
    # api-gateway-v2-agent メインエージェント

    def __init__(self, db_path: str = "api-gateway-v2-agent.db"):
        # 初期化
        self.db = Api_gateway_v2_agentDatabase(db_path)
        self.discord_bot = Api_gateway_v2_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting api-gateway-v2-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping api-gateway-v2-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Api_gateway_v2_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
