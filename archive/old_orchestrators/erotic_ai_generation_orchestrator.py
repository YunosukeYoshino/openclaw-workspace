#!/usr/bin/env python3
"""
えっちコンテンツ高度生成エージェントオーケストレーター

AIによる高度なコンテンツ生成エージェントプロジェクト

プロジェクト:
- erotic-ai-story-agent - えっちAIストーリーエージェント
- erotic-ai-scene-agent - えっちAIシーンエージェント
- erotic-ai-dialogue-agent - えっちAIダイアログエージェント
- erotic-style-transfer-agent - えっちスタイル変換エージェント
- erotic-creative-assistant-agent - えっち創作アシスタントエージェント

各エージェント:
- agent.py - エージェント本体
- db.py - SQLiteデータベースモジュール
- discord.py - Discord Botモジュール
- README.md - ドキュメント（バイリンガル）
- requirements.txt - 依存パッケージ
"""

import json
import os
from pathlib import Path
from datetime import datetime
import subprocess

# エージェント情報
PROJECT_NAME = "えっちコンテンツ高度生成エージェント"
AGENTS = [
    {
        "name": "erotic-ai-story-agent",
        "title": "えっちAIストーリーエージェント",
        "description": "AIによるえっちなストーリー・プロット生成エージェント",
        "tables": ["stories", "characters", "scenarios"]
    },
    {
        "name": "erotic-ai-scene-agent",
        "title": "えっちAIシーンエージェント",
        "description": "AIによるえっちなシーン・情景描写生成エージェント",
        "tables": ["scenes", "locations", "moods"]
    },
    {
        "name": "erotic-ai-dialogue-agent",
        "title": "えっちAIダイアログエージェント",
        "description": "AIによるえっちな会話・対話生成エージェント",
        "tables": ["dialogues", "characters", "conversations"]
    },
    {
        "name": "erotic-style-transfer-agent",
        "title": "えっちスタイル変換エージェント",
        "description": "コンテンツのスタイル・トーン変換エージェント",
        "tables": ["styles", "templates", "transformations"]
    },
    {
        "name": "erotic-creative-assistant-agent",
        "title": "えっち創作アシスタントエージェント",
        "description": "創作活動の支援・アイデア提案エージェント",
        "tables": ["ideas", "prompts", "projects"]
    }
]

# ワークスペース
WORKSPACE = Path("/workspace")
AGENTS_DIR = WORKSPACE / "agents"
PROGRESS_FILE = WORKSPACE / "erotic_ai_generation_progress.json"

# テンプレート
AGENT_TEMPLATE = '''#!/usr/bin/env python3
"""
{title}

{description}
"""

import sqlite3
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class {class_name}:
    """{title}"""

    def __init__(self, db_path: str = "{name}.db"):
        """初期化"""
        self.db_path = db_path
        self.conn = None
        self._initialize_db()

    def _initialize_db(self):
        """データベース初期化"""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()

        # エントリーテーブル作成
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT NOT NULL,
                tags TEXT,
                priority INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        {table_creates}

        self.conn.commit()
        logger.info("Database initialized")

    def add_entry(self, title: str, content: str, tags: Optional[str] = None, priority: int = 0) -> int:
        """エントリー追加"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO entries (title, content, tags, priority) VALUES (?, ?, ?, ?)",
            (title, content, tags, priority)
        )
        self.conn.commit()
        entry_id = cursor.lastrowid
        logger.info(f"Entry added: {{title}} (ID: {{entry_id}})")
        return entry_id

    def get_entry(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """エントリー取得"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None

    def list_entries(self, limit: int = 100, status: str = None) -> List[Dict[str, Any]]:
        """エントリーリスト取得"""
        cursor = self.conn.cursor()
        if status:
            cursor.execute(
                "SELECT * FROM entries WHERE status = ? ORDER BY created_at DESC LIMIT ?",
                (status, limit)
            )
        else:
            cursor.execute("SELECT * FROM entries ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    def update_entry(self, entry_id: int, **kwargs) -> bool:
        """エントリー更新"""
        valid_fields = ['title', 'content', 'tags', 'priority', 'status']
        update_fields = {{k: v for k, v in kwargs.items() if k in valid_fields}}
        if not update_fields:
            return False

        update_fields['updated_at'] = str(datetime.now())
        set_clause = ', '.join([f"{{k}} = ?" for k in update_fields.keys()])
        values = list(update_fields.values()) + [entry_id]

        cursor = self.conn.cursor()
        cursor.execute(f"UPDATE entries SET {{set_clause}} WHERE id = ?", values)
        self.conn.commit()
        logger.info(f"Entry updated: ID {{entry_id}}")
        return True

    def delete_entry(self, entry_id: int) -> bool:
        """エントリー削除"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
        self.conn.commit()
        if cursor.rowcount > 0:
            logger.info(f"Entry deleted: ID {{entry_id}}")
            return True
        return False

    def search_entries(self, query: str) -> List[Dict[str, Any]]:
        """エントリー検索"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM entries WHERE title LIKE ? OR content LIKE ? OR tags LIKE ?",
            (f"%{{query}}%", f"%{{query}}%", f"%{{query}}%")
        )
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    def get_stats(self) -> Dict[str, int]:
        """統計情報取得"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM entries WHERE status = 'active'")
        active = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM entries")
        total = cursor.fetchone()[0]
        return {{"active": active, "total": total}}

    def close(self):
        """データベース接続を閉じる"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")


def main():
    """メイン関数"""
    agent = {class_name}()
    print(f"{{agent.__class__.__name__}} initialized")
    print(f"Stats: {{agent.get_stats()}}")
    agent.close()


if __name__ == "__main__":
    main()
'''

