# ゲームプレイヤー統計エージェント / Game Player Statistics Agent

プレイヤーの詳細な統計・分析を行うエージェント
Agent for detailed player statistics and analysis

## Features / 機能

- プレイヤー統計 (Player Statistics)
- ゲーム進行予測 (Game Progress Prediction)
- ランキング分析 (Ranking Analysis)
- グループ統計 (Group Statistics)
- パターン分析 (Pattern Analysis)

## Installation / インストール

```bash
pip install -r requirements.txt
```

## Usage / 使用方法

```python
from agents.game-player-stats-agent.agent import GamePlayerStatsAgentAgent

agent = GamePlayerStatsAgentAgent()
result = await agent.process_command("player", ["player1"])
print(result)
```

## Database / データベース

- `main_table` - メインデータ（プレイヤー、予測、ランキング、グループ、パターン）
- `entries` - 一般エントリーデータ

## Commands / コマンド

- `player <name>` - プレイヤー統計を表示
- `predict <game>` - ゲームを予測
- `ranking <type>` - ランキングを表示
- `group <name>` - グループ統計を表示
- `pattern <type>` - パターンを分析

## License / ライセンス

MIT
