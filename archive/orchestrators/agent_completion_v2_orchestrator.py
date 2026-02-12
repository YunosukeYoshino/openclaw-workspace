#!/usr/bin/env python3
"""
エージェント補完 V2 オーケストレーター
不足しているファイル（agent.pyまたはdiscord.py）を補完する
"""
import json
from pathlib import Path

# 進捗管理ファイル
PROGRESS_FILE = "agent_completion_v2_progress.json"

# agent.pyテンプレート
AGENT_TEMPLATE = '''#!/usr/bin/env python3
"""
{name} エージェント
{description}
"""

import sqlite3
from pathlib import Path

class {class_name}:
    def __init__(self, db_path=None):
        self.db_path = db_path or Path(__file__).parent / "{name}.db"
        self.db_path = str(self.db_path)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT,
                category TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def add_entry(self, title, content, category=None, tags=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO entries (title, content, category, tags)
            VALUES (?, ?, ?, ?)
        """, (title, content, category, tags))
        conn.commit()
        conn.close()
        return cursor.lastrowid

    def get_entries(self, category=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if category:
            cursor.execute("SELECT * FROM entries WHERE category = ? ORDER BY created_at DESC", (category,))
        else:
            cursor.execute("SELECT * FROM entries ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_entry(self, entry_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
        row = cursor.fetchone()
        conn.close()
        return row

    def update_entry(self, entry_id, title=None, content=None, category=None, tags=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        updates = []
        values = []
        if title:
            updates.append("title = ?")
            values.append(title)
        if content:
            updates.append("content = ?")
            values.append(content)
        if category:
            updates.append("category = ?")
            values.append(category)
        if tags:
            updates.append("tags = ?")
            values.append(tags)
        values.append(entry_id)
        if updates:
            cursor.execute(f"UPDATE entries SET {{', '.join(updates)}}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)
            conn.commit()
        conn.close()

    def delete_entry(self, entry_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
        conn.commit()
        conn.close()

if __name__ == "__main__":
    agent = {class_name}()
    print(f"{{name}} エージェントが初期化されました。")
'''

# discord.pyテンプレート
DISCORD_TEMPLATE = '''#!/usr/bin/env python3
"""
{name} Discord Bot
{description}
"""

import logging
import os

from discord.ext import commands
from discord import Intents

from agent import {class_name}

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Discord Bot設定
TOKEN = os.getenv('DISCORD_TOKEN')
intents = Intents.default()
intents.message_content = True

class {class_name}Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)
        self.agent = {class_name}()

    async def on_ready(self):
        logger.info(f'{{self.user.name}} has connected to Discord!')

    async def on_message(self, message):
        if message.author == self.user:
            return

        content = message.content.lower()

        if content.startswith('!'):
            await self.process_commands(message)
        else:
            await self._natural_language_command(message)

    async def _natural_language_command(self, message):
        """自然言語コマンドを解析して適切な処理を実行"""
        content = message.content.lower()

        # 追加
        if '追加' in content or 'add' in content or '登録' in content or '記録' in content:
            parts = content.split(' ', 1)
            title = parts[1].split('を')[0] if len(parts) > 1 and 'を' in parts[1] else (parts[1] if len(parts) > 1 else "無題")
            title = title.strip() if title else "無題"
            entry_content = content[content.find('を') + 1:] if 'を' in content else (parts[1] if len(parts) > 1 else content)

            self.agent.add_entry(title, entry_content)
            await message.reply(f'✅ エントリー「{{title}}」を追加しました！')

        # 一覧
        elif '一覧' in content or 'list' in content or '表示' in content:
            entries = self.agent.get_entries()
            if entries:
                msg = "📋 エントリー一覧:\\n"
                for entry in entries[:10]:
                    msg += f"- **{{entry[1]}}** ({{entry[6]}})\\n"
                if len(entries) > 10:
                    msg += f"\\n... 他 {{len(entries) - 10}} 件"
                await message.reply(msg)
            else:
                await message.reply("📭 エントリーはありません。")

        # 検索
        elif '検索' in content or 'search' in content:
            parts = content.split(' ', 1)
            category = parts[1] if len(parts) > 1 else None
            if category:
                entries = self.agent.get_entries(category)
                if entries:
                    msg = f"🔍 カテゴリ「{{category}}」の検索結果:\\n"
                    for entry in entries:
                        msg += f"- **{{entry[1]}}**: {{entry[2][:50]}}...\\n"
                    await message.reply(msg)
                else:
                    await message.reply(f"📭 カテゴリ「{{category}}」のエントリーはありません。")

        # 削除
        elif '削除' in content or 'delete' in content:
            import re
            match = re.search(r'\\d+', content)
            if match:
                entry_id = int(match.group())
                self.agent.delete_entry(entry_id)
                await message.reply(f'🗑️ エントリー #{{entry_id}} を削除しました！')
            else:
                await message.reply("❌ 削除するエントリー番号を指定してください。")

def main():
    token = os.getenv('DISCORD_TOKEN', TOKEN)
    if not token:
        logger.error("DISCORD_TOKEN が設定されていません。")
        return

    bot = {class_name}Bot()
    bot.run(token)

if __name__ == "__main__":
    main()
'''

