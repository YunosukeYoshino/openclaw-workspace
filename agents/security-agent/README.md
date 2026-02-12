# Security Agent / セキュリティエージェント

An AI agent for managing security threats, incidents, and countermeasures.

セキュリティ脅威、インシデント、対策を管理するAIエージェント。

## Features / 機能

- **Threat Management / 脅威管理**: Track and resolve security threats / セキュリティ脅威の追跡と解決
- **Incident Management / インシデント管理**: Log and manage security incidents / セキュリティインシデントの記録と管理
- **Security Measures / セキュリティ対策**: Track preventive and corrective controls / 予防的・是正的コントロールの追跡

## Database Schema / データベース構造

### Table: threats (脅威テーブル)
| Column | Type | Description / 説明 |
|--------|------|---------------------|
| id | INTEGER | Primary key / 主キー |
| type | TEXT | Threat type / 脅威タイプ |
| severity | TEXT | Severity (low/medium/high/critical) / 重大度 |
| title | TEXT | Threat title / 脅威タイトル |
| description | TEXT | Description / 説明 |
| status | TEXT | Status (open/investigating/resolved/false_positive) / ステータス |
| source | TEXT | Source / 発生源 |
| detected_at | TIMESTAMP | Detection time / 検知日時 |
| resolved_at | TIMESTAMP | Resolution time / 解決日時 |
| metadata | TEXT | Additional data (JSON) / 追加データ |

### Table: incidents (インシデントテーブル)
| Column | Type | Description / 説明 |
|--------|------|---------------------|
| id | INTEGER | Primary key / 主キー |
| title | TEXT | Incident title / インシデントタイトル |
| description | TEXT | Description / 説明 |
| severity | TEXT | Severity (low/medium/high/critical) / 重大度 |
| status | TEXT | Status (active/contained/investigating/resolved/closed) / ステータス |
| affected_systems | TEXT | Affected systems / 影響システム |
| created_at | TIMESTAMP | Creation time / 作成日時 |
| updated_at | TIMESTAMP | Update time / 更新日時 |
| resolved_at | TIMESTAMP | Resolution time / 解決日時 |
| impact | TEXT | Impact assessment / 影響評価 |

### Table: measures (対策テーブル)
| Column | Type | Description / 説明 |
|--------|------|---------------------|
| id | INTEGER | Primary key / 主キー |
| name | TEXT | Measure name / 対策名 |
| description | TEXT | Description / 説明 |
| type | TEXT | Type (preventive/detective/corrective/deterrent) / タイプ |
| status | TEXT | Status (active/inactive/decommissioned) / ステータス |
| implemented_at | TIMESTAMP | Implementation time / 実装日時 |
| last_tested_at | TIMESTAMP | Last test date / 最終テスト日 |
| effectiveness | TEXT | Effectiveness rating / 有効性評価 |
| related_threats | TEXT | Related threats / 関連脅威 |

## Discord Commands / Discord コマンド

### Threat Management / 脅威管理
```
threat add <type> <severity> [description]
threat add malware critical "Ransomware detected on server"

threat list [status] [severity]
threat list open high

threat resolve <id>
threat resolve 123
```

### Incident Management / インシデント管理
```
incident add <title> <severity> [description]
incident add "Data breach" high "Customer data exposed"

incident list [status]
incident list active

incident update <id> <status>
incident update 456 resolved
```

### Security Measures / セキュリティ対策
```
measure add <type> <name> [description]
measure add preventive "2FA enforcement"

measure list
```

### Statistics / 統計
```
stats
```

## Usage Examples / 使用例

### Adding a threat / 脅威の追加
```
threat add malware critical "Ransomware detected on production server"
```

### Listing open threats / 未解決脅威の一覧
```
threat list open high
```

### Creating an incident / インシデントの作成
```
incident add "Unauthorized access" high "Employee credentials compromised"
```

### Adding a security measure / セキュリティ対策の追加
```
measure add preventive "Multi-factor authentication"
```

### Viewing statistics / 統計の表示
```
stats
```

## API Usage / API 使用例

```python
from agents.security_agent.db import SecurityDB
from agents.security_agent.agent import SecurityDiscordHandler

# Initialize database / データベース初期化
db = SecurityDB()

# Create handler / ハンドラー作成
handler = SecurityDiscordHandler(db)

# Add a threat / 脅威追加
response = handler.process_message("threat add malware critical Ransomware")
print(response)

# List threats / 脅威一覧
response = handler.process_message("threat list open")
print(response)

# Show statistics / 統計表示
response = handler.process_message("stats")
print(response)
```

## Severity Levels / 重大度レベル

- **critical** - Critical impact / クリティカルな影響
- **high** - High impact / 高い影響
- **medium** - Medium impact / 中程度の影響
- **low** - Low impact / 低い影響

## Incident Status / インシデントステータス

- **active** - Active incident / アクティブなインシデント
- **contained** - Contained / 封じ込め済み
- **investigating** - Under investigation / 調査中
- **resolved** - Resolved / 解決済み
- **closed** - Closed / クローズ

## Measure Types / 対策タイプ

- **preventive** - Preventive controls / 予防的コントロール
- **detective** - Detective controls / 検知的コントロール
- **corrective** - Corrective controls / 是正的コントロール
- **deterrent** - Deterrent controls / 抑止的コントロール
