# 野球データ可視化エージェント / Baseball Data Visualization Agent

野球データのグラフ・チャート作成を行うエージェント
Agent for creating graphs and charts of baseball data

## Features / 機能

- 選手比較 (Player Comparison)
- 歴史的試合記録 (Historic Match Records)
- チーム戦力分析 (Team Strength Analysis)
- データ可視化 (Data Visualization)
- スカウティングレポート (Scouting Reports)

## Installation / インストール

```bash
pip install -r requirements.txt
```

## Usage / 使用方法

```python
from agents.baseball-visualization-agent.agent import BaseballVisualizationAgentAgent

agent = BaseballVisualizationAgentAgent()
result = await agent.process_command("compare", ["player1", "player2"])
print(result)
```

## Database / データベース

- `main_table` - メインデータ（選手、試合、チーム、チャート、レポート）
- `entries` - 一般エントリーデータ

## Commands / コマンド

- `compare <player1> <player2>` - 選手を比較
- `match <id>` - 試合情報を表示
- `team <name>` - チーム戦力を分析
- `chart <name>` - データを可視化
- `scout <player>` - スカウティングレポートを表示

## License / ライセンス

MIT
