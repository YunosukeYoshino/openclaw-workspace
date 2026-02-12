# baseball-news-agent

Baseball News Agent - 野球ニュース収集エージェント

## 機能 / Features

- 野球ニュースの収集\n- 選手・チームの最新情報\n- トピック別分類\n- 重要ニュースの通知

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
