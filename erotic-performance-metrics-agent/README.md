# えっちコンテンツパフォーマンスメトリクスエージェント

コンテンツパフォーマンス指標の分析・可視化

## About

えっちコンテンツパフォーマンスメトリクスエージェントはえっちコンテンツ高度分析・予測エージェントの一種として設計されています。

## Features

- データ管理と検索
- Discord Bot統合
- 拡張可能なタグシステム

## Installation

```bash
cd erotic-performance-metrics-agent
pip install -r requirements.txt
```

## Usage

### Run Agent

```bash
python agent.py
```

### Run Discord Bot

```bash
python discord.py <DISCORD_BOT_TOKEN>
```

## Database

SQLiteデータベースを使用しています。初期化は自動的に行われます。

## API Examples

```python
from db import Erotic_performance_metrics_agentDB

db = Erotic_performance_metrics_agentDB()

# エントリーを追加
entry_id = db.add_entry(
    title="Sample Entry",
    content="This is a sample entry.",
    tags=["sample", "test"]
)

# エントリーを取得
entries = db.get_entries()

# 検索
results = db.search_entries("sample")
```

## License

MIT License
