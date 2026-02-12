# Notion Integration

Notion APIを統合して、データベース・ページの同期を行うモジュールです。

## Features / 機能

- 📄 ページの取得・作成・更新・削除
- 📊 データベースの取得・クエリ
- 🔍 Notion内検索
- 📝 ブロックの追加・管理
- 🔑 APIキー認証

## Installation / インストール

```bash
pip install requests
```

## Setup / 設定

1. [Notion Integration](https://www.notion.so/my-integrations)で新しい統合を作成
2. APIキーを取得
3. APIキーを環境変数に設定: `export NOTION_API_KEY=your_api_key`
4. Notionのページやデータベースで統合を共有

## Usage / 使用方法

### Basic Usage / 基本的な使い方

```python
from integrations.notion import NotionClient

# クライアント初期化
client = NotionClient()

# ページ一覧を取得
pages = client.list_pages()
for page in pages:
    print(f"- {page['title']}")

# データベース一覧を取得
databases = client.list_databases()

# 新しいページを作成
client.create_page(
    parent_id="database_id",
    title="New Task",
    content="This is a new task page"
)

# データベースをクエリ
result = client.query_database(database_id="database_id")
```

### Environment Variables / 環境変数

| Variable / 変数 | Description / 説明 | Default / デフォルト |
|-----------------|---------------------|---------------------|
| `NOTION_API_KEY` | Notion APIキー | 必須 |

### CLI Usage / CLI使用方法

```bash
# ページ一覧を表示
python client.py --list-pages

# データベース一覧を表示
python client.py --list-databases

# 検索
python client.py --search "task"

# ページを取得
python client.py --get-page "page_id"

# ページを作成
python client.py --create-page "New Page" --parent "database_id" --content "Content here"
```

## API Reference / APIリファレンス

### `NotionClient`

| Method / メソッド | Description / 説明 |
|-------------------|---------------------|
| `search(query=None, filter_obj=None)` | Notion内を検索 |
| `list_pages()` | ページ一覧を取得 |
| `list_databases()` | データベース一覧を取得 |
| `get_page(page_id)` | ページを取得 |
| `get_database(database_id)` | データベースを取得 |
| `create_page(parent_id, title, ...)` | 新しいページを作成 |
| `update_page(page_id, properties)` | ページを更新 |
| `delete_page(page_id)` | ページを削除（アーカイブ） |
| `add_blocks(block_id, blocks)` | ブロックを追加 |
| `query_database(database_id, ...)` | データベースをクエリ |

## Examples / 例

```python
# 検索
client = NotionClient()
result = client.search(query="meeting")

# データベースをフィルタリングしてクエリ
result = client.query_database(
    database_id="database_id",
    filter_obj={
        'property': 'Status',
        'select': {'equals': 'In Progress'}
    },
    sorts=[{
        'property': 'Priority',
        'direction': 'descending'
    }]
)

# ブロックを追加
blocks = [
    {
        'object': 'block',
        'type': 'heading_1',
        'heading_1': {
            'text': [{'text': {'content': 'Heading'}}]
        }
    },
    {
        'object': 'block',
        'type': 'to_do',
        'to_do': {
            'text': [{'text': {'content': 'Task item'}}],
            'checked': False
        }
    }
]
client.add_blocks("block_id", blocks)

# プロパティを指定してページを作成
properties = {
    'Name': {
        'title': [{'text': {'content': 'Task Name'}}]
    },
    'Status': {
        'select': {'name': 'To Do'}
    },
    'Priority': {
        'number': 1
    }
}
client.create_page(
    parent_id="database_id",
    properties=properties
)
```

## License / ライセンス

MIT
