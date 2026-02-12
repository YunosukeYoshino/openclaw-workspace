# Log Agent

システムログとモニタリング管理のためのDiscordボット

A Discord bot for system logs and monitoring management

## Features / 機能

### Core Features
- **ログ記録 / Log Collection**: Capture logs from various sources with different levels
- **ログ検索 / Log Search**: Search logs by message content and metadata
- **統計 / Statistics**: View log statistics and trends
- **アラート / Alerts**: Create and monitor alerts based on log patterns
- **エクスポート / Exports**: Export logs to JSON format
- **自然言語インターフェース / Natural Language Interface**: Interact using natural language

## Installation / インストール

```bash
# Clone the repository
git clone <repository-url>
cd log-agent

# Install dependencies
pip install -r requirements.txt

# Set Discord bot token
export DISCORD_TOKEN='your-bot-token-here'

# Run the bot
python agent.py
```

## Database Schema / データベース構造

### Tables / テーブル

#### logs
ログエントリを保存 / Stores log entries

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| timestamp | TIMESTAMP | Log timestamp |
| level | TEXT | Level (DEBUG/INFO/WARNING/ERROR/CRITICAL) |
| source | TEXT | Log source name |
| message | TEXT | Log message |
| details | TEXT | JSON details |
| tags | TEXT | JSON tags |
| stack_trace | TEXT | Stack trace for errors |
| correlation_id | TEXT | Correlation ID for traceability |
| compressed | BOOLEAN | Whether data is compressed |

#### sources
ログソースを管理 / Manages log sources

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| name | TEXT | Unique source name |
| type | TEXT | Type (application/system/service/external) |
| enabled | BOOLEAN | Whether source is enabled |
| config | TEXT | JSON configuration |
| last_log | TIMESTAMP | Last log timestamp |
| created_at | TIMESTAMP | Creation time |

#### alerts
アラート定義を保存 / Stores alert definitions

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| name | TEXT | Alert name |
| condition | TEXT | Alert condition |
| level | TEXT | Trigger level (WARNING/ERROR/CRITICAL) |
| threshold | INTEGER | Threshold value |
| time_window | INTEGER | Time window in minutes |
| active | BOOLEAN | Whether alert is active |
| notification_count | INTEGER | Times triggered |
| last_triggered | TIMESTAMP | Last trigger time |
| created_at | TIMESTAMP | Creation time |

#### alert_history
アラート履歴を管理 / Tracks alert triggers

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| alert_id | INTEGER | Foreign key to alerts |
| triggered_at | TIMESTAMP | Trigger timestamp |
| matched_logs | TEXT | JSON of matched logs |
| context | TEXT | Additional context |
| acknowledged | BOOLEAN | Whether acknowledged |
| acknowledged_at | TIMESTAMP | Acknowledgment time |
| notes | TEXT | Notes on acknowledgment |

#### statistics
ログ統計を保存 / Stores aggregated statistics

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| date | TEXT | Date (YYYY-MM-DD) |
| source | TEXT | Source name |
| level | TEXT | Log level |
| count | INTEGER | Count for aggregation |
| updated_at | TIMESTAMP | Last update time |

## Usage / 使い方

### Natural Language Commands / 自然言語コマンド

```bash
# Add log / ログ追加
"ログ記録 データベース接続に失敗しました"
"error ログ記録 APIエラーが発生"
"warning ログ記録 メモリ使用率が高い"

# Show logs / ログ表示
"最新ログ"
"ログ表示"
"error ログ表示"
"warning ログ表示"

# Statistics / 統計
"ログ統計"
"統計"

# Search logs / ログ検索
"ログ検索 データベース"
"検索 エラー"
"search log connection"

# Alerts / アラート
"アラート"
"alert"
"アラート履歴"
"alert history"
"アラート作成"
"create alert"

# Sources / ソース
"ソース"
"sources"
"ログソース"

# Export / エクスポート
"ログエクスポート"
"export logs"

# Help / ヘルプ
"ヘルプ"
"使い方"
```

### Python API Usage / Python API使用例

```python
from db import (
    add_log, get_logs, get_log_stats,
    create_alert, get_alerts, export_logs_to_file, search_logs
)

# Add a log / ログ追加
log_id = add_log(
    level='ERROR',
    message='Database connection failed',
    source='application',
    details={'error_code': 500, 'endpoint': '/api/users'}
)

# Get logs / ログ取得
logs = get_logs(level='ERROR', limit=50)
error_logs = get_logs(level='ERROR', start_time='2024-01-01')

# Get statistics / 統計取得
stats = get_log_stats(days=7)
print(f"Total logs: {sum(stats.values())}")

# Search logs / ログ検索
results = search_logs('database', limit=100)

# Create alert / アラート作成
create_alert(
    name='High Error Rate',
    condition='ERROR logs > 10 in 5 minutes',
    level='ERROR',
    threshold=10,
    time_window=5
)

# Export logs / ログエクスポート
export_path = export_logs_to_file(output_path='export.json')
```

## Log Levels / ログレベル

### DEBUG
詳細なデバッグ情報 / Detailed debugging information

### INFO
一般的な情報メッセージ / General informational messages

### WARNING
警告メッセージ / Warning messages

### ERROR
エラーメッセージ / Error messages

### CRITICAL
致命的なエラー / Critical errors requiring immediate attention

## Alert Conditions / アラート条件

Alerts can be configured with:
- **Condition**: Text description of the alert condition
- **Level**: Minimum log level to trigger
- **Threshold**: Number of occurrences
- **Time Window**: Time period in minutes

Example: `ERROR logs > 10 in 5 minutes`

## Environment Variables / 環境変数

```bash
DISCORD_TOKEN=your-bot-token-here
```

## Project Structure / プロジェクト構造

```
log-agent/
├── db.py              # Database operations / データベース操作
├── agent.py           # Discord bot / Discordボット
├── requirements.txt   # Dependencies / 依存パッケージ
├── README.md          # This file / このファイル
├── log.db             # SQLite database (auto-created) / SQLiteデータベース（自動作成）
└── logs/              # Exported logs / エクスポートされたログ
```

## Dependencies / 依存パッケージ

See `requirements.txt`

## License / ライセンス

MIT License
