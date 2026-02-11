# Support Agent (カスタマーサポートエージェント)

Customer support agent for managing inquiries, FAQ automation, and ticket tracking.

## 機能 / Features

- チケット作成と管理 (Ticket creation and management)
- FAQ検索と管理 (FAQ search and management)
- チケットの追跡とステータス更新 (Ticket tracking and status updates)
- 統計情報の表示 (Statistics display)

## 使い方 / Usage

### チケット作成 / Create Ticket
```
チケット: サービスにログインできません。カテゴリ: ログイン問題、説明: エラーコード401が表示されます
ticket: Cannot login to service. Category: Login issue, Description: Error code 401
```

### FAQ検索 / Search FAQ
```
FAQ: ログイン
faq search: login
```

### FAQ追加 / Add FAQ
```
FAQ追加: Q: パスワードを忘れた場合 A: パスワードリセット機能を使用してください、カテゴリ: アカウント
add faq: Q: Forgot password A: Use password reset, Category: Account
```

### チケット更新 / Update Ticket
```
更新: チケット 1 ステータス: 進行中
update: Ticket 1 Status: in_progress
```

### チケット一覧 / List Tickets
```
一覧: オープン
list: open
```

### 統計 / Stats
```
統計
stats
```

## データベース / Database

SQLiteベースのデータベース (`support.db`) を使用します。
Uses SQLite-based database (`support.db`).

### テーブル / Tables

- `tickets`: サポートチケット (Support tickets)
- `faqs`: よくある質問 (Frequently asked questions)
- `ticket_responses`: チケットへの返信 (Ticket responses)

## インストール / Installation

```bash
pip install -r requirements.txt
```

## 初期化 / Initialize

```bash
python db.py
```
