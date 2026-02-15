#!/usr/bin/env python3
"""
オーケストレーター V65 - 次期プロジェクト案
野球メディア・インタビュー / ゲームeスポーツ大会 / えっちクリエイターサポート / IoT・エッジコンピューティング / セキュリティプライバシー・GDPR
"""

import os
import json
from pathlib import Path

# プロジェクト設定
V65_AGENTS = {
    "野球メディア・インタビューエージェント": [
        {"name": "baseball-media-interview-agent", "desc": "野球メディアインタビューエージェント。メディアインタビューの管理・記録。"},
        {"name": "baseball-podcast-agent", "desc": "野球ポッドキャストエージェント。ポッドキャストコンテンツの制作・管理。"},
        {"name": "baseball-video-content-agent", "desc": "野球ビデオコンテンツエージェント。動画コンテンツの制作・管理。"},
        {"name": "baseball-documentary-agent", "desc": "野球ドキュメンタリーエージェント。ドキュメンタリー制作の管理。"},
        {"name": "baseball-social-media-agent", "desc": "野球ソーシャルメディアエージェント。SNS運営・コンテンツ管理。"},
    ],
    "ゲームeスポーツ大会エージェント": [
        {"name": "game-esports-tournament-agent", "desc": "ゲームeスポーツ大会エージェント。大会運営・管理。"},
        {"name": "game-bracket-agent", "desc": "ゲームブラケットエージェント。トーナメントブラケットの管理。"},
        {"name": "game-ladder-agent", "desc": "ゲームラダーエージェント。ランキング・ラダーの管理。"},
        {"name": "game-match-recorder-agent", "desc": "ゲームマッチレコーダーエージェント。試合記録の管理。"},
        {"name": "game-team-manager-agent", "desc": "ゲームチームマネージャーエージェント。チーム管理・運営。"},
    ],
    "えっちクリエイターサポートエージェント": [
        {"name": "erotic-creator-support-agent", "desc": "えっちクリエイターサポートエージェント。クリエイターへのサポート・相談。"},
        {"name": "erotic-creator-analytics-agent", "desc": "えっちクリエイターアナリティクスエージェント。クリエイターの分析・レポーティング。"},
        {"name": "erotic-creator-growth-agent", "desc": "えっちクリエイターグロースエージェント。クリエイターの成長支援。"},
        {"name": "erotic-creator-monetization-agent", "desc": "えっちクリエイターマネタイゼーションエージェント。収益化支援。"},
        {"name": "erotic-creator-community-agent", "desc": "えっちクリエイターコミュニティエージェント。クリエイターコミュニティの管理。"},
    ],
    "IoT・エッジコンピューティングエージェント": [
        {"name": "iot-device-manager-agent", "desc": "IoTデバイスマネージャーエージェント。IoTデバイスの管理・監視。"},
        {"name": "iot-data-collector-agent", "desc": "IoTデータコレクターエージェント。IoTデータの収集・集約。"},
        {"name": "edge-ai-agent", "desc": "エッジAIエージェント。エッジデバイスでのAI推論管理。"},
        {"name": "iot-security-agent", "desc": "IoTセキュリティエージェント。IoTデバイスのセキュリティ管理。"},
        {"name": "mqtt-agent", "desc": "MQTTエージェント。MQTTプロトコルの管理・通信。"},
    ],
    "セキュリティプライバシー・GDPRエージェント": [
        {"name": "gdpr-compliance-agent", "desc": "GDPRコンプライアンスエージェント。GDPR準拠の管理・監査。"},
        {"name": "privacy-policy-agent", "desc": "プライバシーポリシーエージェント。プライバシーポリシーの管理・更新。"},
        {"name": "data-privacy-agent", "desc": "データプライバシーエージェント。データプライバシーの保護・管理。"},
        {"name": "consent-manager-agent", "desc": "同意管理エージェント。ユーザー同意の管理・記録。"},
        {"name": "data-rights-agent", "desc": "データ権利エージェント。データ権利要求の対応・管理。"},
    ],
}

