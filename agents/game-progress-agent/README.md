# game-progress-agent

Game Progress Agent - ゲーム進捗管理エージェント

## 機能 / Features

- ストーリー進捗の記録\n- サブクエスト・実績管理\n- クリア状況の追跡\n- 次の目標の管理

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
