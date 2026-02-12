# content-recommendation-agent

## 概要 (Overview)

映画・アニメ・音楽などのレコメンデーション

Movie, anime, music, and other content recommendations

## 機能 (Features)

- コンテンツの記録と追跡 (Record and track content)
- 評価・タグ付け機能 (Rating and tagging)
- カテゴリ分類 (Category classification)
- 統計情報の表示 (Statistics display)
- Discord Botによる自然言語操作 (Natural language control via Discord Bot)

## インストール (Installation)

```bash
pip install -r requirements.txt
```

## 環境変数 (Environment Variables)

- `DISCORD_TOKEN` - Discord Botトークン (Discord Bot token)

## 使用方法 (Usage)

### データベース操作 (Database Operations)

```python
from db import Database

db = Database()

# 追加 (Add)
record_id = db.add_record(
    title="Example Title",
    description="Description",
    category="category",
    rating=8,
    status="watching"
)

# 一覧 (List)
records = db.list_records()

# 統計 (Statistics)
stats = db.get_statistics()
```

### Discord Bot (Discord Bot)

```bash
python discord.py
```

**コマンド**:
- `!add <タイトル>` - 追加 (Add)
- `!list` - 一覧 (List)
- `!update <ID> [status|rating]` - 更新 (Update)
- `!delete <ID>` - 削除 (Delete)
- `!stats` - 統計 (Statistics)

**自然言語**:
- 「○○を追加」「○○を見た」 - 記録追加 (Add record)
- 「一覧」「何見てる？」 - 一覧表示 (Show list)

## データベース構造 (Database Schema)

### records テーブル
- `id` - ID
- `title` - タイトル
- `description` - 説明
- `category` - カテゴリ
- `rating` - 評価
- `status` - ステータス
- `start_date` - 開始日
- `end_date` - 終了日
- `notes` - メモ
- `created_at` - 作成日時
- `updated_at` - 更新日時

## ライセンス (License)

MIT
