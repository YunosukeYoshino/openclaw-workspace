# Cloud Agent / クラウドエージェント

An AI agent for managing cloud resources, services, storage, and usage tracking.

クラウドリソース、サービス、ストレージ、使用状況の管理を担当するAIエージェント。

## Features / 機能

- **Service Management / サービス管理**: Register and track cloud services, status, and costs / クラウドサービスの登録、ステータス追跡、コスト管理
- **Storage Management / ストレージ管理**: Track storage resources and usage / ストレージリソースの追跡、使用量監視
- **Usage Logging / 使用ログ記録**: Record and analyze resource usage / リソース使用量の記録と分析

## Database Schema / データベース構造

### Table: services (サービステーブル)
| Column | Type | Description / 説明 |
|--------|------|---------------------|
| id | INTEGER | Primary key / 主キー |
| name | TEXT | Service name / サービス名 |
| provider | TEXT | Provider (aws/azure/gcp etc.) / プロバイダー |
| service_type | TEXT | Service type / サービスタイプ |
| status | TEXT | Status (active/inactive/deprecated/error) / ステータス |
| region | TEXT | Region / リージョン |
| cost_monthly | REAL | Monthly cost (USD) / 月額コスト |
| usage_stats | TEXT | Usage statistics (JSON) / 使用統計 |
| tags | TEXT | Tags / タグ |
| created_at | TIMESTAMP | Creation time / 作成日時 |
| updated_at | TIMESTAMP | Update time / 更新日時 |

### Table: storage (ストレージテーブル)
| Column | Type | Description / 説明 |
|--------|------|---------------------|
| id | INTEGER | Primary key / 主キー |
| name | TEXT | Storage name / ストレージ名 |
| provider | TEXT | Provider / プロバイダー |
| type | TEXT | Type (s3/blob/file/database/backup) / タイプ |
| size_used_gb | REAL | Used size (GB) / 使用容量 (GB) |
| size_total_gb | REAL | Total size (GB) / 総容量 (GB) |
| status | TEXT | Status (active/inactive/archived) / ステータス |
| region | TEXT | Region / リージョン |
| access_tier | TEXT | Access tier / アクセス階層 |
| retention_days | INTEGER | Retention period (days) / 保存期間 (日数) |
| created_at | TIMESTAMP | Creation time / 作成日時 |
| last_accessed | TIMESTAMP | Last access / 最終アクセス日時 |

### Table: usage_logs (使用ログテーブル)
| Column | Type | Description / 説明 |
|--------|------|---------------------|
| id | INTEGER | Primary key / 主キー |
| resource_id | INTEGER | Resource ID / リソースID |
| resource_type | TEXT | Resource type (service/storage) / リソースタイプ |
| metric | TEXT | Metric name / メトリクス名 |
| value | REAL | Value / 値 |
| unit | TEXT | Unit / 単位 |
| timestamp | TIMESTAMP | Timestamp / タイムスタンプ |
| notes | TEXT | Notes / 備考 |

## Discord Commands / Discord コマンド

### Service Management / サービス管理
```
service add "Production DB" aws database 50
service list aws
service list active
service update 123 inactive
```

### Storage Management / ストレージ管理
```
storage add "Backup Storage" aws s3 1000
storage list aws
storage update 123 450
```

### Usage Logging / 使用ログ
```
usage log 123 requests 100000
usage log 123 storage 50 gb
usage list 123
```

### Statistics / 統計
```
stats
```

## Usage Examples / 使用例

### Adding a service / サービスの追加
```
service add "App Server" aws compute 29
```

### Listing services by provider / プロバイダー別のサービス一覧
```
service list aws
```

### Adding and tracking storage / ストレージの追加と追跡
```
storage add "Main Bucket" aws s3 500
storage update 1 250
```

### Logging usage / 使用量のログ記録
```
usage log 1 requests 50000
```

### Viewing cloud statistics / クラウド統計の確認
```
stats
```

## API Usage / API 使用例

```python
from agents.cloud_agent.db import CloudDB
from agents.cloud_agent.agent import CloudDiscordHandler

# Initialize database / データベース初期化
db = CloudDB()

# Create handler / ハンドラー作成
handler = CloudDiscordHandler(db)

# Add a service / サービス追加
response = handler.process_message("service add 'Web Server' aws compute 20")
print(response)

# Log usage / 使用量ログ
response = handler.process_message("usage log 1 requests 100000")
print(response)

# Show statistics / 統計表示
response = handler.process_message("stats")
print(response)
```

## Supported Providers / サポートされるプロバイダー

- **AWS** - Amazon Web Services
- **Azure** - Microsoft Azure
- **GCP** - Google Cloud Platform
- **DigitalOcean**
- **Heroku**
- **Vercel**

## Service Types / サービスタイプ

- **compute** - Computing resources / コンピューティングリソース (EC2, VM, Functions)
- **database** - Databases / データベース (RDS, PostgreSQL, MongoDB)
- **storage** - Storage / ストレージ (S3, Blob, Cloud Storage)
- **network** - Network / ネットワーク (VPC, CDN, Load Balancer)
- **monitoring** - Monitoring tools / 監視ツール
- **other** - Other / その他

## Storage Types / ストレージタイプ

- **s3** - Object storage / オブジェクトストレージ (S3, GCS)
- **blob** - BLOB storage / BLOBストレージ (Azure Blob)
- **file** - File storage / ファイルストレージ
- **database** - Database storage / データベースストレージ
- **backup** - Backup storage / バックアップストレージ

## Cost Management / コスト管理

Track monthly costs and calculate total cost for active services. Alerts are displayed in statistics when costs increase.

月額コストを追跡し、アクティブなサービスの合計コストを計算します。コストが増加した場合、統計コマンドでアラートが表示されます。
