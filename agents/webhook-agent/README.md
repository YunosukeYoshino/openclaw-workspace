# Webhook Agent

Webhook URLの登録・管理、イベントログ記録、設定の更新・削除、履歴照会を行うエージェントです。

---

# Webhook Agent

An agent for managing webhook URL registration, event logging, configuration updates/deletions, and history queries.

## 機能 / Features

### Webhook管理 / Webhook Management

- **登録** (Add): Webhook URLの登録
- **一覧** (List): 登録済みWebhookの表示
- **詳細** (Detail): 個別Webhookの詳細情報
- **更新** (Update): Webhook設定の更新
- **削除** (Delete): Webhookの削除
- **有効/無効** (Toggle): Webhookの有効/無効切り替え

### イベントログ / Event Logging

- **記録** (Logging): Webhook送信イベントの記録
- **履歴** (History): イベント履歴の照会
- **統計** (Statistics): 送信成功率、平均送信時間等の統計
- **クリーンアップ** (Cleanup): 古いイベントの削除

### サポート形式 / Supported Formats

- Discord Webhook
- Slack Webhook
- Telegram Bot API
- Custom Webhook (Generic HTTP)
- Generic Webhook

## データベース構造 / Database Schema

### webhooks テーブル

| カラム | 型 | 説明 |
|-------|---|---|
| id | INTEGER | 主キー |
| name | TEXT | Webhook名 |
| url | TEXT | Webhook URL |
| webhook_type | TEXT | タイプ (discord/slack/telegram/custom/generic) |
| description | TEXT | 説明 |
| secret | TEXT | シークレット/トークン |
| enabled | INTEGER | 有効フラグ (1=有効, 0=無効) |
| rate_limit | INTEGER | レート制限 (回/分) |
| timeout_seconds | INTEGER | タイムアウト (秒) |
| headers | TEXT | HTTPヘッダー (JSON) |
| created_at | TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | 更新日時 |

### webhook_events テーブル

| カラム | 型 | 説明 |
|-------|---|---|
| id | INTEGER | 主キー |
| webhook_id | INTEGER | Webhook ID (外部キー) |
| event_type | TEXT | イベントタイプ |
| payload | TEXT | 送信ペイロード (JSON) |
| response_status | INTEGER | HTTPステータスコード |
| response_body | TEXT | レスポンス本文 |
| duration_ms | INTEGER | 送信時間 (ミリ秒) |
| success | INTEGER | 成功フラグ (1=成功, 0=失敗) |
| error_message | TEXT | エラーメッセージ |
| created_at | TIMESTAMP | 作成日時 |

### webhook_stats テーブル

| カラム | 型 | 説明 |
|-------|---|---|
| id | INTEGER | 主キー |
| webhook_id | INTEGER | Webhook ID (外部キー) |
| date | TEXT | 日付 (YYYY-MM-DD) |
| total_sent | INTEGER | 送信総数 |
| success_count | INTEGER | 成功数 |
| failed_count | INTEGER | 失敗数 |
| avg_duration_ms | REAL | 平均送信時間 (ミリ秒) |

## 使用方法 / Usage

### コマンド形式 / Command Format

#### Webhook追加 / Add Webhook

```
webhook: 名前, https://webhook-url, タイプ: discord, 説明: 通知用
webhook: slack通知, https://hooks.slack.com/services/xxx, タイプ: slack
フック: 通知, https://example.com/webhook
```

#### Webhook一覧 / List Webhooks

```
list_webhooks
webhook一覧
フック一覧
```

#### 有効Webhook一覧 / List Enabled Webhooks

```
active_webhooks
有効webhook
enabled_webhooks
```

#### タイプ別一覧 / List by Type

```
webhook一覧: discord
list_webhooks: slack
```

#### Webhook詳細 / Webhook Detail

```
detail: 1
詳細: 1
show: 1
```

#### Webhook更新 / Update Webhook

```
update: 1, 名前: 新しい名前
更新: 1, URL: https://new-url
update: 1, タイプ: discord, 説明: 更新後
```

#### Webhook削除 / Delete Webhook

```
delete: 1
削除: 1
remove: 1
```

#### 有効/無効切り替え / Toggle Enable/Disable

```
toggle: 1
切り替え: 1
enable: 1
disable: 1
```

#### イベント履歴 / Event History

```
history
履歴
log
履歴: 20
```

#### 特定Webhookの履歴 / Webhook-Specific History

```
history: webhook: 1
履歴: webhook: 2
```

#### 統計 / Statistics

```
stats
統計
statistics
stats: 7日
統計: 30
```

#### 接続テスト / Test Connection

```
test: 1
テスト: 1
ping: 1
test_all
```

