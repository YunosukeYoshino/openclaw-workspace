# Email Agent / メール管理エージェント

未読メールの確認、重要メールの通知、自動返信設定を行うエージェントです。
Manages unread emails, notifies about important emails, and configures auto-replies.

## Features / 機能

- **メール管理 / Email Management**
  - メールの追加・記録
  - 未読メールの管理
  - 既読ステータスの管理

- **重要メール管理 / Important Email Management**
  - 重要メールのマーキング
  - 重要な未読メールの通知

- **連絡先管理 / Contact Management**
  - 連絡先の登録
  - 重要連絡先の管理

- **自動返信 / Auto Reply**
  - 自動返信ルールの設定
  - キーワードに基づく自動返信

## Usage / 使い方

### 日本語

```
メール: from@example.com, 件名: Hello, 重要
未読メール
重要メール
既読: 1
重要: 2
連絡先追加: test@example.com, 名前: John
連絡先
自動返信: オフィス不在, トリガー: vacation, 返信: 休暇中です
```

### English

```
email: from@example.com, subject: Hello, important
unread
important
mark read: 1
mark important: 2
add contact: test@example.com, name: John
contacts
auto reply: Out of office, trigger: vacation, message: I'm on vacation
```

## Commands / コマンド

| Japanese | English | Description |
|----------|---------|-------------|
| メール: {email}, 件名: {subject} | email: {email}, subject: {subject} | Add email |
| 未読メール | unread | List unread emails |
| 重要メール | important | List important emails |
| 既読: {id} | mark read: {id} | Mark as read |
| 重要: {id} | mark important: {id} | Mark as important |
| 連絡先追加: {email}, 名前: {name} | add contact: {email}, name: {name} | Add contact |
| 連絡先 | contacts | List contacts |
| 自動返信: {rule}, トリガー: {keyword}, 返信: {message} | auto reply: {rule}, trigger: {keyword}, message: {message} | Add auto-reply rule |
| 自動返信 | auto replies | List auto-reply rules |

## Installation / インストール

```bash
pip install -r requirements.txt
```

## Database / データベース

- SQLiteを使用
- 自動的に `email.db` が作成されます

## Notes / 注意事項

- 実際のメールサーバー連携には別途実装が必要です
- 自動返信はルールベースで動作します
- メールは手動で追加する形式です
