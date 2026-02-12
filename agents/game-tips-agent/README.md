# game-tips-agent

Game Tips Agent - ゲーム攻略ヒントエージェント

## 機能 / Features

- 攻略ヒントの記録・管理\n- ボス戦・難所の対策\n- おすすめ装備・ビルド\n- 効率的なプレイ方法

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
