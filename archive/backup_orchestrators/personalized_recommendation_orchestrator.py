#!/usr/bin/env python3
"""
Personalized Recommendation Orchestrator
クロスカテゴリパーソナライズドレコメンデーションエージェントのオーケストレーター
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
PROGRESS_FILE = WORKSPACE / "personalized_recommendation_progress.json"

# エージェント定義
AGENTS = [
    {
        "name": "personalized-preference-agent",
        "description_ja": "ユーザー嗜好分析エージェント",
        "description_en": "User Preference Analysis Agent",
        "type": "preference",
        "emoji": "🧠"
    },
    {
        "name": "personalized-cross-recommendation-agent",
        "description_ja": "クロスカテゴリ推薦エージェント",
        "description_en": "Cross-Category Recommendation Agent",
        "type": "recommendation",
        "emoji": "🎯"
    },
    {
        "name": "personalized-ml-recommendation-agent",
        "description_ja": "機械学習推薦エージェント",
        "description_en": "Machine Learning Recommendation Agent",
        "type": "ml",
        "emoji": "🤖"
    },
    {
        "name": "personalized-behavior-agent",
        "description_ja": "ユーザー行動分析エージェント",
        "description_en": "User Behavior Analysis Agent",
        "type": "behavior",
        "emoji": "📊"
    },
    {
        "name": "personalized-feedback-agent",
        "description_ja": "フィードバック学習エージェント",
        "description_en": "Feedback Learning Agent",
        "type": "feedback",
        "emoji": "🔄"
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
        self.db_path = db_path or Path("data/preference.db")
        self.conn = None
        self.init_db()

    def init_db(self):
        """データベース初期化"""
        self.conn = sqlite3.connect(self.db_path)
        self.create_tables()

    def create_tables(self):
        """テーブル作成"""
        cursor = self.conn.cursor()

        # 嗜好テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                item_id TEXT NOT NULL,
                rating REAL,
                interaction_count INTEGER DEFAULT 0,
                last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 行動ログテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS behavior_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                action TEXT NOT NULL,
                category TEXT NOT NULL,
                item_id TEXT,
                context TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 推薦履歴テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                category TEXT NOT NULL,
                item_ids TEXT NOT NULL,
                algorithm TEXT,
                score REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()

    def add_preference(self, category, item_id, rating=None, tags=None):
        """嗜好を追加"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO preferences
            (category, item_id, rating, interaction_count, tags)
            VALUES (?, ?, ?,
                COALESCE((SELECT interaction_count FROM preferences WHERE category=? AND item_id=?), 0) + 1,
                ?)
        """, (category, item_id, rating, category, item_id, tags))
        self.conn.commit()
        return cursor.lastrowid

    def log_behavior(self, user_id, action, category, item_id=None, context=None):
        """行動を記録"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO behavior_logs (user_id, action, category, item_id, context)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, action, category, item_id, context))
        self.conn.commit()
        return cursor.lastrowid

    def get_preferences(self, category=None):
        """嗜好を取得"""
        cursor = self.conn.cursor()
        if category:
            cursor.execute("""
                SELECT * FROM preferences WHERE category = ?
                ORDER BY rating DESC, interaction_count DESC
            """, (category,))
        else:
            cursor.execute("""
                SELECT * FROM preferences
                ORDER BY rating DESC, interaction_count DESC
            """)
        return cursor.fetchall()

    def get_user_behavior(self, user_id, limit=100):
        """ユーザー行動を取得"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM behavior_logs
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (user_id, limit))
        return cursor.fetchall()

    def analyze_preferences(self, category=None):
        """嗜好を分析"""
        preferences = self.get_preferences(category)

        analysis = {{
            "top_items": [],
            "category_distribution": {{}},
            "average_rating": 0,
            "total_interactions": 0
        }}

        category_counts = {{}}
        total_rating = 0
        rating_count = 0

        for pref in preferences:
            # カテゴリ集計
            cat = pref[1]
            category_counts[cat] = category_counts.get(cat, 0) + 1

            # 評価集計
            rating = pref[3]
            if rating:
                total_rating += rating
                rating_count += 1

            # トップアイテム
            analysis["top_items"].append({{
                "category": pref[1],
                "item_id": pref[2],
                "rating": pref[3],
                "interaction_count": pref[4]
            }})

        analysis["category_distribution"] = category_counts
        analysis["total_interactions"] = sum(pref[4] for pref in preferences)
        if rating_count > 0:
            analysis["average_rating"] = total_rating / rating_count

        return analysis

    def get_close(self):
        """接続を閉じる"""
        if self.conn:
            self.conn.close()


if __name__ == "__main__":
    agent = {agent['name'].replace('-', '_').title().replace('_', '')}Agent()

    # サンプルデータ追加
    agent.add_preference("baseball", "npb-2024", 5.0, "プロ野球,日本")
    agent.add_preference("baseball", "mlb-yankees", 4.5, "メジャーリーグ,ヤンキース")
    agent.add_preference("game", "pokemon-scarlet", 4.0, "RPG,ポケモン")
    agent.add_preference("erotic", "character-001", 5.0, "アニメ,かわいい")

    # 分析実行
    analysis = agent.analyze_preferences()
    print("嗜好分析:")
    print(json.dumps(analysis, indent=2, ensure_ascii=False))

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

class PreferenceDB:
    """嗜好データベース管理クラス"""

    def __init__(self, db_path: str = "data/preference.db"):
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

    def create_preference(
        self,
        category: str,
        item_id: str,
        rating: Optional[float] = None,
        tags: Optional[str] = None
    ) -> int:
        """嗜好作成"""
        query = """
            INSERT INTO preferences (category, item_id, rating, tags)
            VALUES (?, ?, ?, ?)
        """
        return self.execute_update(query, (category, item_id, rating, tags))

    def get_preference(self, preference_id: int) -> Optional[Dict]:
        """嗜好取得"""
        rows = self.execute_query(
            "SELECT * FROM preferences WHERE id = ?",
            (preference_id,)
        )
        return dict(rows[0]) if rows else None

    def list_preferences(
        self,
        category: Optional[str] = None,
        min_rating: Optional[float] = None
    ) -> List[Dict]:
        """嗜好一覧"""
        query = "SELECT * FROM preferences WHERE 1=1"
        params = []

        if category:
            query += " AND category = ?"
            params.append(category)

        if min_rating:
            query += " AND rating >= ?"
            params.append(min_rating)

        query += " ORDER BY rating DESC, interaction_count DESC"

        rows = self.execute_query(query, tuple(params) if params else None)
        return [dict(row) for row in rows]

    def create_behavior_log(
        self,
        user_id: str,
        action: str,
        category: str,
        item_id: Optional[str] = None,
        context: Optional[str] = None
    ) -> int:
        """行動ログ作成"""
        query = """
            INSERT INTO behavior_logs (user_id, action, category, item_id, context)
            VALUES (?, ?, ?, ?, ?)
        """
        return self.execute_update(query, (user_id, action, category, item_id, context))

    def get_user_behavior(
        self,
        user_id: str,
        action: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """ユーザー行動取得"""
        query = "SELECT * FROM behavior_logs WHERE user_id = ?"
        params = [user_id]

        if action:
            query += " AND action = ?"
            params.append(action)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        rows = self.execute_query(query, tuple(params))
        return [dict(row) for row in rows]

    def create_recommendation(
        self,
        user_id: str,
        category: str,
        item_ids: str,
        algorithm: str,
        score: float
    ) -> int:
        """推薦作成"""
        query = """
            INSERT INTO recommendations (user_id, category, item_ids, algorithm, score)
            VALUES (?, ?, ?, ?, ?)
        """
        return self.execute_update(query, (user_id, category, item_ids, algorithm, score))

    def get_recommendations(
        self,
        user_id: str,
        category: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """推薦取得"""
        query = "SELECT * FROM recommendations WHERE user_id = ?"
        params = [user_id]

        if category:
            query += " AND category = ?"
            params.append(category)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        rows = self.execute_query(query, tuple(params))
        return [dict(row) for row in rows]

    def get_statistics(self) -> Dict:
        """統計情報取得"""
        total_prefs = self.execute_query("SELECT COUNT(*) FROM preferences")[0][0]
        total_logs = self.execute_query("SELECT COUNT(*) FROM behavior_logs")[0][0]
        total_recs = self.execute_query("SELECT COUNT(*) FROM recommendations")[0][0]

        # カテゴリ別分布
        categories = self.execute_query("""
            SELECT category, COUNT(*) as count
            FROM preferences
            GROUP BY category
            ORDER BY count DESC
        """)

        return {{
            "total_preferences": total_prefs,
            "total_behavior_logs": total_logs,
            "total_recommendations": total_recs,
            "category_distribution": [dict(cat) for cat in categories]
        }}

    def cleanup_old_records(self, days: int = 90) -> int:
        """古いレコードを削除"""
        query = """
            DELETE FROM behavior_logs
            WHERE timestamp < datetime('now', '-' || ? || ' days')
        """
        return self.execute_update(query, (days,))


if __name__ == "__main__":
    import json
    with PreferenceDB() as db:
        stats = db.get_statistics()
        print("統計情報:")
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
from db import PreferenceDB


class {agent['name'].replace('-', '_').title().replace('_', '')}Discord:
    """Discordボットインターフェース"""

    def __init__(self):
        self.db = PreferenceDB()

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

    def handle_add_preference(self, user_id: str, args: list) -> dict:
        """嗜好追加コマンド処理"""
        if len(args) < 2:
            return {{"error": "Usage: add <category> <item_id> [rating] [tags]"}}

        category = args[0]
        item_id = args[1]
        rating = float(args[2]) if len(args) > 2 and args[2].replace('.', '').isdigit() else None
        tags = " ".join(args[3:]) if len(args) > 3 else None

        pref_id = self.db.create_preference(category, item_id, rating, tags)

        # 行動ログ
        self.db.create_behavior_log(user_id, "add_preference", category, item_id)

        return {{
            "success": True,
            "message": f"嗜好を追加しました: {{category}}/{{item_id}}",
            "preference_id": pref_id
        }}

    def handle_list_preferences(self, user_id: str, args: list) -> dict:
        """嗜好一覧コマンド処理"""
        category = args[0] if len(args) > 0 else None

        preferences = self.db.list_preferences(category=category)

        if not preferences:
            return {{
                "success": True,
                "message": "嗜好が見つかりませんでした"
            }}

        # 整形
        lines = ["**嗜好一覧**"]
        for pref in preferences[:10]:  # 上位10件
            rating_str = f"⭐{{pref['rating']}}" if pref['rating'] else ""
            lines.append(f"- {{pref['category']}}/{{pref['item_id']}} {{rating_str}} ({{pref['interaction_count']}}回)")

        return {{
            "success": True,
            "message": "\\n".join(lines)
        }}

    def handle_analyze(self, user_id: str, args: list) -> dict:
        """分析コマンド処理"""
        category = args[0] if len(args) > 0 else None

        preferences = self.db.list_preferences(category=category)

        if not preferences:
            return {{
                "success": True,
                "message": "分析対象の嗜好が見つかりませんでした"
            }}

        # 簡易分析
        category_counts = {{}}
        total_rating = 0
        rating_count = 0

        for pref in preferences:
            cat = pref['category']
            category_counts[cat] = category_counts.get(cat, 0) + 1

            if pref['rating']:
                total_rating += pref['rating']
                rating_count += 1

        lines = ["**嗜好分析**"]
        lines.append(f"総アイテム数: {{len(preferences)}}")
        lines.append(f"総インタラクション: {{sum(p['interaction_count'] for p in preferences)}}")

        if rating_count > 0:
            lines.append(f"平均評価: {{total_rating / rating_count:.2f}}")

        lines.append("\\n**カテゴリ分布**:")
        for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"- {{cat}}: {{count}}アイテム")

        return {{
            "success": True,
            "message": "\\n".join(lines)
        }}

    def handle_recommend(self, user_id: str, args: list) -> dict:
        """推薦コマンド処理"""
        category = args[0] if len(args) > 0 else None

        # 行動履歴に基づいて推薦
        behavior = self.db.get_user_behavior(user_id, limit=50)

        if not behavior:
            return {{
                "success": True,
                "message": "行動履歴が不足しています。まずはいくつかのアイテムに反応してみてください。"
            }}

        # 簡易推薦: 頻度の高いカテゴリから提案
        category_freq = {{}}
        for log in behavior:
            cat = log['category']
            category_freq[cat] = category_freq.get(cat, 0) + 1

        top_category = max(category_freq.items(), key=lambda x: x[1])[0]

        # 推薦アイテムを取得
        if category:
            top_category = category

        preferences = self.db.list_preferences(category=top_category)

        if not preferences:
            return {{
                "success": True,
                "message": f"{{top_category}}カテゴリの推薦アイテムが見つかりませんでした"
            }}

        lines = ["**おすすめ**"]
        lines.append(f"カテゴリ: {{top_category}}")

        for pref in preferences[:5]:
            rating_str = f"⭐{{pref['rating']}}" if pref['rating'] else ""
            lines.append(f"- {{pref['item_id']}} {{rating_str}}")

        # 推薦ログ
        self.db.create_recommendation(
            user_id,
            top_category,
            ",".join([p['item_id'] for p in preferences[:5]]),
            "frequency-based",
            0.8
        )

        return {{
            "success": True,
            "message": "\\n".join(lines)
        }}

    def handle_stats(self, user_id: str, args: list) -> dict:
        """統計コマンド処理"""
        stats = self.db.get_statistics()

        lines = ["**統計情報**"]
        lines.append(f"総嗜好数: {{stats['total_preferences']}}")
        lines.append(f"総行動ログ: {{stats['total_behavior_logs']}}")
        lines.append(f"総推薦数: {{stats['total_recommendations']}}")

        if stats['category_distribution']:
            lines.append("\\n**カテゴリ別**:")
            for cat in stats['category_distribution'][:5]:
                lines.append(f"- {{cat['category']}}: {{cat['count']}}")

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
            "add": self.handle_add_preference,
            "list": self.handle_list_preferences,
            "analyze": self.handle_analyze,
            "recommend": self.handle_recommend,
            "stats": self.handle_stats
        }}

        handler = handlers.get(command)
        if handler:
            return handler(user_id, args)
        else:
            return {{
                "error": f"Unknown command: {{command}}\\nAvailable commands: add, list, analyze, recommend, stats"
            }}

    def format_response(self, response: dict) -> str:
        """レスポンスを整形"""
        if "error" in response:
            return f"❌ {{response['error']}}"

        if "message" in response:
            emoji_map = {{
                "add": "➕",
                "list": "📋",
                "analyze": "📊",
                "recommend": "🎯",
                "stats": "📈"
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

    # テスト: add
    result = bot.handle_command(user_id, "!pref add baseball npb-2024 5.0")
    print(f"add: {{bot.format_response(result)}}")

    # テスト: list
    result = bot.handle_command(user_id, "!pref list")
    print(f"list: {{bot.format_response(result)}}")

    # テスト: recommend
    result = bot.handle_command(user_id, "!pref recommend")
    print(f"recommend: {{bot.format_response(result)}}")
'''

def generate_readme(agent):
    """README.mdを生成"""
    return f'''# {agent['name']}

{agent['emoji']} {agent['description_ja']} / {agent['description_en']}

## 概要 (Overview)

このエージェントは、ユーザーの嗜好を分析し、パーソナライズされたレコメンデーションを提供します。

This agent analyzes user preferences and provides personalized recommendations.

## 機能 (Features)

- **嗜好管理** (Preference Management): ユーザーの好みを記録・管理
- **行動分析** (Behavior Analysis): ユーザーの行動履歴を分析
- **クロスカテゴリ推薦** (Cross-Category Recommendation): 複数カテゴリ間の関連性を考慮した推薦
- **機械学習推薦** (ML Recommendation): 行動データに基づく機械学習による推薦
- **フィードバック学習** (Feedback Learning): ユーザーフィードバックから学習して精度向上

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

# 嗜好追加
agent.add_preference("baseball", "npb-2024", 5.0, "プロ野球,日本")
agent.add_preference("game", "pokemon-scarlet", 4.0, "RPG,ポケモン")

# 分析実行
analysis = agent.analyze_preferences()
print(analysis)

# 接続を閉じる
agent.get_close()
```

### Discord Bot

```
!pref add <category> <item_id> [rating] [tags]
!pref list [category]
!pref analyze [category]
!pref recommend [category]
!pref stats
```

## データベース (Database)

- `preferences`: 嗜好データ
- `behavior_logs`: 行動ログ
- `recommendations`: 推薦履歴

## 環境変数 (Environment Variables)

- `DISCORD_TOKEN`: Discordボットトークン

## ライセンス (License)

MIT License
'''

def generate_requirements_txt(agent):
    """requirements.txtを生成"""
    return '''# Personalized Recommendation Agent Requirements

# Core
python-dotenv>=1.0.0

# Discord
discord.py>=2.3.0

# Database
sqlite3  # Python標準ライブラリ

# Machine Learning (推薦アルゴリズム用)
scikit-learn>=1.3.0
numpy>=1.24.0
pandas>=2.0.0

# Data Visualization
matplotlib>=3.7.0
seaborn>=0.12.0

# Optional: Advanced ML
torch>=2.0.0  # PyTorch for deep learning recommendations
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
    print("パーソナライズドレコメンデーションエージェント オーケストレーター")
    print("Personalized Recommendation Agent Orchestrator")
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
        if commit_changes(f"feat: パーソナライズドレコメンデーションエージェントプロジェクト完了 ({completed_count}/{total})"):
            push_changes()

    print(f"\n🎉 オーケストレーション完了！")
    print(f"\n作成されたエージェント:")
    for agent in AGENTS:
        status = progress["agents"].get(agent["name"], {}).get("status", "pending")
        emoji = "✅" if status == "completed" else "❌"
        print(f"  {emoji} {agent['name']} - {agent['description_ja']}")

if __name__ == "__main__":
    main()