PROGRESS_FILE = "/workspace/v65_progress.json"
BASE_DIR = "/workspace"

# テンプレート
AGENT_TEMPLATE = """#!/usr/bin/env python3
\"\"\"
{name} - {desc}
\"\"\"

import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class {class_name}:
    \"\"\"{name}\"\"\"

    def __init__(self, db_path: str = "{name}.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        \"\"\"データベース初期化\"\"\"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def add_entry(self, title: Optional[str], content: str, metadata: Optional[Dict] = None) -> int:
        \"\"\"エントリー追加\"\"\"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        metadata_json = json.dumps(metadata) if metadata else None

        cursor.execute('''
            INSERT INTO entries (title, content, metadata)
            VALUES (?, ?, ?)
        ''', (title, content, metadata_json))

        entry_id = cursor.lastrowid
        conn.commit()
        conn.close()

        logger.info(f"Entry added: ID={{entry_id}}")
        return entry_id

    def get_entry(self, entry_id: int) -> Optional[Dict]:
        \"\"\"エントリー取得\"\"\"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, title, content, metadata, created_at, updated_at
            FROM entries WHERE id = ?
        ''', (entry_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {{
                "id": row[0],
                "title": row[1],
                "content": row[2],
                "metadata": json.loads(row[3]) if row[3] else None,
                "created_at": row[4],
                "updated_at": row[5]
            }}
        return None

    def list_entries(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        \"\"\"エントリー一覧\"\"\"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, title, content, metadata, created_at, updated_at
            FROM entries ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        ''', (limit, offset))

        rows = cursor.fetchall()
        conn.close()

        return [{{
            "id": row[0],
            "title": row[1],
            "content": row[2],
            "metadata": json.loads(row[3]) if row[3] else None,
            "created_at": row[4],
            "updated_at": row[5]
        }} for row in rows]

    def update_entry(self, entry_id: int, title: Optional[str] = None,
                    content: Optional[str] = None, metadata: Optional[Dict] = None) -> bool:
        \"\"\"エントリー更新\"\"\"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        updates = []
        params = []

        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if content is not None:
            updates.append("content = ?")
            params.append(content)
        if metadata is not None:
            updates.append("metadata = ?")
            params.append(json.dumps(metadata))

        if not updates:
            conn.close()
            return False

        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(entry_id)

        cursor.execute(f'''
            UPDATE entries SET {{', '.join(updates)}}
            WHERE id = ?
        ''', params)

        conn.commit()
        conn.close()

        return cursor.rowcount > 0

    def delete_entry(self, entry_id: int) -> bool:
        \"\"\"エントリー削除\"\"\"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('DELETE FROM entries WHERE id = ?', (entry_id,))

        conn.commit()
        conn.close()

        return cursor.rowcount > 0

    def search_entries(self, query: str, limit: int = 100) -> List[Dict]:
        \"\"\"エントリー検索\"\"\"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, title, content, metadata, created_at, updated_at
            FROM entries
            WHERE title LIKE ? OR content LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (f'%{{query}}%', f'%{{query}}%', limit))

        rows = cursor.fetchall()
        conn.close()

        return [{{
            "id": row[0],
            "title": row[1],
            "content": row[2],
            "metadata": json.loads(row[3]) if row[3] else None,
            "created_at": row[4],
            "updated_at": row[5]
        }} for row in rows]


def main():
    \"\"\"メイン関数\"\"\"
    agent = {class_name}()

    # サンプル実行
    entry_id = agent.add_entry(
        title="サンプル",
        content="{desc}",
        metadata={{"version": "1.0"}}
    )

    print(f"Created entry: {{entry_id}}")

    entry = agent.get_entry(entry_id)
    print(f"Entry: {{entry}}")


if __name__ == "__main__":
    main()
"""

