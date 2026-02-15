#!/usr/bin/env python3
"""
Baseball Advanced Analytics Orchestrator
野球データ高度分析エージェントのオーケストレーター
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 設定
WORKSPACE = Path("/workspace")
AGENTS_DIR = WORKSPACE / "agents"
PROGRESS_FILE = WORKSPACE / "baseball_advanced_analytics_progress.json"

# エージェント定義
AGENTS = [
    {
        "name": "baseball-sabermetrics-agent",
        "description_ja": "セイバーメトリクス分析エージェント",
        "description_en": "Sabermetrics Analysis Agent",
        "type": "analytics",
        "emoji": "📊"
    },
    {
        "name": "baseball-prediction-ml-agent",
        "description_ja": "機械学習試合予測エージェント",
        "description_en": "Machine Learning Prediction Agent",
        "type": "ml",
        "emoji": "🤖"
    },
    {
        "name": "baseball-pitcher-analysis-agent",
        "description_ja": "投手高度分析エージェント",
        "description_en": "Pitcher Advanced Analysis Agent",
        "type": "analysis",
        "emoji": "⚾"
    },
    {
        "name": "baseball-batter-analysis-agent",
        "description_ja": "打者高度分析エージェント",
        "description_en": "Batter Advanced Analysis Agent",
        "type": "analysis",
        "emoji": "🏏"
    },
    {
        "name": "baseball-fielding-agent",
        "description_ja": "守備分析エージェント",
        "description_en": "Fielding Analysis Agent",
        "type": "analysis",
        "emoji": "🧤"
    }
]

def load_progress():
    """進捗状況をロード"""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"agents": {}, "last_updated": None}

def save_progress(progress):
    """進捗状況を保存"""
    progress["last_updated"] = datetime.now().isoformat()
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)

def create_agent_dir(agent):
    """エージェントディレクトリを作成"""
    agent_dir = AGENTS_DIR / agent["name"]
    agent_dir.mkdir(parents=True, exist_ok=True)
    return agent_dir

def generate_agent_py(agent):
    """agent.pyを生成"""
    return f'''#!/usr/bin/env python3
"""
{agent['description_ja']} / {agent['description_en']}
{agent['name']}
"""

import sqlite3
from datetime import datetime
from pathlib import Path

class {agent['name'].replace('-', '_').title().replace('_', '')}Agent:
    """{agent['description_ja']}"""

    def __init__(self, db_path=None):
        self.db_path = db_path or Path("data/baseball_advanced.db")
        self.conn = None
        self.init_db()

    def init_db(self):
        """データベース初期化"""
        self.conn = sqlite3.connect(self.db_path)
        self.create_tables()

    def create_tables(self):
        """テーブル作成"""
        cursor = self.conn.cursor()

        # セイバーメトリクステーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sabermetrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                player_name TEXT,
                team TEXT,
                season INTEGER NOT NULL,
                stat_type TEXT NOT NULL,
                stat_name TEXT NOT NULL,
                stat_value REAL,
                calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 予測モデルテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                match_id TEXT NOT NULL,
                prediction_type TEXT NOT NULL,
                predicted_value REAL,
                confidence REAL,
                actual_value REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 投手分析テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pitcher_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                player_name TEXT,
                team TEXT,
                season INTEGER,
                era REAL,
                whip REAL,
                fip REAL,
                k_per_9 REAL,
                bb_per_9 REAL,
                hr_per_9 REAL,
                strikeout_rate REAL,
                groundball_rate REAL,
                avg_velocity REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 打者分析テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS batter_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                player_name TEXT,
                team TEXT,
                season INTEGER,
                avg REAL,
                obp REAL,
                slg REAL,
                ops REAL,
                wrc_plus REAL,
                iso REAL,
                babip REAL,
                hard_hit_rate REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 守備分析テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fielding_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                player_name TEXT,
                team TEXT,
                season INTEGER,
                position TEXT,
                games_played INTEGER,
                innings_played REAL,
                putouts INTEGER,
                assists INTEGER,
                errors INTEGER,
                fielding_percentage REAL,
                drs INTEGER,
                uzr REAL,
                oaa REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()

    def add_sabermetric(self, player_id, player_name, team, season, stat_type, stat_name, stat_value):
        """セイバーメトリクスを追加"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO sabermetrics (player_id, player_name, team, season, stat_type, stat_name, stat_value)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (player_id, player_name, team, season, stat_type, stat_name, stat_value))
        self.conn.commit()
        return cursor.lastrowid

    def get_sabermetrics(self, player_id=None, season=None):
        """セイバーメトリクスを取得"""
        cursor = self.conn.cursor()
        query = "SELECT * FROM sabermetrics WHERE 1=1"
        params = []

        if player_id:
            query += " AND player_id = ?"
            params.append(player_id)

        if season:
            query += " AND season = ?"
            params.append(season)

        query += " ORDER BY season DESC, calculated_at DESC"
        cursor.execute(query, params)
        return cursor.fetchall()

    def calculate_ops(self, obp, slg):
        """OPSを計算"""
        return obp + slg if obp and slg else None

    def calculate_fip(self, hr, bb, hbp, k, ip):
        """FIP (Fielding Independent Pitching) を計算"""
        if ip == 0:
            return None
        return ((13 * hr) + (3 * (bb + hbp)) - (2 * k)) / ip + 3.2

    def calculate_rc(self, h, tb, bb, hbp, ab, sf):
        """RC (Runs Created) を計算"""
        denominator = ab + bb + hbp + sf
        if denominator == 0:
            return None
        numerator = (h + bb + hbp) * tb
        return numerator / denominator

    def add_prediction(self, model_name, match_id, prediction_type, predicted_value, confidence):
        """予測を追加"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO predictions (model_name, match_id, prediction_type, predicted_value, confidence)
            VALUES (?, ?, ?, ?, ?)
        """, (model_name, match_id, prediction_type, predicted_value, confidence))
        self.conn.commit()
        return cursor.lastrowid

    def get_prediction_accuracy(self, model_name=None, limit=100):
        """予測精度を取得"""
        cursor = self.conn.cursor()
        query = """
            SELECT * FROM predictions
            WHERE actual_value IS NOT NULL
        """
        params = []

        if model_name:
            query += " AND model_name = ?"
            params.append(model_name)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        predictions = cursor.fetchall()

        if not predictions:
            return None

        errors = []
        for pred in predictions:
            predicted = pred[6]
            actual = pred[7]
            if predicted is not None and actual is not None:
                errors.append(abs(predicted - actual))

        if errors:
            mae = sum(errors) / len(errors)  # Mean Absolute Error
            return {{
                "count": len(predictions),
                "mae": mae,
                "predictions": predictions
            }}

        return None

    def get_close(self):
        """接続を閉じる"""
        if self.conn:
            self.conn.close()


