# えっちコンテンツディスカバリーエージェント

Erotic Content Discovery Agent

## 概要 (Overview)

えっちコンテンツの発見、トレンド、新着コンテンツを管理するエージェント

## 機能 (Features)

- コンテンツ発見
- トレンド追跡
- 新着通知
- レコメンデーション

## インストール (Installation)

```bash
pip install -r requirements.txt
```

## 使用方法 (Usage)

### 基本的な使用 (Basic Usage)

```python
from agent import EroticDiscoveryAgent

agent = EroticDiscoveryAgent()
```

### Discord Botとして使用 (Using as Discord Bot)

```bash
python discord.py
```

## データベース構造 (Database Schema)

### trends
トレンドテーブル

### new_content
新着コンテンツテーブル

## コマンド (Commands)

- `!add_trend <name> <data>` - Add Trend
- `!list_trendss [limit]` - List All Trends
- `!add_new_content <name> <data>` - Add New_content
- `!list_new_contents [limit]` - List All New_content

## ライセンス (License)

MIT License
