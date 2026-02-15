#!/usr/bin/env python3
"""
Erotic Content Advanced Search & Curation Orchestrator
えっちコンテンツ高度検索・キュレーションエージェントのオーケストレーター
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
PROGRESS_FILE = WORKSPACE / "erotic_advanced_search_progress.json"

# エージェント定義
AGENTS = [
    {
        "name": "erotic-semantic-search-agent",
        "description_ja": "えっちコンテンツ意味検索エージェント",
        "description_en": "Erotic Content Semantic Search Agent",
        "type": "search",
        "emoji": "🔍"
    },
    {
        "name": "erotic-curation-agent",
        "description_ja": "えっちコンテンツキュレーションエージェント",
        "description_en": "Erotic Content Curation Agent",
        "type": "curation",
        "emoji": "🎨"
    },
    {
        "name": "erotic-tag-analysis-agent",
        "description_ja": "えっちタグ高度分析エージェント",
        "description_en": "Erotic Tag Advanced Analysis Agent",
        "type": "analysis",
        "emoji": "🏷️"
    },
    {
        "name": "erotic-collection-optimizer-agent",
        "description_ja": "えっちコレクション最適化エージェント",
        "description_en": "Erotic Collection Optimization Agent",
        "type": "optimization",
        "emoji": "📚"
    },
    {
        "name": "erotic-content-discovery-agent",
        "description_ja": "えっちコンテンツディスカバリーエージェント",
        "description_en": "Erotic Content Discovery Agent",
        "type": "discovery",
        "emoji": "✨"
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
    agent_class = agent['name'].replace('-', '_').title().replace('_', '')

    # Pythonコード部分（f-stringの外）
    semantic_search_code = '''    def semantic_search(self, query, limit=20):
        """意味検索"""
        cursor = self.conn.cursor()

        # タグベースの簡易検索
        query_tags = [t.strip() for t in query.split() if t.strip()]

        conditions = []
        params = []

        for tag in query_tags:
            conditions.append("tags LIKE ?")
            params.append(f"%{tag}%")

        if conditions:
            query_str = " AND ".join(conditions)
            cursor.execute(f"""
                SELECT * FROM contents WHERE {query_str}
                ORDER BY updated_at DESC
                LIMIT ?
            """, params + [limit])
        else:
            cursor.execute("""
                SELECT * FROM contents
                ORDER BY updated_at DESC
                LIMIT ?
            """, (limit,))

        return cursor.fetchall()

    def get_related_contents(self, content_id, limit=10):
        """関連コンテンツを取得"""
        cursor = self.conn.cursor()

        # 同じタグを持つコンテンツを検索
        cursor.execute("""
            SELECT DISTINCT c.*
            FROM contents c
            INNER JOIN content_tags ct ON c.content_id = ct.content_id
            WHERE ct.tag_name IN (
                SELECT tag_name FROM content_tags WHERE content_id = ?
            ) AND c.content_id != ?
            ORDER BY COUNT(ct.tag_name) DESC, c.updated_at DESC
            LIMIT ?
        """, (content_id, content_id, limit))

        return cursor.fetchall()'''

    top_tags_code = '''    def get_top_tags(self, limit=50):
        """トップタグを取得"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM tags
            ORDER BY count DESC
            LIMIT ?
        """, (limit,))
        return cursor.fetchall()'''

    create_collection_code = '''    def create_collection(self, collection_name, description, tags, auto_update=True):
        """コレクションを作成"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO collections (collection_name, description, tags, auto_update)
            VALUES (?, ?, ?, ?)
        """, (collection_name, description, tags, 1 if auto_update else 0))
        self.conn.commit()
        return cursor.lastrowid'''

    add_to_collection_code = '''    def add_to_collection(self, collection_id, content_id):
        """コレクションにコンテンツを追加"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO collection_items (collection_id, content_id)
            VALUES (?, ?)
        """, (collection_id, content_id))
        self.conn.commit()
        return cursor.lastrowid'''

    get_collection_contents_code = '''    def get_collection_contents(self, collection_id):
        """コレクションのコンテンツを取得"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT c.* FROM contents c
            INNER JOIN collection_items ci ON c.content_id = ci.content_id
            WHERE ci.collection_id = ?
            ORDER BY ci.added_at DESC
        """, (collection_id,))
        return cursor.fetchall()'''

    log_search_code = '''    def log_search(self, query, results_count, clicked_contents=None):
        """検索をログ"""
        cursor = self.conn.cursor()
        clicked_json = json_module.dumps(clicked_contents) if clicked_contents else None
        cursor.execute("""
            INSERT INTO search_logs (query, results_count, clicked_contents)
            VALUES (?, ?, ?)
        """, (query, results_count, clicked_json))
        self.conn.commit()
        return cursor.lastrowid'''

    get_search_suggestions_code = '''    def get_search_suggestions(self, query_prefix, limit=10):
        """検索候補を取得"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT query, COUNT(*) as freq
            FROM search_logs
            WHERE query LIKE ?
            GROUP BY query
            ORDER BY freq DESC
            LIMIT ?
        """, (f"{query_prefix}%", limit))
        return cursor.fetchall()'''

    template = f'''#!/usr/bin/env python3
"""
{agent['description_ja']} / {agent['description_en']}
{agent['name']}
"""

import sqlite3
from datetime import datetime
from pathlib import Path
import json as json_module

class {agent_class}Agent:
    """{agent['description_ja']}"""

    def __init__(self, db_path=None):
        self.db_path = db_path or Path("data/erotic_advanced.db")
        self.conn = None
        self.init_db()

    def init_db(self):
        """データベース初期化"""
        self.conn = sqlite3.connect(self.db_path)
        self.create_tables()

    def create_tables(self):
        """テーブル作成"""
        cursor = self.conn.cursor()

        # コンテンツテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_id TEXT UNIQUE NOT NULL,
                title TEXT,
                artist TEXT,
                source TEXT,
                url TEXT,
                tags TEXT,
                embedding BLOB,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # タグテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_name TEXT UNIQUE NOT NULL,
                category TEXT,
                count INTEGER DEFAULT 0,
                related_tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # コンテンツタグ関連付けテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_id TEXT NOT NULL,
                tag_name TEXT NOT NULL,
                relevance REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(content_id, tag_name)
            )
        """)

        # 検索ログテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                results_count INTEGER,
                clicked_contents TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # キュレーションテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collection_name TEXT NOT NULL,
                description TEXT,
                tags TEXT,
                auto_update BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # コレクションアイテムテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collection_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collection_id INTEGER NOT NULL,
                content_id TEXT NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(collection_id, content_id)
            )
        """)

        self.conn.commit()

    def add_content(self, content_id, title, artist, source, url, tags, description=""):
        """コンテンツを追加"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO contents (content_id, title, artist, source, url, tags, description, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (content_id, title, artist, source, url, tags, description, datetime.now().isoformat()))
        self.conn.commit()

        # タグの更新
        self.update_tags(content_id, tags)

        return cursor.lastrowid

    def update_tags(self, content_id, tags_str):
        """タグを更新"""
        cursor = self.conn.cursor()

        # 既存のタグ関連付けを削除
        cursor.execute("DELETE FROM content_tags WHERE content_id = ?", (content_id,))

        # タグをパース
        tags = [t.strip() for t in tags_str.split(",") if t.strip()]

        for tag in tags:
            # タグを追加（存在しない場合）
            cursor.execute("""
                INSERT OR IGNORE INTO tags (tag_name, count)
                VALUES (?, 0)
            """, (tag,))
            cursor.execute("""
                UPDATE tags SET count = count + 1 WHERE tag_name = ?
            """, (tag,))

            # コンテンツタグ関連付けを追加
            cursor.execute("""
                INSERT OR REPLACE INTO content_tags (content_id, tag_name)
                VALUES (?, ?)
            """, (content_id, tag))

        self.conn.commit()

