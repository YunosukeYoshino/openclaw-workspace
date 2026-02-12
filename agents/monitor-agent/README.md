# Monitor Agent

メトリクスとアラート管理のためのDiscordボット

A Discord bot for metrics and alerts management

## Features / 機能

### Core Features
- **サービス監視 / Service Monitoring**: Monitor services (API, database, cache, queue, etc.)
- **メトリクス記録 / Metric Collection**: Record and store various metrics
- **アラート管理 / Alert Management**: Create alerts based on metric thresholds
- **ヘルスチェック / Health Checks**: Track service health status
- **インシデント管理 / Incident Management**: Track and resolve incidents
- **ダッシュボード / Dashboards**: Create monitoring dashboards
- **メトリクス集計 / Metric Aggregation**: Aggregate metrics over time windows
- **通知管理 / Notification Management**: Track alert notifications
- **統計 / Statistics**: View monitoring summary
- **自然言語インターフェース / Natural Language Interface**: Interact using natural language

## Installation / インストール

```bash
# Clone the repository
git clone <repository-url>
cd monitor-agent

# Install dependencies
pip install -r requirements.txt

# Set Discord bot token
export DISCORD_TOKEN='your-bot-token-here'

# Run the bot
python discord.py
```

## Database Schema / データベース構造

### Tables / テーブル

#### services
監視対象サービスを保存 / Stores monitored services

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| name | TEXT | Unique service name |
| type | TEXT | Type (api/database/cache/queue/worker/external/custom) |
| endpoint | TEXT | Service endpoint |
| environment | TEXT | Environment name |
| health_check_enabled | BOOLEAN | Whether health check is enabled |
| health_check_interval | INTEGER | Check interval in seconds |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Last update time |

#### metrics
メトリクスデータを保存 / Stores metric data

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| metric_name | TEXT | Metric name |
| metric_type | TEXT | Type (counter/gauge/histogram/summary) |
| value | REAL | Metric value |
| unit | TEXT | Metric unit |
| labels | TEXT | JSON labels |
| source | TEXT | Metric source |
| timestamp | TIMESTAMP | Record time |

#### alerts
アラート定義を保存 / Stores alert definitions

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| name | TEXT | Alert name |
| metric_name | TEXT | Metric to monitor |
| condition | TEXT | Alert condition |
| threshold | REAL | Alert threshold value |
| comparison_operator | TEXT | Operator (>/<>=/<=/==/!=) |
| time_window | INTEGER | Time window in seconds |
| aggregation_method | TEXT | Aggregation (avg/sum/min/max/count) |
| severity | TEXT | Severity (info/warning/error/critical) |
| enabled | BOOLEAN | Whether alert is enabled |
| notification_channels | TEXT | JSON of notification channels |
| cooldown_minutes | INTEGER | Cooldown period in minutes |
| last_triggered | TIMESTAMP | Last trigger time |
| trigger_count | INTEGER | Total trigger count |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Last update time |

#### alert_triggers
アラートトリガー履歴を保存 / Stores alert trigger history

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| alert_id | INTEGER | Foreign key to alerts |
| triggered_at | TIMESTAMP | Trigger time |
| actual_value | REAL | Actual metric value |
| threshold | REAL | Alert threshold |
| severity | TEXT | Trigger severity |
| acknowledged | BOOLEAN | Whether acknowledged |
| acknowledged_at | TIMESTAMP | Acknowledgment time |
| acknowledged_by | TEXT | User who acknowledged |
| notes | TEXT | Notes |
| resolved | BOOLEAN | Whether resolved |
| resolved_at | TIMESTAMP | Resolution time |

#### health_checks
ヘルスチェック結果を保存 / Stores health check results

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| service_id | INTEGER | Foreign key to services |
| check_type | TEXT | Type (http/tcp/database/custom) |
| endpoint | TEXT | Endpoint checked |
| status | TEXT | Status (unknown/healthy/unhealthy/degraded) |
| response_time_ms | INTEGER | Response time in ms |
| status_code | INTEGER | HTTP status code |
| error_message | TEXT | Error message |
| checked_at | TIMESTAMP | Check time |

