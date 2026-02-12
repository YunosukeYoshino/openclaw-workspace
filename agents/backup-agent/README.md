# Backup Agent (バックアップ管理エージェント)

Data backup, scheduling, and restore management.

## 機能 / Features

- データのバックアップ (Data backup)
- バックアップのスケジュール設定 (Backup scheduling)
- リストアの管理 (Restore management)
- 古いバックアップのクリーンアップ (Old backup cleanup)

## 使い方 / Usage

### バックアップ作成 / Create Backup
```
バックアップ作成: /path/to/data。タイプ: 完全、圧縮: gzip
backup create: /path/to/data. Type: full, Compression: gzip
```

### バックアップ一覧 / List Backups
```
一覧: 完了
list: completed
```

### リストア / Restore
```
リストア: バックアップ 1 /restore/path
restore: Backup 1 /restore/path
```

### スケジュール作成 / Create Schedule
```
スケジュール: バックアップ 毎日バックアップ。タイプ: 毎日、時間: 02:00
schedule: Backup Daily backup. Type: daily, Time: 02:00
```

### クリーンアップ / Cleanup
```
クリーンアップ: 30
cleanup: 30
```

### リストア履歴 / Restore History
```
履歴: バックアップ 1
history: Backup 1
```

### 統計 / Stats
```
統計
stats
```

## データベース / Database

SQLiteベースのデータベース (`backup.db`) を使用します。
Uses SQLite-based database (`backup.db`).

### テーブル / Tables

- `backups`: バックアップ情報 (Backup information)
- `schedules`: バックアップスケジュール (Backup schedules)
- `restores`: リストア履歴 (Restore history)

## バックアップタイプ / Backup Types

- `full`: 完全バックアップ / Full backup
- `incremental`: 増分バックアップ / Incremental backup
- `differential`: 差分バックアップ / Differential backup

## 圧縮方式 / Compression Methods

- `none`: なし / No compression
- `gzip`: Gzip圧縮 / Gzip compression
- `zip`: Zip圧縮 / Zip compression

## スケジュールタイプ / Schedule Types

- `daily`: 毎日 / Daily
- `weekly`: 毎週 / Weekly
- `monthly`: 毎月 / Monthly
- `cron`: Cron式 / Cron expression

## インストール / Installation

```bash
pip install -r requirements.txt
```

## 初期化 / Initialize

```bash
python db.py
```