{semantic_search_code}

{top_tags_code}

{create_collection_code}

{add_to_collection_code}

{get_collection_contents_code}

{log_search_code}

{get_search_suggestions_code}

    def get_close(self):
        """接続を閉じる"""
        if self.conn:
            self.conn.close()


if __name__ == "__main__":
    agent = {agent_class}Agent()

    # サンプルデータ追加
    agent.add_content("er001", "美少女の冒険", "ArtistA", "pixiv", "https://example.com/1", "アニメ,美少女,冒険", "かわいい")
    agent.add_content("er002", "暗黒の儀式", "ArtistB", "twitter", "https://example.com/2", "ダーク,魔法,エルフ", "暗い系")
    agent.add_content("er003", "日常の幸せ", "ArtistA", "pixiv", "https://example.com/3", "日常,癒やし,スライス", "ほのぼの")

    # 検索
    results = agent.semantic_search("アニメ")
    print(f"検索結果: {{len(results)}}件")

    # タグ取得
    top_tags = agent.get_top_tags(5)
    print("\\nトップタグ:")
    for tag in top_tags:
        print(f"  {{tag[1]}}: {{tag[3]}}回")

    agent.get_close()
'''
    return template

def generate_db_py(agent):
    """db.pyを生成"""
    template = f'''#!/usr/bin/env python3
