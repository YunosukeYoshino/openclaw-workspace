# erotic-content-discovery-agent

✨ えっちコンテンツディスカバリーエージェント / Erotic Content Discovery Agent

## 概要 (Overview)

このエージェントは、えっちコンテンツの高度な検索・キュレーション機能を提供します。意味検索、タグ分析、コレクション管理、自動キュレーションなどが可能です。

This agent provides advanced search and curation features for erotic content, including semantic search, tag analysis, collection management, and auto-curation.

## 機能 (Features)

### 検索機能 (Search Features)
- **意味検索** (Semantic Search): タグベースの高度な検索
- **関連コンテンツ** (Related Contents): 類似コンテンツの自動推薦
- **検索候補** (Search Suggestions): 入力補完と検索履歴に基づく候補

### キュレーション機能 (Curation Features)
- **コレクション管理** (Collection Management): お気に入りコレクションの作成・管理
- **自動キュレーション** (Auto-Curation): タグや条件に基づく自動追加
- **手動キュレーション** (Manual Curation): 手動でのコンテンツ追加・削除

### タグ分析 (Tag Analysis)
- **タグ頻度分析** (Tag Frequency Analysis): 人気タグの把握
- **関連タグ** (Related Tags): タグ間の関連性分析
- **カテゴリ管理** (Category Management): タグのカテゴリ分類

### コンテンツディスカバリー (Content Discovery)
- **トレンド追跡** (Trend Tracking): 注目コンテンツの発見
- **新規コンテンツ** (New Content): 新着コンテンツの通知
- **おすすめ** (Recommendations): 個別化された推薦

## インストール (Installation)

```bash
pip install -r requirements.txt
```

## 使い方 (Usage)

### Python API

```python
from agent import EroticContentDiscoveryAgentAgent

# エージェント初期化
agent = EroticContentDiscoveryAgentAgent()

# コンテンツ追加
agent.add_content(
    "er001",
    "美少女の冒険",
    "ArtistA",
    "pixiv",
    "https://example.com/1",
    "アニメ,美少女,冒険",
    "かわいい"
)

# 検索
results = agent.semantic_search("アニメ")

# コレクション作成
collection_id = agent.create_collection("お気に入り", "かわいい作品", "美少女")

# コレクションに追加
agent.add_to_collection(collection_id, "er001")

# 接続を閉じる
agent.get_close()
```

### Discord Bot

```
!erotic search <query>
!erotic content <content_id>
!erotic tags [category]
!erotic collection [collection_id]
!erotic stats
```

## データベース (Database)

- `contents`: コンテンツデータ
- `tags`: タグデータ
- `content_tags`: コンテンツ-タグ関連付け
- `search_logs`: 検索ログ
- `collections`: コレクション
- `collection_items`: コレクションアイテム

## 環境変数 (Environment Variables)

- `DISCORD_TOKEN`: Discordボットトークン

## ライセンス (License)

MIT License
