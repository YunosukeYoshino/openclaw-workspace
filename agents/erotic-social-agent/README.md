# えっちコンテンツソーシャルエージェント

Erotic Content Social Agent

## 概要 (Overview)

えっちコンテンツのソーシャルシェア、いいね、コメントを管理するエージェント

## 機能 (Features)

- ソーシャル投稿
- いいね管理
- コメント管理
- シェア分析

## インストール (Installation)

```bash
pip install -r requirements.txt
```

## 使用方法 (Usage)

### 基本的な使用 (Basic Usage)

```python
from agent import EroticSocialAgent

agent = EroticSocialAgent()
```

### Discord Botとして使用 (Using as Discord Bot)

```bash
python discord.py
```

## データベース構造 (Database Schema)

### posts
投稿テーブル

### interactions
インタラクションテーブル

## コマンド (Commands)

- `!add_post <name> <data>` - Add Post
- `!list_postss [limit]` - List All Posts
- `!add_interaction <name> <data>` - Add Interaction
- `!list_interactionss [limit]` - List All Interactions

## ライセンス (License)

MIT License
