# ブックマーク管理エージェント
# Bookmark Management Agent

AIエージェント100個のうちの1つ！ / One of the 100 AI agents!

## 概要 / Overview

ブックマークの保存・整理・タグ付け・検索・共有を簡単にできるエージェント。
An agent for easy bookmark saving, organizing, tagging, searching, and sharing.

## 機能 / Features

- 🔖 ブックマーク追加（URL、タイトル、説明、カテゴリ、タグ） / Add bookmarks (URL, title, description, category, tags)
- 📋 ブックマーク一覧（最新順） / List bookmarks (newest first)
- 🔍 キーワード検索 / Keyword search
- 🏷️ タグ検索 / Tag search
- 📁 カテゴリ管理 / Category management
- 🔗 共有リンク作成 / Create share links
- 📊 統計情報 / Statistics

## データベース構造 / Database Structure

```
bookmarks (ブックマーク)
  - id, url, title, description, favicon, category_id,
    shared_key, view_count, created_at, updated_at

categories (カテゴリ)
  - id, name, color, created_at

tags (タグ)
  - id, name, created_at

bookmark_tags (ブックマーク・タグ紐付け)
  - bookmark_id, tag_id
```

## 使い方 / Usage

### Discordから使う / Using via Discord

```
# ブックマーク追加 / Add bookmark
ブックマーク: https://example.com, タイトル:Example Site, カテゴリ:Work, タグ:tool, web
bookmark: https://github.com, title:GitHub, category:Dev, tags:code,git

# 検索 / Search
検索: github
search: example

# タグ検索 / Tag search
タグ: code
tag: web

# 一覧 / List
ブックマーク一覧
bookmark list

# カテゴリ一覧 / Category list
カテゴリ一覧
categories

# タグ一覧 / Tag list
タグ一覧
tags

# 共有リンク作成 / Create share link
共有: 1
share: 2

# 更新 / Update
更新: 1, タイトル:New Title, カテゴリ:Reference
update: 2, title:Updated Title

# 削除 / Delete
削除: 1
delete: 2

# 統計 / Stats
統計
stats
```

## 例 / Examples

```
# 基本的な追加 / Basic add
ブックマーク: https://github.com, タイトル:GitHub, カテゴリ:Dev

# タグ付き追加 / Add with tags
ブックマーク: https://stackoverflow.com, タグ:qa, code, help

# 説明付き追加 / Add with description
ブックマーク: https://example.com, タイトル:Example, 説明:素晴らしいサイト

# 検索 / Search
検索: github
タグ: code
```

## 達成状況 / Progress

- [x] データベース設計 / Database design
- [x] 基本機能実装 / Basic features
- [x] Discord連携 / Discord integration
- [x] 日本語・英語対応 / Japanese & English support
- [ ] Web API化 / Web API
- [ ] エクスポート/インポート / Export/Import
- [ ] ブラウザ拡張連携 / Browser extension integration

## 次のステップ / Next Steps

1. Web API化 / Create Web API
2. ブラウザ拡張と連携 / Integrate with browser extension
3. 自動タグ付け機能 / Auto-tagging feature
4. バックアップ/復元機能 / Backup/Restore functionality
