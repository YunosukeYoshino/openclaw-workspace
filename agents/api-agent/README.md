# API Agent / APIエージェント

A Discord bot agent for managing API keys, sending requests, and logging API activity.

APIキーを管理し、リクエストを送信し、APIアクティビティをログ記録するためのDiscordボットエージェント。

## Features / 機能

- **API Key Management / APIキー管理** - Securely store and manage API keys
- **Request Sending / リクエスト送信** - Send HTTP requests with authentication
- **Request Logging / リクエストログ** - Log all API requests and responses
- **Statistics / 統計** - View request statistics and success rates
- **Templates / テンプレート** - Save and reuse API request templates

## Installation / インストール

```bash
pip install -r requirements.txt
```

## Requirements / 必要パッケージ

- `discord.py==2.3.2`
- `aiohttp`

## Commands / コマンド

| Command / コマンド | Description / 説明 |
|-------------------|---------------------|
| `!api` | Show help / ヘルプ表示 |
| `!api key add <name> <service> <key> [base_url]` | Add API key / APIキー追加 |
| `!api key list` | List API keys / APIキー一覧 |
| `!api key update <id> <new_key>` | Update key / キー更新 |
| `!api key remove <id>` | Remove key / キー削除 |
| `!api send <key_id> <method> <endpoint>` | Send request / リクエスト送信 |
| `!api requests [service]` | Show requests / リクエスト表示 |
| `!api stats [service]` | Show statistics / 統計表示 |
| `!api logs` | Show logs / ログ表示 |
| `!api template` | Manage templates / テンプレート管理 |

## Examples / 使用例

### Add an API key / APIキーを追加
```
!api key add openai openai sk-xxxxx https://api.openai.com/v1
```

### List API keys / APIキー一覧
```
!api key list
```

### Send a request / リクエスト送信
```
!api send 1 GET /models
```

### View statistics / 統計表示
```
!api stats openai
```

## Database Structure / データベース構造

### API Keys Table / APIキーテーブル
- `id` - Primary key / 主キー
- `name` - Key name / キー名
- `service` - Service name / サービス名
- `key_value` - API key value (encrypted) / APIキー値(暗号化)
- `key_type` - Key type (api_key, bearer, etc.) / キータイプ
- `base_url` - Base URL for requests / リクエストのベースURL
- `description` - Description / 説明
- `is_active` - Active status / アクティブ状態
- `created_at` - Creation time / 作成時刻
- `updated_at` - Last update time / 最終更新時刻

### API Requests Table / APIリクエストテーブル
- `id` - Primary key / 主キー
- `api_key_id` - Foreign key to api_keys / APIキーへの外部キー
- `service` - Service name / サービス名
- `method` - HTTP method (GET, POST, etc.) / HTTPメソッド
- `endpoint` - Request endpoint / リクエストエンドポイント
- `request_headers` - Request headers (JSON) / リクエストヘッダー
- `request_body` - Request body / リクエストボディ
- `response_status` - Response status code / レスポンスステータスコード
- `response_headers` - Response headers (JSON) / レスポンスヘッダー
- `response_body` - Response body / レスポンスボディ
- `duration_ms` - Request duration in ms / リクエスト時間(ミリ秒)
- `timestamp` - Request time / リクエスト時刻
- `success` - Success status / 成功状態

### API Templates Table / APIテンプレートテーブル
- `id` - Primary key / 主キー
- `name` - Template name / テンプレート名
- `service` - Service name / サービス名
- `method` - HTTP method / HTTPメソッド
- `endpoint` - Request endpoint / リクエストエンドポイント
- `headers` - Default headers (JSON) / デフォルトヘッダー
- `body_template` - Request body template / リクエストボディテンプレート
- `description` - Description / 説明
- `created_at` - Creation time / 作成時刻

### Request Logs Table / リクエストログテーブル
- `id` - Primary key / 主キー
- `log_type` - Log type / ログタイプ
- `message` - Log message / ログメッセージ
- `details` - Additional details / 詳細情報
- `severity` - Log severity (info, warning, error) / ログ重要度
- `timestamp` - Log time / ログ時刻

## Security Notes / セキュリティ注意点

- API keys are stored in the database. In production, consider encrypting them.
- APIキーはデータベースに保存されます。本番環境では暗号化を検討してください。
- Always use secure communication (HTTPS) for API requests.
- APIリクエストには必ず安全な通信(HTTPS)を使用してください。
- Be cautious when displaying API keys or tokens in logs.
- ログでAPIキーやトークンを表示する際は注意してください。

## Language Support / 言語サポート

This agent supports both Japanese and English (日本語と英語の両方に対応).

## License / ライセンス

MIT License
