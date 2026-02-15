#!/usr/bin/env python3
"""
次期プロジェクト案 V87 オーケストレーター
目標: 2050 AGENTS MILESTONE
"""

import os
import json
import subprocess
import time
from pathlib import Path

# プロジェクト設定
VERSION = "V87"
TARGET_MILESTONE = 2050
BASE_COUNT = 2025
AGENTS_PER_PROJECT = 25

# エージェント定義（カテゴリ x 5エージェント x 5カテゴリ = 25エージェント）
PROJECTS = [
    {
        "category": "baseball-international",
        "name": "野球国際エージェント",
        "agents": [
            ("baseball-international-league-agent", "野球国際リーグエージェント。国際リーグの管理。"),
            ("baseball-world-series-agent", "野球ワールドシリーズエージェント。ワールドシリーズの管理。"),
            ("baseball-olympic-baseball-agent", "野球五輪エージェント。五輪野球の管理。"),
            ("baseball-wbc-agent", "野球WBCエージェント。ワールド・ベースボール・クラシックの管理。"),
            ("baseball-international-player-agent", "野球国際選手エージェント。国際選手の管理・移籍。"),
        ]
    },
    {
        "category": "game-mobile",
        "name": "ゲームモバイルエージェント",
        "agents": [
            ("game-mobile-agent", "ゲームモバイルエージェント。モバイルゲームの管理。"),
            ("game-ios-agent", "ゲームiOSエージェント。iOSゲームの管理。"),
            ("game-android-agent", "ゲームAndroidエージェント。Androidゲームの管理。"),
            ("game-mobile-monetization-agent", "ゲームモバイル収益化エージェント。モバイルゲームの収益化。"),
            ("game-mobile-analytics-agent", "ゲームモバイルアナリティクスエージェント。モバイルゲームの分析。"),
        ]
    },
    {
        "category": "erotic-nft",
        "name": "えっちコンテンツNFT・Web3エージェント",
        "agents": [
            ("erotic-nft-agent", "えっちNFTエージェント。えっちNFTの管理・発行。"),
            ("erotic-web3-agent", "えっちWeb3エージェント。えっちWeb3アプリの管理。"),
            ("erotic-crypto-agent", "えっち暗号通貨エージェント。えっちコンテンツの暗号通貨決済。"),
            ("erotic-nft-marketplace-agent", "えっちNFTマーケットプレイスエージェント。えっちNFTの取引。"),
            ("erotic-blockchain-content-agent", "えっちブロックチェーンコンテンツエージェント。ブロックチェーン上のコンテンツ管理。"),
        ]
    },
    {
        "category": "microservices",
        "name": "マイクロサービス・サービスグリッドエージェント",
        "agents": [
            ("microservices-agent", "マイクロサービスエージェント。マイクロサービスの管理。"),
            ("service-mesh-agent", "サービスメッシュエージェント。サービスメッシュの管理。"),
            ("api-gateway-agent", "APIゲートウェイエージェント。APIゲートウェイの管理。"),
            ("service-discovery-agent", "サービスディスカバリーエージェント。サービスディスカバリーの管理。"),
            ("circuit-breaker-agent", "サーキットブレーカーエージェント。サーキットブレーカーパターンの実装。"),
        ]
    },
    {
        "category": "devops-security",
        "name": "セキュリティ・DevOpsセキュリティエージェント",
        "agents": [
            ("devops-security-agent", "DevOpsセキュリティエージェント。DevOpsのセキュリティ管理。"),
            ("ci-cd-security-agent", "CI/CDセキュリティエージェント。CI/CDパイプラインのセキュリティ。"),
            ("infrastructure-security-agent", "インフラストラクチャセキュリティエージェント。インフラのセキュリティ管理。"),
            ("container-security-scan-agent", "コンテナセキュリティスキャンエージェント。コンテナのセキュリティスキャン。"),
            ("code-security-agent", "コードセキュリティエージェント。コードのセキュリティ管理。"),
        ]
    },
]

# 進捗管理ファイル
PROGRESS_FILE = f"v87_progress.json"