# 不足しているエージェントのリスト
INCOMPLETE_AGENTS = {
    "agent.py": [
        "anime-tracker-agent",
        "appointment-agent",
        "baseball-news-agent",
        "baseball-player-agent",
        "baseball-schedule-agent",
        "baseball-score-agent",
        "baseball-team-agent",
        "bill-tracking-agent",
        "collection-agent",
        "content-recommendation-agent",
        "craft-agent",
        "diy-project-agent",
        "game-achievement-agent",
        "game-library-agent",
        "game-news-agent",
        "game-progress-agent",
        "game-schedule-agent",
        "game-social-agent",
        "game-stats-agent",
        "game-tips-agent",
        "goal-setting-agent",
        "hobby-event-agent",
        "home-maintenance-agent",
        "meal-planning-agent",
        "manga-agent",
        "movie-tracker-agent",
        "music-library-agent",
        "note-taking-agent",
        "novel-agent",
        "photography-agent",
        "project-management-agent",
        "streaming-service-agent",
        "task-agent",
        "time-tracking-agent",
        "vtuber-agent",
        "weather-reminder-agent",
    ],
    "discord.py": [
        "audio-summarizer",
        "bookmark-agent",
        "calendar-integration-agent",
        "clipboard-agent",
        "clothing-agent",
        "device-agent",
        "diet-agent",
        "email-agent",
        "feedback-agent",
        "focus-agent",
        "garden-agent",
        "gardening-agent",
        "household-agent",
        "household-chores-agent",
        "integration-agent",
        "news-agent",
        "notification-agent",
        "phone-agent",
        "report-agent",
        "rss-agent",
        "social-agent",
        "support-agent",
        "weather-agent",
        "workout-agent",
    ],
}

def load_progress():
    """進捗の読み込み"""
    if Path(PROGRESS_FILE).exists():
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"completed": [], "total": 0, "missing_files": {}}

def save_progress(progress):
    """進捗の保存"""
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

def to_class_name(agent_name):
    """エージェント名をクラス名に変換"""
    return "".join(word.capitalize() for word in agent_name.replace("-", " ").split())

def get_description(agent_name):
    """エージェントの説明を生成"""
    return f"{agent_name} - AIエージェント"

def create_agent_py(agent_name):
    """agent.pyを作成"""
    agent_dir = Path("agents") / agent_name
    agent_dir.mkdir(parents=True, exist_ok=True)

    class_name = to_class_name(agent_name)
    content = AGENT_TEMPLATE.format(
        name=agent_name,
        description=get_description(agent_name),
        class_name=class_name,
    )

    with open(agent_dir / "agent.py", "w", encoding="utf-8") as f:
        f.write(content)

    return True

def create_discord_py(agent_name):
    """discord.pyを作成"""
    agent_dir = Path("agents") / agent_name
    agent_dir.mkdir(parents=True, exist_ok=True)

    class_name = to_class_name(agent_name)
    content = DISCORD_TEMPLATE.format(
        name=agent_name,
        description=get_description(agent_name),
        class_name=class_name,
    )

    with open(agent_dir / "discord.py", "w", encoding="utf-8") as f:
        f.write(content)

    return True

def main():
    """メイン処理"""
    print("🚀 エージェント補完 V2 オーケストレーター開始")

    progress = load_progress()
    total_missing = sum(len(v) for v in INCOMPLETE_AGENTS.values())

    print(f"📊 不足ファイル合計: {total_missing}")
    print(f"   - agent.py: {len(INCOMPLETE_AGENTS['agent.py'])}個")
    print(f"   - discord.py: {len(INCOMPLETE_AGENTS['discord.py'])}個")

    for file_type, agents in INCOMPLETE_AGENTS.items():
        for agent_name in agents:
            key = f"{agent_name}:{file_type}"

            if key in progress["completed"]:
                continue

            print(f"📝 作成中: {agent_name}/{file_type}")

            try:
                if file_type == "agent.py":
                    create_agent_py(agent_name)
                elif file_type == "discord.py":
                    create_discord_py(agent_name)

                progress["completed"].append(key)
                save_progress(progress)

                print(f"✅ 完了: {agent_name}/{file_type}")
            except Exception as e:
                print(f"❌ エラー: {agent_name}/{file_type}: {e}")

    progress["total"] = len(progress["completed"])
    print(f"\n🎉 補完完了: {progress['total']}/{total_missing}個")
    print(f"📄 進捗ファイル: {PROGRESS_FILE}")

if __name__ == "__main__":
    main()
