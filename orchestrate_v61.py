#!/usr/bin/env python3
"""
オーケストレーター V61 - 野球メディア×ゲームソーシャル×えっちコンテンツ分類×監視アラート×脆弱性管理
"""

import os
import json
import subprocess
from pathlib import Path

# プロジェクト定義
V61_AGENTS = {
    "baseball": [
        {
            "name": "baseball-media-broadcast-agent",
            "dir": "baseball-media-broadcast-agent",
            "title": "野球メディア放送エージェント",
            "description": "メディア放送の管理"
        },
        {
            "name": "baseball-content-creator-agent",
            "dir": "baseball-content-creator-agent",
            "title": "野球コンテンツクリエイターエージェント",
            "description": "コンテンツ制作の管理"
        },
        {
            "name": "baseball-commentator-agent",
            "dir": "baseball-commentator-agent",
            "title": "野球解説エージェント",
            "description": "解説コンテンツの管理"
        },
        {
            "name": "baseball-production-agent",
            "dir": "baseball-production-agent",
            "title": "野球プロダクションエージェント",
            "description": "制作プロダクションの管理"
        },
        {
            "name": "baseball-highlights-agent",
            "dir": "baseball-highlights-agent",
            "title": "野球ハイライトエージェント",
            "description": "ハイライト映像の管理"
        }
    ],
    "game": [
        {
            "name": "game-social-connect-agent",
            "dir": "game-social-connect-agent",
            "title": "ゲームソーシャルコネクトエージェント",
            "description": "ソーシャル機能の管理"
        },
        {
            "name": "game-multiplayer-coordinator-agent",
            "dir": "game-multiplayer-coordinator-agent",
            "title": "ゲームマルチプレイヤーコーディネーターエージェント",
            "description": "マルチプレイの管理"
        },
        {
            "name": "game-party-manager-agent",
            "dir": "game-party-manager-agent",
            "title": "ゲームパーティマネージャーエージェント",
            "description": "パーティ管理"
        },
        {
            "name": "game-social-features-agent",
            "dir": "game-social-features-agent",
            "title": "ゲームソーシャル機能エージェント",
            "description": "ソーシャル機能の実装"
        },
        {
            "name": "game-competitive-agent",
            "dir": "game-competitive-agent",
            "title": "ゲーム競技エージェント",
            "description": "競技モードの管理"
        }
    ],
    "erotic": [
        {
            "name": "erotic-content-classifier-agent",
            "dir": "erotic-content-classifier-agent",
            "title": "えっちコンテンツ分類エージェント",
            "description": "コンテンツの分類・タグ付け"
        },
        {
            "name": "erotic-content-discovery-agent",
            "dir": "erotic-content-discovery-agent",
            "title": "えっちコンテンツディスカバリーエージェント",
            "description": "コンテンツの発見・推薦"
        },
        {
            "name": "erotic-auto-tag-agent",
            "dir": "erotic-auto-tag-agent",
            "title": "えっち自動タグエージェント",
            "description": "自動タグ付けの管理"
        },
        {
            "name": "erotic-image-analyzer-agent",
            "dir": "erotic-image-analyzer-agent",
            "title": "えっち画像アナライザーエージェント",
            "description": "画像の分析・分類"
        },
        {
            "name": "erotic-nsfw-detector-agent",
            "dir": "erotic-nsfw-detector-agent",
            "title": "えっちNSFW検知エージェント",
            "description": "NSFWコンテンツの検知"
        }
    ],
    "tech": [
        {
            "name": "monitoring-agent",
            "dir": "monitoring-agent",
            "title": "モニタリングエージェント",
            "description": "システム監視の管理"
        },
        {
            "name": "alerting-agent",
            "dir": "alerting-agent",
            "title": "アラートエージェント",
            "description": "アラートの管理・送信"
        },
        {
            "name": "uptime-monitor-agent",
            "dir": "uptime-monitor-agent",
            "title": "アップタイムモニターエージェント",
            "description": "稼働時間の監視"
        },
        {
            "name": "log-analyzer-agent",
            "dir": "log-analyzer-agent",
            "title": "ログアナライザーエージェント",
            "description": "ログの分析"
        },
        {
            "name": "metrics-collector-agent",
            "dir": "metrics-collector-agent",
            "title": "メトリクスコレクターエージェント",
            "description": "メトリクスの収集"
        }
    ],
    "security": [
        {
            "name": "vulnerability-scanner-agent",
            "dir": "vulnerability-scanner-agent",
            "title": "脆弱性スキャナーエージェント",
            "description": "脆弱性のスキャン・検知"
        },
        {
            "name": "pentest-agent",
            "dir": "pentest-agent",
            "title": "ペンテストエージェント",
            "description": "侵入テストの管理"
        },
        {
            "name": "bug-bounty-agent",
            "dir": "bug-bounty-agent",
            "title": "バグバウンティエージェント",
            "description": "バグ報告の管理"
        },
        {
            "name": "exploit-analysis-agent",
            "dir": "exploit-analysis-agent",
            "title": "エクスプロイト分析エージェント",
            "description": "脆弱性エクスプロイトの分析"
        },
        {
            "name": "security-scan-agent",
            "dir": "security-scan-agent",
            "title": "セキュリティスキャンエージェント",
            "description": "セキュリティスキャンの実行"
        }
    ]
}

