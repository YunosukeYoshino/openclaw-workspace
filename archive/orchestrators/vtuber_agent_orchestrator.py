#!/usr/bin/env python3
"""
VTuber Agent Orchestrator
VTuber関連エージェントを並行開発するオーケストレーター
"""

import os
import json
import sys
import time
from datetime import datetime

# プロジェクト設定
PROJECT_NAME = "VTuber Agent Project"
AGENTS = [
    {
        "name": "vtuber-schedule-agent",
        "description_ja": "VTuber配信スケジュール管理エージェント",
        "description_en": "VTuber streaming schedule management agent",
        "features_ja": [
            "VTuber配信スケジュール登録・管理",
            "予定通知・リマインダー",
            "複数VTuberのスケジュール一覧",
            "コラボ配信特別表示"
        ],
        "features_en": [
            "Register and manage VTuber streaming schedules",
            "Schedule notifications and reminders",
            "Multiple VTuber schedule list",
            "Special display for collab streams"
        ]
    },
    {
        "name": "vtuber-archive-agent",
        "description_ja": "VTuberアーカイブ管理エージェント",
        "description_en": "VTuber archive management agent",
        "features_ja": [
            "アーカイブ動画URL管理",
            "お気に入りアーカイブ登録",
            "タグ・カテゴリ管理",
            "視聴履歴・メモ"
        ],
        "features_en": [
            "Archive video URL management",
            "Register favorite archives",
            "Tag and category management",
            "Watch history and notes"
        ]
    },
    {
        "name": "vtuber-news-agent",
        "description_ja": "VTuberニュース・コラボ情報収集エージェント",
        "description_en": "VTuber news and collaboration information collection agent",
        "features_ja": [
            "VTuberニュース収集",
            "コラボ配信情報",
            "イベント・フェス情報",
            "新規デビュー情報"
        ],
        "features_en": [
            "Collect VTuber news",
            "Collaboration streaming information",
            "Event and festival information",
            "New debut information"
        ]
    },
    {
        "name": "vtuber-merch-agent",
        "description_ja": "VTuberグッズ情報管理エージェント",
        "description_en": "VTuber merchandise information management agent",
        "features_ja": [
            "グッズ情報登録・管理",
            "販売サイトURL保存",
            "購入履歴管理",
            "欲しいリスト作成"
        ],
        "features_en": [
            "Register and manage merchandise information",
            "Store sales site URLs",
            "Purchase history management",
            "Create wishlist"
        ]
    },
    {
        "name": "vtuber-ranking-agent",
        "description_ja": "VTuberランキング・統計エージェント",
        "description_en": "VTuber ranking and statistics agent",
        "features_ja": [
            "登録者数ランキング",
            "配信視聴数統計",
            "成長率計算",
            "お気に入りVTuber比較"
        ],
        "features_en": [
            "Subscriber count rankings",
            "Streaming view count statistics",
            "Growth rate calculation",
            "Compare favorite VTubers"
        ]
    }
]