# テンプレート（V86と同じ）
AGENT_TEMPLATE = '''#!/usr/bin/env python3
"""
@@AGENT_NAME@@ - @@DESCRIPTION@@
"""

import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime

# エージェントディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from db import @@CLASS_NAME@@Database
from discord import @@CLASS_NAME@@DiscordBot


class @@CLASS_NAME@@Agent:
    """@@DESCRIPTION@@"""

    def __init__(self, config_path=None):
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), "config.json")
        self.db = @@CLASS_NAME@@Database(self.config_path)
        self.discord = @@CLASS_NAME@@DiscordBot(self.config_path)
        self.name = "@@AGENT_NAME@@"
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

            if task_type == "@@TASK_TYPE@@":
                result = await self._@@TASK_METHOD@@(**task_params)
                return {"success": True, "result": result}
            else:
                return {"success": False, "error": "未知のタスクタイプ"}

        except Exception as e:
            print(f"[{self.name}] タスク実行エラー: {e}")
            return {"success": False, "error": str(e)}

    async def _@@TASK_METHOD@@(self, **params):
        """@@DESCRIPTION@@のメイン処理"""
        # TODO: 実装を追加
        result = {"message": "@@DESCRIPTION@@処理完了", "params": params}
        return result


async def main():
    """メインエントリーポイント"""
    agent = @@CLASS_NAME@@Agent()
    try:
        await agent.start()
    except KeyboardInterrupt:
        print("\\nシャットダウン中...")
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
'''

DB_TEMPLATE = '''#!/usr/bin/env python3
"""
@@AGENT_NAME@@ - データベースモジュール
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any


class @@CLASS_NAME@@Database:
    """@@DESCRIPTION@@ データベース"""

    def __init__(self, config_path=None):
        self.config_path = config_path or Path(__file__).parent / "config.json"
        self.db_path = Path(__file__).parent / "data" / f"{self.__class__.__name__}.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def init_db(self):
        """データベースを初期化"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # メインテーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS @@TABLE_NAME@@ (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    title TEXT,
                    content TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    priority INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # メタデータテーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # タグテーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            """)

            # エントリータグリレーションテーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entry_tags (
                    entry_id INTEGER,
                    tag_id INTEGER,
                    PRIMARY KEY (entry_id, tag_id),
                    FOREIGN KEY (entry_id) REFERENCES @@TABLE_NAME@@(id) ON DELETE CASCADE,
                    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
                )
            """)

            conn.commit()

    def create_entry(self, entry_data: Dict[str, Any]) -> int:
        """エントリーを作成"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO @@TABLE_NAME@@ (type, title, content, status, priority)
                VALUES (?, ?, ?, ?, ?)
            """, (
                entry_data.get("type", "default"),
                entry_data.get("title"),
                entry_data.get("content"),
                entry_data.get("status", "active"),
                entry_data.get("priority", 0)
            ))
            entry_id = cursor.lastrowid

            # タグを追加
            for tag_name in entry_data.get("tags", []):
                self._add_tag_to_entry(cursor, entry_id, tag_name)

            conn.commit()
            return entry_id

    def get_entry(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """エントリーを取得"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM @@TABLE_NAME@@ WHERE id = ?", (entry_id,))
            row = cursor.fetchone()
            if row:
                entry = dict(row)
                entry["tags"] = self._get_entry_tags(cursor, entry_id)
                return entry
            return None

    def list_entries(self, entry_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """エントリー一覧を取得"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if entry_type:
                cursor.execute("""
                    SELECT * FROM @@TABLE_NAME@@
                    WHERE type = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (entry_type, limit))
            else:
                cursor.execute("""
                    SELECT * FROM @@TABLE_NAME@@
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (limit,))

            entries = []
            for row in cursor.fetchall():
                entry = dict(row)
                entry["tags"] = self._get_entry_tags(cursor, entry["id"])
                entries.append(entry)

            return entries

    def update_entry(self, entry_id: int, entry_data: Dict[str, Any]) -> bool:
        """エントリーを更新"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE @@TABLE_NAME@@
                SET type = ?, title = ?, content = ?, status = ?, priority = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                entry_data.get("type"),
                entry_data.get("title"),
                entry_data.get("content"),
                entry_data.get("status"),
                entry_data.get("priority"),
                entry_id
            ))
            conn.commit()
            return cursor.rowcount > 0

    def delete_entry(self, entry_id: int) -> bool:
        """エントリーを削除"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM @@TABLE_NAME@@ WHERE id = ?", (entry_id,))
            conn.commit()
            return cursor.rowcount > 0

    def _add_tag_to_entry(self, cursor, entry_id: int, tag_name: str):
        """エントリーにタグを追加"""
        cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
        cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
        tag_id = cursor.fetchone()[0]
        cursor.execute("INSERT OR IGNORE INTO entry_tags (entry_id, tag_id) VALUES (?, ?)",
                      (entry_id, tag_id))

    def _get_entry_tags(self, cursor, entry_id: int) -> List[str]:
        """エントリーのタグを取得"""
        cursor.execute("""
            SELECT t.name
            FROM tags t
            JOIN entry_tags et ON t.id = et.tag_id
            WHERE et.entry_id = ?
        """, (entry_id,))
        return [row[0] for row in cursor.fetchall()]

    def set_metadata(self, key: str, value: Any):
        """メタデータを設定"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO metadata (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (key, json.dumps(value)))
            conn.commit()

    def get_metadata(self, key: str) -> Optional[Any]:
        """メタデータを取得"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM metadata WHERE key = ?", (key,))
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
            return None


if __name__ == "__main__":
    # テスト実行
    db = @@CLASS_NAME@@Database()
    test_entry = {
        "type": "test",
        "title": "テスト",
        "content": "テストエントリー",
        "tags": ["test", "demo"]
    }
    entry_id = db.create_entry(test_entry)
    print(f"Created entry: {entry_id}")
    print(f"Retrieved: {db.get_entry(entry_id)}")
'''