DB_TEMPLATE = '''#!/usr/bin/env python3
"""
{title} - データベースモジュール

SQLiteデータベース操作モジュール
"""

import sqlite3
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from contextlib import contextmanager
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class {db_class_name}:
    """{title} データベースクラス"""

    def __init__(self, db_path: str = "{name}.db"):
        """初期化

        Args:
            db_path: データベースファイルパス
        """
        self.db_path = db_path

    @contextmanager
    def get_connection(self):
        """データベース接続コンテキストマネージャー"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {{e}}")
            raise
        finally:
            conn.close()

    def initialize_db(self):
        """データベース初期化"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # エントリーテーブル作成
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    content TEXT NOT NULL,
                    tags TEXT,
                    priority INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # {table_name_lower}_テーブル作成
            {table_creates}

            logger.info("Database initialized")

    def execute_query(self, query: str, params: Tuple = (), fetch: bool = True) -> Optional[List[Dict]]:
        """クエリ実行

        Args:
            query: SQLクエリ
            params: パラメータ
            fetch: 結果を取得するかどうか

        Returns:
            クエリ結果（fetch=Trueの場合）
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            if fetch:
                return [dict(row) for row in cursor.fetchall()]
            return None

    def add_entry(self, title: str, content: str, tags: Optional[str] = None, priority: int = 0) -> int:
        """エントリー追加

        Args:
            title: タイトル
            content: コンテンツ
            tags: タグ
            priority: 優先度

        Returns:
            エントリーID
        """
        result = self.execute_query(
            "INSERT INTO entries (title, content, tags, priority) VALUES (?, ?, ?, ?) RETURNING id",
            (title, content, tags, priority)
        )
        entry_id = result[0]['id'] if result else None
        logger.info(f"Entry added: {{title}} (ID: {{entry_id}})")
        return entry_id

    def get_entry(self, entry_id: int) -> Optional[Dict]:
        """エントリー取得

        Args:
            entry_id: エントリーID

        Returns:
            エントリーデータ
        """
        result = self.execute_query("SELECT * FROM entries WHERE id = ?", (entry_id,))
        return result[0] if result else None

    def list_entries(self, limit: int = 100, status: str = None) -> List[Dict]:
        """エントリーリスト取得

        Args:
            limit: 取得件数
            status: ステータスフィルタ

        Returns:
            エントリーリスト
        """
        if status:
            return self.execute_query(
                "SELECT * FROM entries WHERE status = ? ORDER BY created_at DESC LIMIT ?",
                (status, limit)
            )
        return self.execute_query(
            "SELECT * FROM entries ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )

    def update_entry(self, entry_id: int, **kwargs) -> bool:
        """エントリー更新

        Args:
            entry_id: エントリーID
            **kwargs: 更新フィールド

        Returns:
            成功時True
        """
        valid_fields = ['title', 'content', 'tags', 'priority', 'status']
        update_fields = {{k: v for k, v in kwargs.items() if k in valid_fields}}
        if not update_fields:
            return False

        update_fields['updated_at'] = str(datetime.now())
        set_clause = ', '.join([f"{{k}} = ?" for k in update_fields.keys()])
        values = list(update_fields.values()) + [entry_id]

        self.execute_query(f"UPDATE entries SET {{set_clause}} WHERE id = ?", tuple(values), fetch=False)
        logger.info(f"Entry updated: ID {{entry_id}}")
        return True

    def delete_entry(self, entry_id: int) -> bool:
        """エントリー削除

        Args:
            entry_id: エントリーID

        Returns:
            成功時True
        """
        result = self.execute_query("DELETE FROM entries WHERE id = ? RETURNING id", (entry_id,))
        if result:
            logger.info(f"Entry deleted: ID {{entry_id}}")
            return True
        return False

    def search_entries(self, query: str) -> List[Dict]:
        """エントリー検索

        Args:
            query: 検索クエリ

        Returns:
            検索結果
        """
        return self.execute_query(
            "SELECT * FROM entries WHERE title LIKE ? OR content LIKE ? OR tags LIKE ?",
            (f"%{{query}}%", f"%{{query}}%", f"%{{query}}%")
        )

    def get_stats(self) -> Dict[str, int]:
        """統計情報取得

        Returns:
            統計情報
        """
        active = self.execute_query("SELECT COUNT(*) as count FROM entries WHERE status = 'active'")[0]['count']
        total = self.execute_query("SELECT COUNT(*) as count FROM entries")[0]['count']
        return {{"active": active, "total": total}}

    def get_{table_name_lower}(self, limit: int = 100) -> List[Dict]:
        """{table_name}リスト取得

        Args:
            limit: 取得件数

        Returns:
            {table_name}リスト
        """
        return self.execute_query(
            f"SELECT * FROM {table_name_lower} ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )

    def add_{table_name_lower}(self, **kwargs) -> int:
        """{table_name}追加

        Returns:
            追加したID
        """
        # {table_name_lower}_テーブルにデータを追加するロジック
        # 各エージェントの要件に合わせて実装
        pass


def main():
    """メイン関数"""
    db = {db_class_name}()
    db.initialize_db()
    print(f"{{db.__class__.__name__}} initialized")
    print(f"Stats: {{db.get_stats()}}")


if __name__ == "__main__":
    main()
'''

