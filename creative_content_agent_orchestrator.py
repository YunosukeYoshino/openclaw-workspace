#!/usr/bin/env python3
"""
Creative Content Agent Orchestrator
クリエイティブコンテンツ関連エージェントを並行開発するオーケストレーター
"""

import os
import json
import sys
import time
from datetime import datetime

# プロジェクト設定
PROJECT_NAME = "Creative Content Agent Project"
AGENTS = [
    {
        "name": "artwork-agent",
        "description_ja": "イラスト・アートワーク管理エージェント",
        "description_en": "Illustration and artwork management agent",
        "features_ja": [
            "イラスト・アートワーク登録・管理",
            "アーティスト別作品リスト",
            "作品URL・SNSリンク保存",
            "タグ・カテゴリ管理"
        ],
        "features_en": [
            "Register and manage illustrations and artwork",
            "Work lists by artist",
            "Artwork URL and SNS link storage",
            "Tag and category management"
        ]
    },
    {
        "name": "fanart-agent",
        "description_ja": "ファンアートコレクション管理エージェント",
        "description_en": "Fanart collection management agent",
        "features_ja": [
            "ファンアート登録・管理",
            "キャラクター別ファンアート",
            "お気に入りファンアート登録",
            "ファンアートギャラリー"
        ],
        "features_en": [
            "Register and manage fanart",
            "Fanart by character",
            "Register favorite fanart",
            "Fanart gallery"
        ]
    },
    {
        "name": "doujin-agent",
        "description_ja": "同人誌・同人ソフト管理エージェント",
        "description_en": "Doujinshi and doujin software management agent",
        "features_ja": [
            "同人誌・同人ソフト登録・管理",
            "サークル情報管理",
            "イベント・コミケ情報",
            "購入・所持履歴"
        ],
        "features_en": [
            "Register and manage doujinshi and doujin software",
            "Circle information management",
            "Event and Comiket information",
            "Purchase and ownership history"
        ]
    },
    {
        "name": "figure-agent",
        "description_ja": "フィギュア・グッズコレクション管理エージェント",
        "description_en": "Figure and merchandise collection management agent",
        "features_ja": [
            "フィギュア・グッズ登録・管理",
            "メーカー・シリーズ別管理",
            "購入価格・販売価格管理",
            "所持・欲しいリスト"
        ],
        "features_en": [
            "Register and manage figures and merchandise",
            "Management by manufacturer and series",
            "Purchase price and selling price management",
            "Owned and wishlist"
        ]
    },
    {
        "name": "cosplay-agent",
        "description_ja": "コスプレ・衣装管理エージェント",
        "description_en": "Cosplay and costume management agent",
        "features_ja": [
            "コスプレ・衣装登録・管理",
            "キャラクター別衣装リスト",
            "素材・パーツ管理",
            "製作記録・写真管理"
        ],
        "features_en": [
            "Register and manage cosplay and costumes",
            "Costume lists by character",
            "Material and parts management",
            "Production records and photo management"
        ]
    }
]

class CreativeContentAgentOrchestrator:
    """クリエイティブコンテンツエージェントオーケストレーター"""

    def __init__(self):
        self.start_time = datetime.now()
        self.progress_file = "creative_content_agent_progress.json"
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

        # content table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                creator TEXT NOT NULL,
                source TEXT,
                url TEXT,
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
                content_id INTEGER,
                type TEXT NOT NULL,
                content TEXT,
                url TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (content_id) REFERENCES content (id)
            )
        """)

        self.conn.commit()

    def add_content(self, title: str, creator: str, source: str = None, url: str = None, description: str = None, tags: str = None) -> int:
        """コンテンツを追加する"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO content (title, creator, source, url, description, tags)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, creator, source, url, description, tags))
        self.conn.commit()
        return cursor.lastrowid

    def get_content(self, content_id: int) -> Optional[Dict[str, Any]]:
        """コンテンツを取得する"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM content WHERE id = ?', (content_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def list_content(self, creator: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """コンテンツリストを取得する"""
        cursor = self.conn.cursor()
        if creator:
            cursor.execute('SELECT * FROM content WHERE creator = ? ORDER BY created_at DESC LIMIT ?', (creator, limit))
        else:
            cursor.execute('SELECT * FROM content ORDER BY created_at DESC LIMIT ?', (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def search_content(self, query: str) -> List[Dict[str, Any]]:
        """コンテンツを検索する"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM content
            WHERE title LIKE ? OR creator LIKE ? OR description LIKE ? OR tags LIKE ?
            ORDER BY created_at DESC
        """, (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
        return [dict(row) for row in cursor.fetchall()]

    def add_entry(self, content_id: int, entry_type: str, content: str = None, url: str = None, metadata: str = None) -> int:
        """エントリーを追加する"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO entries (content_id, type, content, url, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (content_id, entry_type, content, url, metadata))
        self.conn.commit()
        return cursor.lastrowid

    def get_entries(self, content_id: int, entry_type: str = None) -> List[Dict[str, Any]]:
        """エントリーリストを取得する"""
        cursor = self.conn.cursor()
        if entry_type:
            cursor.execute("""
                SELECT * FROM entries
                WHERE content_id = ? AND type = ?
                ORDER BY created_at DESC
            """, (content_id, entry_type))
        else:
            cursor.execute("""
                SELECT * FROM entries
                WHERE content_id = ?
                ORDER BY created_at DESC
            """, (content_id,))
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
            description="Creative Content Management Agent",
            color=discord.Color.orange()
        )
        embed.add_field(name="Description", value="Creative content and artwork management", inline=False)
        embed.add_field(name="Commands", value="`!add`, `!list`, `!search`, `!gallery`", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def add(self, ctx, title: str, creator: str, *, url: str = ""):
        """コンテンツを追加する"""
        await ctx.send(f"Adding content: {{title}} by {{creator}}")
        # データベースに追加する処理をここに実装

    @commands.command()
    async def list(self, ctx, creator: Optional[str] = None):
        """コンテンツリストを表示する"""
        if creator:
            await ctx.send(f"Listing content by {{creator}}")
        else:
            await ctx.send("Listing all content")
        # データベースから取得する処理をここに実装

    @commands.command()
    async def search(self, ctx, *, query: str):
        """コンテンツを検索する"""
        await ctx.send(f"Searching for: {{query}}")
        # 検索処理をここに実装

    @commands.command()
    async def gallery(self, ctx):
        """ギャラリーを表示する"""
        await ctx.send("Opening gallery...")
        # ギャラリーを表示する処理をここに実装

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
| `!add <title> <creator> [url]` | コンテンツを追加 / Add content |
| `!list [creator]` | コンテンツリスト表示 / List content |
| `!search <query>` | コンテンツ検索 / Search content |
| `!gallery` | ギャラリー表示 / Show gallery |

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
    orchestrator = CreativeContentAgentOrchestrator()
    success = orchestrator.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
