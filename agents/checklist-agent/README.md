# Checklist Agent / チェックリストエージェント

## 概要 / Overview

チェックリストの作成、項目の管理、進捗追跡を行うエージェント。
Agent for creating checklists, managing items, and tracking progress.

## 機能 / Features

- 📋 **チェックリスト作成** (Checklist Creation)
  - チェックリストの作成と管理
  - Create and manage checklists
  - カテゴリによる整理
  - Organize by category

- ✅ **項目管理** (Item Management)
  - 項目の追加・削除
  - Add and remove items
  - 完了状態の切り替え
  - Toggle completion status

- 📊 **進捗追跡** (Progress Tracking)
  - 進捗率の計算と表示
  - Calculate and display progress percentage
  - 完了項目のカウント
  - Count completed items

- 📝 **テンプレート** (Templates)
  - テンプレートの作成と管理
  - Create and manage templates
  - テンプレートからのチェックリスト作成
  - Create checklists from templates

## データベース構造 / Database Schema

```sql
checklists (チェックリスト)
  - id, title, description, category, created_at, updated_at

checklist_items (チェックリスト項目)
  - id, checklist_id, text, completed, position

checklist_templates (テンプレート)
  - id, name, description, created_at

template_items (テンプレート項目)
  - id, template_id, text, position
```

## 使い方 / Usage

### Japanese / 日本語

```
作成: 買い物リスト, カテゴリ: ショッピング
項目: 1, 牛乳
チェック: 1
項目削除: 2
削除: 1
一覧
表示: 1
進捗: 1
テンプレート: 作成: 旅行準備
テンプレート: 項目: 1, パスポート
テンプレート: 使用: 1, 夏休み旅行
統計
```

### English / 英語

```
create: Shopping List, category: Shopping
item: 1, Milk
check: 1
delete item: 2
delete: 1
list
view: 1
progress: 1
template create: Travel Prep
template item: 1, Passport
template use: 1, Summer Trip
stats
```

## コマンド一覧 / Command List

| 日本語 | English | 説明 / Description |
|--------|---------|---------------------|
| 作成: ... | create: ... | チェックリスト作成 / Create checklist |
| 項目: ... | item: ... | 項目を追加 / Add item |
| チェック: ... | check: ... | 項目の完了を切り替え / Toggle item |
| 項目削除: ... | delete item: ... | 項目を削除 / Delete item |
| 削除: ... | delete: ... | チェックリストを削除 / Delete checklist |
| 一覧 | list | チェックリスト一覧 / List checklists |
| 表示: ... | view: ... | チェックリストを表示 / View checklist |
| 進捗: ... | progress: ... | 進捗を表示 / Show progress |
| テンプレート: 作成: ... | template create: ... | テンプレート作成 / Create template |
| テンプレート: 項目: ... | template item: ... | テンプレート項目追加 / Add template item |
| テンプレート: 使用: ... | template use: ... | テンプレートから作成 / Create from template |
| 統計 | stats | 統計情報を表示 / Show statistics |

## 開発状況 / Development Status

- [x] データベース設計 / Database design
- [x] CLI実装 / CLI implementation
- [x] Discord連携 / Discord integration
- [ ] テンプレート共有機能 / Template sharing
- [ ] Web UI追加 / Web UI
- [ ] 定期チェックリスト / Recurring checklists