DB_TEMPLATE = """#!/usr/bin/env python3
\"\"\"
{name} - データベース管理モジュール
\"\"\"

import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    \"\"\"データベース管理クラス\"\"\"

    def __init__(self, db_path: str = "{name}.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        \"\"\"データベース初期化\"\"\"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # エントリーテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT NOT NULL,
                metadata TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # タグテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # エントリータグ関連テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entry_tags (
                entry_id INTEGER,
                tag_id INTEGER,
                PRIMARY KEY (entry_id, tag_id),
                FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )
        ''')

        conn.commit()
        conn.close()

    def add_entry(self, title: Optional[str], content: str,
                  metadata: Optional[Dict] = None, tags: Optional[List[str]] = None) -> int:
        \"\"\"エントリー追加\"\"\"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        metadata_json = json.dumps(metadata) if metadata else None

        cursor.execute('''
            INSERT INTO entries (title, content, metadata)
            VALUES (?, ?, ?)
        ''', (title, content, metadata_json))

        entry_id = cursor.lastrowid

        # タグを追加
        if tags:
            for tag_name in tags:
                tag_id = self._get_or_create_tag(cursor, tag_name)
                cursor.execute('''
                    INSERT INTO entry_tags (entry_id, tag_id)
                    VALUES (?, ?)
                ''', (entry_id, tag_id))

        conn.commit()
        conn.close()

        logger.info(f"Entry added: ID={{entry_id}}")
        return entry_id

    def _get_or_create_tag(self, cursor, tag_name: str) -> int:
        \"\"\"タグ取得または作成\"\"\"
        cursor.execute('SELECT id FROM tags WHERE name = ?', (tag_name,))
        row = cursor.fetchone()

        if row:
            return row[0]

        cursor.execute('INSERT INTO tags (name) VALUES (?)', (tag_name,))
        return cursor.lastrowid

    def get_entry(self, entry_id: int) -> Optional[Dict]:
        \"\"\"エントリー取得\"\"\"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, title, content, metadata, status, created_at, updated_at
            FROM entries WHERE id = ?
        ''', (entry_id,))

        row = cursor.fetchone()

        if not row:
            conn.close()
            return None

        # タグを取得
        cursor.execute('''
            SELECT t.name FROM tags t
            JOIN entry_tags et ON t.id = et.tag_id
            WHERE et.entry_id = ?
        ''', (entry_id,))
        tags = [tag_row[0] for tag_row in cursor.fetchall()]

        conn.close()

        return {{
            "id": row[0],
            "title": row[1],
            "content": row[2],
            "metadata": json.loads(row[3]) if row[3] else None,
            "status": row[4],
            "tags": tags,
            "created_at": row[5],
            "updated_at": row[6]
        }}

    def list_entries(self, status: Optional[str] = None,
                     limit: int = 100, offset: int = 0) -> List[Dict]:
        \"\"\"エントリー一覧\"\"\"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if status:
            cursor.execute('''
                SELECT id, title, content, metadata, status, created_at, updated_at
                FROM entries WHERE status = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            ''', (status, limit, offset))
        else:
            cursor.execute('''
                SELECT id, title, content, metadata, status, created_at, updated_at
                FROM entries
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            ''', (limit, offset))

        rows = cursor.fetchall()
        conn.close()

        return [{{
            "id": row[0],
            "title": row[1],
            "content": row[2],
            "metadata": json.loads(row[3]) if row[3] else None,
            "status": row[4],
            "created_at": row[5],
            "updated_at": row[6]
        }} for row in rows]

    def update_entry(self, entry_id: int, **kwargs) -> bool:
        \"\"\"エントリー更新\"\"\"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        updates = []
        params = []

        if 'title' in kwargs:
            updates.append("title = ?")
            params.append(kwargs['title'])
        if 'content' in kwargs:
            updates.append("content = ?")
            params.append(kwargs['content'])
        if 'metadata' in kwargs:
            updates.append("metadata = ?")
            params.append(json.dumps(kwargs['metadata']))
        if 'status' in kwargs:
            updates.append("status = ?")
            params.append(kwargs['status'])

        if not updates:
            conn.close()
            return False

        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(entry_id)

        cursor.execute(f'''
            UPDATE entries SET {{', '.join(updates)}}
            WHERE id = ?
        ''', params)

        conn.commit()
        conn.close()

        return cursor.rowcount > 0

    def delete_entry(self, entry_id: int) -> bool:
        \"\"\"エントリー削除\"\"\"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('DELETE FROM entries WHERE id = ?', (entry_id,))

        conn.commit()
        conn.close()

        return cursor.rowcount > 0

    def search_entries(self, query: str, limit: int = 100) -> List[Dict]:
        \"\"\"エントリー検索\"\"\"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, title, content, metadata, status, created_at, updated_at
            FROM entries
            WHERE title LIKE ? OR content LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (f'%{{query}}%', f'%{{query}}%', limit))

        rows = cursor.fetchall()
        conn.close()

        return [{{
            "id": row[0],
            "title": row[1],
            "content": row[2],
            "metadata": json.loads(row[3]) if row[3] else None,
            "status": row[4],
            "created_at": row[5],
            "updated_at": row[6]
        }} for row in rows]

    def get_stats(self) -> Dict:
        \"\"\"統計情報取得\"\"\"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM entries')
        total_entries = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM tags')
        total_tags = cursor.fetchone()[0]

        cursor.execute("SELECT status, COUNT(*) FROM entries GROUP BY status")
        status_counts = {{row[0]: row[1] for row in cursor.fetchall()}}

        conn.close()

        return {{
            "total_entries": total_entries,
            "total_tags": total_tags,
            "status_counts": status_counts
        }}


def main():
    \"\"\"メイン関数\"\"\"
    db = DatabaseManager()

    stats = db.get_stats()
    print(f"Stats: {{json.dumps(stats, indent=2, ensure_ascii=False)}}")


if __name__ == "__main__":
    main()
"""

