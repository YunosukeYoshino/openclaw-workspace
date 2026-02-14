# 野球打順構成エージェント

最適な打順構成を提案・分析するエージェント。対戦相手投手との相性考慮

## 概要

野球戦略分析カテゴリのエージェントです。最適な打順構成を提案・分析するエージェント。対戦相手投手との相性考慮を自動化・効率化します。

## インストール

```bash
pip install -r requirements.txt
```

## 使い方

### 基本的な使用方法

```python
from agent import BaseballLineupAgent

async def main():
    agent = BaseballLineupAgent()
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
baseball-lineup-agent/
├── agent.py       # メインエージェント
├── db.py          # データベースモジュール
├── discord.py     # Discordボット
├── README.md      # このファイル
└── requirements.txt
```

## ライセンス

MIT License
