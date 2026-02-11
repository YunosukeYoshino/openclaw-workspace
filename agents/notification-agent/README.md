# Notification Agent (通知管理エージェント)

Aggregate, manage, and filter notifications.

## 機能 / Features

- 通知の集約・管理 (Notification aggregation and management)
- 通知のスケジュール設定 (Notification scheduling)
- 重要度のフィルタリング (Priority filtering)
- ルールベースの自動処理 (Rule-based automated processing)

## 使い方 / Usage

### 通知追加 / Add Notification
```
通知: システムメンテナンス予定。タイプ: 情報、優先: 高、予定: 明日 10:00
notification: System maintenance scheduled. Type: info, Priority: high, Scheduled: tomorrow 10:00
```

### 通知一覧 / List Notifications
```
一覧: 未読、緊急
list: unread, urgent
```

### 既読にする / Mark as Read
```
既読: 通知 1
read: Notification 1
```

### 全て既読 / Mark All Read
```
既読
mark read
```

### スケジュール作成 / Create Schedule
```
スケジュール: 通知 毎日朝のリマインダー。タイプ: 毎日、値: 09:00、テンプレート: おはようございます
schedule: Notification Daily morning reminder. Type: daily, Value: 09:00, Template: Good morning
```

### ルール作成 / Create Rule
```
ルール: エラー通知を緊急にする。条件: タイプ、値: error、アクション: 昇格
rule: Promote error notifications. Condition: type, Value: error, Action: promote
```

### 統計 / Stats
```
統計
stats
```

## データベース / Database

SQLiteベースのデータベース (`notification.db`) を使用します。
Uses SQLite-based database (`notification.db`).

### テーブル / Tables

- `notifications`: 通知 (Notifications)
- `schedules`: スケジュール (Schedules)
- `rules`: ルール (Rules)

## 通知タイプ / Notification Types

- `info`: 情報 / Info
- `warning`: 警告 / Warning
- `error`: エラー / Error
- `success`: 成功 / Success
- `reminder`: リマインダー / Reminder

## 優先度 / Priority Levels

- `low`: 低 / Low
- `normal`: 通常 / Normal
- `high`: 高 / High
- `urgent`: 緊急 / Urgent

## インストール / Installation

```bash
pip install -r requirements.txt
```

## 初期化 / Initialize

```bash
python db.py
```
