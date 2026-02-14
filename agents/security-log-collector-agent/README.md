# セキュリティログコレクターエージェント

セキュリティログの収集・管理を担当するエージェント

An agent responsible for collecting and managing security logs. Provides features such as log aggregation from multiple sources, normalization, and indexing.

## 機能

- エントリーの追加・取得・更新・削除
- タグによる分類・検索
- 統計情報の表示
- Discordボット連携

## インストール

```bash
cd security-log-collector-agent
pip install -r requirements.txt
```

## 使用方法

### Python API

```python
from agent import SecurityLogCollectorAgent

agent = SecurityLogCollectorAgent()
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
