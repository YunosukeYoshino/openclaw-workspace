# Calendar Event Agent / カレンダーイベントエージェント

## 概要 / Overview

カレンダーイベントの管理、予定の整理、リマインダーを行うエージェント。
Agent for managing calendar events, organizing schedules, and reminders.

## 機能 / Features

- 📅 **イベント管理** (Event Management)
  - イベントの追加・更新・削除
  - Add, update, and delete events
  - 日付・時間・場所の設定
  - Set date, time, and location

- 👥 **参加者管理** (Attendee Management)
  - 参加者の追加とステータス管理
  - Add attendees and manage their status
  - 招待・承認・辞退の追跡
  - Track invites, acceptances, and declines

- 🔔 **リマインダー** (Reminders)
  - イベントのリマインダー設定
  - Set event reminders
  - 複数のリマインダー設定
  - Multiple reminder options

- 🔍 **検索と表示** (Search and Display)
  - 日付範囲でのイベント検索
  - Search events by date range
  - 今後のイベント一覧
  - List upcoming events

## データベース構造 / Database Schema

```sql
events (イベント)
  - id, title, description, start_date, start_time
  - end_date, end_time, location, category
  - priority, status, reminder_sent, created_at, updated_at

event_attendees (イベント参加者)
  - id, event_id, attendee_name, status

reminders (リマインダー)
  - id, event_id, reminder_minutes, sent_at
```

## 使い方 / Usage

### Japanese / 日本語

```
追加: 会議, 日付: 2026-02-12, 時間: 10:00, 場所: 会議室A
追加: ミーティング, 日付: 明日, 時間: 14:00
更新: 1, 場所: 会議室B
削除: 1
一覧
一覧: 今日
一覧: 2026-02-12
検索: 会議
参加者: 1, 田中太郎
今後
統計
```

### English / 英語

```
add: Meeting, date: 2026-02-12, time: 10:00, location: Room A
add: Team Sync, date: tomorrow, time: 14:00
update: 1, location: Room B
delete: 1
list
list: today
list: 2026-02-12
search: meeting
attendee: 1, John Doe
upcoming
stats
```

## コマンド一覧 / Command List

| 日本語 | English | 説明 / Description |
|--------|---------|---------------------|
| 追加: ... | add: ... | イベントを追加 / Add event |
| 更新: ... | update: ... | イベントを更新 / Update event |
| 削除: ... | delete: ... | イベントを削除 / Delete event |
| 一覧 | list / events | イベント一覧を表示 / List events |
| 一覧: ... | list: ... | 指定日のイベントを表示 / List events for date |
| 検索: ... | search: ... | イベントを検索 / Search events |
| 参加者: ... | attendee: ... | 参加者を追加 / Add attendee |
| 今後 | upcoming | 今後のイベント / Upcoming events |
| 統計 | stats | 統計情報を表示 / Show statistics |

## 開発状況 / Development Status

- [x] データベース設計 / Database design
- [x] CLI実装 / CLI implementation
- [x] Discord連携 / Discord integration
- [ ] リマインダー送信機能 / Reminder sending
- [ ] カレンダーサービス連携 / Calendar service integration
- [ ] Web API化 / Web API
