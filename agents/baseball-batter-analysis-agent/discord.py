#!/usr/bin/env python3
"""
打者高度分析エージェント Discord連携 / Batter Advanced Analysis Agent Discord Integration
baseball-batter-analysis-agent
"""

import json
from datetime import datetime
from pathlib import Path

# Discord Bot Token（環境変数から取得）
import os
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")

# データベースインポート
import sys
sys.path.insert(0, str(Path(__file__).parent))
from db import BaseballAdvancedDB


class BaseballBatterAnalysisAgentDiscord:
    """Discordボットインターフェース"""

    def __init__(self):
        self.db = BaseballAdvancedDB()

    def parse_command(self, content: str) -> dict:
        """コマンドをパース"""
        parts = content.strip().split()
        if len(parts) < 2:
            return {"error": "Invalid command"}

        command = parts[1].lower()
        args = parts[2:] if len(parts) > 2 else []

        return {
            "command": command,
            "args": args
        }

    def handle_player_stats(self, user_id: str, args: list) -> dict:
        """選手統計コマンド処理"""
        if len(args) < 1:
            return {"error": "Usage: player <player_id> [season]"}

        player_id = args[0]
        season = int(args[1]) if len(args) > 1 and args[1].isdigit() else None

        # 打者統計
        batter_stats = self.db.get_batter_stats(player_id, season)
        # 投手統計
        pitcher_stats = self.db.get_pitcher_stats(player_id, season)

        if not batter_stats and not pitcher_stats:
            return {
                "success": True,
                "message": f"選手ID {player_id} の統計が見つかりませんでした"
            }

        lines = ["**選手統計**"]

        if batter_stats:
            lines.append("\n**打者成績**:")
            lines.append(f"AVG: {batter_stats['avg']:.3f}" if batter_stats.get('avg') else "AVG: -")
            lines.append(f"OBP: {batter_stats['obp']:.3f}" if batter_stats.get('obp') else "OBP: -")
            lines.append(f"SLG: {batter_stats['slg']:.3f}" if batter_stats.get('slg') else "SLG: -")
            lines.append(f"OPS: {batter_stats['ops']:.3f}" if batter_stats.get('ops') else "OPS: -")

        if pitcher_stats:
            lines.append("\n**投手成績**:")
            lines.append(f"ERA: {pitcher_stats['era']:.2f}" if pitcher_stats.get('era') else "ERA: -")
            lines.append(f"WHIP: {pitcher_stats['whip']:.2f}" if pitcher_stats.get('whip') else "WHIP: -")
            lines.append(f"FIP: {pitcher_stats['fip']:.2f}" if pitcher_stats.get('fip') else "FIP: -")
            lines.append(f"K/9: {pitcher_stats['k_per_9']:.1f}" if pitcher_stats.get('k_per_9') else "K/9: -")

        return {
            "success": True,
            "message": "\n".join(lines)
        }

    def handle_top_players(self, user_id: str, args: list) -> dict:
        """トップ選手コマンド処理"""
        season = int(args[0]) if len(args) > 0 and args[0].isdigit() else 2024
        stat_name = args[1] if len(args) > 1 else "OPS"

        top_players = self.db.get_top_players(stat_name, season, limit=10)

        if not top_players:
            return {
                "success": True,
                "message": f"{season}年の{stat_name}ランキングデータが見つかりませんでした"
            }

        lines = [f"**{season}年 {stat_name} トップ10**"]

        for i, player in enumerate(top_players[:10], 1):
            value = player['stat_value']
            lines.append(f"{i}. {player['player_name']} ({player['team']}): {value}")

        return {
            "success": True,
            "message": "\n".join(lines)
        }

    def handle_sabermetrics(self, user_id: str, args: list) -> dict:
        """セイバーメトリクスコマンド処理"""
        if len(args) < 1:
            return {"error": "Usage: saber <player_id> [season]"}

        player_id = args[0]
        season = int(args[1]) if len(args) > 1 and args[1].isdigit() else None

        metrics = self.db.get_player_sabermetrics(player_id, season)

        if not metrics:
            return {
                "success": True,
                "message": f"選手ID {player_id} のセイバーメトリクスが見つかりませんでした"
            }

        lines = [f"**セイバーメトリクス: {player_id}**"]

        for metric in metrics[:20]:
            lines.append(f"{metric[5]}: {metric[6]}")

        return {
            "success": True,
            "message": "\n".join(lines)
        }

    def handle_model_stats(self, user_id: str, args: list) -> dict:
        """モデル統計コマンド処理"""
        model_name = args[0] if len(args) > 0 else "default"

        stats = self.db.get_model_statistics(model_name)

        lines = ["**モデル統計**"]
        lines.append(f"モデル: {stats['model_name']}")
        lines.append(f"総予測数: {stats['total_predictions']}")
        lines.append(f"実績あり: {stats['predictions_with_results']}")
        if stats['predictions_with_results'] > 0:
            lines.append(f"平均誤差: {stats['mean_absolute_error']:.3f}")

        return {
            "success": True,
            "message": "\n".join(lines)
        }

    def handle_fielding(self, user_id: str, args: list) -> dict:
        """守備統計コマンド処理"""
        if len(args) < 1:
            return {"error": "Usage: fielding <player_id> [season]"}

        player_id = args[0]
        season = int(args[1]) if len(args) > 1 and args[1].isdigit() else None

        fielding_stats = self.db.get_fielding_stats(player_id, season)

        if not fielding_stats:
            return {
                "success": True,
                "message": f"選手ID {player_id} の守備統計が見つかりませんでした"
            }

        lines = [f"**守備統計: {player_id}**"]

        for stats in fielding_stats[:5]:
            lines.append(f"シーズン {stats['season']}:")
            lines.append(f"  ポジション: {stats['position']}")
            lines.append(f"  試合: {stats['games_played']}, 回: {stats['innings_played']}")
            if stats.get('drs') is not None:
                lines.append(f"  DRS: {stats['drs']}")
            if stats.get('uzr') is not None:
                lines.append(f"  UZR: {stats['uzr']:.1f}")

        return {
            "success": True,
            "message": "\n".join(lines)
        }

    def handle_command(self, user_id: str, content: str) -> dict:
        """コマンドを処理"""
        parsed = self.parse_command(content)

        if "error" in parsed:
            return {"error": "Invalid command format"}

        command = parsed["command"]
        args = parsed["args"]

        # コマンドルーター
        handlers = {
            "player": self.handle_player_stats,
            "top": self.handle_top_players,
            "saber": self.handle_sabermetrics,
            "model": self.handle_model_stats,
            "fielding": self.handle_fielding
        }

        handler = handlers.get(command)
        if handler:
            return handler(user_id, args)
        else:
            return {
                "error": f"Unknown command: {command}\nAvailable commands: player, top, saber, model, fielding"
            }

    def format_response(self, response: dict) -> str:
        """レスポンスを整形"""
        if "error" in response:
            return f"❌ {response['error']}"

        if "message" in response:
            emoji_map = {
                "player": "🏏",
                "top": "🏆",
                "saber": "📊",
                "model": "🤖",
                "fielding": "🧤"
            }
            command = response.get("command", "")
            emoji = emoji_map.get(command, "✅")
            return f"{emoji} {response['message']}"

        return "✅ コマンドを実行しました"


if __name__ == "__main__":
    bot = BaseballBatterAnalysisAgentDiscord()

    # テスト
    user_id = "test-user"
    print("コマンドテスト:")

    # テスト: top
    result = bot.handle_command(user_id, "!baseball top 2024 OPS")
    print(f"top: {bot.format_response(result)}")

    # テスト: model
    result = bot.handle_command(user_id, "!baseball model default")
    print(f"model: {bot.format_response(result)}")
