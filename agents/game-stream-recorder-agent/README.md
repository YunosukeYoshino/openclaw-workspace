# ゲームストリームレコーダーエージェント

ゲームライブ配信の録画・保存を管理するエージェント

An agent that manages recording and storage of game live streams. Provides automatic recording, cloud storage, and archive management.

## 機能

- エントリーの追加・取得・更新・削除
- タグによる分類・検索
- 統計情報の表示
- Discordボット連携

## インストール

```bash
cd game-stream-recorder-agent
pip install -r requirements.txt
```

## 使用方法

### Python API

```python
from agent import GameStreamRecorderAgent

agent = GameStreamRecorderAgent()
entry_id = agent.add_entry("サンプル", "これはサンプルエントリーです", tags=["sample", "test"])
print(f"作成されたエントリーID: {entry_id}")
agent.close()
```

### Discord Bot

```bash
export DISCORD_BOT_TOKEN="your_bot_token_here"
python discord.py
```

## ライセンス

MIT License