#### 古いイベント削除 / Cleanup Old Events

```
cleanup_events
クリーンアップ: 30
cleanup: 90
```

#### サマリー / Summary

```
summary
サマリー
overview
```

### db.py API / Database API

```python
from db import *

# データベース初期化
init_db()

# Webhook追加
webhook_id = add_webhook(
    name="通知",
    url="https://discord.com/api/webhooks/xxx",
    webhook_type="discord",
    description="エラー通知",
    enabled=1,
    rate_limit=60,
    timeout_seconds=10
)

# Webhook取得
webhook = get_webhook(webhook_id)

# Webhook一覧
webhooks = list_webhooks(enabled_only=True, webhook_type="discord")

# Webhook更新
update_webhook(webhook_id, name="新しい名前", enabled=1)

# Webhook削除
delete_webhook(webhook_id)

# イベントログ記録
event_id = log_webhook_event(
    webhook_id=webhook_id,
    event_type="notification",
    payload={"message": "Hello"},
    response_status=200,
    duration_ms=150,
    success=1
)

# イベント履歴取得
events = get_webhook_events(webhook_id=webhook_id, limit=50, success_only=None)

# 統計取得
stats = get_webhook_stats(webhook_id=webhook_id, days=7)

# サマリー取得
summary = get_webhook_summary()

# 古いイベント削除
deleted = cleanup_old_events(days=30)
```

### discord.py API / Discord Integration API

```python
from discord import handle_message, parse_message

# メッセージ解析
parsed = parse_message("webhook: 通知, https://webhook-url")
# → {'action': 'add', 'name': '通知', 'url': 'https://webhook-url', ...}

# メッセージ処理
response = handle_message("webhook: 通知, https://webhook-url")
# → "✅ Webhook #1 追加完了\n名前: 通知\nURL: https://webhook-url"
```

## ファイル構成 / File Structure

```
webhook-agent/
├── db.py       # SQLiteデータベースモジュール
├── discord.py  # Discord連携モジュール
└── README.md   # このファイル
```

## 依存関係 / Dependencies

- Python 3.7+
- sqlite3 (標準ライブラリ)

## 設定 / Configuration

### レート制限 / Rate Limiting

デフォルト: 60回/分 (各Webhookごと)

### タイムアウト / Timeout

デフォルト: 10秒

### 自動タイプ検出 / Auto Type Detection

URLからWebhookタイプを自動検出:

- `discord.com` / `discordapp.com` → Discord
- `hooks.slack.com` → Slack
- `api.telegram.org` → Telegram
- その他 → Generic

## イベントタイプ例 / Event Type Examples

- `notification` - 通知送信
- `alert` - アラート
- `report` - レポート
- `backup` - バックアップ完了通知
- `error` - エラー通知
- `status` - ステータス更新

## スケジュールされたクリーンアップ / Scheduled Cleanup

定期的に古いイベントを削除することで、データベースのサイズを管理できます:

```python
# 30日以上前のイベントを削除
cleanup_old_events(days=30)
```

## セキュリティ / Security

- シークレット情報はデータベースに保存されますが、詳細表示ではマスクされます
- URLは検証されます (http:// / https:// で始まる必要があります)
- 接続テストはローカル検証のみ行い、実際のリクエストは送信しません

## 使用例 / Examples

### Discord通知の設定 / Setup Discord Notification

```
webhook: Discord通知, https://discord.com/api/webhooks/xxx/yyy, タイプ: discord, 説明: エラー通知用
```

### Slack Webhookの追加 / Add Slack Webhook

```
フック: Slack通知, https://hooks.slack.com/services/T000/B000/XXX, タイプ: slack
```

### 全Webhookの状態確認 / Check All Webhooks

```
active_webhooks
```

### 履歴確認 / Check History

```
履歴: 50
```

### 過去7日間の統計 / Last 7 Days Statistics

```
統計: 7
```

### 全体サマリー / Overall Summary

```
サマリー
```

## トラブルシューティング / Troubleshooting

### Webhookが見つからない / Webhook Not Found

- `list_webhooks` で登録済みWebhookを確認
- IDが正しいか確認

### イベントが記録されない / Events Not Logged

- Webhookが有効になっているか確認 (`active_webhooks`)
- URLが正しい形式か確認 (https://...)

### データベースエラー / Database Errors

- データベースファイルの権限を確認
- `init_db()` を実行して初期化

## 開発ノート / Development Notes

- 拡張可能なアーキテクチャ
- 新しいWebhookタイプの追加が容易
- イベントログは詳細な分析に対応
- 統計データは日付ごとに集計され、クエリが高速

## ライセンス / License

本エージェントは OpenClaw プロジェクトの一部です。

This agent is part of the OpenClaw project.
