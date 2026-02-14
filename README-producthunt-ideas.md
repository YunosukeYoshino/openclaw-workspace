# ProductHunt アイディア倉庫

ProductHuntのトレンドを自動取得して、個人開発のアイディアを管理するツール。

## 特徴

- 📊 ProductHuntのトレンドを自動スクレイピング
- 💾 SQLiteでアイディアを保存
- 🔍 アイディアの検索・フィルタリング
- 📝 個人的なノート・優先度・ステータス管理
- 📈 統計情報でトレンド分析

## セットアップ

### 1. 実行

```bash
# ProductHuntのトレンドを取得
python3 producthunt-scraper.py

# アイディアを管理
python3 producthunt-ideas.py help
```

## 使い方

### データの取得

```bash
# 最新のトレンドを取得
python3 producthunt-scraper.py
```

これにより以下が実行されます：
- ProductHuntのトレンドを取得
- データベースに保存
- JSONファイルにエクスポート
- 統計情報を表示

### アイディアの管理

```bash
# アイディア一覧を表示
python3 producthunt-ideas.py list

# 検索
python3 producthunt-ideas.py search "AI"

# ノートを追加
python3 producthunt-ideas.py note <ID> "面白いアイディア！" --priority 3

# ステータス更新
python3 producthunt-ideas.py status <ID> planning

# 詳細表示
python3 producthunt-ideas.py show <ID>

# 統計情報
python3 producthunt-ideas.py stats
```

### フィルタリング

```bash
# プラン中のアイディアのみ
python3 producthunt-ideas.py list --status planning

# 100票以上のプロダクトのみ
python3 producthunt-ideas.py list --min-votes 100

# 最新20件のみ
python3 producthunt-ideas.py list --limit 20
```

## ステータス管理

アイディアの進捗を以下のステータスで管理できます：

- `new` - 新規追加（未分類）
- `researching` - 調査中
- `planning` - 計画中
- `developing` - 開発中
- `completed` - 完了
- `skipped` - スキップ

## 優先度

- `0` - 未分類
- `1` - 低
- `2` - 中
- `3` - 高

## データベース構造

### products テーブル

| カラム | 説明 |
|--------|------|
| id | プロダクトID |
| name | プロダクト名 |
| description | 説明 |
| url | ProductHunt URL |
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
| product_id | プロダクトID（外部キー） |
| note | 個人的なノート |
| priority | 優先度（0-3） |
| status | ステータス |
| created_at | 作成日時 |
| updated_at | 更新日時 |

## エクスポート

データはJSONファイルにエクスポートされます：

```bash
# 手動でエクスポート
python3 producthunt-scraper.py  # 自動でエクスポート
```

エクスポートされたファイル：
- `producthunt_export_YYYY-MM-DD.json`

## 注意点

ProductHuntはSPA（Single Page Application）なので、完全なスクレイピングにはブラウザ自動化ツールが必要です。現在は簡易実装としてテストデータを返しています。

本格的なスクレイピングを行いたい場合は、以下のツールの導入を検討してください：

- Playwright
- Puppeteer
- Selenium

## 今後の改善案

- [ ] ProductHunt API統合（認証キーが必要）
- [ ] ブラウザ自動化による完全スクレイピング
- [ ] Webダッシュボード
- [ ] 自動定期取得（cron）
- [ ] AIによるアイディア評価・分類
- [ ] ソーシャルメディア連携

## ライセンス

MIT