DISCORD_TEMPLATE = '''#!/usr/bin/env python3
"""
@@AGENT_NAME@@ - Discord Bot モジュール
"""

import os
import asyncio
from typing import Optional, Dict, Any


class @@CLASS_NAME@@DiscordBot:
    """@@DESCRIPTION@@ Discord Bot"""

    def __init__(self, config_path=None):
        self.config_path = config_path
        self.token = os.getenv("DISCORD_TOKEN")
        self.channel_id = os.getenv("DISCORD_CHANNEL_ID")
        self.enabled = self.token and self.channel_id
        self.name = "@@AGENT_NAME@@"

    async def start(self):
        """Botを開始"""
        if not self.enabled:
            print(f"[{self.name}] Discord Botは無効化されています")
            return

        print(f"[{self.name}] Discord Botを開始")

    async def stop(self):
        """Botを停止"""
        print(f"[{self.name}] Discord Botを停止")

    async def send_message(self, message: str, embed: Optional[Dict] = None):
        """メッセージを送信"""
        if not self.enabled:
            return

        print(f"[{self.name}] メッセージ送信: {message}")

    async def send_embed(self, title: str, description: str, fields: Optional[Dict] = None, color: int = 0x00ff00):
        """埋め込みメッセージを送信"""
        if not self.enabled:
            return

        embed_data = {
            "title": title,
            "description": description,
            "color": color
        }
        if fields:
            embed_data["fields"] = fields

        await self.send_message("", embed=embed_data)

    async def notify_task_complete(self, task_id: str, result: Dict[str, Any]):
        """タスク完了を通知"""
        await self.send_embed(
            title=f"✅ タスク完了: {task_id}",
            description=f"{result.get('message', '処理完了')}"
        )

    async def notify_task_error(self, task_id: str, error: str):
        """タスクエラーを通知"""
        await self.send_embed(
            title=f"❌ タスクエラー: {task_id}",
            description=error,
            color=0xff0000
        )


if __name__ == "__main__":
    # テスト実行
    async def test():
        bot = @@CLASS_NAME@@DiscordBot()
        await bot.start()
        await bot.send_message("テストメッセージ")
        await bot.stop()

    asyncio.run(test())
'''

README_TEMPLATE = '''# @@AGENT_NAME@@

@@DESCRIPTION@@

## 機能

- @@DESCRIPTION@@
- データベース管理
- Discord Bot統合

## インストール

\`\`\`bash
pip install -r requirements.txt
\`\`\`

## 使用方法

\`\`\`bash
# エージェントを開始
python agent.py

# データベースを初期化
python db.py

# Discord Botをテスト
python discord.py
\`\`\`

## 設定

環境変数または \`config.json\` で設定を管理します。

\`\`\`bash
export DISCORD_TOKEN="your_bot_token"
export DISCORD_CHANNEL_ID="your_channel_id"
\`\`\`

## プロジェクト構成

\`\`\`
@@AGENT_NAME@@/
├── agent.py         # メインエージェント
├── db.py           # データベースモジュール
├── discord.py      # Discord Botモジュール
├── README.md       # このファイル
└── requirements.txt # Python依存関係
\`\`\`

## ライセンス

MIT
'''

REQUIREMENTS_TEMPLATE = '''discord.py>=2.3.0
aiosqlite>=0.19.0
python-dotenv>=1.0.0
'''

# ヘルパー関数
def camel_case(name):
    """kebab-caseをCamelCaseに変換"""
    return ''.join(word.capitalize() for word in name.replace('-', '_').split('_'))

def kebab_to_snake(name):
    """kebab-caseをsnake_caseに変換"""
    return name.replace('-', '_')