DISCORD_TEMPLATE = '''#!/usr/bin/env python3
"""
{title} - Discord Botモジュール

Discord Bot連携モジュール
"""

import discord
from discord.ext import commands
from typing import Optional, List
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class {discord_class_name}:
    """{title} Discord Botクラス"""

    def __init__(self, agent_instance, token: Optional[str] = None):
        """初期化

        Args:
            agent_instance: エージェントインスタンス
            token: Discord Botトークン
        """
        self.agent = agent_instance
        self.token = token
        self.bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())
        self._setup_commands()

    def _setup_commands(self):
        """コマンド設定"""

        @self.bot.command(name='add_{short_name}')
        async def add_entry(ctx, title: str, *, content: str):
            """エントリー追加コマンド"""
            entry_id = self.agent.add_entry(title, content)
            await ctx.send(f"✅ エントリー追加完了 (ID: {{entry_id}})")

        @self.bot.command(name='list_{short_name}')
        async def list_entries(ctx, limit: int = 10):
            """エントリーリスト表示コマンド"""
            entries = self.agent.list_entries(limit=limit)
            if not entries:
                await ctx.send("📋 エントリーがありません")
                return

            msg = "**📋 エントリーリスト**\\n\\n"
            for entry in entries:
                msg += f"**ID {{entry['id']}}**: {{entry.get('title', 'No title')}}\\n"
                msg += f"{{entry.get('content', '')[:50]}}...\\n\\n"
            await ctx.send(msg[:2000])

        @self.bot.command(name='get_{short_name}')
        async def get_entry(ctx, entry_id: int):
            """エントリー取得コマンド"""
            entry = self.agent.get_entry(entry_id)
            if not entry:
                await ctx.send(f"❌ エントリーが見つかりません (ID: {{entry_id}})")
                return

            msg = f"**📝 エントリー ID {{entry['id']}}**\\n\\n"
            msg += f"**タイトル**: {{entry.get('title', 'No title')}}\\n"
            msg += f"**コンテンツ**: {{entry.get('content', '')}}\\n"
            if entry.get('tags'):
                msg += f"**タグ**: {{entry['tags']}}\\n"
            await ctx.send(msg)

        @self.bot.command(name='search_{short_name}')
        async def search_entries(ctx, *, query: str):
            """エントリー検索コマンド"""
            entries = self.agent.search_entries(query)
            if not entries:
                await ctx.send(f"🔍 検索結果なし: {{query}}")
                return

            msg = f"**🔍 検索結果: {{query}}**\\n\\n"
            for entry in entries[:10]:
                msg += f"**ID {{entry['id']}}**: {{entry.get('title', 'No title')}}\\n"
            await ctx.send(msg)

        @self.bot.command(name='stats_{short_name}')
        async def get_stats(ctx):
            """統計情報表示コマンド"""
            stats = self.agent.get_stats()
            msg = f"**📊 統計情報**\\n"
            msg += f"📝 総エントリー: {{stats['total']}}\\n"
            msg += f"✅ アクティブ: {{stats['active']}}\\n"
            await ctx.send(msg)

    def run(self):
        """Bot実行"""
        if not self.token:
            logger.warning("Discord Bot token not set")
            return

        logger.info("Starting Discord Bot...")
        self.bot.run(self.token)


def main():
    """メイン関数"""
    from agent import {agent_class_name}

    agent = {agent_class_name}()
    discord_bot = {discord_class_name}(agent)
    discord_bot.run()


if __name__ == "__main__":
    main()
'''

