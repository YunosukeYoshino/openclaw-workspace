# ID管理エージェント

ユーザーIDの管理・運用

## 概要

ID管理エージェントはsecurityカテゴリのエージェントです。Japanese言語に対応しています。

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
from agent import IdManagementAgent

agent = IdManagementAgent()
await agent.initialize()
result = await agent.process(data)
```

### Database

```python
from db import IdManagementAgentDB

db = IdManagementAgentDB()
record_id = db.insert_record("type", "title", "content")
record = db.get_record(record_id)
```

## 言語サポート

- Japanese

## ライセンス

MIT License