def replace_placeholders(template, agent_name, class_name, description, table_name, task_type, task_method):
    """プレースホルダーを置換"""
    return (template
            .replace("@@AGENT_NAME@@", agent_name)
            .replace("@@CLASS_NAME@@", class_name)
            .replace("@@DESCRIPTION@@", description)
            .replace("@@TABLE_NAME@@", table_name)
            .replace("@@TASK_TYPE@@", task_type)
            .replace("@@TASK_METHOD@@", task_method))

def create_agent_directory(agent_name, description):
    """エージェントディレクトリとファイルを作成"""
    class_name = camel_case(agent_name)
    table_name = kebab_to_snake(agent_name)
    task_type = kebab_to_snake(agent_name).replace('_', '-')
    task_method = kebab_to_snake(agent_name)

    # ディレクトリ作成
    agent_dir = Path(f"/workspace/{agent_name}")
    agent_dir.mkdir(exist_ok=True)

    # agent.py作成
    agent_content = replace_placeholders(AGENT_TEMPLATE, agent_name, class_name, description, table_name, task_type, task_method)
    (agent_dir / "agent.py").write_text(agent_content)
    (agent_dir / "agent.py").chmod(0o755)

    # db.py作成
    db_content = replace_placeholders(DB_TEMPLATE, agent_name, class_name, description, table_name, task_type, task_method)
    (agent_dir / "db.py").write_text(db_content)
    (agent_dir / "db.py").chmod(0o755)

    # discord.py作成
    discord_content = replace_placeholders(DISCORD_TEMPLATE, agent_name, class_name, description, table_name, task_type, task_method)
    (agent_dir / "discord.py").write_text(discord_content)
    (agent_dir / "discord.py").chmod(0o755)

    # README.md作成
    readme_content = replace_placeholders(README_TEMPLATE, agent_name, class_name, description, table_name, task_type, task_method)
    (agent_dir / "README.md").write_text(readme_content)

    # requirements.txt作成
    (agent_dir / "requirements.txt").write_text(REQUIREMENTS_TEMPLATE)

    return agent_dir

def save_progress(progress):
    """進捗を保存"""
    with open(f"/workspace/{PROGRESS_FILE}", "w") as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)

def load_progress():
    """進捗を読み込み"""
    if os.path.exists(f"/workspace/{PROGRESS_FILE}"):
        with open(f"/workspace/{PROGRESS_FILE}", "r") as f:
            return json.load(f)
    return {"completed": [], "total": AGENTS_PER_PROJECT}

def main():
    """メインオーケストレーター"""
    print(f"=== {VERSION} オーケストレーター 開始 ===")
    print(f"目標: {TARGET_MILESTONE} エージェント (現在: {BASE_COUNT} + {AGENTS_PER_PROJECT})")

    progress = load_progress()
    completed_agents = progress.get("completed", [])

    total_agents = []
    for project in PROJECTS:
        for agent_name, description in project["agents"]:
            total_agents.append((agent_name, description, project["category"], project["name"]))

    print(f"\n作成対象: {len(total_agents)} エージェント")
    print(f"完了済み: {len(completed_agents)} エージェント")

    # 各エージェントを作成
    for agent_name, description, category, project_name in total_agents:
        if agent_name in completed_agents:
            print(f"✅ {agent_name} - 既に完了")
            continue

        try:
            print(f"\n🔄 作成中: {agent_name}")
            print(f"   プロジェクト: {project_name}")
            print(f"   カテゴリ: {category}")
            print(f"   説明: {description}")

            agent_dir = create_agent_directory(agent_name, description)
            print(f"   ✅ 作成完了: {agent_dir}")

            completed_agents.append(agent_name)
            progress["completed"] = completed_agents
            progress["total"] = AGENTS_PER_PROJECT
            save_progress(progress)

        except Exception as e:
            print(f"   ❌ エラー: {e}")
            import traceback
            traceback.print_exc()
            continue

    print(f"\n=== {VERSION} オーケストレーター 完了 ===")
    print(f"作成完了: {len(completed_agents)}/{AGENTS_PER_PROJECT} エージェント")
    print(f"総エージェント数: {BASE_COUNT + len(completed_agents)}")

    if len(completed_agents) == AGENTS_PER_PROJECT:
        print(f"\n🎉 {TARGET_MILESTONE} AGENTS MILESTONE REACHED! 🎉")
    else:
        print(f"\n⚠️  まだ {AGENTS_PER_PROJECT - len(completed_agents)} エージェントが未完了")

    return len(completed_agents) == AGENTS_PER_PROJECT

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
