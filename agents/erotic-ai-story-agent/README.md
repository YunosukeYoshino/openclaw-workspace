# えっちAIストーリーエージェント / えっちAIストーリーエージェント (EN)

AIによるえっちなストーリー・プロット生成エージェント / AIによるえっちなストーリー・プロット生成エージェント

## Overview / 概要

AIを活用したAIによるえっちなストーリー・プロット生成エージェント。

## Features / 機能

- AIによるコンテンツ生成
- 高度なスタイル変換
- クリエイティブなアシスタント機能

## Installation / インストール

```bash
pip install -r requirements.txt
```

## Usage / 使用方法

### Agent Usage / エージェントの使用

```python
from agent import EroticAiStoryAgent

agent = EroticAiStoryAgent()
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

### stories / storiesテーブル

| Column | Type | Description |\n|--------|------|-------------|\n| id | INTEGER | Primary Key |\n| name | TEXT | Name |\n| description | TEXT | Description |

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

- `!add_ai-story <title> <content>` - Add entry / エントリー追加
- `!list_ai-story [limit]` - List entries / エントリー一覧
- `!get_ai-story <id>` - Get entry / エントリー取得
- `!search_ai-story <query>` - Search entries / エントリー検索
- `!stats_ai-story` - Get statistics / 統計情報

## License / ライセンス

MIT License
