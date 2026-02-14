#!/usr/bin/env python3
"""
event-sourcing-agent - イベントソーシングエージェント。イベントソーシングの実装。
"""

import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime

# エージェントディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from db import EventSourcingAgentDatabase
from discord import EventSourcingAgentDiscordBot


class EventSourcingAgentAgent:
    """イベントソーシングエージェント。イベントソーシングの実装。"""

    def __init__(self, config_path=None):
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), "config.json")
        self.db = EventSourcingAgentDatabase(self.config_path)
        self.discord = EventSourcingAgentDiscordBot(self.config_path)
        self.name = "event-sourcing-agent"
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

            if task_type == "event-sourcing-agent":
                result = await self._event_sourcing_agent(**task_params)
                return {"success": True, "result": result}
            else:
                return {"success": False, "error": "未知のタスクタイプ"}

        except Exception as e:
            print(f"[{self.name}] タスク実行エラー: {e}")
            return {"success": False, "error": str(e)}

    async def _event_sourcing_agent(self, **params):
        """イベントソーシングエージェント。イベントソーシングの実装。のメイン処理"""
        # TODO: 実装を追加
        result = {"message": "イベントソーシングエージェント。イベントソーシングの実装。処理完了", "params": params}
        return result


async def main():
    """メインエントリーポイント"""
    agent = EventSourcingAgentAgent()
    try:
        await agent.start()
    except KeyboardInterrupt:
        print("\nシャットダウン中...")
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
