#!/usr/bin/env python3
# game-virtual-item-agent
# ゲームバーチャルアイテムエージェント。バーチャルアイテムの管理・取引。

import asyncio
import logging
from db import Game_virtual_item_agentDatabase
from discord import Game_virtual_item_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Game_virtual_item_agentAgent:
    # game-virtual-item-agent メインエージェント

    def __init__(self, db_path: str = "game-virtual-item-agent.db"):
        # 初期化
        self.db = Game_virtual_item_agentDatabase(db_path)
        self.discord_bot = Game_virtual_item_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting game-virtual-item-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping game-virtual-item-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Game_virtual_item_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
