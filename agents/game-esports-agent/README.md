# ゲームeスポーツエージェント / Game Esports Agent

ゲームeスポーツ・トーナメント情報を管理するエージェント
Agent for managing game esports and tournament information

## Features / 機能

- レビュー管理 (Review Management)
- DLC管理 (DLC Management)
- eスポーツ情報 (Esports Information)
- 攻略ガイド (Game Guides)
- ニュース・アップデート (News & Updates)

## Installation / インストール

```bash
pip install -r requirements.txt
```

## Usage / 使用方法

```python
from agents.game-esports-agent.agent import GameEsportsAgentAgent

agent = GameEsportsAgentAgent()
result = await agent.process_command("review", ["elden-ring"])
print(result)
```

## Database / データベース

- `items` - アイテムデータ（レビュー、DLC、トーナメント、ガイド、ニュース）
- `entries` - 一般エントリーデータ

## Commands / コマンド

- `review <name>` - レビューを表示
- `dlc <name>` - DLCを表示
- `esports <name>` - eスポーツ情報を表示
- `guide <name>` - ガイドを表示
- `news <name>` - ニュースを表示

## License / ライセンス

MIT
