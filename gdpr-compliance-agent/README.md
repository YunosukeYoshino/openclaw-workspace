# gdpr-compliance-agent

GDPRコンプライアンスエージェント。GDPR準拠の管理・監査。

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
from agent import GdprComplianceAgent

agent = GdprComplianceAgent()

# エントリー追加
entry_id = agent.add_entry(
    title="タイトル",
    content="コンテンツ",
    metadata={"key": "value"}
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
