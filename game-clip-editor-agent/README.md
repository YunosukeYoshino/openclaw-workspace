# ゲームクリップ編集エージェント

クリップの編集・効果追加・字幕追加を自動化するエージェント

## 概要

ゲーム配信クリップカテゴリのエージェントです。クリップの編集・効果追加・字幕追加を自動化するエージェントを自動化・効率化します。

## インストール

```bash
pip install -r requirements.txt
```

## 使い方

### 基本的な使用方法

```python
from agent import GameClipEditorAgent

async def main():
    agent = GameClipEditorAgent()
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
game-clip-editor-agent/
├── agent.py       # メインエージェント
├── db.py          # データベースモジュール
├── discord.py     # Discordボット
├── README.md      # このファイル
└── requirements.txt
```

## ライセンス

MIT License
