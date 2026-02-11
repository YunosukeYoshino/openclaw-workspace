# Search Agent / 検索エージェント

## 概要 / Overview

ウェブ検索・ローカルファイル検索・検索履歴管理を統合した検索エージェント。
Integrated search agent for web search, local file search, and search history management.

## 機能 / Features

- 🔍 **ウェブ検索** (Web Search)
  - キーワードによるウェブ検索
  - Keyword-based web search
  - 検索結果の保存
  - Save search results

- 📁 **ローカル検索** (Local Search)
  - インデックスされたローカルファイルの検索
  - Search indexed local files
  - ファイル名と内容の検索
  - Search by filename and content

- 📜 **検索履歴** (Search History)
  - すべての検索履歴を表示
  - Display all search history
  - 検索結果の保存と管理
  - Save and manage search results

- ⭐ **保存済み検索** (Saved Searches)
  - よく使う検索を保存
  - Save frequently used searches
  - 保存した検索の管理
  - Manage saved searches

## データベース構造 / Database Schema

```sql
search_history (検索履歴)
  - id, query, search_type, result_count, search_timestamp, saved

saved_searches (保存済み検索)
  - id, search_id, name, description, created_at

search_results (検索結果キャッシュ)
  - id, search_id, title, url, snippet, rank

local_files_index (ローカルファイルインデックス)
  - id, filepath, filename, content_preview, indexed_at, last_modified, file_type
```

## 使い方 / Usage

### Japanese / 日本語

```
ウェブ検索: OpenAI ChatGPT
ローカル検索: ドキュメント
ファイル検索: プロジェクト
検索履歴
保存済み検索
保存: 1, 名前: AI関連
統計
```

### English / 英語

```
web search: OpenAI ChatGPT
local search: documents
search file: project
history
saved searches
save: 1, name: AI related
stats
```

## 例 / Examples

### Japanese

```
ウェブ検索: 最新のAI技術
ローカル検索: 計画書
検索履歴
保存: 1, 名前: AI検索
```

### English

```
web search: latest AI technology
local search: plan documents
history
save: 1, name: AI search
```

## コマンド一覧 / Command List

| 日本語 | English | 説明 / Description |
|--------|---------|---------------------|
| ウェブ検索: ... | web search: ... | ウェブ検索 / Web search |
| ローカル検索: ... | local search: ... | ローカルファイル検索 / Local file search |
| ファイル検索: ... | search file: ... | ファイル検索 / File search |
| 検索履歴 | history / search history | 検索履歴を表示 / Show search history |
| 保存済み検索 | saved searches / saved | 保存済み検索を表示 / Show saved searches |
| 保存: ID | save: ID | 検索を保存 / Save search |
| 統計 | stats | 統計情報を表示 / Show statistics |

## 開発状況 / Development Status

- [x] データベース設計 / Database design
- [x] CLI実装 / CLI implementation
- [x] Discord連携 / Discord integration
- [ ] 実際のウェブ検索API統合 / Real web search API integration
- [ ] ローカルファイルの自動インデックス化 / Automatic local file indexing
- [ ] Web API化 / Web API

## 次のステップ / Next Steps

1. Google Search APIまたはBing Search APIとの統合
2. ローカルファイルシステムの自動インデックス化
3. 検索結果のエクスポート機能
4. 高度な検索機能（フィルタリング、ソートなど）
5. ウェブインターフェースの追加

## 注 / Note

現在、ウェブ検索機能はプレースホルダーです。実際の検索には、Google Search APIやBing Search APIなどのサービスとの統合が必要です。
Currently, the web search function is a placeholder. For actual search, integration with services like Google Search API or Bing Search API is required.
