# えっちコンテンツキュレーションエージェント

Erotic Content Curation Agent

## 概要 (Overview)

えっちコンテンツのキュレーション、コレクション、おすすめリストを管理するエージェント

## 機能 (Features)

- キュレーション管理
- コレクション作成
- おすすめリスト
- テーマ分類

## インストール (Installation)

```bash
pip install -r requirements.txt
```

## 使用方法 (Usage)

### 基本的な使用 (Basic Usage)

```python
from agent import EroticCurationAgent

agent = EroticCurationAgent()
```

### Discord Botとして使用 (Using as Discord Bot)

```bash
python discord.py
```

## データベース構造 (Database Schema)

### collections
コレクションテーブル

### items
アイテムテーブル

## コマンド (Commands)

- `!add_collection <name> <data>` - Add Collection
- `!list_collectionss [limit]` - List All Collections
- `!add_item <name> <data>` - Add Item
- `!list_itemss [limit]` - List All Items

## ライセンス (License)

MIT License
