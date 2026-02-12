#!/usr/bin/env python3
"""
エージェントのREADME.mdを自動生成するスクリプト
"""

import sys
from pathlib import Path

AGENT_TEMPLATES = {
    "tracker": "トラッカー",
    "log": "ログ",
    "manager": "管理",
    "agent": "エージェント"
}

def generate_readme(agent_name: str) -> str:
    """README.mdを生成"""

    # エージェント名から日本語名を推測
    if "tracker" in agent_name:
        ja_name = agent_name.replace("-agent", "").replace("-", " ") + " トラッカー"
        desc = f"{ja_name}は、{agent_name.replace('-agent', '')}の記録と追跡を管理するAIエージェントです。"
    elif "log" in agent_name:
        ja_name = agent_name.replace("-agent", "").replace("-", " ") + " ログ"
        desc = f"{ja_name}は、{agent_name.replace('-agent', '').replace('-', '')}のログを記録・管理するAIエージェントです。"
    elif "manager" in agent_name:
        ja_name = agent_name.replace("-agent", "").replace("-", " ") + " マネージャー"
        desc = f"{ja_name}は、{agent_name.replace('-agent', '').replace('-', '')}の管理を行うAIエージェントです。"
    else:
        ja_name = agent_name.replace("-", " ")
        desc = f"{ja_name}は、{agent_name.replace('-agent', '').replace('-', '')}の管理と追跡を行うAIエージェントです。"

    readme = f"""# {agent_name}

{desc}

## Features

- {agent_name.replace('-agent', '').replace('-', ' ')}の記録
- 統計情報の表示
- 履歴管理
- 検索・フィルタ機能

## Installation

```bash
cd agents/{agent_name}
pip install -r requirements.txt
```

## Usage

### Discord Botとして実行

```bash
python discord.py
```

### データベース操作

```python
from db import {agent_name.replace('-', '_')}DB

db = {agent_name.replace('-', '_')}DB()
db.add_record({{'field1': 'value1', 'field2': 'value2'}})
records = db.get_all_records()
```

## Database Schema

The agent uses SQLite with the following schema:

```sql
CREATE TABLE {agent_name.replace('-', '_')} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Natural Language Commands

The agent supports the following natural language commands (via Discord):

- "Add {agent_name.replace('-agent', '').replace('-', ' ')} record"
- "Show my {agent_name.replace('-agent', '').replace('-', ' ')} history"
- "List recent {agent_name.replace('-agent', '').replace('-', ' ')} entries"

## Configuration

Configuration is stored in `config.json`:

```json
{{
    "database_path": "{agent_name}.db",
    "log_level": "INFO"
}}
```

## Requirements

See `requirements.txt` for dependencies.

## License

MIT License
"""
    return readme

def main():
    """メイン処理"""
    if len(sys.argv) < 2:
        print("Usage: python3 generate_readme.py <agent-name>")
        return

    agent_name = sys.argv[1]
    agents_dir = Path("/workspace/agents")
    agent_dir = agents_dir / agent_name

    if not agent_dir.exists():
        print(f"Error: Agent directory '{agent_dir}' does not exist")
        return

    readme_path = agent_dir / "README.md"
    if readme_path.exists():
        print(f"README.md already exists: {readme_path}")
        return

    readme_content = generate_readme(agent_name)
    readme_path.write_text(readme_content)
    print(f"✅ Created README.md for {agent_name}")

if __name__ == '__main__':
    main()
