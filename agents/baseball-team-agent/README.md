# baseball-team-agent

Baseball Team Agent - チーム情報管理エージェント

## 機能 / Features

- チームプロフィール管理\n- チーム成績追跡\n- 順位表の管理\n- チーム比較

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
