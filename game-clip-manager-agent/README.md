# ゲームクリップマネージャーエージェント

配信中のハイライトクリップを自動生成・管理するエージェント

## 概要

ゲーム配信クリップカテゴリのエージェントです。配信中のハイライトクリップを自動生成・管理するエージェントを自動化・効率化します。

## インストール

```bash
pip install -r requirements.txt
```

## 使い方

### 基本的な使用方法

```python
from agent import GameClipManagerAgent

async def main():
    agent = GameClipManagerAgent()
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
game-clip-manager-agent/
├── agent.py       # メインエージェント
├── db.py          # データベースモジュール
├── discord.py     # Discordボット
├── README.md      # このファイル
└── requirements.txt
```

## ライセンス

MIT License
