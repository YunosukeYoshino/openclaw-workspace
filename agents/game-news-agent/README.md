# game-news-agent

Game News Agent - ゲームニュース収集エージェント

## 機能 / Features

- ゲームニュースの収集\n- アップデート情報の追跡\n- イベント情報の管理\n- 新作ゲームの情報

## インストール / Installation

```bash
pip install -r requirements.txt
```

## 使用方法 / Usage

```python
from discord import GameDiscordBot

bot = GameDiscordBot()
result = bot.process_command("ヘルプ")
print(result)
```

## データベース / Database

SQLiteベースのデータベースを使用します。

## ライセンス / License

MIT License
