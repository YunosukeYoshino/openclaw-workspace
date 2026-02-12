# Report Agent

レポート、分析、エクスポート管理のためのDiscordボット

A Discord bot for reports, analytics, and exports management

## Features / 機能

### Core Features
- **レポート作成 / Report Creation**: Create various types of reports (summary, analytics, trend, comparison, custom)
- **アナリティクス / Analytics**: Track and store metrics data with timestamps
- **エクスポート / Exports**: Export reports to JSON or CSV format
- **テンプレート / Templates**: Create and reuse report templates
- **自然言語インターフェース / Natural Language Interface**: Interact using natural language

## Installation / インストール

```bash
# Clone the repository
git clone <repository-url>
cd report-agent

# Install dependencies
pip install -r requirements.txt

# Set Discord bot token
export DISCORD_TOKEN='your-bot-token-here'

# Run the bot
python agent.py
```

## Database Schema / データベース構造

### Tables / テーブル

#### reports
レポートのメタデータを管理 / Stores report metadata

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| title | TEXT | Report title |
| description | TEXT | Report description |
| report_type | TEXT | Type (summary/analytics/trend/comparison/custom) |
| source | TEXT | Data source |
| status | TEXT | Status (draft/generating/ready/scheduled) |
| data | TEXT | JSON configuration |
| format | TEXT | Output format (json/csv/pdf/html) |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Last update time |
| scheduled_at | TIMESTAMP | Scheduled time |

#### analytics
メトリクスデータを保存 / Stores metric data points

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| report_id | INTEGER | Foreign key to reports |
| metric_name | TEXT | Metric name |
| metric_value | REAL | Metric value |
| metric_unit | TEXT | Unit of measurement |
| timestamp | TIMESTAMP | Data point timestamp |
| category | TEXT | Metric category |
| tags | TEXT | JSON tags |

#### exports
エクスポート履歴を管理 / Tracks export history

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| report_id | INTEGER | Foreign key to reports |
| format | TEXT | Export format |
| file_path | TEXT | Exported file path |
| status | TEXT | Status (pending/processing/completed/failed) |
| exported_at | TIMESTAMP | Export time |
| file_size | INTEGER | File size in bytes |
| error_message | TEXT | Error message if failed |
| created_at | TIMESTAMP | Creation time |

#### templates
レポートテンプレートを保存 / Stores report templates

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| name | TEXT | Unique template name |
| description | TEXT | Template description |
| template_type | TEXT | Template type |
| config | TEXT | JSON configuration |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Last update time |

## Usage / 使い方

### Natural Language Commands / 自然言語コマンド

```bash
# Create report / レポート作成
"レポート作成"
"分析レポート作成"
"トレンドレポート作成"
"比較レポート作成"

# Add analytics data / アナリティクスデータ追加
"データ追加 sales 12345"
"アナリティクス users 1000"
"記録 revenue 50000"

# Show reports / レポート表示
"レポート表示"
"最新のレポートを見て"

# Show analytics / アナリティクス表示
"アナリティクス"
"分析を見て"

# Export reports / レポートエクスポート
"csvエクスポート"
"jsonエクスポート"

# Export history / エクスポート履歴
"エクスポート履歴"
"エクスポート一覧"

# Template / テンプレート
"テンプレート作成"
"デフォルトテンプレート"

# Help / ヘルプ
"ヘルプ"
"使い方"
```

### Python API Usage / Python API使用例

```python
from db import (
    create_report, get_report, list_reports,
    add_analytics, get_analytics, export_report
)

# Create a report / レポート作成
report_id = create_report(
    title="Sales Report",
    report_type="analytics",
    description="Monthly sales analysis"
)

# Add analytics data / アナリティクスデータ追加
add_analytics(report_id, "sales", 12345, unit="USD", category="revenue")
add_analytics(report_id, "users", 1000, unit="count", category="customers")

# Get analytics / アナリティクス取得
analytics = get_analytics(report_id)

# Export report / レポートエクスポート
file_path = export_report(report_id, format="csv")
print(f"Exported to: {file_path}")
```

## Report Types / レポートタイプ

### Type: summary
データのサマリー / Data summary

### Type: analytics
分析レポート / Analytical report with detailed metrics

### Type: trend
トレンド分析 / Trend analysis over time

### Type: comparison
比較レポート / Comparison between datasets

### Type: custom
カスタムレポート / Custom configurable report

## Export Formats / エクスポート形式

### JSON
構造化データ / Structured data with full report and analytics

### CSV
表形式データ / Tabular format suitable for spreadsheet analysis

## Environment Variables / 環境変数

```bash
DISCORD_TOKEN=your-bot-token-here
```

## Project Structure / プロジェクト構造

```
report-agent/
├── db.py              # Database operations / データベース操作
├── agent.py           # Discord bot / Discordボット
├── requirements.txt   # Dependencies / 依存パッケージ
├── README.md          # This file / このファイル
├── report.db          # SQLite database (auto-created) / SQLiteデータベース（自動作成）
└── exports/           # Exported files / エクスポートファイル
```

## Dependencies / 依存パッケージ

See `requirements.txt`

## License / ライセンス

MIT License
