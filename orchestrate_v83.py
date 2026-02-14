#!/usr/bin/env python3
"""
オーケストレーター - V83 エージェント生成
25個のエージェントを自動生成
"""

import os
import json
from pathlib import Path

# プロジェクトルート
PROJECT_ROOT = Path("/workspace")
AGENTS_DIR = PROJECT_ROOT / "agents"

# 進捗管理ファイル
PROGRESS_FILE = PROJECT_ROOT / "v83_progress.json"

# エージェント定義
AGENTS = [
    # 野球球場・スタジアムエージェント (5個)
    {
        "name": "baseball-stadium-agent",
        "title": "野球場エージェント",
        "description": "野球場の情報管理",
        "category": "baseball",
        "language": "Japanese",
        "tools": ["pandas", "numpy", "requests", "geopy", "matplotlib"]
    },
    {
        "name": "baseball-seating-agent",
        "title": "野球場座席エージェント",
        "description": "野球場座席の管理・販売",
        "category": "baseball",
        "language": "Japanese",
        "tools": ["pandas", "numpy", "requests", "fastapi", "sqlalchemy"]
    },
    {
        "name": "baseball-amenities-agent",
        "title": "野球場アメニティエージェント",
        "description": "野球場アメニティの管理",
        "category": "baseball",
        "language": "Japanese",
        "tools": ["pandas", "numpy", "requests", "fastapi", "rich"]
    },
    {
        "name": "baseball-venue-agent",
        "title": "野球会場エージェント",
        "description": "野球会場の管理・運営",
        "category": "baseball",
        "language": "Japanese",
        "tools": ["pandas", "numpy", "requests", "geopy", "fastapi"]
    },
    {
        "name": "baseball-facilities-agent",
        "title": "野球場施設エージェント",
        "description": "野球場施設の管理・メンテナンス",
        "category": "baseball",
        "language": "Japanese",
        "tools": ["pandas", "numpy", "requests", "schedule", "rich"]
    },

    # ゲームクロスプラットフォームエージェント (5個)
    {
        "name": "game-cross-platform-agent",
        "title": "ゲームクロスプラットフォームエージェント",
        "description": "ゲームのクロスプラットフォーム対応",
        "category": "gaming",
        "language": "Japanese",
        "tools": ["pandas", "numpy", "requests", "fastapi", "redis"]
    },
    {
        "name": "game-sync-engine-agent",
        "title": "ゲーム同期エンジンエージェント",
        "description": "ゲームデータの同期エンジン",
        "category": "gaming",
        "language": "Japanese",
        "tools": ["pandas", "numpy", "requests", "redis", "websockets"]
    },
    {
        "name": "game-cloud-save-agent",
        "title": "ゲームクラウドセーブエージェント",
        "description": "ゲームクラウドセーブの管理",
        "category": "gaming",
        "language": "Japanese",
        "tools": ["pandas", "numpy", "boto3", "azure-sdk", "fastapi"]
    },
    {
        "name": "game-progression-agent",
        "title": "ゲーム進行管理エージェント",
        "description": "ゲーム進行状況の管理",
        "category": "gaming",
        "language": "Japanese",
        "tools": ["pandas", "numpy", "requests", "fastapi", "redis"]
    },
    {
        "name": "game-achievement-sync-agent",
        "title": "ゲーム実績同期エージェント",
        "description": "ゲーム実績の同期・管理",
        "category": "gaming",
        "language": "Japanese",
        "tools": ["pandas", "numpy", "requests", "fastapi", "redis"]
    },

    # えっちコンテンツユーザーフィードバックエージェント (5個)
    {
        "name": "erotic-feedback-collector-agent",
        "title": "えっちコンテンツフィードバック収集エージェント",
        "description": "えっちコンテンツのフィードバック収集",
        "category": "content",
        "language": "Japanese",
        "tools": ["pandas", "numpy", "requests", "fastapi", "sqlalchemy"]
    },
    {
        "name": "erotic-feedback-analyzer-agent",
        "title": "えっちコンテンツフィードバック分析エージェント",
        "description": "えっちコンテンツのフィードバック分析",
        "category": "content",
        "language": "Japanese",
        "tools": ["pandas", "numpy", "scikit-learn", "matplotlib", "seaborn"]
    },
    {
        "name": "erotic-rating-system-agent",
        "title": "えっちコンテンツ評価システムエージェント",
        "description": "えっちコンテンツの評価システム",
        "category": "content",
        "language": "Japanese",
        "tools": ["pandas", "numpy", "requests", "fastapi", "redis"]
    },
    {
        "name": "erotic-review-moderator-agent",
        "title": "えっちコンテンツレビューモデレーターエージェント",
        "description": "えっちコンテンツレビューのモデレーション",
        "category": "content",
        "language": "Japanese",
        "tools": ["pandas", "numpy", "scikit-learn", "requests", "fastapi"]
    },
    {
        "name": "erotic-suggestion-agent",
        "title": "えっちコンテンツ提案エージェント",
        "description": "えっちコンテンツの提案・推奨",
        "category": "content",
        "language": "Japanese",
        "tools": ["pandas", "numpy", "scikit-learn", "requests", "fastapi"]
    },

    # API管理・ゲートウェイエージェント (5個)
    {
        "name": "api-gateway-v2-agent",
        "title": "APIゲートウェイV2エージェント",
        "description": "APIゲートウェイの管理V2",
        "category": "cloud",
        "language": "Japanese",
        "tools": ["fastapi", "uvicorn", "requests", "redis", "prometheus-client"]
    },
    {
        "name": "api-versioning-agent",
        "title": "APIバージョニングエージェント",
        "description": "APIバージョンの管理",
        "category": "cloud",
        "language": "Japanese",
        "tools": ["fastapi", "uvicorn", "requests", "pyyaml", "rich"]
    },
    {
        "name": "api-rate-limit-agent",
        "title": "APIレート制限エージェント",
        "description": "APIレート制限の管理",
        "category": "cloud",
        "language": "Japanese",
        "tools": ["fastapi", "uvicorn", "redis", "prometheus-client", "requests"]
    },
    {
        "name": "api-documentation-agent",
        "title": "APIドキュメントエージェント",
        "description": "APIドキュメントの生成・管理",
        "category": "cloud",
        "language": "Japanese",
        "tools": ["fastapi", "uvicorn", "swagger", "redoc", "requests"]
    },
    {
        "name": "api-testing-agent",
        "title": "APIテストエージェント",
        "description": "APIテストの自動化",
        "category": "cloud",
        "language": "Japanese",
        "tools": ["requests", "pytest", "locust", "jupyter", "fastapi"]
    },

    # セキュリティ監査・コンプライアンスエージェント (5個)
    {
        "name": "audit-manager-agent",
        "title": "監査マネージャーエージェント",
        "description": "監査ログの管理・分析",
        "category": "security",
        "language": "Japanese",
        "tools": ["pandas", "numpy", "requests", "elasticsearch", "rich"]
    },
    {
        "name": "compliance-monitor-agent",
        "title": "コンプライアンスモニターエージェント",
        "description": "コンプライアンスの監視・チェック",
        "category": "security",
        "language": "Japanese",
        "tools": ["pandas", "numpy", "requests", "schedule", "rich"]
    },
    {
        "name": "risk-assessment-agent",
        "title": "リスクアセスメントエージェント",
        "description": "セキュリティリスクの評価",
        "category": "security",
        "language": "Japanese",
        "tools": ["pandas", "numpy", "scikit-learn", "requests", "rich"]
    },
    {
        "name": "security-gap-analysis-agent",
        "title": "セキュリティギャップ分析エージェント",
        "description": "セキュリティギャップの分析",
        "category": "security",
        "language": "Japanese",
        "tools": ["pandas", "numpy", "requests", "pyyaml", "rich"]
    },
    {
        "name": "incident-review-agent",
        "title": "インシデントレビューエージェント",
        "description": "インシデントのレビュー・分析",
        "category": "security",
        "language": "Japanese",
        "tools": ["pandas", "numpy", "requests", "jinja2", "rich"]
    },
]

