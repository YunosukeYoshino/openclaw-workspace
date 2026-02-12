# baseball-score-agent

Baseball Score Tracking Agent - 試合スコア追跡エージェント

## 機能 / Features

- スコアの記録・追跡\n- チームの勝敗記録\n- シーズン統計の管理\n- 対戦相手のスコア比較

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
