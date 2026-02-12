# RSS Agent / RSSエージェント

A Discord bot agent for managing RSS feeds and staying updated with new articles.

RSSフィードを管理し、新着記事を追跡するためのDiscordボットエージェント。

## Features / 機能

- **RSS Feed Subscription / RSSフィード購読** - Add and manage RSS feeds
- **Article Notifications / 記事通知** - Get notified about new articles
- **Feed Organization / フィード整理** - Organize feeds by category
- **Article Management / 記事管理** - Mark articles as read, add favorites
- **Statistics / 統計** - View feed and article statistics

## Installation / インストール

```bash
pip install -r requirements.txt
```

## Requirements / 必要パッケージ

- `discord.py==2.3.2`
- `feedparser`

## Commands / コマンド

| Command / コマンド | Description / 説明 |
|-------------------|---------------------|
| `!rss` | Show help / ヘルプ表示 |
| `!rss add <name> <url>` | Add RSS feed / RSSフィード追加 |
| `!rss list` | List all feeds / 全フィード一覧 |
| `!rss remove <id>` | Remove feed / フィード削除 |
| `!rss check <id>` | Check for new articles / 新着記事チェック |
| `!rss articles [id]` | Show articles / 記事表示 |
| `!rss unread` | Show unread articles / 未読記事表示 |
| `!rss favorite <id>` | Mark article as favorite / お気に入りに追加 |
| `!rss stats` | Show statistics / 統計表示 |

## Examples / 使用例

### Add a feed / フィードを追加
```
!rss add tech-news https://example.com/feed
```

### List feeds / フィード一覧
```
!rss list
```

### Check for new articles / 新着記事チェック
```
!rss check 1
```

### Show unread articles / 未読記事表示
```
!rss unread
```

## Database Structure / データベース構造

### Feeds Table / フィードテーブル
- `id` - Primary key / 主キー
- `name` - Feed name / フィード名
- `url` - Feed URL / フィードURL
- `category` - Category / カテゴリ
- `update_interval` - Update interval in seconds / 更新間隔(秒)
- `last_checked` - Last check time / 最終チェック時刻
- `is_active` - Active status / アクティブ状態
- `created_at` - Creation time / 作成時刻

### Articles Table / 記事テーブル
- `id` - Primary key / 主キー
- `feed_id` - Foreign key to feeds / フィードへの外部キー
- `title` - Article title / 記事タイトル
- `link` - Article link / 記事リンク
- `description` - Article description / 記事説明
- `content` - Full content / 完全なコンテンツ
- `published_date` - Publication date / 公開日
- `author` - Author name / 著者名
- `is_read` - Read status / 既読状態
- `is_favorite` - Favorite status / お気に入り状態
- `created_at` - Creation time / 作成時刻

### Notifications Table / 通知テーブル
- `id` - Primary key / 主キー
- `feed_id` - Feed reference / フィード参照
- `article_id` - Article reference / 記事参照
- `notification_time` - Notification time / 通知時刻
- `message` - Notification message / 通知メッセージ

## Language Support / 言語サポート

This agent supports both Japanese and English (日本語と英語の両方に対応).

## License / ライセンス

MIT License
