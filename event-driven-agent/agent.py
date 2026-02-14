#!/usr/bin/env python3
"""
event-driven-agent - イベント駆動エージェント。イベント駆動アーキテクチャの管理。
"""

import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime

# エージェントディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from db import EventDrivenAgentDatabase
from discord import EventDrivenAgentDiscordBot


class EventDrivenAgentAgent:
    """イベント駆動エージェント。イベント駆動アーキテクチャの管理。"""

    def __init__(self, config_path=None):
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), "config.json")
        self.db = EventDrivenAgentDatabase(self.config_path)
        self.discord = EventDrivenAgentDiscordBot(self.config_path)
        self.name = "event-driven-agent"
        self.version = "1.0.0"
        self.status = "idle"

    async def start(self):
        """エージェントを開始"""
        self.status = "running"
        print(f"[{self.name}] 開始 (v{self.version})")
        await self.discord.start()

    async def stop(self):
        """エージェントを停止"""
        self.status = "stopped"
        print(f"[{self.name}] 停止")
        await self.discord.stop()

    async def run_task(self, task_data):
        """タスクを実行"""
        try:
            task_type = task_data.get("type")
            task_params = task_data.get("params", {})

            if task_type == "event-driven-agent":
                result = await self._event_driven_agent(**task_params)
                return {"success": True, "result": result}
            else:
                return {"success": False, "error": "未知のタスクタイプ"}

        except Exception as e:
            print(f"[{self.name}] タスク実行エラー: {e}")
            return {"success": False, "error": str(e)}

    async def _event_driven_agent(self, **params):
        """イベント駆動エージェント。イベント駆動アーキテクチャの管理。のメイン処理"""
        # TODO: 実装を追加
        result = {"message": "イベント駆動エージェント。イベント駆動アーキテクチャの管理。処理完了", "params": params}
        return result


async def main():
    """メインエントリーポイント"""
    agent = EventDrivenAgentAgent()
    try:
        await agent.start()
    except KeyboardInterrupt:
        print("\nシャットダウン中...")
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