# テンプレート（V79-V82と同じ）
AGENT_TEMPLATE = '''#!/usr/bin/env python3
"""
{title}
{description}
"""

import asyncio
import os
from typing import Optional, Dict, Any, List
from datetime import datetime
import json

class {agent_class}:
    """{title}"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {{}}
        self.name = "{agent_name}"
        self.title = "{title}"
        self.description = "{description}"
        self.category = "{category}"
        self.language = "{language}"
        self.state = "idle"
        self.created_at = datetime.now().isoformat()
        self.tasks: List[Dict[str, Any]] = []

    async def initialize(self) -> bool:
        """エージェントの初期化"""
        try:
            self.state = "initializing"
            print(f"Initializing {{self.title}}...")
            await asyncio.sleep(0.5)
            self.state = "ready"
            return True
        except Exception as e:
            print(f"Error initializing: {{e}}")
            self.state = "error"
            return False

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """データ処理"""
        if self.state != "ready":
            return {{"error": "Agent not ready", "state": self.state}}

        self.state = "processing"
        try:
            result = {{
                "success": True,
                "data": input_data,
                "processed_at": datetime.now().isoformat(),
                "agent": self.name
            }}
            self.state = "ready"
            return result
        except Exception as e:
            self.state = "error"
            return {{"error": str(e), "state": self.state}}

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """タスク実行"""
        task_id = task.get("id", f"task_{{len(self.tasks)}}")
        self.tasks.append({{"id": task_id, "task": task, "status": "pending"}})

        try:
            result = await self.process(task.get("data", {{}}))
            self.tasks[-1]["status"] = "completed"
            return result
        except Exception as e:
            self.tasks[-1]["status"] = "failed"
            return {{"error": str(e), "task_id": task_id}}

    async def get_status(self) -> Dict[str, Any]:
        """ステータス取得"""
        return {{
            "name": self.name,
            "title": self.title,
            "state": self.state,
            "tasks_completed": sum(1 for t in self.tasks if t["status"] == "completed"),
            "tasks_pending": sum(1 for t in self.tasks if t["status"] == "pending"),
            "created_at": self.created_at
        }}

    async def cleanup(self) -> None:
        """クリーンアップ"""
        self.state = "stopped"
        print(f"{{self.title}} stopped.")

async def main():
    """メイン処理"""
    agent = {agent_class}()
    await agent.initialize()

    sample_task = {{
        "id": "sample_001",
        "data": {{
            "message": "Sample task for {title}"
        }}
    }}

    result = await agent.execute_task(sample_task)
    print(f"Result: {{json.dumps(result, ensure_ascii=False, indent=2)}}")

    status = await agent.get_status()
    print(f"Status: {{json.dumps(status, ensure_ascii=False, indent=2)}}")

    await agent.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
'''

