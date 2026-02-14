#!/usr/bin/env python3
# wasm-compiler-agent
# WebAssemblyコンパイラエージェント。Wasmコンパイル・ビルドの管理。

import asyncio
import logging
from db import Wasm_compiler_agentDatabase
from discord import Wasm_compiler_agentDiscordBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Wasm_compiler_agentAgent:
    # wasm-compiler-agent メインエージェント

    def __init__(self, db_path: str = "wasm-compiler-agent.db"):
        # 初期化
        self.db = Wasm_compiler_agentDatabase(db_path)
        self.discord_bot = Wasm_compiler_agentDiscordBot(self.db)

    async def run(self):
        # エージェントを実行
        logger.info("Starting wasm-compiler-agent...")
        self.db.initialize()
        await self.discord_bot.start()

    async def stop(self):
        # エージェントを停止
        logger.info("Stopping wasm-compiler-agent...")
        await self.discord_bot.stop()


async def main():
    # メイン関数
    agent = Wasm_compiler_agentAgent()
    try:
        await agent.run()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