class VTuberAgentOrchestrator:
    """VTuberエージェントオーケストレーター"""

    def __init__(self):
        self.start_time = datetime.now()
        self.progress_file = "vtuber_agent_progress.json"
        self.progress = self.load_progress()

    def load_progress(self):
        """進捗管理ファイルを読み込む"""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "project": PROJECT_NAME,
            "start_time": self.start_time.isoformat(),
            "agents": {},
            "total": len(AGENTS),
            "completed": 0
        }

    def save_progress(self):
        """進捗を保存する"""
        self.progress["last_update"] = datetime.now().isoformat()
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, ensure_ascii=False, indent=2)

    def create_agent_directory(self, agent_name):
        """エージェントディレクトリを作成する"""
        agent_path = f"agents/{agent_name}"
        if not os.path.exists(agent_path):
            os.makedirs(agent_path, exist_ok=True)
            return agent_path
        return None  # 既に存在

    def generate_agent_code(self, agent):
        """エージェントコードを生成する"""
        agent_name = agent["name"]
        description_ja = agent["description_ja"]
        description_en = agent["description_en"]
        features_en = agent["features_en"]
        class_name = self._to_class_name(agent_name)

        agent_template = '''#!/usr/bin/env python3
"""
{agent_name}
{description_ja} / {description_en}
"""

import os
import sys
from datetime import datetime

class {class_name}:
    """{description_ja}"""

    def __init__(self):
        self.agent_name = "{agent_name}"
        self.description = "{description_en}"
        self.features = {features_en}

    def get_agent_info(self):
        """エージェント情報を取得する"""
        return {{
            "name": self.agent_name,
            "description": self.description,
            "features": self.features
        }}

    def run(self):
        """エージェントを実行する"""
        print(f"{{self.agent_name}} is running...")
        # エージェントのメインロジックをここに実装
        return {{"status": "running", "timestamp": datetime.now().isoformat()}}

if __name__ == "__main__":
    agent = {class_name}()
    print(agent.get_agent_info())
    print(agent.run())
'''

        agent_code = agent_template.replace("{agent_name}", agent_name).replace("{description_ja}", description_ja).replace("{description_en}", description_en).replace("{class_name}", class_name)
        return agent_code

    def generate_db_code(self, agent):
        """データベースコードを生成する"""
        agent_name = agent["name"]
        class_name = self._to_class_name(agent_name)

        db_template = '''#!/usr/bin/env python3
"""
{agent_name} Database Module
SQLite database for {agent_name}
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

class {class_name}Database:
    """Database for {agent_name}"""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), "{agent_name}.db")
        self.db_path = db_path
        self.conn = None
        self.connect()
        self.create_tables()

    def connect(self):
        """データベースに接続する"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        """データベース接続を閉じる"""
        if self.conn:
            self.conn.close()

    def create_tables(self):
        """テーブルを作成する"""
        cursor = self.conn.cursor()

        # vtubers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vtubers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                channel_url TEXT,
                description TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # entries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vtuber_id INTEGER,
                type TEXT NOT NULL,
                title TEXT,
                content TEXT,
                url TEXT,
                scheduled_time TIMESTAMP,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vtuber_id) REFERENCES vtubers (id)
            )
        """)

        self.conn.commit()

    def add_vtuber(self, name: str, channel_url: str = None, description: str = None, tags: str = None) -> int:
        """VTuberを追加する"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO vtubers (name, channel_url, description, tags)
            VALUES (?, ?, ?, ?)
        """, (name, channel_url, description, tags))
        self.conn.commit()
        return cursor.lastrowid

    def get_vtuber(self, vtuber_id: int) -> Optional[Dict[str, Any]]:
        """VTuberを取得する"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM vtubers WHERE id = ?', (vtuber_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def list_vtubers(self, limit: int = 100) -> List[Dict[str, Any]]:
        """VTuberリストを取得する"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM vtubers ORDER BY created_at DESC LIMIT ?', (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def search_vtubers(self, query: str) -> List[Dict[str, Any]]:
        """VTuberを検索する"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM vtubers
            WHERE name LIKE ? OR description LIKE ? OR tags LIKE ?
            ORDER BY created_at DESC
        """, (f'%{query}%', f'%{query}%', f'%{query}%'))
        return [dict(row) for row in cursor.fetchall()]

    def add_entry(self, vtuber_id: int, entry_type: str, title: str = None, content: str = None, url: str = None, scheduled_time: str = None, metadata: str = None) -> int:
        """エントリーを追加する"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO entries (vtuber_id, type, title, content, url, scheduled_time, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (vtuber_id, entry_type, title, content, url, scheduled_time, metadata))
        self.conn.commit()
        return cursor.lastrowid

    def get_entries(self, vtuber_id: int, entry_type: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """エントリーリストを取得する"""
        cursor = self.conn.cursor()
        if entry_type:
            cursor.execute("""
                SELECT * FROM entries
                WHERE vtuber_id = ? AND type = ?
                ORDER BY created_at DESC LIMIT ?
            """, (vtuber_id, entry_type, limit))
        else:
            cursor.execute("""
                SELECT * FROM entries
                WHERE vtuber_id = ?
                ORDER BY created_at DESC LIMIT ?
            """, (vtuber_id, limit))
        return [dict(row) for row in cursor.fetchall()]

    def get_upcoming_streams(self, days: int = 7) -> List[Dict[str, Any]]:
        """近日の配信を取得する"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT e.*, v.name as vtuber_name
            FROM entries e
            JOIN vtubers v ON e.vtuber_id = v.id
            WHERE e.type = 'stream'
            AND e.scheduled_time >= datetime('now')
            AND e.scheduled_time <= datetime('now', '+' || ? || ' days')
            ORDER BY e.scheduled_time ASC
        """, (days,))
        return [dict(row) for row in cursor.fetchall()]

if __name__ == "__main__":
    db = {class_name}Database()
    print(f"Database initialized: {{db.db_path}}")
'''

        db_code = db_template.replace("{agent_name}", agent_name).replace("{class_name}", class_name)
        return db_code

    def generate_discord_code(self, agent):
        """Discord Botコードを生成する"""
        agent_name = agent["name"]
        class_name = self._to_class_name(agent_name)

        discord_template = '''#!/usr/bin/env python3
"""
{agent_name} Discord Bot
Discord bot interface for {agent_name}
"""

import discord
from discord.ext import commands
from typing import Optional
import os

class {class_name}Bot(commands.Bot):
    """Discord Bot for {agent_name}"""

    def __init__(self, command_prefix: str = "!"):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.agent_name = "{agent_name}"

    async def on_ready(self):
        """Bot起動時の処理"""
        print(f'{{self.user.name}} has connected to Discord!')

    async def on_message(self, message: discord.Message):
        """メッセージ受信時の処理"""
        if message.author == self.user:
            return

        await self.process_commands(message)

    @commands.command()
    async def info(self, ctx):
        """エージェント情報を表示する"""
        embed = discord.Embed(
            title=f"{{self.agent_name}}",
            description="VTuber Management Agent",
            color=discord.Color.purple()
        )
        embed.add_field(name="Description", value="VTuber tracking and management", inline=False)
        embed.add_field(name="Commands", value="`!add`, `!list`, `!search`, `!upcoming`", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def add(self, ctx, name: str, *, description: str = ""):
        """VTuberを追加する"""
        await ctx.send(f"Adding VTuber: {{name}}")
        # データベースに追加する処理をここに実装

    @commands.command()
    async def list(self, ctx):
        """VTuberリストを表示する"""
        await ctx.send("Listing VTubers")
        # データベースから取得する処理をここに実装

    @commands.command()
    async def search(self, ctx, *, query: str):
        """VTuberを検索する"""
        await ctx.send(f"Searching for: {{query}}")
        # 検索処理をここに実装

    @commands.command()
    async def upcoming(self, ctx, days: int = 7):
        """近日の配信を表示する"""
        await ctx.send(f"Upcoming streams in next {{days}} days")
        # 近日の配信を表示する処理をここに実装

def main():
    """Botを起動する"""
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("DISCORD_TOKEN environment variable is required")
        return

    bot = {class_name}Bot()
    bot.run(token)

if __name__ == "__main__":
    main()
'''

        discord_code = discord_template.replace("{agent_name}", agent_name).replace("{class_name}", class_name)
        return discord_code

    def generate_readme(self, agent):
        """READMEを生成する"""
        agent_name = agent["name"]
        description_ja = agent["description_ja"]
        description_en = agent["description_en"]
        features_ja = agent["features_ja"]
        features_en = agent["features_en"]

        readme = f'''# {agent_name}

{description_ja} / {description_en}

## 機能 / Features

### 日本語 / Japanese
{chr(10).join(f"- {f}" for f in features_ja)}

### English / 英語
{chr(10).join(f"- {f}" for f in features_en)}

## インストール / Installation

```bash
pip install -r requirements.txt
```

## 使用方法 / Usage

### エージェント実行 / Running the Agent

```bash
python3 agent.py
```

### Discord Bot / Discord Bot

```bash
export DISCORD_TOKEN="your_bot_token"
python3 discord.py
```

## データベース / Database

SQLiteデータベースを使用しています。初回実行時に自動的に作成されます。

## コマンド / Commands

| コマンド / Command | 説明 / Description |
|-------------------|-------------------|
| `!add <name> [description]` | VTuberを追加 / Add VTuber |
| `!list` | VTuberリスト表示 / List VTubers |
| `!search <query>` | VTuber検索 / Search VTubers |
| `!upcoming [days]` | 近日の配信表示 / Show upcoming streams |

## ライセンス / License

MIT License
'''

        return readme

    def generate_requirements(self):
        """requirements.txtを生成する"""
        return '''discord.py>=2.3.2
'''

    def _to_class_name(self, snake_str):
        """snake_caseをCamelCaseに変換する"""
        components = snake_str.split('-')
        return ''.join(x.title().replace('_', '') for x in components)

    def create_agent(self, agent):
        """エージェントを作成する"""
        agent_name = agent["name"]

        # ディレクトリ作成
        agent_path = self.create_agent_directory(agent_name)
        if not agent_path:
            print(f"  ⚠️  ディレクトリ既存: {agent_name}")
            return False

        # ファイル作成
        with open(f"{agent_path}/agent.py", 'w', encoding='utf-8') as f:
            f.write(self.generate_agent_code(agent))
        print(f"  ✅ agent.py")

        with open(f"{agent_path}/db.py", 'w', encoding='utf-8') as f:
            f.write(self.generate_db_code(agent))
        print(f"  ✅ db.py")

        with open(f"{agent_path}/discord.py", 'w', encoding='utf-8') as f:
            f.write(self.generate_discord_code(agent))
        print(f"  ✅ discord.py")

        with open(f"{agent_path}/README.md", 'w', encoding='utf-8') as f:
            f.write(self.generate_readme(agent))
        print(f"  ✅ README.md")

        with open(f"{agent_path}/requirements.txt", 'w', encoding='utf-8') as f:
            f.write(self.generate_requirements())
        print(f"  ✅ requirements.txt")

        # 進捗を更新
        self.progress["agents"][agent_name] = {
            "status": "completed",
            "path": agent_path,
            "completed_at": datetime.now().isoformat()
        }
        self.progress["completed"] = len([a for a in self.progress["agents"].values() if a["status"] == "completed"])
        self.save_progress()

        return True

    def run(self):
        """オーケストレーターを実行する"""
        print(f"🚀 {PROJECT_NAME} 開始")
        print(f"📅 開始時刻: {self.start_time.isoformat()}")
        print(f"📊 エージェント数: {len(AGENTS)}")
        print()

        completed_count = 0

        for agent in AGENTS:
            agent_name = agent["name"]
            print(f"🔧 作成中: {agent_name}")

            # 既に完了しているか確認
            if agent_name in self.progress["agents"] and self.progress["agents"][agent_name]["status"] == "completed":
                print(f"  ⏭️  既に完了")
                completed_count += 1
                continue

            # エージェントを作成
            if self.create_agent(agent):
                print(f"  ✅ 完了")
                completed_count += 1
            else:
                print(f"  ⚠️  スキップ")

            print()

        # 結果表示
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        print("=" * 50)
        print("📊 結果サマリ")
        print("=" * 50)
        print(f"✅ 完了: {completed_count}/{len(AGENTS)}")
        print(f"⏱️  実行時間: {duration:.2f}秒")
        print(f"🕐 終了時刻: {end_time.isoformat()}")
        print()

        if completed_count == len(AGENTS):
            print("🎉 プロジェクト完了！")
            return True
        else:
            print(f"⚠️  {len(AGENTS) - completed_count}個のエージェントが未完了")
            return False

def main():
    orchestrator = VTuberAgentOrchestrator()
    success = orchestrator.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
