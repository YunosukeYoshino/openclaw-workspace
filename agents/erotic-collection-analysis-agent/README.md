# erotic-collection-analysis-agent

コレクション分析エージェント

## Description

Analyze user collections and identify patterns in favorites

ユーザーコレクションを分析し、お気に入りのパターンを特定

## Features

- エントリーの追加・管理
- タグベースの検索・分類
- Discord Botによる対話的な操作
- SQLiteデータベースによるデータ永続化

## Installation

```bash
cd agents/erotic-collection-analysis-agent
pip install -r requirements.txt
```

## Usage

### As a Python Module

```python
from erotic-collection-analysis-agent.agent import EroticCollectionAnalysisAgentAgent

agent = EroticCollectionAnalysisAgentAgent()
entry_id = agent.add_entry(
    title="サンプルタイトル",
    content="サンプルコンテンツ",
    artist="イラストレーター名",
    tags=["tag1", "tag2"]
)
print(f"Created entry: {{entry_id}}")
```

### Discord Bot

```bash
export DISCORD_BOT_TOKEN="your_token_here"
python -m erotic-collection-analysis-agent.discord
```

## Discord Commands

| Command | Description |
|---------|-------------|
| `!add <title> [content]` | エントリーを追加 |
| `!list [limit]` | エントリー一覧 |
| `!search <query>` | エントリーを検索 |
| `!get <id>` | エントリー詳細 |
| `!help` | ヘルプ |

## Database Schema

- `entries` - コンテンツエントリー
- `tags` - タグ
- `entry_tags` - エントリーとタグの紐付け
- collections
- analysis
- entries

## API Reference

### Agent Class

```python
class EroticCollectionAnalysisAgentAgent:
    def __init__(self, db_path: str = "erotic-collection-analysis-agent.db")
    def add_entry(self, title, content="", source_url="", artist="", tags=None) -> int
    def get_entry(self, entry_id) -> Optional[Dict]
    def list_entries(self, limit=100, offset=0) -> List[Dict]
    def search_entries(self, query) -> List[Dict]
```

## Development

```bash
# Run tests
pytest tests/

# Format code
black .
flake8 .
```

## License

MIT License