DISCORD_TEMPLATE = """#!/usr/bin/env python3
\"\"\"
{name} - Discord Botモジュール
\"\"\"

import discord
from discord.ext import commands
import logging
from typing import Optional
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class {class_name}Bot(commands.Bot):
    \"\"\"{name} Discord Bot\"\"\"

    def __init__(self, command_prefix: str = "!", token: Optional[str] = None):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=command_prefix, intents=intents)

        self.token = token

    async def setup_hook(self):
        \"\"\"Botセットアップ\"\"\"
        logger.info(f"Bot ready: {{self.user}}")

    async def on_ready(self):
        \"\"\"Bot起動時\"\"\"
        logger.info(f"Bot is ready! Logged in as {{self.user}}")
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="{desc}"
        )
        await self.change_presence(activity=activity)

    async def on_message(self, message: discord.Message):
        \"\"\"メッセージ受信時\"\"\"
        if message.author == self.user:
            return

        await self.process_commands(message)

    async def send_help(self, channel: discord.TextChannel):
        \"\"\"ヘルプ送信\"\"\"
        embed = discord.Embed(
            title="{name}",
            description="{desc}",
            color=0x00ff00
        )

        embed.add_field(
            name="コマンド",
            value="`!status` - ステータス確認\\n`!add <content>` - エントリー追加\\n`!list` - エントリー一覧\\n`!search <query>` - エントリー検索\\n`!help` - ヘルプ表示",
            inline=False
        )

        await channel.send(embed=embed)

    async def send_status(self, channel: discord.TextChannel, status_data: dict):
        \"\"\"ステータス送信\"\"\"
        embed = discord.Embed(
            title="ステータス",
            description=f"現在のステータス",
            color=0x00ff00
        )

        for key, value in status_data.items():
            embed.add_field(name=key, value=str(value), inline=False)

        await channel.send(embed=embed)

    async def send_entry(self, channel: discord.TextChannel, entry: dict):
        \"\"\"エントリー送信\"\"\"
        embed = discord.Embed(
            title=entry.get('title', 'エントリー'),
            description=entry.get('content', '')[:2000],
            color=0x00ff00
        )

        if entry.get('metadata'):
            embed.add_field(
                name="メタデータ",
                value=f"```json\\n{{entry['metadata']}}\\n```",
                inline=False
            )

        embed.set_footer(text=f"ID: {{entry.get('id')}} | 作成: {{entry.get('created_at')}}")

        await channel.send(embed=embed)

    async def send_error(self, channel: discord.TextChannel, error: str):
        \"\"\"エラー送信\"\"\"
        embed = discord.Embed(
            title="エラー",
            description=error,
            color=0xff0000
        )
        await channel.send(embed=embed)


class {class_name}Commands(commands.Cog):
    \"\"\"{name} コマンド\"\"\"

    def __init__(self, bot: {class_name}Bot):
        self.bot = bot
        self.db = None  # DatabaseManagerをセット

    def set_db(self, db):
        \"\"\"データベース設定\"\"\"
        self.db = db

    @commands.command(name='status')
    async def cmd_status(self, ctx: commands.Context):
        \"\"\"ステータス確認\"\"\"
        if not self.db:
            await self.bot.send_error(ctx.channel, "データベースが未設定です")
            return

        stats = self.db.get_stats()
        await self.bot.send_status(ctx.channel, stats)

    @commands.command(name='add')
    async def cmd_add(self, ctx: commands.Context, *, content: str):
        \"\"\"エントリー追加\"\"\"
        if not self.db:
            await self.bot.send_error(ctx.channel, "データベースが未設定です")
            return

        try:
            entry_id = self.db.add_entry(
                title=None,
                content=content,
                metadata={{"author": str(ctx.author)}}
            )

            await ctx.send(f"エントリーを追加しました (ID: {{entry_id}})")
        except Exception as e:
            await self.bot.send_error(ctx.channel, f"追加失敗: {{e}}")

    @commands.command(name='list')
    async def cmd_list(self, ctx: commands.Context, limit: int = 10):
        \"\"\"エントリー一覧\"\"\"
        if not self.db:
            await self.bot.send_error(ctx.channel, "データベースが未設定です")
            return

        entries = self.db.list_entries(limit=limit)

        if not entries:
            await ctx.send("エントリーがありません")
            return

        for entry in entries:
            await self.bot.send_entry(ctx.channel, entry)

    @commands.command(name='search')
    async def cmd_search(self, ctx: commands.Context, *, query: str):
        \"\"\"エントリー検索\"\"\"
        if not self.db:
            await self.bot.send_error(ctx.channel, "データベースが未設定です")
            return

        entries = self.db.search_entries(query, limit=10)

        if not entries:
            await ctx.send(f"検索結果: '{{query}}' - 見つかりませんでした")
            return

        for entry in entries:
            await self.bot.send_entry(ctx.channel, entry)

    @commands.command(name='help')
    async def cmd_help(self, ctx: commands.Context):
        \"\"\"ヘルプ表示\"\"\"
        await self.bot.send_help(ctx.channel)


def create_bot(token: Optional[str] = None, command_prefix: str = "!") -> {class_name}Bot:
    \"\"\"Botインスタンス作成\"\"\"
    bot = {class_name}Bot(command_prefix=command_prefix, token=token)

    # コグを追加
    bot.add_cog({class_name}Commands(bot))

    return bot


def main():
    \"\"\"メイン関数\"\"\"
    import os

    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("DISCORD_TOKEN environment variable not set")
        return

    bot = create_bot(token=token)
    bot.run(token)


if __name__ == "__main__":
    main()
"""

