# Message Agent

メッセージとコミュニケーションの管理を担当するAIエージェント。テキストメッセージ、通信ログ、コンタクト情報を追跡します。

## 機能

- **メッセージ管理 (Messages)**: 送受信メッセージの記録、検索、ステータス追跡
- **通信ログ (Communication Logs)**: 通話、会議、チャットセッションの記録
- **コンタクト管理 (Contacts)**: 連絡先の管理と追跡

## データベース構造

### テーブル: messages
| カラム | 型 | 説明 |
|--------|-----|------|
| id | INTEGER | 主キー |
| sender | TEXT | 送信者 |
| recipient | TEXT | 受信者 |
| content | TEXT | メッセージ内容 |
| platform | TEXT | プラットフォーム (discord/slack/emailなど) |
| message_type | TEXT | メッセージタイプ (text/image/video/file/audio) |
| status | TEXT | ステータス (sent/delivered/read/failed) |
| thread_id | TEXT | スレッドID |
| tags | TEXT | タグ |
| metadata | TEXT | 追加情報 (JSON) |
| timestamp | TIMESTAMP | 送信日時 |

### テーブル: communication_logs
| カラム | 型 | 説明 |
|--------|-----|------|
| id | INTEGER | 主キー |
| participants | TEXT | 参加者 |
| platform | TEXT | プラットフォーム |
| communication_type | TEXT | タイプ (chat/call/video/email/meeting) |
| title | TEXT | タイトル |
| summary | TEXT | サマリー |
| start_time | TIMESTAMP | 開始日時 |
| end_time | TIMESTAMP | 終了日時 |
| duration_minutes | INTEGER | 継続時間 (分) |
| message_count | INTEGER | メッセージ数 |
| tags | TEXT | タグ |

### テーブル: contacts
| カラム | 型 | 説明 |
|--------|-----|------|
| id | INTEGER | 主キー |
| name | TEXT | 名前 |
| identifier | TEXT | 識別子 (ユーザーID、メールアドレスなど) |
| platform | TEXT | プラットフォーム |
| relationship | TEXT | 関係 (friend/colleague/clientなど) |
| notes | TEXT | メモ |
| last_contacted | TIMESTAMP | 最終連絡日時 |
| created_at | TIMESTAMP | 作成日時 |

## Discord コマンド

### メッセージ管理
```
message add Alice Bob "Hello, how are you?" discord
message list from Alice
message list to Bob
message search important
```

### コンタクト管理
```
contact add Alice alice#1234 discord
contact list discord
```

### 通信ログ
```
communication start Alice, Bob, Carol discord
communication end 123 "Discussed project timeline"
communication list meeting
```

### 統計
```
stats
```

## 使用例

### メッセージの記録
```
message add John Sarah "Please review the document by Friday" email
```

### 送信者からのメッセージ一覧
```
message list from John
```

### メッセージの検索
```
message search urgent
```

### コンタクトの追加
```
contact add "Project Manager" pm@company.com email
```

### 会議の記録
```
communication start "Team Meeting - Project X" zoom
communication end 1 "Reviewed progress and assigned tasks"
```

### 統計の確認
```
stats
```

## API 使用例

```python
from agents.message_agent.db import MessageDB
from agents.message_agent.discord import MessageDiscordHandler

# データベース初期化
db = MessageDB()

# ハンドラー作成
handler = MessageDiscordHandler(db)

# メッセージ追加
response = handler.process_message("message add Alice Bob 'Hi there!' discord")
print(response)

# メッセージ検索
response = handler.process_message("message search important")
print(response)

# コンタクト追加
response = handler.process_message("contact add John john#9999 discord")
print(response)

# 統計表示
response = handler.process_message("stats")
print(response)
```

## サポートされるプラットフォーム

- **Discord** - ディスコード
- **Slack** - スラック
- **Email** - メール
- **Telegram** - テレグラム
- **WhatsApp** - ワッツアップ
- **Line** - ライン

## 通信タイプ

- **chat** - チャット
- **call** - 音声通話
- **video** - ビデオ通話
- **email** - メールスレッド
- **meeting** - 会議

## メッセージステータス

- **sent** - 送信済み
- **delivered** - 配信済み
- **read** - 既読
- **failed** - 送信失敗

## 検索機能

メッセージ内容をキーワードで検索できます。部分一致で検索されるため、関連するメッセージを見つけやすいです。

例:
```
message search project
message search urgent
message search "meeting notes"
```

## 通信ログ

通話や会議の記録を行い、サマリーと継続時間を追跡します。チームミーティング、顧客コール、サポート対応などの履歴管理に便利です。
