# Security Agent

セキュリティ管理を担当するAIエージェント。脅威、インシデント、セキュリティ対策を管理します。

## 機能

- **脅威管理 (Threats)**: セキュリティ脅威の検知、追跡、解決管理
- **インシデント管理 (Incidents)**: セキュリティインシデントの記録とステータス追跡
- **対策管理 (Measures)**: セキュリティ対策/コントロールの管理

## データベース構造

### テーブル: threats
| カラム | 型 | 説明 |
|--------|-----|------|
| id | INTEGER | 主キー |
| type | TEXT | 脅威タイプ |
| severity | TEXT | 重大度 (low/medium/high/critical) |
| title | TEXT | タイトル |
| description | TEXT | 説明 |
| status | TEXT | ステータス (open/investigating/resolved/false_positive) |
| source | TEXT | 検知元 |
| detected_at | TIMESTAMP | 検知日時 |
| resolved_at | TIMESTAMP | 解決日時 |
| metadata | TEXT | 追加情報 (JSON) |

### テーブル: incidents
| カラム | 型 | 説明 |
|--------|-----|------|
| id | INTEGER | 主キー |
| title | TEXT | タイトル |
| description | TEXT | 説明 |
| severity | TEXT | 重大度 (low/medium/high/critical) |
| status | TEXT | ステータス (active/contained/investigating/resolved/closed) |
| affected_systems | TEXT | 影響を受けたシステム |
| created_at | TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | 更新日時 |
| resolved_at | TIMESTAMP | 解決日時 |
| impact | TEXT | 影響の詳細 |

### テーブル: measures
| カラム | 型 | 説明 |
|--------|-----|------|
| id | INTEGER | 主キー |
| name | TEXT | 名称 |
| description | TEXT | 説明 |
| type | TEXT | タイプ (preventive/detective/corrective/deterrent) |
| status | TEXT | ステータス (active/inactive/decommissioned) |
| implemented_at | TIMESTAMP | 実装日時 |
| last_tested_at | TIMESTAMP | 最終テスト日時 |
| effectiveness | TEXT | 有効性評価 |
| related_threats | TEXT | 関連脅威 |

## Discord コマンド

### 脅威管理
```
threat add phishing critical ユーザーへのフィッシングメール
threat list
threat list open high
threat resolve 123
```

### インシデント管理
```
incident add "Ransomware attack" high 顧客データへの影響
incident list active
incident update 123 contained
```

### セキュリティ対策
```
measure add preventive MFA実装 多要素認証の導入
measure list
```

### 統計
```
stats
```

## 使用例

### 脅威の追加
```
threat add sql-injection high ログインフォームでのSQLインジェクション脆弱性
```

### アクティブな高リスク脅威の一覧
```
threat list open high
```

### インシデントの記録
```
incident add "DDoS Attack" critical メインサイトへのDDoS攻撃
```

### セキュリティ統計の確認
```
stats
```

## API 使用例

```python
from agents.security_agent.db import SecurityDB
from agents.security_agent.discord import SecurityDiscordHandler

# データベース初期化
db = SecurityDB()

# ハンドラー作成
handler = SecurityDiscordHandler(db)

# メッセージ処理
response = handler.process_message("threat add malware medium 悪意のあるソフトウェア検出")
print(response)
```

## 脅威の重大度レベル

- **critical**: 即時対応が必要な重大な脅威
- **high**: 迅速な対応が必要な脅威
- **medium**: 計画的な対応が必要な脅威
- **low**: 監視で十分な脅威

## セキュリティ対策のタイプ

- **preventive**: 発生を防ぐ対策（認証、暗号化など）
- **detective**: 検知する対策（ログ、監視など）
- **corrective**: 事後対応の対策（バックアップ、復旧手順など）
- **deterrent**: 抑制する対策（ポリシー、警告など）