README_TEMPLATE = """# {name}

{desc}

## 機能

- エントリーの追加・取得・更新・削除
- タグ付け・検索機能
- Discord Bot連携
- SQLiteデータベースによる永続化

## インストール

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本使用

```python
from agent import {class_name}

agent = {class_name}()

# エントリー追加
entry_id = agent.add_entry(
    title="タイトル",
    content="コンテンツ",
    metadata={{"key": "value"}}
)

# エントリー取得
entry = agent.get_entry(entry_id)
print(entry)
```

### Discord Bot

```bash
export DISCORD_TOKEN="your_bot_token"
python discord.py
```

コマンド:
- `!status` - ステータス確認
- `!add <content>` - エントリー追加
- `!list` - エントリー一覧
- `!search <query>` - エントリー検索
- `!help` - ヘルプ表示

## データベーススキーマ

### entriesテーブル
- `id` - エントリーID (主キー)
- `title` - タイトル
- `content` - コンテンツ
- `metadata` - メタデータ (JSON)
- `status` - ステータス
- `created_at` - 作成日時
- `updated_at` - 更新日時

### tagsテーブル
- `id` - タグID (主キー)
- `name` - タグ名 (ユニーク)
- `created_at` - 作成日時

### entry_tagsテーブル
- `entry_id` - エントリーID (外部キー)
- `tag_id` - タグID (外部キー)

## ライセンス

MIT License
"""