README_TEMPLATE = '''# {title} / {title} (EN)

{description} / {description_en}

## Overview / 概要

{overview_jp}

## Features / 機能

- {feature1_jp}
- {feature2_jp}
- {feature3_jp}

## Installation / インストール

```bash
pip install -r requirements.txt
```

## Usage / 使用方法

### Agent Usage / エージェントの使用

```python
from agent import {class_name}

agent = {class_name}()
entry_id = agent.add_entry("タイトル", "コンテンツ", "tags")
```

### Discord Bot Usage / Discord Botの使用

```bash
python discord.py
```

## Database Schema / データベーススキーマ

### entries / エントリーテーブル

| Column / カラム | Type / 型 | Description / 説明 |
|-----------------|-----------|---------------------|
| id | INTEGER | Primary Key / 主キー |
| title | TEXT | Entry title / タイトル |
| content | TEXT | Entry content / コンテンツ |
| tags | TEXT | Tags / タグ |
| priority | INTEGER | Priority / 優先度 |
| status | TEXT | Status / ステータス |
| created_at | TIMESTAMP | Creation time / 作成日時 |
| updated_at | TIMESTAMP | Update time / 更新日時 |

### {table_name_lower} / {table_name_lower}テーブル

{table_schema}

## API / API

### add_entry(title, content, tags=None, priority=0)
Add a new entry. / 新しいエントリーを追加します。

### get_entry(entry_id)
Get an entry by ID. / IDでエントリーを取得します。

### list_entries(limit=100, status=None)
List entries. / エントリーを一覧表示します。

### update_entry(entry_id, **kwargs)
Update an entry. / エントリーを更新します。

### delete_entry(entry_id)
Delete an entry. / エントリーを削除します。

### search_entries(query)
Search entries. / エントリーを検索します。

### get_stats()
Get statistics. / 統計情報を取得します。

## Discord Commands / Discordコマンド

- `!add_{short_name} <title> <content>` - Add entry / エントリー追加
- `!list_{short_name} [limit]` - List entries / エントリー一覧
- `!get_{short_name} <id>` - Get entry / エントリー取得
- `!search_{short_name} <query>` - Search entries / エントリー検索
- `!stats_{short_name}` - Get statistics / 統計情報

## License / ライセンス

MIT License
'''

REQUIREMENTS_TEMPLATE = '''# Requirements / 依存パッケージ

# Core dependencies / コア依存パッケージ
discord.py>=2.3.0

# Optional dependencies / オプション依存パッケージ
openai>=1.0.0
transformers>=4.30.0
torch>=2.0.0
pillow>=10.0.0
'''


def load_progress():
    """進捗管理ファイルを読み込む"""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {
        "project": PROJECT_NAME,
        "started_at": None,
        "completed_at": None,
        "agents": {agent["name"]: {"status": "pending", "files": []} for agent in AGENTS}
    }


def save_progress(progress):
    """進捗管理ファイルを保存する"""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)


