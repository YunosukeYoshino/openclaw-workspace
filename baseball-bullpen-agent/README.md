# 野球ブルペン管理エージェント

継投策・救援投手の起用プランを管理するエージェント。投手疲労度管理

## 概要

野球戦略分析カテゴリのエージェントです。継投策・救援投手の起用プランを管理するエージェント。投手疲労度管理を自動化・効率化します。

## インストール

```bash
pip install -r requirements.txt
```

## 使い方

### 基本的な使用方法

```python
from agent import BaseballBullpenAgent

async def main():
    agent = BaseballBullpenAgent()
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
baseball-bullpen-agent/
├── agent.py       # メインエージェント
├── db.py          # データベースモジュール
├── discord.py     # Discordボット
├── README.md      # このファイル
└── requirements.txt
```

## ライセンス

MIT License
