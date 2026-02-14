# アイディア倉庫 - ProductHunt & Hacker News

トレンドからアイディアを収集・管理する個人開発用ツール。

## 📦 特徴

- 📊 ProductHunt・Hacker Newsのトレンドを自動取得
- 💾 SQLiteでアイディアを保存・管理
- 🔍 キーワード検索・フィルタリング
- 📝 個人的なノート・優先度・ステータス管理
- 📈 統計情報でトレンド分析

## 🚀 セットアップ

### 実行

```bash
# ProductHuntトレンド取得（テストデータ）
python3 producthunt-scraper.py

# Hacker Newsトレンド取得（本番データ）
python3 hackernews-scraper.py

# アイディア管理
python3 producthunt-ideas.py help
```

## 📚 スクリプト一覧

| スクリプト | 説明 |
|-----------|------|
| `producthunt-scraper.py` | ProductHuntトレンド取得（簡易版） |
| `producthunt-scraper-v2.py` | ProductHuntトレンド取得（HTML解析版） |
| `hackernews-scraper.py` | Hacker Newsトレンド取得（API版） |
| `producthunt-ideas.py` | アイディア管理CLI |
| `analyze-producthunt-html.py` | ProductHunt HTML解析ツール |

## 🎯 使い方

### データの取得

```bash
# Hacker Newsトレンド取得（推奨 - API利用）
python3 hackernews-scraper.py

# ProductHuntトレンド取得（簡易版）
python3 producthunt-scraper.py
```

### アイディアの管理

```bash
# アイディア一覧
python3 producthunt-ideas.py list

# 検索
python3 producthunt-ideas.py search "AI"

# ノート追加
python3 producthunt-ideas.py note <ID> "面白い！" --priority 3

# ステータス更新
python3 producthunt-ideas.py status <ID> planning

# 詳細表示
python3 producthunt-ideas.py show <ID>

# 統計情報
python3 producthunt-ideas.py stats
```

### フィルタリング

```bash
# ステータスでフィルタ
python3 producthunt-ideas.py list --status planning

# 最低投票数でフィルタ
python3 producthunt-ideas.py list --min-votes 100

# 表示件数制限
python3 producthunt-ideas.py list --limit 20
```

## 📊 データソース

### Hacker News
- ✅ API利用（認証不要）
- ✅ リアルタイムデータ
- ✅ エンジニア向けコンテンツ

### ProductHunt
- ⚠️ Cloudflare保護により直接スクレイピング不可
- ✅ テストデータで構造確認済み
- 🔄 APIキーがあれば本格実装可能

## 💼 ステータス管理

アイディアの進捗を管理：

- `new` - 新規追加
- `researching` - 調査中
- `planning` - 計画中
- `developing` - 開発中
- `completed` - 完了
- `skipped` - スキップ

## 🎯 優先度

- `0` - 未分類
- `1` - 低
- `2` - 中
- `3` - 高

## 📄 エクスポート

```bash
# 自動エクスポート（取得時に実行）
# - producthunt_export_YYYY-MM-DD.json
# - hackernews_export_YYYY-MM-DD.json
```

## 🗄️ データベース構造

### products テーブル

| カラム | 説明 |
|--------|------|
| id | プロダクトID |
| name | プロダクト名 |
| description | 説明 |
| url | URL |
| votes | 投票数 |
| comments | コメント数 |
| tagline | キャッチコピー |
| topics | トピック（JSON） |
| launch_date | 登録日 |
| screenshot_url | スクリーンショットURL |
| scraped_at | スクレイプ日時 |

### idea_notes テーブル

| カラム | 説明 |
|--------|------|
| id | ノートID |
| product_id | プロダクトID |
| note | 個人的なノート |
| priority | 優先度（0-3） |
| status | ステータス |
| created_at | 作成日時 |
| updated_at | 更新日時 |

## 🔧 今後の改善案

- [ ] ProductHunt API統合（APIキー必要）
- [ ] Webダッシュボード
- [ ] 自動定期取得（cron）
- [ ] AIによるアイディア評価・分類
- [ ] GitHub Issuesとの連携
- [ ] Notion等へのエクスポート
- [ ] ソーシャルシェア機能

## 📝 注意点

- ProductHuntはCloudflare保護により直接スクレイピング不可
- Hacker News APIは認証不要で利用可能
- テストデータは実際のProductHuntデータを模倣

## 📄 ライセンス

MIT
