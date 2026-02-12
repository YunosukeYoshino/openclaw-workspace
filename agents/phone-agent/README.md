# Phone Agent / 電話エージェント

An AI agent for managing call records, voicemail, and contacts.

通話記録、ボイスメール、連絡先の管理を担当するAIエージェント。

## Features / 機能

- **Call Records / 通話記録**: Track incoming, outgoing, and missed calls / 着信、発信、不在着信の追跡
- **Contact Management / 連絡先管理**: Manage phone contacts with notes and tags / メモやタグ付きの連絡先管理
- **Call Statistics / 通話統計**: Track call duration and patterns / 通話時間とパターンの追跡

## Database Schema / データベース構造

### Table: calls (通話テーブル)
| Column | Type | Description / 説明 |
|--------|------|---------------------|
| id | INTEGER | Primary key / 主キー |
| contact_name | TEXT | Contact name / 連絡先名 |
| phone_number | TEXT | Phone number / 電話番号 |
| call_type | TEXT | Call type (incoming/outgoing/missed) / 通話タイプ |
| call_time | TIMESTAMP | Call timestamp / 通話日時 |
| duration | INTEGER | Duration in seconds / 継続時間 (秒) |
| notes | TEXT | Notes / メモ |
| created_at | TIMESTAMP | Creation time / 作成日時 |
| updated_at | TIMESTAMP | Update time / 更新日時 |

### Table: contacts (連絡先テーブル)
| Column | Type | Description / 説明 |
|--------|------|---------------------|
| id | INTEGER | Primary key / 主キー |
| name | TEXT | Contact name / 連絡先名 |
| phone_number | TEXT | Phone number (unique) / 電話番号 (一意) |
| email | TEXT | Email address / メールアドレス |
| tags | TEXT | Tags / タグ |
| notes | TEXT | Notes / メモ |
| created_at | TIMESTAMP | Creation time / 作成日時 |
| updated_at | TIMESTAMP | Update time / 更新日時 |

### Table: call_tags (通話タグテーブル)
| Column | Type | Description / 説明 |
|--------|------|---------------------|
| id | INTEGER | Primary key / 主キー |
| call_id | INTEGER | Call ID (FK) / 通話ID (外部キー) |
| tag | TEXT | Tag text / タグテキスト |
| created_at | TIMESTAMP | Creation time / 作成日時 |

## Discord Commands / Discord コマンド

### Call Management / 通話管理
```
call add "John Doe" +1-555-1234 incoming 5 "Project discussion"
call list incoming
call list from John
call update 123 notes "Follow up required"
```

### Contact Management / 連絡先管理
```
contact add "Alice Smith" +1-555-5678 alice@email.com
contact list Alice
contact update 123 email new@email.com
```

### Statistics / 統計
```
stats
```

## Usage Examples / 使用例

### Logging a call / 通話の記録
```
call add "John Doe" +1-555-1234 incoming 15 "Discussed project timeline"
```

### Listing incoming calls / 着信の一覧
```
call list incoming
```

### Adding a contact / 連絡先の追加
```
contact add "Project Manager" +1-555-9999 pm@company.com
```

### Viewing statistics / 統計の表示
```
stats
```

## API Usage / API 使用例

```python
from agents.phone_agent.db import PhoneDB
from agents.phone_agent.agent import PhoneDiscordHandler

# Initialize database / データベース初期化
db = PhoneDB()

# Create handler / ハンドラー作成
handler = PhoneDiscordHandler(db)

# Log a call / 通話を記録
response = handler.process_message("call add 'John Doe' +1-555-1234 incoming 10")
print(response)

# List contacts / 連絡先一覧
response = handler.process_message("contact list")
print(response)

# Show statistics / 統計表示
response = handler.process_message("stats")
print(response)
```

## Call Types / 通話タイプ

- **incoming** - Incoming call / 着信
- **outgoing** - Outgoing call / 発信
- **missed** - Missed call / 不在着信

## Contact Fields / 連絡先フィールド

- **name** - Contact name / 連絡先名
- **phone** - Phone number / 電話番号
- **email** - Email address / メールアドレス
- **notes** - Additional notes / 追加メモ
- **tags** - Tags for categorization / 分類用タグ

## Statistics / 統計

The statistics command shows:
- Total number of calls / 総通話数
- Calls by type (incoming/outgoing/missed) / タイプ別通話数
- Total contacts / 総連絡先数
- Call duration for current month / 今月の通話時間

統計コマンドでは以下を表示します：
- 総通話数
- タイプ別通話数（着信/発信/不在着信）
- 総連絡先数
- 今月の通話時間
