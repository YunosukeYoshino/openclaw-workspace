#!/usr/bin/env python3
"""
野球殿堂エージェント
Baseball Hall of Fame Agent

野球殿堂入り選手・殿堂情報を管理するエージェント
Agent for managing Baseball Hall of Fame inductees and information
"""

import asyncio
from typing import Optional
from .db import BaseballHofAgentDB

class BaseballHofAgentAgent:
    "Baseball Hall of Fame Agent""

    def __init__(self, db_path: str = "data/baseball-hof-agent.db"):
        self.db = BaseballHofAgentDB(db_path)
        self.name = "野球殿堂エージェント"

    async def process_command(self, command: str, args: list) -> str:
        """コマンドを処理する"""
        if command in ["rule", "term", "explain"]:
            return await self.show_rule(args)
        elif command in ["hof", "inductee", "category"]:
            return await self.show_hof(args)
        elif command in ["award", "mvp", "cy"]:
            return await self.show_award(args)
        elif command in ["stadium", "seat", "access"]:
            return await self.show_stadium(args)
        elif command in ["legend", "play", "record"]:
            return await self.show_legend(args)
        else:
            return "不明なコマンドです。"

    async def show_rule(self, args: list) -> str:
        """ルールを表示する"""
        rules = self.db.get_all_rules()
        if not rules:
            return "ルールが登録されていません。"
        return "\\n".join([f"- {{r['name']}}: {{r['description']}}" for r in rules[:5]])

    async def show_hof(self, args: list) -> str:
        """殿堂入り選手を表示する"""
        inductees = self.db.get_all_inductees()
        if not inductees:
            return "殿堂入り選手が登録されていません。"
        return "\\n".join([f"- {{i['name']}} ({{i['year']}})" for i in inductees[:5]])

    async def show_award(self, args: list) -> str:
        """賞を表示する"""
        awards = self.db.get_all_awards()
        if not awards:
            return "賞が登録されていません。"
        return "\\n".join([f"- {{a['name']}} ({{a['year']}})" for a in awards[:5]])

    async def show_stadium(self, args: list) -> str:
        """野球場を表示する"""
        stadiums = self.db.get_all_stadiums()
        if not stadiums:
            return "野球場が登録されていません。"
        return "\\n".join([f"- {{s['name']}} (収容: {{s['capacity']}})" for s in stadiums[:5]])

    async def show_legend(self, args: list) -> str:
        """伝説を表示する"""
        legends = self.db.get_all_legends()
        if not legends:
            return "伝説が登録されていません。"
        return "\\n".join([f"- {{l['name']}}: {{l['description']}}" for l in legends[:5]])

def main():
    import sys
    agent = BaseballHofAgentAgent()
    print(f"{{agent.name}} エージェントが準備完了")

if __name__ == "__main__":
    main()
