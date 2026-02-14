# 野球守備配置エージェント

守備位置・シフト配置の最適化を行うエージェント。打者傾向に基づく配置

## 概要

野球戦略分析カテゴリのエージェントです。守備位置・シフト配置の最適化を行うエージェント。打者傾向に基づく配置を自動化・効率化します。

## インストール

```bash
pip install -r requirements.txt
```

## 使い方

### 基本的な使用方法

```python
from agent import BaseballDefensiveAlignmentAgent

async def main():
    agent = BaseballDefensiveAlignmentAgent()
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
baseball-defensive-alignment-agent/
├── agent.py       # メインエージェント
├── db.py          # データベースモジュール
├── discord.py     # Discordボット
├── README.md      # このファイル
└── requirements.txt
```

## ライセンス

MIT License