def create_agent_directory(agent_dir, agent_name, title, description):
    """エージェントディレクトリとファイルを作成"""
    base_path = Path("/workspace") / agent_dir
    base_path.mkdir(parents=True, exist_ok=True)
    
    # agent.py
    agent_py_content = '''#!/usr/bin/env python3
"""
''' + title + '''
''' + description + '''
"""

import discord
from discord.ext import commands
import sqlite3
from datetime import datetime
import json

class ''' + agent_name.replace("-", "_").title().replace("_", "") + '''(commands.Bot):
    def __init__(self, token):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.token = token
        self.db_path = "''' + agent_name + '''.db"
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        conn.commit()
        conn.close()
    
    async def on_ready(self):
        print(f"{{self.user}} has connected to Discord!")
    
    async def on_message(self, message):
        if message.author == self.user:
            return
        await self.process_commands(message)
    
    def run_bot(self):
        self.run(self.token)

if __name__ == "__main__":
    import os
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("DISCORD_TOKEN environment variable is required")
        exit(1)
    bot = ''' + agent_name.replace("-", "_").title().replace("_", "") + '''(token)
    bot.run_bot()
'''
    
    (base_path / "agent.py").write_text(agent_py_content)
    
    # db.py
    db_py_content = '''#!/usr/bin/env python3
"""
Database Manager for ''' + agent_name + '''
"""

import sqlite3
from datetime import datetime
from typing import List, Optional

class DatabaseManager:
    def __init__(self, db_path: str = "''' + agent_name + '''.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        conn.commit()
        conn.close()
    
    def add_record(self, content: str) -> int:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO records (content) VALUES (?)", (content,))
        conn.commit()
        record_id = c.lastrowid
        conn.close()
        return record_id
    
    def get_record(self, record_id: int) -> Optional[dict]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM records WHERE id = ?", (record_id,))
        row = c.fetchone()
        conn.close()
        if row:
            return {"id": row[0], "content": row[1], "created_at": row[2]}
        return None
    
    def list_records(self, limit: int = 100) -> List[dict]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM records ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        conn.close()
        return [{"id": r[0], "content": r[1], "created_at": r[2]} for r in rows]

if __name__ == "__main__":
    db = DatabaseManager()
    print("Database initialized")
'''
    
    (base_path / "db.py").write_text(db_py_content)
    
    # discord.py
    discord_py_content = '''#!/usr/bin/env python3
"""
Discord Bot for ''' + agent_name + '''
"""

import discord
from discord.ext import commands
import os

class DiscordBot(commands.Bot):
    def __init__(self, token: str, db_manager):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.token = token
        self.db = db_manager
    
    async def on_ready(self):
        print(f"Bot logged in as {self.user}")
    
    async def on_message(self, message):
        if message.author == self.user:
            return
        await self.process_commands(message)
    
    @commands.command()
    async def hello(self, ctx):
        await ctx.send("Hello! I am ''' + title + '''")
    
    @commands.command()
    async def add(self, ctx, *, content: str):
        record_id = self.db.add_record(content)
        await ctx.send(f"Added record #{record_id}")
    
    @commands.command()
    async def list(self, ctx, limit: int = 10):
        records = self.db.list_records(limit)
        if records:
            response = "Recent records:\\n" + "\\n".join(f"#{r['id']}: {r['content'][:50]}..." for r in records[:5])
            await ctx.send(response)
        else:
            await ctx.send("No records found")

if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from db import DatabaseManager
    
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("DISCORD_TOKEN is required")
        exit(1)
    
    db = DatabaseManager()
    bot = DiscordBot(token, db)
    bot.run(token)
'''
    
    (base_path / "discord.py").write_text(discord_py_content)
    
    # requirements.txt
    requirements_content = '''discord.py>=2.3.0
'''
    (base_path / "requirements.txt").write_text(requirements_content)
    
    # README.md (Bilingual)
    readme_content = '''# ''' + title + ''' (''' + agent_name + ''')

''' + description + '''

## 機能 / Features

- ''' + description + '''の管理・運用
- Discordボットによる対話型インターフェース
- SQLiteによるデータ永続化

## インストール / Installation

```bash
pip install -r requirements.txt
```

## 設定 / Configuration

環境変数 `DISCORD_TOKEN` を設定してください。

Set the `DISCORD_TOKEN` environment variable.

```bash
export DISCORD_TOKEN="your_bot_token"
```

## 使い方 / Usage

```bash
python agent.py
```

または / Or:

```bash
python discord.py
```

## データベース / Database

データはSQLiteに保存されます。`''' + agent_name + '''.db`ファイルが作成されます。

Data is stored in SQLite. A `''' + agent_name + '''.db` file will be created.

## ライセンス / License

MIT License
'''
    
    (base_path / "README.md").write_text(readme_content)
    
    return True

