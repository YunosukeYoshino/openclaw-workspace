# Social Media Agent / ソーシャルメディア統合エージェント

SNSの投稿管理、通知の集約、スケジュール投稿を行うエージェントです。
Manages social media posts, aggregates notifications, and schedules posts.

## Features / 機能

- **投稿管理 / Post Management**
  - 下書き投稿の作成
  - 投稿のステータス管理
  - 投稿の一覧表示

- **スケジュール投稿 / Scheduled Posts**
  - 未来の投稿を予約
  - 日時指定で投稿を管理

- **通知管理 / Notification Management**
  - 複数SNSの通知を集約
  - 未読通知の管理
  - 通知の既読処理

- **アカウント管理 / Account Management**
  - 連携アカウントの登録
  - アカウントの一覧表示

## Usage / 使い方

### 日本語

```
投稿: Hello World!
予定投稿: 重要なお知らせ, 時間: 明日10:00
投稿一覧
未読通知
通知一覧
既読: 1
アカウント追加: twitter, アカウント名: myaccount
```

### English

```
post: Hello World!
schedule: Important announcement, time: tomorrow 10:00
posts
unread
notifications
mark read: 1
add account: twitter, account name: myaccount
```

## Commands / コマンド

| Japanese | English | Description |
|----------|---------|-------------|
| 投稿: {content} | post: {content} | Add post |
| 予定投稿: {content}, 時間: {datetime} | schedule: {content}, time: {datetime} | Schedule post |
| 投稿一覧 | posts | List posts |
| 未読通知 | unread | List unread notifications |
| 通知一覧 | notifications | List all notifications |
| 既読: {id} | mark read: {id} | Mark as read |
| アカウント追加: {platform}, 名前: {name} | add account: {platform}, name: {name} | Add account |
| アカウント一覧 | accounts | List accounts |

## Supported Platforms / 対応プラットフォーム

- Twitter / X
- Facebook
- Instagram
- LinkedIn
- Mastodon

## Installation / インストール

```bash
pip install -r requirements.txt
```

## Database / データベース

- SQLiteを使用
- 自動的に `social.db` が作成されます

## Notes / 注意事項

- 実際のSNS API連携には別途実装が必要です
- スケジュール投稿の自動投稿機能は別途実装が必要です
- 通知は手動で追加する形式です
