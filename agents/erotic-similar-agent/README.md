# erotic-similar-agent

類似えっちコンテンツ検索エージェント

## Description

Find similar erotic content based on tags, artists, and patterns

タグ、イラストレーター、パターンに基づいて類似のえっちコンテンツを検索

## Features

- エントリーの追加・管理
- タグベースの検索・分類
- Discord Botによる対話的な操作
- SQLiteデータベースによるデータ永続化

## Installation

```bash
cd agents/erotic-similar-agent
pip install -r requirements.txt
```

## Usage

### As a Python Module

```python
from erotic-similar-agent.agent import EroticSimilarAgentAgent

agent = EroticSimilarAgentAgent()
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
python -m erotic-similar-agent.discord
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
- similar_content
- tags
- entries

## API Reference

### Agent Class

```python
class EroticSimilarAgentAgent:
    def __init__(self, db_path: str = "erotic-similar-agent.db")
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
