#!/usr/bin/env python3
"""
次期プロジェクト案 V23 オーケストレーター
- 野球ファンコミュニティ・ソーシャルエージェント (5個)
- ゲームマーケティング・プロモーションエージェント (5個)
- えっちコンテンツセキュリティ・プライバシーエージェント (5個)
- 野球コーチング・トレーニングエージェント (5個)
- ゲームアクセシビリティ・インクルージョンエージェント (5個)
"""

import os
import json
from pathlib import Path
from datetime import datetime

PROGRESS_FILE = "v23_progress.json"

# V23 プロジェクト定義
PROJECTS = {
    "baseball_fan_community": {
        "name": "野球ファンコミュニティ・ソーシャルエージェント",
        "name_en": "Baseball Fan Community & Social Agents",
        "description": "野球ファンコミュニティの交流を強化し、ソーシャル機能を拡充するエージェント群。",
        "agents": [
            {
                "id": "baseball-fan-forum-agent",
                "name": "野球ファンフォーラムエージェント",
                "name_en": "Baseball Fan Forum Agent",
                "description": "野球ファン専用フォーラムの管理、スレッド作成、モデレーション機能を提供します。",
                "features": [
                    "フォーラムスレッドの自動作成・管理",
                    "スパム・不適切コンテンツのモデレーション",
                    "人気トピックのハイライト",
                    "ユーザーランク・バッジシステム"
                ]
            },
            {
                "id": "baseball-fan-social-sharing-agent",
                "name": "野球ファンSNS共有エージェント",
                "name_en": "Baseball Fan Social Sharing Agent",
                "description": "試合の見せ場、ファン体験をSNSで共有する機能を提供します。",
                "features": [
                    "SNS連携によるシェア機能",
                    "自動生成シェアテンプレート",
                    "チーム別ハッシュタグ管理",
                    "バズった投稿の追跡・分析"
                ]
            },
            {
                "id": "baseball-fan-messenger-agent",
                "name": "野球ファンメッセンジャーエージェント",
                "name_en": "Baseball Fan Messenger Agent",
                "description": "ファン同士のリアルタイムメッセージング、グループチャット機能を提供します。",
                "features": [
                    "1対1メッセージング",
                    "グループチャット・ルーム作成",
                    "試合中のリアルタイムチャット",
                    "メッセージ履歴・検索"
                ]
            },
            {
                "id": "baseball-fan-event-organizer-agent",
                "name": "野球ファンイベントオーガナイザーエージェント",
                "name_en": "Baseball Fan Event Organizer Agent",
                "description": "オフライン・オンラインイベントの企画・管理を支援します。",
                "features": [
                    "観戦イベントの企画・告知",
                    "参加者登録・管理",
                    "イベントリマインダー通知",
                    "イベント後のフィードバック収集"
                ]
            },
            {
                "id": "baseball-fan-leaderboard-agent",
                "name": "野球ファンリーダーボードエージェント",
                "name_en": "Baseball Fan Leaderboard Agent",
                "description": "ファン活動に基づくリーダーボード・ランキングシステムを提供します。",
                "features": [
                    "投稿・参加回数によるスコア計算",
                    "チーム別・期間別ランキング",
                    "実績・バッジの付与",
                    "ランキング履歴の表示"
                ]
            }
        ]
    },
    "game_marketing": {
        "name": "ゲームマーケティング・プロモーションエージェント",
        "name_en": "Game Marketing & Promotion Agents",
        "description": "ゲームのマーケティング、プロモーション、ユーザー獲得を支援するエージェント群。",
        "agents": [
            {
                "id": "game-campaign-manager-agent",
                "name": "ゲームキャンペーンマネージャーエージェント",
                "name_en": "Game Campaign Manager Agent",
                "description": "マーケティングキャンペーンの企画・実行・分析を支援します。",
                "features": [
                    "マルチチャネルキャンペーン管理",
                    "A/Bテストの設定・分析",
                    "ROI追跡・レポート",
                    "ターゲットセグメント設定"
                ]
            },
            {
                "id": "game-influencer-connect-agent",
                "name": "ゲームインフルエンサー連携エージェント",
                "name_en": "Game Influencer Connect Agent",
                "description": "インフルエンサーとの連携、プロモーション企画を管理します。",
                "features": [
                    "インフルエンサーデータベース管理",
                    "プロモーション提案の作成",
                    "連携状況の追跡",
                    "成果測定・分析"
                ]
            },
            {
                "id": "game-content-marketing-agent",
                "name": "ゲームコンテンツマーケティングエージェント",
                "name_en": "Game Content Marketing Agent",
                "description": "ブログ記事、動画、SNSコンテンツの作成・配信を支援します。",
                "features": [
                    "コンテンツカレンダー管理",
                    "SEO最適化の提案",
                    "コンテンツ効果の分析",
                    "マルチフォーマット出力"
                ]
            },
            {
                "id": "game-community-growth-agent",
                "name": "ゲームコミュニティ成長エージェント",
                "name_en": "Game Community Growth Agent",
                "description": "コミュニティの成長戦略、エンゲージメント向上を支援します。",
                "features": [
                    "コミュニティメトリクス追跡",
                    "成長戦略の提案",
                    "ユーザーリテンション分析",
                    "ボラタイルユーザーの検出"
                ]
            },
            {
                "id": "game-pr-manager-agent",
                "name": "ゲームPRマネージャーエージェント",
                "name_en": "Game PR Manager Agent",
                "description": "広報活動、プレスリリース、メディア対応を支援します。",
                "features": [
                    "プレスリリース作成・配信",
                    "メディアリスト管理",
                    "クライシス管理対応",
                    "プレスイベント企画"
                ]
            }
        ]
    },
    "erotic_security": {
        "name": "えっちコンテンツセキュリティ・プライバシーエージェント",
        "name_en": "Erotic Content Security & Privacy Agents",
        "description": "えっちコンテンツのセキュリティ保護、プライバシー維持を支援するエージェント群。",
        "agents": [
            {
                "id": "erotic-access-control-agent",
                "name": "えっちアクセス制御エージェント",
                "name_en": "Erotic Access Control Agent",
                "description": "年齢認証、アクセス権限管理、コンテンツ保護機能を提供します。",
                "features": [
                    "年齢認証システム",
                    "ユーザーレベルに応じたアクセス制御",
                    "地域別コンテンツ規制対応",
                    "不正アクセス検知"
                ]
            },
            {
                "id": "erotic-privacy-guard-agent",
                "name": "えっちプライバシーガードエージェント",
                "name_en": "Erotic Privacy Guard Agent",
                "description": "ユーザー閲覧履歴、好みの保護・管理機能を提供します。",
                "features": [
                    "閲覧履歴の暗号化保存",
                    "匿名化設定オプション",
                    "データ削除・エクスポート",
                    "プライバシー設定管理"
                ]
            },
            {
                "id": "erotic-content-filter-agent",
                "name": "えっちコンテンツフィルターエージェント",
                "name_en": "Erotic Content Filter Agent",
                "description": "不適切コンテンツの検出・フィルタリング機能を提供します。",
                "features": [
                    "AIによる不適切コンテンツ検出",
                    "ユーザー設定に応じたフィルタリング",
                    "コンテンツレーティング管理",
                    "通報・検閲機能"
                ]
            },
            {
                "id": "erotic-security-audit-agent",
                "name": "えっちセキュリティ監査エージェント",
                "name_en": "Erotic Security Audit Agent",
                "description": "システムのセキュリティ監査、脆弱性検出機能を提供します。",
                "features": [
                    "定期的セキュリティスキャン",
                    "脆弱性レポート作成",
                    "アクセスログ監査",
                    "コンプライアンスチェック"
                ]
            },
            {
                "id": "erotic-dmca-agent",
                "name": "えっちDMCAエージェント",
                "name_en": "Erotic DMCA Agent",
                "description": "著作権侵害の検出・対応、DMCA管理機能を提供します。",
                "features": [
                    "著作権侵害コンテンツ検出",
                    "DMCAテイクダウン管理",
                    "権利者データベース管理",
                    "法令遵守チェック"
                ]
            }
        ]
    },
    "baseball_coaching": {
        "name": "野球コーチング・トレーニングエージェント",
        "name_en": "Baseball Coaching & Training Agents",
        "description": "野球のコーチング、トレーニング、スキル向上を支援するエージェント群。",
        "agents": [
            {
                "id": "baseball-swing-analyzer-agent",
                "name": "野球スイング分析エージェント",
                "name_en": "Baseball Swing Analyzer Agent",
                "description": "スイング動画のAI分析、改善提案機能を提供します。",
                "features": [
                    "動画からのスイング軌道分析",
                    "バットスピード・角度の計測",
                    "プロ選手との比較",
                    "改善ドリルの提案"
                ]
            },
            {
                "id": "baseball-pitching-coach-agent",
                "name": "野球ピッチングコーチエージェント",
                "name_en": "Baseball Pitching Coach Agent",
                "description": "投球フォームの分析、球種開発、コーチング機能を提供します。",
                "features": [
                    "投球フォームのAI分析",
                    "球速・回転数の追跡",
                    "球種開発アドバイス",
                    "怪我予防チェック"
                ]
            },
            {
                "id": "baseball-drill-planner-agent",
                "name": "野球ドリルプランナーエージェント",
                "name_en": "Baseball Drill Planner Agent",
                "description": "個人レベルに合わせた練習メニューの作成・管理機能を提供します。",
                "features": [
                    "スキルレベル別ドリル提案",
                    "練習スケジュール作成",
                    "進捗追跡・記録",
                    "バリエーション豊富なドリル"
                ]
            },
            {
                "id": "baseball-mental-game-agent",
                "name": "野球メンタルゲームエージェント",
                "name_en": "Baseball Mental Game Agent",
                "description": "メンタルトレーニング、集中力向上のサポート機能を提供します。",
                "features": [
                    "メンタル強化エクササイズ",
                    "試合前のルーティーン作成",
                    "ストレス管理テクニック",
                    "自信構築プログラム"
                ]
            },
            {
                "id": "baseball-fitness-agent",
                "name": "野球フィットネスエージェント",
                "name_en": "Baseball Fitness Agent",
                "description": "野球選手向けのフィットネス・筋トレプログラムを提供します。",
                "features": [
                    "ポジション別トレーニング",
                    "怪我予防エクササイズ",
                    "柔軟性・可動域改善",
                    "シーズン中・オフシーズンプログラム"
                ]
            }
        ]
    },
    "game_accessibility": {
        "name": "ゲームアクセシビリティ・インクルージョンエージェント",
        "name_en": "Game Accessibility & Inclusion Agents",
        "description": "ゲームのアクセシビリティ向上、インクルージョン推進を支援するエージェント群。",
        "agents": [
            {
                "id": "game-audio-accessibility-agent",
                "name": "ゲーム音声アクセシビリティエージェント",
                "name_en": "Game Audio Accessibility Agent",
                "description": "視覚障害者向けの音声ガイド、音響アクセシビリティ機能を提供します。",
                "features": [
                    "画面読み上げ機能",
                    "3Dオーディオナビゲーション",
                    "音声による状況説明",
                    "音量・音声速度調整"
                ]
            },
            {
                "id": "game-visual-accessibility-agent",
                "name": "ゲーム視覚アクセシビリティエージェント",
                "name_en": "Game Visual Accessibility Agent",
                "description": "視覚的なアクセシビリティ機能、色覚サポートを提供します。",
                "features": [
                    "高コントラストモード",
                    "色覚多様性対応",
                    "フォントサイズ・UI調整",
                    "視覚補助オプション"
                ]
            },
            {
                "id": "game-motor-accessibility-agent",
                "name": "ゲーム運動機能アクセシビリティエージェント",
                "name_en": "Game Motor Accessibility Agent",
                "description": "運動障害者向けのコントロールカスタマイズ機能を提供します。",
                "features": [
                    "ボタンリマップ機能",
                    "片手操作モード",
                    "自動入力補助",
                    "入力感度調整"
                ]
            },
            {
                "id": "game-cognitive-accessibility-agent",
                "name": "ゲーム認知アクセシビリティエージェント",
                "name_en": "Game Cognitive Accessibility Agent",
                "description": "認知特性に合わせたゲーム設定・サポート機能を提供します。",
                "features": [
                    "難易度動的調整",
                    "チュートリアル・ヒント機能",
                    "ペース調整オプション",
                    "情報量調整"
                ]
            },
            {
                "id": "game-inclusion-designer-agent",
                "name": "ゲームインクルージョンデザイナーエージェント",
                "name_en": "Game Inclusion Designer Agent",
                "description": "多様なプレイヤーを考慮したゲームデザインのレビュー・提案機能を提供します。",
                "features": [
                    "アクセシビリティチェックリスト",
                    "多様性表現のレビュー",
                    "デザイン改善提案",
                    "ユーザーフィードバック収集"
                ]
            }
        ]
    }
}


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"completed_agents": [], "completed_projects": [], "started_at": datetime.utcnow().isoformat()}


