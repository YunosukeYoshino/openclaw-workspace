# Software Agent 77

Discordベースのソフトウェアエージェント。SQLiteデータベースと自然言語解析によるメッセージ処理を提供します。

## 特徴

- 🗣️ **自然言語処理**: メッセージを自動的に解析して応答
- 🌏 **多言語対応**: 日本語と英語をサポート
- 📊 **タスク管理**: タスクの追加・追跡・完了
- 💾 **SQLiteデータベース**: 会話履歴・コンテキスト・知識ベースを永続化
- 🤖 **AI応答**: OpenAI GPTによる自然な応答生成

## ファイル構成

```
software-agent-77/
├── db.py          # データベース管理モジュール
├── discord.py     # Discord Botと自然言語処理モジュール
├── requirements.txt
└── README.md
```

## インストール

### 1. 依存パッケージのインストール

```bash
cd software-agent-77
pip install -r requirements.txt
```

### 2. 環境変数の設定

```bash
export DISCORD_TOKEN="your_discord_bot_token"
export OPENAI_API_KEY="your_openai_api_key"
```

Discord Bot Tokenの取得:
1. [Discord Developer Portal](https://discord.com/developers/applications) にアクセス
2. 新しいアプリケーションを作成
3. BotタブでBotを作成し、トークンをコピー

OpenAI API Keyの取得:
1. [OpenAI Platform](https://platform.openai.com/) にサインアップ
2. API Keysで新しいキーを作成

## 使い方

### Botの起動

```bash
python discord.py
```

### コマンド

- `/help` または `!help` - ヘルプを表示
- `/stats` または `!stats` - 統計情報を表示
- `/tasks` または `!tasks` - 未完了タスクの一覧
- `/lang [ja|en]` または `!lang [ja|en]` - 言語の切り替え
- `/reset` または `!reset` - 会話コンテキストのリセット

### 自然言語処理

コマンドを使用せず、自然な文章で話しかけてください。

**例（日本語）:**
- "明日のタスクを追加して"
- "今日はいい天気だね"
- "質問があります"

**例（英語）:**
- "Add a task for tomorrow"
- "Nice weather today"
- "I have a question"

Botは自動的に言語を検出し、適切に応答します。

## データベース構造

### テーブル

#### users
ユーザー情報を管理
- `id`, `discord_id`, `username`, `language`, `created_at`, `updated_at`

#### messages
メッセージ履歴を保存
- `id`, `discord_id`, `channel_id`, `content`, `language`, `intent`, `metadata`, `created_at`

#### contexts
会話コンテキストを管理
- `id`, `discord_id`, `channel_id`, `context_data`, `created_at`, `updated_at`

#### knowledge
知識ベース
- `id`, `category`, `question`, `answer`, `language`, `keywords`, `usage_count`, `created_at`, `updated_at`

#### tasks
タスク管理
- `id`, `discord_id`, `title`, `description`, `status`, `priority`, `due_date`, `created_at`, `updated_at`

## API リファレンス

### db.py

```python
from db import get_database

db = get_database()

# ユーザー管理
db.add_or_update_user(discord_id, username, language='ja')
user = db.get_user(discord_id)

# メッセージ管理
db.save_message(discord_id, channel_id, content, language, intent, metadata)
messages = db.get_recent_messages(discord_id, channel_id, limit=10)

# コンテキスト管理
db.save_context(discord_id, channel_id, context_data)
context = db.get_context(discord_id, channel_id)

# 知識ベース
db.add_knowledge(category, question, answer, language='ja', keywords=[])
knowledge = db.search_knowledge(query, language='ja')

# タスク管理
db.add_task(discord_id, title, description, priority, due_date)
tasks = db.get_tasks(discord_id, status='pending')
db.update_task_status(task_id, 'completed')

# 統計情報
stats = db.get_stats()
```

### discord.py

`SoftwareAgent77` クラスを拡張してカスタム機能を追加できます。

```python
from discord.ext import commands

class MyAgent(SoftwareAgent77):
    @commands.command(name='mycommand')
    async def my_command(self, ctx):
        await ctx.send("Custom command!")
```

## 意図分類 (Intent Classification)

Botは以下の意図を検出します:

- `question`: 質問
- `task`: タスクの追加・管理
- `greeting`: 挨拶
- `casual`: 世間話
- `command`: コマンド実行
- `information`: 情報提供の依頼

## ライセンス

MIT License
