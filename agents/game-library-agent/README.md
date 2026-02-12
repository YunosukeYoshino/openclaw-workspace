# game-library-agent

Game Library Agent - ゲームライブラリ管理エージェント

## 機能 / Features

- ゲームコレクションの管理\n- プレイ時間の記録\n- 評価・レビューの管理\n- 未プレイゲームの追跡

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
