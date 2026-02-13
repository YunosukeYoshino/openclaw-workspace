# erotic-favorites-agent

お気に入りのえっちな作品を管理・コレクションするエージェント

❤️

## 機能

- お気に入り作品の追加・編集・削除
- タイトル・アーティスト・キーワードで検索
- カテゴリ分類・タグ管理
- 評価ランク機能
- 公開/非公開設定
- コレクション（フォルダ）管理
- メモ・ノート機能
- 統計情報の表示
- Discord Botからの操作

## インストール

```bash
pip install -r requirements.txt
```

## 使い方

### Python API

```python
from db import EroticFavoritesAgentDB

# データベース初期化
db = EroticFavoritesAgentDB()
db.initialize()

# お気に入り追加
fav_id = db.add_favorite(
    title="素晴らしい作品",
    artist="名前なし",
    description="最高の作品",
    category="漫画",
    tags="最高,おすすめ",
    favorite_rank=5
)

# お気に入り検索
favorites = db.search_favorites("最高")
for fav in favorites:
    print(str(fav['title']) + " by " + str(fav['artist']))

# コレクション作成
coll_id = db.create_collection(
    name="ベスト作品集",
    description="最高評価の作品"
)

# コレクションに追加
db.add_to_collection(coll_id, fav_id)

# 統計情報
stats = db.get_stats()
print("総お気に入り数: " + str(stats['total_favorites']))
```

### Discord Bot

```bash
export DISCORD_TOKEN="your_bot_token"
python discord.py
```

## Discordコマンド

| コマンド | 説明 |
|----------|------|
| `!お気に入り追加 <タイトル> [アーティスト]` | お気に入りを追加 |
| `!お気に入り検索 <キーワード>` | キーワードで検索 |
| `!お気に入り一覧 [件数]` | お気に入り一覧を表示 |
| `!お気に入り詳細 <ID>` | 指定IDの詳細を表示 |
| `!カテゴリ一覧` | カテゴリ一覧を表示 |
| `!コレクション作成 <名前> [説明]` | コレクションを作成 |
| `!コレクション一覧` | コレクション一覧を表示 |
| `!コレクション追加 <コレID> <お気に入りID>` | コレクションに追加 |
| `!統計` | 統計情報を表示 |
| `!お気に入り削除 <ID>` | お気に入りを削除 |
| `!ヘルプ` | このヘルプを表示 |

## データベース構造

### favoritesテーブル

| カラム | 型 | 説明 |
|--------|------|------|
| id | INTEGER | 主キー |
| title | TEXT | タイトル |
| artist | TEXT | アーティスト名 |
| description | TEXT | 説明 |
| source | TEXT | ソース |
| url | TEXT | URL |
| category | TEXT | カテゴリ |
| tags | TEXT | タグ（カンマ区切り） |
| favorite_rank | INTEGER | 評価ランク (0-5) |
| is_public | INTEGER | 公開設定 (0=非公開, 1=公開) |
| notes | TEXT | メモ・ノート |
| created_at | TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | 更新日時 |

### collectionsテーブル

| カラム | 型 | 説明 |
|--------|------|------|
| id | INTEGER | 主キー |
| name | TEXT | コレクション名 |
| description | TEXT | 説明 |
| icon | TEXT | アイコン |
| created_at | TIMESTAMP | 作成日時 |

### collection_itemsテーブル

| カラム | 型 | 説明 |
|--------|------|------|
| id | INTEGER | 主キー |
| collection_id | INTEGER | コレクションID |
| favorite_id | INTEGER | お気に入りID |
| added_at | TIMESTAMP | 追加日時 |

## ライセンス

MIT

---

# erotic-favorites-agent (English)

Agent for managing and collecting favorite erotic works

❤️

## Features

- Add, edit, and delete favorite works
- Search by title, artist, or keywords
- Category classification and tag management
- Rating system
- Public/private settings
- Collection (folder) management
- Notes functionality
- Statistics display
- Discord Bot control

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Python API

```python
from db import EroticFavoritesAgentDB

# Initialize database
db = EroticFavoritesAgentDB()
db.initialize()

# Add favorite
fav_id = db.add_favorite(
    title="Amazing Work",
    artist="Unknown",
    description="The best work",
    category="Manga",
    tags="best,recommended",
    favorite_rank=5
)

# Search favorites
favorites = db.search_favorites("best")
for fav in favorites:
    print(str(fav['title']) + " by " + str(fav['artist']))

# Create collection
coll_id = db.create_collection(
    name="Best Works",
    description="Highest rated works"
)

# Add to collection
db.add_to_collection(coll_id, fav_id)

# Statistics
stats = db.get_stats()
print("Total favorites: " + str(stats['total_favorites']))
```

### Discord Bot

```bash
export DISCORD_TOKEN="your_bot_token"
python discord.py
```

## Discord Commands

| Command | Description |
|---------|-------------|
| `!favadd <title> [artist]` | Add a favorite |
| `!favsearch <keyword>` | Search by keyword |
| `!favlist [count]` | List favorites |
| `!favdetail <id>` | Show favorite details |
| `!categories` | List categories |
| `!newcoll <name> [description]` | Create a collection |
| `!colllist` | List collections |
| `!addtocoll <coll_id> <fav_id>` | Add to collection |
| `!stats` | Show statistics |
| `!favdel <id>` | Delete a favorite |
| `!help` | Show help |

## License

MIT