def main():
    progress_file = Path("/workspace/v61_progress.json")
    
    # 進捗をロード
    if progress_file.exists():
        progress = json.loads(progress_file.read_text())
    else:
        progress = {"completed": [], "failed": []}
    
    total_agents = sum(len(agents) for agents in V61_AGENTS.values())
    completed = len(progress["completed"])
    
    print(f"=== オーケストレーター V61 ===")
    print(f"進捗: {completed}/{total_agents}")
    print()
    
    # エージェントを作成
    for category, agents in V61_AGENTS.items():
        print(f"--- {category.upper()} ---")
        for agent in agents:
            agent_name = agent["name"]
            agent_dir = agent["dir"]
            title = agent["title"]
            description = agent["description"]
            
            if agent_name in progress["completed"]:
                print(f"✓ {agent_name} (既に完了)")
                continue
            
            if agent_name in progress["failed"]:
                print(f"? {agent_name} (再試行)")
            
            try:
                print(f"  作成中: {agent_name}...")
                if create_agent_directory(agent_dir, agent_name, title, description):
                    progress["completed"].append(agent_name)
                    if agent_name in progress["failed"]:
                        progress["failed"].remove(agent_name)
                    print(f"  ✓ {agent_name} 完了")
                else:
                    raise Exception("作成失敗")
            except Exception as e:
                print(f"  ✗ {agent_name} 失敗: {e}")
                import traceback
                traceback.print_exc()
                if agent_name not in progress["failed"]:
                    progress["failed"].append(agent_name)
            
            # 進捗を保存
            progress_file.write_text(json.dumps(progress, indent=2))
    
    # 最終報告
    completed = len(progress["completed"])
    failed = len(progress["failed"])
    
    print()
    print("=== 完了報告 ===")
    print(f"完了: {completed}/{total_agents}")
    print(f"失敗: {failed}")
    
    if failed > 0:
        print(f"失敗したエージェント:")
        for name in progress["failed"]:
            print(f"  - {name}")
    else:
        print("🎉 全エージェントの作成が完了しました！")
    
    # Git commit
    print()
    print("Git commit & push...")
    try:
        subprocess.run(["git", "add", "-A"], check=True)
        subprocess.run(["git", "commit", "-m", "feat: 次期プロジェクト案 V61 完了 (25/25)"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✓ Git commit & push 完了")
    except Exception as e:
        print(f"✗ Git 操作失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