if __name__ == "__main__":
    agent = {agent['name'].replace('-', '_').title().replace('_', '')}Agent()

    # サンプルデータ追加
    agent.add_sabermetric("player001", "山田太郎", "ヤンキース", 2024, "batting", "OPS", 0.923)
    agent.add_sabermetric("player001", "山田太郎", "ヤンキース", 2024, "batting", "wRC+", 145)

    # セイバーメトリクス取得
    metrics = agent.get_sabermetrics(player_id="player001")
    print("セイバーメトリクス:")
    for metric in metrics:
        print(f"  {{metric[2]}}: {{metric[5]}} = {{metric[6]}}")

    # 計算
    print(f"\\nOPS計算: {{agent.calculate_ops(0.380, 0.543)}}")
    print(f"FIP計算: {{agent.calculate_fip(20, 50, 5, 200, 180)}}")

    agent.get_close()
'''

def generate_db_py(agent):
    """db.pyを生成"""
    return f'''#!/usr/bin/env python3
"""
{agent['description_ja']} データベース管理 / {agent['description_en']} Database Management
{agent['name']}
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

class BaseballAdvancedDB:
    """野球高度分析データベース管理クラス"""

    def __init__(self, db_path: str = "data/baseball_advanced.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self.connect()

    def connect(self):
        """データベース接続"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        """接続を閉じる"""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def execute_query(self, query: str, params: tuple = None) -> List[sqlite3.Row]:
        """クエリ実行"""
        cursor = self.conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()

    def execute_update(self, query: str, params: tuple = None) -> int:
        """更新クエリ実行"""
        cursor = self.conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        self.conn.commit()
        return cursor.lastrowid

    def create_player_sabermetric(
        self,
        player_id: str,
        player_name: str,
        team: str,
        season: int,
        stat_type: str,
        stat_name: str,
        stat_value: float
    ) -> int:
        """選手セイバーメトリクス作成"""
        query = """
            INSERT INTO sabermetrics (player_id, player_name, team, season, stat_type, stat_name, stat_value)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_update(query, (player_id, player_name, team, season, stat_type, stat_name, stat_value))

    def get_player_sabermetrics(
        self,
        player_id: str,
        season: Optional[int] = None
    ) -> List[Dict]:
        """選手セイバーメトリクス取得"""
        query = "SELECT * FROM sabermetrics WHERE player_id = ?"
        params = [player_id]

        if season:
            query += " AND season = ?"
            params.append(season)

        query += " ORDER BY season DESC, calculated_at DESC"
        rows = self.execute_query(query, tuple(params))
        return [dict(row) for row in rows]

    def get_top_players(
        self,
        stat_name: str,
        season: int,
        stat_type: str = "batting",
        limit: int = 10
    ) -> List[Dict]:
        """トップ選手を取得"""
        query = """
            SELECT DISTINCT player_id, player_name, team, stat_value
            FROM sabermetrics
            WHERE season = ? AND stat_type = ? AND stat_name = ?
            ORDER BY stat_value DESC
            LIMIT ?
        """
        rows = self.execute_query(query, (season, stat_type, stat_name, limit))
        return [dict(row) for row in rows]

    def create_pitcher_stats(
        self,
        player_id: str,
        player_name: str,
        team: str,
        season: int,
        era: Optional[float] = None,
        whip: Optional[float] = None,
        fip: Optional[float] = None,
        k_per_9: Optional[float] = None,
        bb_per_9: Optional[float] = None
    ) -> int:
        """投手統計作成"""
        query = """
            INSERT INTO pitcher_stats (player_id, player_name, team, season, era, whip, fip, k_per_9, bb_per_9)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_update(query, (player_id, player_name, team, season, era, whip, fip, k_per_9, bb_per_9))

    def get_pitcher_stats(self, player_id: str, season: Optional[int] = None) -> Optional[Dict]:
        """投手統計取得"""
        query = "SELECT * FROM pitcher_stats WHERE player_id = ?"
        params = [player_id]

        if season:
            query += " AND season = ?"
            params.append(season)

        query += " ORDER BY season DESC LIMIT 1"
        rows = self.execute_query(query, tuple(params))
        return dict(rows[0]) if rows else None

    def create_batter_stats(
        self,
        player_id: str,
        player_name: str,
        team: str,
        season: int,
        avg: Optional[float] = None,
        obp: Optional[float] = None,
        slg: Optional[float] = None,
        ops: Optional[float] = None
    ) -> int:
        """打者統計作成"""
        query = """
            INSERT INTO batter_stats (player_id, player_name, team, season, avg, obp, slg, ops)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_update(query, (player_id, player_name, team, season, avg, obp, slg, ops))

    def get_batter_stats(self, player_id: str, season: Optional[int] = None) -> Optional[Dict]:
        """打者統計取得"""
        query = "SELECT * FROM batter_stats WHERE player_id = ?"
        params = [player_id]

        if season:
            query += " AND season = ?"
            params.append(season)

        query += " ORDER BY season DESC LIMIT 1"
        rows = self.execute_query(query, tuple(params))
        return dict(rows[0]) if rows else None

    def create_prediction(
        self,
        model_name: str,
        match_id: str,
        prediction_type: str,
        predicted_value: float,
        confidence: float
    ) -> int:
        """予測作成"""
        query = """
            INSERT INTO predictions (model_name, match_id, prediction_type, predicted_value, confidence)
            VALUES (?, ?, ?, ?, ?)
        """
        return self.execute_update(query, (model_name, match_id, prediction_type, predicted_value, confidence))

    def update_prediction_result(self, prediction_id: int, actual_value: float) -> bool:
        """予測結果を更新"""
        query = "UPDATE predictions SET actual_value = ? WHERE id = ?"
        result = self.execute_update(query, (actual_value, prediction_id))
        return result > 0

    def get_model_statistics(self, model_name: str) -> Dict:
        """モデル統計取得"""
        # 予測数
        total = self.execute_query(
            "SELECT COUNT(*) FROM predictions WHERE model_name = ?",
            (model_name,)
        )[0][0]

        # 実績がある予測
        with_actual = self.execute_query(
            "SELECT COUNT(*) FROM predictions WHERE model_name = ? AND actual_value IS NOT NULL",
            (model_name,)
        )[0][0]

        # 平均誤差
        error_rows = self.execute_query(
            "SELECT ABS(predicted_value - actual_value) as error FROM predictions WHERE model_name = ? AND actual_value IS NOT NULL",
            (model_name,)
        )
        if error_rows:
            mae = sum(row['error'] for row in error_rows) / len(error_rows)
        else:
            mae = 0

        return {{
            "model_name": model_name,
            "total_predictions": total,
            "predictions_with_results": with_actual,
            "mean_absolute_error": mae
        }}

    def get_fielding_stats(self, player_id: str, season: Optional[int] = None) -> List[Dict]:
        """守備統計取得"""
        query = "SELECT * FROM fielding_stats WHERE player_id = ?"
        params = [player_id]

        if season:
            query += " AND season = ?"
            params.append(season)

        query += " ORDER BY season DESC"
        rows = self.execute_query(query, tuple(params))
        return [dict(row) for row in rows]


