# えっちコンテンツ閲覧履歴エージェント
# Erotic Content History Agent

AIエージェント100個のうちの1つ！ / One of the 100 AI agents!

## 概要 / Overview

えっちなコンテンツの閲覧履歴を記録・管理するエージェント。
An agent for recording and managing viewing history of erotic content.

## 機能 / Features

- 📝 履歴追加（コンテンツID、タイトル、アーティスト、タグ、ソース） / Add history (content ID, title, artist, tags, source)
- 📋 履歴一覧（最新順） / List history (newest first)
- 🔍 キーワード検索 / Keyword search
- 🎨 アーティスト別履歴 / History by artist
- 🌐 ソース別履歴 / History by source
- 🔥 最多閲覧コンテンツ / Most viewed content
- 🕐 最近の履歴 / Recent history
- 🧹 履歴削除（個別・古い履歴・全削除） / Delete history (individual, old, all)
- 📊 統計情報 / Statistics

## データベース構造 / Database Structure

```
history (履歴)
  - id, content_id, content_title, artist, viewed_at,
    tags, source
```

## 使い方 / Usage

### Discordから使う / Using via Discord

```
# 履歴追加 / Add history
履歴: id:001, タイトル:素晴らしい作品, アーティスト:Name
history: id:002, title:Great Art, artist:Name, source:site.com
view: id:003, title:Amazing, tags:最高,おすすめ, source:example.com

# 検索 / Search
検索: 作品名
search: keyword

# 最近の履歴 / Recent history
最近
recent
最新

# アーティスト別 / By artist
アーティスト: アーティスト名
artist: Artist Name

# ソース別 / By source
ソース: site.com
source: example.com
サイト: site.com

# 最多閲覧 / Most viewed
top
最多
人気

# 統計 / Stats
統計
stats
履歴統計

# 一覧 / List
履歴一覧
history list

# 削除 / Delete
削除: 1
delete: 2
del: 3

# 古い履歴を削除 / Clear old history
クリア: 30
clear: 30
clear old: 30

# 全履歴削除 / Clear all history
クリア
clear
delete all
```

## 例 / Examples

```
# 基本的な追加 / Basic add
履歴: id:001, タイトル:素晴らしい作品

# アーティストとソース付き / With artist and source
履歴: id:002, タイトル:最高のアート, アーティスト:Name, source:site.com

# タグ付き追加 / Add with tags
履歴: id:003, タグ:最高,おすすめ, source:example.com

# 最近の履歴を表示 / Show recent history
最近

# 最多閲覧コンテンツを表示 / Show most viewed
top

# 30日より古い履歴を削除 / Delete history older than 30 days
クリア: 30
```

## 達成状況 / Progress

- [x] データベース設計 / Database design
- [x] 基本機能実装 / Basic features
- [x] Discord連携 / Discord integration
- [x] 日本語・英語対応 / Japanese & English support
- [ ] Web API化 / Web API
- [ ] 履歴のエクスポート / Export history
- [ ] 他エージェントとの連携 / Integration with other agents

## 次のステップ / Next Steps

1. Web API化 / Create Web API
2. 履歴のインポート/エクスポート / Import/Export history
3. 他エージェント（ブックマーク、お気に入り）との連携 / Integrate with bookmark & favorites agents
4. 閲覧傾向の分析 / Viewing pattern analysis
