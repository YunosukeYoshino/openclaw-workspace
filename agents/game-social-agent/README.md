# game-social-agent

Game Social Agent - ゲームソーシャル管理エージェント

## 機能 / Features

- フレンド・チーム管理\n- オンラインイベントの記録\n- マッチング履歴の管理\n- ソーシャル機能の活用

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
