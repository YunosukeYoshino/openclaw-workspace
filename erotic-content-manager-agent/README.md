# えっちコンテンツマネージャーエージェント

えっちコンテンツの管理・整理・カテゴリ化を行うエージェント

## 概要

えっちコンテンツ管理カテゴリのエージェントです。えっちコンテンツの管理・整理・カテゴリ化を行うエージェントを自動化・効率化します。

## インストール

```bash
pip install -r requirements.txt
```

## 使い方

### 基本的な使用方法

```python
from agent import EroticContentManagerAgent

async def main():
    agent = EroticContentManagerAgent()
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
erotic-content-manager-agent/
├── agent.py       # メインエージェント
├── db.py          # データベースモジュール
├── discord.py     # Discordボット
├── README.md      # このファイル
└── requirements.txt
```

## ライセンス

MIT License
