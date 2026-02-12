# baseball-player-agent

Baseball Player Agent - 選手情報管理エージェント

## 機能 / Features

- 選手プロフィール管理\n- 成績記録・追跡\n- 選手比較\n- お気に入り選手管理

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