"""
{agent['description_ja']} データベース管理 / {agent['description_en']} Database Management
{agent['name']}
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

class EroticAdvancedDB:
    """えっちコンテンツ高度検索・キュレーションデータベース管理クラス"""

    def __init__(self, db_path: str = "data/erotic_advanced.db"):
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

    def create_content(
        self,
        content_id: str,
        title: str,
        artist: str,
        source: str,
        url: str,
        tags: str,
        description: str = ""
    ) -> int:
        """コンテンツ作成"""
        query = """
            INSERT OR REPLACE INTO contents
            (content_id, title, artist, source, url, tags, description, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_update(
            query,
            (content_id, title, artist, source, url, tags, description, datetime.now().isoformat())
        )

    def get_content(self, content_id: str) -> Optional[Dict]:
        """コンテンツ取得"""
        rows = self.execute_query(
            "SELECT * FROM contents WHERE content_id = ?",
            (content_id,)
        )
        return dict(rows[0]) if rows else None

    def list_contents(
        self,
        tag: Optional[str] = None,
        artist: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """コンテンツ一覧"""
        query = "SELECT * FROM contents WHERE 1=1"
        params = []

        if tag:
            query += " AND tags LIKE ?"
            params.append(f"%{{tag}}%")

        if artist:
            query += " AND artist = ?"
            params.append(artist)

        query += " ORDER BY updated_at DESC LIMIT ?"
        params.append(limit)

        rows = self.execute_query(query, tuple(params))
        return [dict(row) for row in rows]

    def create_tag(
        self,
        tag_name: str,
        category: str = "",
        related_tags: str = ""
    ) -> int:
        """タグ作成"""
        query = """
            INSERT OR IGNORE INTO tags (tag_name, category, related_tags)
            VALUES (?, ?, ?)
        """
        return self.execute_update(query, (tag_name, category, related_tags))

    def get_tag(self, tag_name: str) -> Optional[Dict]:
        """タグ取得"""
        rows = self.execute_query(
            "SELECT * FROM tags WHERE tag_name = ?",
            (tag_name,)
        )
        return dict(rows[0]) if rows else None

    def list_tags(
        self,
        category: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """タグ一覧"""
        query = "SELECT * FROM tags WHERE 1=1"
        params = []

        if category:
            query += " AND category = ?"
            params.append(category)

        query += " ORDER BY count DESC LIMIT ?"
        params.append(limit)

        rows = self.execute_query(query, tuple(params))
        return [dict(row) for row in rows]

    def create_collection(
        self,
        collection_name: str,
        description: str,
        tags: str,
        auto_update: bool = True
    ) -> int:
        """コレクション作成"""
        query = """
            INSERT INTO collections (collection_name, description, tags, auto_update)
            VALUES (?, ?, ?, ?)
        """
        return self.execute_update(query, (collection_name, description, tags, 1 if auto_update else 0))

    def get_collection(self, collection_id: int) -> Optional[Dict]:
        """コレクション取得"""
        rows = self.execute_query(
            "SELECT * FROM collections WHERE id = ?",
            (collection_id,)
        )
        return dict(rows[0]) if rows else None

    def list_collections(self, limit: int = 50) -> List[Dict]:
        """コレクション一覧"""
        rows = self.execute_query(
            "SELECT * FROM collections ORDER BY updated_at DESC LIMIT ?",
            (limit,)
        )
        return [dict(row) for row in rows]

    def add_to_collection(self, collection_id: int, content_id: str) -> int:
        """コレクションにコンテンツ追加"""
        query = """
            INSERT OR IGNORE INTO collection_items (collection_id, content_id)
            VALUES (?, ?)
        """
        return self.execute_update(query, (collection_id, content_id))

    def remove_from_collection(self, collection_id: int, content_id: str) -> bool:
        """コレクションからコンテンツ削除"""
        query = "DELETE FROM collection_items WHERE collection_id = ? AND content_id = ?"
        self.execute_update(query, (collection_id, content_id))
        return self.conn.total_changes > 0

    def get_collection_contents(self, collection_id: int) -> List[Dict]:
        """コレクションのコンテンツ取得"""
        query = """
            SELECT c.* FROM contents c
            INNER JOIN collection_items ci ON c.content_id = ci.content_id
            WHERE ci.collection_id = ?
            ORDER BY ci.added_at DESC
        """
        rows = self.execute_query(query, (collection_id,))
        return [dict(row) for row in rows]

    def create_search_log(
        self,
        query: str,
        results_count: int,
        clicked_contents: Optional[List[str]] = None
    ) -> int:
        """検索ログ作成"""
        import json as json_module
        clicked_json = json_module.dumps(clicked_contents) if clicked_contents else None
        query_str = """
            INSERT INTO search_logs (query, results_count, clicked_contents)
            VALUES (?, ?, ?)
        """
        return self.execute_update(query_str, (query, results_count, clicked_json))

    def get_search_logs(
        self,
        limit: int = 100
    ) -> List[Dict]:
        """検索ログ取得"""
        rows = self.execute_query(
            "SELECT * FROM search_logs ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        return [dict(row) for row in rows]

    def get_statistics(self) -> Dict:
        """統計情報取得"""
        total_contents = self.execute_query("SELECT COUNT(*) FROM contents")[0][0]
        total_tags = self.execute_query("SELECT COUNT(*) FROM tags")[0][0]
        total_collections = self.execute_query("SELECT COUNT(*) FROM collections")[0][0]
        total_searches = self.execute_query("SELECT COUNT(*) FROM search_logs")[0][0]

        # アーティスト別分布
        artists = self.execute_query("""
            SELECT artist, COUNT(*) as count
            FROM contents
            GROUP BY artist
            ORDER BY count DESC
            LIMIT 10
        """)

        return {{
            "total_contents": total_contents,
            "total_tags": total_tags,
            "total_collections": total_collections,
            "total_searches": total_searches,
            "top_artists": [dict(artist) for artist in artists]
        }}


if __name__ == "__main__":
    import json
    with EroticAdvancedDB() as db:
        stats = db.get_statistics()
        print("統計情報:")
        print(json.dumps(stats, indent=2, ensure_ascii=False))
'''
    return template

def generate_discord_py(agent):
    """discord.pyを生成"""
    agent_class = agent['name'].replace('-', '_').title().replace('_', '')
    template = f'''#!/usr/bin/env python3
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
from db import EroticAdvancedDB


class {agent_class}Discord:
    """Discordボットインターフェース"""

    def __init__(self):
        self.db = EroticAdvancedDB()

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

    def handle_search(self, user_id: str, args: list) -> dict:
        """検索コマンド処理"""
        if len(args) < 1:
            return {{"error": "Usage: search <query>"}}

        query = " ".join(args)
        contents = self.db.list_contents(tag=query, limit=10)

        # 検索ログ
        self.db.create_search_log(query, len(contents))

        if not contents:
            return {{
                "success": True,
                "message": f"検索結果が見つかりませんでした: {{query}}"
            }}

        lines = [f"**検索結果: {{query}}** ({{len(contents)}}件)"]

        for content in contents[:5]:
            lines.append(f"- {{content['title']}} ({{content['artist']}})")
            lines.append(f"  タグ: {{content['tags'][:50]}}..." if len(content['tags']) > 50 else f"  タグ: {{content['tags']}}")

        return {{
            "success": True,
            "message": "\\n".join(lines)
        }}

    def handle_content(self, user_id: str, args: list) -> dict:
        """コンテンツ詳細コマンド処理"""
        if len(args) < 1:
            return {{"error": "Usage: content <content_id>"}}

        content_id = args[0]
        content = self.db.get_content(content_id)

        if not content:
            return {{
                "success": True,
                "message": f"コンテンツが見つかりませんでした: {{content_id}}"
            }}

        lines = ["**コンテンツ詳細**"]
        lines.append(f"タイトル: {{content['title']}}")
        lines.append(f"アーティスト: {{content['artist']}}")
        lines.append(f"ソース: {{content['source']}}")
        lines.append(f"タグ: {{content['tags']}}")
        if content['description']:
            lines.append(f"説明: {{content['description']}}")

        return {{
            "success": True,
            "message": "\\n".join(lines)
        }}

    def handle_tags(self, user_id: str, args: list) -> dict:
        """タグ一覧コマンド処理"""
        category = args[0] if len(args) > 0 else None
        tags = self.db.list_tags(category=category, limit=30)

        if not tags:
            return {{
                "success": True,
                "message": "タグが見つかりませんでした"
            }}

        lines = ["**タグ一覧**"]

        for tag in tags[:20]:
            lines.append(f"- {{tag['tag_name']}} ({{tag['count']}}回)")

        return {{
            "success": True,
            "message": "\\n".join(lines)
        }}

    def handle_collection(self, user_id: str, args: list) -> dict:
        """コレクションコマンド処理"""
        if len(args) < 1:
            # コレクション一覧
            collections = self.db.list_collections(limit=10)

            if not collections:
                return {{
                    "success": True,
                    "message": "コレクションが見つかりませんでした"
                }}

            lines = ["**コレクション一覧**"]

            for collection in collections:
                lines.append(f"- {{collection['collection_name']}}: {{collection['description'][:50]}}...")

            return {{
                "success": True,
                "message": "\\n".join(lines)
            }}

        # コレクション詳細
        collection_id = int(args[0]) if args[0].isdigit() else None
        if collection_id:
            contents = self.db.get_collection_contents(collection_id)

            if not contents:
                return {{
                    "success": True,
                    "message": f"コレクションID {{collection_id}} にコンテンツが見つかりませんでした"
                }}

            lines = [f"**コレクション内容 ({{len(contents)}}件)**"]

            for content in contents[:10]:
                lines.append(f"- {{content['title']}} ({{content['artist']}})")

            return {{
                "success": True,
                "message": "\\n".join(lines)
            }}

        return {{"error": "Invalid collection_id"}}

    def handle_stats(self, user_id: str, args: list) -> dict:
        """統計コマンド処理"""
        stats = self.db.get_statistics()

        lines = ["**統計情報**"]
        lines.append(f"総コンテンツ数: {{stats['total_contents']}}")
        lines.append(f"総タグ数: {{stats['total_tags']}}")
        lines.append(f"総コレクション数: {{stats['total_collections']}}")
        lines.append(f"総検索数: {{stats['total_searches']}}")

        if stats['top_artists']:
            lines.append("\\n**トップアーティスト**:")
            for artist in stats['top_artists'][:5]:
                lines.append(f"- {{artist['artist']}}: {{artist['count']}}作品")

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
            "search": self.handle_search,
            "content": self.handle_content,
            "tags": self.handle_tags,
            "collection": self.handle_collection,
            "stats": self.handle_stats
        }}

        handler = handlers.get(command)
        if handler:
            return handler(user_id, args)
        else:
            return {{
                "error": f"Unknown command: {{command}}\\nAvailable commands: search, content, tags, collection, stats"
            }}

    def format_response(self, response: dict) -> str:
        """レスポンスを整形"""
        if "error" in response:
            return f"❌ {{response['error']}}"

        if "message" in response:
            emoji_map = {{
                "search": "🔍",
                "content": "📄",
                "tags": "🏷️",
                "collection": "📚",
                "stats": "📊"
            }}
            command = response.get("command", "")
            emoji = emoji_map.get(command, "✅")
            return f"{{emoji}} {{response['message']}}"

        return "✅ コマンドを実行しました"


if __name__ == "__main__":
    bot = {agent_class}Discord()

    # テスト
    user_id = "test-user"
    print("コマンドテスト:")

    # テスト: search
    result = bot.handle_command(user_id, "!erotic search アニメ")
    print(f"search: {{bot.format_response(result)}}")

    # テスト: stats
    result = bot.handle_command(user_id, "!erotic stats")
    print(f"stats: {{bot.format_response(result)}}")
'''
    return template

def generate_readme(agent):
    """README.mdを生成"""
    template = f'''# {agent['name']}

{agent['emoji']} {agent['description_ja']} / {agent['description_en']}

## 概要 (Overview)

このエージェントは、えっちコンテンツの高度な検索・キュレーション機能を提供します。意味検索、タグ分析、コレクション管理、自動キュレーションなどが可能です。

This agent provides advanced search and curation features for erotic content, including semantic search, tag analysis, collection management, and auto-curation.

## 機能 (Features)

### 検索機能 (Search Features)
- **意味検索** (Semantic Search): タグベースの高度な検索
- **関連コンテンツ** (Related Contents): 類似コンテンツの自動推薦
- **検索候補** (Search Suggestions): 入力補完と検索履歴に基づく候補

### キュレーション機能 (Curation Features)
- **コレクション管理** (Collection Management): お気に入りコレクションの作成・管理
- **自動キュレーション** (Auto-Curation): タグや条件に基づく自動追加
- **手動キュレーション** (Manual Curation): 手動でのコンテンツ追加・削除

### タグ分析 (Tag Analysis)
- **タグ頻度分析** (Tag Frequency Analysis): 人気タグの把握
- **関連タグ** (Related Tags): タグ間の関連性分析
- **カテゴリ管理** (Category Management): タグのカテゴリ分類

### コンテンツディスカバリー (Content Discovery)
- **トレンド追跡** (Trend Tracking): 注目コンテンツの発見
- **新規コンテンツ** (New Content): 新着コンテンツの通知
- **おすすめ** (Recommendations): 個別化された推薦

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

# コンテンツ追加
agent.add_content(
    "er001",
    "美少女の冒険",
    "ArtistA",
    "pixiv",
    "https://example.com/1",
    "アニメ,美少女,冒険",
    "かわいい"
)

# 検索
results = agent.semantic_search("アニメ")

# コレクション作成
collection_id = agent.create_collection("お気に入り", "かわいい作品", "美少女")

# コレクションに追加
agent.add_to_collection(collection_id, "er001")

# 接続を閉じる
agent.get_close()
```

### Discord Bot

```
!erotic search <query>
!erotic content <content_id>
!erotic tags [category]
!erotic collection [collection_id]
!erotic stats
```

## データベース (Database)

- `contents`: コンテンツデータ
- `tags`: タグデータ
- `content_tags`: コンテンツ-タグ関連付け
- `search_logs`: 検索ログ
- `collections`: コレクション
- `collection_items`: コレクションアイテム

## 環境変数 (Environment Variables)

- `DISCORD_TOKEN`: Discordボットトークン

## ライセンス (License)

MIT License
'''
    return template

def generate_requirements_txt(agent):
    """requirements.txtを生成"""
    return '''# Erotic Content Advanced Search & Curation Agent Requirements

# Core
python-dotenv>=1.0.0

# Discord
discord.py>=2.3.0

# Database
sqlite3  # Python標準ライブラリ

# Search & NLP
scikit-learn>=1.3.0
numpy>=1.24.0
pandas>=2.0.0

# Optional: Vector Database for semantic search
chromadb>=0.4.0  # Vector embeddings
sentence-transformers>=2.2.0  # Text embeddings
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
    print("えっちコンテンツ高度検索・キュレーション エージェント オーケストレーター")
    print("Erotic Content Advanced Search & Curation Agent Orchestrator")
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
        if commit_changes(f"feat: えっちコンテンツ高度検索・キュレーションエージェントプロジェクト完了 ({completed_count}/{total})"):
            push_changes()

    print(f"\n🎉 オーケストレーション完了！")
    print(f"\n作成されたエージェント:")
    for agent in AGENTS:
        status = progress["agents"].get(agent["name"], {}).get("status", "pending")
        emoji = "✅" if status == "completed" else "❌"
        print(f"  {emoji} {agent['name']} - {agent['description_ja']}")

if __name__ == "__main__":
    main()