if __name__ == "__main__":
    import json
    with BaseballAdvancedDB() as db:
        # テスト: 投手統計作成
        db.create_pitcher_stats("p001", "佐藤投手", "巨人", 2024, 2.45, 0.98, 2.89, 9.5, 2.1)

        # テスト: 投手統計取得
        stats = db.get_pitcher_stats("p001", 2024)
        print("投手統計:")
        print(json.dumps(stats, indent=2, ensure_ascii=False))
'''

def generate_discord_py(agent):
    """discord.pyを生成"""
    return f'''#!/usr/bin/env python3
"""
{agent['description_ja']} Discord連携 / {agent['description_en']} Discord Integration
{agent['name']}
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


class {agent['name'].replace('-', '_').title().replace('_', '')}Discord:
    """Discordボットインターフェース"""

    def __init__(self):
        self.db = BaseballAdvancedDB()

    def parse_command(self, content: str) -> dict:
        """コマンドをパース"""
        parts = content.strip().split()
        if len(parts) < 2:
            return {{"error": "Invalid command"}}

        command = parts[1].lower()
        args = parts[2:] if len(parts) > 2 else []

        return {{
            "command": command,
            "args": args
        }}

    def handle_player_stats(self, user_id: str, args: list) -> dict:
        """選手統計コマンド処理"""
        if len(args) < 1:
            return {{"error": "Usage: player <player_id> [season]"}}

        player_id = args[0]
        season = int(args[1]) if len(args) > 1 and args[1].isdigit() else None

        # 打者統計
        batter_stats = self.db.get_batter_stats(player_id, season)
        # 投手統計
        pitcher_stats = self.db.get_pitcher_stats(player_id, season)

        if not batter_stats and not pitcher_stats:
            return {{
                "success": True,
                "message": f"選手ID {{player_id}} の統計が見つかりませんでした"
            }}

        lines = ["**選手統計**"]

        if batter_stats:
            lines.append("\\n**打者成績**:")
            lines.append(f"AVG: {{batter_stats['avg']:.3f}}" if batter_stats.get('avg') else "AVG: -")
            lines.append(f"OBP: {{batter_stats['obp']:.3f}}" if batter_stats.get('obp') else "OBP: -")
            lines.append(f"SLG: {{batter_stats['slg']:.3f}}" if batter_stats.get('slg') else "SLG: -")
            lines.append(f"OPS: {{batter_stats['ops']:.3f}}" if batter_stats.get('ops') else "OPS: -")

        if pitcher_stats:
            lines.append("\\n**投手成績**:")
            lines.append(f"ERA: {{pitcher_stats['era']:.2f}}" if pitcher_stats.get('era') else "ERA: -")
            lines.append(f"WHIP: {{pitcher_stats['whip']:.2f}}" if pitcher_stats.get('whip') else "WHIP: -")
            lines.append(f"FIP: {{pitcher_stats['fip']:.2f}}" if pitcher_stats.get('fip') else "FIP: -")
            lines.append(f"K/9: {{pitcher_stats['k_per_9']:.1f}}" if pitcher_stats.get('k_per_9') else "K/9: -")

        return {{
            "success": True,
            "message": "\\n".join(lines)
        }}

    def handle_top_players(self, user_id: str, args: list) -> dict:
        """トップ選手コマンド処理"""
        season = int(args[0]) if len(args) > 0 and args[0].isdigit() else 2024
        stat_name = args[1] if len(args) > 1 else "OPS"

        top_players = self.db.get_top_players(stat_name, season, limit=10)

        if not top_players:
            return {{
                "success": True,
                "message": f"{{season}}年の{{stat_name}}ランキングデータが見つかりませんでした"
            }}

        lines = [f"**{{season}}年 {{stat_name}} トップ10**"]

        for i, player in enumerate(top_players[:10], 1):
            value = player['stat_value']
            lines.append(f"{{i}}. {{player['player_name']}} ({{player['team']}}): {{value}}")

        return {{
            "success": True,
            "message": "\\n".join(lines)
        }}

    def handle_sabermetrics(self, user_id: str, args: list) -> dict:
        """セイバーメトリクスコマンド処理"""
        if len(args) < 1:
            return {{"error": "Usage: saber <player_id> [season]"}}

        player_id = args[0]
        season = int(args[1]) if len(args) > 1 and args[1].isdigit() else None

        metrics = self.db.get_player_sabermetrics(player_id, season)

        if not metrics:
            return {{
                "success": True,
                "message": f"選手ID {{player_id}} のセイバーメトリクスが見つかりませんでした"
            }}

        lines = [f"**セイバーメトリクス: {{player_id}}**"]

        for metric in metrics[:20]:
            lines.append(f"{{metric[5]}}: {{metric[6]}}")

        return {{
            "success": True,
            "message": "\\n".join(lines)
        }}

    def handle_model_stats(self, user_id: str, args: list) -> dict:
        """モデル統計コマンド処理"""
        model_name = args[0] if len(args) > 0 else "default"

        stats = self.db.get_model_statistics(model_name)

        lines = ["**モデル統計**"]
        lines.append(f"モデル: {{stats['model_name']}}")
        lines.append(f"総予測数: {{stats['total_predictions']}}")
        lines.append(f"実績あり: {{stats['predictions_with_results']}}")
        if stats['predictions_with_results'] > 0:
            lines.append(f"平均誤差: {{stats['mean_absolute_error']:.3f}}")

        return {{
            "success": True,
            "message": "\\n".join(lines)
        }}

    def handle_fielding(self, user_id: str, args: list) -> dict:
        """守備統計コマンド処理"""
        if len(args) < 1:
            return {{"error": "Usage: fielding <player_id> [season]"}}

        player_id = args[0]
        season = int(args[1]) if len(args) > 1 and args[1].isdigit() else None

        fielding_stats = self.db.get_fielding_stats(player_id, season)

        if not fielding_stats:
            return {{
                "success": True,
                "message": f"選手ID {{player_id}} の守備統計が見つかりませんでした"
            }}

        lines = [f"**守備統計: {{player_id}}**"]

        for stats in fielding_stats[:5]:
            lines.append(f"シーズン {{stats['season']}}:")
            lines.append(f"  ポジション: {{stats['position']}}")
            lines.append(f"  試合: {{stats['games_played']}}, 回: {{stats['innings_played']}}")
            if stats.get('drs') is not None:
                lines.append(f"  DRS: {{stats['drs']}}")
            if stats.get('uzr') is not None:
                lines.append(f"  UZR: {{stats['uzr']:.1f}}")

        return {{
            "success": True,
            "message": "\\n".join(lines)
        }}

    def handle_command(self, user_id: str, content: str) -> dict:
        """コマンドを処理"""
        parsed = self.parse_command(content)

        if "error" in parsed:
            return {{"error": "Invalid command format"}}

        command = parsed["command"]
        args = parsed["args"]

        # コマンドルーター
        handlers = {{
            "player": self.handle_player_stats,
            "top": self.handle_top_players,
            "saber": self.handle_sabermetrics,
            "model": self.handle_model_stats,
            "fielding": self.handle_fielding
        }}

        handler = handlers.get(command)
        if handler:
            return handler(user_id, args)
        else:
            return {{
                "error": f"Unknown command: {{command}}\\nAvailable commands: player, top, saber, model, fielding"
            }}

    def format_response(self, response: dict) -> str:
        """レスポンスを整形"""
        if "error" in response:
            return f"❌ {{response['error']}}"

        if "message" in response:
            emoji_map = {{
                "player": "🏏",
                "top": "🏆",
                "saber": "📊",
                "model": "🤖",
                "fielding": "🧤"
            }}
            command = response.get("command", "")
            emoji = emoji_map.get(command, "✅")
            return f"{{emoji}} {{response['message']}}"

        return "✅ コマンドを実行しました"


if __name__ == "__main__":
    bot = {agent['name'].replace('-', '_').title().replace('_', '')}Discord()

    # テスト
    user_id = "test-user"
    print("コマンドテスト:")

    # テスト: top
    result = bot.handle_command(user_id, "!baseball top 2024 OPS")
    print(f"top: {{bot.format_response(result)}}")

    # テスト: model
    result = bot.handle_command(user_id, "!baseball model default")
    print(f"model: {{bot.format_response(result)}}")
'''

def generate_readme(agent):
    """README.mdを生成"""
    return f'''# {agent['name']}

{agent['emoji']} {agent['description_ja']} / {agent['description_en']}

## 概要 (Overview)

このエージェントは、野球の高度なデータ分析を提供します。セイバーメトリクス、機械学習による予測、投手/打者/守備の詳細分析を行います。

This agent provides advanced baseball data analysis, including sabermetrics, machine learning predictions, and detailed pitcher/batter/fielding analysis.

## 機能 (Features)

### セイバーメトリクス (Sabermetrics)
- **OPS** (On-base Plus Slugging): 出塁率 + 長打率
- **wRC+** (Weighted Runs Created Plus): 調整された得点生産
- **FIP** (Fielding Independent Pitching): 守備から独立した投手指標
- **RC** (Runs Created): 得点貢献度

### 予測モデル (Prediction Models)
- 試合結果予測
- 選手成績予測
- モデル精度追跡

### 投手分析 (Pitcher Analysis)
- ERA, WHIP, FIP
- K/9, BB/9, HR/9
- 奪三振率, ゴロ率
- 平均球速

### 打者分析 (Batter Analysis)
- AVG, OBP, SLG, OPS
- wRC+, ISO, BABIP
- 硬打球率

### 守備分析 (Fielding Analysis)
- 守備率
- DRS (Defensive Runs Saved)
- UZR (Ultimate Zone Rating)
- OAA (Outs Above Average)

## インストール (Installation)

```bash
pip install -r requirements.txt
```

## 使い方 (Usage)

### Python API

```python
from agent import {agent['name'].replace('-', '_').title().replace('_', '')}Agent

# エージェント初期化
agent = {agent['name'].replace('-', '_').title().replace('_', '')}Agent()

# セイバーメトリクス追加
agent.add_sabermetric("player001", "山田太郎", "ヤンキース", 2024, "batting", "OPS", 0.923)

# セイバーメトリクス取得
metrics = agent.get_sabermetrics(player_id="player001")

# 計算
ops = agent.calculate_ops(0.380, 0.543)
fip = agent.calculate_fip(20, 50, 5, 200, 180)

# 接続を閉じる
agent.get_close()
```

### Discord Bot

```
!baseball player <player_id> [season]
!baseball top <season> <stat_name>
!baseball saber <player_id> [season]
!baseball model <model_name>
!baseball fielding <player_id> [season]
```

## データベース (Database)

- `sabermetrics`: セイバーメトリクスデータ
- `predictions`: 予測データ
- `pitcher_stats`: 投手統計
- `batter_stats`: 打者統計
- `fielding_stats`: 守備統計

## 環境変数 (Environment Variables)

- `DISCORD_TOKEN`: Discordボットトークン

## ライセンス (License)

MIT License
'''

def generate_requirements_txt(agent):
    """requirements.txtを生成"""
    return '''# Baseball Advanced Analytics Agent Requirements

# Core
python-dotenv>=1.0.0

# Discord
discord.py>=2.3.0

# Database
sqlite3  # Python標準ライブラリ

# Data Analysis
pandas>=2.0.0
numpy>=1.24.0

# Machine Learning
scikit-learn>=1.3.0
torch>=2.0.0  # PyTorch for predictions

# Data Visualization
matplotlib>=3.7.0
seaborn>=0.12.0
'''

def create_agent_files(agent_dir, agent):
    """エージェントファイルを作成"""
    # agent.py
    with open(agent_dir / "agent.py", "w", encoding="utf-8") as f:
        f.write(generate_agent_py(agent))

    # db.py
    with open(agent_dir / "db.py", "w", encoding="utf-8") as f:
        f.write(generate_db_py(agent))

    # discord.py
    with open(agent_dir / "discord.py", "w", encoding="utf-8") as f:
        f.write(generate_discord_py(agent))

    # README.md
    with open(agent_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(generate_readme(agent))

    # requirements.txt
    with open(agent_dir / "requirements.txt", "w", encoding="utf-8") as f:
        f.write(generate_requirements_txt(agent))

def verify_agent(agent_dir, agent):
    """エージェントファイルを検証"""
    required_files = ["agent.py", "db.py", "discord.py", "README.md", "requirements.txt"]
    all_exist = True

    for filename in required_files:
        file_path = agent_dir / filename
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  ✅ {filename} ({size} bytes)")
        else:
            print(f"  ❌ {filename} missing")
            all_exist = False

    return all_exist

def commit_changes(message):
    """変更をコミット"""
    try:
        subprocess.run(
            ["git", "add", "-A"],
            cwd=WORKSPACE,
            capture_output=True,
            text=True
        )

        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=WORKSPACE,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f"  ✅ Committed: {message}")
            return True
        else:
            print(f"  ❌ Commit failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ❌ Git error: {e}")
        return False

def push_changes():
    """変更をプッシュ"""
    try:
        result = subprocess.run(
            ["git", "push"],
            cwd=WORKSPACE,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f"  ✅ Pushed to remote")
            return True
        else:
            print(f"  ❌ Push failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ❌ Git error: {e}")
        return False

def main():
    """メイン処理"""
    print("=" * 60)
    print("野球データ高度分析エージェント オーケストレーター")
    print("Baseball Advanced Analytics Agent Orchestrator")
    print("=" * 60)

    progress = load_progress()
    existing_agents = progress.get('agents', {})
    print(f"\n既存の進捗: {existing_agents}")

    completed_count = 0
    for agent in AGENTS:
        agent_name = agent["name"]
        agent_dir = AGENTS_DIR / agent_name

        print(f"\n🔧 作成中: {agent_name}")
        print(f"   {agent['description_ja']}")

        # ディレクトリ作成
        create_agent_dir(agent)

        # ファイル作成
        print("  ファイル作成中...")
        create_agent_files(agent_dir, agent)

        # 検証
        print("  検証中...")
        if verify_agent(agent_dir, agent):
            progress["agents"][agent_name] = {
                "status": "completed",
                "timestamp": datetime.now().isoformat()
            }
            completed_count += 1
        else:
            progress["agents"][agent_name] = {
                "status": "failed",
                "timestamp": datetime.now().isoformat()
            }

    # 進捗保存
    save_progress(progress)

    # 統計
    total = len(AGENTS)
    print(f"\n{'=' * 60}")
    print(f"📊 統計 (Statistics)")
    print(f"   完了: {completed_count}/{total}")
    print(f"   成功率: {completed_count/total*100:.1f}%")
    print(f"{'=' * 60}")

    # Git commit & push
    if completed_count > 0:
        print(f"\n📦 Git commit & push...")
        if commit_changes(f"feat: 野球データ高度分析エージェントプロジェクト完了 ({completed_count}/{total})"):
            push_changes()

    print(f"\n🎉 オーケストレーション完了！")
    print(f"\n作成されたエージェント:")
    for agent in AGENTS:
        status = progress["agents"].get(agent["name"], {}).get("status", "pending")
        emoji = "✅" if status == "completed" else "❌"
        print(f"  {emoji} {agent['name']} - {agent['description_ja']}")

if __name__ == "__main__":
    main()
