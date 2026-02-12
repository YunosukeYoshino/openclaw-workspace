# Cloud Agent

クラウドリソースの管理を担当するAIエージェント。サービス、ストレージ、使用状況を追跡します。

## 機能

- **サービス管理 (Services)**: クラウドサービスの登録、ステータス追跡、コスト管理
- **ストレージ管理 (Storage)**: ストレージリソースの追跡、使用量監視
- **使用ログ (Usage Logs)**: リソース使用量の記録と分析

## データベース構造

### テーブル: services
| カラム | 型 | 説明 |
|--------|-----|------|
| id | INTEGER | 主キー |
| name | TEXT | サービス名 |
| provider | TEXT | プロバイダー (aws/azure/gcpなど) |
| service_type | TEXT | サービスタイプ |
| status | TEXT | ステータス (active/inactive/deprecated/error) |
| region | TEXT | リージョン |
| cost_monthly | REAL | 月額コスト (USD) |
| usage_stats | TEXT | 使用統計 (JSON) |
| tags | TEXT | タグ |
| created_at | TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | 更新日時 |

### テーブル: storage
| カラム | 型 | 説明 |
|--------|-----|------|
| id | INTEGER | 主キー |
| name | TEXT | ストレージ名 |
| provider | TEXT | プロバイダー |
| type | TEXT | タイプ (s3/blob/file/database/backup) |
| size_used_gb | REAL | 使用容量 (GB) |
| size_total_gb | REAL | 総容量 (GB) |
| status | TEXT | ステータス (active/inactive/archived) |
| region | TEXT | リージョン |
| access_tier | TEXT | アクセス階層 |
| retention_days | INTEGER | 保存期間 (日数) |
| created_at | TIMESTAMP | 作成日時 |
| last_accessed | TIMESTAMP | 最終アクセス日時 |

### テーブル: usage_logs
| カラム | 型 | 説明 |
|--------|-----|------|
| id | INTEGER | 主キー |
| resource_id | INTEGER | リソースID |
| resource_type | TEXT | リソースタイプ (service/storage) |
| metric | TEXT | メトリクス名 |
| value | REAL | 値 |
| unit | TEXT | 単位 |
| timestamp | TIMESTAMP | タイムスタンプ |
| notes | TEXT | 備考 |

## Discord コマンド

### サービス管理
```
service add "Production DB" aws database 50
service list aws
service list active
service update 123 inactive
```

### ストレージ管理
```
storage add "Backup Storage" aws s3 1000
storage list aws
storage update 123 450
```

### 使用ログ
```
usage log 123 requests 100000
usage log 123 storage 50 gb
usage list 123
```

### 統計
```
stats
```

## 使用例

### サービスの追加
```
service add "App Server" aws compute 29
```

### プロバイダー別のサービス一覧
```
service list aws
```

### ストレージの追加と追跡
```
storage add "Main Bucket" aws s3 500
storage update 1 250
```

### 使用量のログ記録
```
usage log 1 requests 50000
```

### クラウド統計の確認
```
stats
```

## API 使用例

```python
from agents.cloud_agent.db import CloudDB
from agents.cloud_agent.discord import CloudDiscordHandler

# データベース初期化
db = CloudDB()

# ハンドラー作成
handler = CloudDiscordHandler(db)

# サービス追加
response = handler.process_message("service add 'Web Server' aws compute 20")
print(response)

# 使用量ログ
response = handler.process_message("usage log 1 requests 100000")
print(response)

# 統計表示
response = handler.process_message("stats")
print(response)
```

## サポートされるプロバイダー

- **AWS** - Amazon Web Services
- **Azure** - Microsoft Azure
- **GCP** - Google Cloud Platform
- **DigitalOcean**
- **Heroku**
- **Vercel**

## サービスタイプ

- **compute** - コンピューティングリソース (EC2, VM, Functions)
- **database** - データベース (RDS, PostgreSQL, MongoDB)
- **storage** - ストレージ (S3, Blob, Cloud Storage)
- **network** - ネットワーク (VPC, CDN, Load Balancer)
- **monitoring** - 監視ツール
- **other** - その他

## ストレージタイプ

- **s3** - オブジェクトストレージ (S3, GCS)
- **blob** - BLOBストレージ (Azure Blob)
- **file** - ファイルストレージ
- **database** - データベースストレージ
- **backup** - バックアップストレージ

## コスト管理

月額コストを追跡し、アクティブなサービスの合計コストを計算します。コストが増加した場合、統計コマンドでアラートが表示されます。