DB_TEMPLATE = '''#!/usr/bin/env python3
"""
{title} - データベース管理
SQLiteベースのデータ永続化
"""

import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
import json

class {db_class}:
    """{title} データベースクラス"""

    def __init__(self, db_path: str = "{db_path}"):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self):
        """データベース接続のコンテキストマネージャ"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def _init_db(self):
        """データベース初期化"""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    title TEXT,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT UNIQUE NOT NULL,
                    status TEXT DEFAULT 'pending',
                    result TEXT,
                    error TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def insert_record(self, record_type: str, title: str, content: str,
                       metadata: Optional[Dict[str, Any]] = None) -> int:
        """レコード挿入"""
        metadata_json = json.dumps(metadata) if metadata else None
        with self._get_connection() as conn:
            cursor = conn.execute(
                'INSERT INTO records (type, title, content, metadata) VALUES (?, ?, ?, ?)',
                (record_type, title, content, metadata_json)
            )
            return cursor.lastrowid

    def get_record(self, record_id: int) -> Optional[Dict[str, Any]]:
        """レコード取得"""
        with self._get_connection() as conn:
            row = conn.execute('SELECT * FROM records WHERE id = ?', (record_id,)).fetchone()
            if row:
                return dict(row)
        return None

    def list_records(self, record_type: Optional[str] = None,
                    limit: int = 100) -> List[Dict[str, Any]]:
        """レコード一覧"""
        with self._get_connection() as conn:
            if record_type:
                rows = conn.execute(
                    'SELECT * FROM records WHERE type = ? ORDER BY created_at DESC LIMIT ?',
                    (record_type, limit)
                ).fetchall()
            else:
                rows = conn.execute(
                    'SELECT * FROM records ORDER BY created_at DESC LIMIT ?',
                    (limit,)
                ).fetchall()
            return [dict(row) for row in rows]

    def insert_task(self, task_id: str, status: str = "pending") -> int:
        """タスク挿入"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                'INSERT INTO tasks (task_id, status) VALUES (?, ?)',
                (task_id, status)
            )
            return cursor.lastrowid

    def update_task(self, task_id: str, status: str,
                   result: Optional[str] = None, error: Optional[str] = None):
        """タスク更新"""
        completed_at = datetime.now().isoformat() if status == "completed" else None
        with self._get_connection() as conn:
            conn.execute(
                'UPDATE tasks SET status = ?, result = ?, error = ?, completed_at = ? WHERE task_id = ?',
                (status, result, error, completed_at, task_id)
            )

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """タスク取得"""
        with self._get_connection() as conn:
            row = conn.execute('SELECT * FROM tasks WHERE task_id = ?', (task_id,)).fetchone()
            if row:
                return dict(row)
        return None

    def set_setting(self, key: str, value: str):
        """設定保存"""
        with self._get_connection() as conn:
            conn.execute(
                'INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = ?, updated_at = CURRENT_TIMESTAMP',
                (key, value, value)
            )

    def get_setting(self, key: str) -> Optional[str]:
        """設定取得"""
        with self._get_connection() as conn:
            row = conn.execute('SELECT value FROM settings WHERE key = ?', (key,)).fetchone()
            if row:
                return row['value']
        return None

async def main():
    """動作確認"""
    db = {db_class}()

    record_id = db.insert_record(
        record_type="sample",
        title="Sample Record",
        content="This is a sample record for {title}"
    )
    print(f"Inserted record: {{record_id}}")

    record = db.get_record(record_id)
    print(f"Retrieved record: {{record}}")

    db.insert_task("task_001")
    db.update_task("task_001", "completed", result="Success")

    task = db.get_task("task_001")
    print(f"Task status: {{task}}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
'''

