# erotic-rating-agent

えっちなコンテンツの評価・レビューを管理するエージェント

⭐

## 機能

- 評価の追加・編集・削除
- 詳細評価（画質・ストーリー・エロさ・技術）機能
- タイトル・アーティスト・キーワードで検索
- レビューテキスト記録
- おすすめマーク機能
- 高評価作品ランキング
- 統計情報の表示
- Discord Botからの操作

## インストール

```bash
pip install -r requirements.txt
```

## 使い方

### Python API

```python
from db import EroticRatingAgentDB

# データベース初期化
db = EroticRatingAgentDB()
db.initialize()

# 評価追加
rating_id = db.add_rating(
    title="素晴らしい作品",
    artist="名前なし",
    overall_rating=5,
    art_quality=5,
    story_quality=4,
    erotic_quality=5,
    review_text="傑作です！"
)

# 評価検索
ratings = db.search_ratings("最高")
for rating in ratings:
    stars = "⭐" * rating['overall_rating']
    print(str(rating['title']) + " " + stars)

# 高評価順に取得
top_rated = db.get_top_rated(limit=10)
for i, rating in enumerate(top_rated, 1):
    print(str(i) + ". " + str(rating['title']))

# 統計情報
stats = db.get_stats()
print("総評価数: " + str(stats['total_ratings']))
```

### Discord Bot

```bash
export DISCORD_TOKEN="your_bot_token"
python discord.py
```

## Discordコマンド

| コマンド | 説明 |
|----------|------|
| `!評価追加 <タイトル> <総合評価> [アーティスト]` | 評価を追加 |
| `!詳細評価 <タイトル> <総合> <画質> <ストーリー> <エロさ>` | 詳細評価を追加 |
| `!評価検索 <キーワード>` | キーワードで検索 |
| `!評価一覧 [件数]` | 評価一覧を表示 |
| `!評価詳細 <ID>` | 指定IDの詳細を表示 |
| `!高評価 [件数]` | 高評価順に表示 |
| `!おすすめ [件数]` | おすすめを表示 |
| `!統計` | 統計情報を表示 |
| `!評価削除 <ID>` | 評価を削除 |
| `!ヘルプ` | このヘルプを表示 |

## データベース構造

### ratingsテーブル

| カラム | 型 | 説明 |
|--------|------|------|
| id | INTEGER | 主キー |
| title | TEXT | タイトル |
| artist | TEXT | アーティスト名 |
| description | TEXT | 説明 |
| source | TEXT | ソース |
| url | TEXT | URL |
| overall_rating | INTEGER | 総合評価 (0-5) |
| art_quality | INTEGER | 画質評価 (0-5) |
| story_quality | INTEGER | ストーリー評価 (0-5) |
| erotic_quality | INTEGER | エロさ評価 (0-5) |
| technical_quality | INTEGER | 技術評価 (0-5) |
| tags | TEXT | タグ（カンマ区切り） |
| review_text | TEXT | レビューテキスト |
| is_recommended | INTEGER | おすすめ (0=非おすすめ, 1=おすすめ) |
| created_at | TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | 更新日時 |

### rating_categoriesテーブル

| カラム | 型 | 説明 |
|--------|------|------|
| id | INTEGER | 主キー |
| name | TEXT | カテゴリ名 |
| description | TEXT | 説明 |
| created_at | TIMESTAMP | 作成日時 |

### review_commentsテーブル

| カラム | 型 | 説明 |
|--------|------|------|
| id | INTEGER | 主キー |
| rating_id | INTEGER | 評価ID |
| comment | TEXT | コメント |
| created_at | TIMESTAMP | 作成日時 |

## ライセンス

MIT

---

# erotic-rating-agent (English)

Agent for managing erotic content ratings and reviews

⭐

## Features

- Add, edit, and delete ratings
- Detailed rating system (art, story, erotic, technical)
- Search by title, artist, or keywords
- Review text recording
- Recommended mark feature
- Top-rated works ranking
- Statistics display
- Discord Bot control

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Python API

```python
from db import EroticRatingAgentDB

# Initialize database
db = EroticRatingAgentDB()
db.initialize()

# Add rating
rating_id = db.add_rating(
    title="Amazing Work",
    artist="Unknown",
    overall_rating=5,
    art_quality=5,
    story_quality=4,
    erotic_quality=5,
    review_text="Masterpiece!"
)

# Search ratings
ratings = db.search_ratings("best")
for rating in ratings:
    stars = "⭐" * rating['overall_rating']
    print(str(rating['title']) + " " + stars)

# Get top rated
top_rated = db.get_top_rated(limit=10)
for i, rating in enumerate(top_rated, 1):
    print(str(i) + ". " + str(rating['title']))

# Statistics
stats = db.get_stats()
print("Total ratings: " + str(stats['total_ratings']))
```

### Discord Bot

```bash
export DISCORD_TOKEN="your_bot_token"
python discord.py
```

## Discord Commands

| Command | Description |
|---------|-------------|
| `!rateadd <title> <overall> [artist]` | Add a rating |
| `!ratedetail <title> <overall> <art> <story> <erotic>` | Add detailed rating |
| `!ratesearch <keyword>` | Search by keyword |
| `!ratelist [count]` | List ratings |
| `!showrate <id>` | Show rating details |
| `!toprated [count]` | Show top rated |
| `!recommended [count]` | Show recommended |
| `!stats` | Show statistics |
| `!ratedel <id>` | Delete a rating |
| `!help` | Show help |

## License

MIT
