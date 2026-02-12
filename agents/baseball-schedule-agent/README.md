# baseball-schedule-agent

Baseball Schedule Agent - 試合スケジュール管理エージェント

## 機能 / Features

- 試合スケジュールの管理\n- カレンダー連携\n- 試合リマインダー\n- シーズン日程の追跡

## インストール / Installation

```bash
pip install -r requirements.txt
```

## 使用方法 / Usage

```python
from discord import BaseballDiscordBot

bot = BaseballDiscordBot()
result = bot.process_command("ヘルプ")
print(result)
```

## データベース / Database

SQLiteベースのデータベースを使用します。

## ライセンス / License

MIT License
