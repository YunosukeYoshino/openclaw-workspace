# 野球柔軟性トレーニングエージェント

野球選手の柔軟性トレーニングを管理するエージェント

An agent that manages flexibility training programs for baseball players. Includes stretching, yoga, and range of motion exercises.

## 機能

- エントリーの追加・取得・更新・削除
- タグによる分類・検索
- 統計情報の表示
- Discordボット連携

## インストール

```bash
cd baseball-flexibility-training-agent
pip install -r requirements.txt
```

## 使用方法

### Python API

```python
from agent import BaseballFlexibilityTrainingAgent

agent = BaseballFlexibilityTrainingAgent()
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