def create_agent_files(agent_info, progress):
    """エージェントファイルを作成する"""
    agent_name = agent_info["name"]
    agent_dir = AGENTS_DIR / agent_name
    agent_dir.mkdir(parents=True, exist_ok=True)

    # クラス名の生成
    class_name = agent_name.replace("-", " ").title().replace(" ", "")
    db_class_name = f"{class_name}DB"
    discord_class_name = f"{class_name}Discord"
    short_name = agent_name.replace("erotic-", "").replace("-agent", "")

    # テーブル作成コードの生成
    table_creates = []
    for table in agent_info["tables"]:
        table_lower = table.lower()
        table_creates.append(f"""
        cursor.execute(\"\"\"
            CREATE TABLE IF NOT EXISTS {table_lower} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                description TEXT,
                entry_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (entry_id) REFERENCES entries(id)
            )
        \"\"")""")

    table_create_code = "\n".join(table_creates)

    # agent.py の作成
    agent_code = AGENT_TEMPLATE.format(
        title=agent_info["title"],
        description=agent_info["description"],
        name=agent_name,
        class_name=class_name,
        table_creates=table_create_code
    )
    agent_file = agent_dir / "agent.py"
    with open(agent_file, 'w') as f:
        f.write(agent_code)

    # db.py の作成
    table_name = agent_info["tables"][0] if agent_info["tables"] else "items"
    table_name_lower = table_name.lower()
    db_code = DB_TEMPLATE.format(
        title=agent_info["title"],
        description=agent_info["description"],
        name=agent_name,
        db_class_name=db_class_name,
        table_creates=table_create_code,
        table_name=table_name,
        table_name_lower=table_name_lower
    )
    db_file = agent_dir / "db.py"
    with open(db_file, 'w') as f:
        f.write(db_code)

    # discord.py の作成
    discord_code = DISCORD_TEMPLATE.format(
        title=agent_info["title"],
        description=agent_info["description"],
        name=agent_name,
        discord_class_name=discord_class_name,
        agent_class_name=class_name,
        short_name=short_name
    )
    discord_file = agent_dir / "discord.py"
    with open(discord_file, 'w') as f:
        f.write(discord_code)

    # README.md の作成
    overview_jp = f"AIを活用した{agent_info['description']}。"
    overview_en = f"{agent_info['description']} using AI."
    table_schema = "| Column | Type | Description |\\n|--------|------|-------------|\\n| id | INTEGER | Primary Key |\\n| name | TEXT | Name |\\n| description | TEXT | Description |"

    readme_code = README_TEMPLATE.format(
        title=agent_info["title"],
        description=agent_info["description"],
        description_en=agent_info["description"],
        overview_jp=overview_jp,
        class_name=class_name,
        feature1_jp="AIによるコンテンツ生成",
        feature2_jp="高度なスタイル変換",
        feature3_jp="クリエイティブなアシスタント機能",
        table_name=table_name,
        table_name_lower=table_name_lower,
        table_schema=table_schema,
        short_name=short_name
    )
    readme_file = agent_dir / "README.md"
    with open(readme_file, 'w') as f:
        f.write(readme_code)

    # requirements.txt の作成
    requirements_file = agent_dir / "requirements.txt"
    with open(requirements_file, 'w') as f:
        f.write(REQUIREMENTS_TEMPLATE)

    # 進捗を更新
    progress["agents"][agent_name] = {
        "status": "completed",
        "files": ["agent.py", "db.py", "discord.py", "README.md", "requirements.txt"]
    }
    save_progress(progress)

    return agent_name


def main():
    """メイン関数"""
    print(f"🚀 {PROJECT_NAME} オーケストレーター開始")

    # 進捗管理ファイルの読み込み
    progress = load_progress()

    if progress["started_at"] is None:
        progress["started_at"] = datetime.now().isoformat()
        save_progress(progress)

    # 完了していないエージェントを作成
    pending_agents = [a for a in AGENTS if progress["agents"][a["name"]]["status"] == "pending"]

    if not pending_agents:
        print("✅ すべてのエージェントが完了しています")
        if progress["completed_at"] is None:
            progress["completed_at"] = datetime.now().isoformat()
            save_progress(progress)
        return

    print(f"📋 残り {{len(pending_agents)}} 個のエージェントを作成します")

    for agent_info in pending_agents:
        print(f"⏳ {{agent_info['title']}} を作成中...")
        agent_name = create_agent_files(agent_info, progress)
        print(f"✅ {{agent_name}} 完了")

    # すべて完了
    progress["completed_at"] = datetime.now().isoformat()
    save_progress(progress)

    print(f"🎉 {PROJECT_NAME} 完了！")
    print(f"📊 作成したエージェント: {{len(AGENTS)}} 個")

    # Git commit
    commit_msg = f"feat: {PROJECT_NAME}完了 ({{len(AGENTS)}}/{{len(AGENTS)}})"
    try:
        subprocess.run(["git", "add", "-A"], check=True)
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        subprocess.run(["git", "push"], check=True)
        print(f"✅ Git commit & push 完了")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Git commit エラー: {{e}}")


if __name__ == "__main__":
    main()
