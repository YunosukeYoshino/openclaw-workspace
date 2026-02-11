# クリップボード管理エージェント
# Clipboard Management Agent

AIエージェント100個のうちの1つ！ / One of the 100 AI agents!

## 概要 / Overview

クリップボード履歴の保存・検索、よく使うテキスト（スニペット）の管理ができるエージェント。
An agent for clipboard history management and frequently used text (snippets).

## 機能 / Features

### クリップボード履歴 / Clipboard History
- 📋 履歴の自動保存 / Automatic history saving
- 🔍 履歴の検索 / Search history
- 📊 使用回数の記録 / Track usage count
- 🧹 古い履歴のクリア / Clear old history

### スニペット（よく使うテキスト）/ Snippets (Frequently Used Text)
- 📝 スニペットの保存（タイトル、内容、説明、カテゴリ、タグ） / Save snippets (title, content, description, category, tags)
- 🔍 スニペットの検索 / Search snippets
- ⭐ お気に入り機能 / Favorites feature
- 📁 カテゴリ管理 / Category management
- 🏷️ タグ管理 / Tag management

## データベース構造 / Database Structure

```
clipboard_history (履歴)
  - id, content, content_hash, content_type, size,
    use_count, created_at, last_used

snippets (スニペット)
  - id, title, content, description, category_id,
    is_favorite, use_count, created_at, updated_at

categories (カテゴリ)
  - id, name, color, created_at

tags (タグ)
  - id, name, created_at

snippet_tags (スニペット・タグ紐付け)
  - snippet_id, tag_id
```

## 使い方 / Usage

### Discordから使う / Using via Discord

```
# 履歴に追加 / Add to history
履歴: これはテキストです
history: Sample text here

# スニペット追加 / Add snippet
スニペット: よく使う返信, 内容:ありがとうございます。確認いたします。
snippet: Reply template, content:Thank you. I will check.

# スニペット追加（カテゴリ・タグ付き）/ Add with category & tags
スニペット: API応答, 内容:処理が完了しました, カテゴリ:Code, タグ:api, json

# 履歴検索 / Search history
履歴検索: テキスト
history search: sample

# スニペット検索 / Search snippets
スニペット検索: 返信
検索: api

# 一覧 / List
履歴
history
スニペット一覧
snippet list

# お気に入り一覧 / Favorites
お気に入り
favorites

# スニペット取得 / Get snippet
取得: 1
get: 2

# お気に入り追加/削除 / Toggle favorite
お気に入り: 1
favorite: 2

# 削除 / Delete
削除: 1
履歴削除: 5

# 古い履歴削除 / Clear old history
古い履歴削除: 30
clear: 7

# 統計 / Stats
統計
stats
```

## 例 / Examples

```
# 基本的な履歴保存 / Basic history save
履歴: https://example.com

# よく使うメール返信 / Frequent email reply
スニペット: 受領確認, 内容:メールを受け取りました。確認後、ご連絡いたします。

# コードスニペット / Code snippet
スニペット: Python hello, 内容:print("Hello, World!"), カテゴリ:Code, タグ:python

# お気に入りに追加 / Add to favorites
スニペット: 重要な連絡, 内容:緊急の対応が必要です, お気に入り

# お気に入りを検索 / Search favorites
お気に入り

# タグで検索 / Search by tag
スニペット検索: python
```

## 達成状況 / Progress

- [x] データベース設計 / Database design
- [x] 履歴管理機能 / History management
- [x] スニペット管理機能 / Snippet management
- [x] Discord連携 / Discord integration
- [x] 日本語・英語対応 / Japanese & English support
- [ ] クリップボード監視機能 / Clipboard monitoring
- [ ] 自動タグ付け機能 / Auto-tagging feature
- [ ] エクスポート/インポート / Export/Import

## 次のステップ / Next Steps

1. クリップボード監視（OSクリップボードとの連携）/ Clipboard monitoring
2. 自動タグ付け（内容分析）/ Auto-tagging by content analysis
3. Web API化 / Web API
4. クロスプラットフォーム対応 / Cross-platform support