REQUIREMENTS_TEMPLATE = """discord.py>=2.3.0
"""

# 進捗管理
def load_progress() -> dict:
    """進捗読み込み"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"completed": [], "total": 0}

def save_progress(progress: dict):
    """進捗保存"""
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)

def to_class_name(name: str) -> str:
    """クラス名変換"""
    parts = name.replace('-', '_').split('_')
    return ''.join(p.capitalize() for p in parts)

def create_agent_files(category: str, agent_info: dict) -> bool:
    """エージェントファイル作成"""
    name = agent_info['name']
    desc = agent_info['desc']
    class_name = to_class_name(name)

    # ディレクトリ作成
    agent_dir = Path(BASE_DIR) / name
    agent_dir.mkdir(parents=True, exist_ok=True)

    # ファイル作成
    files = {
        "agent.py": AGENT_TEMPLATE.format(
            name=name, desc=desc, class_name=class_name
        ),
        "db.py": DB_TEMPLATE.format(name=name, desc=desc, class_name=class_name),
        "discord.py": DISCORD_TEMPLATE.format(
            name=name, desc=desc, class_name=class_name
        ),
        "README.md": README_TEMPLATE.format(
            name=name, desc=desc, class_name=class_name
        ),
        "requirements.txt": REQUIREMENTS_TEMPLATE,
    }

    for filename, content in files.items():
        filepath = agent_dir / filename
        filepath.write_text(content, encoding='utf-8')

    logger.info(f"Created: {{name}}/")
    return True

def main():
    """メイン処理"""
    global logger
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    progress = load_progress()

    # 全エージェント数を計算
    total_agents = sum(len(agents) for agents in V65_AGENTS.values())
    progress["total"] = total_agents

    logger.info(f"Starting V65 Orchestration: {{total_agents}} agents")

    created_count = 0

    for category, agents in V65_AGENTS.items():
        logger.info(f"Category: {{category}} ({{len(agents)}} agents)")

        for agent_info in agents:
            name = agent_info['name']

            if name in progress["completed"]:
                logger.info(f"  - {{name}}: already completed, skipping")
                continue

            if create_agent_files(category, agent_info):
                progress["completed"].append(name)
                created_count += 1

        # カテゴリごとに進捗保存
        save_progress(progress)

    logger.info(f"V65 Orchestration completed: {{created_count}} agents created")

    # 最終進捗表示
    logger.info(f"Progress: {{len(progress['completed'])}}/{{progress['total']}} completed")

    if len(progress["completed"]) == progress["total"]:
        logger.info("🎉 All V65 agents completed!")
        return 0
    else:
        logger.info("Some agents remaining, run again to continue")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
