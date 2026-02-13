# えっちコンテンツ高度検索エージェント
# Erotic Content Advanced Search Agent

AIエージェント100個のうちの1つ！ / One of 100 AI agents!

---

## 概要 / Overview

えっちなコンテンツの高度な検索機能を提供するエージェント。
An agent that provides advanced search functionality for erotic content.

## 機能 / Features

- 🔍 キーワード検索 / Keyword search
- 🏷️ タグ検索 / Tag search
- 🎨 アーティスト検索 / Artist search
- 📍 ソース検索 / Source search
- 📝 インデックス登録 / Register to search index
- 📋 検索履歴 / Search history
- 📊 統計情報 / Statistics
- 🔄 インデックス再構築 / Rebuild index

## データベース構造 / Database Structure

### search_index (コンテンツインデックス / Content Index)
```
- id: 主キー / Primary Key
- content_id: コンテンツID
- title: タイトル
- artist: アーティスト
- tags: タグ（カンマ区切り）
- description: 説明
- source: ソース
- indexed_at: インデックス作成日時
```

### search_queries (検索クエリ履歴 / Search Query History)
```
- id: 主キー / Primary Key
- query: 検索クエリ
- results_count: 結果件数
- executed_at: 実行日時
```

## 使い方 / Usage

### Discordから使う / Using via Discord

```
# 検索 / Search
検索: キーワード:最高の作品
search: keyword: amazing

# タグ検索 / Tag search
検索: タグ:最高,おすすめ
search: tag: best

# アーティスト検索 / Artist search
検索: アーティスト:名前
search: artist: Name

# 複数条件 / Multiple filters
検索: タグ:最高, アーティスト:名前

# インデックス追加 / Add to index
追加: id:001, タイトル:素晴らしい作品, アーティスト:名前なし, タグ:最高
add: id:002, title:Great Art, artist:Artist Name, tags:best,recommended

# 更新 / Update
更新: 1, タイトル:新しいタイトル
update: 1, title:New Title

# 削除 / Delete
削除: 1
delete: 1

# 検索履歴 / Search history
履歴
history

# 統計 / Stats
統計
stats
```

## 検索機能詳細 / Search Feature Details

### キーワード検索 / Keyword Search
タイトル、アーティスト、タグ、説明からキーワードを検索

### タグ検索 / Tag Search
指定したタグを持つコンテンツを検索（複数タグ可）

### アーティスト検索 / Artist Search
指定したアーティストの作品を検索

### ソース検索 / Source Search
指定したソースのコンテンツを検索

### 組合せ検索 / Combined Search
複数の条件を組み合わせて検索可能

## 統計情報 / Statistics

- 総インデックス数 / Total indexed items
- 検索クエリ数 / Total search queries
- 平均結果数 / Average results per query
- トップ検索クエリ / Top search query

## 導入状況 / Progress

- [x] データベース設計 / Database design
- [x] 基本検索機能 / Basic search features
- [x] インデックス管理 / Index management
- [x] Discord連携 / Discord integration
- [x] 日本語・英語対応 / Japanese & English support
- [ ] Web API化 / Web API
- [ ] ファジー検索 / Fuzzy search
- [ ] 自動インデックス更新 / Auto index update
- [ ] 他エージェントとの連携 / Integration with other agents

## 次のステップ / Next Steps

1. Web API化 / Create Web API
2. ファジー検索の実装 / Implement fuzzy search
3. 自動インデックス更新機能の追加 / Add auto index update
4. 他エージェント（お気に入り、評価）との連携 / Integrate with favorites/rating agents
5. 検索結果のソート・フィルター強化 / Enhanced sorting and filtering

## ライセンス / License

MIT License
