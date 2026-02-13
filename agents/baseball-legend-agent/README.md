# 野球伝説エージェント / Baseball Legends Agent

野球の伝説的選手・名場面を管理するエージェント
Agent for managing legendary baseball players and famous plays

## Features / 機能

- ルール・用語の説明 (Rule Explanation)
- 殿堂入り選手の管理 (Hall of Fame Management)
- 賞の管理 (Awards Management)
- 野球場情報の管理 (Stadium Information Management)
- 伝説的選手・名場面の管理 (Legends Management)

## Installation / インストール

```bash
pip install -r requirements.txt
```

## Usage / 使用方法

```python
from agents.baseball-legend-agent.agent import BaseballLegendAgentAgent

agent = BaseballLegendAgentAgent()
result = await agent.process_command("rule", ["obstruction"])
print(result)
```

## Database / データベース

- `rules` - ルール・用語データ
- `entries` - 一般エントリーデータ

## Commands / コマンド

- `rule <term>` - 用語を説明
- `hof <name>` - 殿堂入り選手を表示
- `award <name>` - 賞を表示
- `stadium <name>` - 野球場情報を表示
- `legend <name>` - 伝説を表示

## License / ライセンス

MIT
