# えっちコンテンツブックマークエージェント
# Erotic Content Bookmark Agent

AIエージェント100個のうちの1つ！ / One of the 100 AI agents!

## 概要 / Overview

えっちなコンテンツのブックマーク・整理・検索を行うエージェント。
An agent for bookmarking, organizing, and searching erotic content.

## 機能 / Features

- 🔖 ブックマーク追加（URL、タイトル、説明、タグ、カテゴリ） / Add bookmarks (URL, title, description, tags, category)
- 📋 ブックマーク一覧（最新順） / List bookmarks (newest first)
- 🔍 キーワード検索 / Keyword search
- 🏷️ タグ検索 / Tag search
- 📁 カテゴリ管理 / Category management
- 🕐 最近アクセスしたブックマーク / Recently accessed bookmarks
- 📊 統計情報 / Statistics

## データベース構造 / Database Structure

```
bookmarks (ブックマーク)
  - id, url, title, description, tags, category,
    created_at, last_accessed
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

# 一覧 / List
ブックマーク一覧
bookmark list

# カテゴリ一覧 / Category list
カテゴリ一覧
categories

# タグ一覧 / Tag list
タグ一覧
tags

# 最近アクセス / Recently accessed
最近
recent
履歴
history

# 更新 / Update
更新: 1, タイトル:New Title, カテゴリ:Reference
update: 2, title:Updated Title

# 削除 / Delete
削除: 1
delete: 2

# 統計 / Stats
統計
stats
ブックマーク統計
```

## 例 / Examples

```
# 基本的な追加 / Basic add
ブックマーク: https://example.com, タイトル:Example, カテゴリ:Work

# タグ付き追加 / Add with tags
ブックマーク: https://example.com, タグ:最高,おすすめ

# 説明付き追加 / Add with description
ブックマーク: https://example.com, タイトル:Example, 説明:素晴らしい作品

# 検索 / Search
検索: github
タグ: 最高

# 最近アクセスしたブックマークを表示 / Show recently accessed
最近
```

## 達成状況 / Progress

- [x] データベース設計 / Database design
- [x] 基本機能実装 / Basic features
- [x] Discord連携 / Discord integration
- [x] 日本語・英語対応 / Japanese & English support
- [ ] Web API化 / Web API
- [ ] ブラウザ拡張連携 / Browser extension integration
- [ ] エクスポート/インポート / Export/Import

## 次のステップ / Next Steps

1. Web API化 / Create Web API
2. ブラウザ拡張と連携 / Integrate with browser extension
3. 自動タグ付け機能 / Auto-tagging feature
4. バックアップ/復元機能 / Backup/Restore functionality