def save_progress(progress):
    progress["updated_at"] = datetime.utcnow().isoformat()
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)


def create_agent_dir(project_id, agent_info):
    agent_id = agent_info["id"]
    dir_path = Path(f"agents/{project_id}/{agent_id}")
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def generate_agent_code(project_id, project_info, agent_info):
    agent_id = agent_info["id"]
    name = agent_info["name"]
    name_en = agent_info["name_en"]
    description = agent_info["description"]
    features = agent_info["features"]

    # agent.py
    agent_code = f'''#!/usr/bin/env python3
\"\"\"
{name} / {name_en}

{description}

Features:
{chr(10).join(f"- [FEATURE] {f}" for f in features)}
\"\"\"

import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any


class {to_class_name(agent_id)}:
    \"\"\"{name} - {name_en}\"\"\"

    def __init__(self):
        self.agent_id = "{agent_id}"
        self.name = "{name}"
        self.name_en = "{name_en}"
        self.description = "{description}"

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"Process input and return results.\"\"\"
        # TODO: Implement processing logic
        return {{
            "status": "success",
            "agent_id": self.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "result": input_data
        }}

    async def get_features(self) -> List[str]:
        \"\"\"Return list of available features.\"\"\"
        return {json.dumps(features, ensure_ascii=False)}


def main():
    agent = {to_class_name(agent_id)}()
    print(f"Agent initialized: {{agent.name}}")


if __name__ == "__main__":
    main()
'''

    # db.py
    db_code = f'''#!/usr/bin/env python3
\"\"\"
{name} - Database Module

SQLite-based database management for {name_en}.
\"\"\"

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any


class {to_class_name(agent_id)}DB:
    \"\"\"Database manager for {name}\"\"\"

    def __init__(self, db_path: str = "data/{agent_id}.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self.init_db()

    def init_db(self):
        \"\"\"Initialize database tables.\"\"\"
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Main table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Tags table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            """)

            # Entry-tags junction table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entry_tags (
                    entry_id INTEGER,
                    tag_id INTEGER,
                    PRIMARY KEY (entry_id, tag_id),
                    FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE,
                    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
                )
            """)

            conn.commit()

    def get_connection(self) -> sqlite3.Connection:
        \"\"\"Get database connection.\"\"\"
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self):
        \"\"\"Close database connection.\"\"\"
        if self.conn:
            self.conn.close()
            self.conn = None

    def add_entry(self, title: str, content: str, metadata: str = None, tags: List[str] = None) -> int:
        \"\"\"Add a new entry.\"\"\"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO entries (title, content, metadata) VALUES (?, ?, ?)",
                (title, content, metadata)
            )
            entry_id = cursor.lastrowid

            if tags:
                for tag_name in tags:
                    cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
                    cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
                    tag_id = cursor.fetchone()["id"]
                    cursor.execute("INSERT INTO entry_tags (entry_id, tag_id) VALUES (?, ?)",
                                 (entry_id, tag_id))

            conn.commit()
            return entry_id

    def get_entries(self, status: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        \"\"\"Retrieve entries.\"\"\"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute("SELECT * FROM entries WHERE status = ? ORDER BY created_at DESC LIMIT ?",
                             (status, limit))
            else:
                cursor.execute("SELECT * FROM entries ORDER BY created_at DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def update_entry_status(self, entry_id: int, status: str) -> bool:
        \"\"\"Update entry status.\"\"\"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE entries SET status = ?, updated_at = ? WHERE id = ?",
                (status, datetime.utcnow().isoformat(), entry_id)
            )
            conn.commit()
            return cursor.rowcount > 0


def main():
    db = {to_class_name(agent_id)}DB()
    print(f"Database initialized for {agent_id}")


if __name__ == "__main__":
    main()
'''

    # discord.py
    discord_code = f'''#!/usr/bin/env python3
\"\"\"
{name} - Discord Integration

Discord bot integration for {name_en}.
\"\"\"

import discord
from discord.ext import commands
from typing import Optional


class {to_class_name(agent_id)}Discord(commands.Cog):
    \"\"\"Discord Cog for {name}\"\"\"

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="{agent_id}_help")
    async def help_command(self, ctx):
        \"\"\"Show help for {name}\"\"\"
        embed = discord.Embed(
            title="{name} / {name_en}",
            description="{agent_info['description']}",
            color=discord.Color.blue()
        )
        features = {json.dumps(agent_info["features"], ensure_ascii=False)}
        for i, feature in enumerate(features, 1):
            embed.add_field(name=f"Feature {{i}}", value=feature, inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="{agent_id}_status")
    async def status_command(self, ctx):
        \"\"\"Show status of {name}\"\"\"
        await ctx.send(f"✅ {name} is operational")


def setup(bot):
    bot.add_cog({to_class_name(agent_id)}Discord(bot))
    print(f"Discord Cog loaded: {agent_id}")


def main():
    # Standalone execution for testing
    intents = discord.Intents.default()
    bot = commands.Bot(command_prefix="!", intents=intents)
    setup(bot)
    print(f"Discord integration ready for {agent_id}")


if __name__ == "__main__":
    main()
'''

    # README.md
    readme_content = f'''# {name} / {name_en}

{description}

## Features

{chr(10).join(f"- {f}" for f in features)}

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Command Line

```bash
python agent.py
python db.py
python discord.py
```

### As Module

```python
from agent import {to_class_name(agent_id)}
from db import {to_class_name(agent_id)}DB

# Initialize agent
agent = {to_class_name(agent_id)}()

# Initialize database
db = {to_class_name(agent_id)}DB()

# Process data
result = await agent.process({{"input": "data"}})
```

## Discord Commands

- `!{agent_id}_help` - Show help information
- `!{agent_id}_status` - Show agent status

## Database Schema

### entries

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| title | TEXT | Entry title |
| content | TEXT | Entry content |
| metadata | TEXT | Additional metadata (JSON) |
| status | TEXT | Entry status (active/archived/completed) |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

### tags

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | TEXT | Tag name (unique) |

### entry_tags

| Column | Type | Description |
|--------|------|-------------|
| entry_id | INTEGER | Reference to entries.id |
| tag_id | INTEGER | Reference to tags.id |

## API Reference

### {to_class_name(agent_id)}

#### `process(input_data: Dict[str, Any]) -> Dict[str, Any]`

Process input data and return results.

**Parameters:**
- `input_data`: Dictionary containing input data

**Returns:**
- Dictionary with processing results

#### `get_features() -> List[str]`

Return list of available features.

**Returns:**
- List of feature names

### {to_class_name(agent_id)}DB

#### `add_entry(title, content, metadata=None, tags=None) -> int`

Add a new entry to the database.

**Parameters:**
- `title`: Entry title
- `content`: Entry content
- `metadata`: Optional metadata (JSON string)
- `tags`: Optional list of tag names

**Returns:**
- ID of the created entry

#### `get_entries(status=None, limit=100) -> List[Dict[str, Any]]`

Retrieve entries from the database.

**Parameters:**
- `status`: Optional filter by status
- `limit`: Maximum number of entries to return

**Returns:**
- List of entry dictionaries

#### `update_entry_status(entry_id, status) -> bool`

Update the status of an entry.

**Parameters:**
- `entry_id`: ID of the entry to update
- `status`: New status value

**Returns:**
- True if update was successful

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.
'''

    # requirements.txt
    requirements = '''discord.py>=2.3.0
python-dotenv>=1.0.0
'''

    return {
        "agent.py": agent_code,
        "db.py": db_code,
        "discord.py": discord_code,
        "README.md": readme_content,
        "requirements.txt": requirements
    }


