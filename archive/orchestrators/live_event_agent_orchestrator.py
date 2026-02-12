#!/usr/bin/env python3
"""
Live Event Agent Orchestrator
ライブイベント・コンサート関連エージェントを並行開発するオーケストレーター
"""

import os
import json
import sys
import time
from datetime import datetime

# プロジェクト設定
PROJECT_NAME = "Live Event Agent Project"
AGENTS = [
    {
        "name": "live-event-schedule-agent",
        "description_ja": "ライブイベント・コンサートスケジュール管理エージェント",
        "description_en": "Live event and concert schedule management agent",
        "features_ja": [
            "ライブイベントスケジュール登録・管理",
            "アーティスト別イベント一覧",
            "開催場所・会場情報管理",
            "イベント通知・リマインダー"
        ],
        "features_en": [
            "Register and manage live event schedules",
            "Event lists by artist",
            "Venue and location information management",
            "Event notifications and reminders"
        ]
    },
    {
        "name": "live-event-ticket-agent",
        "description_ja": "チケット販売・予約管理エージェント",
        "description_en": "Ticket sales and reservation management agent",
        "features_ja": [
            "チケット販売情報管理",
            "予約状況トラッキング",
            "販売サイトURL保存",
            "購入履歴管理"
        ],
        "features_en": [
            "Ticket sales information management",
            "Reservation status tracking",
            "Sales site URL storage",
            "Purchase history management"
        ]
    },
    {
        "name": "live-event-voting-agent",
        "description_ja": "投票・アンケート管理エージェント",
        "description_en": "Voting and survey management agent",
        "features_ja": [
            "投票・アンケート作成",
            "投票結果集計",
            "複数選択・ランク投票対応",
            "投票履歴・統計"
        ],
        "features_en": [
            "Create voting and surveys",
            "Aggregate voting results",
            "Multiple choice and ranking voting support",
            "Voting history and statistics"
        ]
    },
    {
        "name": "live-event-recap-agent",
        "description_ja": "イベントレポート・まとめ作成エージェント",
        "description_en": "Event report and summary creation agent",
        "features_ja": [
            "イベントレポート作成",
            "写真・動画管理",
            "参加者感想・コメント",
            "イベントハイライトまとめ"
        ],
        "features_en": [
            "Create event reports",
            "Photo and video management",
            "Participant impressions and comments",
            "Event highlights summary"
        ]
    },
    {
        "name": "live-stream-info-agent",
        "description_ja": "ライブ配信情報・アーカイブ管理エージェント",
        "description_en": "Live streaming information and archive management agent",
        "features_ja": [
            "ライブ配信スケジュール管理",
            "アーカイブ動画URL管理",
            "配信プラットフォーム対応",
            "視聴履歴・メモ"
        ],
        "features_en": [
            "Live streaming schedule management",
            "Archive video URL management",
            "Streaming platform support",
            "Watch history and notes"
        ]
    }
]

class LiveEventAgentOrchestrator:
    """ライブイベントエージェントオーケストレーター"""

    def __init__(self):
        self.start_time = datetime.now()
        self.progress_file = "live_event_agent_progress.json"
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

        # events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist TEXT NOT NULL,
                venue TEXT,
                event_date TIMESTAMP,
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
                event_id INTEGER,
                type TEXT NOT NULL,
                content TEXT,
                url TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES events (id)
            )
        """)

        self.conn.commit()

    def add_event(self, title: str, artist: str, venue: str = None, event_date: str = None, description: str = None, tags: str = None) -> int:
        """イベントを追加する"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO events (title, artist, venue, event_date, description, tags)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, artist, venue, event_date, description, tags))
        self.conn.commit()
        return cursor.lastrowid

    def get_event(self, event_id: int) -> Optional[Dict[str, Any]]:
        """イベントを取得する"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM events WHERE id = ?', (event_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def list_events(self, artist: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """イベントリストを取得する"""
        cursor = self.conn.cursor()
        if artist:
            cursor.execute('SELECT * FROM events WHERE artist = ? ORDER BY event_date DESC LIMIT ?', (artist, limit))
        else:
            cursor.execute('SELECT * FROM events ORDER BY event_date DESC LIMIT ?', (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def search_events(self, query: str) -> List[Dict[str, Any]]:
        """イベントを検索する"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM events
            WHERE title LIKE ? OR artist LIKE ? OR venue LIKE ? OR tags LIKE ?
            ORDER BY event_date DESC
        """, (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
        return [dict(row) for row in cursor.fetchall()]

    def add_entry(self, event_id: int, entry_type: str, content: str = None, url: str = None, metadata: str = None) -> int:
        """エントリーを追加する"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO entries (event_id, type, content, url, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (event_id, entry_type, content, url, metadata))
        self.conn.commit()
        return cursor.lastrowid

    def get_entries(self, event_id: int, entry_type: str = None) -> List[Dict[str, Any]]:
        """エントリーリストを取得する"""
        cursor = self.conn.cursor()
        if entry_type:
            cursor.execute("""
                SELECT * FROM entries
                WHERE event_id = ? AND type = ?
                ORDER BY created_at DESC
            """, (event_id, entry_type))
        else:
            cursor.execute("""
                SELECT * FROM entries
                WHERE event_id = ?
                ORDER BY created_at DESC
            """, (event_id,))
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
            description="Live Event Management Agent",
            color=discord.Color.red()
        )
        embed.add_field(name="Description", value="Live event and concert management", inline=False)
        embed.add_field(name="Commands", value="`!add`, `!list`, `!search`, `!upcoming`", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def add(self, ctx, title: str, artist: str, *, venue: str = ""):
        """イベントを追加する"""
        await ctx.send(f"Adding event: {{title}} by {{artist}}")
        # データベースに追加する処理をここに実装

    @commands.command()
    async def list(self, ctx, artist: Optional[str] = None):
        """イベントリストを表示する"""
        if artist:
            await ctx.send(f"Listing events by {{artist}}")
        else:
            await ctx.send("Listing all events")
        # データベースから取得する処理をここに実装

    @commands.command()
    async def search(self, ctx, *, query: str):
        """イベントを検索する"""
        await ctx.send(f"Searching for: {{query}}")
        # 検索処理をここに実装

    @commands.command()
    async def upcoming(self, ctx, days: int = 30):
        """近日のイベントを表示する"""
        await ctx.send(f"Upcoming events in next {{days}} days")
        # 近日のイベントを表示する処理をここに実装

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
| `!add <title> <artist> [venue]` | イベントを追加 / Add event |
| `!list [artist]` | イベントリスト表示 / List events |
| `!search <query>` | イベント検索 / Search events |
| `!upcoming [days]` | 近日のイベント表示 / Show upcoming events |

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
    orchestrator = LiveEventAgentOrchestrator()
    success = orchestrator.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
