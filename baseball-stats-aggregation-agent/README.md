# 野球統計集計エージェント

野球統計を集計・分析するエージェント。打率、防御率など

## 概要

野球試合データ・統計カテゴリのエージェントです。野球統計を集計・分析するエージェント。打率、防御率などを自動化・効率化します。

## インストール

```bash
pip install -r requirements.txt
```

## 使い方

### 基本的な使用方法

```python
from agent import BaseballStatsAggregationAgent

async def main():
    agent = BaseballStatsAggregationAgent()
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
baseball-stats-aggregation-agent/
├── agent.py       # メインエージェント
├── db.py          # データベースモジュール
├── discord.py     # Discordボット
├── README.md      # このファイル
└── requirements.txt
```

## ライセンス

MIT License