#### metric_aggregations
集計済みメトリクスを保存 / Stores aggregated metrics

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| metric_name | TEXT | Metric name |
| aggregation_type | TEXT | Type (avg/sum/min/max/count/p50/p75/p90/p95/p99) |
| window_start | TIMESTAMP | Window start time |
| window_end | TIMESTAMP | Window end time |
| value | REAL | Aggregated value |
| labels | TEXT | JSON labels |
| calculated_at | TIMESTAMP | Calculation time |

#### incidents
インシデントを追跡 / Tracks incidents

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| title | TEXT | Incident title |
| description | TEXT | Incident description |
| severity | TEXT | Severity (minor/major/critical) |
| status | TEXT | Status (open/investigating/resolved/closed) |
| detected_at | TIMESTAMP | Detection time |
| resolved_at | TIMESTAMP | Resolution time |
| duration_minutes | INTEGER | Incident duration |
| affected_services | TEXT | JSON of affected services |
| root_cause | TEXT | Root cause analysis |
| resolution | TEXT | Resolution details |
| postmortem | TEXT | Postmortem notes |
| created_by | TEXT | Creator |
| assigned_to | TEXT | Assignee |

#### dashboards
ダッシュボードを保存 / Stores dashboards

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| name | TEXT | Dashboard name |
| description | TEXT | Dashboard description |
| layout | TEXT | JSON layout |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Last update time |

#### widgets
ダッシュボードウィジェットを保存 / Stores dashboard widgets

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| dashboard_id | INTEGER | Foreign key to dashboards |
| widget_type | TEXT | Type (line/bar/gauge/stat/table/log) |
| title | TEXT | Widget title |
| metric_name | TEXT | Associated metric |
| query | TEXT | Query string |
| config | TEXT | JSON configuration |
| position_x | INTEGER | X position |
| position_y | INTEGER | Y position |
| width | INTEGER | Widget width |
| height | INTEGER | Widget height |
| created_at | TIMESTAMP | Creation time |

## Usage / 使い方

### Natural Language Commands / 自然言語コマンド

```bash
# Services / サービス
"サービス作成 \"API Service\" api"
"create service \"Database\" database"
"サービス一覧"
"services"
"list services"

# Metrics / メトリクス
"メトリック記録 cpu_usage 75.5"
"record metric memory_usage 512"
"メトリック"
"metrics"

# Alerts / アラート
"アラート作成 \"High CPU\" threshold 80"
"create alert \"High Memory\" threshold 90"
"アラート一覧"
"alerts"
"アラート履歴"
"alert history"
"アラート承認 ID: 123"
"acknowledge alert ID: 456"

# Health Checks / ヘルスチェック
"ヘルスチェック"
"health checks"

# Incidents / インシデント
"インシデント作成 \"API Outage\""
"incident create \"Database Failure\" critical"
"インシデント一覧"
"incidents"
"インシデント解決 ID: 123"
"resolve incident ID: 456"

# Dashboards / ダッシュボード
"ダッシュボード作成 \"Main Dashboard\""
"create dashboard \"API Monitor\""
"ダッシュボード一覧"
"dashboards"

# Summary / 概要
"モニタリング概要"
"monitoring summary"
"summary"

# Help / ヘルプ
"ヘルプ"
"help"
"使い方"
```

### Python API Usage / Python API使用例

