# Webhook Integration

汎用的なWebhookシステムを実装して、外部サービスとの連携を行うモジュールです。

## Features / 機能

- 🪝 Webhookの登録・管理
- 📤 Webhookの送信
- 🔍 Webhook一覧の取得
- ⚙️ Webhookの有効化・無効化
- 🌐 一時的なWebhook送信（登録なし）
- 📊 全Webhook一括送信
- 💾 永続化（JSONデータベース）

## Installation / インストール

```bash
pip install requests
```

## Setup / 設定

```bash
# デフォルトでは webhooks.json に保存されます
export WEBHOOKS_DB_PATH=/path/to/webhooks.json
```

## Usage / 使用方法

### Basic Usage / 基本的な使い方

```python
from integrations.webhook import WebhookManager

# マネージャー初期化
manager = WebhookManager()

# Webhookを登録
manager.register_webhook(
    webhook_id="github",
    name="GitHub Webhook",
    url="https://api.github.com/repos/user/repo/dispatches"
)

# Webhookを送信
manager.send_webhook(
    webhook_id="github",
    data={
        "event_type": "test",
        "client_payload": {"key": "value"}
    }
)

# 全ての有効なWebhookに送信
manager.send_to_all(data={"message": "Broadcast"})

# Webhook一覧を取得
webhooks = manager.list_webhooks()
for webhook in webhooks:
    print(f"{webhook.name}: {webhook.url}")
```

### Environment Variables / 環境変数

| Variable / 変数 | Description / 説明 | Default / デフォルト |
|-----------------|---------------------|---------------------|
| `WEBHOOKS_DB_PATH` | Webhookデータベースファイルのパス | `/workspace/integrations/webhook/webhooks.json` |

### CLI Usage / CLI使用方法

```bash
# Webhook一覧を表示
python client.py --list

# Webhookを登録
python client.py --register github "GitHub Webhook" https://example.com/webhook

# Webhookを削除
python client.py --unregister github

# Webhookを有効化
python client.py --enable github

# Webhookを無効化
python client.py --disable github

# Webhookを送信
python client.py --send github --data '{"event": "test"}'

# 全ての有効なWebhookに送信
python client.py --send-all --data '{"message": "Broadcast"}'

# 一時的なWebhookを送信
python client.py --raw https://example.com/webhook --data '{"key": "value"}'
```

## API Reference / APIリファレンス

### `WebhookManager`

| Method / メソッド | Description / 説明 |
|-------------------|---------------------|
| `register_webhook(webhook_id, name, url, ...)` | Webhookを登録 |
| `unregister_webhook(webhook_id)` | Webhookを削除 |
| `get_webhook(webhook_id)` | Webhookを取得 |
| `list_webhooks(enabled_only=False)` | Webhook一覧を取得 |
| `enable_webhook(webhook_id)` | Webhookを有効化 |
| `disable_webhook(webhook_id)` | Webhookを無効化 |
| `send_webhook(webhook_id, data, ...)` | Webhookを送信 |
| `send_to_all(data, ...)` | 全ての有効なWebhookに送信 |
| `send_raw_webhook(url, data, ...)` | 一時的なWebhookを送信 |

### `Webhook`

| Field / フィールド | Type / 型 | Description / 説明 |
|-------------------|-----------|---------------------|
| `id` | str | Webhook ID |
| `name` | str | Webhook名 |
| `url` | str | Webhook URL |
| `method` | str | HTTPメソッド（デフォルト: "POST"） |
| `headers` | Dict | HTTPヘッダー |
| `enabled` | bool | 有効フラグ |
| `created_at` | str | 作成日時 |

## Examples / 例

```python
from integrations.webhook import WebhookManager

manager = WebhookManager()

# カスタムヘッダー付きで登録
manager.register_webhook(
    webhook_id="slack",
    name="Slack Notification",
    url="https://hooks.slack.com/services/...",
    headers={"Content-Type": "application/json"}
)

# GETリクエストのWebhookを登録
manager.register_webhook(
    webhook_id="example_get",
    name="Example GET",
    url="https://example.com/api/webhook",
    method="GET"
)

# GitHub Actionsをトリガー
manager.register_webhook(
    webhook_id="github_actions",
    name="GitHub Actions",
    url="https://api.github.com/repos/user/repo/dispatches",
    headers={
        "Authorization": "Bearer token",
        "Accept": "application/vnd.github.v3+json"
    }
)
manager.send_webhook(
    webhook_id="github_actions",
    data={
        "event_type": "deploy",
        "client_payload": {"environment": "production"}
    }
)

# Webhookを一時的に無効化
manager.disable_webhook("github_actions")

# 再度有効化
manager.enable_webhook("github_actions")

# 有効なWebhookのみを取得
enabled_webhooks = manager.list_webhooks(enabled_only=True)

# 一時的なWebhook送信（登録なし）
manager.send_raw_webhook(
    url="https://example.com/one-time-webhook",
    data={"event": "temporary"},
    method="POST"
)

# カスタムヘッダー付きで一時送信
manager.send_raw_webhook(
    url="https://example.com/api",
    data={"key": "value"},
    headers={"X-Custom-Header": "Custom-Value"}
)

# タイムアウト設定
manager.send_webhook(
    webhook_id="github",
    data={"event": "test"},
    timeout=60
)
```

## Response Format / レスポンス形式

Webhook送信のレスポンス:

```python
{
    "status_code": 200,        # HTTPステータスコード
    "success": True,           # 成功かどうか（2xxならTrue）
    "data": {...},             # レスポンスボディ（JSON）
    "error": "..."             # エラー発生時のみ
}
```

## Use Cases / 使用例

### 1. 通知システム
```python
manager.register_webhook(
    webhook_id="notification",
    name="Notification Service",
    url="https://api.notification.com/send"
)

manager.send_webhook("notification", {
    "title": "Alert",
    "message": "Something happened"
})
```

### 2. CI/CDトリガー
```python
manager.register_webhook(
    webhook_id="deploy",
    name="Deploy to Production",
    url="https://api.ci-cd.com/trigger"
)

manager.send_webhook("deploy", {
    "environment": "production",
    "version": "v1.0.0"
})
```

### 3. データ同期
```python
# 複数のサービスに一括送信
manager.register_webhook("service_a", "Service A", "https://api.a.com/sync")
manager.register_webhook("service_b", "Service B", "https://api.b.com/sync")
manager.register_webhook("service_c", "Service C", "https://api.c.com/sync")

manager.send_to_all({
    "event": "data_updated",
    "data": {"id": 123, "value": "new"}
})
```

## License / ライセンス

MIT