DISCORD_TEMPLATE = '''#!/usr/bin/env python3
"""
{title} - Discord連携
Discordボットインターフェース
"""

import asyncio
import os
from typing import Optional, Dict, Any, List
from datetime import datetime

class {discord_class}:
    """{title} Discord連携クラス"""

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("DISCORD_TOKEN")
        self.client = None
        self.commands: List[Dict[str, Any]] = []

    async def start(self):
        """Discordボット起動"""
        if not self.token:
            print("DISCORD_TOKEN not set, running in mock mode")
            return

        try:
            import discord
            intents = discord.Intents.default()
            intents.message_content = True
            self.client = discord.Client(intents=intents)

            @self.client.event
            async def on_ready():
                print(f'{{self.client.user}} has connected to Discord!')

            @self.client.event
            async def on_message(message):
                if message.author == self.client.user:
                    return

                await self._handle_message(message)

            await self.client.start(self.token)
        except ImportError:
            print("discord.py not installed, running in mock mode")

    async def _handle_message(self, message):
        """メッセージハンドリング"""
        content = message.content.lower()

        if content.startswith('!help'):
            help_text = await self.get_help()
            await message.channel.send(help_text)

        elif content.startswith('!status'):
            status = await self.get_status()
            await message.channel.send(status)

    async def send_message(self, channel_id: int, content: str):
        """メッセージ送信"""
        if self.client:
            channel = self.client.get_channel(channel_id)
            if channel:
                await channel.send(content)
        else:
            print(f"Mock: Send to channel {{channel_id}}: {{content}}")

    async def get_help(self) -> str:
        """ヘルプメッセージ"""
        return f"""
**{title} - Commands**

!help - Show this help message
!status - Show agent status
!info - Show agent information

{category} category agent
"""

    async def get_status(self) -> str:
        """ステータスメッセージ"""
        return f"""
**{title} Status**

Status: Ready
Language: {language}
Category: {category}
Commands: {{len(self.commands)}}
"""

    async def stop(self):
        """ボット停止"""
        if self.client:
            await self.client.close()

async def main():
    """動作確認"""
    bot = {discord_class}()
    await bot.start()

if __name__ == "__main__":
    asyncio.run(main())
'''

README_TEMPLATE = '''# {title}

{description}

## 概要

{title}は{category}カテゴリのエージェントです。{language}言語に対応しています。

## 機能

- データ処理・分析
- タスク管理
- 状態監視
- Discord連携

## インストール

```bash
pip install -r requirements.txt
```

## 使用方法

### エージェントとして実行

```bash
python agent.py
```

### データベース操作

```bash
python db.py
```

### Discordボット

```bash
export DISCORD_TOKEN=your_token
python discord.py
```

## データベース構造

### records テーブル
- `id`: 主キー
- `type`: レコードタイプ
- `title`: タイトル
- `content`: コンテンツ
- `metadata`: メタデータ（JSON）
- `created_at`: 作成日時
- `updated_at`: 更新日時

### tasks テーブル
- `id`: 主キー
- `task_id`: タスクID
- `status`: ステータス（pending/completed/failed）
- `result`: 結果
- `error`: エラーメッセージ
- `created_at`: 作成日時
- `completed_at`: 完了日時

### settings テーブル
- `key`: 設定キー
- `value`: 設定値
- `updated_at`: 更新日時

## Discordコマンド

- `!help` - ヘルプ表示
- `!status` - ステータス確認
- `!info` - エージェント情報

## API

### Agent

```python
from agent import {agent_class}

agent = {agent_class}()
await agent.initialize()
result = await agent.process(data)
```

### Database

```python
from db import {db_class}

db = {db_class}()
record_id = db.insert_record("type", "title", "content")
record = db.get_record(record_id)
```

## 言語サポート

- {language}

## ライセンス

MIT License
'''