def to_class_name(agent_id: str) -> str:
    """Convert agent ID to class name."""
    parts = agent_id.replace("-", "_").split("_")
    return "".join(p.capitalize() for p in parts)


def write_agent_files(dir_path, files):
    for filename, content in files.items():
        file_path = dir_path / filename
        file_path.write_text(content, encoding="utf-8")
        print(f"  Created: {file_path}")


def create_agent(project_id, project_info, agent_info, progress):
    dir_path = create_agent_dir(project_id, agent_info)
    print(f"Creating agent: {agent_info['id']}")

    files = generate_agent_code(project_id, project_info, agent_info)
    write_agent_files(dir_path, files)

    progress["completed_agents"].append(agent_info["id"])
    save_progress(progress)


def run():
    print("=" * 60)
    print("次期プロジェクト案 V23 オーケストレーター")
    print("=" * 60)

    progress = load_progress()

    for project_id, project_info in PROJECTS.items():
        print(f"\\n📦 Project: {project_info['name']}")

        if project_id in progress.get("completed_projects", []):
            print(f"  ✓ Already completed")
            continue

        project_started = False
        for agent_info in project_info["agents"]:
            agent_id = agent_info["id"]

            if agent_id in progress["completed_agents"]:
                print(f"  ✓ {agent_id}: Already created")
                continue

            if not project_started:
                project_started = True
                print(f"  Starting project...")

            create_agent(project_id, project_info, agent_info, progress)

        if project_started:
            progress["completed_projects"].append(project_id)
            save_progress(progress)
            print(f"  ✓ Project {project_id} completed!")

    # Summary
    print("\\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Total agents created: {len(progress['completed_agents'])}/{sum(len(p['agents']) for p in PROJECTS.values())}")
    print(f"Total projects completed: {len(progress['completed_projects'])}/{len(PROJECTS)}")

    if len(progress['completed_agents']) == sum(len(p['agents']) for p in PROJECTS.values()):
        print("\\n🎉 All agents created successfully!")
    else:
        print("\\n⚠️  Some agents remain. Run again to continue.")


if __name__ == "__main__":
    run()
