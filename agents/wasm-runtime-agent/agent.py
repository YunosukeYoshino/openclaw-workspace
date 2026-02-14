#!/usr/bin/env python3
# wasm-runtime-agent
# WebAssemblyランタイムエージェント。Wasmランタイムの管理・最適化。

import asyncio
import logging
from db import Wasm_runtime_agentDatabase
from discord import Wasm_runtime_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Wasm_runtime_agentAgent:
    # wasm-runtime-agent メインエージェント

    def __init__(self, db_path: str = "wasm-runtime-agent.db"):
        # 初期化
        self.db = Wasm_runtime_agentDatabase(db_path)
        self.discord_bot = Wasm_runtime_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting wasm-runtime-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping wasm-runtime-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Wasm_runtime_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
