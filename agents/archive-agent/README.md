# Archive Agent / アーカイブエージェント

A Discord bot agent for managing archive items, categories, and maintaining organized records of important information.

Discordボットエージェントで、アーカイブアイテム・カテゴリを管理し、重要な情報を整理・保管します。

## Features / 機能

- **Archive Item Management / アーカイブアイテム管理**: Register and manage archive items with titles, descriptions, content, tags, and URLs
  - タイトル、説明、コンテンツ、タグ、URL付きでアーカイブアイテムを登録・管理

- **Category Management / カテゴリ管理**: Organize items into categories for better organization
  - アイテムをカテゴリに整理して管理

- **Search & Reference / 検索・参照**: Full-text search through titles, descriptions, and content; filter by category, tags, or status
  - タイトル、説明、コンテンツの全文検索、カテゴリ・タグ・ステータスでのフィルタリング

- **Status Management / ステータス管理**: Mark items as active or archived with automatic timestamp tracking
  - アイテムをアクティブ/アーカイブ済みとして管理、自動タイムスタンプ記録

- **Tag System / タグシステム**: Flexible tagging for cross-category organization
  - カテゴリをまたいだ整理のための柔軟なタグシステム

- **Priority Levels / 優先度レベル**: Assign priority to items for importance tracking
  - アイテムに優先度を設定して重要度を管理

## Installation / インストール

```bash
pip install -r requirements.txt
```

## Usage / 使い方

### Commands / コマンド

#### `!archive` or `!追加` - Add Archive Item
```
!archive Project Plan, 説明: Q1 plan, カテゴリ: ドキュメント, 優先度: 3
!archive Meeting Notes 2025-02-12, タグ: 会議, メモ
!archive Website Resource, URL: https://example.com, カテゴリ: リンク
```

Add a new archive item with title, description, category, tags, priority, and/or URL.

タイトル、説明、カテゴリ、タグ、優先度、URLを指定してアーカイブアイテムを追加。

#### `!update` - Update Archive Item
```
!update 1, タイトル: New Title, 説明: Updated description
!update 2, ステータス: archived, 優先度: 5
```

Update an existing archive item's fields.

既存のアーカイブアイテムのフィールドを更新。

#### `!list_archive` - List Archive Items
```
!list_archive
!list_archive: ステータス: active, 件数: 10
!list_archive: カテゴリ: 1, ステータス: archived
```

Display archive items with optional filtering by status and category.

ステータスやカテゴリでフィルタリングしてアーカイブアイテムを表示。

#### `!search` - Search Archive
```
!search project
!search 会議
!search important notes
```

Search through titles, descriptions, and content.

タイトル、説明、コンテンツから検索。

#### `!detail` or `!view` - View Item Details
```
!detail 1
!view 2
```

View detailed information about a specific item including tags.

特定アイテムの詳細情報（タグ含む）を表示。

#### `!to_archive` - Archive Item
```
!to_archive 1
```

Mark an item as archived.

アイテムをアーカイブ済みとしてマーク。

#### `!unarchive` or `!restore` - Unarchive Item
```
!unarchive 1
!restore 2
```

Restore an archived item to active status.

アーカイブ済みアイテムをアクティブ状態に復元。

#### `!delete` - Delete Archive Item
```
!delete 1
```

Delete an archive item permanently.

アーカイブアイテムを完全に削除。

#### `!category` - Category Management
```
!category追加: ドキュメント, 説明: 重要なドキュメント, 色: 青
!categorydelete: 1
```

Add or delete categories.

カテゴリの追加・削除。

#### `!categories` - List Categories
```
!categories
!カテゴリ一覧
```

Display all categories.

全カテゴリを表示。

#### `!tag` - Tag Operations
```
!tag: 会議
!タグ追加: 1, 重要
!タグ削除: 1, 雑多
```

Search items by tag, add tags, or remove tags.

タグで検索、タグ追加、タグ削除。

#### `!tags` - List All Tags
```
!tags
!タグ一覧
```

Display all tags with item counts.

全タグとアイテム数を表示。

#### `!stats` - View Statistics
```
!stats
!アーカイブ統計
```

Display overall archive statistics including totals by category and status.

カテゴリ・ステータス別の統計を含む全体統計を表示。

## Data Structure / データ構造

### Archive Items / アーカイブアイテム

- **id** - Unique identifier
- **title** - Item title / アイテムタイトル
- **description** - Short description / 短い説明
- **content** - Full content / コンテンツ全文
- **category_id** - Category reference / カテゴリ参照
- **status** - `active` or `archived` / アクティブまたはアーカイブ済み
- **tags** - Comma-separated tags / カンマ区切りのタグ
- **priority** - Priority level (0-10) / 優先度レベル
- **url** - Optional URL / URL（オプション）
- **file_path** - Optional file path / ファイルパス（オプション）
- **metadata** - Additional metadata (JSON) / 追加メタデータ（JSON）
- **archived_at** - Archive timestamp / アーカイブ日時
- **created_at** - Creation timestamp / 作成日時
- **updated_at** - Last update timestamp / 更新日時

### Categories / カテゴリ

- **id** - Unique identifier
- **name** - Category name / カテゴリ名
- **description** - Category description / カテゴリ説明
- **color** - Display color / 表示色

## Examples / 使用例

### Creating a Knowledge Base / 知識ベースの構築
```
!category追加: 技術ドキュメント
!category追加: 会議記録
!category追加: プロジェクト

!archive API仕様書, 説明: REST API v2, カテゴリ: 技術ドキュメント, URL: https://api.example.com/docs, 優先度: 5
!archive 週次ミーティング 2025-02-10, 説明: スプリント計画, カテゴリ: 会議記録, タグ: スプリント, プランニング
!archive プロジェクトロードマップ, 説明: Q1-Q4の計画, カテゴリ: プロジェクト, 優先度: 8
```

### Search and Retrieve / 検索・参照
```
!search API
!タグ: スプリント
!categories
!list_archive: カテゴリ: 1, ステータス: active
!detail 1
```

### Archive Old Items / 古いアイテムのアーカイブ
```
!list_archive: ステータス: active
!to_archive 5
!to_archive 7
!list_archive: ステータス: archived
```

### Restore Archived Items / アーカイブ済みアイテムの復元
```
!search: 重要
!unarchive 3
!detail 3
```

## Running the Bot / ボットの実行

```python
import discord
from discord.ext import commands
from discord import ArchiveAgent

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
bot.add_cog(ArchiveAgent(bot))

# Replace with your token
bot.run('YOUR_BOT_TOKEN')
```

## Database Schema / データベース構造

- `categories`: Archive category definitions / アーカイブカテゴリ定義
- `archive_items`: Archive item records / アーカイブアイテムレコード
- `tags`: Tag definitions for normalization / 正規化用タグ定義
- `item_tags`: Item-tag relationship (many-to-many) / アイテム-タグ関係（多対多）

## Requirements / 要件

- Python 3.8+
- discord.py 2.0+

## License / ライセンス

MIT
