# 野球伝説の選手エージェント

野球の伝説的な選手・レジェンドを管理するエージェント

## 概要

野球フランチャイズカテゴリのエージェントです。野球の伝説的な選手・レジェンドを管理するエージェントを自動化・効率化します。

## インストール

```bash
pip install -r requirements.txt
```

## 使い方

### 基本的な使用方法

```python
from agent import BaseballLegendaryPlayersAgent

async def main():
    agent = BaseballLegendaryPlayersAgent()
    result = await agent.process({"key": "value"})
    print(result)
```

### Discordボットとして使用

```bash
export DISCORD_TOKEN=your_bot_token
python discord.py
```

## 機能

- データの記録・管理
- SQLiteデータベースによる永続化
- Discordボットとの連携
- 統計情報の取得

## ファイル構成

```
baseball-legendary-players-agent/
├── agent.py       # メインエージェント
├── db.py          # データベースモジュール
├── discord.py     # Discordボット
├── README.md      # このファイル
└── requirements.txt
```

## ライセンス

MIT License