```python
from db import (
    create_service, get_services, record_metric, get_metrics,
    create_alert, get_alerts, trigger_alert, get_alert_triggers, acknowledge_trigger,
    record_health_check, get_health_checks, aggregate_metrics,
    create_incident, update_incident, get_incidents,
    create_dashboard, get_dashboards, add_widget, get_widgets,
    get_monitoring_summary
)

# Create service / サービス作成
service_id = create_service(
    name='API Service',
    service_type='api',
    endpoint='https://api.example.com',
    environment='production',
    health_check_interval=60
)

# Record metrics / メトリクス記録
record_metric('cpu_usage', 75.5, metric_type='gauge', unit='%')
record_metric('memory_usage', 512, metric_type='gauge', unit='MB')
record_metric('request_count', 1500, metric_type='counter')

# Create alert / アラート作成
alert_id = create_alert(
    name='High CPU Usage',
    metric_name='cpu_usage',
    threshold=80,
    condition='>',
    severity='warning',
    notification_channels=['slack', 'email']
)

# Trigger alert / アラートトリガー
trigger_id = trigger_alert(alert_id, actual_value=85)

# Acknowledge alert / アラート承認
acknowledge_trigger(trigger_id, acknowledged_by='admin', notes='Investigating')

# Record health check / ヘルスチェック記録
record_health_check(
    service_id=service_id,
    check_type='http',
    status='healthy',
    response_time_ms=125,
    status_code=200
)

# Get health checks / ヘルスチェック取得
checks = get_health_checks(service_id=service_id)

# Aggregate metrics / メトリクス集計
from datetime import datetime, timedelta
end_time = datetime.now()
start_time = end_time - timedelta(hours=1)
avg_cpu = aggregate_metrics('cpu_usage', 'avg', start_time, end_time)

# Create incident / インシデント作成
incident_id = create_incident(
    title='API Service Outage',
    description='API service is responding slowly',
    severity='major',
    created_by='admin'
)

# Resolve incident / インシデント解決
update_incident(
    incident_id=incident_id,
    status='resolved',
    root_cause='Database connection pool exhausted',
    resolution='Increased connection pool size'
)

# Create dashboard / ダッシュボード作成
dashboard_id = create_dashboard(
    name='Main Dashboard',
    description='Primary monitoring dashboard'
)

# Add widgets / ウィジェット追加
add_widget(
    dashboard_id=dashboard_id,
    widget_type='line',
    title='CPU Usage',
    metric_name='cpu_usage',
    position_x=0,
    position_y=0,
    width=8,
    height=3
)

# Get monitoring summary / モニタリング概要取得
summary = get_monitoring_summary()
print(f"Active incidents: {summary['active_incidents']}")
print(f"Healthy services: {summary['health']['healthy']}")
```

## Metric Types / メトリックタイプ

### Counter
Monotonically increasing value (e.g., request count)

### Gauge
Value that can go up or down (e.g., CPU usage, memory)

### Histogram
Distribution of values (e.g., request latency)

### Summary
Summary statistics with quantiles

## Alert Severity / アラート重大度

- **Info**: Informational alert
- **Warning**: Warning that should be investigated
- **Error**: Error that requires attention
- **Critical**: Critical issue requiring immediate action

## Incident Severity / インシデント重大度

- **Minor**: Low impact issue
- **Major**: Significant impact
- **Critical**: Critical system failure

## Widget Types / ウィジェットタイプ

- **Line**: Time series line chart
- **Bar**: Bar chart
- **Gauge**: Gauge meter
- **Stat**: Single value display
- **Table**: Data table
- **Log**: Log viewer

## Environment Variables / 環境変数

```bash
DISCORD_TOKEN=your-bot-token-here
```

## Project Structure / プロジェクト構造

```
monitor-agent/
├── db.py              # Database operations / データベース操作
├── discord.py         # Discord bot / Discordボット
├── requirements.txt   # Dependencies / 依存パッケージ
├── README.md          # This file / このファイル
└── monitor.db         # SQLite database (auto-created) / SQLiteデータベース（自動作成）
```

## Dependencies / 依存パッケージ

See `requirements.txt`

## License / ライセンス

MIT License