REQUIREMENTS_TEMPLATE = '''# Requirements for {title}
# Automatically generated dependencies

# Core dependencies
asyncio
typing
datetime
json
sqlite3
contextlib

# Additional dependencies
'''

def generate_agent_files(agent_info: dict) -> bool:
    """エージェントファイル生成"""
    name = agent_info["name"]
    title = agent_info["title"]
    description = agent_info["description"]
    category = agent_info["category"]
    language = agent_info["language"]
    tools = agent_info["tools"]

    # ディレクトリ作成
    agent_dir = AGENTS_DIR / name
    agent_dir.mkdir(parents=True, exist_ok=True)

    # クラス名生成
    agent_class = "".join(word.capitalize() for word in name.replace("-", " ").split()).replace("_", "")
    db_class = f"{agent_class}DB"
    discord_class = f"{agent_class}Discord"

    # ファイル生成
    try:
        # agent.py
        agent_content = AGENT_TEMPLATE.format(
            title=title,
            description=description,
            agent_class=agent_class,
            agent_name=name,
            category=category,
            language=language
        )
        (agent_dir / "agent.py").write_text(agent_content)

        # db.py
        db_content = DB_TEMPLATE.format(
            title=title,
            db_class=db_class,
            db_path=f"data/{name}.db"
        )
        (agent_dir / "db.py").write_text(db_content)

        # discord.py
        discord_content = DISCORD_TEMPLATE.format(
            title=title,
            discord_class=discord_class,
            category=category,
            language=language
        )
        (agent_dir / "discord.py").write_text(discord_content)

        # README.md
        readme_content = README_TEMPLATE.format(
            title=title,
            description=description,
            category=category,
            language=language,
            agent_class=agent_class,
            db_class=db_class
        )
        (agent_dir / "README.md").write_text(readme_content)

        # requirements.txt
        requirements_content = REQUIREMENTS_TEMPLATE.format(title=title)
        for tool in tools:
            requirements_content += f"# {tool}\n"
        (agent_dir / "requirements.txt").write_text(requirements_content)

        print(f"✅ Generated: {name}")
        return True

    except Exception as e:
        print(f"❌ Error generating {name}: {e}")
        return False

def load_progress() -> dict:
    """進捗読み込み"""
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text())
    return {"completed": [], "failed": []}

def save_progress(progress: dict):
    """進捗保存"""
    PROGRESS_FILE.write_text(json.dumps(progress, indent=2))

def main():
    """メイン処理"""
    progress = load_progress()

    print(f"\n🚀 Starting V83 Orchestration...")
    print(f"   Total agents: {len(AGENTS)}")
    print(f"   Already completed: {len(progress['completed'])}")
    print(f"   Failed: {len(progress['failed'])}\n")

    for agent_info in AGENTS:
        if agent_info["name"] in progress["completed"]:
            print(f"⏭️  Skipping: {agent_info['name']} (already completed)")
            continue

        if agent_info["name"] in progress["failed"]:
            print(f"🔄 Retrying: {agent_info['name']} (previously failed)")

        success = generate_agent_files(agent_info)
        if success:
            progress["completed"].append(agent_info["name"])
            print(f"✅ Completed: {agent_info['name']}")
        else:
            progress["failed"].append(agent_info["name"])
            print(f"❌ Failed: {agent_info['name']}")

        save_progress(progress)

    print(f"\n📊 Summary:")
    print(f"   Total: {len(AGENTS)}")
    print(f"   Completed: {len(progress['completed'])}")
    print(f"   Failed: {len(progress['failed'])}")

    if len(progress["completed"]) == len(AGENTS):
        print(f"\n🎉 All agents generated successfully!")
    else:
        print(f"\n⚠️  Some agents failed. Check the list above.")

if __name__ == "__main__":
    main()
